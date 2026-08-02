#!/usr/bin/env python3
"""visual_check.py: PHASE 4.2. The gate that mechanically refuses talking heads.

WHY THIS EXISTS
The owner watched the last episode and said:

    "the scenes are boring and not actually illustrating anything ... you made it
     two ppl talking and doing nothing for the most part"

Every quality gate in this pipeline had passed that episode. That is the part
worth staring at. story_check, script_check, face_check, vo_cast, render_gate and
a three-critic panel all went green on a show whose central defect was VISIBLE
FROM THE FIRST SECOND. They went green because not one of them ever looked at a
picture: the storyboard critic and the flow critic grade JSON prose, and prose
about a boring scene reads exactly like prose about a good one.

`scripts/contact_sheet.py` is the other half of the answer, and it gives a critic
eyes. But a critic with eyes is still DOWNSTREAM, and the standing lesson in
`retro.py` is that a downstream critic never fixes an upstream decision: the funny
critic named the same cause on two consecutive cases and six rewrites moved the
score 57 -> 69 -> 63, because the ceiling was set before the critic was called.

So this gate runs on the BOARD. Before a frame is rendered and before a cent of
audio is bought, which is the same reason story_check runs at Phase 3.

THE ROOT CAUSE IT IS BUILT AGAINST
The art library was ported from `alaska-ai-weekly`. It is a shelf of parkas,
snow, spruce and glaciers, and ASSET_MANIFEST tells every run to cast from the
shelf first. So a national story gets an Alaska set, the set therefore cannot
illustrate anything, and once the set is inert the only thing an episode has left
to do is HAVE TWO PEOPLE TALK. "Two people talking and doing nothing" is not a
staging failure. It is what remains after the world has been amputated from the
story.

The show's new law: THE WORLD OF THE STORY BECOMES THE SET. A Ford engine story
is staged inside a Ford engine. This file enforces the parts of that law that can
be counted, and forces the rest to be WRITTEN DOWN, the same way story_check
forces the absurd sentence to be written down. You cannot mechanically detect
funny and this does not pretend to.

-----------------------------------------------------------------------------
THE STORYBOARD SCHEMA THIS REQUIRES
The board writer has to produce these. Existing fields (`id`, `t`, `beat`,
`action`, `assets`, `camera`, `captions`) are unchanged and still used.

  visual_system.world = {
    "name":          "the inside of a Ford hybrid engine bay",
    "drawn_from":    ["Ford", "engine", "recall", "speaker"],
        NOUNS LIFTED FROM THE STORY ITSELF. Checked against the board's own
        title, angle and target, so a world cannot be asserted into relevance.
    "why_this_world": "one plain sentence, why this world and not a room"
  }

  shots[].visual                  what the viewer SEES, independent of the words.
  shots[].visual_contributes      what this picture adds that the LINE does not.
                                  Refused if it is declared as accompaniment, and
                                  refused if it just restates the caption.
  shots[].staging = {"RAY": "left", "DEE": "right"}
                                  camera-left / camera-right / center / off.
  shots[].staging_change_reason   required only when somebody swaps sides.
  shots[].events = [
    {"t": 4.0, "kind": "prop", "what": "a piston rises through the floor"},
    {"t": 7.5, "kind": "sight_gag", "what": "...", "the_joke": "why it is funny"}
  ]
        A VISUAL EVENT is something CHANGING ON SCREEN. `kind` comes from a closed
        vocabulary (see EVENT_KINDS below) split into events that count and things
        that do not: a mouth moving, a blink, an idle and a talking gesture are
        NOT visual events, they are what a talking head does. A sight gag also
        declares `the_joke`, because a gag nobody can state is decoration.

WHAT IT CHECKS
  1. MOTION ENERGY, and no single image held too long.
  2. TALKING HEADS as a fraction of screen time.
  3. Every beat says what the PICTURE contributes that the line does not.
  4. WORLD RELEVANCE: the set is built from the story's own nouns, and is not
     the Alaska shelf wearing a new label.
  5. SIGHT GAGS: a minimum number of visuals that ARE the joke.
  6. SCREEN-SIDE CONTINUITY, deterministic.

  python3 scripts/visual_check.py                       # out/dispatch/storyboard.json
  python3 scripts/visual_check.py runs/2026-08-02/storyboard.json
  python3 scripts/visual_check.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# THE NUMBERS. Every one of them is calibrated against case 0002, which is the
# episode the owner's verdict describes, so "what the failed episode did" is the
# floor a threshold must sit ABOVE, never the level it sits at.

# MOTION ENERGY. Case 0002's board declares roughly eleven things that actually
# change on screen across 54.6s, a rate of about 12 per 60s, and the owner called
# it two people doing nothing. A threshold at 12 would have passed it. 18 per 60s
# is one new thing on screen every 3.3 seconds, which is also about where
# short-form stops feeling like a slideshow with a podcast over it.
MIN_EVENTS_PER_60S = 18.0

# NO SINGLE IMAGE HELD TOO LONG. Case 0002's S4 runs 20.4 to 30.4 and its own
# board says "the cards are gone; this beat is performance, not graphics": ten
# unbroken seconds of two figures talking. That single shot is the owner's
# sentence, rendered. face_check allows a FACE to hold 8s; the whole picture gets
# less, because a held face inside a changing frame is a performance and a held
# frame is a slide.
MAX_STATIC_HOLD_S = 5.0

# TALKING HEADS. Case 0002 spent S2 (5.6s) plus S4 (10.0s) with nothing on screen
# but the two of them, 29% of the episode. The ceiling has to sit below what the
# failed episode did or it certifies nothing. 0.20 of a 60s show is 12 seconds:
# one whole shot of pure performance, and no more. Performance is not banned, it
# is rationed.
MAX_TALKING_HEAD_FRACTION = 0.20

# SIGHT GAGS. One is an accident, two is a coincidence, three is a policy.
# retro.py's standing repeat offender is `carried_by_fact`, the fact doing all the
# work and the picture none; three gags across three DISTINCT shots is the
# minimum that makes the picture a co-author rather than a backdrop. Distinct
# shots, so they cannot all be stacked into the button.
MIN_SIGHT_GAGS = 3

# WORLD RELEVANCE. One shared noun is a coincidence ("the story mentions a
# building, so, a building"). Two forces the world to be built from the story's
# actual subject.
MIN_WORLD_NOUNS = 2

# A judgement written in five words is not a judgement. Same bar story_check puts
# on `why_absurd_not_just_bad`.
MIN_JUDGEMENT_WORDS = 6

# How much of a beat's "what the picture adds" may be words already in that
# beat's own caption. Above this, the picture is saying what the line says, which
# is the definition of illustration rather than contribution.
MAX_CAPTION_ECHO = 0.6

# ---------------------------------------------------------------------------
# CLOSED VOCABULARY, on purpose. An open one lets a typo ("propp") silently
# become a qualifying event, and lets a board invent a kind that means "they
# talked". Unknown kinds are a hard failure.

# Things that CHANGE ON SCREEN.
EVENT_KINDS_COUNT = {
    "prop",        # an object arrives, moves, breaks, multiplies
    "set",         # the world itself changes
    "reveal",      # something hidden becomes visible
    "transform",   # a thing becomes a different thing
    "entrance",    # a figure enters frame
    "exit",        # a figure leaves frame
    "camera",      # a real move: push, whip, crane, rack. Not a drift.
    "cut",         # a cut to a genuinely different picture
    "scale",       # the size relationship changes
    "text_card",   # a card, stamp, badge, document lands
    "sight_gag",   # the picture IS the joke. Must declare `the_joke`.
}

# Things a talking head does. Declaring more of these does not make an episode
# less static, which is exactly why they are named and excluded rather than left
# out of the vocabulary where they would look like typos.
EVENT_KINDS_IGNORED = {
    "idle", "mouth", "talk", "speak", "blink", "breathe", "gesture",
    "expression", "look", "nod", "sway",
}

# ---------------------------------------------------------------------------
# "The visual accompanies the dialogue" is the confession this gate exists to
# catch. A board that writes any of these has told you the picture is decoration,
# and it usually writes one because it is being honest.
ACCOMPANIMENT = (
    "accompan", "supports the line", "supports the dialogue", "support the line",
    "illustrates the line", "illustrates the dialogue", "illustrates what",
    "while they talk", "while they discuss", "as they talk", "as they discuss",
    "as they speak", "matches the line", "matches the dialogue",
    "reinforces the line", "reinforces what", "underscores", "backs up the line",
    "visual accompaniment", "shows them talking", "sets the mood",
    "atmosphere only", "adds nothing", "same as the line", "restates the line",
    "background for the", "backdrop for the", "keeps the frame busy",
    "just the two of them talking", "carries the dialogue",
)

# THE SHELF THAT CAUSED THIS. If one of these appears in the world, the set or
# the hero structure and does NOT appear in the story, the board has gone
# shopping on the Alaska shelf instead of building the story's world. The words
# are not banned; a story about Alaska may use every one of them.
ALASKA_SHELF = (
    "alaska", "alaskan", "parka", "snow", "snowfield", "snowdrift", "spruce",
    "glacier", "tundra", "wolf", "wolves", "boreal", "arctic", "permafrost",
    "igloo", "moose", "caribou", "salmon", "anchorage", "fairbanks", "nenana",
    "aurora", "sled", "husky", "iceberg", "ptarmigan", "fjord", "taiga",
)

STOP = {
    "the", "and", "for", "that", "this", "with", "from", "they", "them", "their",
    "have", "has", "had", "was", "were", "been", "being", "are", "not", "but",
    "you", "your", "its", "it's", "into", "onto", "over", "under", "then",
    "than", "when", "what", "who", "how", "why", "all", "any", "one", "two",
    "his", "her", "she", "him", "our", "out", "off", "about", "which", "will",
    "would", "could", "should", "there", "here", "does", "did", "done", "just",
    "also", "more", "most", "some", "such", "only", "very", "each", "every",
    "shot", "scene", "frame", "screen", "line", "beat", "camera", "still",
}

SIDES = {"left", "right", "center", "centre", "off", "offscreen", "none"}
FLIPPABLE = {"left", "right"}


def words(s):
    return [w for w in re.findall(r"[a-z0-9']+", str(s).lower())
            if len(w) >= 4 and w not in STOP]


def stem_match(a, b):
    """Loose enough for plurals and tense, tight enough not to marry 'record' to
    'recall'. Four shared leading characters plus one being a prefix of the
    other."""
    a, b = str(a).lower(), str(b).lower()
    if len(a) < 4 or len(b) < 4 or a[:4] != b[:4]:
        return False
    return a.startswith(b) or b.startswith(a)


def shots_of(sb):
    return [s for s in (sb.get("shots") or []) if isinstance(s, dict)]


def span(shot):
    t = shot.get("t") or [0, 0]
    try:
        return float(t[0]), float(t[1])
    except Exception:
        return 0.0, 0.0


def runtime(sb):
    ss = shots_of(sb)
    ends = [span(s)[1] for s in ss] or [0.0]
    return max(max(ends), float(sb.get("delivered_runtime_seconds") or 0.0),
               float(sb.get("estimated_seconds") or 0.0))


def story_text(sb):
    """The story's SPINE: title, angle, target. Deliberately NOT the captions.
    The world has to come from what the episode is ABOUT, not from a noun that
    happened to fall into one line of dialogue."""
    return " ".join(str(sb.get(k, "")) for k in ("title", "angle", "target", "angle_type"))


# ---------------------------------------------------------------------------


def check(sb):
    """-> [(name, ok, detail)]. Every name carries a distinct keyword so the
    self-test can prove each guard fires ALONE."""
    rows = []

    def row(n, ok, d=""):
        rows.append((n, bool(ok), d))
        return ok

    ss = shots_of(sb)
    total = runtime(sb)
    if not ss or total <= 0:
        row("the board has timed shots", False,
            "no shots, or no shot carries a t=[start, end]. Nothing to grade.")
        return rows

    # -- collect events -----------------------------------------------------
    counted, ignored, bad_kind, outside = [], 0, [], []
    for s in ss:
        a, b = span(s)
        for e in (s.get("events") or []):
            if not isinstance(e, dict):
                bad_kind.append(f"{s.get('id')}: event is not an object")
                continue
            kind = str(e.get("kind", "")).strip().lower()
            try:
                t = float(e.get("t"))
            except Exception:
                outside.append(f"{s.get('id')}: event '{kind}' has no numeric t")
                continue
            if kind in EVENT_KINDS_IGNORED:
                ignored += 1
                continue
            if kind not in EVENT_KINDS_COUNT:
                bad_kind.append(f"{s.get('id')}: '{kind or 'MISSING'}'")
                continue
            if not (a - 0.001 <= t <= b + 0.001):
                outside.append(f"{s.get('id')}: event at t={t:g} is outside [{a:g}, {b:g}]")
                continue
            counted.append((t, kind, s, e))

    row("every event kind is in the vocabulary", not bad_kind,
        f"{len(bad_kind)} unknown: {bad_kind[:3]}. Known: "
        f"{sorted(EVENT_KINDS_COUNT)[:5]}..., ignored: {sorted(EVENT_KINDS_IGNORED)[:4]}..."
        if bad_kind else
        f"{len(counted)} visual event(s), {ignored} idle/mouth/gesture entries not counted")

    row("every event sits inside its own shot", not outside,
        f"{len(outside)}: {outside[:3]}. A board whose event times do not land in "
        f"their shot is measuring an episode that will not exist."
        if outside else "timings consistent")

    # -- 1. MOTION ENERGY ---------------------------------------------------
    rate = len(counted) * 60.0 / total
    # A board from before this schema existed declares no `events` at all, which
    # scores zero and reads like an accusation. Say which it is, so a run does
    # not go hunting for missing pictures in a board that simply predates the
    # field.
    legacy = "" if any("events" in s for s in ss) else (
        " NOTE: no shot declares `events`, so this board predates the schema in "
        "visual_check's header. Add the field before reading this as a verdict.")
    row(f"motion energy is at least {MIN_EVENTS_PER_60S:g} events per 60s",
        rate >= MIN_EVENTS_PER_60S,
        f"{len(counted)} events in {total:.1f}s = {rate:.1f}/60s"
        + ("" if rate >= MIN_EVENTS_PER_60S else
           f". Case 0002 ran about 12/60s and the owner called it two people "
           f"doing nothing. Put things ON SCREEN, do not write more dialogue."
           + legacy))

    times = sorted(t for t, _, _, _ in counted)
    marks = [0.0] + times + [total]
    holds = [(marks[i + 1] - marks[i], marks[i]) for i in range(len(marks) - 1)]
    worst, at = max(holds) if holds else (total, 0.0)
    row(f"no image holds longer than {MAX_STATIC_HOLD_S:g}s",
        worst <= MAX_STATIC_HOLD_S,
        f"longest still frame {worst:.1f}s from t={at:.1f}s"
        + ("" if worst <= MAX_STATIC_HOLD_S else
           "  <- that is a slide. Case 0002 held one for 10s and that shot IS the "
           "complaint."))

    # -- 2. TALKING HEADS ---------------------------------------------------
    # Derived, not declared. A shot with nothing changing on screen IS two
    # figures talking, whatever the prose around it says, and a board cannot
    # argue its way out of an empty event list.
    dead = [s for s in ss if not any(x[2] is s for x in counted)]
    dead_s = sum(span(s)[1] - span(s)[0] for s in dead)
    frac = dead_s / total
    row(f"talking heads under {MAX_TALKING_HEAD_FRACTION:.0%} of screen time",
        frac <= MAX_TALKING_HEAD_FRACTION,
        f"{dead_s:.1f}s of {total:.1f}s = {frac:.0%}"
        + (f" ({[s.get('id') for s in dead]})" if dead else "")
        + ("" if frac <= MAX_TALKING_HEAD_FRACTION else
           ". Case 0002 spent 29% here. Performance is rationed, not banned: give "
           "these shots something to DO or fold them into a shot that has."))

    # -- 3. DOES THE PICTURE CARRY THE JOKE ---------------------------------
    missing, accomp, thin, echo = [], [], [], []
    for s in ss:
        sid = s.get("id", "?")
        vis = str(s.get("visual", "")).strip()
        con = str(s.get("visual_contributes", "")).strip()
        if not vis or not con:
            missing.append(f"{sid}({'visual' if not vis else 'visual_contributes'})")
            continue
        low = con.lower()
        hit = [p for p in ACCOMPANIMENT if p in low]
        if hit:
            accomp.append(f"{sid}: '{hit[0]}'")
            continue
        if len(con.split()) < MIN_JUDGEMENT_WORDS:
            thin.append(f"{sid}: {len(con.split())} words")
            continue
        cw = words(con)
        cap = set(words(" ".join(s.get("captions") or [])))
        if len(cw) >= 4 and cap:
            share = sum(1 for w in cw if w in cap) / float(len(cw))
            if share > MAX_CAPTION_ECHO:
                echo.append(f"{sid}: {share:.0%} of it is the caption's own words")

    row("every shot declares what the viewer SEES", not missing,
        f"{len(missing)} incomplete: {missing[:4]}. If you cannot write the "
        f"picture down separately from the line, there is no picture."
        if missing else f"{len(ss)} shot(s) declared")

    row("no shot's visual merely accompanies the dialogue", not accomp,
        f"{len(accomp)}: {accomp[:3]}. That sentence is the confession. A picture "
        f"that accompanies is decoration; give the shot something the line "
        f"cannot say." if accomp else "every shot claims its own contribution")

    row("the contribution is argued, not asserted", not thin,
        f"{len(thin)}: {thin[:3]}, under {MIN_JUDGEMENT_WORDS} words"
        if thin else "reasoned")

    row("no shot's visual just restates the caption", not echo,
        f"{len(echo)}: {echo[:3]}. Saying the line again in pictures is "
        f"illustration. The picture has to ADD." if echo else "no caption echo")

    # -- 4. WORLD RELEVANCE -------------------------------------------------
    vsys = sb.get("visual_system") or {}
    world = vsys.get("world") or {}
    wname = str(world.get("name", "")).strip()
    wwhy = str(world.get("why_this_world", "")).strip()
    drawn = [str(x) for x in (world.get("drawn_from") or []) if str(x).strip()]

    row("the board names the WORLD of the story",
        bool(wname) and len(wwhy.split()) >= MIN_JUDGEMENT_WORDS and bool(drawn),
        f"'{wname[:52]}'" if wname and drawn and len(wwhy.split()) >= MIN_JUDGEMENT_WORDS
        else "MISSING visual_system.world{name, drawn_from, why_this_world}. The law "
             "is that the world of the story becomes the set; a set that cannot be "
             "named from the story is the Alaska shelf with the lights changed.")

    st = set(words(story_text(sb)))
    matched = [n for n in drawn if any(stem_match(w, sw) for w in words(n) for sw in st)]
    row(f"the world is drawn from at least {MIN_WORLD_NOUNS} of the story's own nouns",
        len(matched) >= MIN_WORLD_NOUNS,
        f"{matched[:5]} found in the title/angle/target"
        if len(matched) >= MIN_WORLD_NOUNS else
        f"only {len(matched)} of {len(drawn)} ({drawn[:4]}) appear in the story's own "
        f"title, angle or target. A world can be asserted into relevance in prose; "
        f"it cannot be asserted into the story's nouns.")

    if wname:
        nm = words(wname)
        row("the world's NAME is built from those nouns",
            any(stem_match(w, x) for w in nm for n in matched for x in words(n)),
            f"'{wname[:52]}'" if any(stem_match(w, x) for w in nm for n in matched
                                     for x in words(n))
            else f"'{wname[:52]}' shares no noun with {matched[:4]}. The set is next "
                 f"to the story, not made of it.")

    shelf_field = " ".join(str(vsys.get(k, "")) for k in
                           ("set", "hero_structure", "palette_family", "atmosphere"))
    shelf_text = (wname + " " + shelf_field).lower()
    stray = sorted({a for a in ALASKA_SHELF
                    if re.search(rf"\b{a}\b", shelf_text)
                    and not re.search(rf"\b{a}", story_text(sb).lower())})
    row("the set is not the ported Alaska shelf", not stray,
        f"{stray} appear in the set with no counterpart in the story. That shelf is "
        f"WHY the pictures illustrate nothing: it is a place, and the stories are "
        f"national. Build the story's world instead of shopping." if stray
        else "built, not shopped")

    # -- 5. SIGHT GAGS ------------------------------------------------------
    gag_shots, unstated = set(), []
    for t, kind, s, e in counted:
        if kind != "sight_gag":
            continue
        if len(str(e.get("the_joke", "")).split()) < MIN_JUDGEMENT_WORDS:
            unstated.append(f"{s.get('id')} @{t:g}s")
            continue
        gag_shots.add(s.get("id"))
    row(f"at least {MIN_SIGHT_GAGS} sight gags, in {MIN_SIGHT_GAGS} different shots",
        len(gag_shots) >= MIN_SIGHT_GAGS,
        f"{len(gag_shots)} shot(s) carry one: {sorted(gag_shots)}"
        + ("" if len(gag_shots) >= MIN_SIGHT_GAGS else
           ". A visual that IS the joke, not a visual near one. The show's standing "
           "defect is `carried_by_fact`: the dialogue doing all the work."))
    row("every sight gag states the joke", not unstated,
        f"{len(unstated)}: {unstated[:3]} declare no `the_joke`. Nothing here can "
        f"detect funny; a gag you cannot state in a sentence is decoration wearing "
        f"the label." if unstated else "stated")

    # -- 6. SCREEN-SIDE CONTINUITY ------------------------------------------
    bad_side, flips = [], []
    for i, s in enumerate(ss):
        stg = s.get("staging") or {}
        if not isinstance(stg, dict):
            bad_side.append(f"{s.get('id')}: staging is not an object")
            continue
        for who, side in stg.items():
            if str(side).strip().lower() not in SIDES:
                bad_side.append(f"{s.get('id')}/{who}: '{side}'")
        if i == 0:
            continue
        prev = ss[i - 1].get("staging") or {}
        if not isinstance(prev, dict):
            continue
        reason = str(s.get("staging_change_reason", "")).strip()
        for who, side in stg.items():
            a = str(prev.get(who, "")).strip().lower()
            b = str(side).strip().lower()
            if a in FLIPPABLE and b in FLIPPABLE and a != b and not reason:
                flips.append(f"{who} {a}->{b} at {s.get('id')}")

    row(f"staging sides are one of {sorted(SIDES)[:4]}...", not bad_side,
        f"{bad_side[:3]}" if bad_side else "declared")
    row("screen side is continuous across the cut", not flips,
        f"{len(flips)}: {flips[:3]}. A figure that jumps sides between adjacent "
        f"shots re-orients the viewer for no reason. Declare "
        f"`staging_change_reason` if the cut earns it (a reverse, a crossing, a "
        f"new axis)." if flips else "nobody teleports")

    return rows


# ---------------------------------------------------------------------------


def run(path):
    try:
        sb = json.load(open(path))
    except Exception as e:
        print(f"visual_check: cannot read {path}: {e}", file=sys.stderr)
        return 1
    rows = check(sb)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<56} {d}")
    if all(o for _, o, _ in rows):
        print("\nvisual_check: PASS. The picture is doing work the dialogue is not.")
        return 0
    print("\nvisual_check: FAIL at PHASE 4.2, before a frame is rendered and before")
    print("  a cent of audio is bought, which is the entire point of the timing.")
    print("  The fix is the BOARD, never this file. Build the story's world, put")
    print("  things in it, and give the shots something to do.")
    return 1


# ---------------------------------------------------------------------------


def _ev(t, kind="prop", what="a thing moves", joke=None):
    e = {"t": t, "kind": kind, "what": what}
    if joke:
        e["the_joke"] = joke
    return e


def _shot(sid, t0, t1, events, caps, contributes, staging=None, reason=None):
    s = {
        "id": sid, "t": [t0, t1], "beat": "b", "action": "a",
        "visual": "a wide of the bay floor, pistons above, the pair small below",
        "visual_contributes": contributes,
        "captions": caps,
        "staging": staging or {"RAY": "left", "DEE": "right"},
        "events": events,
    }
    if reason:
        s["staging_change_reason"] = reason
    return s


def _board(shots, **over):
    """A Ford recall story staged inside a Ford engine, which is the law this
    gate exists to enforce. Overrides let each red fixture break ONE thing."""
    sb = {
        "title": "CASE No. 0004 - The Repair That Needed A Repair",
        "angle": "Ford recalled 43,438 SUVs in October for a speaker sound they "
                 "would not make, then the same recall came back covering 66,383.",
        "target": "Ford Motor Company (an institution)",
        "angle_type": "ratio",
        "visual_system": {
            "set": "engine bay interior, cutaway",
            "hero_structure": "the pair standing on a cylinder head, the block above them",
            "palette_family": "oil steel and warning amber",
            "atmosphere": "hot metal, work light",
            "world": {
                "name": "the inside of a Ford engine bay, cut away",
                "drawn_from": ["Ford", "engine", "recall", "speaker"],
                "why_this_world": "The story happens inside a machine that was "
                                  "opened, closed, and has to be opened again.",
            },
        },
        "shots": shots,
    }
    for k, v in over.items():
        sb[k] = v
    return sb


def _good_shots():
    """Seven shots, 54s, 20 visual events, gaps of 3.5s at worst, three gags in
    three shots. Built to be genuinely good rather than merely to pass: the
    self-tests in this repo have shipped a bad "good" fixture three times
    (face_check's held a face 12s, tts_budget's over-budget preview actually fit,
    vo_soundcheck's short fixture was exempt under its own rule), so the numbers
    below are asserted by the self-test itself, not trusted."""
    C = [
        ("we open under the block, so the viewer is inside the thing being recalled",
         ["Ford is recalling sixty-six thousand SUVs.", "For a noise."]),
        ("the letter arrives as weather in the bay, not as a prop somebody holds",
         ["Fine. So fix it.", "They did. October."]),
        ("the two counts are cast as physical parts, so the viewer weighs them",
         ["Forty-three thousand.", "It's back. Sixty-six."]),
        ("the repaired bolt backs itself out while nobody mentions it",
         ["They already fixed those.", "So the repair needs a repair."]),
        ("the sorting is drawn as a chute that keeps rejecting the same car",
         ["Twenty-eight speakers.", "That's how they decide."]),
        ("the monolith is the block itself closing, with no face to appeal to",
         ["The remedy is under development.", "Interim letters expected."]),
        ("the button is the paperwork, physically bolted where the part should be",
         ["That's tomorrow.", "I still have the first letter."]),
    ]
    G = {0: "the engine is reciting its own recall notice",
         3: "the fix undoes itself in the background of the wide",
         6: "the record is torqued into the empty bolt hole"}
    plan = [(0.0, 8.0, [0.5, 3.0, 6.0]), (8.0, 15.0, [9.0, 12.0]),
            (15.0, 22.0, [15.5, 18.5, 21.0]), (22.0, 30.0, [23.0, 26.0, 29.0]),
            (30.0, 38.0, [31.0, 34.0, 37.0]), (38.0, 46.0, [39.0, 42.0, 45.0]),
            (46.0, 54.0, [47.0, 50.0, 53.0])]
    shots = []
    for i, (t0, t1, ts) in enumerate(plan):
        evs = []
        for j, t in enumerate(ts):
            if j == 0 and i in G:
                evs.append(_ev(t, "sight_gag", "the gag lands", G[i]))
            else:
                evs.append(_ev(t, ["prop", "set", "reveal", "camera", "text_card"][j % 5],
                               "the bay reconfigures around them"))
        shots.append(_shot(f"S{i + 1}", t0, t1, evs, C[i][1], C[i][0]))
    return shots


def _flat(n_events, total=54.0, shots=7):
    """A board with n_events spread evenly, used to isolate the counting guards."""
    step = total / float(shots)
    per = [n_events // shots] * shots
    for i in range(n_events - sum(per)):
        per[i] += 1
    out, gags = [], 0
    for i in range(shots):
        t0, t1 = i * step, (i + 1) * step
        evs = []
        for j in range(per[i]):
            t = t0 + (j + 1) * (step / (per[i] + 1.0))
            if gags < MIN_SIGHT_GAGS and j == 0:
                evs.append(_ev(round(t, 2), "sight_gag", "gag",
                               "the machine performs its own paperwork on itself"))
                gags += 1
            else:
                evs.append(_ev(round(t, 2), "prop", "a part moves"))
        out.append(_shot(f"S{i + 1}", round(t0, 2), round(t1, 2), evs,
                         ["a caption", "another caption"],
                         "the world does a thing the dialogue never mentions"))
    return out


def self_test():
    """Both directions, and each red fixture must trip ONLY its own guard.

    "Some row went red" is not a test. script_check's self-test learned this the
    hard way: a dead guard stayed invisible because a neighbouring guard covered
    for it on the same fixture. So each case names the guard(s) it should trip,
    and any OTHER red row fails the case.
    """
    ok = True
    good = _board(_good_shots())

    # The good fixture is asserted, not trusted. If a threshold moves, this says
    # so instead of the fixture quietly drifting under it.
    facts = []
    ss = shots_of(good)
    n_ev = sum(len(s["events"]) for s in ss)
    total = runtime(good)
    facts.append(("the good fixture really is dense",
                  n_ev * 60.0 / total >= MIN_EVENTS_PER_60S,
                  f"{n_ev} events, {n_ev * 60.0 / total:.1f}/60s vs {MIN_EVENTS_PER_60S:g}"))
    ts = sorted(e["t"] for s in ss for e in s["events"])
    gaps = [b - a for a, b in zip([0.0] + ts, ts + [total])]
    facts.append(("the good fixture never holds a frame", max(gaps) <= MAX_STATIC_HOLD_S,
                  f"longest hold {max(gaps):.1f}s vs {MAX_STATIC_HOLD_S:g}s"))
    facts.append(("the good fixture has no dead shot",
                  all(s["events"] for s in ss),
                  f"{sum(1 for s in ss if not s['events'])} shot(s) with no events"))
    facts.append(("the good fixture really carries 3 gags in 3 shots",
                  len({s["id"] for s in ss
                       for e in s["events"] if e["kind"] == "sight_gag"}) >= MIN_SIGHT_GAGS,
                  ""))
    for name, good_, detail in facts:
        print(f"  {'ok  ' if good_ else 'FAIL'} fixture: {name}"
              + (f"   <- {detail}" if not good_ else ""))
        ok &= bool(good_)

    rows = check(good)
    clean = all(o for _, o, _ in rows)
    if not clean:
        for n, o, d in rows:
            if not o:
                print(f"       (good board tripped '{n}': {d})")
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a board whose world does the work")
    ok &= clean

    # -- red fixtures, each isolated ---------------------------------------
    # ISOLATION IS THE WHOLE JOB HERE, and it is fiddly because these guards
    # overlap by nature: fewer events means longer holds, and a dead shot is a
    # long hold. The first cut of each of these three fixtures tripped the hold
    # guard as well, which the self-test caught and which is exactly why the
    # isolation rule is enforced rather than "some row went red".

    # 12 shots of 4.5s, one event each, so the rate is 13.3/60s (under the bar)
    # while the longest hold is 4.5s (under ITS bar) and no shot is dead.
    slideshow = _board(_flat(12, total=54.0, shots=12))

    # 21 events packed into the first 30s, then one 24s shot that opens with an
    # event and then holds. Rate 23/60s, no dead shot, one 23.5s slide.
    held = _board(_flat(20, total=30.0, shots=6)
                  + [_shot("S7", 30.0, 54.0, [_ev(30.5, "prop", "a part moves")],
                           ["a caption"], "the bay keeps working past the line")])

    # Eight live shots of 4.5s (events at +1.0 and +3.5) interleaved with six
    # dead shots of 2.0s. 12.0s dead of 48.0 = 25%, over the ceiling, while the
    # longest hold is 4.0s and the rate is 20/60s. A dead shot has to be SHORT
    # and flanked or it trips the hold guard instead, which is the honest reason
    # the two guards are separate: a short static passage and a long one are
    # different defects.
    heads_shots, t, live, gag = [], 0.0, 0, 0
    for i in range(14):
        dead = (i % 2 == 1) and len([s for s in heads_shots if not s["events"]]) < 6
        if dead:
            heads_shots.append(_shot(f"S{i + 1}", round(t, 2), round(t + 2.0, 2), [],
                                     ["talk", "more talk"],
                                     "the pair hold the frame and keep speaking"))
            t += 2.0
            continue
        evs = []
        for j, off in enumerate((1.0, 3.5)):
            if j == 0 and gag < MIN_SIGHT_GAGS:
                evs.append(_ev(round(t + off, 2), "sight_gag", "gag",
                               "the machine performs its own paperwork on itself"))
                gag += 1
            else:
                evs.append(_ev(round(t + off, 2), "prop", "a part moves"))
        heads_shots.append(_shot(f"S{i + 1}", round(t, 2), round(t + 4.5, 2), evs,
                                 ["a caption", "another"],
                                 "the world does a thing the dialogue never mentions"))
        t += 4.5
        live += 1
    heads = _board(heads_shots)

    def swap(shots, i, **fields):
        out = [dict(s) for s in shots]
        out[i] = dict(out[i], **fields)
        return out

    g = _good_shots()

    cases = [
        ("a slideshow with too little happening", ["motion energy"], slideshow),
        ("one image held for a third of the episode", ["holds longer"], held),
        ("too much of the show is two people talking", ["talking heads"], heads),
        ("a beat that never says what the viewer sees", ["viewer SEES"],
         _board(swap(g, 2, visual=""))),
        ("a picture that merely accompanies the dialogue", ["accompanies"],
         _board(swap(g, 2, visual_contributes="It accompanies the dialogue while they talk."))),
        ("a contribution asserted in four words", ["argued, not asserted"],
         _board(swap(g, 2, visual_contributes="It looks quite good"))),
        ("a picture that just says the caption again", ["restates the caption"],
         _board(swap(g, 2,
                     captions=["Forty three thousand vehicles recalled again."],
                     visual_contributes="Forty three thousand vehicles recalled again "
                                        "vehicles thousand recalled."))),
        # No world at all, so the "NAME is built from those nouns" row is never
        # emitted (there is no name to build). Two guards, not three.
        ("a board that never names its world", ["names the WORLD", "story's own nouns"],
         _board(g, visual_system={"set": "a room"})),
        ("a world with nothing to do with the story", ["story's own nouns", "NAME is built"],
         _board(g, visual_system=dict(
             _board(g)["visual_system"],
             world={"name": "a municipal swimming pool at closing time",
                    "drawn_from": ["pool", "chlorine", "lifeguard"],
                    "why_this_world": "It felt like a nice place to set a scene."}))),
        ("the Alaska shelf wearing a new label", ["Alaska shelf"],
         _board(g, visual_system=dict(
             _board(g)["visual_system"],
             set="a spruce stand under aurora",
             world=dict(_board(g)["visual_system"]["world"],
                        name="a Ford engine abandoned in a snowfield")))),
        ("an episode with no sight gags in it", ["sight gags"],
         _board([dict(s, events=[dict(e, kind="prop") if e["kind"] == "sight_gag" else e
                                 for e in s["events"]]) for s in g])),
        ("a sight gag nobody can state", ["states the joke", "sight gags"],
         _board([dict(s, events=[{k: v for k, v in e.items() if k != "the_joke"}
                                 for e in s["events"]]) for s in g])),
        ("a character who teleports across the cut", ["screen side"],
         _board(swap(g, 3, staging={"RAY": "right", "DEE": "left"}))),
        # One BOGUS kind ADDED to a shot that keeps its real events, so the rate
        # and the holds are untouched and only the vocabulary guard can fire.
        ("an event kind invented to look like motion", ["vocabulary"],
         _board(swap(g, 2, events=g[2]["events"] + [_ev(19.0, "vibe")]))),
        ("an event timed outside its own shot", ["inside its own shot"],
         _board(swap(g, 2, events=g[2]["events"] + [_ev(48.0, "prop")]))),
    ]

    for name, want, board in cases:
        rows = check(board)
        missed = [w for w in want if not any(w in n and not o for n, o, _ in rows)]
        others = [n for n, o, _ in rows if not o and not any(w in n for w in want)]
        good_case = not missed and not others
        print(f"  {'ok  ' if good_case else 'FAIL'} catches: {name}"
              + (f"   <- did NOT fire: {missed}" if missed else "")
              + (f"   <- not isolated, also fired: {others}" if others else ""))
        ok &= good_case

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?",
                    default=os.path.join(REPO, "out", "dispatch", "storyboard.json"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.path)


if __name__ == "__main__":
    sys.exit(main())
