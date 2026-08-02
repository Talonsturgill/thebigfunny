#!/usr/bin/env python3
"""retro.py — a defect that recurs is a PROCESS defect, and the machine says so.

WHY THIS EXISTS
The funny critic failed case 0002 (76, "inert in between") and then failed case
0003 six times running (57, 58, 63, 69, 64, 63), and both times it named the same
cause: the STORY was not absurd enough for any writing to rescue. Each run read
that note, rewrote the script, and moved on. Nothing counted.

That is the actual failure. The critic sits at Phase 6, downstream of the story
pick at Phase 3 and the angle at Phase 3.5, so it can only ever report a decision
that was already made and paid for. A gate that keeps failing for one reason is
not a quality problem, it is a DESIGN problem one phase upstream, and a machine
that cannot notice its own repetition will re-learn the same lesson forever.

WHAT THIS DOES
  - `record` writes every critic verdict to ledger/verdicts.json, per run.
  - `check` reads the whole history and finds REPEAT OFFENDERS: a defect that
    has now appeared in N or more runs.
  - A repeat offender is escalated from "fix the script" to "fix the PROCESS",
    with the phase that owns it named, because the run that hits it is not
    allowed to just rewrite and continue.

  python3 scripts/retro.py                       # the standing report
  python3 scripts/retro.py --record verdict.json # append one critic result
  python3 scripts/retro.py --check               # exit 1 if a repeat is unaddressed
  python3 scripts/retro.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(REPO, "ledger", "verdicts.json")

# A defect seen in this many DISTINCT runs stops being bad luck.
REPEAT_AT = 2

# Which phase owns each defect. This is the whole point: the fix for a repeat
# offender belongs where the decision was made, not where it was detected.
OWNER = {
    "agreement_not_comedy":
        ("PHASE 3 (pick the story) and 3.5 (the angle)",
         "The critic cannot make a story absurd. If episodes keep scoring as "
         "'a true fact with a tone of voice', the STORY SELECTION is admitting "
         "material that was never funny. Gate absurdity BEFORE the angle room."),
    "carried_by_fact":
        ("PHASE 3 (pick the story)",
         "The fact is doing all the work and the writing none. Same root as "
         "agreement_not_comedy: the run keeps picking infuriating over absurd."),
    "aphorism":
        ("PHASE 4 (the writers room)",
         "The writer reaches for a sentence that already exists on the internet. "
         "COMEDY_CRAFT.md bans it; if it recurs, the ban needs to be a GATE."),
    "explaining_lines":
        ("PHASE 4 (the writers room)",
         "A line explains the line above it. Already a house rule, so recurrence "
         "means the rule is not being enforced mechanically."),
    "ray_prompts":
        ("PHASE 4 (the writers room)",
         "Ray asks questions instead of arriving at verdicts, which contradicts "
         "the cast law. Recurrence means script_check should count his questions."),
    "button_doesnt_land":
        ("PHASE 4.4 (the button)",
         "The ending is the one the viewer already had queued. The button is "
         "chosen before the script is written and keeps being an afterthought."),
    "repeated_trick":
        ("PHASE 4 (the writers room)",
         "The same comic move twice in one episode."),
    "irony_wrong_way":
        ("PHASE 4.4 (the button)",
         "A joke makes the INSTITUTION the sympathetic party."),
}


def _load():
    try:
        return json.load(open(LEDGER))
    except Exception:
        return {
            "_spec": {
                "purpose": "Every critic verdict, every run, so the machine can see "
                           "its own repetition. A defect in REPEAT_AT or more distinct "
                           "runs is escalated from a script problem to a PROCESS "
                           "problem, and retro.py names the phase that owns it.",
                "why": "The funny critic failed two consecutive episodes for the same "
                       "reason and nothing counted, so each run re-learned it and moved "
                       "on. Cross-run memory is the difference between a machine that "
                       "improves and one that merely repeats.",
                "entry_schema": {
                    "case": "int", "run_date": "YYYY-MM-DD", "critic": "funny|flow|...",
                    "score": "int", "read": "which pass, 1-based",
                    "defects": ["stable slugs, see retro.OWNER"],
                    "note": "the critic's own killer sentence, verbatim",
                },
            },
            "entries": [],
        }


def _save(doc):
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    json.dump(doc, open(LEDGER, "w"), indent=2, ensure_ascii=False)
    open(LEDGER, "a").write("\n")


def record(entry):
    doc = _load()
    doc["entries"].append(entry)
    _save(doc)
    return len(doc["entries"])


def repeat_offenders(entries=None, threshold=REPEAT_AT):
    """-> {defect: {"runs": [case...], "count": n}} for defects across >=N runs."""
    ent = entries if entries is not None else _load()["entries"]
    seen = {}
    for e in ent:
        for d in e.get("defects", []):
            seen.setdefault(d, set()).add(e.get("case"))
    return {d: {"runs": sorted(c), "count": len(c)}
            for d, c in seen.items() if len(c) >= threshold}


def report(entries=None):
    ent = entries if entries is not None else _load()["entries"]
    lines = []
    if not ent:
        return ["retro: no verdicts recorded yet."]

    by_case = {}
    for e in ent:
        by_case.setdefault(e.get("case"), []).append(e)
    lines.append("SCORES BY RUN")
    for case in sorted(by_case):
        for critic in sorted({x.get("critic") for x in by_case[case]}):
            reads = [x for x in by_case[case] if x.get("critic") == critic]
            reads.sort(key=lambda x: x.get("read", 0))
            scores = ", ".join(str(x.get("score")) for x in reads)
            lines.append(f"  case {case:>4}  {critic:<6}  {scores}")

    rep = repeat_offenders(ent)
    if not rep:
        lines.append("\nNo repeat offenders. Defects are being fixed and staying fixed.")
        return lines

    lines.append(f"\nREPEAT OFFENDERS (seen in {REPEAT_AT}+ distinct runs)")
    lines.append("A defect this persistent is not a script problem. It is a PROCESS")
    lines.append("problem in the phase that MADE the decision, not the one that caught it.")
    for d, info in sorted(rep.items(), key=lambda kv: -kv[1]["count"]):
        phase, why = OWNER.get(d, ("PHASE UNKNOWN", "No owner mapped. Map it in retro.OWNER."))
        lines.append(f"\n  {d}  ({info['count']} runs: {info['runs']})")
        lines.append(f"    OWNER: {phase}")
        lines.append(f"    {why}")
    return lines


def check(entries=None, addressed=None):
    """Exit non-zero while a repeat offender has no upgrade against it.

    `addressed` is the set of defect slugs some entry in ledger/upgrades.json
    claims to have fixed, so closing one out is done by SHIPPING a change, not by
    editing this file."""
    ent = entries if entries is not None else _load()["entries"]
    if addressed is None:
        addressed = set()
        try:
            up = json.load(open(os.path.join(REPO, "ledger", "upgrades.json")))
            for e in up.get("entries", []):
                for d in e.get("addresses", []):
                    addressed.add(d)
        except Exception:
            pass
    rep = repeat_offenders(ent)
    open_ = {d: i for d, i in rep.items() if d not in addressed}
    for line in report(ent):
        print(line)
    if open_:
        print(f"\nretro: FAIL. {len(open_)} repeat offender(s) with no upgrade against them:")
        for d in sorted(open_):
            phase, _ = OWNER.get(d, ("PHASE UNKNOWN", ""))
            print(f"  - {d}: fix {phase}, then log it in ledger/upgrades.json with "
                  f'"addresses": ["{d}"]')
        print("  Rewriting the artifact again is not a fix. The decision upstream is.")
        return 1
    print("\nretro: PASS. Every repeat offender has an upgrade logged against it.")
    return 0


def self_test():
    ok = True
    one = [{"case": 2, "critic": "funny", "score": 76, "read": 1,
            "defects": ["agreement_not_comedy"]}]
    two = one + [{"case": 3, "critic": "funny", "score": 57, "read": 1,
                  "defects": ["agreement_not_comedy", "aphorism"]}]

    checks = [
        ("one run is not a pattern", not repeat_offenders(one)),
        ("the SAME defect in two runs is", "agreement_not_comedy" in repeat_offenders(two)),
        ("a one-off in the second run is not",
         "aphorism" not in repeat_offenders(two)),
        ("names the phase that OWNS it, not the one that caught it",
         "PHASE 3" in "\n".join(report(two))),
    ]

    # RED: an open repeat offender fails the retro.
    checks.append(("fails while a repeat offender is unaddressed",
                   check(two, addressed=set()) == 1))
    # ...and closing it requires a SHIPPED upgrade that claims it.
    checks.append(("passes once an upgrade claims it",
                   check(two, addressed={"agreement_not_comedy"}) == 0))

    for name, good in checks:
        print(f"  {'ok  ' if good else 'FAIL'} {name}")
        ok &= bool(good)
    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", help="a JSON file holding one verdict entry")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.record:
        n = record(json.load(open(a.record)))
        print(f"retro: recorded, {n} verdict(s) on file")
        return 0
    if a.check:
        return check()
    for line in report():
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
