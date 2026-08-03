#!/usr/bin/env python3
"""retime_check.py: after a script retime, prove the scene file still renders.

WHY THIS EXISTS, and it is a self-inflicted wound worth a gate.

The Institution's line needed 3.26s in a 2.60s slot, so the script tail moved
0.9s and the board moved with it. The scene file is SELF-TIMED from those
numbers, so it had to move too, and I re-keyed it with a sequential string
replacement. An earlier substitution's OUTPUT then matched a later rule, two
interpolation endpoints collapsed onto the same frame, and EVERY still failed
with:

    inputRange must be strictly monotonically increasing but got [1350,1350]

That is a render-time crash from a source file that typechecks perfectly. tsc
cannot see it, the self-tests cannot see it, and it kills the whole composition
rather than one shot, so the first thing you learn is that nothing renders at
all.

WHAT IT CHECKS

  1. Every `interpolate(f, [...])` input range is strictly increasing.
  2. Every `<Shot from={a} to={b}>` has b > a.
  3. Shots do not overlap and leave no gap, because a self-timed episode with a
     hole in it renders black and says nothing about why.
  4. The shot windows still match the board they are cut to.

  python3 scripts/retime_check.py                       # video-engine/src/Case0003.tsx
  python3 scripts/retime_check.py --scene X --board Y
  python3 scripts/retime_check.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_SCENE = os.path.join(REPO, "video-engine", "src", "Case0003.tsx")
DEFAULT_BOARD = os.path.join(REPO, "out", "dispatch", "storyboard.json")


def ranges(src):
    """-> [(raw, [seconds...])] for every interpolate input range in the file."""
    out = []
    for m in re.finditer(r"interpolate\(\s*[A-Za-z_]\w*\s*,\s*\[([^\]]*)\]", src):
        nums = [float(x) for x in re.findall(r"s\(\s*([\d.]+)\s*\)", m.group(1))]
        if not nums:
            nums = [float(x) for x in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)", m.group(1))]
        if nums:
            out.append((m.group(1).strip(), nums))
    return out


def shots(src):
    """-> [(from, to)] for every <Shot from={} to={}>."""
    return [(float(a), float(b)) for a, b in
            re.findall(r"<Shot\s+from=\{([\d.]+)\}\s+to=\{([\d.]+)\}", src)]


def check(src, board=None):
    rows = []

    def row(n, ok, d=""):
        rows.append((n, bool(ok), d))

    bad = [raw for raw, v in ranges(src)
           if any(v[i] >= v[i + 1] for i in range(len(v) - 1))]
    row("every interpolate range is strictly increasing", not bad,
        f"{len(bad)} degenerate: {bad[:2]}. Remotion throws at RENDER time and "
        f"kills the whole composition, so nothing renders and the error names a "
        f"frame number rather than a shot." if bad else f"{len(ranges(src))} range(s)")

    sh = shots(src)
    row("the scene declares shots at all", bool(sh), f"{len(sh)} shot(s)"
        if sh else "no <Shot from= to=> found. A self-timed episode with no "
                   "windows renders one frame of nothing.")
    if not sh:
        return rows

    inverted = [(a, b) for a, b in sh if b <= a]
    row("no shot ends before it starts", not inverted, f"{inverted[:2]}"
        if inverted else "clean")

    holes = [(sh[i][1], sh[i + 1][0]) for i in range(len(sh) - 1)
             if abs(sh[i + 1][0] - sh[i][1]) > 0.001]
    row("the shots are continuous, no gaps and no overlaps", not holes,
        f"{len(holes)}: {holes[:3]}. A hole renders BLACK and an overlap renders "
        f"whichever came last, and neither says why." if holes else
        f"{sh[0][0]:.1f}s to {sh[-1][1]:.1f}s unbroken")

    if board:
        bt = sorted(tuple(x["t"]) for x in board.get("shots", [])
                    if isinstance(x.get("t"), list) and len(x["t"]) == 2)
        drift = [(a, b) for (a, b) in bt
                 if not any(abs(a - c) < 0.051 and abs(b - d) < 0.051 for c, d in sh)]
        row("the scene is still cut to the board", not drift,
            f"{len(drift)} board shot(s) have no matching window: {drift[:2]}. "
            f"The board moved and the scene did not, so the picture is off the "
            f"words." if drift else f"{len(bt)} shot(s) aligned")
    return rows


def run(scene, board_path):
    src = open(scene).read()
    board = None
    if board_path and os.path.exists(board_path):
        try:
            board = json.load(open(board_path))
        except Exception as e:
            print(f"retime_check: cannot read {board_path}: {e}", file=sys.stderr)
            return 1
    rows = check(src, board)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<52} {d}")
    if all(o for _, o, _ in rows):
        print("\nretime_check: PASS. The scene will render.")
        return 0
    print("\nretime_check: FAIL. Fix the SCENE, not this file.")
    return 1


def self_test():
    ok = True
    good = ("<Shot from={0} to={2.4}>x</Shot>\n"
            "<Shot from={2.4} to={5.0}>y</Shot>\n"
            "interpolate(f, [s(0.3), s(1.2)], [0, 1])\n")
    cases = [
        ("accepts a scene that will render", [], good),
        ("catches a degenerate interpolate range", ["strictly increasing"],
         good.replace("[s(0.3), s(1.2)]", "[s(1.2), s(1.2)]")),
        ("catches a range that runs backwards", ["strictly increasing"],
         good.replace("[s(0.3), s(1.2)]", "[s(1.2), s(0.3)]")),
        # Not isolable, and it declares both: a window that ends before it starts
        # also breaks continuity with its neighbour by construction. Declaring
        # one guard and silently tolerating the other is how a dead guard hides.
        ("catches a shot that ends before it starts",
         ["ends before it starts", "continuous"],
         good.replace("from={2.4} to={5.0}", "from={5.0} to={2.4}")),
        ("catches a HOLE between shots", ["continuous"],
         good.replace("from={2.4} to={5.0}", "from={3.1} to={5.0}")),
        ("catches an OVERLAP between shots", ["continuous"],
         good.replace("from={2.4} to={5.0}", "from={1.9} to={5.0}")),
        ("catches a scene with no shots at all", ["declares shots"],
         "interpolate(f, [s(0.3), s(1.2)], [0, 1])\n"),
    ]
    for name, want, src in cases:
        rows = check(src)
        red = [n for n, o, _ in rows if not o]
        missed = [w for w in want if not any(w in n for n in red)]
        extra = [n for n in red if not any(w in n for w in want)]
        good_ = not missed and not extra
        print(f"  {'ok  ' if good_ else 'FAIL'} {name}"
              + (f"   <- did NOT fire: {missed}" if missed else "")
              + (f"   <- also fired: {extra}" if extra else ""))
        ok &= good_

    # The board comparison, both directions.
    board = {"shots": [{"t": [0, 2.4]}, {"t": [2.4, 5.0]}]}
    aligned = all(o for _, o, _ in check(good, board))
    print(f"  {'ok  ' if aligned else 'FAIL'} accepts a scene still cut to its board")
    ok &= aligned
    moved = {"shots": [{"t": [0, 2.4]}, {"t": [3.3, 5.9]}]}
    caught = any(not o for n, o, _ in check(good, moved) if "cut to the board" in n)
    print(f"  {'ok  ' if caught else 'FAIL'} catches a board that moved and a scene that did not")
    ok &= caught

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", default=DEFAULT_SCENE)
    ap.add_argument("--board", default=DEFAULT_BOARD)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.scene, a.board)


if __name__ == "__main__":
    sys.exit(main())
