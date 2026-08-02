#!/usr/bin/env python3
"""captions_text.py: the ONE definition of what a viewer is allowed to read.

Performance markup is direction for the voice model. It is never dialogue, and
it must never reach the screen: a burned-in caption reading "[sarcasm] Twenty
eight speakers" is nonsense on the picture and a backstage note shown to the
audience.

WHY THIS FILE EXISTS. The strip lived in two places, `vo_cast.strip_tags` and
`gen_captions_ts.strip_tags`, both spelled `\\[[^\\]]{1,20}\\]`, and both wrong the
same way: the cap was twenty characters and the cast write longer tags than
that. "[sarcasm]" was stripped and "[sarcasm, medium pause]" was not, and both
of those words are in vo_gemini.KNOWN_TAGS, so it is a combination the writer is
documented to produce. It leaked into captions.json, vo_lines.json,
caseNNNN_captions.ts and the burned-in caption.

Two copies of one rule drift apart, which is the same defect that put
build_scenes.py's TAIL out of sync with the routine's ceiling. So there is one
copy, here, and both callers import it.

THE RULE. A tag is a short direction PHRASE in square brackets. It carries no
sentence-ending punctuation, because a bracketed aside inside real dialogue
does, and that aside is something the viewer is meant to read.
"""

import re

# Generous enough for every tag the cast actually write, and structural rather
# than a length guess: no . ! or ? inside the brackets.
TAG = re.compile(r"\s*\[[^\].!?]{1,60}\]\s*")


def strip_tags(t):
    """Remove performance tags from anything a VIEWER reads."""
    return TAG.sub(" ", str(t)).strip()


def self_test():
    ok = True
    cases = [
        # The bug, verbatim. Both of these words are in vo_gemini.KNOWN_TAGS.
        ("[sarcasm] Twenty-eight speakers.", "Twenty-eight speakers."),
        ("[sarcasm, medium pause] Twenty-eight speakers.", "Twenty-eight speakers."),
        # Every tag the live script carries.
        ("[flat] One eviction case.", "One eviction case."),
        ("[extremely fast] reasonable procedures to ensure maximum possible accuracy",
         "reasonable procedures to ensure maximum possible accuracy"),
        ("[medium pause] He got sued once.", "He got sued once."),
        # Mid-line, which is where the old length cap was aimed.
        ("Evicted. [short pause] Evicted.", "Evicted. Evicted."),
        # A bracketed aside that is DIALOGUE survives, because it has sentence
        # punctuation in it. This is what the cap was protecting and the reason
        # the rule is structural instead of just longer.
        ("He said [and I quote. loudly.] no.", "He said [and I quote. loudly.] no."),
        # Nothing to strip is left exactly alone.
        ("So which one of those do I live in?", "So which one of those do I live in?"),
    ]
    for src, want in cases:
        got = strip_tags(src)
        good = got == want
        print(f"  {'ok  ' if good else 'FAIL'} {src[:46]!r}"
              + ("" if good else f"   <- got {got!r}, want {want!r}"))
        ok &= good
    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
