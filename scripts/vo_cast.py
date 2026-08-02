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
  python scripts/vo_cast.py --dry-run          # casting + timing, no API calls
  python scripts/vo_cast.py --fit              # measure real takes, freeze the timings
  python scripts/vo_cast.py                    # synthesize out/dispatch/vo.wav
  python scripts/vo_cast.py --self-test        # prove the guards fire

--fit before the real synthesis, always. The timing check below assumes 3.6
words/sec and the measured cast runs 1.85 to 2.81, per line, so the guess fails
AFTER you have paid for the takes. See fit().

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
# THE MODEL LIVES IN vo_gemini AND NOWHERE ELSE.
#
# This file used to carry `os.environ.setdefault("DISPATCH_GEMINI_TTS_MODEL",
# "gemini-2.5-pro-preview-tts")` right here, at module scope. vo_gemini is
# imported LATER, inside take(), so by the time it ran its own
# `os.environ.get(..., "gemini-3.1-flash-tts-preview")` the variable was already
# set and the newer model never won. Every take of case 0002 was therefore
# synthesized on 2.5-pro while the run reported 3.1-flash, including the takes
# the owner then described as robotic. Two defaults for one setting is the bug;
# the older one silently outranked the newer one purely by import order, and
# nothing failed, so it shipped and got written down as fact.
#
# So there is exactly one default now, in vo_gemini.MODEL, and expected_model()
# below asserts what actually resolved instead of trusting either comment.
EXPECTED_TTS_MODEL = "gemini-3.1-flash-tts-preview"


def resolved_model():
    """The model that will REALLY be used, read back from vo_gemini after import."""
    sys.path.insert(0, SKILL)
    import vo_gemini
    return vo_gemini.MODEL


# Google's own one-word dispositions for the prebuilt voices. Only the flat end
# of the roster is listed, because that is the end that has to be refused; a
# voice absent from this map is not assumed good, it is simply not KNOWN flat,
# and the mechanical gate does not pretend otherwise.
FLAT_VOICES = {
    "Schedar": "Even", "Charon": "Informative", "Rasalgethi": "Informative",
    "Iapetus": "Clear", "Erinome": "Clear", "Achernar": "Soft",
    "Vindemiatrix": "Gentle", "Despina": "Smooth", "Algieba": "Smooth",
    "Sadaltager": "Knowledgeable",
}

# Words that, in a director's note, ask the model to REMOVE prosody. "Deadpan"
# is deliberately NOT here: deadpan is a legitimate comic register and the show
# needs it. What broke Dee was pairing it with instructions that spell out the
# mechanism, so the mechanism is what gets refused.
FLATTENING_PHRASES = (
    "monotone", "no rising intonation", "no intonation", "no inflection",
    "without inflection", "flat delivery", "completely flat", "no variation",
    "no pitch", "even tone", "and monotone",
)


def casting_problems(table=None):
    """Return the casting-law violations in a CAST table. Empty list means clean.

    Two checks, one per cause of the 2026-08-02 Dee failure: a flat VOICE, and a
    brief that directs flatness. A character may opt out with flat_ok, which
    exists for exactly one character and says why in the table."""
    t = CAST if table is None else table
    out = []
    for who, c in t.items():
        if c.get("flat_ok"):
            continue
        v = c.get("voice", "")
        if v in FLAT_VOICES:
            out.append(f"{who} is cast as {v}, whose roster descriptor is "
                       f"\"{FLAT_VOICES[v]}\"; cast for eccentricity instead")
        brief = " ".join(str(c.get(k, "")) for k in ("style", "pace", "scene")).lower()
        for p in FLATTENING_PHRASES:
            if p in brief:
                out.append(f"{who}'s brief directs the absence of prosody (\"{p}\"); "
                           f"dry withholds the REACTION, never the melody")
                break
    return out


# ---------------------------------------------------------------------------
# THE CASTING TABLE
#
# Voice choice is doing real work here, so the reasoning is written down rather
# than left to whoever edits this next.
#
# CASTING LAW, 2026-08-02, after the owner said Dee sounded "mad robotic" and had
# "no fluctuation": READ THE ROSTER DESCRIPTOR BEFORE YOU CAST. Google ships each
# prebuilt voice with a one-word disposition, and that disposition is a property
# of the voice that direction does not overcome. Dee was cast as Schedar, whose
# descriptor is literally "Even", and then handed a brief demanding "completely
# deadpan" with "no rising intonation". Flattest voice in the catalogue, told to
# flatten. Two causes stacked, and the sweep that replaced her measured all seven
# candidates at 3.46 to 4.12 semitones of pitch variance, which is to say the
# soundcheck could not tell them apart and the ear could.
#
# The two rules that came out of it:
#   1. Cast for ECCENTRICITY. A human character never gets a voice whose
#      descriptor is a synonym for flat (Even, Neutral, Calm). Prefer the ones
#      with a disposition: Forward, Lively, Firm, Casual, Mature, Gravelly.
#   2. NEVER DIRECT THE ABSENCE OF PROSODY. "Dry" and "deadpan" describe a
#      withheld REACTION, not a withheld melody. A brief that says monotone, flat,
#      even, no intonation or no inflection gets exactly what it asked for.
#
# THE ONE EXEMPTION is THE INSTITUTION, and the exemption is the joke: it is a
# phone tree, its blandness is the character, and a lively read would destroy it.
# It is marked exempt in the table so a future pass does not "fix" it.
CAST = {
    "RAY": {
        # Gravelly. Ray is a tired adult who has already found out, not an
        # excited one. A bright voice makes him a ranter and the register dies.
        "voice": "Algenib",
        "name": "Ray",
        "scene": ("A quiet street at night. Ray has just read a federal filing. He is "
                  "not shocked and he is not performing outrage; he found out ten "
                  "minutes ago and already reached his verdict. He is a tired working "
                  "adult who is annoyed and wants the conversation over with."),
        "style": ("Flat, unimpressed, deadpan American, and genuinely irritated. The "
                  "contempt points UPWARD at the institution and never at the person "
                  "he is talking to. He is RIGHT and he knows it. He arrives at "
                  "verdicts, he never rants, and he never explains the joke. Let real "
                  "annoyance colour the words rather than volume. He swears like a "
                  "tired adult, never like an excited teenager."),
        "pace": ("Fast and clipped. Run the sentences together. No dramatic pauses "
                 "except where the transcript marks one, no drawn-out words, no "
                 "announcer cadence."),
        "accent": "General American, working class.",
        # Kept so --dry-run and older callers still work.
        "style_legacy": "fast and clipped, annoyed and unimpressed",
    },
    "DEE": {
        # Forward. NOT "Even" (Schedar), which was the pick through 2026-08-02 and
        # was wrong twice over: the roster's own word for that voice is "Even", and
        # the brief underneath it ASKED for flatness. Owner verdict on the result,
        # twice: "mad robotic", "no fluctuation in her voice". See the DRY IS NOT
        # FLAT note below; do not re-flatten this brief.
        "voice": "Pulcherrima",
        "name": "Dee",
        "scene": ("The same street at night. Dee has the printout in her hand and she is "
                  "showing Ray the part that matters. She is not reading a document to "
                  "an empty room, she is building a case to a person standing in front "
                  "of her, and she wants him to get to the same place she already is."),
        "style": ("Dry, sharp and quietly contemptuous of the document, not of Ray. "
                  "DRY IS NOT FLAT. She withholds the obvious REACTION, never the "
                  "melody of her own voice: a real person reading a number she finds "
                  "absurd still lands on the absurd part, still leans on the word that "
                  "does the damage, still lets the pitch fall away on the throwaway "
                  "half of the sentence. Use natural conversational intonation with "
                  "real variation from phrase to phrase. She underlines by pointing at "
                  "the fact, never by raising her volume. She has no patience left and "
                  "it is audible."),
        "pace": ("Brisk and conversational, the clip of someone who has read this twice "
                 "already and wants you to see the line she is pointing at. Numbers are "
                 "spoken like a person quoting an outrageous figure to a friend, with "
                 "the weight on the part that makes it outrageous, NEVER recited like a "
                 "digit string or an account number. Do not pause between sentences "
                 "unless the transcript marks it."),
        "accent": "General American.",
        "style_legacy": "dry, sharp and out of patience, quoting a document she finds absurd",
    },
    "INSTITUTION": {
        # Smooth. The politeness is the menace, so it must sound HELPFUL, never
        # threatening. This is hold music with a mouth.
        "voice": "Despina",
        # THE ONE EXEMPTION from the casting law above. Despina's descriptor is
        # "Smooth" and that is the point: this character is a phone tree, its
        # blandness IS the joke, and an eccentric read would turn a process into
        # a villain with opinions. Do not "fix" this one.
        "flat_ok": "a phone tree; the blandness is the character",
        "name": "The Institution",
        "scene": ("An automated telephone system reading a policy clause to a customer "
                  "who has been on hold. Nobody is present. Nothing is being decided."),
        "style": ("Smooth, pleasant, unfailingly polite corporate automation. The "
                  "POLITENESS is the menace, never threat. It does not acknowledge the "
                  "question it was asked. It has no opinion because it is a process "
                  "working exactly as designed. NEVER use the [robotic] tag: it is "
                  "banned in vo_gemini and it makes this sound broken rather than calm."),
        "pace": ("Normal announcement pace, slightly too even. A recorded menu does not "
                 "drag. Legal and remedy clauses may be marked [extremely fast] in the "
                 "transcript, which reads as a disclaimer and is in character."),
        "accent": "General American, corporate neutral.",
        "style_legacy": "smooth, pleasant and automated, unfailingly polite",
    },
}

# THE TAG VOCABULARY, and which character may use what. Confirmed by owner A/B on
# 2026-08-02: tagged takes were the ones described as having "real fluctuation",
# and untagged director-notes takes still read as competent reading. Tags are how
# this show gets a performance instead of a recital.
#
#   [sarcasm]        Ray. Documented as a powerful modifier and it lands.
#   [sigh]           Ray, before a verdict he is tired of reaching.
#   [scoffs]         Ray, on an absurd number.
#   [short pause]    ~250ms, a comma's worth of thinking.
#   [medium pause]   ~500ms. THE comic beat before a punchline.
#   [long pause]     ~1000ms. Use once an episode at most.
#   [extremely fast] The Institution, on legal or remedy text. Reads as a
#                    disclaimer, which is exactly what it is.
#   [flat]           Any character, to kill an intonation the model wants to add.
#
# BANNED: [robotic]. Tested and rejected by the owner as "a robot sound and
# horrid"; vo_gemini raises on it rather than trusting anyone to remember.
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

    # THE CASTING LAW. Checked on the real table every run, not only in the
    # self-test, because the failure it catches ships quietly: a flat voice
    # renders clean, passes every objective gate, and is only caught by a human
    # listening. See casting_problems().
    probs = casting_problems()
    row("cast for eccentricity, and no brief directs flatness",
        not probs, "; ".join(probs) if probs else "clean")

    # And the model the run will REALLY use, read back rather than asserted. A
    # stale override in this file silently outranked the newer default for the
    # whole of case 0002 and the run reported the model it did not use.
    try:
        m = resolved_model()
        row(f"TTS model is {EXPECTED_TTS_MODEL}", m == EXPECTED_TTS_MODEL, m)
    except Exception as e:
        row(f"TTS model is {EXPECTED_TTS_MODEL}", False, f"could not resolve: {e}")

    # The Institution is an emission, not a conversation. More than a couple of
    # lines means it has become a character you can argue with.
    inst = [p for p in planned if p["who"] == "INSTITUTION"]
    row("Institution speaks at most twice", len(inst) <= 2, f"{len(inst)} line(s)")

    bad = [p for p in planned if p["slot"] <= 0]
    row("no line starts before the previous ends", not bad,
        f"{len(bad)} overlap(s)" if bad else "clean")

    # ROOM TO BE SPOKEN. Prefer the MEASURED take over the heuristic whenever a
    # cached take exists, because the heuristic is a guess and the take is the
    # fact. The old rule was `slot < words / 3.6` in both directions, and 3.6 was
    # wrong twice over: it under-booked the slow direction (2026-08-02, Ray at
    # 1.85 w/s overran a slot this check had passed) and then over-booked the
    # fast one (same day, after the pace fix Ray runs 3.75 w/s and the check
    # started demanding more room than the audio needs, vetoing a timeline that
    # --fit had built from the real durations). A guess must never overrule a
    # measurement it disagrees with.
    tight = []
    for p in planned:
        measured = cached_duration(p)
        # Tolerance is NEGATIVE on purpose. --fit gives the final line a slot
        # exactly equal to its duration (the 1.5s tail follows it), so demanding
        # a cushion here fails a timeline that is correct by construction. A
        # genuine overrun is still caught at synthesis, which hard-fails on
        # dur > slot + 0.35 and refuses to slide the timeline.
        need = measured - 0.02 if measured is not None else max(1.0, len(p["text"].split()) / 3.6)
        if p["slot"] < need:
            tight.append(f"{p['who']}@{p['t']}s"
                         + ("(measured)" if measured is not None else "(estimated)"))
    row("every line has room to be spoken", not tight,
        f"{len(tight)} too tight: {tight[:3]}" if tight else "clean")
    return rows


def strip_tags(t):
    """Remove performance tags from anything a VIEWER reads.

    The tags are direction for the voice model, not dialogue. Left in, the
    burned-in caption says "[sarcasm] Twenty-eight speakers", which is both
    nonsense on screen and a backstage note shown to the audience. Stripped here,
    at the one place captions are produced, so no scene can forget."""
    import re as _re
    return _re.sub(r"\s*\[[^\]]{1,20}\]\s*", " ", t).strip()


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
    return [{"start": l["start"], "end": l["end"], "text": strip_tags(l["text"])}
            for l in lines_out]


def take_path(p):
    """Where this line's cached take lives. ONE definition, deliberately.

    This key existed in two copies, in cached_duration and in take, and the two
    then had to be edited in lockstep forever. They were not: the MODEL was
    missing from both, so changing the model would have replayed old audio under
    a new name. That is the third instance in one day of the same bug class, an
    input that changes the audio without changing the identity of the audio, so
    the key is computed in exactly one place now and everything reads it here.

    Anything that changes how a take SOUNDS belongs in this string.
    """
    import hashlib
    sys.path.insert(0, SKILL)
    import vo_gemini
    c = CAST[p["who"]]
    key = hashlib.sha1(
        f"{vo_gemini.MODEL}|{p['voice']}|{c.get('scene','')}|{c.get('style','')}"
        f"|{c.get('pace','')}|{c.get('accent','')}|{p['text']}".encode()).hexdigest()[:16]
    return os.path.join(TAKES, f"{key}.wav")


def cached_duration(p):
    """Seconds of the cached take for this line, or None if it has not been
    synthesized yet. Lets the guards check against fact instead of a constant."""
    import wave as _wave
    path = take_path(p)
    if not os.path.exists(path):
        return None
    try:
        with _wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


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
    import wave as _wave
    import numpy as np
    import vo_gemini

    c = CAST[p["who"]]
    path = take_path(p)   # see take_path: one key, and the model is in it
    if os.path.exists(path):
        with _wave.open(path, "rb") as w:
            return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype("float32") / 32767.0
    # Gemini TTS sometimes answers HTTP 200 with finishReason OTHER and no audio
    # at all. vo_gemini retries 429/500/503 but not that, so a single random
    # empty response would kill a whole run after most of the takes were already
    # paid for. Observed live on 2026-08-02. Retry it here; it is transient.
    a = None
    direction = {k: c[k] for k in ("name", "scene", "style", "pace", "accent") if k in c}
    for attempt in range(4):
        try:
            a = trim_silence(vo_gemini.synth(p["text"], voice=p["voice"],
                                             direction=direction), sr)
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
    # Which next step is right depends on the build path, and printing only one
    # of them is how case 0002 spent a Gate 0 blocker on a SCENE_START_LINE that
    # was never in its chain. A self-timed CaseNNNN composition takes no props.
    print("next: bash scripts/render.sh draft"
          "   (self-timed CaseNNNN comp: no props, no build_scenes.py)\n"
          "      python3 scripts/build_scenes.py first ONLY for a generic "
          "Episode.tsx build")
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

    # --- the casting law, both directions -------------------------------
    for name, table in [
        ("a human cast to a voice whose descriptor is flat",
         {"DEE": dict(CAST["DEE"], voice="Schedar")}),
        ("a brief that directs the ABSENCE of prosody",
         {"DEE": dict(CAST["DEE"], style="Precise and completely deadpan, with no "
                                         "rising intonation at the end of a sentence.")}),
        ("a brief that asks for monotone in the pace note",
         {"DEE": dict(CAST["DEE"], pace="Even and monotone throughout.")}),
    ]:
        problems = casting_problems(table)
        print(f"  {'ok  ' if problems else 'FAIL'} catches: {name}")
        ok &= bool(problems)

    exempt = casting_problems({"INSTITUTION": CAST["INSTITUTION"]})
    print(f"  {'ok  ' if not exempt else 'FAIL'} exempts: the Institution, whose flatness IS the joke")
    ok &= not exempt

    live = casting_problems(CAST)
    print(f"  {'ok  ' if not live else 'FAIL'} accepts: the cast as it stands today"
          + ("  <- " + "; ".join(live) if live else ""))
    ok &= not live

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
