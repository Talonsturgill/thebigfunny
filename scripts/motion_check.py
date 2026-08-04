#!/usr/bin/env python3
"""motion_check — does anything actually MOVE, or is it a slideshow?

    python3 scripts/motion_check.py runs/2026-08-03/case0003_tiktok.mp4
    python3 scripts/motion_check.py <mp4> --json
    python3 scripts/motion_check.py --self-test

WHY THIS EXISTS (owner, 2026-08-03, on case 0003):

    "there was no like no motion, no character motion, no scene motion, no
     camera motion"
    "5 second rule, scene change or something happen every 5 seconds to drive
     attention"

He was right, and nothing in the machine could see it. Every gate we had asks
about the FILE (does it parse, is it 1080x1920, is it under sixty, is there
audio) or about the DOCUMENT (does the board declare enough events). Not one of
them ever asked whether the pixels change. Measured on the shipped recut:

    59% of the film visually FROZEN, longest frozen stretch 3.0s,
    and the entire character animation vocabulary was 3.4px of idle sway.

`visual_check.py` counts events the BOARD DECLARES. That is a document check and
it passed this episode, because the board honestly declared events that the
engine then could not render. This gate reads the RENDER. The difference between
those two is the whole reason the owner saw something no critic did.

## What it measures

Luma delta between frames sampled every INTERVAL_S, downscaled, mean absolute.
Cheap, robust, and it correlates with what a thumb scrolling past can see.

  frozen share   fraction of sample gaps under FROZEN_DELTA. A held drawing.
  longest hold   longest consecutive frozen run, in seconds.
  events/5s      the owner's rule: a "change" is a gap above EVENT_DELTA.
  cut share      how much of the motion is CUTS rather than movement. A film
                 that only moves when it cuts is a slideshow with editing.

## The thresholds, and why they are where they are

FROZEN_DELTA 3.0 was calibrated on case 0003: at that threshold the tool
reported 59% frozen and the owner independently said "no motion". Anything the
owner calls frozen, this must call frozen.

MAX_FROZEN_SHARE 0.15 is the target from the WORKLOG, not a measured industry
number, and it is stated as a target rather than dressed up as a finding.

CUT vs MOVEMENT matters because a big delta is ambiguous: a cut and a fast
camera move look identical to a frame differ. A cut is a SINGLE huge spike
bounded by low neighbours; sustained movement is elevated delta over several
consecutive samples. Counting them separately is what stops a run from passing
this gate by simply cutting more often, which would be gaming the number while
making the show worse.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INTERVAL_S = 0.5
FROZEN_DELTA = 3.0          # below this, a viewer sees a held drawing
EVENT_DELTA = 8.0           # above this, something legibly happened
CUT_DELTA = 45.0            # a spike this large bounded by calm is a cut
MAX_FROZEN_SHARE = 0.15
MAX_HOLD_S = 2.0
# THE LIFE BAND, added 2026-08-03 from the motion research. Between FROZEN and
# EVENT sits genuine continuous movement that is neither a freeze nor a cut: a
# camera drift, a moving hold, a prop running. Professional limited animation
# runs THREE budgets that fail differently and cannot substitute for each other
# (LIFE / EVENTS / STAGING, see knowledge/MOTION_BIBLE.md section 1).
#
# Without this floor the gate measures LIFE and EVENTS with one instrument, and
# a film can satisfy it entirely by cutting. That is the loophole case 0003 went
# through: visual_check passed it on declared events while 59% of it was frozen.
MIN_LIVE_SHARE = 0.40
MIN_EVENTS_PER_5S = 1.0     # the owner's five second rule
MAX_CUT_SHARE = 0.65        # above this, the motion is editing, not movement
# Lang et al. 1993 / Lang 2000: an EDIT (angle change, same scene) improves
# recognition with no observed ceiling, but a CUT (change to a NEW scene) stops
# helping above roughly 10 in two minutes and then recognition drops sharply.
# So: many angle changes, few location changes. This cap is specifically what
# stops "add more cuts" from being a way to pass the motion floor.
MAX_SCENE_CHANGES_PER_MIN = 5.0


def ff_bin(name):
    for d in (
        os.path.join(REPO, "video-engine", "node_modules", "@remotion",
                     "compositor-linux-x64-gnu"),
        os.path.join(REPO, "video-engine", "node_modules", "@remotion",
                     "compositor-linux-arm64-gnu"),
    ):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    from shutil import which
    return which(name)


def duration_of(path):
    fp = ff_bin("ffprobe")
    if not fp:
        return None
    out = subprocess.run([fp, "-v", "error", "-show_entries", "format=duration",
                          "-of", "json", path], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception:
        return None


def sample(path, interval=INTERVAL_S):
    """-> ([t], [delta]) or (None, reason).

    Frames are pulled from the RENDER, one seek per sample. Slower than decoding
    once, and immune to the vendored ffmpeg's missing filters, which is the
    trade this repo has made before and been right about.
    """
    ff = ff_bin("ffmpeg")
    if not ff:
        return None, "no ffmpeg: npm install in video-engine/ (it vendors one)"
    dur = duration_of(path)
    if not dur or dur <= 0:
        return None, "could not read duration"
    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        return None, f"missing dep: {e}"

    n = max(2, int(dur / interval))
    tmp = tempfile.mkdtemp(prefix="motion_")
    ts, frames = [], []
    for i in range(n):
        t = i * interval
        out = os.path.join(tmp, f"f{i:05d}.png")
        r = subprocess.run([ff, "-y", "-loglevel", "error", "-ss", f"{t:.3f}",
                            "-i", path, "-frames:v", "1",
                            "-vf", "scale=192:-2", out],
                           capture_output=True)
        if r.returncode != 0 or not os.path.exists(out):
            continue
        ts.append(t)
        frames.append(np.asarray(Image.open(out).convert("L"), dtype=np.float32))
    if len(frames) < 3:
        return None, f"only {len(frames)} frames sampled; nothing to compare"
    deltas = [float(abs(frames[i + 1] - frames[i]).mean())
              for i in range(len(frames) - 1)]
    return (ts[1:], deltas), None


def analyse(ts, deltas):
    n = len(deltas)
    frozen = [d < FROZEN_DELTA for d in deltas]
    frozen_share = sum(frozen) / n

    longest, run, at, best_at = 0, 0, 0.0, 0.0
    for i, f in enumerate(frozen):
        if f:
            if run == 0:
                at = ts[i]
            run += 1
            if run > longest:
                longest, best_at = run, at
        else:
            run = 0

    events = [d >= EVENT_DELTA for d in deltas]
    span = max(ts) - min(ts) + INTERVAL_S
    events_per_5s = (sum(events) / span) * 5.0 if span else 0.0

    # A CUT is a spike bounded by comparative calm. Sustained movement is not.
    cuts = 0
    for i, d in enumerate(deltas):
        if d < CUT_DELTA:
            continue
        prev = deltas[i - 1] if i > 0 else 0.0
        nxt = deltas[i + 1] if i + 1 < n else 0.0
        if prev < d * 0.5 and nxt < d * 0.5:
            cuts += 1
    moving = sum(events)
    cut_share = (cuts / moving) if moving else 1.0
    cuts_per_min = (cuts / span) * 60.0 if span else 0.0

    # LIFE: moving, and NOT because of a cut.
    #
    # First definition of this was the band FROZEN <= d < EVENT, and the
    # self-test caught it immediately: a continuous pan produces deltas ABOVE
    # EVENT_DELTA, so the fixture that is nothing but movement scored 0% live.
    # The band was excluding exactly what it exists to reward. LIFE is not a
    # middle magnitude, it is a CAUSE: the picture changed and no edit did it.
    cut_at = set()
    for i, d in enumerate(deltas):
        if d < CUT_DELTA:
            continue
        prev = deltas[i - 1] if i > 0 else 0.0
        nxt = deltas[i + 1] if i + 1 < n else 0.0
        if prev < d * 0.5 and nxt < d * 0.5:
            cut_at.add(i)
    live = [d >= FROZEN_DELTA and i not in cut_at
            for i, d in enumerate(deltas)]
    live_share = sum(live) / n

    # The five second rule, reported per bucket so a failure has an address.
    buckets = []
    b = 0.0
    while b < max(ts):
        sel = [d for t, d in zip(ts, deltas) if b <= t < b + 5.0]
        if sel:
            buckets.append((b, sum(1 for d in sel if d >= EVENT_DELTA),
                            sum(sel) / len(sel)))
        b += 5.0

    return {
        "samples": n,
        "interval_s": INTERVAL_S,
        "mean_delta": sum(deltas) / n,
        "frozen_share": frozen_share,
        "longest_hold_s": longest * INTERVAL_S,
        "longest_hold_at": best_at,
        "events_per_5s": events_per_5s,
        "cut_share": cut_share,
        "cuts": cuts,
        "cuts_per_min": cuts_per_min,
        "live_share": live_share,
        "buckets": buckets,
    }


def check(path):
    """-> ([(name, ok, detail)], stats|None). A missing input FAILS, never skips."""
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d))

    if not path or not os.path.exists(path):
        row("the render exists", False,
            f"{path or '<none>'} is not on disk. Nothing to measure, which is "
            f"not the same as nothing being wrong.")
        return rows, None
    row("the render exists", True, path)

    got, err = sample(path)
    if got is None:
        row("frames could be sampled", False, err)
        return rows, None
    ts, deltas = got
    s = analyse(ts, deltas)
    row("frames could be sampled", True,
        f"{s['samples']} gaps at {INTERVAL_S}s (anything shorter is invisible here)")

    row(f"frozen share <= {MAX_FROZEN_SHARE:.0%}",
        s["frozen_share"] <= MAX_FROZEN_SHARE,
        f"{s['frozen_share']:.0%} of the film is a held drawing"
        + ("" if s["frozen_share"] <= MAX_FROZEN_SHARE
           else "   <- this is the slideshow number. Move the camera, move the "
                "cast, move a prop."))

    row(f"longest static hold <= {MAX_HOLD_S}s",
        s["longest_hold_s"] <= MAX_HOLD_S,
        f"{s['longest_hold_s']:.1f}s at {s['longest_hold_at']:.1f}s")

    row(f"events per 5s >= {MIN_EVENTS_PER_5S} (the five second rule)",
        s["events_per_5s"] >= MIN_EVENTS_PER_5S,
        f"{s['events_per_5s']:.2f}")

    dead = [f"{b:.0f}-{b+5:.0f}s" for b, ev, _ in s["buckets"] if ev == 0]
    row("no 5s bucket with nothing happening in it", not dead,
        "clean" if not dead else f"dead: {', '.join(dead[:6])}")

    row(f"live share >= {MIN_LIVE_SHARE:.0%} (things move BETWEEN the cuts)",
        s["live_share"] >= MIN_LIVE_SHARE,
        f"{s['live_share']:.0%} of the film is continuous movement"
        + ("" if s["live_share"] >= MIN_LIVE_SHARE
           else "   <- the LIFE budget. A camera drift, a moving hold, a prop "
                "running. Cutting more cannot fix this row, which is the point."))

    # HONEST LIMITATION, stated in the row itself rather than discovered later.
    # Lang's ceiling applies to CUTS (a change to a new SCENE), not to EDITS (an
    # angle change within one scene, which is memory-positive and uncapped). A
    # frame differ cannot tell those apart: both are a spike. So this row counts
    # hard visual discontinuities, and for a single-location episode most of them
    # are EDITS and are fine. It is reported as a WARNING, and the real check
    # belongs on the BOARD, which knows how many distinct locations it declared.
    over = s["cuts_per_min"] > MAX_SCENE_CHANGES_PER_MIN
    row(f"visual discontinuities (warn only, see note)", True,
        f"{s['cuts_per_min']:.1f}/min"
        + ("" if not over else
           f"   <- above the {MAX_SCENE_CHANGES_PER_MIN:.0f}/min ceiling IF these "
           f"are scene changes. A frame differ cannot tell an angle change from a "
           f"location change, so check the board: EDITs are uncapped and "
           f"memory-positive, CUTs are not."))

    row(f"cut share <= {MAX_CUT_SHARE:.0%} (movement, not just editing)",
        s["cut_share"] <= MAX_CUT_SHARE,
        f"{s['cut_share']:.0%} of the visible change is CUTS ({s['cuts']} of them)"
        + ("" if s["cut_share"] <= MAX_CUT_SHARE
           else "   <- cutting more often is not moving. This gate exists so "
                "that trick does not pass."))
    return rows, s


def run(path, as_json=False):
    rows, s = check(path)
    if as_json:
        print(json.dumps({
            "ok": all(o for _, o, _ in rows),
            "rows": [{"name": n, "ok": o, "detail": d} for n, o, d in rows],
            "stats": {k: v for k, v in (s or {}).items() if k != "buckets"},
        }, indent=2))
        return 0 if all(o for _, o, _ in rows) else 1

    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<46} {d}")
    if s:
        print("\n  per 5s bucket (events, mean delta):")
        for b, ev, md in s["buckets"]:
            bar = "#" * min(40, int(md))
            print(f"    {b:5.0f}-{b+5:<5.0f} {ev:2d} ev  {md:6.2f}  {bar}")
    if all(o for _, o, _ in rows):
        print("\nmotion_check: PASS. Things move.")
        return 0
    print("\nmotion_check: FAIL. This is a SLIDESHOW. Fix the ENGINE and the "
          "STAGING,\n              not this file.")
    return 1


def self_test():
    """Prove it can tell a slideshow from a moving picture, and isolate each guard.

    Fixtures are built from generated PNGs, never lavfi video sources: the
    vendored ffmpeg has no wrapped_avframe decoder, so nullsrc/testsrc fail to
    encode there and a previous self-test printed THE GATE IS WRONG when only
    the fixture was unbuildable.
    """
    ff = ff_bin("ffmpeg")
    if not ff:
        print("self-test: no ffmpeg. npm install in video-engine/ first.")
        return 1
    try:
        import numpy as np
        from PIL import Image
    except ImportError as e:
        print(f"self-test: missing dep {e}")
        return 1

    tmp = tempfile.mkdtemp(prefix="motion_selftest_")
    W, H, FPS, SECS = 216, 384, 30, 12
    # BLOCKY texture, not per-pixel noise. The first fixture used per-pixel
    # random noise and the cut-detection row would not fire: downscaling to
    # 192px area-averages high-frequency noise toward its mean, so two
    # completely different random panels differed by less than CUT_DELTA once
    # sampled. The guard was right and the fixture was wrong, which is the order
    # this repo checks them in. CUT_DELTA 45 is calibrated on REAL cuts measured
    # in case 0003, which came in at 79 to 149.
    #
    # 12px blocks survive the downscale, so a cut is a genuinely large delta,
    # and there is still enough structure for a pan to register as movement.
    rng = np.random.default_rng(7)
    BLK = 12
    small = rng.integers(20, 235, (H // BLK + 1, (W * 3) // BLK + 1, 3),
                         dtype=np.uint8)
    texture = np.repeat(np.repeat(small, BLK, axis=0), BLK, axis=1)[:H, :W * 3]

    def encode(name, frame_fn):
        d = os.path.join(tmp, name)
        os.makedirs(d, exist_ok=True)
        for i in range(FPS * SECS):
            Image.fromarray(frame_fn(i)).save(os.path.join(d, f"{i:05d}.png"))
        out = os.path.join(tmp, f"{name}.mp4")
        subprocess.run([ff, "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(d, "%05d.png"), "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", out], check=True,
                       capture_output=True)
        return out

    # SLIDESHOW: a still image that hard-cuts every 3s. High cut share, high
    # frozen share, long holds. This is case 0003 in miniature.
    def slideshow(i):
        panel = (i // (FPS * 3)) % 3
        return texture[:, panel * W:(panel + 1) * W].copy()

    # MOVING: a continuous pan across the same texture. Nothing is ever frozen
    # and there are no cuts at all.
    def moving(i):
        x = int((i / (FPS * SECS)) * (W * 2))
        return texture[:, x:x + W].copy()

    slides = encode("slides", slideshow)
    moves = encode("moves", moving)

    ok = True

    rows, s = check(slides)
    want = ["frozen share", "longest static hold", "cut share"]
    fired = [g for g in want if any(g in n and not o for n, o, _ in rows)]
    good = len(fired) == len(want)
    print(f"  {'ok  ' if good else 'FAIL'} catches: a slideshow of held frames"
          + ("" if good else f"   <- did NOT fire: {set(want) - set(fired)}"))
    if s:
        print(f"       (measured frozen {s['frozen_share']:.0%}, "
              f"hold {s['longest_hold_s']:.1f}s, cuts {s['cut_share']:.0%})")
    ok &= good

    rows, s = check(moves)
    offenders = [n for n, o, _ in rows if not o]
    good = not offenders
    print(f"  {'ok  ' if good else 'FAIL'} accepts: a continuously moving picture"
          + ("" if good else f"   <- tripped {offenders}"))
    if s:
        print(f"       (measured frozen {s['frozen_share']:.0%}, "
              f"hold {s['longest_hold_s']:.1f}s, cuts {s['cut_share']:.0%})")
    ok &= good

    rows, _ = check(os.path.join(tmp, "does_not_exist.mp4"))
    good = any("the render exists" in n and not o for n, o, _ in rows)
    print(f"  {'ok  ' if good else 'FAIL'} catches: a render that is not there")
    ok &= good

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        ap.error("give a render, or --self-test")
    return run(a.path, a.json)


if __name__ == "__main__":
    sys.exit(main())
