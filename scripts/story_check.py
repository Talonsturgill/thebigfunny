#!/usr/bin/env python3
"""story_check.py — PHASE 3. Is this story ABSURD, or merely infuriating?

WHY THIS EXISTS
`scripts/retro.py` found the repeat offender: `agreement_not_comedy` and
`carried_by_fact` both appeared in cases 0002 and 0003, and the funny critic
named the same cause in both. Its sentence on case 0003, after six rewrites:

    "Duplicate rows in a database is infuriating but not absurd, so the writing
     has to carry a premise it was never built to carry."

The critic sits at PHASE 6. The decision it is complaining about is made at
PHASE 3. So every run so far has discovered, after writing a script and paying
for audio, that the story could never have been funny. That is not a quality
problem, it is a gate in the wrong place.

WHAT THIS CAN AND CANNOT DO
It cannot tell you what is funny. Nothing mechanical can, and the soundcheck
already learned that lesson the expensive way (its prosody thresholds ran
BACKWARDS against the owner's ear).

What it CAN do is force the judgement to be made EXPLICITLY, in writing, before
the story is committed. The show's whole thesis is "the fact supplies the joke",
which means if you cannot write the absurd sentence down in one plain line, you
do not have one, and no writers room will conjure it later.

  python3 scripts/story_check.py out/dispatch/story.json
  python3 scripts/story_check.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# THE COMPRESSION TEST. An absurd mechanism is short. If it needs a paragraph it
# is a situation, not a joke, and a 60 second show cannot carry it.
MAX_WORDS = 22

# Talking it up is the tell. A genuinely absurd fact does not need to be sold,
# and reaching for these is the writer noticing it does not land on its own.
INTENSIFIERS = (
    "outrageous", "outrageously", "shocking", "shockingly", "insane", "insanely",
    "unbelievable", "unbelievably", "staggering", "staggeringly", "appalling",
    "egregious", "unconscionable", "horrifying", "disgusting", "shameful",
    "incredible", "incredibly", "absolutely", "literally", "unreal",
)

# Harm words are not a mechanism. "People lost their homes" is a CONSEQUENCE and
# every one of these stories has one; the absurdity has to be in what was DONE.
HARM_ONLY = (
    "harm", "harmed", "suffer", "suffered", "victim", "victims", "hurt",
    "devastated", "ruined", "lost their", "denied", "struggling",
)

REQUIRED = ("absurd_sentence", "who_does_the_stupid_thing", "why_absurd_not_just_bad")


def check(story):
    """-> list of (name, ok, detail)."""
    rows = []

    def row(n, ok, d=""):
        rows.append((n, bool(ok), d)); return ok

    for f in REQUIRED:
        row(f"declares {f}", bool(str(story.get(f, "")).strip()),
            "present" if str(story.get(f, "")).strip() else
            "MISSING. If you cannot write it, you do not have it.")

    sent = str(story.get("absurd_sentence", "")).strip()
    if sent:
        words = len(sent.split())
        row(f"the absurd sentence compresses (<= {MAX_WORDS} words)",
            words <= MAX_WORDS,
            f"{words} words" + ("" if words <= MAX_WORDS else
                                ". A mechanism that needs a paragraph is a situation, not a joke."))

        low = sent.lower()
        found = [w for w in INTENSIFIERS if re.search(rf"\b{w}\b", low)]
        row("states the fact without selling it", not found,
            "clean" if not found else
            f"contains {found}. A genuinely absurd fact does not need an adjective; "
            f"reaching for one is you noticing it does not land.")

        harm = [w for w in HARM_ONLY if w in low]
        has_verb_of_doing = bool(re.search(
            r"\b(count|counted|charg|bill|list|listed|sent|mail|record|type|typed|"
            r"deni|approv|round|delet|dupl|price|renam|reclassif|require|recall|"
            r"fine|fined|schedul|refus|mark|marked|flag)\w*", low))
        row("the absurdity is in what was DONE, not who was hurt",
            has_verb_of_doing or not harm,
            "names an action" if has_verb_of_doing else
            f"reads as consequence only ({harm}). Every one of these stories has a "
            f"victim; the ABSURDITY has to be in the mechanism.")

    who = str(story.get("who_does_the_stupid_thing", "")).strip()
    if who:
        # The act-out is the single move that scored on case 0003. It needs a
        # person doing a thing, because you cannot become a policy.
        row("there is a PERSON to act out, not a policy",
            not re.match(r"^(the )?(system|policy|process|company|algorithm|software)\b",
                         who.lower()),
            who[:60] if not re.match(
                r"^(the )?(system|policy|process|company|algorithm|software)\b", who.lower())
            else f"'{who[:40]}' is not a person. COMEDY_CRAFT's act-out needs somebody "
                 f"to BECOME; you cannot impersonate a process.")

    why = str(story.get("why_absurd_not_just_bad", "")).strip()
    if why:
        low = why.lower()
        row("says why it is ABSURD, not merely that it is bad",
            not re.search(r"\b(bad|wrong|unfair|greedy|corrupt|evil)\b\s*$", low.strip("."))
            and len(why.split()) >= 6,
            "reasoned" if len(why.split()) >= 6 else "too short to be a reason")

    return rows


def run(path):
    try:
        story = json.load(open(path))
    except Exception as e:
        print(f"story_check: cannot read {path}: {e}", file=sys.stderr)
        return 1
    rows = check(story)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<52} {d}")
    if all(o for _, o, _ in rows):
        print("\nstory_check: PASS. The absurdity is written down and it is a mechanism.")
        return 0
    print("\nstory_check: FAIL at PHASE 3, which is the cheapest place to fail.")
    print("  Two episodes have now been written, scored and rendered before anyone")
    print("  noticed the story was infuriating rather than absurd. Take another one;")
    print("  there are seven beats and the whole public record.")
    return 1


def self_test():
    ok = True
    good = {
        "absurd_sentence": "They counted the same eviction twice and the second one cost him the apartment.",
        "who_does_the_stupid_thing": "a clerk who saw the duplicate and shipped it anyway",
        "why_absurd_not_just_bad": "The machine that judges you cannot tell one thing from two things.",
    }
    rows = check(good)
    print(f"  {'ok  ' if all(o for _,o,_ in rows) else 'FAIL'} accepts a story whose absurdity is a mechanism")
    ok &= all(o for _, o, _ in rows)

    cases = [
        ("catches a story that was never written down", {}),
        ("catches selling it with an adjective",
         dict(good, absurd_sentence="They made an absolutely outrageous and shocking error.")),
        ("catches a mechanism that needs a paragraph",
         dict(good, absurd_sentence=" ".join(["word"] * 40))),
        ("catches consequence dressed as absurdity",
         dict(good, absurd_sentence="Families suffered and people were harmed and many victims lost their homes.")),
        ("catches a policy where a PERSON is needed",
         dict(good, who_does_the_stupid_thing="the system")),
    ]
    for name, story in cases:
        rows = check(story)
        red = not all(o for _, o, _ in rows)
        print(f"  {'ok  ' if red else 'FAIL'} {name}")
        ok &= red

    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=os.path.join(REPO, "out", "dispatch", "story.json"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.path)


if __name__ == "__main__":
    sys.exit(main())
