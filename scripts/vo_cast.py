#!/usr/bin/env python3
"""vo_cast.py — synthesize an episode in THREE voices, not one.

THE PROBLEM THIS EXISTS TO FIX
The ported voice path spoke every line in one voice. This show has no narrator:
every line belongs to Ray, Dee or the Institution, and they are the entire
premise. One voice reading all three is not a stylistic compromise, it collapses
the cast into a podcast with drawings. Case 0001 shipped without audio rather
than ship a single-voice read.

HOW
Gemini TTS exposes ~30 prebuilt voices, so each character gets its own, plus a
per-line style instruction that carries the delivery direction from
knowledge/CAST_BIBLE.md into the synthesis itself.

TIMING IS TAKEN FROM THE SCRIPT, NOT FROM THE AUDIO
Each line is placed at the `t` the writer specified and the gaps are padded with
silence. That is deliberate: the storyboard is cut to those same numbers, so
anchoring both to one source means the picture cannot drift from the words. If a
take runs LONGER than its slot the script is wrong, and this fails loudly rather
than silently sliding everything after it.

  export GEMINI_API_KEY=...
  python scripts/vo_cast.py                    # synthesize out/dispatch/vo.wav
  python scripts/vo_cast.py --dry-run          # casting + timing, no API calls
  python scripts/vo_cast.py --self-test        # prove the guards fire

Exit 0 pass, 1 fail.
"""

import argparse
import json
import os
import sys
import wave

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "out", "dispatch")
SKILL = os.path.join(REPO, ".claude", "skills", "bigfunny-dispatch")

# From config/scoring_rubric.yaml and scripts/build_scenes.py. Duplicated
# nowhere else; the render pipeline enforces the same ceiling downstream.
MAX_TOTAL_S = 60.0
TAIL = 1.5

# ---------------------------------------------------------------------------
# THE CASTING TABLE
#
# Voice choice is doing real work here, so the reasoning is written down rather
# than left to whoever edits this next.
CAST = {
    "RAY": {
        # Gravelly. Ray is a tired adult who has already found out, not an
        # excited one. A bright voice makes him a ranter and the register dies.
        "voice": "Algenib",
        "style": ("in a flat, tired, matter-of-fact voice, like someone stating "
                  "a verdict they already reached. Do not sell the joke. Land on "
                  "the last word and stop"),
    },
    "DEE": {
        # Even. Her comedy is total deadpan delivery of something insane, so the
        # voice must not lift at the end of a sentence.
        "voice": "Schedar",
        "style": ("in an even, precise, dry voice, reading from a document. No "
                  "rising intonation at the end of sentences. Completely deadpan"),
    },
    "INSTITUTION": {
        # Smooth. The politeness is the menace, so it must sound HELPFUL, never
        # threatening. This is hold music with a mouth.
        "voice": "Despina",
        "style": ("in a smooth, pleasant, automated corporate voice, unfailingly "
                  "polite and slightly too even, like a recorded phone menu"),
    },
}

SPOKEN = set(CAST)          # ONSCREEN lines are text, never voiced.


def load_script(path=None):
    return json.load(open(path or os.path.join(OUT, "script.json")))


def plan(script):
    """Cast every spoken line and compute its slot. Raises on a casting gap."""
    lines = [l for l in script["lines"] if l["who"] in SPOKEN]
    unknown = {l["who"] for l in script["lines"]} - SPOKEN - {"ONSCREEN"}
    if unknown:
        raise SystemExit(
            f"FAIL casting: script has speaker(s) {sorted(unknown)} with no voice.\n"
            f"       Either cast them in CAST or, far more likely, the script "
            f"invented a fourth character. CAST_BIBLE.md says do not.")
    out = []
    for i, l in enumerate(lines):
        nxt = lines[i + 1]["t"] if i + 1 < len(lines) else script["estimated_seconds"]
        out.append({"idx": i, "who": l["who"], "t": l["t"], "slot": round(nxt - l["t"], 3),
                    "text": l["text"], "voice": CAST[l["who"]]["voice"],
                    "claims": l.get("claims", [])})
    return out


def check(script, planned):
    """The guards. Returns a list of (name, ok, detail)."""
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d)); return ok

    total = script["estimated_seconds"] + TAIL
    row(f"script + {TAIL}s tail <= {MAX_TOTAL_S}s", total <= MAX_TOTAL_S, f"{total:.1f}s")
    row("every spoken line is cast", all(p["voice"] for p in planned),
        f"{len(planned)} lines")

    voices = {p["who"]: p["voice"] for p in planned}
    row("three distinct voices, not one",
        len(set(voices.values())) == len(voices) and len(voices) > 1,
        ", ".join(f"{k}={v}" for k, v in sorted(voices.items())) or "none")

    # The Institution is an emission, not a conversation. More than a couple of
    # lines means it has become a character you can argue with.
    inst = [p for p in planned if p["who"] == "INSTITUTION"]
    row("Institution speaks at most twice", len(inst) <= 2, f"{len(inst)} line(s)")

    bad = [p for p in planned if p["slot"] <= 0]
    row("no line starts before the previous ends", not bad,
        f"{len(bad)} overlap(s)" if bad else "clean")

    tight = [f"{p['who']}@{p['t']}s" for p in planned
             if p["slot"] < max(1.0, len(p["text"].split()) / 3.6)]
    row("every line has room to be spoken", not tight,
        f"{len(tight)} too tight: {tight[:3]}" if tight else "clean")
    return rows


def cues(lines_out):
    """captions.json, in the shape Episode.tsx's schema declares:
    [{start, end, text}].

    THIS CLOSES A REAL BREAK IN THE CHAIN. build_scenes.py READS
    out/dispatch/captions.json and, before this, nothing in the repo wrote it:
    align_captions.py emits words60.json in a different schema entirely, so the
    first run with a working VO would have died on FileNotFoundError after
    paying for every TTS call.

    No forced alignment is needed at line level, and that is not a shortcut. The
    start comes from the script (which the storyboard is also cut to) and the end
    comes from the MEASURED duration of the take that was actually synthesized.
    Both are real numbers, not the stacked approximations that desynced the
    upstream show. Word-level karaoke timing would still want whisper; line-level
    does not, and line-level is what this show burns in."""
    return [{"start": l["start"], "end": l["end"], "text": l["text"]}
            for l in lines_out]


def trim_silence(a, sr, thr_db=-42.0, keep=0.06):
    """Strip the dead air Gemini pads onto every take.

    MEASURED 2026-08-02 across all three voices: each take carries about 0.25s
    of leading and 0.30s of trailing silence. Untrimmed, a 16 line episode
    spends nearly nine seconds saying nothing, which on a show with a HARD 60
    second ceiling is most of a beat wasted. Worse, the padding lands INSIDE the
    line's slot, so a take that fits perfectly well overruns and fails the run
    for a reason that has nothing to do with the writing.

    It also makes captions.json honest: the cue's end is the end of the SPEECH,
    not the end of the file, so a burned-in caption does not hang on screen over
    silence.

    Deliberately conservative. The threshold is low (-42 dBFS), the envelope is
    smoothed over 20ms so a single tick cannot defeat the trim, and `keep`
    leaves a little air on each end so a plosive onset is never clipped. If the
    take is silent end to end it is returned untouched rather than reduced to
    nothing, because an empty array downstream would be a much harder failure to
    read than a silent line.
    """
    import numpy as np
    thr = 10 ** (thr_db / 20.0)
    w = max(1, int(0.02 * sr))
    sm = np.convolve(np.abs(a), np.ones(w) / w, mode="same")
    idx = np.where(sm > thr)[0]
    if len(idx) == 0:
        return a
    pad = int(keep * sr)
    i0 = max(0, idx[0] - pad)
    i1 = min(len(a), idx[-1] + 1 + pad)
    return a[i0:i1]


TAKES = os.path.join(OUT, "takes")
# Breathing room between lines. Small, because a sixty second show cannot afford
# air, but non-zero because two takes butted together sound like one person
# gasping.
GAP = 0.26


def take(p, sr):
    """Synthesize one line, trimmed, CACHED on disk by (voice, style, text).

    The cache is the point. Before it, fitting a script meant guessing a
    words-per-second rate, failing on the first overrun, editing, and paying for
    every take again. Rates are not stable enough for that to converge: measured
    on 2026-08-02 the same voice ran 2.07 w/s on one line and 2.43 on another,
    because a full stop mid-line buys a pause the word count cannot see. So
    measure once, keep the audio, and lay the timeline out from what the takes
    ACTUALLY are.
    """
    import hashlib
    import wave as _wave
    import numpy as np
    import vo_gemini

    style = CAST[p["who"]]["style"]
    key = hashlib.sha1(f"{p['voice']}|{style}|{p['text']}".encode()).hexdigest()[:16]
    path = os.path.join(TAKES, f"{key}.wav")
    if os.path.exists(path):
        with _wave.open(path, "rb") as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype("float32") / 32767.0
    # Gemini TTS sometimes answers HTTP 200 with finishReason OTHER and no audio
    # at all. vo_gemini retries 429/500/503 but not that, so a single random
    # empty response would kill a whole run after most of the takes were already
    # paid for. Observed live on 2026-08-02. Retry it here; it is transient.
    a = None
    for attempt in range(4):
        try:
            a = trim_silence(vo_gemini.synth(p["text"], voice=p["voice"], style=style), sr)
            break
        except RuntimeError as e:
            if "no audio in response" not in str(e) or attempt == 3:
                raise
            print(f"    retry {attempt + 1}/3 ({p['who']}, empty TTS response)")
    os.makedirs(TAKES, exist_ok=True)
    with _wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype("<i2").tobytes())
    return a


def fit(script, planned, path):
    """Lay the timeline out from MEASURED take durations and write it back.

    This does NOT weaken the rule that the picture follows the script rather
    than the audio. It sets the script's numbers ONCE, from the real takes, and
    then everything downstream (storyboard, scene bounds, captions) is cut to
    those same frozen numbers. One source of truth, chosen with the facts in
    hand instead of guessed.
    """
    sys.path.insert(0, SKILL)
    from vo_backends import SR

    cursor, rows = 0.0, []
    for p in planned:
        dur = len(take(p, SR)) / SR
        rows.append((p, round(cursor, 2), dur))
        cursor += dur + GAP + float(p.get("hold", 0.0))
    end = cursor - GAP
    total = end + TAIL

    for p, t0, dur in rows:
        print(f"  {p['who']:<12} {t0:>5.2f}s  {dur:>5.2f}s  {p['text'][:46]}")
    print(f"\n  spoken ends {end:.2f}s, +{TAIL}s tail = {total:.2f}s")

    if total > MAX_TOTAL_S:
        over = total - MAX_TOTAL_S
        print(f"\nfit: FAIL. {over:.2f}s over the {MAX_TOTAL_S}s law. CUT roughly "
              f"{int(over * 2.2)} words. Do NOT raise the ceiling; it is a law.",
              file=sys.stderr)
        return 1

    by_idx = {id(p): t0 for p, t0, _ in rows}
    spoken = [l for l in script["lines"] if l["who"] in SPOKEN]
    for l, p in zip(spoken, planned):
        l["t"] = by_idx[id(p)]
    script["estimated_seconds"] = round(end, 2)
    json.dump(script, open(path, "w"), indent=2)
    print(f"\nfit: wrote {len(spoken)} timings to {path}. estimated_seconds={end:.2f}")
    return 0


def synth_all(planned, script):
    sys.path.insert(0, SKILL)
    import numpy as np
    from vo_backends import SR

    total_s = script["estimated_seconds"] + TAIL
    track = np.zeros(int(total_s * SR), dtype="float32")
    lines_out = []
    for p in planned:
        a = take(p, SR)
        dur = len(a) / SR
        if dur > p["slot"] + 0.35:
            raise SystemExit(
                f"FAIL slot overrun: {p['who']} at {p['t']}s needs {dur:.2f}s but "
                f"has {p['slot']:.2f}s.\n"
                f"       Cut the line. Sliding everything after it would drift the "
                f"picture off the words, which is the failure the storyboard "
                f"anchoring exists to prevent.")
        i0 = int(p["t"] * SR)
        track[i0:i0 + len(a)] += a[:max(0, len(track) - i0)]
        lines_out.append({"idx": p["idx"], "who": p["who"], "start": p["t"],
                          "end": round(p["t"] + dur, 3), "text": p["text"],
                          "voice": p["voice"], "claims": p["claims"]})
        print(f"  {p['who']:<12} {p['voice']:<10} {p['t']:>5.1f}s  {dur:>4.2f}s  "
              f"{p['text'][:44]}")

    peak = float(np.max(np.abs(track))) or 1.0
    track = (track / peak) * 0.89
    os.makedirs(OUT, exist_ok=True)
    wav = os.path.join(OUT, "vo.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((track * 32767).astype("<i2").tobytes())
    json.dump({"lines": lines_out}, open(os.path.join(OUT, "vo_lines.json"), "w"), indent=2)
    json.dump(cues(lines_out), open(os.path.join(OUT, "captions.json"), "w"), indent=2)
    print(f"\nwrote {wav} ({total_s:.1f}s), vo_lines.json, captions.json")
    print("next: python3 scripts/build_scenes.py  then  bash scripts/render.sh draft")
    return 0


def self_test():
    """Prove the guards fire. A gate that cannot fail certifies nothing."""
    ok = True
    cases = [
        ("a fourth character with no voice",
         {"estimated_seconds": 20, "lines": [{"t": 0, "who": "NARRATOR", "text": "hi"}]},
         "raises"),
        ("two lines overlapping",
         {"estimated_seconds": 20, "lines": [
             {"t": 5.0, "who": "RAY", "text": "one"}, {"t": 5.0, "who": "DEE", "text": "two"}]},
         "overlap"),
        ("a line with no room to be spoken",
         {"estimated_seconds": 20, "lines": [
             {"t": 0.0, "who": "RAY", "text": " ".join(["word"] * 40)},
             {"t": 1.0, "who": "DEE", "text": "ok"}]},
         "tight"),
        ("script over the 60s ceiling",
         {"estimated_seconds": 59.0, "lines": [{"t": 0.0, "who": "RAY", "text": "hi"}]},
         "over"),
    ]
    for name, script, _kind in cases:
        try:
            rows = check(script, plan(script))
            fired = any(not o for _, o, _ in rows)
        except SystemExit:
            fired = True
        print(f"  {'ok  ' if fired else 'FAIL'} catches: {name}")
        ok &= fired

    sample = [{"idx": 0, "who": "RAY", "start": 0.0, "end": 2.1, "text": "One.",
               "voice": "Algenib", "claims": []},
              {"idx": 1, "who": "DEE", "start": 3.0, "end": 5.4, "text": "Two.",
               "voice": "Schedar", "claims": []}]
    c = cues(sample)
    shape_ok = (len(c) == 2 and set(c[0]) == {"start", "end", "text"}
                and c[0]["end"] == 2.1 and c[1]["text"] == "Two.")
    print(f"  {'ok  ' if shape_ok else 'FAIL'} emits captions.json in Episode's schema")
    ok &= shape_ok

    good = {"estimated_seconds": 30.0, "lines": [
        {"t": 0.0, "who": "RAY", "text": "Short line."},
        {"t": 6.0, "who": "DEE", "text": "Another short line."},
        {"t": 14.0, "who": "INSTITUTION", "text": "We value your business."}]}
    rows = check(good, plan(good))
    clean = all(o for _, o, _ in rows)
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a well-formed three-voice script")
    ok &= clean
    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", help="default out/dispatch/script.json")
    ap.add_argument("--dry-run", action="store_true", help="casting + timing, no API")
    ap.add_argument("--fit", action="store_true",
                    help="synthesize (cached), measure, and rewrite the line timings "
                         "from the REAL take durations")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    path = a.script or os.path.join(OUT, "script.json")
    script = load_script(path)
    planned = plan(script)

    if a.fit:
        if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
            print("\nvo_cast --fit needs GEMINI_API_KEY to measure the takes.", file=sys.stderr)
            return 1
        return fit(script, planned, path)
    rows = check(script, planned)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<44} {d}")
    if not all(o for _, o, _ in rows):
        print("\nvo_cast: FAIL. Fix the script before synthesizing.")
        return 1

    print(f"\n  CASTING")
    for who in sorted({p["who"] for p in planned}):
        print(f"    {who:<12} {CAST[who]['voice']:<10} {CAST[who]['style'][:58]}...")

    if a.dry_run:
        print("\ndry run: casting and timing check out. No audio synthesized.")
        return 0
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        print("\nvo_cast: no GEMINI_API_KEY in the environment. Set it, or use "
              "--dry-run.", file=sys.stderr)
        return 1
    print()
    return synth_all(planned, script)


if __name__ == "__main__":
    sys.exit(main())
