#!/usr/bin/env python3
"""script_check.py: Gate 0's mechanical half. Run it on the script, before any
scene code exists.

WHY THIS EXISTS

Gate 0 is seven prose bullets judged by a model. Two of them are arithmetic and
were being judged by eye, and both got through on case 0002:

1. **The claim-ids.** The `sourced` hard gate says every factual line traces to a
   verified claim. Nothing checked that the ids in the script actually RESOLVE,
   or that the claim they resolve to was not CUT by the fact-checker. Case 0002
   cut claim c11 (the record never says the 28 speakers failed) and the only
   thing standing between that cut claim and the script was a paragraph in a
   WORKLOG. Prose does not bind a script. A dangling id is a line with no
   source; a CUT id is worse, because it is a line the fact-checker already
   killed. Both are the failure that ends a channel, and both are one `in` away
   from being impossible.

2. **Ray's cadence.** CAST_BIBLE: "Every episode is, structurally, Ray finding
   out", and its five-beat table gives him 20-40s, the beat literally named "Ray
   finds out. The show." Case 0002 shipped with Ray silent for 27.9 seconds and
   with NO Ray line anywhere in the middle third. The flow critic and the scorer
   both found it, and both found it AFTER a full-res render and a panel round.
   It is two subtractions on a JSON file. It belongs at Gate 0, where the fix is
   free.

This deliberately does NOT re-check what vo_cast.py already checks (casting,
overlap, the Institution's line budget, the 60s law). Two gates enforcing one
rule drift apart; that is how build_scenes.py's TAIL and the routine's ceiling
got out of sync once already.

  python3 scripts/script_check.py                     # out/dispatch/{script,claims}.json
  python3 scripts/script_check.py --script X --claims Y
  python3 scripts/script_check.py --self-test         # prove it can go red

Exit 0 pass, 1 fail.
"""

import argparse
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "out", "dispatch")

# Ray may not be gone longer than one whole named beat of the five-beat shape in
# CAST_BIBLE.md (the beats are 5 to 20 seconds wide). Calibrated against the two
# scripts that exist: case 0001's longest Ray gap is 11.4s and reads fine; case
# 0002's is 27.9s and both the flow critic and the scorer called it out.
MAX_RAY_GAP_S = 20.0

# Anything the fact-checker did not leave standing. Case 0002's claims.json uses
# `status`, case 0001's used `ruling`; accept either rather than force one
# schema on a file the fact-checker writes.
STATUS_FIELDS = ("status", "ruling", "verdict", "state")
NOT_USABLE = ("cut", "kill", "reject", "unverified", "unproven", "fail", "drop")

# ---------------------------------------------------------------------------
# THE CAST SPEAK LIKE PEOPLE. (owner, 2026-08-02)
#
# "ban the word 'cannot', and use the word 'can't' instead" and "lean toward
# 'there's' instead of 'there is' as it sounds more natural".
#
# This is a gate rather than a note in the writer prompt because the uncontracted
# form is exactly what a model reaches for by default, and it is the difference
# between a person talking and a document being read aloud, which is the single
# most repeated complaint this show has had.
#
# It also costs RUNTIME. Every uncontracted pair is a syllable the sixty second
# law has to pay for, and the show is always short of seconds.
#
# A line may opt out with "verbatim": true, for a quote that must not be altered.
CONTRACTIONS = {
    "cannot": "can't", "can not": "can't",
    "there is": "there's", "there are": "there're",
    "it is": "it's", "that is": "that's", "what is": "what's",
    "do not": "don't", "does not": "doesn't", "did not": "didn't",
    "is not": "isn't", "are not": "aren't", "was not": "wasn't",
    "will not": "won't", "would not": "wouldn't", "could not": "couldn't",
    "should not": "shouldn't", "have not": "haven't", "has not": "hasn't",
    "you are": "you're", "they are": "they're", "we are": "we're",
    "i am": "I'm", "you will": "you'll", "they will": "they'll",
    "let us": "let's",
}


def load(path):
    return json.load(open(path))


def claim_index(claims_doc):
    """id -> claim, for whichever shape the fact-checker wrote."""
    claims = claims_doc.get("claims", claims_doc) if isinstance(claims_doc, dict) else claims_doc
    return {c["id"]: c for c in claims if isinstance(c, dict) and "id" in c}


def claim_is_cut(claim):
    for f in STATUS_FIELDS:
        v = claim.get(f)
        if isinstance(v, str) and any(w in v.lower() for w in NOT_USABLE):
            return v
    return None


def conjunction_openers(lines):
    """-> [(t, word)] for any line whose SENTENCE starts with And or But.

    Owner, 2026-08-02: "ban starting sentences with 'And or But' ever."

    It is a real writing tic and not just taste: an opener like that makes the
    line sound appended to the previous one, so the delivery inherits the last
    line's energy instead of starting its own. In a two-hander where every line
    is a new speaker taking the floor, that is exactly wrong.
    """
    import re as _re
    out = []
    for ln in lines:
        if ln.get("verbatim"):
            continue
        txt = _re.sub(r"\[[^\]]*\]", " ", ln.get("text", "")).strip()
        for sentence in _re.split(r"(?<=[.!?])\s+", txt):
            m = _re.match(r"^\s*(And|But)\b", sentence.strip(), _re.I)
            if m:
                out.append((ln.get("t"), m.group(1)))
    return out


def stilted(lines):
    """-> [(t, found, want)] for every uncontracted pair a person would contract."""
    import re as _re
    out = []
    for ln in lines:
        if ln.get("verbatim"):
            continue
        txt = _re.sub(r"\[[^\]]*\]", " ", ln.get("text", "")).lower()
        for found, want in CONTRACTIONS.items():
            if _re.search(r"(?<![\w'])" + _re.escape(found) + r"(?![\w'])", txt):
                out.append((ln.get("t"), found, want))
    return out


def spans(lines):
    """[(t, end, who)]. A line runs until the next line starts. Pre-VO there are
    no durations, so this is the only honest span available, and it is the same
    assumption the storyboard is cut to."""
    ordered = sorted(lines, key=lambda l: l["t"])
    out = []
    for i, l in enumerate(ordered):
        end = ordered[i + 1]["t"] if i + 1 < len(ordered) else None
        out.append((l["t"], end, l["who"]))
    return out


def check(script, claims_doc):
    """The guards. Returns [(name, ok, detail)]."""
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d))
        return ok

    lines = script.get("lines")
    if not isinstance(lines, list) or not lines:
        # A verdict, not a traceback. `script["lines"]` on a malformed document
        # raised KeyError and printed a stack trace where a FAIL row belongs, and
        # a gate that crashes has not failed the work, it has failed to run.
        row("the script document has lines", False,
            "no `lines` array, or it is empty. There is nothing to check, which is "
            "not the same as nothing being wrong.")
        return rows

    idx = claim_index(claims_doc)

    # THE CLAIM SET MUST EXIST BEFORE IT CAN RESOLVE.
    #
    # 2026-08-02, repo-wide review: a script citing NOTHING, checked against an
    # EMPTY claims.json, printed `ok  every claim-id resolves  0 distinct id(s),
    # all found` and exited 0. Vacuous truth read as a pass on the house's first
    # law. The set being empty is the failure; resolution is the second question.
    row("claims.json carries a cleared claim set", bool(idx),
        f"{len(idx)} cleared claim(s)" if idx else
        "claims.json yielded ZERO claims. Phase 2 either did not run or cleared "
        "nothing, and every citation row below is vacuously true against it.")

    cited = [(l, c) for l in lines for c in l.get("claims", [])]
    row("the script cites its sources at all", bool(cited),
        f"{len(cited)} citation(s) across {len({id(l) for l, _ in cited})} line(s)"
        if cited else
        "NOT ONE line carries a claim-id. `No claim without a source` is the "
        "first house rule, and a script that cites nothing satisfies every "
        "citation check by having nothing to check.")

    dangling = sorted({c for _, c in cited if c not in idx})
    row("every claim-id resolves in claims.json", not dangling,
        f"{len(dangling)} dangling: {dangling[:4]}" if dangling
        else f"{len({c for _, c in cited})} distinct id(s), all found")

    cut = sorted({f"{c}({claim_is_cut(idx[c])})" for _, c in cited
                  if c in idx and claim_is_cut(idx[c])})
    row("no line cites a claim the fact-checker cut", not cut,
        f"{len(cut)} cut: {cut[:4]}" if cut else "clean")

    est = float(script.get("estimated_seconds") or 0.0)
    ray = [(t, end if end is not None else est) for t, end, who in spans(lines)
           if who == "RAY"]

    # Longest stretch with no Ray in it, counting the head (does the show open
    # without him) and the tail (does he get the last word).
    if ray:
        starts = [t for t, _ in ray]
        gaps = [(starts[0], 0.0)] + [(starts[i + 1] - starts[i], starts[i])
                                     for i in range(len(starts) - 1)]
        gaps += [(max(0.0, est - starts[-1]), starts[-1])]
        worst, at = max(gaps)
    else:
        worst, at = est, 0.0
    row(f"Ray is never gone longer than {MAX_RAY_GAP_S}s",
        worst <= MAX_RAY_GAP_S,
        f"longest silence {worst:.1f}s from {at:.1f}s"
        + ("" if worst <= MAX_RAY_GAP_S else "  <- give him a line inside it"))

    # The middle third is the beat CAST_BIBLE names "Ray finds out. The show."
    # Proportional rather than a literal 20-40 window so it holds for a 45s
    # episode as well as a 58s one.
    lo, hi = est / 3.0, est * 2.0 / 3.0
    inside = [t for t, e in ray if t < hi and e > lo]
    co = conjunction_openers(script["lines"])
    row("no sentence opens with And or But", not co,
        "clean" if not co else "; ".join(f"t={a}: '{b}'" for a, b in co[:4]))

    st = stilted(script["lines"])
    row("the cast speak like people, not documents", not st,
        "clean" if not st else "; ".join(f"t={a}: '{b}' -> '{c}'" for a, b, c in st[:4]))

    row("Ray speaks in the middle third", bool(inside),
        f"{len(inside)} line(s) in {lo:.1f}-{hi:.1f}s" if inside
        else f"NONE in {lo:.1f}-{hi:.1f}s, the beat named 'Ray finds out'")
    return rows


def run(script_path, claims_path):
    script = load(script_path)
    claims_doc = load(claims_path)
    rows = check(script, claims_doc)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<44} {d}")
    if all(o for _, o, _ in rows):
        print("\nscript_check: Gate 0's mechanical half is clean.")
        return 0
    print("\nscript_check: FAIL. Fix the SCRIPT, not this file. Gate 0 is the "
          "cheap save;\n              the same fix after a render costs a full "
          "render.")
    return 1


def self_test():
    """Prove every guard fires, and that a good script still passes.

    Each case names the guard it is supposed to trip, and the fixture is built so
    that ONLY that guard trips. "Some row went red" is not a test: the first cut
    of this self-test asserted exactly that, and disabling the Ray-gap guard
    entirely still printed all green, because the same fixture also had no Ray in
    the middle third and the neighbouring guard covered for the dead one. A
    self-test that cannot isolate cannot detect a broken guard, which is the
    same "gate that cannot fail" trap one level up.
    """
    claims = {"claims": [
        {"id": "c1", "status": "VERIFIED"},
        {"id": "c2", "status": "VERIFIED"},
        {"id": "c3", "status": "CUT"},
    ]}

    def script(lines, est=54.0):
        return {"estimated_seconds": est, "lines": lines}

    good = script([
        {"t": 0.0, "who": "RAY", "text": "The fact.", "claims": ["c1"]},
        {"t": 6.0, "who": "DEE", "text": "The detail.", "claims": ["c2"]},
        {"t": 14.0, "who": "RAY", "text": "So fix it.", "claims": []},
        {"t": 22.0, "who": "DEE", "text": "They did.", "claims": ["c2"]},
        {"t": 30.0, "who": "RAY", "text": "The verdict.", "claims": []},
        {"t": 40.0, "who": "INSTITUTION", "text": "We value you.", "claims": ["c1"]},
        {"t": 50.0, "who": "RAY", "text": "The button.", "claims": []},
    ])

    cases = [
        # RED: the uncontracted form is what a model reaches for by default and it
        # is the difference between a person talking and a document read aloud.
        ("a line nobody would say out loud", "speak like people",
         script([dict(good["lines"][0], text="There is a thing you cannot argue with.")]
                + good["lines"][1:])),
        ("a line that opens on a conjunction", "And or But",
         script([dict(good["lines"][0], text="And then they did it again.")]
                + good["lines"][1:])),
        ("a claim-id that resolves to nothing", "resolves",
         script([dict(good["lines"][0], claims=["c9"])] + good["lines"][1:])),
        ("a line citing a claim the fact-checker CUT", "cut",
         script([dict(good["lines"][0], claims=["c3"])] + good["lines"][1:])),
        # Ray IS in the middle third here (22.0-28.0 against 18.0-36.0), so only
        # the gap guard can catch the 22s hole between his lines.
        ("Ray gone longer than one whole beat", "never gone longer",
         script([{"t": 0.0, "who": "RAY", "text": "The fact.", "claims": ["c1"]},
                 {"t": 5.0, "who": "DEE", "text": "block", "claims": ["c2"]},
                 {"t": 22.0, "who": "RAY", "text": "the middle", "claims": []},
                 {"t": 28.0, "who": "DEE", "text": "block", "claims": ["c2"]},
                 {"t": 40.0, "who": "RAY", "text": "back", "claims": []},
                 {"t": 50.0, "who": "RAY", "text": "the button", "claims": []}])),
        # Every Ray gap here is 18s or under, so only the middle-third guard can
        # catch him stepping around the beat named after him (15.0-30.0).
        ("Ray absent from the middle third", "middle third",
         script([{"t": 0.0, "who": "RAY", "text": "The fact.", "claims": ["c1"]},
                 {"t": 5.0, "who": "DEE", "text": "block", "claims": ["c2"]},
                 {"t": 13.0, "who": "RAY", "text": "So fix it.", "claims": []},
                 {"t": 14.5, "who": "DEE", "text": "block", "claims": ["c2"]},
                 {"t": 24.0, "who": "DEE", "text": "block", "claims": ["c2"]},
                 {"t": 31.0, "who": "RAY", "text": "back", "claims": []},
                 {"t": 40.0, "who": "RAY", "text": "the button", "claims": []}],
                est=45.0)),
        # The one case that is legitimately not isolable: a script with no Ray in
        # it fails both Ray guards by definition, so it declares both.
        ("a script with no Ray in it at all", "never gone longer|middle third",
         script([{"t": 0.0, "who": "DEE", "text": "All mine.", "claims": ["c1"]},
                 {"t": 30.0, "who": "INSTITUTION", "text": "Ours.", "claims": ["c2"]}])),
        # THE VACUOUS PASS. A script that cites NOTHING, against an EMPTY claim
        # set, printed `ok  every claim-id resolves  0 distinct id(s), all found`
        # and exited 0 before 2026-08-02. Both halves are tested, because either
        # one alone is a different failure: no citations is a writer defect, no
        # cleared claims is a Phase 2 defect, and the pair is the one that was
        # certifying itself.
        ("a script that cites no source at all", "cites its sources",
         script([dict(l, claims=[]) for l in good["lines"]])),
        # Not isolable, and it declares both: a script that cites properly
        # against an EMPTY claim set has ids that cannot resolve by definition.
        # The point of the new row is that the empty set is named as the cause,
        # instead of the run reading four dangling ids as a writer's typo.
        ("a claims.json that cleared nothing", "carries a cleared claim set|resolves",
         good, {"claims": []}),
        ("a document with no lines at all", "has lines", {"lines": []}),
    ]

    ok = True
    for case in cases:
        name, guards, s = case[0], case[1], case[2]
        case_claims = case[3] if len(case) > 3 else claims
        want = guards.split("|")
        rows = check(s, case_claims)
        missed = [g for g in want
                  if not any(g in n and not o for n, o, _ in rows)]
        others = [n for n, o, _ in rows
                  if not o and not any(g in n for g in want)]
        good_case = not missed and not others
        print(f"  {'ok  ' if good_case else 'FAIL'} catches: {name}"
              + (f"   <- did NOT fire: {missed}" if missed else "")
              + (f"   <- not isolated, also fired: {others}" if others else ""))
        ok &= good_case

    rows = check(good, claims)
    clean = all(o for _, o, _ in rows)
    if not clean:
        for n, o, d in rows:
            if not o:
                print(f"       (good script tripped '{n}': {d})")
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a well-formed script")
    ok &= clean

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", help="default out/dispatch/script.json")
    ap.add_argument("--claims", help="default out/dispatch/claims.json")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(a.script or os.path.join(OUT, "script.json"),
               a.claims or os.path.join(OUT, "claims.json"))


if __name__ == "__main__":
    sys.exit(main())
