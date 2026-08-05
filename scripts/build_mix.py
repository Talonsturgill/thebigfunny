#!/usr/bin/env python3
"""build_mix — the step that was never built, so the show ships voices on silence.

    python3 scripts/build_mix.py                     # cues + vo from out/dispatch/
    python3 scripts/build_mix.py --vo A --cues B --out C
    python3 scripts/build_mix.py --self-test

WHY THIS EXISTS (2026-08-05, found by grepping for a caller and finding none):

`scripts/sfx_bank.py` is a real piece of game-audio middleware. Seventeen effect
kinds, six sibling takes each, a shuffle-bag that plays every take before any
repeats, no-repeat-last-2 across reshuffles, an episode-seeded deal so a re-run
is bit-identical, a curated real-recording tier that supersedes the synth takes,
and a self-heal that rebuilds the bank on a miss. It was written on 2026-07-21
against the owner note "ours is boring and reusing the same sfx".

**`resolve()` has never been called by anything.** `mux_and_verify.sh` takes one
video and one audio file, and that audio file is the VO. So every episode this
show has shipped is dialogue over digital silence: cards weighing as much as a
door slam onto a floor, an odometer counting to nine, a chute running, three
fasteners dropping off a wall, a cover plate falling. All of it silent.

This is the same failure as the faces (`face_size.py`): capability built,
capability never reached, and the viewer pays for a thing that already exists.

## Why this does the arithmetic itself instead of calling ffmpeg

The Remotion-vendored ffmpeg is built `--disable-filters`, which this repo has
already been burned by twice (see the header of `mux_and_verify.sh`). There is
no `amix`, no `adelay`, no `volume`. Rather than depend on a system ffmpeg that
is not present in every environment this runs in, the mix is summed in Python
from `wave` frames. It is a few hundred kilosamples of integer addition and it
takes under a second.

## What a mix is, beyond adding files together

DUCKING is the whole job. Two audio files added together is not a mix, it is a
collision, and the thing that loses a collision with a 2 second door slam is the
line the episode is about. Every cue is ducked by the VO envelope, so an effect
under dialogue sits well below it and an effect in a gap plays at full weight.
That is also why the cue sheet carries `db` per cue rather than one global
level: a card landing and a wheel tick are not the same size of event.
"""
import argparse, array, json, math, os, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

SR = 44100
# How far a cue is pushed down where the voice is loudest. -11 dB is roughly the
# broadcast convention for music under speech, and an effect is more transient
# than music, so it survives the duck better than a bed would.
DUCK_DB = -11.0
# THE BED DUCKS HARDER THAN THE EFFECTS. An effect is transient and survives a
# deep duck; a bed is continuous, so under speech it is the thing competing with
# every syllable. Broadcast practice is music several dB further down than
# spot effects, and the show's brief makes that a creative point too: the score
# is the polite surface, and a polite surface never talks over anybody.
MUSIC_DUCK_DB = -8.0
# The envelope is smoothed over this window so the duck does not chatter on
# every syllable, and released slower than it attacks so it does not pump.
ENV_ATTACK_S = 0.020
ENV_RELEASE_S = 0.260
# Everything lands under this so the encode has headroom.
CEILING = 0.89


def _db(x):
    return 10.0 ** (x / 20.0)


def read_wav(path):
    """-> (list_of_float_L, list_of_float_R). Mono is duplicated, not widened."""
    with wave.open(path, "rb") as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        if sw != 2:
            raise ValueError(f"{path}: {sw*8}-bit, this mixer reads 16-bit PCM only")
        if sr != SR:
            raise ValueError(f"{path}: {sr}Hz, the bank and the VO are both {SR}Hz. "
                             "Resampling belongs in the tool that WRITES the file, "
                             "not silently here where nobody would see it happen.")
        a = array.array("h")
        a.frombytes(w.readframes(n))
    if ch == 1:
        f = [s / 32768.0 for s in a]
        return f, list(f)
    return [a[i] / 32768.0 for i in range(0, len(a), 2)], \
           [a[i + 1] / 32768.0 for i in range(0, len(a), 2)]


def write_wav(path, L, R):
    a = array.array("h", [0]) * (len(L) * 2)
    for i in range(len(L)):
        a[2 * i] = max(-32768, min(32767, int(L[i] * 32767)))
        a[2 * i + 1] = max(-32768, min(32767, int(R[i] * 32767)))
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(a.tobytes())


def envelope(mono):
    """A smoothed 0..1 loudness envelope of the voice, attack-fast release-slow.

    One-pole per sample. The release is 13x the attack so the duck opens back up
    between sentences without pumping inside one, which is what a chattering
    duck sounds like and why the first cut of this had a tremolo on every
    effect that overlapped a line.
    """
    ka = 1.0 - math.exp(-1.0 / (ENV_ATTACK_S * SR))
    kr = 1.0 - math.exp(-1.0 / (ENV_RELEASE_S * SR))
    env = [0.0] * len(mono)
    e = 0.0
    for i, s in enumerate(mono):
        x = abs(s)
        e += (x - e) * (ka if x > e else kr)
        env[i] = e
    peak = max(env) or 1.0
    return [v / peak for v in env]


def build(vo_path, cues_path, out_path, quiet=False):
    from sfx_bank import resolve

    spec = json.load(open(cues_path))
    seed = str(spec.get("episode_seed", "default"))
    cues = spec.get("cues", [])

    voL, voR = read_wav(vo_path)
    n = len(voL)
    mono = [(voL[i] + voR[i]) * 0.5 for i in range(n)]
    env = envelope(mono)

    L = list(voL)
    R = list(voR)

    # THE SCORE, first, so everything else sits on top of it.
    #
    # Generated rather than fetched, and generated HERE rather than read off
    # disk, so a run cannot half-do it: there is no path where the cue sheet
    # declares a bed and the mix quietly ships without one. See build_music.py's
    # header for why this show synthesizes its own score instead of downloading
    # somebody else's.
    music = spec.get("music")
    if music:
        import build_music
        mL, mR = build_music.render(
            seed=str(music.get("seed", seed)),
            seconds=n / SR,
            mood=music.get("mood", "hold"),
            turn=music.get("turn"))
        mg = _db(float(music.get("db", -26.0)))
        for i in range(min(n, len(mL))):
            d = _db(MUSIC_DUCK_DB * env[i])
            L[i] += mL[i] * mg * d
            R[i] += mR[i] * mg * d
        if not quiet:
            t = music.get("turn")
            print(f"  score    {music.get('mood','hold'):<8} "
                  f"{float(music.get('db',-26.0)):+.0f} dB, seed {music.get('seed', seed)}"
                  + (f", sours at {float(t):.1f}s" if t is not None else ", no turn"))

    placed, report = 0, []
    for c in cues:
        kind = c["kind"]
        path = resolve(kind, episode_seed=seed)
        sL, sR = read_wav(path)
        g = _db(float(c.get("db", -16.0)))
        at = int(round(float(c["t"]) * SR))
        end = min(n, at + len(sL))
        if at >= n:
            report.append((c["t"], kind, os.path.basename(path), "PAST THE END, dropped"))
            continue
        for i in range(max(0, at), end):
            # THE DUCK. Under a loud line an effect sits DUCK_DB down; in a gap
            # it plays at its authored level.
            d = _db(DUCK_DB * env[i])
            j = i - at
            L[i] += sL[j] * g * d
            R[i] += sR[j] * g * d
        placed += 1
        report.append((c["t"], kind, os.path.basename(path),
                       f"{c.get('db', -16.0):+.0f} dB, {len(sL)/SR:.2f}s"))

    # SOFT LIMIT, not a hard clip. A hard clip on a card slam is audible as a
    # click, which is worse than the slam being 1 dB quieter.
    peak = max(max(abs(x) for x in L), max(abs(x) for x in R)) or 1.0
    if peak > CEILING:
        k = CEILING / peak
        L = [x * k for x in L]
        R = [x * k for x in R]

    write_wav(out_path, L, R)
    if not quiet:
        for t, kind, take, note in report:
            print(f"  {t:6.2f}s  {kind:<8} {take:<16} {note}")
        print(f"\nbuild_mix: {placed}/{len(cues)} cues mixed into {out_path}")
        print(f"           peak {20*math.log10(peak):+.1f} dBFS before limiting, "
              f"ducked {DUCK_DB:+.0f} dB under the voice")
    return placed, len(cues)


def self_test():
    """Both directions: it must MIX, and it must not let a cue eat the voice."""
    import tempfile, random
    ok = True
    d = tempfile.mkdtemp()
    # A fake VO: a loud tone for 1s, silence for 1s.
    volL = [0.6 * math.sin(2 * math.pi * 220 * i / SR) if i < SR else 0.0
            for i in range(2 * SR)]
    write_wav(f"{d}/vo.wav", volL, volL)
    # A fake effect: full-scale noise, 0.2s.
    random.seed(7)
    fx = [random.uniform(-0.9, 0.9) for _ in range(SR // 5)]
    os.makedirs(f"{d}/bank", exist_ok=True)
    write_wav(f"{d}/bank/tick_v1.wav", fx, fx)

    import sfx_bank
    real_takes = sfx_bank.takes
    sfx_bank.takes = lambda kind: [f"{d}/bank/tick_v1.wav"]

    def mix_at(t):
        json.dump({"episode_seed": "t", "cues": [{"t": t, "kind": "tick", "db": 0}]},
                  open(f"{d}/c.json", "w"))
        build(f"{d}/vo.wav", f"{d}/c.json", f"{d}/m.wav", quiet=True)
        return read_wav(f"{d}/m.wav")[0]

    try:
        loud = mix_at(0.4)      # cue UNDER the voice
        quiet = mix_at(1.4)     # cue in the GAP
        base = read_wav(f"{d}/vo.wav")[0]

        # 1. it actually mixes something in
        moved = any(abs(loud[i] - base[i]) > 1e-4 for i in range(int(0.4*SR), int(0.5*SR)))
        print(f"  {'ok  ' if moved else 'FAIL'} the effect actually reaches the mix"
              + ("" if moved else "   <- the output is byte-identical to the VO"))
        ok &= moved

        # 2. the duck works: the same cue is LOUDER in the gap than under the line
        def energy(sig, a, b):
            return sum(x * x for x in sig[int(a*SR):int(b*SR)]) ** 0.5
        under = energy(loud, 0.4, 0.6) - energy(base, 0.4, 0.6)
        gap = energy(quiet, 1.4, 1.6)
        ducked = gap > under * 1.5
        print(f"  {'ok  ' if ducked else 'FAIL'} a cue under dialogue is ducked below "
              f"the same cue in a gap"
              + ("" if ducked else "   <- the mix is an addition, not a mix"))
        ok &= ducked

        # 3. nothing clips
        clipped = max(abs(x) for x in quiet) <= CEILING + 1e-6
        print(f"  {'ok  ' if clipped else 'FAIL'} the limiter holds the ceiling "
              f"(peak {max(abs(x) for x in quiet):.3f} <= {CEILING})")
        ok &= clipped

        # 4. a cue past the end of the VO is dropped, not crashed on
        try:
            mix_at(99.0)
            print("  ok   a cue past the end of the VO is dropped, not crashed on")
        except Exception as e:
            print(f"  FAIL a cue past the end of the VO is dropped, not crashed on: {e}")
            ok = False
    finally:
        sfx_bank.takes = real_takes

    print("\nself-test: " + ("mixes, ducks and limits, as designed"
                             if ok else "THE MIXER IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", default=os.path.join(REPO, "out/dispatch/vo.wav"))
    ap.add_argument("--cues", default=os.path.join(REPO, "out/dispatch/sfx_cues.json"))
    ap.add_argument("--out", default=os.path.join(REPO, "out/dispatch/mix.wav"))
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    for p in (a.vo, a.cues):
        if not os.path.exists(p):
            print(f"build_mix: {p} is not on disk")
            return 1
    placed, total = build(a.vo, a.cues, a.out)
    return 0 if placed == total else 1


if __name__ == "__main__":
    sys.exit(main())
