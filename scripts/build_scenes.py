#!/usr/bin/env python3
"""Compute scene frame boundaries from the VO line timings so the timeline stays
in sync with the narration automatically. Scene i begins at the start of a mapped
VO line; S1 covers lines 0-1. Writes episode_props.json {captions, scenes, total}.
"""
import json, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "out", "dispatch")
FPS = 30

# Hold after the last word.
#
# Was 2.6s on the upstream show, which had no duration ceiling. This show has a
# HARD 60.0s gate, and 2.6 made the arithmetic contradict itself: Gate 0 admits a
# script up to 58s, the render is script + TAIL, and 58.0 + 2.6 = 60.6 fails the
# gate AFTER paying for a full-res render. That is exactly the cost Gate 0 exists
# to avoid. A sixty second short does not need a two and a half second hold.
TAIL = 1.5

# The hard ceiling, from config/scoring_rubric.yaml (sixty_seconds gate).
MAX_TOTAL_S = 60.0
# What Gate 0 may admit. DERIVED, not written down separately, so the routine's
# number and this one cannot drift apart again.
MAX_SCRIPT_S = MAX_TOTAL_S - TAIL

# scene -> index of the VO line that starts it. 2026-07-22 "the checkpoint lever frozen
# at the midpoint" has 7 scenes (S1..S7 in video-engine/src/Episode.tsx, SCENE_COMPONENTS)
# mapped onto 9 VO lines (vo_lines.json has exactly 9 lines this run, some scenes span 2
# lines of VO): S1 line0 (map/counter+offer), S2 line1 (parcels+NOT FOR SALE+"not a sale"
# is still S2's content but starts visually at the parcels line), S3 line3 (EUL
# mechanism), S4 line4 (MachineShadow/Moriarty), S5 line5 (Hollister), S6 line6 (lever
# return, covers "nobody picked"+"still open"), S7 line8 (closing question+hold+loop).
# (keep this list's length equal to SCENE_COMPONENTS.length every run -- an earlier list
# here silently mismatched it once and Episode fell back to hardcoded DEFAULT_BOUNDS.)
# 2026-07-23 "Counting Belugas From Orbit": 7 scenes (S1..S7) onto 11 VO lines.
# S1 L0 (silt/find-the-whale), S2 L1 (331+decline), S3 L2 (from space, SatelliteEye),
# S4 L3-L4 (GAIA+partners, the learning pipeline), S5 L5-L6 (cannot-count-yet, needs a
# clear look), S6 L7-L8 (June 2025 empty, sky booked), S7 L9-L10 (holding on, the question).
# 2026-07-25 "The One It Didn't Hear": 7 scenes (S1..S7) onto 12 VO lines. Shot boundaries
# are anchored to VO LINE STARTS so the picture can never drift from the words (the Gate 0B/0C
# finding that killed the first board: the collapse was spoken at 19.6s and drawn at 33.9s).
# S1 L0-L1 (Otto at work + the second job), S2 L2 (duration lanes + the gate latching),
# S3 L3-L4 (boundary + travel out + THE COLLAPSE), S4 L5 (signature shot + the dark lamp),
# S5 L6-L7 (still heard + by hand + the boulder), S6 L8 (crate + money),
# S7 L9-L11 (wireframe twin + calendar + button).
# 2026-07-26 "The Field That Stopped in 2019": NINE scenes (S1..S9 in Episode.tsx) onto
# 14 VO lines. Shot boundaries are anchored to VO LINE STARTS so the picture can never
# drift from the words. S1 L0 (the letter opens), S2 L1-L2 (the 200 baseline + McCabe's
# fair defense, VOICED not merely posted), S3 L3-L4 (the mouth cranks wide + the intake +
# the burst from the unchanged stem), S4 L5 (the plain letter + 3,048 into one finite
# tape), S5 L6 (three Alaskans reacting three different ways), S6 L7-L8 (the machine opens
# on the capped third pipe + the pawl + the two records), S7 L9-L10 (the arrow on the
# doorless wall + the door swinging free), S8 L11-L12 (NO ALGORITHM + the signature shot),
# S9 L13 (the button, back at the same table, staying interior).
SCENE_START_LINE = [0, 2, 4, 5, 7, 9, 11]   # 2026-07-29: 7 shots, see out/dispatch/storyboard.json


def _apply_caption_fixups(caps):
    """On-screen captions are force-aligned from Whisper's transcript of the
    PHONETICALLY-respelled audio, so proper-noun respellings ('Ex Prize', 'DRY-ad',
    'Nana' for Nenana) leak onto screen as typos (the 2026-07-20 panel caught all three
    as hard blockers). vo_script.json declares a `caption_fixups` {phonetic: display}
    map; apply it to every cue text (case-insensitive, word-boundary) so the REAL
    spelling always shows. Permanent pipeline fix so no future run leaks a respelling."""
    import re as _re
    sp = os.path.join(OUT, "vo_script.json")
    fixups = json.load(open(sp)).get("caption_fixups", {}) if os.path.exists(sp) else {}
    if not fixups:
        return caps
    # Use alnum lookarounds, NOT \b: \b fails on tokens whose edge char is punctuation
    # (e.g. "A.I." ends in '.', so \b after it never matches and the fixup silently no-ops —
    # the 2026-07-21c panel caught "A.I." leaking on screen while NOAA/GAIA normalized fine).
    # Longest keys first so a key that is a prefix of another can't pre-empt it.
    for c in caps:
        t = c.get("text", "")
        for wrong, right in sorted(fixups.items(), key=lambda kv: -len(kv[0])):
            t = _re.sub(r"(?<![A-Za-z0-9])" + _re.escape(wrong) + r"(?![A-Za-z0-9])", right, t, flags=_re.IGNORECASE)
        c["text"] = t
    return caps


def _episode_scene_count():
    """How many scenes Episode.tsx actually renders.

    Episode.tsx falls back to hardcoded DEFAULT_BOUNDS when
    `scenes.length !== SCENE_COMPONENTS.length`, and it does so SILENTLY: the
    picture keeps the previous episode's frame timings while the audio follows
    this episode's VO, so the words and the pictures drift with nothing printed.
    That already happened once upstream and the comment at the top of
    SCENE_START_LINE warns about it in prose, which is not a check.

    So read the truth out of the component and compare. Prose is not a gate.
    """
    import re
    ep = os.path.join(REPO, "video-engine", "src", "Episode.tsx")
    if not os.path.exists(ep):
        return None
    m = re.search(r"const\s+SCENE_COMPONENTS\s*:[^=]*=\s*\[([^\]]*)\]", open(ep).read())
    if not m:
        return None
    return len([p for p in (x.strip() for x in m.group(1).split(",")) if p])


def main():
    lines = json.load(open(os.path.join(OUT, "vo_lines.json")))["lines"]
    caps = _apply_caption_fixups(json.load(open(os.path.join(OUT, "captions.json"))))
    start = {L["idx"]: L["start"] for L in lines}
    last_end = max(L["end"] for L in lines)
    total_s = last_end + TAIL
    total_f = round(total_s * FPS)

    # HARD: the 60 second law. Fail here, before the render, not at Phase 6 after
    # paying for it.
    if total_s > MAX_TOTAL_S:
        raise SystemExit(
            f"FAIL sixty_seconds: VO ends at {last_end:.2f}s, +{TAIL}s tail = "
            f"{total_s:.2f}s, over the {MAX_TOTAL_S}s hard gate.\n"
            f"       Cut the script to {MAX_SCRIPT_S:.1f}s or less and rebuild the VO.\n"
            f"       Do NOT raise the ceiling; it is a law (CLAUDE.md)."
        )

    # HARD: the scene-count contract with Episode.tsx.
    want = _episode_scene_count()
    if want is not None and want != len(SCENE_START_LINE):
        raise SystemExit(
            f"FAIL scene_count: SCENE_START_LINE has {len(SCENE_START_LINE)} entries but "
            f"Episode.tsx renders {want} scenes.\n"
            f"       Episode would SILENTLY fall back to DEFAULT_BOUNDS and the picture "
            f"would drift from the words.\n"
            f"       Fix SCENE_START_LINE (this file) or SCENE_COMPONENTS (Episode.tsx) "
            f"so they agree."
        )

    bounds = [round(start[si] * FPS) for si in SCENE_START_LINE]
    scenes = []
    for i, b in enumerate(bounds):
        end = bounds[i + 1] if i + 1 < len(bounds) else total_f
        scenes.append({"from": b, "dur": end - b})

    props = {"captions": caps, "scenes": scenes, "total": total_f}
    # voice-acting data (scripts/vo_envelope.py): per-frame mouth envelope + the
    # vo-director's emphasis accents, for lib/voice.tsx. Optional, additive.
    mt = os.path.join(OUT, "mouth_track.json")
    ac = os.path.join(OUT, "accents.json")
    if os.path.exists(mt):
        props["mouth"] = json.load(open(mt))["values"]
    if os.path.exists(ac):
        props["accents"] = json.load(open(ac))
    json.dump(props, open(os.path.join(OUT, "episode_props.json"), "w"))
    print(f"total={total_f}f ({total_s:.2f}s)  mouth={'y' if 'mouth' in props else 'n'} accents={len(props.get('accents', []))}")
    for i, s in enumerate(scenes):
        print(f"  S{i+1}: from={s['from']} dur={s['dur']} ({s['dur']/FPS:.2f}s)")


if __name__ == "__main__":
    main()
