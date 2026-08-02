#!/usr/bin/env python3
"""contact_sheet.py: give the critics EYES.

WHY THIS EXISTS
The owner watched case 0003 and said "the scenes are boring and not actually
illustrating anything". Every gate in this machine had already passed it. That
is not a run of bad luck, it is a structural blind spot: the storyboard critic
and the flow critic grade JSON. Nothing in the pipeline has ever LOOKED at the
episode. A show that is judged entirely on its description will drift until the
description is the only good thing about it.

This renders N stills spread evenly across an episode and stitches them into one
labelled grid, so a critic agent can be handed a single PNG and grade what the
audience will actually see, at roughly the size the audience will see it.

THE REMOTION `--frames` FLAG: CHECKED, AND IT IS NOT HERE.
The plan for this script was Remotion's batch-still flag, `--frames=0,10,20`,
which renders several stills in ONE invocation and would make a contact sheet
about as expensive as a single still. It is not available in this tree, and this
was verified rather than assumed:

  - `video-engine/package.json` pins `@remotion/cli` and `remotion` at 4.0.399.
  - `node_modules/@remotion/cli/dist/still.js` in that version contains an
    explicit REJECTION of the flag:
        "--frames flag was passed to the `still` command. This flag only works
         with the `render` command. Did you mean `--frame`?"
    followed by `process.exit(1)`. So on 4.0.399 it does not merely fail to help,
    it aborts the render.
  - `--frames` on the `render` command in 4.0.399 parses as a single number or a
    contiguous `A-B` range only (see `dist/config/frame-range.js`, which splits on
    "-" and rejects more than two numbers). It cannot express a sparse list, so
    it is not a substitute either.
  - `npm view remotion version` reports 4.0.504 upstream, so the flag may well
    exist there. Upgrading Remotion is not this script's business.

SO THIS SCRIPT DOES THE OTHER THING, AND SAYS SO EVERY TIME IT RUNS.
It makes N separate `remotion still` calls, a few in parallel, and prints which
path it took. It also re-probes the installed CLI on every run: the moment
somebody upgrades the engine and the batch flag becomes real, this prints a loud
note saying so instead of quietly continuing to do it the slow way forever. That
note is the whole reason the probe is not just a comment.

USAGE
  python3 scripts/contact_sheet.py Case0004 out/dispatch/contact_sheet.png
  python3 scripts/contact_sheet.py Case0004 out.png -n 16 --cols 4
  python3 scripts/contact_sheet.py Case0004 out.png --dry-run   # plan only, no render
  python3 scripts/contact_sheet.py --probe                      # just report the CLI

Exit 0 on success, 1 on failure.
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE = os.path.join(REPO, "video-engine")
ENTRY = "src/index.ts"

# The version that is claimed to have batch stills. Kept as a constant so the
# probe reports a comparison rather than a hunch.
BATCH_STILL_SINCE = (4, 0, 502)

# Twelve cells across a 60 second episode is one look every five seconds, which
# is roughly one per SHOT on a seven-shot board plus the transitions. Fewer than
# that and a whole beat can hide between cells; many more and each cell gets too
# small to judge staging in a 4-wide grid.
DEFAULT_N = 12
DEFAULT_COLS = 4

# Render at half res and display smaller still. This is deliberate: the platform
# decides on a thumbnail, so a contact sheet that reads at thumbnail size is
# testing the same thing the feed tests. Full res would also cost 4x the time
# for a picture nobody inspects pixel-by-pixel.
DEFAULT_SCALE = 0.5
CELL_W = 300

# Each `remotion still` boots node and a browser, so these are heavy processes,
# not threads. render.sh uses --concurrency=2 for the same memory reason; three
# in flight is the most this box takes without swapping.
DEFAULT_WORKERS = 3


# ---------------------------------------------------------------------------
# capability probe


def installed_cli_version():
    """-> (tuple, str) for the @remotion/cli that is actually on disk.

    node_modules first, because that is what will run. package.json is only the
    fallback for a tree that has not been installed yet.
    """
    import json
    for path, key in (
        (os.path.join(ENGINE, "node_modules", "@remotion", "cli", "package.json"), "version"),
        (os.path.join(ENGINE, "package.json"), None),
    ):
        try:
            doc = json.load(open(path))
        except Exception:
            continue
        v = doc.get("version") if key else (doc.get("dependencies", {}) or {}).get("@remotion/cli")
        if not v:
            continue
        raw = str(v)
        m = re.search(r"(\d+)\.(\d+)\.(\d+)", raw)
        if m:
            return tuple(int(x) for x in m.groups()), raw
    return None, "unknown"


def batch_stills_supported():
    """-> (bool, reason). Two independent signals, because a version number is a
    claim and the shipped code is the fact.

    Signal 1 is the version compare. Signal 2 reads the installed still.js for
    the string 4.0.399 prints when it REFUSES the flag; if that refusal is still
    in the file, the flag is not usable no matter what the version says.
    """
    ver, raw = installed_cli_version()
    still_js = os.path.join(ENGINE, "node_modules", "@remotion", "cli", "dist", "still.js")
    refuses = None
    try:
        src = open(still_js, encoding="utf-8", errors="replace").read()
        refuses = "This flag only works with the `render` command" in src
    except Exception:
        pass

    if refuses is True:
        return False, (f"@remotion/cli {raw}: dist/still.js still contains the explicit "
                       f"'--frames ... only works with the render command' rejection, so the "
                       f"still command aborts if the flag is passed")
    if ver is None:
        return False, "could not determine the installed @remotion/cli version"
    if ver < BATCH_STILL_SINCE:
        return False, (f"@remotion/cli {raw} is older than "
                       f"{'.'.join(str(x) for x in BATCH_STILL_SINCE)}")
    return True, (f"@remotion/cli {raw} is at or past "
                  f"{'.'.join(str(x) for x in BATCH_STILL_SINCE)} and no longer refuses --frames")


# ---------------------------------------------------------------------------
# composition metadata


def composition_meta(comp):
    """-> (fps, total_frames). Asks Remotion rather than guessing, because a
    contact sheet spread over the wrong duration silently samples the wrong
    episode length and every cell is off."""
    out = subprocess.run(["npx", "remotion", "compositions", ENTRY],
                         cwd=ENGINE, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"remotion compositions failed:\n{out.stderr.strip()[:800]}")
    # "Case0004            30      1080x1920      1638 (54.60 sec)"
    for line in out.stdout.splitlines():
        m = re.match(r"^(\S+)\s+(\d+)\s+(\d+)x(\d+)\s+(\d+)\s", line.strip())
        if m and m.group(1) == comp:
            return int(m.group(2)), int(m.group(5))
    ids = [l.split()[0] for l in out.stdout.splitlines() if l.strip() and not l.startswith(" ")]
    raise RuntimeError(f"composition '{comp}' is not registered. Known: {' '.join(ids[:20])}")


def pick_frames(total, n):
    """Evenly spread, inclusive of the first and last renderable frame.

    The last frame matters: the button and the end card live there, and an
    episode whose ending is never sampled is exactly the episode that ships with
    a dead button (retro.py's open `button_doesnt_land` offender).
    """
    last = max(0, total - 1)
    if n <= 1:
        return [0]
    step = last / float(n - 1)
    return sorted({int(round(i * step)) for i in range(n)})


# ---------------------------------------------------------------------------
# rendering


def props_arg():
    """Same conditional as render.sh: Remotion HARD ERRORS on a --props path that
    does not exist, so the flag is only passed when the file is really there."""
    p = os.path.join(REPO, "out", "dispatch", "episode_props.json")
    return [f"--props={p}"] if os.path.isfile(p) else []


def render_one(comp, frame, path, scale, extra):
    cmd = ["npx", "remotion", "still", ENTRY, comp, path,
           f"--frame={frame}", f"--scale={scale}"] + extra
    r = subprocess.run(cmd, cwd=ENGINE, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(path):
        return frame, (r.stderr or r.stdout).strip()[-600:]
    return frame, None


def render_all(comp, frames, tmpdir, scale, workers):
    extra = props_arg()
    jobs = [(f, os.path.join(tmpdir, f"f{f:06d}.png")) for f in frames]
    errors = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(render_one, comp, f, p, scale, extra): (f, p) for f, p in jobs}
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            frame, err = fut.result()
            done += 1
            if err:
                errors[frame] = err
                print(f"  [{done}/{len(jobs)}] frame {frame}: FAILED", file=sys.stderr)
            else:
                print(f"  [{done}/{len(jobs)}] frame {frame}: ok")
    return jobs, errors


# ---------------------------------------------------------------------------
# stitch


def _font(size):
    from PIL import ImageFont
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def stitch(jobs, fps, out_path, cols, cell_w, title=""):
    """Grid of cells, each labelled with its TIMESTAMP.

    The timestamp is not decoration. A critic's note is only actionable if it can
    say "at 31 seconds nothing has changed since 22", which is the reader-sim
    timeline the WORKLOG asks for, and that needs the clock on the picture.
    """
    from PIL import Image, ImageDraw

    tiles = []
    for frame, path in sorted(jobs, key=lambda j: j[0]):
        if not os.path.isfile(path):
            continue
        im = Image.open(path).convert("RGB")
        h = max(1, int(round(im.height * (cell_w / float(im.width)))))
        tiles.append((frame, im.resize((cell_w, h), Image.LANCZOS)))
    if not tiles:
        raise RuntimeError("no stills were rendered, nothing to stitch")

    cell_h = max(t.height for _, t in tiles)
    pad, bar, margin = 8, 26, 12
    head = 34 if title else 0
    rows = (len(tiles) + cols - 1) // cols
    W = margin * 2 + cols * cell_w + (cols - 1) * pad
    H = margin * 2 + head + rows * (cell_h + bar) + (rows - 1) * pad

    sheet = Image.new("RGB", (W, H), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    if title:
        draw.text((margin, margin), title, font=_font(18), fill=(232, 232, 236))

    for i, (frame, tile) in enumerate(tiles):
        r, c = divmod(i, cols)
        x = margin + c * (cell_w + pad)
        y = margin + head + r * (cell_h + bar + pad)
        sheet.paste(tile, (x, y))
        draw.rectangle([x, y + cell_h, x + cell_w - 1, y + cell_h + bar - 1], fill=(34, 34, 38))
        secs = frame / float(fps) if fps else 0.0
        draw.text((x + 6, y + cell_h + 5),
                  f"{i + 1:02d}   t={secs:6.2f}s   f={frame}",
                  font=_font(14), fill=(214, 214, 220))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    sheet.save(out_path)
    return sheet.size


# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(
        description="Render N stills across an episode and stitch a labelled contact sheet.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("comp", nargs="?", help="composition id, e.g. Case0004")
    ap.add_argument("out", nargs="?", help="output grid PNG path")
    ap.add_argument("-n", "--count", type=int, default=DEFAULT_N, help="how many stills")
    ap.add_argument("--cols", type=int, default=DEFAULT_COLS, help="grid columns")
    ap.add_argument("--scale", type=float, default=DEFAULT_SCALE, help="render scale per still")
    ap.add_argument("--cell-width", type=int, default=CELL_W, help="cell width in the grid, px")
    ap.add_argument("--workers", type=int, default=DEFAULT_WORKERS,
                    help="parallel remotion still processes")
    ap.add_argument("--keep", metavar="DIR", help="keep the individual stills in DIR")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the frame plan and exit without rendering")
    ap.add_argument("--probe", action="store_true",
                    help="report the installed Remotion CLI and exit")
    a = ap.parse_args()

    supported, reason = batch_stills_supported()
    if a.probe:
        print(f"contact_sheet: batch stills (--frames=a,b,c on `remotion still`): "
              f"{'AVAILABLE' if supported else 'NOT AVAILABLE'}")
        print(f"  {reason}")
        return 0

    if not a.comp or not a.out:
        ap.error("comp and out are required (or pass --probe)")

    if supported:
        # Loud on purpose. This script does the slow thing; the day the engine is
        # upgraded, somebody should be told the fast path exists rather than
        # inheriting a workaround nobody remembers is a workaround.
        print("contact_sheet: NOTE, the installed CLI now supports batch stills")
        print(f"  {reason}")
        print("  This script still renders one still per call. Revisit the header.")
    else:
        print(f"contact_sheet: one `remotion still` per frame ({reason})")

    try:
        fps, total = composition_meta(a.comp)
    except Exception as e:
        print(f"contact_sheet: {e}", file=sys.stderr)
        return 1

    frames = pick_frames(total, a.count)
    print(f"contact_sheet: {a.comp}, {total} frames at {fps}fps "
          f"({total / float(fps):.2f}s), sampling {len(frames)}")
    if a.dry_run:
        for f in frames:
            print(f"  frame {f:>5}  t={f / float(fps):6.2f}s")
        return 0

    tmp = a.keep or tempfile.mkdtemp(prefix="contact_sheet_")
    os.makedirs(tmp, exist_ok=True)
    jobs, errors = render_all(a.comp, frames, tmp, a.scale, max(1, a.workers))
    if errors:
        print(f"\ncontact_sheet: {len(errors)} still(s) failed to render", file=sys.stderr)
        for f, e in sorted(errors.items())[:3]:
            print(f"  frame {f}: {e}", file=sys.stderr)
        if len(errors) == len(frames):
            return 1

    title = f"{a.comp}   {total} frames @ {fps}fps   {total / float(fps):.2f}s"
    try:
        size = stitch(jobs, fps, a.out, max(1, a.cols), a.cell_width, title)
    except Exception as e:
        print(f"contact_sheet: stitch failed: {e}", file=sys.stderr)
        return 1
    print(f"\ncontact_sheet: wrote {a.out} ({size[0]}x{size[1]}, "
          f"{len(jobs) - len(errors)} cells)")
    if not a.keep:
        for _, p in jobs:
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmp)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
