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
        ("PHASE 3.7 (the producer room)",
         "The ending is the one the viewer already had queued. The button used "
         "to be whatever the writer landed on at the end of a draft, which is "
         "why it kept being an afterthought: nothing owned it until it was too "
         "late to change. The producer now names the button, its document, its "
         "image and why Ray does not win BEFORE a line is written, and the plan "
         "binds every later phase. Ownership moved from 4.4, which is the "
         "director now."),
    "beautiful_and_unfunny":
        ("PHASE 3.7 (the producer room) and 4.2 (the world)",
         "The set is excellent and the episode contains no joke. This is NOT "
         "carried_by_fact, and the distinction matters because retro routes on "
         "it: carried_by_fact is the DIALOGUE doing all the work under a live "
         "fact, this is a live WORLD under no joke at all. The taxonomy was "
         "written when the sets were inert and had no word for a set that is "
         "doing everything and still is not funny. Count the gags that survive "
         "their own safety guards unamended; if the answer is zero, the world "
         "was designed on the assumption a laugh would arrive later."),
    "artifacts_fork":
        ("PHASE 4.2 (the world), at handoff",
         "The plan and the world describe different films and nobody ruled on "
         "it. The room converged on the SET and never on the STORY. "
         "scripts/coherence_check.py catches the mechanical half; a recurrence "
         "means it is missing a field."),
    "repeated_trick":
        ("PHASE 4 (the writers room)",
         "The same comic move twice in one episode."),
    "irony_wrong_way":
        ("PHASE 4.4 (the button)",
         "A joke makes the INSTITUTION the sympathetic party."),
}


class LedgerCorrupt(RuntimeError):
    """Present and unreadable. Never confused with absent."""


def _load():
    """The verdict ledger, or a fresh one IF AND ONLY IF the file is absent.

    2026-08-02, repo-wide review: this was `except Exception: return <empty>`
    and `_save` wrote non-atomically to the final path, so a process killed
    mid-write produced exactly the corruption this handler swallowed. Verified
    against a truncated file: `retro: no verdicts recorded yet.` then `retro:
    PASS. Every repeat offender has an upgrade logged against it.` exit 0, and
    the next --record OVERWROTE THE WHOLE HISTORY with one entry.

    This ledger is the machine's only memory of its own repetition. Silently
    forgetting it and reporting PASS is worse than crashing, because the whole
    point of the file is that a defect seen twice gets escalated.
    """
    if not os.path.exists(LEDGER):
        return _blank()
    try:
        with open(LEDGER) as fh:
            doc = json.load(fh)
    except Exception as e:
        raise LedgerCorrupt(
            f"{LEDGER} exists and cannot be parsed ({e}). This is the machine's "
            f"cross-run memory and it is unreadable, so no repeat offender can be "
            f"detected this run and --record would overwrite the history with one "
            f"entry. Restore it from git before recording anything."
        ) from e
    if not isinstance(doc, dict) or not isinstance(doc.get("entries"), list):
        raise LedgerCorrupt(f"{LEDGER} parsed but has no `entries` array.")
    return doc


def _blank():
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
    # ATOMIC, because a torn write here is the corruption _load now refuses, and
    # this file is appended to on every recorded verdict.
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LEDGER)


def record(entry):
    doc = _load()
    doc["entries"].append(entry)
    _save(doc)
    return len(doc["entries"])


def run_key(e):
    """What makes two verdicts come from DIFFERENT runs.

    2026-08-02, repo-wide review: this was `e.get("case")`, so every entry that
    omitted `case` collapsed into the single key None. Two genuine repeats from
    two different runs counted as one, and a standing repeat offender went
    undetected by the one function whose whole job is detecting it. The run_date
    disambiguates re-runs of the same case, and an entry carrying NEITHER cannot
    be attributed to a run at all, so it is refused rather than merged.
    """
    case, date = e.get("case"), e.get("run_date")
    if case is None and not date:
        raise ValueError(
            "a verdict entry carries neither `case` nor `run_date`, so it cannot "
            "be attributed to a run. Entries like this used to collapse into one "
            "key and hide repeats: " + json.dumps(e)[:200])
    return (case, date)


def repeat_offenders(entries=None, threshold=REPEAT_AT):
    """-> {defect: {"runs": [label...], "count": n}} for defects across >=N runs."""
    ent = entries if entries is not None else _load()["entries"]
    seen = {}
    for e in ent:
        k = run_key(e)
        for d in e.get("defects", []):
            seen.setdefault(d, set()).add(k)
    return {d: {"runs": [f"{c if c is not None else '?'}@{dt or '?'}"
                         for c, dt in sorted(k, key=lambda x: (str(x[0]), str(x[1])))],
                "count": len(k)}
            for d, k in seen.items() if len(k) >= threshold}


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

    # RED: two verdicts from two different runs that both omit `case` used to
    # collapse into the single key None and count as ONE run, so a genuine
    # repeat offender was invisible to the function that exists to find it.
    dateless = [{"run_date": "2026-08-01", "critic": "funny",
                 "defects": ["carried_by_fact"]},
                {"run_date": "2026-08-02", "critic": "funny",
                 "defects": ["carried_by_fact"]}]
    checks.append(("two runs with no case number are still TWO runs",
                   "carried_by_fact" in repeat_offenders(dateless)))
    # And the same case re-scored on the same day is still ONE run.
    same = [{"case": 3, "run_date": "2026-08-02", "critic": "funny", "read": 1,
             "defects": ["carried_by_fact"]},
            {"case": 3, "run_date": "2026-08-02", "critic": "funny", "read": 2,
             "defects": ["carried_by_fact"]}]
    checks.append(("the same case re-read on the same day is ONE run",
                   not repeat_offenders(same)))
    try:
        repeat_offenders([{"critic": "funny", "defects": ["x"]}])
        checks.append(("refuses a verdict that belongs to no run", False))
    except ValueError:
        checks.append(("refuses a verdict that belongs to no run", True))

    # RED: the ledger PRESENT and unreadable must never report "no verdicts yet"
    # and pass. That state also let --record overwrite the whole history.
    import tempfile
    global LEDGER
    keep = LEDGER
    try:
        with tempfile.TemporaryDirectory() as d:
            LEDGER = os.path.join(d, "verdicts.json")
            _save({"entries": list(two)})
            open(LEDGER, "w").write('{"entries": [{"case": 2')   # truncated
            try:
                report()
                checks.append(("refuses a CORRUPT ledger instead of reporting none", False))
            except LedgerCorrupt:
                checks.append(("refuses a CORRUPT ledger instead of reporting none", True))
            os.remove(LEDGER)
            checks.append(("an ABSENT ledger is still an empty one",
                           report() == ["retro: no verdicts recorded yet."]))
    finally:
        LEDGER = keep

    for name, good in checks:
        print(f"  {'ok  ' if good else 'FAIL'} {name}")
        ok &= bool(good)
    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def slug(row_name):
    """A gate row's human name -> a stable defect slug the ledger can count."""
    import re as _re
    t = _re.sub(r"[^a-z0-9]+", "_", row_name.strip().lower()).strip("_")
    return f"gate_{t}"[:64]


def record_gate(gate, failed_rows, case=None, run_date=None):
    """Record a GATE failure into the same cross-run memory as a critic verdict.

    Owner, 2026-08-03: "any repeat offenders in the quality gates that the judges
    kept seeing, those root cause should be fixed."

    Until now this ledger only remembered what the CRITICS said. A gate could
    fail on the same guard every run forever and nothing counted it, so each run
    fixed the artifact and moved on and the underlying cause was never touched.
    That is the same "each run re-learns it" failure the ledger was built to end,
    one layer down.

    Gate failures reuse the critic schema on purpose rather than getting their
    own table: `repeat_offenders()` already counts defect slugs across distinct
    runs, and `check()` already refuses to pass until an upgrade claims a repeat
    offender by slug. Recording gates as `critic="gate:<name>"` means both of
    those work on gate failures for free, and a gate that keeps failing is
    escalated to a PROCESS defect exactly like a critic note that keeps
    recurring.
    """
    return record({
        "case": case,
        "run_date": run_date,
        "critic": f"gate:{gate}",
        "defects": [slug(r) for r in failed_rows if str(r).strip()],
        "note": f"{gate} failed {len(failed_rows)} row(s): "
                + "; ".join(str(r)[:60] for r in failed_rows[:4]),
    })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", help="a JSON file holding one verdict entry")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--record-gate", metavar="GATE",
                    help="record a GATE failure into cross-run memory")
    ap.add_argument("--failed", default="",
                    help="with --record-gate: comma-separated failing row names")
    ap.add_argument("--case", type=int)
    ap.add_argument("--run-date")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.record_gate:
        rows = [r for r in a.failed.split(",") if r.strip()]
        if not rows:
            print("retro: --record-gate needs --failed with at least one row",
                  file=sys.stderr)
            return 1
        n = record_gate(a.record_gate, rows, case=a.case, run_date=a.run_date)
        print(f"retro: recorded gate failure for {a.record_gate}, "
              f"{len(rows)} row(s), {n} verdict(s) on file")
        return 0
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
