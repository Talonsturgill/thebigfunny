#!/usr/bin/env python3
"""coherence_check.py: do the plan and the world describe the SAME film?

WHY THIS EXISTS
The first Phase 3.7-to-4.2 dry run produced two artifacts that disagreed about
what the episode was, and NOBODY IN THE ROOM NOTICED. The producer's plan had a
turn at 14s where a gate slams and the envelope stops dead, and a button where
the cast is shoved past their own letterbox into a bin that was empty in shot 1.
The designer's world refused all four of those things on correct claim-safety
grounds: the gate must never be shown closing, the bin is conditional, the pile
has no primitive, and the actual final shot is a different image entirely.

Both documents were good. Both were internally consistent. The room had
converged on the SET and never on the STORY, and it took an adversarial agent
reading both files side by side to see it. Its words: "A room that produces this
without either side noticing has converged on the set and never on the story."

That is not a taste failure and it must not need a model to catch. The turn and
the button are NAMED FIELDS in both schemas. Two documents claiming different
values for the same named field is arithmetic, and arithmetic belongs in a gate
that runs in a second and cannot be talked out of its verdict.

WHAT IT CANNOT DO
It cannot tell you which document is right. It refuses to guess, because the
answer is a creative decision and the whole point is to put that decision back
in front of the room before Phase 4 writes to one of them and silently ratifies
it. A disagreement is reported as a FORK, with both readings quoted.

  python3 scripts/coherence_check.py
  python3 scripts/coherence_check.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLAN = os.path.join(REPO, "out", "dispatch", "episode_plan.json")
WORLD = os.path.join(REPO, "out", "dispatch", "world.json")

# Two texts describing the same beat should share real words. This is
# deliberately crude: it is looking for a FORK, not for paraphrase quality, and
# a crude test that runs every time beats a subtle one that needs a model.
STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "at", "it", "is",
    "its", "that", "this", "with", "for", "from", "by", "as", "are", "was",
    "then", "into", "out", "up", "down", "over", "one", "two", "their", "them",
    "they", "he", "she", "his", "her", "not", "no", "but", "so", "which",
}

# HOUSE-STYLE VOCABULARY, excluded from every comparison.
#
# Caught on the gate's second live run: the BUTTON row PASSED on the shared
# words ['filling', 'flat', 'frame', 'mark', 'plate'] while the plan described a
# count room and the world described a mail chute. Two completely different
# films matched, because EVERY episode of this show ends on a flat plate filling
# frame with one red mark on it. That is the brand's button format, so it is
# shared by construction and proves nothing.
#
# These words describe HOW a thing is shot. The test is about WHAT the thing IS,
# and a similarity test that matches on house style will pass any two documents
# this studio ever produces.
HOUSE = {
    "flat", "plate", "frame", "filling", "fills", "mark", "stamp", "red",
    "legible", "held", "hold", "holds", "camera", "shot", "close", "wide",
    "macro", "locked", "cut", "cuts", "screen", "image", "picture", "viewer",
    "sees", "beat", "second", "seconds", "shows", "show", "square", "off",
    "single", "only", "first", "last", "final", "under", "above", "beside",
    "behind", "across", "through", "past", "between", "against", "around",
}
MIN_SHARED = 2


def words(t):
    return {w for w in re.findall(r"[a-z]{3,}", str(t).lower())
            if w not in STOP and w not in HOUSE}


def load(path):
    try:
        with open(path) as fh:
            return json.load(fh), None
    except FileNotFoundError:
        return None, f"missing: {os.path.relpath(path, REPO)}"
    except Exception as e:
        return None, f"unreadable: {os.path.relpath(path, REPO)}: {e}"


def _text(node, *keys):
    """Pull the first non-empty string out of a nested dict, tolerantly.

    Both schemas are young and both have already been revised once by their own
    dry runs, so this reads whatever shape it finds rather than hard-failing on
    a renamed key. A missing field is reported as missing; it is never silently
    treated as agreement.
    """
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return " ".join(_text(x) for x in node)
    if not isinstance(node, dict):
        return str(node)
    if keys:
        for k in keys:
            if k in node:
                return _text(node[k])
    return " ".join(_text(v) for v in node.values() if isinstance(v, (str, list, dict)))


def check(plan, world):
    """-> list of (name, ok, detail)."""
    rows = []

    def row(n, ok, d=""):
        rows.append((n, bool(ok), d))
        return ok

    # -- 1. the same story ---------------------------------------------------
    pw = _text(plan.get("world"), "name")
    ww = _text(world.get("world"), "name")
    if pw and ww:
        shared = words(pw) & words(ww)
        row("both documents name the SAME world", bool(shared),
            f"'{pw[:34]}' / '{ww[:34]}'" if shared else
            f"plan says '{pw[:34]}', world says '{ww[:34]}'. These are different films.")
    else:
        row("both documents name the SAME world", False,
            f"only ONE document names a world (plan: '{pw[:34]}', world: '{ww[:34]}')."
            if (pw or ww) else
            "NEITHER document names a world. The whole point of Phase 4.2 is that the "
            "world of the story becomes the set, and two documents that never say what "
            "the world IS have not agreed on it, they have skipped it.")

    # -- 2. THE TURN ---------------------------------------------------------
    # The turn is the single most load-bearing beat in a 60 second episode and
    # it is a named field in both schemas, so a fork here is checkable.
    pt = _text(plan.get("the_turn"), "what_gets_worse", "what")
    wt = _text(world.get("the_turn") or world.get("turn"), "what_gets_worse", "what")
    if pt and wt:
        shared = words(pt) & words(wt)
        row(f"the plan and the world agree on THE TURN ({MIN_SHARED}+ shared terms)",
            len(shared) >= MIN_SHARED,
            f"shared: {sorted(shared)[:5]}" if len(shared) >= MIN_SHARED else
            f"FORK. plan: '{pt[:70]}' / world: '{wt[:70]}'. Nobody has ruled on which "
            f"one the episode is. Rule on it before Phase 4 writes to one and "
            f"ratifies it by accident.")
    else:
        row("the plan and the world agree on THE TURN", False,
            ("only ONE document declares a turn. The other has no opinion about the "
             "most load-bearing beat in the episode, which is not agreement.")
            if (pt or wt) else
            ("NEITHER document declares a turn. Silence is not agreement: it is two "
             "documents that have not decided what the episode's most load-bearing "
             "beat IS. This exact hole let the gate pass the fork it was built to "
             "catch on its first live run."))

    # -- 3. THE BUTTON -------------------------------------------------------
    pb = _text(plan.get("the_button"), "image", "document")
    wb = _text(world.get("the_button") or world.get("button"), "image", "document")
    if not wb:
        # The designer's schema has no `the_button`; its ending lives in the LAST
        # shot. Read it there rather than scoring silence as agreement.
        shots = world.get("shots") or []
        if isinstance(shots, list) and shots:
            wb = _text(shots[-1], "visual", "image", "what_the_viewer_SEES", "description")
    if pb and wb:
        shared = words(pb) & words(wb)
        row(f"the plan and the world agree on THE BUTTON ({MIN_SHARED}+ shared terms)",
            len(shared) >= MIN_SHARED,
            f"shared: {sorted(shared)[:5]}" if len(shared) >= MIN_SHARED else
            f"FORK. plan: '{pb[:70]}' / world: '{wb[:70]}'. `button_doesnt_land` is a "
            f"standing repeat offender here, and two documents disagreeing about what "
            f"the ending IS is the most direct way to earn it again.")
    else:
        row("the plan and the world agree on THE BUTTON", False,
            "only ONE document declares a button."
            if (pb or wb) else
            "NEITHER document declares a button. `button_doesnt_land` is a standing "
            "repeat offender here, and the surest way to earn it again is for no "
            "artifact to say what the ending IS.")

    # -- 4. props the plan needs and the world dropped -----------------------
    # The dry run's plan leaned on a pile of mail; the world dropped `Queue`
    # with "there is no queue in this world". That deletion silently removed the
    # force that carried the cast past their exit, which was the whole ending.
    need = {str(x).lower() for x in (plan.get("world") or {}).get("missing_primitives", [])}
    need |= {str(x).lower() for x in (plan.get("world") or {}).get("new_props", [])}
    dropped = set()
    for e in (world.get("cast_from_kit") or []):
        if isinstance(e, dict) and str(e.get("status", "")).lower() in {"not_required", "dropped"}:
            dropped.add(str(e.get("primitive", "")).lower())
    orphaned = sorted({n for n in need if n and n in dropped})
    row("nothing the plan depends on was silently dropped by the world",
        not orphaned,
        "clean" if not orphaned else
        f"{orphaned} appear in the plan and are marked not-required by the world. "
        f"A primitive dropped as unnecessary can be carrying a beat. In the dry run "
        f"`Queue` was dropped, and the pile of mail it represented was the only force "
        f"moving the cast past their own exit.")

    # -- 5. EVERY CLEARED CLAIM THE WORLD NAMES IS ACTUALLY STAGED ----------
    # The devil's advocate found c7 listed in world.mechanism.claim_ids and
    # staged in NONE of the fifteen shots. The room then spent a whole pass
    # discussing "the INVALID return with the wheel not moving" as though it were
    # on the page. It was a passing mention in a scale note.
    #
    # This is arithmetic and it is the same class the gate was built for: a claim
    # the world CLAIMS to stage and does not is a promise to the fact-checker
    # that the board cannot keep, and it is how a cleared claim quietly becomes
    # an unstaged one between phases.
    ids = [str(x) for x in ((world.get("mechanism") or {}).get("claim_ids") or [])]
    if ids:
        staged = json.dumps({k: world.get(k) for k in ("shots", "sight_gags")}).lower()
        unstaged = sorted({i for i in ids if i and i.lower() not in staged})
        row("every claim the world names is staged in a shot or a gag",
            not unstaged,
            f"all {len(ids)} staged" if not unstaged else
            f"{unstaged} appear in mechanism.claim_ids and in NO shot and NO gag. "
            f"A claim the world says it stages and does not is a promise to the "
            f"fact-checker the board cannot keep, and the room will discuss it as "
            f"though it were on the page.")
    else:
        row("every claim the world names is staged in a shot or a gag", False,
            "the world names NO claim ids at all. The set is what makes the fact "
            "visible, so a world bound to no cleared claim is decoration, and this "
            "row can only certify staging for claims somebody wrote down.")

    # -- 6. THE GAG COUNT AGREES --------------------------------------------
    # The plan asserted four gags surviving their claim guards; the world carried
    # two. A count in one document with no referent in the other is the same
    # defect as disagreeing about the turn, and a producer who believes he has
    # four will not commission the two that are missing.
    claimed = plan.get("sight_gags_surviving_claim_guards")
    actual = world.get("sight_gags")
    if claimed is not None and isinstance(actual, list):
        row("the plan's gag count matches the gags the world actually has",
            int(claimed) == len(actual),
            f"both {claimed}" if int(claimed) == len(actual) else
            f"plan claims {claimed} surviving gags, world carries {len(actual)}. A "
            f"producer who believes he has {claimed} will not commission the "
            f"{int(claimed) - len(actual)} that are missing.")
    else:
        row("the plan's gag count matches the gags the world actually has", False,
            ("only ONE document has an opinion about the sight gags "
             f"(plan count={claimed!r}, world list={'absent' if actual is None else actual})")
            if (claimed is not None or actual is not None) else
            "NEITHER document declares a sight gag. An episode whose two artifacts "
            "both forgot to say what is FUNNY ON SCREEN is the talking-heads defect "
            "arriving through the front door.")

    # -- 7. THE WORLD DOES NOT CONTRADICT ITSELF ----------------------------
    # world.json's turn said the pile FANS across the floor and its own
    # handoff_to_board said NEVER FAN THE PILE, in the same file. The gate could
    # catch two different films and not two different stagings of one, because
    # every check compared ACROSS documents and none looked WITHIN one.
    ban = " ".join(str(x) for x in (world.get("handoff_to_board") or [])).lower()
    turn_txt = _text(world.get("the_turn"), "what_gets_worse").lower()
    # Only CONTENT words. The first cut matched `never (\w+)` and caught "never a"
    # out of "never a face", then searched for a bare "a" in the turn text, which
    # matches essentially any sentence. A guard whose first live run fires on a
    # stopword teaches the room to ignore it, which is worse than not having it.
    #
    # THE SECOND CUT WAS WORSE AND LOOKED FINE. It read ONE word after "never"
    # and then filtered that word through HOUSE, and a ban is written as a PHRASE:
    # "never shown closing", "never hold on the pile", "never close the gate". The
    # first word of a staging ban is almost always a staging verb, which is what
    # HOUSE is a list of, so the guard discarded nearly every real ban and stayed
    # green because the fixture had been quietly reworded to a verb that survived
    # the filter. HOUSE exists to stop two DIFFERENT documents matching on house
    # style; this row compares one document against ITSELF, where house-style
    # verbs are the entire content. So it does not apply here, and the phrase is
    # read whole.
    forbidden = {w for phrase in re.findall(r"never ([\w ]{3,40})", ban)
                 for w in re.findall(r"[a-z]{3,}", phrase)
                 if w not in STOP}
    self_broken = sorted({v for v in forbidden if re.search(rf"\b{v}", turn_txt)})
    row("the world does not forbid on one line what it stages on another",
        not self_broken,
        "consistent" if not self_broken else
        f"handoff_to_board says 'never {self_broken[0]}' and the_turn does exactly "
        f"that. The board is handed two instructions and will pick one at random.")

    # -- 8. shippability agrees ---------------------------------------------
    ps, ws = plan.get("shippable"), world.get("shippable")
    if ps is not None and ws is not None:
        row("both documents agree on whether this is shippable", ps == ws,
            f"both {ps}" if ps == ws else
            f"plan says shippable={ps}, world says {ws}. One of them is about to hand "
            f"a later phase something it must not build.")
    else:
        row("both documents agree on whether this is shippable", False,
            f"only ONE document declares shippability (plan={ps!r}, world={ws!r})."
            if (ps is not None or ws is not None) else
            "NEITHER document declares shippability. Both schemas require the field, "
            "and a phase that never says whether its output may be built hands the "
            "decision to whoever reads it next.")

    return rows


def run():
    plan, e1 = load(PLAN)
    world, e2 = load(WORLD)
    for e in (e1, e2):
        if e:
            print(f"  FAIL {e}")
    if plan is None or world is None:
        print("\ncoherence_check: FAIL. Both artifacts must exist by the end of Phase 4.2.")
        return 1
    rows = check(plan, world)
    if not rows:
        print("  FAIL no comparable fields in either document")
        print("\ncoherence_check: FAIL. Nothing could be compared, which is not a pass.")
        return 1
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<58} {d}")
    if all(o for _, o, _ in rows):
        print("\ncoherence_check: PASS. The plan and the world describe the same film.")
        return 0
    print("\ncoherence_check: FAIL. The room converged on the SET and not on the STORY.")
    print("  This is not a request to edit this file or to soften a threshold. Two")
    print("  documents disagree about what the episode IS, and a human decision about")
    print("  which is right has not been made. Make it, write it into BOTH, rerun.")
    return 1


def self_test():
    ok = True
    good_plan = {
        "shippable": True,
        "world": {"name": "the ten day mail chute", "new_props": ["DayLampPanel"]},
        "the_turn": {"what_gets_worse": "the gate shuts and the lamps keep going out while the envelope sits still"},
        "the_button": {"image": "the notice lying in the bin at the end of the chute"},
        "sight_gags_surviving_claim_guards": 2,
    }
    good_world = {
        "shippable": True,
        "world": {"name": "the ten day chute"},
        "the_turn": {"what_gets_worse": "the envelope sits still and the lamps keep going out past the shut gate"},
        "the_button": {"image": "the notice face up in the bin, one dark lamp above it"},
        "cast_from_kit": [{"primitive": "Passage", "status": "substituted"}],
        # A complete world binds itself to cleared claims and stages every one of
        # them. The fixture carries what a real world carries, or the rows that
        # certify those fields are being tested against a document that would
        # never reach them.
        "mechanism": {"claim_ids": ["c4"]},
        "shots": [{"visual": "the envelope enters the chute, licensed by c4"}],
        "sight_gags": [{"gag": "the lamp"}, {"gag": "the bin"}],
    }
    rows = check(good_plan, good_world)
    clean = all(o for _, o, _ in rows)
    if not clean:
        for n, o, d in rows:
            if not o:
                print(f"       (good pair tripped '{n}': {d})")
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: two documents describing one film")
    ok &= clean

    # Each red case names the guard it must trip, and any OTHER red row fails
    # the case. "Some row went red" is not a test; a dead guard hides behind a
    # neighbour that covers for it on the same fixture.
    cases = [
        ("catches: THE REAL DRY-RUN FORK, a turn each document refuses", ["THE TURN"],
         good_plan,
         dict(good_world, the_turn={"what_gets_worse":
              "the gate is already shut when the camera arrives and is never seen closing"})),
        ("catches: two different endings", ["THE BUTTON"],
         good_plan,
         dict(good_world, the_button={"image":
              "a receipt filling frame with the brand stamp landing on it"})),
        # THE SECOND LIVE-RUN BUG. Two different films, endings that share only
        # the brand's button format, which every episode has by construction.
        ("catches: endings matching only on house style", ["THE BUTTON"],
         dict(good_plan, the_button={"image":
              "flat plate filling frame, the notice legible, one red stamp mark off-square"}),
         dict(good_world, the_button={"image":
              "flat plate filling frame, the receipt legible, one red stamp mark off-square"})),
        ("catches: two different worlds", ["SAME world"],
         good_plan, dict(good_world, world={"name": "a municipal swimming pool"})),
        ("catches: a prop the plan needs and the world dropped", ["silently dropped"],
         good_plan,
         dict(good_world, cast_from_kit=[{"primitive": "DayLampPanel", "status": "not_required"}])),
        ("catches: a claim the world names and never stages", ["claim the world names"],
         good_plan, dict(good_world, mechanism={"claim_ids": ["c4", "c7"]},
                         shots=[{"visual": "cards land, licensed by c4"}])),
        ("catches: a gag count with no referent", ["gag count"],
         dict(good_plan, sight_gags_surviving_claim_guards=4),
         dict(good_world, sight_gags=[{"gag": "one"}, {"gag": "two"}])),
        ("catches: the world forbidding what its own turn stages", ["forbid on one line"],
         good_plan, dict(good_world, handoff_to_board=["never scatter the pile"],
                         the_turn={"what_gets_worse":
                             "the gate shuts and the lamps keep going out while the "
                             "envelope sits still, and the copies scatter across the floor"})),
        # THE LIVE BAN, WORD FOR WORD, off this file's own docstring. The guard
        # read one word after "never", so the ban became "shown", which is house
        # vocabulary and was discarded. Every real staging ban in this repo starts
        # with a staging verb, so the guard was dead for its entire working life
        # and its fixture had been reworded to a verb that happened to survive.
        ("catches: a ban whose verb is house vocabulary", ["forbid on one line"],
         good_plan, dict(good_world, handoff_to_board=["never shown closing"],
                         the_turn={"what_gets_worse":
                             "the gate is shown closing while the envelope sits still"})),
        # And a three letter one, because the length filter was the other half of
        # the same bug.
        ("catches: a ban shorter than the old length filter", ["forbid on one line"],
         good_plan, dict(good_world, handoff_to_board=["never fan the pile"],
                         the_turn={"what_gets_worse":
                             "the gate shuts and the lamps keep going out while the "
                             "copies fan across the floor"})),
        ("catches: one document saying ship and the other saying do not", ["shippable"],
         good_plan, dict(good_world, shippable=False)),
        ("catches: only one document declaring a turn at all", ["THE TURN"],
         good_plan, {k: v for k, v in good_world.items() if k != "the_turn"}),
        # THE BUG THIS GATE SHIPPED WITH. Both silent scored as agreement, so it
        # passed the fork it exists to catch on its first live run.
        ("catches: NEITHER document declaring a turn", ["THE TURN"],
         {k: v for k, v in good_plan.items() if k != "the_turn"},
         {k: v for k, v in good_world.items() if k != "the_turn"}),
        ("catches: NEITHER document declaring a button", ["THE BUTTON"],
         {k: v for k, v in good_plan.items() if k != "the_button"},
         {k: v for k, v in good_world.items() if k != "the_button"}),
        # THE SAME HOLE, FOUR MORE TIMES. The turn and the button were fixed to
        # refuse silence and the other four rows kept scoring it as agreement, so
        # a pair of documents that simply never mentioned the world, the claims,
        # the gags or shippability collected four green rows for saying nothing.
        # A row that is not emitted is indistinguishable from a row that passed.
        ("catches: NEITHER document naming a world", ["SAME world"],
         {k: v for k, v in good_plan.items() if k != "world"},
         {k: v for k, v in good_world.items() if k != "world"}),
        ("catches: a world bound to no cleared claim at all", ["claim the world names"],
         good_plan, {k: v for k, v in good_world.items() if k != "mechanism"}),
        ("catches: NEITHER document declaring a sight gag", ["gag count"],
         {k: v for k, v in good_plan.items() if k != "sight_gags_surviving_claim_guards"},
         {k: v for k, v in good_world.items() if k != "sight_gags"}),
        ("catches: NEITHER document declaring shippability", ["shippable"],
         {k: v for k, v in good_plan.items() if k != "shippable"},
         {k: v for k, v in good_world.items() if k != "shippable"}),
    ]
    for name, want, p, w in cases:
        rows = check(p, w)
        red = [n for n, o, _ in rows if not o]
        missed = [g for g in want if not any(g in n for n in red)]
        extra = [n for n in red if not any(g in n for g in want)]
        good_ = not missed and not extra
        print(f"  {'ok  ' if good_ else 'FAIL'} {name}"
              + ("" if good_ else f"   <- missed {missed}, also fired {extra}"))
        ok &= good_

    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run()


if __name__ == "__main__":
    sys.exit(main())
