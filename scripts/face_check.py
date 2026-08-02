#!/usr/bin/env python3
"""face_check.py — an episode whose faces do not move does not ship.

WHY THIS IS A GATE AND NOT A NOTE
Case 0002 shipped with THREE expression changes in fifty-two seconds and cleared
every gate in the machine, because not one of them could see a face. The owner
watched it and said it was impossible to feel anything. A rule nobody can fail is
a preference, so this is the rule with teeth.

WHAT IT REFUSES

1. A DEAD FACE. Nobody holds one expression longer than MAX_HOLD_S while they
   are on screen. Nine seconds of one face is a slide, not a performance.

2. TOO FEW CHANGES. At least MIN_CHANGES across the episode. Deliberately low:
   this catches an episode that forgot, not one with a quiet passage.

3. A LISTENER WHO NEVER REACTS. The one that matters most. In a two-hander the
   joke lands on the face of the person who is NOT talking, so at least
   MIN_REACTIONS of the changes must happen to a character during someone
   else's line. A script that only ever directs the speaker has written a
   newsreader, and the machine had no way to notice.

It reads the SCRIPT, so it runs before anything is rendered and before a single
take is paid for.

  python3 scripts/face_check.py                     # out/dispatch/script.json
  python3 scripts/face_check.py runs/2026-08-02/script.json
  python3 scripts/face_check.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_faces_ts import build, validate, CHARACTERS  # one definition of the track

# A held face is fine for a beat. It is not fine for a whole shot: the longest
# single line in case 0002 ran 6.3s, so anything past two of those is a figure
# that has stopped acting.
MAX_HOLD_S = 8.0
MIN_CHANGES = 6
MIN_REACTIONS = 2


def analyse(script):
    lines = script["lines"]
    end = float(script.get("estimated_seconds")
                or max(float(l["t"]) for l in lines) + 3.0)
    tracks = build(lines)

    problems, notes = [], []
    problems += validate(lines)

    changes = 0
    for who, beats in tracks.items():
        # a character's own screen life ends with the episode
        for i, (t, emo) in enumerate(beats):
            nxt = beats[i + 1][0] if i + 1 < len(beats) else end
            held = nxt - t
            if held > MAX_HOLD_S:
                problems.append(
                    f"{who} holds '{emo}' for {held:.1f}s from t={t:g} "
                    f"(max {MAX_HOLD_S:g}s). That is a slide, not a performance.")
        changes += max(0, len(beats) - 1)

    if changes < MIN_CHANGES:
        problems.append(
            f"only {changes} expression change(s) in the episode, need {MIN_CHANGES}. "
            f"Case 0002 shipped with 3 and the owner could not feel anything.")

    # REACTIONS: a face change on a line somebody ELSE is speaking.
    reactions = 0
    for ln in lines:
        speaker = (ln.get("who") or "").upper()
        for who in (ln.get("face") or {}):
            if who.upper() in CHARACTERS and who.upper() != speaker:
                reactions += 1
    if reactions < MIN_REACTIONS:
        problems.append(
            f"only {reactions} listener reaction(s), need {MIN_REACTIONS}. Every "
            f"`face` entry names the character who is already talking, so nobody "
            f"in this episode reacts to anything. The joke lands on the LISTENER.")

    notes.append(f"{changes} expression changes, {reactions} listener reactions, "
                 f"{end:.1f}s")
    for who, beats in sorted(tracks.items()):
        notes.append(f"  {who:<4} " + " -> ".join(f"{e}@{t:g}s" for t, e in beats))
    return problems, notes


def run(path):
    try:
        script = json.load(open(path))
    except Exception as e:
        print(f"face_check: cannot read {path}: {e}", file=sys.stderr)
        return 1
    problems, notes = analyse(script)
    for n in notes:
        print("  " + n)
    if problems:
        print("\nface_check: FAIL")
        for p in problems:
            print("  - " + p)
        return 1
    print("\nface_check: PASS")
    return 0


def self_test():
    ok = True

    def script(lines, secs=30.0):
        return {"estimated_seconds": secs, "lines": lines}

    # The first draft of this fixture let Dee hold one face for 12s and the gate
    # correctly refused it. Keeping the note: the "good" case has to be good, or
    # a green self-test is measuring the fixture's sloppiness and not the rule.
    good = script([
        {"t": 0.0, "who": "RAY", "face": {"RAY": "angry", "DEE": "flat"}},
        {"t": 4.0, "who": "DEE", "face": {"DEE": "smug", "RAY": "squint"}},
        {"t": 8.0, "who": "RAY", "face": {"RAY": "shock"}},
        {"t": 12.0, "who": "DEE", "face": {"DEE": "flat", "RAY": "angry"}},
        {"t": 16.0, "who": "RAY", "face": {"RAY": "smug", "DEE": "squint"}},
        {"t": 20.0, "who": "DEE", "face": {"DEE": "smug"}},
        {"t": 24.0, "who": "RAY", "face": {"RAY": "flat", "DEE": "shock"}},
    ])
    p, _ = analyse(good)
    print(f"  {'ok  ' if not p else 'FAIL'} accepts an episode whose faces move"
          + ("  <- " + "; ".join(p) if p else ""))
    ok &= not p

    cases = [
        ("catches a face held for a whole shot",
         script([{"t": 0.0, "who": "RAY", "face": {"RAY": "angry", "DEE": "flat"}},
                 {"t": 2.0, "who": "DEE", "face": {"DEE": "smug"}},
                 {"t": 4.0, "who": "RAY", "face": {"RAY": "flat"}},
                 {"t": 6.0, "who": "DEE", "face": {"DEE": "squint"}},
                 {"t": 8.0, "who": "RAY", "face": {"RAY": "smug"}},
                 {"t": 9.0, "who": "DEE", "face": {"DEE": "shock"}}], 40.0)),
        ("catches an episode with almost no expression changes",
         script([{"t": 0.0, "who": "RAY", "face": {"RAY": "angry"}},
                 {"t": 5.0, "who": "DEE", "face": {"DEE": "flat"}}], 12.0)),
        ("catches a script where only the SPEAKER is ever directed",
         script([{"t": 0.0, "who": "RAY", "face": {"RAY": "angry"}},
                 {"t": 4.0, "who": "DEE", "face": {"DEE": "flat"}},
                 {"t": 8.0, "who": "RAY", "face": {"RAY": "smug"}},
                 {"t": 12.0, "who": "DEE", "face": {"DEE": "smug"}},
                 {"t": 16.0, "who": "RAY", "face": {"RAY": "shock"}},
                 {"t": 20.0, "who": "DEE", "face": {"DEE": "squint"}},
                 {"t": 24.0, "who": "RAY", "face": {"RAY": "flat"}}], 28.0)),
        ("catches a register the rig cannot draw",
         script([{"t": 0.0, "who": "RAY", "face": {"RAY": "livid"}}], 10.0)),
    ]
    for name, s in cases:
        p, _ = analyse(s)
        print(f"  {'ok  ' if p else 'FAIL'} {name}")
        ok &= bool(p)

    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=os.path.join(REPO, "out", "dispatch", "script.json"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.path)


if __name__ == "__main__":
    sys.exit(main())
