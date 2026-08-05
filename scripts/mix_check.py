#!/usr/bin/env python3
"""mix_check — did the episode make any sound other than talking?

    python3 scripts/mix_check.py                       # out/dispatch/{vo,mix}.wav
    python3 scripts/mix_check.py --vo A --mix B --cues C
    python3 scripts/mix_check.py --self-test

WHY THIS EXISTS (2026-08-05):

`scripts/sfx_bank.py` is seventeen effect kinds with six takes each, a shuffle
bag, no-repeat-last-2 and a curated real-recording tier. `resolve()` had never
been called by anything. `mux_and_verify.sh` muxes ONE audio file and that file
is the VO, so every episode this show has shipped is dialogue over digital
silence: a card the size of a door landing on a floor, an odometer counting to
nine, a chute running, a cover plate falling off a wall, all silent.

`build_mix.py` builds the mix. This is the gate that stops the next run quietly
skipping it, which is exactly how the last one went unnoticed for three
episodes. It reads the AUDIO, not the cue sheet, for the same reason
`motion_check` reads pixels: a cue sheet that lists thirty cues proves nothing
about a file nobody mixed.

## The rows

  MIXED       the delivered audio differs from the VO. This is the one that
              catches the failure that prompted the gate.
  VOICE WINS  the effects have not buried the line. A mix is not "both files at
              once"; if the added energy rivals the voice, the joke is gone and
              the fix is the cue levels, never the gate.
  NO CLIPPING the sum stayed under the ceiling.
  NO DEAD AIR no 12 second stretch of the film with nothing but voice in it.
              Not a beauty standard: a cartoon that goes quiet for a quarter of
              its runtime reads as a slideshow with a podcast over it, which is
              the note this show has already had once, about pictures.
"""
import argparse, array, json, math, os, sys, wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100
# A RATE, not a count. The first cut of this was "12 or more cues" and its own
# self-test caught it: 10 cues across a 20 second fixture is dense sound design
# and the gate called it a token gesture, because 12 was tuned against a 53
# second film and never told what a second was. Threshold arithmetic that only
# works at one duration is a bug the day an episode is 40 seconds.
MIN_CUE_RATE = 0.22          # per second, about 12 across a 53s episode
MIN_CUES_FLOOR = 6
DEAD_AIR_S = 12.0
# An effects layer nobody can hear passes "did you mix anything" and fails the
# viewer. The loudest single effect has to land within this band of the voice's
# own peak: quieter than the top and not more than 24 dB under it.
FX_PEAK_BAND_DB = (-24.0, 3.0)
# How much louder than the voice the effects are allowed to get, measured as
# added RMS against VO RMS over the whole film. Effects are transient and the
# voice is continuous, so a healthy mix sits well under unity here.
VOICE_MARGIN_DB = -6.0
CEILING = 0.90
# When the cue sheet declares a score, the score has to actually be under the
# film. Measured as the share of half-second windows carrying something other
# than voice: spot effects alone leave most of a film empty on this measure, a
# bed fills it. 85% leaves room for a deliberate silence of several seconds.
BED_COVERAGE = 0.85


def read_mono(path):
    with wave.open(path, "rb") as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        if sw != 2 or sr != SR:
            raise ValueError(f"{path}: {sr}Hz/{sw*8}-bit, expected {SR}Hz/16-bit")
        a = array.array("h"); a.frombytes(w.readframes(n))
    if ch == 1:
        return [s / 32768.0 for s in a]
    return [(a[i] + a[i + 1]) / 65536.0 for i in range(0, len(a), 2)]


def rms(sig):
    return (sum(x * x for x in sig) / max(1, len(sig))) ** 0.5


def check(vo, mix, cues):
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d))

    n = min(len(vo), len(mix))
    dur = n / SR
    aligned = abs(len(vo) - len(mix)) < SR * 0.05
    row("the mix is the same length as the VO", aligned,
        f"{len(vo)/SR:.2f}s vs {len(mix)/SR:.2f}s"
        + ("" if aligned else "   <- a mix that drifts from the VO drifts from the CAPTIONS"))

    # THE ONE THAT CATCHES THE FAILURE. Residual = what the mix has that the VO
    # does not. If it is silence, nobody mixed anything.
    resid = [mix[i] - vo[i] for i in range(n)]
    r_rms, v_rms = rms(resid), rms(vo[:n])
    mixed = r_rms > v_rms * 0.004
    row("the episode makes a sound other than talking", mixed,
        f"added layer at {20*math.log10(max(r_rms,1e-9)/max(v_rms,1e-9)):+.1f} dB "
        f"relative to the voice"
        + ("" if mixed else "   <- the delivered audio IS the VO. Nothing was mixed, "
                            "and three episodes shipped that way before anybody checked."))

    quiet_enough = r_rms <= v_rms * (10 ** (VOICE_MARGIN_DB / 20.0))
    row(f"the voice still wins (added layer <= {VOICE_MARGIN_DB:.0f} dB vs VO)", quiet_enough,
        f"{20*math.log10(max(r_rms,1e-9)/max(v_rms,1e-9)):+.1f} dB"
        + ("" if quiet_enough else "   <- the effects are burying the line. Lower the "
                                   "cue levels; never lower this."))

    peak = max(abs(x) for x in mix[:n]) if n else 0.0
    row("nothing clips", peak <= CEILING + 1e-3, f"peak {peak:.3f} (ceiling {CEILING})")

    # AUDIBLE, not merely present. RMS over a whole film is the wrong instrument
    # for a transient layer: thirty short effects across 53 seconds sit 20 dB
    # down on that measure no matter how loud each one is. Peak-to-peak is what
    # says whether anybody will hear the card land.
    r_pk = max((abs(x) for x in resid), default=0.0)
    v_pk = max((abs(x) for x in vo[:n]), default=1e-9)
    fx_db = 20 * math.log10(max(r_pk, 1e-9) / max(v_pk, 1e-9))
    lo, hi = FX_PEAK_BAND_DB
    row(f"the loudest effect is actually audible ({lo:.0f} to {hi:.0f} dB vs the voice)",
        lo <= fx_db <= hi,
        f"loudest effect peaks {fx_db:+.1f} dB against the voice"
        + ("" if lo <= fx_db <= hi else
           "   <- mixed and inaudible passes every other row here and still ships "
           "a silent cartoon" if fx_db < lo else
           "   <- an effect louder than the line it plays under"))

    if cues is None:
        row("the cue sheet was readable", False, "no cue sheet given")
        return rows

    if cues.get("music"):
        # THE ROW THAT NEEDS NO STEM. resid is everything the mix has that the
        # VO does not, so with a bed under the film it is continuous and with
        # spot effects alone it is mostly silence. That difference is the
        # measurement, and it cannot be satisfied by declaring a score in the
        # sheet and never rendering one.
        win = int(0.5 * SR)
        wins = [resid[i:i + win] for i in range(0, n - win, win)]
        floor = max(1e-5, v_rms * 0.0015)
        cov = sum(1 for w in wins if rms(w) > floor) / max(1, len(wins))
        row(f"the score plays under the film ({BED_COVERAGE*100:.0f}% coverage)",
            cov >= BED_COVERAGE,
            f"{cov*100:.0f}% of the film carries something other than voice"
            + ("" if cov >= BED_COVERAGE else
               "   <- the cue sheet declares a score and the mix does not have one"))
    ts = sorted(float(c["t"]) for c in cues.get("cues", []))
    want = max(MIN_CUES_FLOOR, int(round(dur * MIN_CUE_RATE)))
    row(f"the cue sheet is not a token gesture ({want}+ cues at this length)",
        len(ts) >= want, f"{len(ts)} cues over {dur:.1f}s")

    gaps = []
    prev = 0.0
    for t in ts + [dur]:
        if t - prev > DEAD_AIR_S:
            gaps.append((prev, t))
        prev = t
    row(f"no dead air longer than {DEAD_AIR_S:.0f}s", not gaps,
        "clean" if not gaps else
        ", ".join(f"{a:.1f}-{b:.1f}s" for a, b in gaps)
        + "   <- a cartoon that goes quiet for that long is a podcast with pictures")
    return rows


def run(vo_p, mix_p, cues_p):
    for p in (vo_p, mix_p):
        if not os.path.exists(p):
            print(f"  FAIL the audio exists                          {p} is not on disk")
            print("\nmix_check: FAIL. Run scripts/build_mix.py first.")
            return 1
    cues = json.load(open(cues_p)) if os.path.exists(cues_p) else None
    rows = check(read_mono(vo_p), read_mono(mix_p), cues)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<52} {d}")
    ok = all(o for _, o, _ in rows)
    print("\nmix_check: PASS" if ok else
          "\nmix_check: FAIL. The show is shipping voices on silence.")
    return 0 if ok else 1


def self_test():
    import random
    random.seed(3)
    N = SR * 20
    vo = [0.3 * math.sin(2 * math.pi * 200 * i / SR) for i in range(N)]
    quiet_cues = {"cues": [{"t": 1.0, "kind": "tick"}, {"t": 1.4, "kind": "tick"}]}
    full_cues = {"cues": [{"t": float(i), "kind": "tick"} for i in range(0, 20, 2)]}

    cases = [
        ("audio that was never mixed (the shipped failure)",
         "makes a sound other than talking", vo, list(vo), full_cues),
        ("effects that bury the line",
         "the voice still wins",
         vo, [vo[i] + random.uniform(-0.9, 0.9) for i in range(N)], full_cues),
        ("a cue sheet that is a token gesture",
         "token gesture", vo, [vo[i] * 1.02 for i in range(N)], quiet_cues),
        ("a stretch of the film with no sound design at all",
         "dead air", vo, [vo[i] * 1.02 for i in range(N)], quiet_cues),
        ("an effects layer nobody can hear",
         "actually audible",
         vo, [vo[i] + 0.00002 * math.sin(i * 0.7) for i in range(N)], full_cues),
        ("a cue sheet that declares a score the mix does not have",
         "the score plays under the film",
         vo,
         # spot effects only: four short bursts, no bed
         [vo[i] + (0.09 * math.sin(i * 0.31) if (i // (SR * 4)) * SR * 4 <= i
                   < (i // (SR * 4)) * SR * 4 + SR // 5 else 0.0) for i in range(N)],
         dict(full_cues, music={"mood": "hold"})),
    ]
    ok = True
    for name, guard, v, m, c in cases:
        rows = check(v, m, c)
        fired = any(guard in n and not o for n, o, _ in rows)
        print(f"  {'ok  ' if fired else 'FAIL'} catches: {name}"
              + ("" if fired else f"   <- did NOT fire: {guard}"))
        ok &= fired

    good = [vo[i] + (0.09 if abs(i % SR) < 900 else 0.0) * math.sin(2 * math.pi * 900 * i / SR)
            + 0.004 * math.sin(2 * math.pi * 130 * i / SR)          # the bed
            for i in range(N)]
    rows = check(vo, good, dict(full_cues, music={"mood": "hold"}))
    clean = all(o for _, o, _ in rows)
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a real mix (voice plus a quiet "
          f"effects layer on a full cue sheet)")
    if not clean:
        for n, o, d in rows:
            if not o:
                print(f"       (tripped '{n}': {d})")
    ok &= clean
    print("\nself-test: " + ("both directions correct, as designed"
                             if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", default=os.path.join(REPO, "out/dispatch/vo.wav"))
    ap.add_argument("--mix", default=os.path.join(REPO, "out/dispatch/mix.wav"))
    ap.add_argument("--cues", default=os.path.join(REPO, "out/dispatch/sfx_cues.json"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.vo, a.mix, a.cues)


if __name__ == "__main__":
    sys.exit(main())
