#!/usr/bin/env python3
"""vo_envelope.py — a per-frame mouth-openness track from the REAL voice audio.

WHY THIS EXISTS
`lib/voice.tsx` has always referenced "mouth_track.json via scripts/vo_envelope.py".
That script was never ported, so nothing has ever driven a mouth from the audio.
Every figure in every episode moved its mouth on `ambientMouth()`, a free-running
sine that DISCARDS amplitude on purpose: a slow open/close cycle unrelated to the
words. The owner's verdict on 2026-08-02 was that the mouths "are just floating
around, which doesn't look like someone speaking", and they were right, because
nothing about that cycle knows whether anyone is speaking.

THE OWNER RULE THIS DOES NOT BREAK
The 2026-07-21 rule is "characters NEVER lip-sync THE NARRATOR", and the note
behind it was "it looked like they were trying to narrate". That rule was
inherited from a show that HAD a narrator talking over the scene, where syncing a
bystander's mouth to someone else's voice is exactly the failure described.

The Big Funny has no narrator. Every line belongs to Ray, Dee or the Institution,
and the speaker is standing in frame saying it. Moving the SPEAKER'S OWN mouth to
their OWN line is not what that rule forbids; it is what the rule's reasoning
asks for. The ban still holds where it was written: a listener never moves, and
nobody ever mouths a line that is not theirs.

WHAT IT PRODUCES
An amplitude envelope, not phonemes. Cartoon mouths have always been driven by
loudness, and it reads as speech because it starts and stops when the voice does.

  python3 scripts/vo_envelope.py --case 2
  python3 scripts/vo_envelope.py --case 2 --check
  python3 scripts/vo_envelope.py --self-test

Exit 0 pass, 1 fail.
"""
import argparse
import array
import json
import math
import os
import sys
import wave

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(REPO, "out", "dispatch")
SRC = os.path.join(REPO, "video-engine", "src")
FPS = 30

# Attack fast, release slow. A mouth snaps open on a consonant and closes
# lazily; symmetric smoothing gives a chewing motion, which is the thing that
# read as floating in the first place.
ATTACK = 0.62
RELEASE = 0.22
# Below this fraction of the take's own loudness the mouth is SHUT, not merely
# small. TalkMouth draws a closed line under 0.06, and a mouth that never fully
# closes is the single clearest tell of a fake talk cycle.
GATE = 0.055
# Ceiling percentile. Peak-normalising makes one plosive define the whole scale
# and flattens everything else to a mumble.
CEIL_PCT = 0.93
MAX_OPEN = 0.62
# Cartoon lip sync is a HANDFUL OF SHAPES, HELD. It is not a continuous analog
# level redrawn every frame: at 30fps that buzzes, and the owner's verdict on the
# first cut was that it "just is not matching or resonating". So the envelope is
# quantized to four mouth positions and each is held for at least MIN_HOLD
# frames, which is what a human animator does working on twos.
LEVELS = (0.0, 0.2, 0.4, 0.62)
MIN_HOLD = 3


def read_wav(path):
    with wave.open(path, "rb") as w:
        n, sr, width, ch = w.getnframes(), w.getframerate(), w.getsampwidth(), w.getnchannels()
        raw = w.readframes(n)
    if width != 2:
        raise ValueError(f"{path}: expected 16-bit PCM, got {width * 8}-bit")
    a = array.array("h")
    a.frombytes(raw[: len(raw) - (len(raw) % 2)])
    if ch > 1:                                  # mixdown
        a = array.array("h", [int(sum(a[i:i + ch]) / ch) for i in range(0, len(a) - ch + 1, ch)])
    return a, sr


def raw_envelope(samples, sr, fps=FPS):
    """CONTINUOUS openness 0..MAX_OPEN, before quantizing. accents() needs this:
    on the quantized track the derivative is zero inside every hold, so onsets
    vanish."""
    hop = max(1, int(round(sr / fps)))
    rms = []
    for i in range(0, len(samples), hop):
        chunk = samples[i:i + hop]
        if not chunk:
            break
        acc = 0
        for s in chunk:
            acc += s * s
        rms.append(math.sqrt(acc / len(chunk)) / 32768.0)
    if not rms:
        return []

    ordered = sorted(rms)
    ceil = ordered[min(len(ordered) - 1, int(len(ordered) * CEIL_PCT))]
    if ceil <= 0:
        return [0.0] * len(rms)

    out, prev = [], 0.0
    for v in rms:
        # perceptual-ish curve: loudness in dB reads closer to how open a mouth
        # looks than raw amplitude, which buries everything quiet.
        x = min(1.0, v / ceil)
        x = 0.0 if x < GATE else (x ** 0.6)
        k = ATTACK if x > prev else RELEASE
        prev = prev + (x - prev) * k
        # Clamp to the 0..1 the smoother works in, THEN scale to the widest the
        # mouth should ever open. Applying MAX_OPEN in both places (as the first
        # cut did) squares it, and the loudest shout in the episode came out at
        # 0.67 instead of 0.82.
        out.append(min(1.0, max(0.0, prev)) * MAX_OPEN)
    return out


def envelope(samples, sr, fps=FPS):
    """The SHIPPED mouth track: a few shapes, each held."""
    return _hold(_quantize(raw_envelope(samples, sr, fps)))


def spread(samples, sr, fps=FPS):
    """Per-frame LIP SPREAD 0..1, from the spectral centroid. The second axis.

    Amplitude alone cannot animate a mouth. The literature is blunt about it: a
    volume-to-jaw mapping "fails under close-up scrutiny because it cannot
    distinguish between vowel and consonant shapes", which is exactly the owner's
    note that the mouth was "not matching or resonating". Loudness says HOW MUCH
    mouth; it never says WHICH mouth, so every sound at the same volume gets the
    same shape and the face reads as a flapping hinge.

    Proper lip sync uses visemes: Preston Blair's canonical chart is 10 shapes,
    and production systems compress English's ~44 phonemes to 8-15. Doing that
    properly needs a phonetic alignment. The standard offline approximation, and
    what procedural systems use when they have no transcription, is a SPECTRAL
    feature alongside the amplitude one.

    The spectral centroid is the cheap honest proxy for it: energy concentrated
    high means a spread, bright shape (ee, s, t), energy concentrated low means a
    rounded one (oo, oh, w). Combined with openness that is a two-axis mouth,
    which is most of what the eye actually reads at this size.
    """
    import numpy as np
    hop = max(1, int(round(sr / fps)))
    a = np.frombuffer(samples.tobytes(), dtype="<i2").astype(np.float64) / 32768.0
    win = hop * 2
    freqs = np.fft.rfftfreq(win, 1.0 / sr)
    hann = np.hanning(win)
    out = []
    for i in range(0, len(a), hop):
        seg = a[i:i + win]
        if len(seg) < win:
            seg = np.pad(seg, (0, win - len(seg)))
        mag = np.abs(np.fft.rfft(seg * hann))
        tot = mag.sum()
        out.append(float((freqs * mag).sum() / tot) if tot > 1e-9 else 0.0)
    if not out:
        return []
    # Normalise against THIS voice, not an absolute Hz scale: the three
    # characters have different registers and a fixed threshold would give one of
    # them a permanently rounded mouth.
    v = np.array(out)
    voiced = v[v > 1]
    if voiced.size < 4:
        return [0.5] * len(out)
    lo, hi = np.percentile(voiced, 12), np.percentile(voiced, 88)
    if hi - lo < 1e-6:
        return [0.5] * len(out)
    return [round(float(min(1.0, max(0.0, (x - lo) / (hi - lo)))), 3) for x in v]


def _quantize(env):
    """Snap to the nearest of a few real mouth shapes."""
    return [min(LEVELS, key=lambda L: abs(L - v)) for v in env]


def _hold(q):
    """No mouth shape changes more often than every MIN_HOLD frames.

    Snapping alone still lets the mouth chatter between two neighbouring shapes
    on consecutive frames, which looks worse than the analog value it replaced.
    Holding is the half that makes it read as animation. The window takes the
    WIDEST opening in it, so a hold never swallows an attack.
    """
    out, i = [], 0
    while i < len(q):
        j = min(len(q), i + MIN_HOLD)
        out.extend([round(max(q[i:j]), 3)] * (j - i))
        i = j
    return out


def accents(env):
    """Per-frame ONSET strength 0..1.

    NOT WIRED TO A BODY, deliberately, and the reason lives here rather than in
    a commit message. Driving a whole figure from this looked GLITCHY, because
    the value has an instant attack: as a position offset it is a step function,
    and a step in position is a jump, not a movement. Per-syllable body motion is
    also simply wrong. Animation changes POSE on phrase boundaries and HOLDS it;
    it does not twitch once per stressed vowel. The composition already changes
    pose on line boundaries, which is where that belongs.

    Kept generated because it is the right signal for something that can absorb
    a step (a brow, a prop hit, a cut) rather than something that has to travel.

    Onset = the RISE in loudness, not loudness itself. A long held vowel is loud
    the whole way through and should get ONE accent at its attack, not a shove
    for its full duration. Rises are kept, falls discarded, then decayed so the
    body settles out of the hit instead of snapping back.
    """
    out, carry = [], 0.0
    for i, v in enumerate(env):
        rise = max(0.0, v - env[i - 1]) if i else 0.0
        hit = min(1.0, rise * 4.4)            # a real attack saturates; a drift does not
        carry = hit if hit > carry else carry * 0.82
        out.append(round(carry, 3))
    return out


HEADER = '''/**
 * {name} — GENERATED by scripts/vo_envelope.py from out/dispatch/vo.wav.
 *
 * DO NOT HAND-EDIT. Regenerate:  python3 scripts/vo_envelope.py --case {case}
 *
 * Per-frame mouth openness (0..1) at {fps}fps on the GLOBAL timeline, taken from
 * the loudness of the voice track that was actually synthesized. It is an
 * amplitude envelope, not phonemes, which is how cartoon mouths have always
 * worked: it reads as speech because it starts and stops when the voice does.
 *
 * Gate this with speakerAt(): the SPEAKER's mouth uses it, everyone else stays
 * shut. The 2026-07-21 rule bans mouthing a NARRATOR's voiceover, and this show
 * has no narrator; a listener still never moves.
 */
'''


def _rows(a):
    return "\n".join("  " + ", ".join(f"{v:g}" for v in a[i:i + 20]) + ","
                     for i in range(0, len(a), 20))


def render_ts(env, case, name, spr=None, raw=None):
    acc = accents(raw if raw is not None else env)
    spr = _hold([round(x, 2) for x in (spr or [0.5] * len(env))])[:len(env)]
    return (HEADER.format(name=name, case=case, fps=FPS)
            + "export const MOUTH: number[] = [\n" + _rows(env) + "\n];\n\n"
            + "/** LIP SPREAD 0..1: 0 rounded (oo, oh), 1 spread (ee, s). The second\n"
            + " *  axis. Openness alone cannot tell a vowel from a consonant. */\n"
            + "export const SPREAD: number[] = [\n" + _rows(spr) + "\n];\n\n"
            + "/** Where the voice PUSHES, 0..1. NOT wired to a body: it has an instant\n"
            + " *  attack, so as a position offset it is a step, and a step is a jerk. */\n"
            + "export const ACCENT: number[] = [\n" + _rows(acc) + "\n];\n\n"
            + "const at = (a: number[], f: number): number =>\n"
            + "  a[Math.max(0, Math.min(a.length - 1, Math.round(f)))] ?? 0;\n\n"
            + "/** Mouth openness at a global frame. Clamped at both ends. */\n"
            + "export const openAt = (f: number): number => at(MOUTH, f);\n\n"
            + "/** Lip spread at a global frame. */\n"
            + "export const spreadAt = (f: number): number => at(SPREAD, f);\n\n"
            + "/** Onset strength at a global frame. */\n"
            + "export const accentAt = (f: number): number => at(ACCENT, f);\n")


def self_test():
    ok = True
    sr = 44100

    def tone(dur, amp, freq=180.0):
        return array.array("h", [int(amp * 32767 * math.sin(2 * math.pi * freq * t / sr))
                                 for t in range(int(dur * sr))])

    silence = array.array("h", [0] * int(0.5 * sr))
    speechy = tone(0.5, 0.7) + silence + tone(0.5, 0.7)
    env = envelope(speechy, sr)

    mid = len(env) // 2
    checks = [
        ("opens on voice", max(env[:12]) > 0.25),
        ("SHUTS in the gap, not merely quiets", min(env[mid - 3:mid + 4]) < 0.06),
        ("re-opens on the second phrase", max(env[-12:]) > 0.25),
        ("never exceeds 1", max(env) <= 1.0),
        ("one value per video frame", abs(len(env) - round(1.5 * FPS)) <= 1),
    ]

    # Pure silence must never move a mouth.
    quiet = envelope(array.array("h", [0] * sr), sr)
    checks.append(("a silent track leaves the mouth shut", max(quiet) == 0.0))

    # RED on purpose: symmetric smoothing is the chewing defect this replaces, so
    # prove the asymmetry is real and not decorative.
    checks.append(("closes slower than it opens (not a chewing sine)", ATTACK > RELEASE * 2))

    # Accents must fire on ATTACKS and stay quiet through a held sound, which is
    # the whole difference between a body that speaks and a body that jitters.
    held = raw_envelope(tone(1.2, 0.7), sr)
    ha = accents(held)
    onset_peak = max(ha[:8])
    sustain_peak = max(ha[15:])
    checks += [
        ("accents fire on the attack", onset_peak > 0.3),
        ("accents go quiet through a HELD sound", sustain_peak < onset_peak * 0.5),
        ("silence produces no accent", max(accents(raw_envelope(array.array("h", [0] * sr), sr))) == 0.0),
    ]

    # The mouth must be SHAPES HELD, not an analog level redrawn every frame.
    runs, i = [], 0
    while i < len(env):
        j = i
        while j < len(env) and env[j] == env[i]:
            j += 1
        runs.append(j - i); i = j
    checks += [
        ("uses a small set of mouth shapes", len(set(env)) <= len(LEVELS)),
        ("holds each shape for 2+ frames (a sound covers 2-6)", min(runs) >= 2),
    ]

    # And the second axis must actually vary with CONTENT, not with loudness.
    bright = tone(0.6, 0.6, 2600.0)
    dark = tone(0.6, 0.6, 220.0)
    sb, sd = spread(bright, sr), spread(dark, sr)
    mid = len(sb) // 2
    checks.append(("lip spread separates a bright sound from a dark one at EQUAL volume",
                   sum(sb[2:mid]) / max(1, len(sb[2:mid])) > sum(sd[2:mid]) / max(1, len(sd[2:mid]))))

    for name, good in checks:
        print(f"  {'ok  ' if good else 'FAIL'} {name}")
        ok &= bool(good)

    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int)
    ap.add_argument("--wav", default=os.path.join(OUT, "vo.wav"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.case is None:
        print("vo_envelope: --case is required", file=sys.stderr)
        return 2

    name = f"case{a.case:04d}_mouth.ts"
    dest = os.path.join(SRC, name)
    try:
        samples, sr = read_wav(a.wav)
    except Exception as e:
        print(f"vo_envelope: cannot read {a.wav}: {e}", file=sys.stderr)
        return 1
    env = envelope(samples, sr)
    if not env:
        print("vo_envelope: empty envelope, the VO has no audio", file=sys.stderr)
        return 1
    text = render_ts(env, a.case, name, spread(samples, sr),
                     raw_envelope(samples, sr))

    if a.check:
        cur = open(dest).read() if os.path.exists(dest) else ""
        if cur == text:
            print(f"vo_envelope: {name} is current ({len(env)} frames)")
            return 0
        print(f"vo_envelope: FAIL {name} is STALE. Run: python3 scripts/vo_envelope.py "
              f"--case {a.case}", file=sys.stderr)
        return 1

    open(dest, "w").write(text)
    moving = sum(1 for v in env if v >= 0.06)
    print(f"vo_envelope: wrote {dest}")
    print(f"  {len(env)} frames ({len(env)/FPS:.2f}s), mouth open on {moving} "
          f"({100*moving/len(env):.0f}%), peak {max(env):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
