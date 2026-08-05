#!/usr/bin/env python3
"""build_music — the score. Original, synthesized, seeded per episode.

    python3 scripts/build_music.py --seed 2026-08-03 --seconds 53.3 \
        --mood hold --turn 26.0 --out out/dispatch/music.wav
    python3 scripts/build_music.py --moods
    python3 scripts/build_music.py --self-test

## Why this is synthesized and not fetched

`scripts/get_music.py` is the ported Alaska fetcher: search a royalty-free host,
download, convert, credit. Its backup path reads a music-sources pool
config that was never ported, and it hands the result to an `audio_v3` module
referenced nowhere in this repo. Neither is written here as a path, because
`refs_check` is right that a named path in prose is a promise a run will try to
keep. Its own docstring says "exit !=0 on any failure so
the caller can fall back to the engine's synth bed", and that synth bed was
never ported either. So the fetcher is not a working option today, and four
things say it should not become the primary one:

1. **A daily run cannot depend on a network.** A 404, a hotlink block or a host
   going down takes the audio out of an episode that has to ship anyway. This
   show's whole business case is that it ships every day forever.
2. **Attribution is a daily, permanent obligation.** A CC-BY track needs its
   credit in the post copy every time, and one mis-credited track is exactly the
   savage-and-wrong class of risk the fact-check gate exists to prevent. The
   show does not get to be careless about a licence just because it is music.
3. **A pool repeats and the ledger forbids repeating.** Seeded synthesis gives
   every episode its own score for free; a pool of fetched tracks cycles.
4. **The show has a specific sound and no library track will have it.** See below.

## The brief, from the show's own thesis

CLAUDE.md: "THE PAINT IS THE ANTAGONIST. Not the fee or the number, but the calm
competent surface that presents an atrocity as a normal Tuesday."

So the score IS the paint. It is pleasant. It is competent. It is the music you
would hear on hold while being told your call is important, playing calmly over
a man being counted nine times for one eviction. It never comments, never
stings, never tells you a thing is bad. Refusing to editorialise is the same
rule the Institution's visuals hold, one channel over.

And then it SOURS. At `--turn` the harmony goes wrong while the tempo, the
instrument and the politeness stay exactly the same: the major thirds go minor,
the resolution stops arriving. Nothing announces it. That is the thesis in
audio, and it is the difference between a bed and a score.

## Moods

  hold    the house sound. Major 7ths, gentle arpeggio, elevator-pleasant.
  dread   low, slow, unresolved. For an episode with no comic surface to hide
          behind.
  march   the same politeness with an institutional pulse under it.

Everything is deterministic in `--seed`, so a re-run of an episode is
bit-identical and two episodes never get the same performance.
"""
import argparse, array, math, os, random, sys, wave

SR = 44100
A4 = 440.0

# ---------------------------------------------------------------------------
# THE HARMONY.
#
# Chord shapes as semitone offsets from a root. The BEFORE and AFTER tables use
# the SAME root motion on purpose: the bass line does not change at the turn, so
# nothing announces that anything happened. Only the quality of each chord goes
# wrong under it, which is what "painted normal" sounds like.
# ---------------------------------------------------------------------------
SHAPES = {
    "maj7":  [0, 4, 7, 11],
    "m7":    [0, 3, 7, 10],
    "7sus4": [0, 5, 7, 10],
    "mMaj7": [0, 3, 7, 11],     # pleasant voicing, minor third. The sour twin.
    "m7b5":  [0, 3, 6, 10],     # a V that will not resolve.
    "min9":  [0, 3, 7, 10, 14],
}

# roots as MIDI note numbers. 48 = C3.
MOODS = {
    "hold": {
        "bpm": 76, "bars_per_chord": 1,
        # ROOTS IDENTICAL IN BOTH TABLES. The module docstring and the comment
        # above SHAPES both promise "the bass line does not change at the turn,
        # so nothing announces that anything happened", and then chord 2 moved
        # 45 -> 44, which is a bass note walking down a semitone at exactly the
        # moment the change is supposed to be unannounced. Only the QUALITY
        # changes now, which is what the paragraph always claimed.
        "before": [(48, "maj7"), (45, "m7"), (41, "maj7"), (43, "7sus4")],
        "after":  [(48, "mMaj7"), (45, "m7b5"), (41, "m7"), (43, "m7b5")],
        "arp": [0, 2, 1, 3, 2, 1],  # indices into the chord, a polite figure
        "pulse": False,
        "blurb": "elevator-pleasant, and it sours at the turn without changing tempo",
    },
    "dread": {
        "bpm": 58, "bars_per_chord": 2,
        "before": [(41, "min9"), (39, "m7")],
        "after":  [(41, "m7b5"), (39, "m7b5")],
        "arp": [0, 1, 0, 2],
        "pulse": False,
        "blurb": "low, slow, unresolved. no comic surface to hide behind",
    },
    "march": {
        "bpm": 92, "bars_per_chord": 1,
        "before": [(48, "maj7"), (48, "maj7"), (46, "m7"), (43, "7sus4")],
        "after":  [(48, "mMaj7"), (48, "mMaj7"), (46, "m7b5"), (43, "m7b5")],
        "arp": [0, 1, 2, 1],
        "pulse": True,
        "blurb": "the same politeness with an institutional pulse under it",
    },
}


def hz(midi):
    return A4 * (2.0 ** ((midi - 69) / 12.0))


def _add(buf, at, samples, gain):
    n = len(buf)
    for i, s in enumerate(samples):
        j = at + i
        if j >= n:
            break
        buf[j] += s * gain


def pluck(f, dur_s, rng, bright=1.0):
    """A bell / electric-piano tone. Additive with per-partial decay.

    Higher partials die first, which is what makes a struck tone sound struck
    rather than like a filtered sawtooth held at a fixed brightness.
    """
    n = int(dur_s * SR)
    out = [0.0] * n
    parts = [(1, 1.0, 1.0), (2, 0.42, 1.9), (3, 0.20, 2.8), (4.01, 0.11, 4.2),
             (5.98, 0.05, 6.0)]
    ph = rng.uniform(0, 6.283)
    for mult, amp, decay in parts:
        w = 2 * math.pi * f * mult / SR
        a = amp * (bright ** (mult - 1))
        k = decay / max(0.05, dur_s)
        for i in range(n):
            out[i] += a * math.exp(-k * i / SR) * math.sin(w * i + ph * mult)
    # a 4ms attack, or the onset clicks
    at = int(0.004 * SR)
    for i in range(min(at, n)):
        out[i] *= i / at
    return out


def pad(f, dur_s, rng):
    """A soft sustained voice. Slow attack, slow release, gentle chorus.

    The two detunes are what stop four sine waves sounding like a test tone; a
    pad with no beating between partials reads as a hold signal, not as music.
    """
    n = int(dur_s * SR)
    out = [0.0] * n
    dets = [1.0, 1.0 + rng.uniform(0.0015, 0.0035), 1.0 - rng.uniform(0.0015, 0.0035)]
    for d in dets:
        w = 2 * math.pi * f * d / SR
        ph = rng.uniform(0, 6.283)
        for i in range(n):
            out[i] += math.sin(w * i + ph) + 0.22 * math.sin(2 * w * i + ph)
    atk, rel = int(0.35 * SR), int(0.55 * SR)
    for i in range(n):
        e = 1.0
        if i < atk:
            e = i / atk
        if i > n - rel:
            e = min(e, (n - i) / rel)
        out[i] *= e / len(dets) * 0.5
    return out


def render(seed, seconds, mood="hold", turn=None):
    """-> (L, R) floats. The whole score, deterministic in `seed`."""
    if mood not in MOODS:
        raise ValueError(f"unknown mood {mood!r}; try {', '.join(MOODS)}")
    m = MOODS[mood]
    rng = random.Random(f"{seed}|{mood}")
    n = int(seconds * SR)
    L = [0.0] * n
    R = [0.0] * n

    beat = 60.0 / m["bpm"]
    bar = 4 * beat
    chord_s = bar * m["bars_per_chord"]
    turn_s = seconds if turn is None else float(turn)

    # THE TURN LANDS WHERE IT IS ASKED TO.
    #
    # This loop steps by whole chords, and the sour table was selected with
    # `t >= turn_s`, so the turn could only ever happen ON a chord boundary and
    # rounded UP to the next one. Case 0003 asks for 26.047s, the frame VERIFIED
    # comes down on a copy, and got 28.421s: 2.4 seconds late, well past the shot
    # it was written for. `dread` was up to 7.1s late.
    #
    # The self-test did not catch it because the fixture put the turn exactly on
    # a boundary, which is the only value where the bug is invisible. Same
    # lesson as the control row two commits ago: a test that only exercises the
    # lucky input is not a test. The fixture below now uses an off-grid turn.
    #
    # Fix: cut the chord short at the turn. The bar in progress ends early, the
    # sour table starts exactly on the requested second, and because the root
    # does not move (see the tables) the seam is inaudible as an EVENT while the
    # harmony underneath it has changed.
    t = 0.0
    idx = 0
    while t < seconds:
        # THE TURN IS A LOOKUP, NOT A TRANSITION. Nothing crossfades, nothing
        # swells; the next chord is simply the sour one. The bass root does not
        # move, so the change has no announcement attached to it.
        table = m["after"] if t >= turn_s - 1e-9 else m["before"]
        root, shape = table[idx % len(table)]
        tones = [root + s for s in SHAPES[shape]]
        at = int(t * SR)
        # If the turn falls inside this chord, END THE CHORD THERE.
        span = chord_s
        if t < turn_s < t + chord_s:
            span = turn_s - t

        # PAD: the chord, held for the whole bar, mid register.
        for k, note in enumerate(tones):
            # tiny per-note timing and level jitter, seeded. A grid with no
            # jitter is a MIDI file, not a performance.
            j = int(rng.uniform(0, 0.012) * SR)
            v = 0.30 * rng.uniform(0.88, 1.0)
            voice = pad(hz(note + 12), span * 0.98, rng)
            # spread the voicing across the image, low notes centred
            panL = 0.5 + 0.16 * math.sin(k * 1.7)
            _add(L, at + j, voice, v * panL)
            _add(R, at + j, voice, v * (1.0 - panL))

        # SUB: the root, two octaves down, quiet. It is the only thing that does
        # not change at the turn, which is why the turn reads as the ground
        # staying put while everything above it goes wrong.
        # ONE render, BOTH channels. This was two separate pad() calls, each
        # drawing its own detune and phase from the rng, so the sub was
        # decorrelated across the image: it beat against itself and partially
        # cancelled on a mono fold-down, which is how most phones play this.
        # Twice the CPU for a worse bass. A centred sub is one signal.
        sub = pad(hz(root - 12), span * 0.98, rng)
        _add(L, at, sub, 0.20)
        _add(R, at, sub, 0.20)

        # ARP: the polite figure. One note per beat-ish, bell tone, high.
        step = span / len(m["arp"])
        for s_i, ci in enumerate(m["arp"]):
            note = tones[ci % len(tones)] + 24
            a = at + int((s_i * step + rng.uniform(0, 0.010)) * SR)
            v = 0.16 * rng.uniform(0.7, 1.0)
            tone = pluck(hz(note), min(step * 1.6, 1.4), rng, bright=0.92)
            pan = 0.5 + 0.22 * math.sin(s_i * 2.1)
            _add(L, a, tone, v * pan)
            _add(R, a, tone, v * (1.0 - pan))

        if m["pulse"]:
            for b in range(max(1, int(span / beat))):
                a = at + int(b * beat * SR)
                _add(L, a, pluck(hz(root - 24), 0.16, rng, bright=0.4), 0.22)
                _add(R, a, pluck(hz(root - 24), 0.16, rng, bright=0.4), 0.22)

        t += span
        idx += 1

    # Fade the ends. A bed that starts at full level on frame one announces
    # itself, and the one thing this score must never do is announce itself.
    fi, fo = int(1.6 * SR), int(2.2 * SR)
    for i in range(min(fi, n)):
        k = i / fi
        L[i] *= k; R[i] *= k
    for i in range(min(fo, n)):
        k = i / fo
        L[n - 1 - i] *= k; R[n - 1 - i] *= k

    peak = max(max((abs(x) for x in L), default=0), max((abs(x) for x in R), default=0)) or 1.0
    k = 0.72 / peak
    return [x * k for x in L], [x * k for x in R]


def write_wav(path, L, R):
    a = array.array("h", [0]) * (len(L) * 2)
    for i in range(len(L)):
        a[2 * i] = max(-32768, min(32767, int(L[i] * 32767)))
        a[2 * i + 1] = max(-32768, min(32767, int(R[i] * 32767)))
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(a.tobytes())


def self_test():
    ok = True
    import tempfile
    d = tempfile.mkdtemp()

    a = render("2026-08-03", 8.0, "hold", turn=4.0)
    b = render("2026-08-03", 8.0, "hold", turn=4.0)
    same = a[0] == b[0] and a[1] == b[1]
    print(f"  {'ok  ' if same else 'FAIL'} the same seed renders the same score "
          f"(a re-run of an episode is bit-identical)")
    ok &= same

    c = render("2026-08-04", 8.0, "hold", turn=4.0)
    diff = c[0] != a[0]
    print(f"  {'ok  ' if diff else 'FAIL'} a different seed renders a different score "
          f"(the ledger forbids two episodes alike)")
    ok &= diff

    # THE TURN HAS TO BE AUDIBLE, and the first cut of this could not prove it.
    # It compared a window at 6.4s against one at 18.4s and asked whether the
    # spectrum moved. It moves either way: the progression is four chords long,
    # so those two windows sit on DIFFERENT CHORDS and would differ in a score
    # with no turn at all. The control row below caught it immediately, which is
    # the entire reason a self-test carries one.
    #
    # So: sample the SAME SLOT of the progression on both sides of the turn, and
    # make the assertion musical rather than statistical. Chord 0 of `hold` is C
    # major 7 before the turn and C minor-major 7 after it. The only difference
    # is E natural becoming E flat. Measure exactly those two pitches and require
    # the winner to CHANGE. Nothing but the third moving can do that.
    EB4, E4 = 311.13, 329.63
    cyc = 4 * (60.0 / MOODS["hold"]["bpm"]) * 4        # four chords, one bar each

    def energy(sig, f, t0, t1):
        w = 2 * math.pi * f / SR
        a, b = int(t0 * SR), int(t1 * SR)
        re = sum(sig[i] * math.cos(w * i) for i in range(a, b))
        im = sum(sig[i] * math.sin(w * i) for i in range(a, b))
        return (re * re + im * im) ** 0.5 / max(1, b - a)

    def thirds(sig, t0):
        return energy(sig, EB4, t0, t0 + 2.0), energy(sig, E4, t0, t0 + 2.0)

    # AN OFF-GRID TURN, on purpose. The first version of this fixture used
    # turn=cyc, exactly on a chord boundary, which is the one value where the
    # quantization bug is invisible: the turn rounded up to the next boundary
    # and the next boundary WAS the requested time. A real turn (26.047s in case
    # 0003) landed 2.4s late and this test said it was fine.
    off = cyc + 1.317
    turned = render("2026-08-03", 2.5 * cyc + 6, "hold", turn=off)[0]
    b_eb, b_e = thirds(turned, 0.4)
    a_eb, a_e = thirds(turned, off + 0.15)
    flipped = b_e > b_eb and a_eb > a_e
    print(f"  {'ok  ' if flipped else 'FAIL'} the turn actually changes the harmony "
          f"(E natural {b_e/max(b_eb,1e-9):.1f}x before, E flat {a_eb/max(a_e,1e-9):.1f}x after)")
    ok &= flipped

    # And a score with NO turn must keep the major third in both windows, or the
    # row above is measuring the arpeggio moving rather than the harmony.
    flat = render("2026-08-03", 2.5 * cyc + 6, "hold", turn=None)[0]
    f_eb, f_e = thirds(flat, 0.4)
    g_eb, g_e = thirds(flat, off + 0.15)
    still = f_e > f_eb and g_e > g_eb
    print(f"  {'ok  ' if still else 'FAIL'} a score with no turn keeps its major third "
          f"in the same slot ({f_e/max(f_eb,1e-9):.1f}x, {g_e/max(g_eb,1e-9):.1f}x)")
    ok &= still

    # THE ROW THE QUANTIZATION BUG NEEDED. Not "does the harmony change" but
    # "does it change WHEN ASKED". Sweep turns that deliberately miss the grid.
    late = []
    for want in (cyc + 0.4, cyc + 1.317, cyc + 2.9):
        sig = render("s", 2.5 * cyc + 6, "hold", turn=want)[0]
        # the sour third must be winning 0.15s after the requested second, and
        # the sweet third must still be winning 0.15s before it
        p_eb, p_e = thirds(sig, want - 2.15)
        q_eb, q_e = thirds(sig, want + 0.15)
        if not (p_e > p_eb and q_eb > q_e):
            late.append(want)
    print(f"  {'ok  ' if not late else 'FAIL'} the turn lands WHEN ASKED, not at the "
          f"next chord boundary"
          + ("" if not late else f"   <- still late for turn(s) {late}"))
    ok &= not late

    # ROOTS MUST NOT MOVE. The docstring promises the bass does not change at
    # the turn, and for two of three moods it did.
    moved = {k: [r for r, _ in v["before"]] for k, v in MOODS.items()
             if [r for r, _ in v["before"]] != [r for r, _ in v["after"]]}
    print(f"  {'ok  ' if not moved else 'FAIL'} the bass root does not move at the turn "
          f"(the change is unannounced)"
          + ("" if not moved else f"   <- moves in {sorted(moved)}"))
    ok &= not moved

    # A CENTRED SUB MUST SURVIVE MONO. Two pad() calls for L and R drew
    # different phases and partially cancelled when folded down.
    Lc, Rc = render("s", 6.0, "hold", turn=None)
    def _r(x): return (sum(v * v for v in x) / len(x)) ** 0.5
    mono = _r([(Lc[i] + Rc[i]) * 0.5 for i in range(len(Lc))])
    keep = mono / max(1e-9, (_r(Lc) + _r(Rc)) / 2)
    print(f"  {'ok  ' if keep >= 0.97 else 'FAIL'} the mix survives a mono fold-down "
          f"({keep*100:.0f}% of the level kept)")
    ok &= keep >= 0.97

    for mood in MOODS:
        L, R = render("s", 6.0, mood, turn=3.0)
        peak = max(max(abs(x) for x in L), max(abs(x) for x in R))
        good = 0.3 < peak <= 0.75 and len(L) == int(6.0 * SR)
        print(f"  {'ok  ' if good else 'FAIL'} mood '{mood}' renders at a sane level "
              f"and length (peak {peak:.2f}, {len(L)/SR:.1f}s)")
        ok &= good

    write_wav(f"{d}/x.wav", *a)
    print("\nself-test: " + ("deterministic, varied, and the turn is audible"
                             if ok else "THE SCORE GENERATOR IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="default", help="episode date. same seed, same score")
    ap.add_argument("--seconds", type=float, default=54.0)
    ap.add_argument("--mood", default="hold")
    ap.add_argument("--turn", type=float, default=None,
                    help="second the harmony sours. usually the episode's turn.")
    ap.add_argument("--out", default="out/dispatch/music.wav")
    ap.add_argument("--moods", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.moods:
        for k, v in MOODS.items():
            print(f"  {k:<7} {v['bpm']:>3} bpm   {v['blurb']}")
        return 0
    L, R = render(a.seed, a.seconds, a.mood, a.turn)
    write_wav(a.out, L, R)
    print(f"build_music: '{a.mood}' at {MOODS[a.mood]['bpm']} bpm, {a.seconds:.1f}s, "
          f"seed {a.seed}" + (f", sours at {a.turn:.1f}s" if a.turn else ", no turn")
          + f"\n             -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
