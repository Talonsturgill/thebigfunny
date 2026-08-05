#!/usr/bin/env python3
"""face_size — is anybody's face big enough to read on a phone?

    python3 scripts/face_size.py                    # video-engine/src/Case0003.tsx
    python3 scripts/face_size.py --scene <file.tsx>
    python3 scripts/face_size.py --self-test

WHY THIS EXISTS (2026-08-03, found by measuring rather than by watching):

Every cast placement in case 0003 puts a head under 8% of frame height. The
median is 4.7%, which at 1920px is a 90px head, which on a phone held at arm's
length is about SEVEN MILLIMETRES.

That single number explains a pile of things that looked unrelated:

  - the owner calling the cast "a piece of furniture in the screen". At 4.7% a
    character IS a prop. There is no acting to see because there is no face to
    see it on.
  - the beats that landed best being the TYPE beats (the eight-card wall, the
    RESOLVED / INVALID pair). Type is the only thing legible at that scale.
  - both simulated viewers reporting "Ray tiny at top left", "Dee tiny at the
    bottom".

And it means the show is THROWING AWAY the most expensive thing it owns. There
is a seven-emotion eye table with per-emotion lid, brow and brow-tilt values, a
generated face track (34 expression changes in this episode), a `face_check` gate
that verifies them, and eyelines. All of it renders at seven millimetres.

**This show has never once cut to a face.** Largest head in the episode: 5.9%.

## The thresholds

Reference practice for animated comedy on a phone: a reaction shot puts the head
at 25-40% of frame height, and even a wide keeps a speaking head near 10%. These
are conventions, not measured findings from a study, and the code says so.

  SPEAK_MIN 7%   the MEDIAN placement, not every one. A wide is legitimate;
                 an episode of nothing but wides is not.
  REACT_MIN 20%  at least one shot per episode must be a real reaction shot

The second is the one that matters. An episode may legitimately be full of wides
if the conceit calls for it, but if it NEVER gets close, every expression it
generates is decoration nobody sees.
"""
import argparse, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(REPO, "video-engine", "src", "Case0003.tsx")
H = 1920
HEAD_FRAC = 100.0 / 680.0          # Y.crown -> Y.chin over Y.ground, from Figure.tsx
SPEAK_MIN = 7.0
REACT_MIN = 20.0


def measure(src):
    """-> [(from, to, zoom, mult, head_px, pct)] for every Cast placement."""
    m = re.search(r'const CARD_W = (\d+)', src)
    card_w = float(m.group(1)) if m else 620.0
    # CAST_TO_CARD is DEFINED in lib/countroom.tsx and only IMPORTED by a scene,
    # so read it from where it lives. The first cut searched the scene text and
    # matched a later unrelated `= 0.72`, which produced head sizes of 5000% and
    # a bar chart 30KB wide. A number that absurd is a parse bug, not a finding.
    c2c = 0.72
    lib = os.path.join(REPO, "video-engine", "src", "lib", "countroom.tsx")
    if os.path.exists(lib):
        m = re.search(r'export const CAST_TO_CARD\s*=\s*([\d.]+)', open(lib).read())
        if m:
            c2c = float(m.group(1))
    out = []
    parts = re.split(r'<Shot from=\{([\d.]+)\} to=\{([\d.]+)\}>', src)
    for i in range(1, len(parts), 3):
        a, b, body = float(parts[i]), float(parts[i + 1]), parts[i + 2]
        # ZOOM CAN BE ANIMATED, and this regex only ever matched a literal.
        # `zoom={interpolate(f, [...], [1.35, 1.42], clamp)}` silently scored as
        # zoom=1.0 and understated every head in that shot by 35-42%. Case 0003's
        # cold open already uses it, and the motion doctrine pushes every shot
        # toward a moving camera, so this was one staging decision away from
        # letting an unreadable episode pass.
        #
        # An animated zoom has a RANGE. Take the SMALLEST value in it: that is
        # the widest the shot ever gets, so the head size reported is the
        # smallest the viewer ever sees, and the gate cannot be satisfied by a
        # zoom that only briefly gets close.
        zm = re.search(r'<Cam[^>]*?zoom=\{(.+?)\}\s*>', body, re.S)
        zoom = 1.0
        if zm:
            nums = [float(x) for x in re.findall(r'(?<![\w.])\d+\.?\d*', zm.group(1))]
            # drop frame-number arguments: a zoom is a small multiplier, and an
            # interpolate's input range is frames or seconds, which are not.
            cand = [x for x in nums if 0.05 <= x <= 20.0]
            zoom = min(cand) if cand else 1.0
        for cm in re.finditer(
                r'crown=\{CARD_W \* CAST_TO_CARD(?:\s*\*\s*([\d.]+))?\}', body):
            mult = float(cm.group(1)) if cm.group(1) else 1.0
            head = card_w * c2c * mult * HEAD_FRAC * zoom
            out.append((a, b, zoom, mult, head, head / H * 100.0))
    return out


def check(src):
    rows = []

    def row(n, ok, d):
        rows.append((n, ok, d))

    hits = measure(src)
    if not hits:
        row("the scene places the cast at all", False,
            "no `crown={CARD_W * CAST_TO_CARD...}` found. Either the cast are "
            "never staged or this scene uses a shape this gate cannot read, and "
            "both need a human.")
        return rows, hits
    row("the scene places the cast at all", True, f"{len(hits)} placement(s)")

    insane = [h for h in hits if h[5] > 100.0]
    row("the measurements are physically possible", not insane,
        "sane" if not insane else
        f"{len(insane)} placement(s) over 100% of frame height. That is a PARSE "
        f"fault in this gate, not a staging finding: check CARD_W / CAST_TO_CARD.")
    if insane:
        return rows, hits

    biggest = max(h[5] for h in hits)
    row(f"at least one REACTION shot (head >= {REACT_MIN:.0f}% of frame)",
        biggest >= REACT_MIN,
        f"largest head is {biggest:.1f}%"
        + ("" if biggest >= REACT_MIN else
           "   <- this episode never cuts to a face, so every expression it "
           "generates is decoration nobody can see"))

    # The MEDIAN, not every placement. The first cut of this failed any shot under
    # 7% and the self-test caught it immediately: a wide establishing shot with
    # small figures is legitimate cinema, and a gate that bans it would push
    # every episode into the same mid-shot. What is NOT legitimate is an episode
    # whose TYPICAL character is unreadable, which is what case 0003 is.
    pcts = sorted(h[5] for h in hits)
    median = pcts[len(pcts) // 2] if len(pcts) % 2 else \
        (pcts[len(pcts) // 2 - 1] + pcts[len(pcts) // 2]) / 2
    tiny = [h for h in hits if h[5] < SPEAK_MIN]
    row(f"the MEDIAN placement is >= {SPEAK_MIN:.0f}% of frame height",
        median >= SPEAK_MIN,
        f"median {median:.1f}%, {len(tiny)} of {len(hits)} below"
        + ("" if median >= SPEAK_MIN else
           "   <- wides are fine, an episode of nothing but wides is not"))
    return rows, hits


def run(path):
    if not os.path.exists(path):
        print(f"  FAIL the scene exists                          {path} is not on disk")
        return 1
    src = open(path).read()
    rows, hits = check(src)
    for n, ok, d in rows:
        print(f"  {'ok  ' if ok else 'FAIL'} {n:<48} {d}")
    if hits:
        print("\n  every cast placement, head as % of frame height:")
        for a, b, z, m_, px, pct in sorted(hits, key=lambda h: h[5]):
            bar = "#" * max(1, min(60, int(pct)))
            print(f"    {a:5.1f}-{b:<6.1f} zoom {z:4.2f}  {pct:5.1f}%  {bar}")
    ok = all(o for _, o, _ in rows)
    print("\nface_size: PASS" if ok else
          "\nface_size: FAIL. The acting layer is rendering at a size nobody can "
          "see.\n           Get closer, or stop generating expressions.")
    return 0 if ok else 1


def self_test():
    shot = ('<Shot from={0} to={4}>\n<Cam cy={0.5} zoom={%s}>\n'
            'crown={CARD_W * CAST_TO_CARD * %s}\n</Cam>\n</Shot>\n')
    head = 'const CARD_W = 620;\nCAST_TO_CARD = 0.72\n'
    wide_only = head + shot % ("1.45", "1.0")             # 5.0%
    has_close = head + shot % ("1.45", "1.0") + \
        '<Shot from={4} to={8}>\n<Cam cy={0.5} zoom={5.0}>\ncrown={CARD_W * CAST_TO_CARD * 1.6}\n</Cam>\n</Shot>\n'
    ok = True
    animated = head + (
        '<Shot from={0} to={4}>\n'
        '<Cam cy={0.5} zoom={interpolate(f, [0, s(2.3)], [1.35, 1.42], clamp)}>\n'
        'crown={CARD_W * CAST_TO_CARD * 1.0}\n</Cam>\n</Shot>\n')
    cases = [
        ("an episode that never cuts to a face", "REACTION shot", wide_only),
        ("an episode whose typical character is unreadable", "MEDIAN placement", wide_only),
        ("a scene that never stages the cast", "places the cast at all", head),
    ]
    for name, guard, src in cases:
        rows, _ = check(src)
        fired = any(guard in n and not o for n, o, _ in rows)
        print(f"  {'ok  ' if fired else 'FAIL'} catches: {name}"
              + ("" if fired else f"   <- did NOT fire: {guard}"))
        ok &= fired
    z = measure(animated)
    got = z[0][2] if z else 0.0
    okz = abs(got - 1.35) < 0.01
    print(f"  {'ok  ' if okz else 'FAIL'} reads an ANIMATED zoom at its widest "
          f"(interpolate 1.35->1.42 read as {got:.2f}, want 1.35)")
    ok &= okz

    rows, hits = check(has_close)
    clean = all(o for _, o, _ in rows)
    big = max(h[5] for h in hits) if hits else 0
    print(f"  {'ok  ' if clean else 'FAIL'} accepts: a wide PLUS a real close-up "
          f"(largest head {big:.0f}%)")
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
    ap.add_argument("--scene", default=DEFAULT)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    return self_test() if a.self_test else run(a.scene)


if __name__ == "__main__":
    sys.exit(main())
