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
MIN_SHARED = 2


def words(t):
    return {w for w in re.findall(r"[a-z]{3,}", str(t).lower()) if w not in STOP}


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

    # -- 5. shippability agrees ---------------------------------------------
    ps, ws = plan.get("shippable"), world.get("shippable")
    if ps is not None and ws is not None:
        row("both documents agree on whether this is shippable", ps == ws,
            f"both {ps}" if ps == ws else
            f"plan says shippable={ps}, world says {ws}. One of them is about to hand "
            f"a later phase something it must not build.")

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
    }
    good_world = {
        "shippable": True,
        "world": {"name": "the ten day chute"},
        "the_turn": {"what_gets_worse": "the envelope sits still and the lamps keep going out past the shut gate"},
        "the_button": {"image": "the notice face up in the bin, one dark lamp above it"},
        "cast_from_kit": [{"primitive": "Passage", "status": "substituted"}],
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
        ("catches: two different worlds", ["SAME world"],
         good_plan, dict(good_world, world={"name": "a municipal swimming pool"})),
        ("catches: a prop the plan needs and the world dropped", ["silently dropped"],
         good_plan,
         dict(good_world, cast_from_kit=[{"primitive": "DayLampPanel", "status": "not_required"}])),
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
