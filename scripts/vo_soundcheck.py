#!/usr/bin/env python3
"""vo_soundcheck.py — measure how a take actually SOUNDS, not whether it exists.

THE PROBLEM THIS EXISTS TO FIX
Case 0002 shipped with every gate green and the owner's first note was that the
voices sound robotic. Nothing in the machine could have caught that: vo_cast
checks casting and slot arithmetic, mux_and_verify checks that audio is present,
render_gate checks the container. All of them pass on a perfect monotone drone.
The only judge of delivery was a human listening, which does not scale to a
daily show and cannot A/B thirty voices.

The upstream machine had this and the port lost it. scripts/setup_env.sh still
installs librosa "for the vo_soundcheck.py pitch-variance gate" against a file
that does not exist in this repo. This is that file, rebuilt, with no dependency
beyond numpy and scipy so it cannot silently skip.

WHAT IT MEASURES, and why each one is here

  pitch_var_st   Standard deviation of log-F0 in SEMITONES over voiced frames.
                 This is the "no fluctuation" complaint made numeric. A human
                 reading with intent moves around 2 to 4 semitones; a flat TTS
                 drone sits under 1.5. THE headline number.
  pitch_range_st 5th-to-95th percentile F0 spread. Catches a take that is mostly
                 flat but has one whoop in it, which std alone can be fooled by.
  dyn_db         Spread of frame RMS in dB across voiced frames. Delivery that
                 leans on words has dynamics; a drone does not.
  rate_wps       Words per second against the reference text. Too slow reads as
                 robotic no matter how good the pitch is (measured 2026-08-02:
                 Ray at 1.85 w/s sounded sedated, 3.75 sounded annoyed).
  pauses         Count and total duration of internal silences over 180ms. Comic
                 timing is pauses in the right places; a drone has none, and a
                 take that "read the director's notes aloud" has many.
  peak/clip      Obvious damage.
  overrun_ratio  Duration against what the word count predicts. The documented
                 Gemini failure mode is performing your DIRECTION as dialogue,
                 which makes a take dramatically longer than its text. A ratio
                 over ~1.8 means check the transcript.

WHAT IT CANNOT DO, stated plainly so nobody trusts it too far. It does not know
whether a take is FUNNY, whether the accent is right, whether a markup tag was
spoken aloud instead of performed, or -- tested and confirmed on 2026-08-02 --
whether a voice sounds ROBOTIC. That last one was the whole reason it was
commissioned, and it failed at it: see the labelled table below, where the take
the owner hated scored best on every prosody metric this file computes.

So it is a MALFUNCTION detector, not a taste engine. It catches dead audio,
clipping, a take that performed your director's notes as dialogue, and delivery
that is sedated or gabbling past any reasonable range. Those are real and they
were shipping unchecked. Tone still needs ears, and knowing which half is which
is the difference between a useful tool and a rubber stamp.

  python scripts/vo_soundcheck.py out/dispatch/takes/*.wav
  python scripts/vo_soundcheck.py --line "the words" take.wav
  python scripts/vo_soundcheck.py --episode        # every line of the built VO
  python scripts/vo_soundcheck.py --self-test      # prove the gate can go red

Exit 0 pass, 1 fail.
"""

import argparse
import glob
import json
import math
import os
import sys
import wave

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "out", "dispatch")

# ---------------------------------------------------------------------------
# WHAT THIS FILE IS ALLOWED TO FAIL A TAKE FOR
#
# An earlier version of this header claimed these numbers were "calibrated
# against real takes". They were not; they were guessed, and then real takes
# falsified them within the hour. Both falsifications are recorded because they
# are the whole reason the thresholds now look like this:
#
#   1. PITCH VARIANCE AND DYNAMICS DO NOT MEASURE "ROBOTIC". Tested against five
#      takes the owner labelled by ear on 2026-08-02, and the result was not
#      weak, it was INVERTED:
#
#        take              owner verdict   pitch_var   dyn_db
#        T5 [robotic]      "horrid"           3.79      18.1   <- worst, best numbers
#        T3 [medium pause] "real fluctuation" 3.22      20.4
#        T1 [sarcasm]      "real fluctuation" 2.54      13.4
#        T2 [sigh]         "real fluctuation" 1.42      10.7   <- liked, worst numbers
#
#      The take he hated scored highest on both and the take he liked scored
#      lowest. "Robotic" here is timbre and artefact, not prosody statistics, and
#      no amount of threshold tuning fixes a metric pointing the wrong way. These
#      numbers are printed for a human to interpret and are NEVER failed on. If a
#      future run is tempted to gate on them, read this table first.
#   2. FASTER IS NOT BETTER. The owner chose a 1.92 w/s take over a 2.83 w/s one,
#      because the slower take was performing and the faster one was reading.
#      A rate floor set to make the machine's preferred take pass would have
#      failed the owner's preferred take. So the floor only catches genuinely
#      sedated delivery, far below anything either of us liked.
#
# The honest split: this file HARD-FAILS damage and obvious malfunction, which
# it can measure, and REPORTS prosody, which it cannot judge. A soundcheck that
# pretends to have taste would just launder a guess into a gate.
MIN_ARTIC_WPS = 1.5         # below this is sedated by any standard
MAX_ARTIC_WPS = 5.2         # above this is unintelligible under burned captions
MAX_OVERRUN = 1.8           # duration vs word count: did it speak the DIRECTION?
CLIP_PEAK = 0.985

# Advisory only. Printed, never failed on, for the reasons above.
LOW_PITCH_VAR_ST = 2.0
LOW_DYN_DB = 6.0

VOICED_FLOOR_HZ, VOICED_CEIL_HZ = 70.0, 400.0


def read_wav(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
        if w.getsampwidth() != 2:
            raise ValueError(f"{path}: expected 16-bit PCM")
        a = np.frombuffer(raw, dtype="<i2").astype("float32") / 32768.0
        if w.getnchannels() == 2:
            a = a.reshape(-1, 2).mean(axis=1)
    return a, sr


def f0_track(a, sr, hop=0.010, win=0.040):
    """Autocorrelation pitch track. Deliberately dependency-free.

    librosa would be one line, but setup_env has failed to install it before and
    a soundcheck that silently skips is exactly the 204-to-everything failure in
    FIELD_NOTES. Autocorrelation is crude for absolute pitch and perfectly
    adequate for VARIANCE, which is all this file claims to measure.
    """
    hop_n, win_n = int(hop * sr), int(win * sr)
    lo, hi = int(sr / VOICED_CEIL_HZ), int(sr / VOICED_FLOOR_HZ)
    out = []
    for i in range(0, max(0, len(a) - win_n), hop_n):
        fr = a[i:i + win_n]
        rms = float(np.sqrt(np.mean(fr ** 2)))
        if rms < 0.012:                      # unvoiced or silence
            out.append((0.0, rms)); continue
        fr = fr - fr.mean()
        ac = np.correlate(fr, fr, mode="full")[win_n - 1:]
        if ac[0] <= 0:
            out.append((0.0, rms)); continue
        ac = ac / ac[0]
        seg = ac[lo:hi]
        if not len(seg):
            out.append((0.0, rms)); continue
        k = int(np.argmax(seg)) + lo
        # A real periodicity peak; anything weaker is noise pretending to be pitch.
        out.append((sr / k if ac[k] > 0.32 else 0.0, rms))

    # OCTAVE CORRECTION + SMOOTHING. Added 2026-08-02 after the first cut of this
    # file reported a 29-semitone range on a five-second line, which is not a
    # thing a human larynx does. A bare argmax lands on a sub-harmonic or a
    # harmonic constantly, so the "pitch variance" being measured was the
    # tracker's own instability. Fold every value toward the running median by
    # octaves, then median-filter. Without this the monotone guard is noise.
    vals = [f for f, _ in out if f > 0]
    if len(vals) >= 8:
        med = float(np.median(vals))
        fixed = []
        for f, r in out:
            if f > 0:
                while f > med * 1.6:
                    f /= 2.0
                while f < med / 1.6:
                    f *= 2.0
            fixed.append((f, r))
        out = fixed
        f_arr = np.array([f for f, _ in out])
        voiced = f_arr > 0
        if voiced.sum() >= 5:
            sm = f_arr.copy()
            idx = np.where(voiced)[0]
            for j in range(len(idx)):
                w = idx[max(0, j - 2):j + 3]
                sm[idx[j]] = np.median(f_arr[w])
            out = [(sm[i], out[i][1]) for i in range(len(out))]
    return out


def pauses_over(a, sr, thr=0.012, min_s=0.18):
    """Internal silences, ignoring lead and tail (trim_silence already took those)."""
    hop = int(0.010 * sr)
    quiet = [float(np.sqrt(np.mean(a[i:i + hop] ** 2))) < thr
             for i in range(0, max(0, len(a) - hop), hop)]
    runs, cur = [], 0
    for q in quiet:
        cur = cur + 1 if q else 0
        if not q and cur:
            runs.append(cur)
    if cur:
        runs.append(cur)
    runs = [r * 0.010 for r in runs if r * 0.010 >= min_s]
    return len(runs), round(sum(runs), 2)


def measure(path, text=None):
    a, sr = read_wav(path)
    dur = len(a) / sr
    track = f0_track(a, sr)
    f0 = np.array([f for f, _ in track if f > 0])
    rms = np.array([r for f, r in track if f > 0])

    if len(f0) >= 8:
        st = 12.0 * np.log2(f0 / np.median(f0))
        pitch_var = float(np.std(st))
        pitch_range = float(np.percentile(st, 95) - np.percentile(st, 5))
        med_f0 = float(np.median(f0))
    else:
        pitch_var = pitch_range = med_f0 = 0.0

    if len(rms) >= 8:
        db = 20.0 * np.log10(np.maximum(rms, 1e-6))
        dyn = float(np.percentile(db, 95) - np.percentile(db, 5))
    else:
        dyn = 0.0

    n_pause, pause_s = pauses_over(a, sr)
    words = len(text.split()) if text else None
    # Time actually spent SPEAKING. The owner picked a take this file called
    # "sedated" at 1.92 gross w/s, because its tags buy deliberate pauses. Rate
    # has to be measured over the speech, or the gate punishes exactly the
    # expressiveness it was built to encourage.
    speech_s = max(0.35, dur - pause_s)
    return {
        "file": os.path.basename(path),
        "duration_s": round(dur, 2),
        "words": words,
        "rate_wps": round(words / dur, 2) if words and dur else None,
        "artic_wps": round(words / speech_s, 2) if words else None,
        # 2.6 w/s is this cast's comfortable delivery; the ratio says how far the
        # take runs past what its own text should take.
        "overrun_ratio": round(dur / (words / 2.6), 2) if words else None,
        "speech_s": round(speech_s, 2),
        "median_f0_hz": round(med_f0, 1),
        "pitch_var_st": round(pitch_var, 2),
        "pitch_range_st": round(pitch_range, 2),
        "dyn_db": round(dyn, 1),
        "pauses": n_pause,
        "pause_s": pause_s,
        "peak": round(float(np.max(np.abs(a))) if len(a) else 0.0, 3),
    }


def verdict(m):
    """Returns (ok, [problems]). Only judges what it can actually hear."""
    bad = []
    if m.get("artic_wps") is not None and m["artic_wps"] < MIN_ARTIC_WPS:
        bad.append(f"SEDATED ({m['artic_wps']} w/s speaking < {MIN_ARTIC_WPS})")
    if m.get("artic_wps") is not None and m["artic_wps"] > MAX_ARTIC_WPS:
        bad.append(f"GABBLING ({m['artic_wps']} w/s speaking > {MAX_ARTIC_WPS})")
    if m["overrun_ratio"] is not None and m["overrun_ratio"] > MAX_OVERRUN:
        bad.append(f"OVERRUN x{m['overrun_ratio']} (did it perform the DIRECTION as dialogue?)")
    if m["peak"] >= CLIP_PEAK:
        bad.append(f"CLIPPING (peak {m['peak']})")
    if m["duration_s"] < 0.25 or m["peak"] < 0.02:
        bad.append("DEAD (no usable audio)")
    return (not bad), bad


def advisories(m):
    """Deliberately empty of prosody judgement.

    An earlier cut flagged "flat pitch" and "low dynamics" here. The labelled
    test in the header shows both metrics ran BACKWARDS against the owner's ear,
    so printing them as concerns would actively mislead the next run into
    "fixing" takes that are fine. The numbers stay in the table; the opinions
    are gone."""
    return []


def report(rows):
    ok_all = True
    print(f"  {'take':<34}{'dur':>6}{'artic':>6}{'pitch':>7}{'range':>7}{'dyn':>6}{'paus':>6}  verdict")
    for m in rows:
        ok, bad = verdict(m)
        ok_all &= ok
        adv = advisories(m)
        tail = "; ".join(bad) if bad else ("ok" + (f"   [{', '.join(adv)}]" if adv else ""))
        print(f"  {m['file'][:33]:<34}{m['duration_s']:>6}"
              f"{(m.get('artic_wps') or 0):>6}"
              f"{m['pitch_var_st']:>7}{m['pitch_range_st']:>7}{m['dyn_db']:>6}{m['pauses']:>6}  "
              + tail)
    return ok_all


def episode():
    """Every line of the built VO, sliced out of vo.wav by its measured timings."""
    lines = json.load(open(os.path.join(OUT, "vo_lines.json")))["lines"]
    a, sr = read_wav(os.path.join(OUT, "vo.wav"))
    rows = []
    for l in lines:
        seg = a[int(l["start"] * sr):int(l["end"] * sr)]
        if not len(seg):
            continue
        tmp = os.path.join(OUT, "takes", f"_sc_{l['idx']}.wav")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        with wave.open(tmp, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(seg, -1, 1) * 32767).astype("<i2").tobytes())
        m = measure(tmp, l["text"])
        m["file"] = f"{l['who']}: {l['text'][:24]}"
        rows.append(m)
        os.remove(tmp)
    return rows


def _tone(sr, dur, f0, vib_st, amp=0.25, noise=0.0, dyn_db=14.0):
    """Synthetic voiced signal with controllable pitch variance AND dynamics.

    `dyn_db` exists because the first cut of this self-test built its "good"
    fixture as a constant-amplitude tone, which by construction has no dynamic
    range, so the clean case failed on FLAT DYNAMICS and the gate reported
    itself wrong when it was right. A fixture that cannot represent the passing
    condition tests nothing. Same lesson as the ffmpeg self-test that could not
    build a video with the vendored binary.
    """
    t = np.arange(int(dur * sr)) / sr
    f = f0 * (2 ** ((vib_st * np.sin(2 * np.pi * 0.9 * t)) / 12.0))
    sig = np.zeros_like(t)
    for h, g in ((1, 1.0), (2, 0.5), (3, 0.28), (4, 0.14)):
        sig += g * np.sin(2 * np.pi * h * np.cumsum(f) / sr)
    sig *= amp / np.max(np.abs(sig))
    # syllable-rate amplitude envelope, so a "lively" fixture actually has the
    # loud-and-soft a lively read has
    env = 10 ** ((dyn_db / 2.0) * np.sin(2 * np.pi * 2.7 * t) / 20.0)
    sig *= env / np.max(env)
    if noise:
        sig += noise * np.random.RandomState(7).randn(len(sig)).astype("float32")
    return sig.astype("float32")


def self_test():
    """A gate that cannot fail certifies nothing (knowledge/FIELD_NOTES.md).
    Each case must trip the ONE guard it names, and the clean case must trip none.
    An earlier gate in this repo passed its self-test while a guard was dead,
    because the fixtures only asserted that SOMETHING went red."""
    import tempfile
    sr, ok = 24000, True
    d = tempfile.mkdtemp()

    def w(name, sig):
        p = os.path.join(d, name)
        with wave.open(p, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
            f.writeframes((np.clip(sig, -1, 1) * 32767).astype("<i2").tobytes())
        return p

    cases = [
        ("catches: a sedated read", w("slow.wav", _tone(sr, 6.0, 130, 3.0)),
         "four words here", "SEDATED"),
        ("catches: gabbling", w("fast.wav", _tone(sr, 1.0, 130, 3.0)),
         " ".join(["word"] * 9), "GABBLING"),
        ("catches: a dead/empty take", w("dead.wav", np.zeros(int(sr * 2.0), dtype="float32")),
         " ".join(["word"] * 4), "DEAD"),
        ("catches: clipping", w("clip.wav", _tone(sr, 3.0, 130, 3.0, amp=1.6)),
         " ".join(["word"] * 9), "CLIPPING"),
        ("catches: a take that ran the direction as dialogue",
         w("over.wav", _tone(sr, 9.0, 130, 3.0)), " ".join(["word"] * 9), "OVERRUN"),
    ]
    for name, path, text, want in cases:
        _, bad = verdict(measure(path, text))
        hit = any(b.startswith(want) for b in bad)
        print(f"  {'ok  ' if hit else 'FAIL'} {name}")
        if not hit:
            print(f"        wanted {want}, got {bad or ['nothing']}")
        ok &= hit

    clean = measure(w("good.wav", _tone(sr, 3.0, 130, 3.0)), " ".join(["word"] * 9))
    good, bad = verdict(clean)
    print(f"  {'ok  ' if good else 'FAIL'} accepts: a lively, well-paced take")
    if not good:
        print(f"        complained: {bad}")
    ok &= good

    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("takes", nargs="*")
    ap.add_argument("--line", help="reference text, for rate on a single take")
    ap.add_argument("--episode", action="store_true", help="measure the built VO line by line")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    if a.episode:
        rows = episode()
    else:
        paths = [p for t in a.takes for p in sorted(glob.glob(t))]
        if not paths:
            ap.error("give some .wav takes, or --episode, or --self-test")
        rows = [measure(p, a.line) for p in paths]

    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    ok = report(rows)
    print("\nsoundcheck: " + ("PASS" if ok else "FAIL"))
    print("  (measures monotony, pace and damage. It cannot hear whether a take is "
          "FUNNY,\n   nor whether a markup tag was spoken aloud instead of performed.)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
