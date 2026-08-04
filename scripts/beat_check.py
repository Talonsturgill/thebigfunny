#!/usr/bin/env python3
"""beat_check — is this a STORY, or a list of observations?

    python3 scripts/beat_check.py                       # out/dispatch/story.json
    python3 scripts/beat_check.py --story path.json
    python3 scripts/beat_check.py --self-test

WHY THIS EXISTS (owner, 2026-08-03, on case 0003):

    "it made no sense" / "there wasn't anything like coherent about it"

Both notes are the same defect and it has a name. Trey Parker, NYU Tisch guest
lecture (routinely misattributed to the documentary "6 Days to Air"; it is the
NYU class, https://speakola.com/arts/matt-stone-trey-parker-nyu-writing-class-2014):

    "if the words 'and then' belong between those beats, you're fucked."
    "What should happen between every beat that you've written down, is either
     the word 'therefore' or 'but'."
    "Literally we'll sometimes write it out to make sure we're doing it."

That last line is why this gate can exist. The connective is a WRITTEN ARTIFACT,
not a vibe, so it can be linted.

Case 0003's beats were joined by "and then" on nearly every seam: one eviction
case, and then a report goes to a landlord, and then he got sued once, and then
somebody got paid. Nothing caused anything. A script like that reads as a list
of observations no matter how good each observation is, which is exactly what
two independent blind funny reads reported.

## THE SPLIT, stated honestly

This gate is the LINT HALF and it does not pretend otherwise:

  - a connective exists on every seam, and it is exactly BUT or THEREFORE
  - no banned connective appears anywhere in the beats
  - the connectives alternate rather than being six THEREFOREs in a row
  - every BUT names the expectation it violates, in under ten words
  - the two-hander declares opposed wants
  - every beat declares its own joke

The JUDGEMENT HALF cannot be linted and belongs to the flow critic as three
yes/no questions, because a writer can label any two beats THEREFORE and no
string check can disprove it:

  Test A, deletion: delete beat N. If N+1 still makes sense, the link was
                    "and then".
  Test B, swap:     swap N and N+1. If the script still parses, they are not
                    causally linked.
  Test C, named expectation: does the named expectation actually follow from
                    beat N, or was a clause written to satisfy this gate?

A run that passes the lint and skips the judgement has not passed Gate 0. Saying
so here because this repo's oldest lesson is that a check which did not run reads
exactly like a check that passed.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(REPO, "out", "dispatch", "story.json")

LINKS = ("BUT", "THEREFORE")
# "meanwhile" is the B-plot connective. Legitimate in 22 minutes because the
# plots converge causally later. In 60 seconds there is no meanwhile: one plot.
BANNED = ("and then", "meanwhile", "at the same time", "after that",
          "later on", "subsequently", "and also")
MIN_BEATS, MAX_BEATS = 5, 7
MIN_EACH_LINK = 2
MAX_EXPECT_WORDS = 10


def load(path):
    try:
        with open(path) as f:
            return json.load(f), None
    except FileNotFoundError:
        return None, f"{path} does not exist"
    except Exception as e:
        return None, f"{path} is unreadable: {e}"


def check(doc):
    """-> [(name, ok, detail)]. A missing field FAILS; it never skips.

    Skipping on absence is how coherence_check certified two documents that had
    both failed to declare the most load-bearing beat in the episode. Silence is
    not agreement.
    """
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d))
        return ok

    if not isinstance(doc, dict):
        row("the story document parses as an object", False, f"got {type(doc).__name__}")
        return rows

    beats = doc.get("beats")
    if not isinstance(beats, list) or not beats:
        row("the story declares a beats block", False,
            "no `beats` array. Parker: 'literally we'll sometimes write it out'. "
            "If the chain is not written down, there is nothing to check and "
            "nothing to trust.")
        return rows
    row("the story declares a beats block", True, f"{len(beats)} beat(s)")

    row(f"beat count is {MIN_BEATS}-{MAX_BEATS} (the causal six)",
        MIN_BEATS <= len(beats) <= MAX_BEATS, f"{len(beats)}")

    # ---- every beat is a beat -------------------------------------------------
    missing_text = [i for i, b in enumerate(beats)
                    if not isinstance(b, dict) or not str(b.get("text", "")).strip()]
    row("every beat says what happens", not missing_text,
        "clean" if not missing_text else f"beat(s) {missing_text} have no text")

    # A beat with no joke is a connective in a costume.
    nojoke = [i + 1 for i, b in enumerate(beats)
              if isinstance(b, dict) and not str(b.get("joke", "")).strip()]
    row("every beat carries its own joke", not nojoke,
        "clean" if not nojoke else
        f"beat(s) {nojoke} declare no `joke`. Parker: 'each individual scene has "
        f"to work as a funny sketch'. A beat with no laugh and no sight gag is a "
        f"connective.")

    # ---- the chain ------------------------------------------------------------
    links = []
    bad_link = []
    for i, b in enumerate(beats[1:], start=1):
        lk = str(b.get("link", "")).strip().upper() if isinstance(b, dict) else ""
        links.append(lk)
        if lk not in LINKS:
            bad_link.append((i + 1, lk or "<none>"))
    row("every seam declares BUT or THEREFORE", not bad_link,
        f"{len(links)} seam(s), all valid" if not bad_link else
        "; ".join(f"beat {n}: '{v}'" for n, v in bad_link[:4])
        + "   <- 'and then' belongs here, which means the story is a list")

    # The banned words, as a literal string check over everything the beats say.
    hits = []
    for i, b in enumerate(beats, start=1):
        if not isinstance(b, dict):
            continue
        blob = " ".join(str(b.get(k, "")) for k in ("text", "link", "expects", "joke")).lower()
        for w in BANNED:
            if w in blob:
                hits.append((i, w))
    row("no banned connective anywhere in the beats", not hits,
        "clean" if not hits else "; ".join(f"beat {i}: '{w}'" for i, w in hits[:4]))

    nb, nt = links.count("BUT"), links.count("THEREFORE")
    row(f"the chain alternates ({MIN_EACH_LINK}+ of each)",
        nb >= MIN_EACH_LINK and nt >= MIN_EACH_LINK,
        f"{nb} BUT, {nt} THEREFORE"
        + ("" if nb >= MIN_EACH_LINK and nt >= MIN_EACH_LINK else
           "   <- all THEREFORE is a ramp and reads mechanical; all BUT is "
           "obstruction and reads like a sketch that will not end"))

    # ---- every BUT names the expectation it violates --------------------------
    bad_expect = []
    for i, b in enumerate(beats[1:], start=1):
        if not isinstance(b, dict):
            continue
        if str(b.get("link", "")).strip().upper() != "BUT":
            continue
        e = str(b.get("expects", "")).strip()
        if not e:
            bad_expect.append((i + 1, "no `expects`"))
        elif len(e.split()) > MAX_EXPECT_WORDS:
            bad_expect.append((i + 1, f"{len(e.split())} words, max {MAX_EXPECT_WORDS}"))
    row("every BUT names the expectation it violates", not bad_expect,
        "clean" if not bad_expect else
        "; ".join(f"beat {n}: {w}" for n, w in bad_expect[:4])
        + "   <- if you cannot write it in ten words, the BUT is decorative")

    # ---- the two-hander -------------------------------------------------------
    rw = str(doc.get("ray_wants", "")).strip()
    dw = str(doc.get("dee_wants", "")).strip()
    inc = str(doc.get("incompatible", "")).strip()

    row("Ray and Dee each declare a want", bool(rw) and bool(dw),
        f"ray: {rw[:38] or '<none>'} | dee: {dw[:38] or '<none>'}")

    # The mechanical half of opposition. Whether two DIFFERENT wants are truly
    # incompatible is a semantic judgement and belongs to a critic; what can be
    # checked here is that they are not the same sentence, which is the failure
    # case 0003 actually had. Ray and Dee agreed.
    same = bool(rw) and bool(dw) and rw.lower() == dw.lower()
    row("their wants are not the same want", not same,
        "distinct" if not same else
        "identical. Two people who agree cannot generate a scene.")

    row("the script names why both cannot be satisfied", bool(inc),
        inc[:60] if inc else
        "no `incompatible`. Comic tension is two people who want incompatible "
        "things, not two people who notice the same thing.")

    return rows


def run(path):
    doc, err = load(path)
    if doc is None:
        print(f"  FAIL the story document exists                 {err}")
        print("\nbeat_check: FAIL. There is no story to check, which is not the "
              "same as\n            nothing being wrong.")
        return 1
    rows = check(doc)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<46} {d}")
    if all(o for _, o, _ in rows):
        print("\nbeat_check: lint clean. The JUDGEMENT half (deletion, swap, "
              "named-expectation)\n            still has to run in the flow "
              "critic. Lint alone is not Gate 0.")
        return 0
    print("\nbeat_check: FAIL. Fix the STORY, not this file. A reaction sequence "
          "cannot\n            produce anything but commentary, however well it "
          "is written.")
    return 1


def self_test():
    """Each fixture trips ONLY its own guard, and each guard is checked live.

    'Some row went red' is not a test. script_check shipped with a self-test that
    asserted exactly that and a guard could be disabled entirely while the suite
    stayed green, because a neighbour covered for it.
    """
    def good():
        return {
            "ray_wants": "to be told the number is wrong",
            "dee_wants": "to close the ticket and go home",
            "incompatible": "the ticket cannot close while he disputes it",
            "beats": [
                {"text": "Ray pays the bill on time.", "joke": "he is proud of it"},
                {"text": "The system bills him again.", "link": "THEREFORE",
                 "joke": "the second bill thanks him"},
                {"text": "He calls to dispute it.", "link": "BUT",
                 "expects": "a human will fix it", "joke": "hold music is a jingle"},
                {"text": "Disputing opens a case, and cases carry a fee.",
                 "link": "THEREFORE", "joke": "the fee is itemised as help"},
                {"text": "He refuses to pay the fee.", "link": "BUT",
                 "expects": "refusing ends it", "joke": "he says the quiet part"},
                {"text": "The filing says the fee is automatic.",
                 "link": "THEREFORE", "joke": "it was true on page one"},
            ],
        }

    def mutate(fn):
        d = good()
        fn(d)
        return d

    def set_link(d, i, v):
        d["beats"][i]["link"] = v

    cases = [
        # Not isolable, and it declares both on purpose: with zero connectives
        # there are necessarily zero BUTs and zero THEREFOREs, so the
        # alternation guard cannot pass either. Declaring one and suppressing
        # the other would be exactly the trick that lets a dead guard hide.
        ("a chain with no connectives at all",
         "every seam declares|the chain alternates",
         mutate(lambda d: [b.pop("link", None) for b in d["beats"][1:]])),
        ("an 'and then' hiding in a beat", "no banned connective",
         mutate(lambda d: d["beats"][2].update(
             {"text": "He calls, and then he waits."}))),
        # All six links THEREFORE: the seams are all valid, so ONLY the
        # alternation guard can catch a ramp.
        ("a chain that is all THEREFORE", "alternates",
         mutate(lambda d: [set_link(d, i, "THEREFORE")
                           for i in range(1, len(d["beats"]))])),
        ("a BUT that names no expectation", "names the expectation",
         mutate(lambda d: d["beats"][2].pop("expects"))),
        ("a beat with no joke in it", "carries its own joke",
         mutate(lambda d: d["beats"][3].pop("joke"))),
        ("two characters who want the same thing", "not the same want",
         mutate(lambda d: d.update({"dee_wants": d["ray_wants"]}))),
        ("no declared incompatibility", "why both cannot be satisfied",
         mutate(lambda d: d.pop("incompatible"))),
        ("a story with no beats block", "declares a beats block",
         mutate(lambda d: d.pop("beats"))),
    ]

    ok = True
    for name, guard, doc in cases:
        want = guard.split("|")
        rows = check(doc)
        missed = [g for g in want
                  if not any(g in n and not o for n, o, _ in rows)]
        others = [n for n, o, _ in rows
                  if not o and not any(g in n for g in want)]
        good_case = not missed and not others
        print(f"  {'ok  ' if good_case else 'FAIL'} catches: {name}"
              + ("" if not missed else f"   <- did NOT fire: {missed}")
              + (f"   <- not isolated, also fired: {others}" if others else ""))
        ok &= good_case

    rows = check(good())
    offenders = [(n, d) for n, o, d in rows if not o]
    clean = not offenders
    for n, d in offenders:
        print(f"       (good story tripped '{n}': {d})")
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a properly chained story")
    ok &= clean

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default=DEFAULT)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run(a.story)


if __name__ == "__main__":
    sys.exit(main())
