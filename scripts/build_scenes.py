#!/usr/bin/env python3
"""Compute scene frame boundaries from the VO line timings so the timeline stays
in sync with the narration automatically. Scene i begins at the start of a mapped
VO line; S1 covers lines 0-1. Writes episode_props.json {captions, scenes, total}.
"""
import json, os, sys

# scripts/ on the path, so `run_guard` resolves however this is invoked.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
# THE FALLBACK, not the contract. This literal is case 0001's shot map, and it
# was committed here as though it were a property of the pipeline: on 2026-08-02
# it had 7 entries against an Episode.tsx carrying 9 SCENE_COMPONENTS, so the
# generic Episode path documented in CLAUDE.md's quickstart could not run at all.
# An episode-specific constant in a per-run script is a contract that goes stale
# every single run and is only noticed when it happens to crash.
#
# The shot map belongs to THE STORYBOARD, which is written per run and knows the
# real shot boundaries. scene_start_lines() derives it from there and falls back
# to this only when no board exists, which is the pre-board draft case.
SCENE_START_LINE = [0, 2, 4, 5, 7, 9, 11]   # 2026-07-29: 7 shots, case 0001


def scene_start_lines(lines, board_path=None):
    """-> [vo line index] where each shot begins, derived from the storyboard.

    A shot boundary must land ON a VO line start or the picture drifts from the
    words, which is the Gate 0B finding that killed the first board (the
    collapse was spoken at 19.6s and drawn at 33.9s). So each shot's start time
    is snapped to the LAST line that has begun by then, and duplicates collapse:
    two shots inside one line is a camera move, not a scene boundary the props
    file can express.
    """
    board_path = board_path or os.path.join(OUT, "storyboard.json")
    if not os.path.exists(board_path):
        return list(SCENE_START_LINE), "the committed fallback (no storyboard on disk)"
    try:
        board = json.load(open(board_path))
    except Exception as e:
        raise SystemExit(f"FAIL storyboard: {board_path} exists and cannot be parsed: {e}")

    shots = board.get("shots") or board.get("board") or []
    starts = []
    for sh in shots:
        if not isinstance(sh, dict):
            continue
        # `t` in this repo's boards is [start, end], not a scalar. Accept both,
        # plus the scalar spellings a future board might use.
        t = sh.get("t")
        if isinstance(t, (list, tuple)) and t and isinstance(t[0], (int, float)):
            starts.append(float(t[0]))
            continue
        for k in ("t", "start", "at", "from_s", "start_s"):
            v = sh.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                starts.append(float(v))
                break
    if not starts:
        return list(SCENE_START_LINE), "the committed fallback (no shot times in the board)"

    line_starts = sorted((L["start"], L["idx"]) for L in lines)
    out = []
    for t in sorted(starts):
        idx = line_starts[0][1]
        for st, i in line_starts:
            if st <= t + 0.001:
                idx = i
            else:
                break
        if idx not in out:
            out.append(idx)
    out.sort()
    if out and out[0] != line_starts[0][1]:
        # The first shot must start the episode. A board whose first shot lands
        # after line 0 leaves the opening seconds with no scene at all.
        out.insert(0, line_starts[0][1])
    return out, f"{board_path} ({len(shots)} shot(s) -> {len(out)} scene(s))"


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
    # COUNT THE SUBSTITUTIONS. The comment above recounts a fixup that silently
    # no-opped and put "A.I." on screen, and then this function was written with
    # a bare re.sub that cannot tell that story about itself: a `caption_fixups`
    # key that no longer appears in the transcript is indistinguishable from one
    # that worked. A respelling declared and not applied is the exact defect the
    # 2026-07-21c panel caught, so it fails here rather than on the picture.
    hits = {k: 0 for k in fixups}
    for c in caps:
        t = c.get("text", "")
        for wrong, right in sorted(fixups.items(), key=lambda kv: -len(kv[0])):
            t, n = _re.subn(r"(?<![A-Za-z0-9])" + _re.escape(wrong) + r"(?![A-Za-z0-9])",
                            right, t, flags=_re.IGNORECASE)
            hits[wrong] += n
        c["text"] = t
    dead = sorted(k for k, n in hits.items() if n == 0)
    if dead:
        raise SystemExit(
            f"FAIL caption_fixups: {dead} are declared in vo_script.json and match "
            f"NOTHING in the captions.\n"
            f"       Either the respelling changed and the fixup is stale, or the "
            f"pattern is wrong and the phonetic spelling is about to ship on screen.\n"
            f"       A fixup that matches zero times looks exactly like one that "
            f"worked, which is how 'A.I.' reached the picture."
        )
    for k, n in sorted(hits.items()):
        print(f"  caption fixup {k!r} -> applied {n}x")
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

    # The shot map for THIS run, from THIS run's board.
    scene_lines, source = scene_start_lines(lines)
    print(f"  scene map from {source}: {scene_lines}")

    # HARD: the scene-count contract with Episode.tsx.
    want = _episode_scene_count()
    if want is not None and want != len(scene_lines):
        raise SystemExit(
            f"FAIL scene_count: the shot map has {len(scene_lines)} entries but "
            f"Episode.tsx renders {want} scenes.\n"
            f"       source: {source}\n"
            f"       Episode would SILENTLY fall back to DEFAULT_BOUNDS and the picture "
            f"would drift from the words.\n"
            f"       Fix the storyboard's shot count or SCENE_COMPONENTS (Episode.tsx) "
            f"so they agree."
        )

    # A verdict, not a KeyError. This was `start[si]` against a hardcoded map, so
    # a run whose VO had fewer lines than the map expected died on a bare
    # `KeyError: 7` in a file whose other two failures are careful messages.
    missing = [si for si in scene_lines if si not in start]
    if missing:
        raise SystemExit(
            f"FAIL scene_bounds: the shot map points at VO line(s) {missing} and this "
            f"run's VO has {len(start)} line(s), indices "
            f"{sorted(start)[:3]}..{sorted(start)[-1:]}.\n"
            f"       source: {source}\n"
            f"       A shot anchored to a line that was never spoken has no start time."
        )

    bounds = [round(start[si] * FPS) for si in scene_lines]
    scenes = []
    for i, b in enumerate(bounds):
        end = bounds[i + 1] if i + 1 < len(bounds) else total_f
        scenes.append({"from": b, "dur": end - b})

    props = {"captions": caps, "scenes": scenes, "total": total_f}
    # voice-acting data (scripts/vo_envelope.py): per-frame mouth envelope + the
    # vo-director's emphasis accents, for lib/voice.tsx. Optional, additive.
    # THROUGH THE FRESHNESS GUARD. These two were `if os.path.exists(...)`, which
    # is exactly the read scripts/run_guard.py was written for and never wired
    # into: out/dispatch/ survives across container sessions, so the PREVIOUS
    # episode's mouth envelope at the right path is byte-for-byte
    # indistinguishable from this one's, and the mouths would move to the last
    # cut's audio. optional() returns None when the file was never written and
    # RAISES when it exists and predates this run.
    from run_guard import optional
    mt = optional(os.path.join(OUT, "mouth_track.json"), label="mouth track")
    ac = optional(os.path.join(OUT, "accents.json"), label="accents")
    if mt:
        props["mouth"] = json.load(open(mt))["values"]
    if ac:
        props["accents"] = json.load(open(ac))
    json.dump(props, open(os.path.join(OUT, "episode_props.json"), "w"))
    print(f"total={total_f}f ({total_s:.2f}s)  mouth={'y' if 'mouth' in props else 'n'} accents={len(props.get('accents', []))}")
    for i, s in enumerate(scenes):
        print(f"  S{i+1}: from={s['from']} dur={s['dur']} ({s['dur']/FPS:.2f}s)")


def self_test():
    """A gate that cannot fail certifies nothing, and this file had no self-test
    while carrying three SystemExit gates and a hardcoded episode shot map."""
    import tempfile
    ok = True
    lines = [{"idx": i, "start": t, "end": t + 1.5}
             for i, t in enumerate([0.0, 3.0, 7.0, 11.0, 16.0, 22.0])]

    def board(times):
        return {"shots": [{"id": f"s{i+1}", "t": [a, b]}
                          for i, (a, b) in enumerate(times)]}

    checks = []
    with tempfile.TemporaryDirectory() as d:
        def write(doc):
            q = os.path.join(d, "b.json")
            json.dump(doc, open(q, "w"))
            return q

        got, src = scene_start_lines(lines, write(board([(0.0, 3.0), (7.0, 11.0), (16.0, 24.0)])))
        checks.append(("snaps every shot onto a VO line start", got == [0, 2, 4]))
        checks.append(("names where the map came from", "b.json" in src))

        # A shot that starts mid-line snaps BACK to the line that is speaking,
        # never forward, or the picture cuts before the words it belongs to.
        got, _ = scene_start_lines(lines, write(board([(0.0, 3.0), (8.4, 11.0)])))
        checks.append(("a mid-line shot snaps back, not forward", got == [0, 2]))

        # Two shots inside one line is a camera move, not a scene boundary.
        got, _ = scene_start_lines(lines, write(board([(0.0, 1.0), (1.2, 3.0), (7.0, 9.0)])))
        checks.append(("two shots inside one line collapse to one scene", got == [0, 2]))

        # A board whose first shot lands late still starts the episode at line 0.
        got, _ = scene_start_lines(lines, write(board([(7.0, 11.0), (16.0, 22.0)])))
        checks.append(("the first scene always starts the episode", got[0] == 0))

        # No board is the pre-board draft case and falls back, loudly.
        got, src = scene_start_lines(lines, os.path.join(d, "absent.json"))
        checks.append(("no board falls back and says so",
                       got == list(SCENE_START_LINE) and "fallback" in src))

        # A board that is PRESENT and unparseable is not a missing one.
        bad = os.path.join(d, "bad.json")
        open(bad, "w").write("{not json")
        try:
            scene_start_lines(lines, bad)
            checks.append(("a CORRUPT board is refused, not treated as absent", False))
        except SystemExit:
            checks.append(("a CORRUPT board is refused, not treated as absent", True))

    for name, good in checks:
        print(f"  {'ok  ' if good else 'FAIL'} {name}")
        ok &= bool(good)
    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    main()
