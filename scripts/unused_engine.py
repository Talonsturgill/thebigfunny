#!/usr/bin/env python3
"""unused_engine — what has this engine BUILT and never called?

    python3 scripts/unused_engine.py
    python3 scripts/unused_engine.py --json

WHY THIS EXISTS (owner, 2026-08-03):

    "wow crazy u had it there and just not wired, what else do u have and are
     not using?"

He asked after finding that `headTurn` and `headTilt` were consumed in full by
the head transform and HARDCODED TO ZERO, so the rig could always turn a head and
never did. That is not an isolated slip, it is a repeat pattern here: FIELD_NOTES
already records `run_guard.py` shipping with the freshness invariant implemented
correctly and NO CALLERS anywhere, while three opportunistic reads did exactly
what it was written to prevent.

The failure mode is specific and expensive: a capability that exists, typechecks,
and is never reached looks identical to a capability that does not exist, and the
next run BUILDS IT AGAIN. This run hand-rolled a camera push into an episode file
while `lib/stage3d.tsx` held a full 2.5D move vocabulary (dollyThrough,
orbitReveal, craneDown, truckAcross, riseWith) plus `Atmosphere`, which is the
aerial-perspective depth cue MOTION_BIBLE asks for by name.

WHAT IT REPORTS

  DEAD        exported, and referenced nowhere outside its own file.
  LIB-ONLY    used inside lib/ but never by an episode or scene.

Neither is automatically a defect. A show that de-Alaska'd itself legitimately
leaves Alaska props unused, and this tool cannot tell a retired asset from a
forgotten capability. It is a PROMPT, not a gate: the job is to look at the list
before building something new, which is the step that was skipped.
"""
import argparse, collections, glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "video-engine", "src")
EXPORT = re.compile(r'^export (?:const|function|type|interface|class)\s+([A-Za-z_]\w*)', re.M)


def scan():
    libs = sorted(glob.glob(os.path.join(SRC, "lib", "*.ts"))
                  + glob.glob(os.path.join(SRC, "lib", "*.tsx")))
    cons = sorted(glob.glob(os.path.join(SRC, "*.ts"))
                  + glob.glob(os.path.join(SRC, "*.tsx")))
    libtext = {p: open(p).read() for p in libs}
    context = "\n".join(open(p).read() for p in cons)
    dead, libonly = [], []
    total = 0
    for p, s in libtext.items():
        for name in EXPORT.findall(s):
            total += 1
            pat = re.compile(r'\b' + re.escape(name) + r'\b')
            in_eps = len(pat.findall(context))
            in_lib = sum(len(pat.findall(t)) for q, t in libtext.items() if q != p)
            if in_eps == 0 and in_lib == 0:
                dead.append((name, os.path.basename(p)))
            elif in_eps == 0:
                libonly.append((name, os.path.basename(p)))
    return total, dead, libonly


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    total, dead, libonly = scan()
    if a.json:
        print(json.dumps({"total": total,
                          "dead": [{"name": n, "file": f} for n, f in dead],
                          "lib_only": [{"name": n, "file": f} for n, f in libonly]},
                         indent=2))
        return 0
    print(f"{total} exported symbols in video-engine/src/lib/\n")
    for title, rows in (("DEAD: exported, referenced nowhere outside its own file", dead),
                        ("LIB-ONLY: used inside lib/, never by an episode", libonly)):
        by = collections.defaultdict(list)
        for n, f in rows:
            by[f].append(n)
        print(f"{title}  ({len(rows)})")
        for f in sorted(by, key=lambda k: -len(by[k])):
            print(f"  {f:24s} {len(by[f]):3d}  {', '.join(sorted(by[f])[:8])}"
                  + (" ..." if len(by[f]) > 8 else ""))
        print()
    print("Not a gate. Look at this BEFORE building something new: a capability\n"
          "that exists and is never reached looks exactly like one that does not,\n"
          "and the next run builds it again.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
