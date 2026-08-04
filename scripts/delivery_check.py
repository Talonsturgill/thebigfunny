#!/usr/bin/env python3
"""delivery_check — is the POST FILE actually postable, and is there a link to it?

Phase 7's gate. Everything upstream of here asks whether the episode is good.
This asks the only question the owner actually experiences: can they tap a link
on a phone and get a file a platform will accept.

    python3 scripts/delivery_check.py runs/2026-08-03/case0003_tiktok.mp4
    python3 scripts/delivery_check.py <file> --url https://raw.../case0003_tiktok.mp4
    python3 scripts/delivery_check.py --self-test

WHY THIS EXISTS (owner, 2026-08-03):

    "the deliverable definition of done is to add in a url that will allow me to
    download the video, in 9:16 or whatever TikTok wants"

Before this, `render_gate` passed the master and the run called itself delivered.
The master was `yuvj420p`, full-range JPEG YUV, which is what Remotion emits and
which no gate looked at. On a show built out of crushed dark teal a range
mismatch is the single most visible defect available, because the platform's own
re-encode reads the range tag and lifts or crushes every black in the film. It
would have shipped, and it would have looked "a bit washed out" and nobody would
have known why.

The URL half is the same class of gap one layer up: a path inside a git repo is
not a deliverable to a person holding a phone. A run that ends with
`runs/<date>/x.mp4` has told the owner where the file is on a machine they are
not sitting at.

NOTE ON THE URL CHECK. It is a real fetch, not a string match. The canonical URL
only resolves after the run's PR merges, so the one failure mode that matters is
writing a link into the draft that 404s, which is worse than no link because it
is the first thing the owner acts on.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 1080, 1920
MAX_S = 60.0
MAX_BYTES = 280 * 1024 * 1024      # platform mobile upload cap
MIN_BYTES = 250_000


def ffprobe_bin():
    """The vendored probe, same resolution order as mux_and_verify's ffmpeg."""
    for d in (
        os.path.join(REPO, "video-engine", "node_modules", "@remotion",
                     "compositor-linux-x64-gnu"),
        os.path.join(REPO, "video-engine", "node_modules", "@remotion",
                     "compositor-linux-arm64-gnu"),
    ):
        p = os.path.join(d, "ffprobe")
        if os.path.exists(p):
            return p
    from shutil import which
    return which("ffprobe")


def probe(path):
    fp = ffprobe_bin()
    if not fp:
        return None, "no ffprobe: npm install in video-engine/ (it vendors one)"
    out = subprocess.run(
        [fp, "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
        capture_output=True, text=True)
    if out.returncode != 0:
        return None, f"ffprobe failed: {out.stderr.strip()[:200]}"
    try:
        return json.loads(out.stdout), None
    except Exception as e:
        return None, f"ffprobe output unparseable: {e}"


def faststart(path):
    """moov before mdat, so a player can start on the first bytes it receives."""
    with open(path, "rb") as f:
        head = f.read(4 * 1024 * 1024)
    m, d = head.find(b"moov"), head.find(b"mdat")
    if m == -1:
        return False
    return d == -1 or m < d


def check(path, url=None, fetch=True):
    """-> [(name, ok, detail)]. Every row fires; nothing is skipped on absence.

    A missing input FAILS rather than skipping, which is this repo's oldest and
    most expensive lesson: a check that did not run reads exactly like a check
    that passed.
    """
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d))
        return ok

    if not path or not os.path.exists(path):
        row("the post file exists", False,
            f"{path or '<none>'} is not on disk. There is nothing to deliver, "
            f"which is not the same as nothing being wrong.")
        return rows
    row("the post file exists", True, path)

    size = os.path.getsize(path)
    row("non-trivial size", size >= MIN_BYTES, f"{size:,} bytes")
    row(f"under the {MAX_BYTES // (1024*1024)}MB upload cap",
        size <= MAX_BYTES, f"{size / (1024*1024):.1f}MB")

    meta, err = probe(path)
    if meta is None:
        row("probes as a video", False, err)
        return rows

    vids = [s for s in meta.get("streams", []) if s.get("codec_type") == "video"]
    auds = [s for s in meta.get("streams", []) if s.get("codec_type") == "audio"]

    if not vids:
        row("has a video track", False, "no video stream at all")
        return rows
    v = vids[0]
    row("has a video track", True, v.get("codec_name", "?"))

    row("is 9:16 at 1080x1920",
        v.get("width") == W and v.get("height") == H,
        f"{v.get('width')}x{v.get('height')}")

    # THE ONE THAT WOULD HAVE SHIPPED. Remotion emits yuvj420p (full-range JPEG
    # YUV). Platforms re-encode assuming limited range unless told otherwise, so
    # the blacks move. Nothing upstream of this line ever looked.
    pf = v.get("pix_fmt")
    row("pixel format is yuv420p, not yuvj420p", pf == "yuv420p",
        f"{pf}" + ("" if pf == "yuv420p" else
                   "  <- full-range YUV. The platform re-encode will shift every "
                   "black in the film. Re-encode with -pix_fmt yuv420p."))

    cr = v.get("color_range")
    row("colour range is declared tv (limited)", cr == "tv",
        f"{cr or 'UNDECLARED'}" + ("" if cr == "tv" else
                                   "  <- undeclared range is guessed downstream"))

    row("codec is h264", v.get("codec_name") == "h264", v.get("codec_name", "?"))

    row("audio track present", bool(auds),
        (f"{auds[0].get('codec_name')} {auds[0].get('sample_rate')}Hz "
         f"{auds[0].get('channels')}ch") if auds
        else "NO AUDIO. A silent upload is the 2026-07-17 failure.")
    if auds:
        row("audio is aac at 48kHz",
            auds[0].get("codec_name") == "aac"
            and str(auds[0].get("sample_rate")) == "48000",
            f"{auds[0].get('codec_name')} @ {auds[0].get('sample_rate')}Hz")

    try:
        dur = float(meta.get("format", {}).get("duration", 0))
    except (TypeError, ValueError):
        dur = 0.0
    row("duration readable", dur > 0, f"{dur:.2f}s")
    row(f"duration <= {MAX_S}s (sixty_seconds law)", 0 < dur <= MAX_S, f"{dur:.2f}s")

    row("faststart (moov before mdat)", faststart(path),
        "moov first" if faststart(path)
        else "moov is AFTER mdat: a player must fetch the whole file to begin")

    # ---- the URL half -------------------------------------------------------
    # A path inside a repo is not a deliverable to a person holding a phone.
    if url is None:
        row("a download URL was produced", False,
            "no --url given. Phase 7 is not done until the owner has a link they "
            "can tap. See prompts/BIGFUNNY_ROUTINE.md, THE DEFINITION OF DONE.")
        return rows

    row("a download URL was produced", True, url)
    row("the URL points at the POST file",
        url.rstrip("/").endswith(os.path.basename(path)),
        f"ends with {os.path.basename(path)}"
        if url.rstrip("/").endswith(os.path.basename(path))
        else f"URL basename does not match {os.path.basename(path)}")

    if not fetch:
        row("the URL actually resolves", False,
            "fetch skipped. A URL that was never fetched is a URL that 404s in "
            "the owner's inbox; --no-fetch is for the self-test only.")
        return rows

    try:
        req = urllib.request.Request(url, method="GET",
                                     headers={"Range": "bytes=0-1023"})
        with urllib.request.urlopen(req, timeout=45) as r:
            code, got = r.status, len(r.read())
        ok = code in (200, 206) and got > 0
        row("the URL actually resolves", ok,
            f"HTTP {code}, {got} bytes read"
            + ("" if ok else "  <- a link that 404s is worse than no link"))
    except urllib.error.HTTPError as e:
        row("the URL actually resolves", False,
            f"HTTP {e.code}. If the PR has not merged yet, that is the cause: "
            f"the raw link only resolves on main.")
    except Exception as e:
        row("the URL actually resolves", False, f"{type(e).__name__}: {e}")

    return rows


def run(path, url, fetch=True):
    rows = check(path, url, fetch=fetch)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<44} {d}")
    if all(o for _, o, _ in rows):
        print("\ndelivery_check: PASS. The owner can tap a link and get a "
              "postable file.")
        return 0
    print("\ndelivery_check: FAIL. Fix the DELIVERABLE, not this file. The run "
          "is not\n                delivered because an mp4 exists somewhere.")
    return 1


def self_test():
    """Prove every guard fires, and that each fixture trips ONLY its own guard.

    "Some row went red" is not a test. script_check shipped with a self-test that
    asserted exactly that, and a guard could be disabled entirely while the suite
    stayed green because a neighbour covered for it.
    """
    import tempfile

    ff = None
    for d in (os.path.join(REPO, "video-engine", "node_modules", "@remotion",
                           "compositor-linux-x64-gnu"),):
        p = os.path.join(d, "ffmpeg")
        if os.path.exists(p):
            ff = p
    if not ff:
        print("self-test: no ffmpeg to build fixtures with. "
              "npm install in video-engine/ first.")
        return 1

    tmp = tempfile.mkdtemp(prefix="delivery_selftest_")
    good = os.path.join(tmp, "good_tiktok.mp4")

    # Build fixture video from a generated PNG, NOT from lavfi: the vendored
    # ffmpeg has no wrapped_avframe decoder, so every lavfi VIDEO source fails
    # to encode there. That cost a previous self-test a false "THE GATE IS
    # WRONG" when the gate was fine and only the fixture was unbuildable.
    # NOISE, not a flat fill. A flat teal frame encodes to about 13KB, which is
    # under MIN_BYTES, so the first cut of this self-test failed its own
    # non-trivial-size row on every fixture and reported THE GATE IS WRONG when
    # the gate was right and the fixture was a solid colour. Noise defeats the
    # encoder and gives a fixture with a realistic bitrate.
    from PIL import Image
    import numpy as _np
    png = os.path.join(tmp, "f.png")
    rng = _np.random.default_rng(11)
    Image.fromarray(rng.integers(0, 255, (H, W, 3), dtype=_np.uint8)).save(png)
    sil = os.path.join(tmp, "s.wav")
    subprocess.run([ff, "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", "anullsrc=r=48000:cl=stereo:d=3", "-c:a", "pcm_s16le",
                    sil], check=True)

    def build(out, pix="yuv420p", faststart_on=True, size=(W, H), audio=True):
        cmd = [ff, "-y", "-loglevel", "error", "-loop", "1", "-t", "3", "-i", png]
        if audio:
            cmd += ["-i", sil]
        # The full colour set, not just -color_range. On its own that flag did
        # not reach the container and every fixture probed as UNDECLARED, which
        # tripped the range row on cases that were supposed to isolate other
        # guards. The real delivery encode sets all four, so the fixture does.
        cmd += ["-c:v", "libx264", "-pix_fmt", pix, "-r", "30",
                "-s", f"{size[0]}x{size[1]}",
                "-color_range", "tv" if pix == "yuv420p" else "pc",
                "-colorspace", "bt709", "-color_primaries", "bt709",
                "-color_trc", "bt709"]
        if audio:
            cmd += ["-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
                    "-shortest"]
        cmd += ["-movflags", "+faststart" if faststart_on else "-faststart", out]
        subprocess.run(cmd, check=True, capture_output=True)

    build(good)

    bad_pix = os.path.join(tmp, "badpix_tiktok.mp4")
    build(bad_pix, pix="yuvj420p")
    bad_dim = os.path.join(tmp, "baddim_tiktok.mp4")
    build(bad_dim, size=(1920, 1080))
    no_audio = os.path.join(tmp, "noaudio_tiktok.mp4")
    build(no_audio, audio=False)

    URL = "file-not-fetched"
    # `guard` may name several rows with "|". Only ONE case needs it, and it is
    # genuinely not isolable rather than lazily written: yuvj420p IS full-range
    # by definition, so a file with that pixel format cannot fail the format row
    # without also failing the range row. Declaring both is the honest form; the
    # trap this avoids is a case that quietly passes because a neighbouring
    # guard covered for a dead one.
    cases = [
        ("a full-range yuvj420p master",
         "yuv420p, not yuvj420p|colour range is declared tv", bad_pix),
        ("a landscape video", "9:16", bad_dim),
        ("a silent video", "audio track present", no_audio),
        ("a post file that does not exist", "the post file exists",
         os.path.join(tmp, "nope.mp4")),
        ("no URL at all", "a download URL was produced", good, None),
    ]

    ok = True
    for case in cases:
        name, guard, path = case[0], case[1], case[2]
        u = case[3] if len(case) > 3 else URL
        want = guard.split("|")
        rows = check(path, u, fetch=False)
        missed = [g for g in want
                  if not any(g in n and not o for n, o, _ in rows)]
        others = [n for n, o, _ in rows
                  if not o and not any(g in n for g in want)
                  and "actually resolves" not in n
                  and "points at the POST file" not in n]
        good_case = not missed and not others
        fired = not missed
        print(f"  {'ok  ' if good_case else 'FAIL'} catches: {name}"
              + ("" if fired else f"   <- did NOT fire: {missed}")
              + (f"   <- not isolated, also fired: {others}" if others else ""))
        ok &= good_case

    # The accept direction. `--no-fetch` deliberately fails the resolve row, so
    # a good file is judged on everything BUT the network.
    rows = check(good, "https://example.invalid/good_tiktok.mp4", fetch=False)
    offenders = [n for n, o, _ in rows if not o and "actually resolves" not in n]
    clean = not offenders
    if not clean:
        for n, o, d in rows:
            if not o:
                print(f"       (good file tripped '{n}': {d})")
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a spec-clean post file")
    ok &= clean

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="the POST file, runs/<date>/<case>_tiktok.mp4")
    ap.add_argument("--url", help="the download URL the owner will be given")
    ap.add_argument("--no-fetch", action="store_true",
                    help="skip the live fetch (self-test only; it FAILS the row)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.error("give the post file, or --self-test")
    return run(a.path, a.url, fetch=not a.no_fetch)


if __name__ == "__main__":
    sys.exit(main())
