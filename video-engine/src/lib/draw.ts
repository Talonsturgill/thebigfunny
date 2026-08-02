/**
 * draw.ts — the drawing primitives. Curves, not coordinates.
 *
 * WHY THIS FILE EXISTS
 * The old cast was hand-authored SVG `d` strings, and every failure it had came
 * from that fact rather than from any individual number being wrong:
 *
 *   - Every form was an axis-aligned box or a CONSTANT-WIDTH stroke, so no limb
 *     could taper and no torso could have a waist that was not bolted on.
 *   - Everything was perfectly bilaterally symmetric, because mirroring a path
 *     is the only cheap way to author one by hand.
 *   - Ink weight was uniform everywhere, which is the single loudest tell of
 *     clip art.
 *
 * Fixing those one path at a time is what the last seven passes were, and it
 * produced a mannequin. So this file stops writing coordinates and starts
 * describing FORMS: a spine of points with a width at each point, turned into a
 * smooth closed outline. A limb is a ribbon that is fat at the bicep and thin at
 * the wrist. A torso is a ribbon that is wide at the shoulder, narrow at the
 * waist and wide again at the hip; the hourglass is not a special case, it is
 * three numbers.
 *
 * Nothing here knows what a character is. That is deliberate.
 */

export type Pt = readonly [number, number];

const sub = (a: Pt, b: Pt): Pt => [a[0] - b[0], a[1] - b[1]];
const add = (a: Pt, b: Pt): Pt => [a[0] + b[0], a[1] + b[1]];
const mul = (a: Pt, k: number): Pt => [a[0] * k, a[1] * k];
const len = (a: Pt) => Math.hypot(a[0], a[1]) || 1e-6;
const norm = (a: Pt): Pt => mul(a, 1 / len(a));
/** left-hand perpendicular */
const perp = (a: Pt): Pt => [-a[1], a[0]];
const f2 = (n: number) => (Math.round(n * 100) / 100).toString();

/**
 * Catmull-Rom through `pts`, emitted as cubic beziers.
 *
 * Catmull-Rom is the right spline here because it INTERPOLATES its control
 * points: the curve passes exactly through the joints you specify, so a knee is
 * where you said the knee was. A B-spline only approximates them, which means
 * every joint drifts and the pose you authored is not the pose that renders.
 *
 * `closed` wraps the ends so an outline has no seam. `tension` 0 is the standard
 * uniform Catmull-Rom; higher flattens toward straight lines.
 */
export function spline(pts: readonly Pt[], closed = false, tension = 0): string {
  if (pts.length < 2) return '';
  if (pts.length === 2) return `M${f2(pts[0][0])},${f2(pts[0][1])} L${f2(pts[1][0])},${f2(pts[1][1])}`;
  const n = pts.length;
  const at = (i: number): Pt =>
    closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))];
  const k = (1 - tension) / 6;
  let d = `M${f2(pts[0][0])},${f2(pts[0][1])}`;
  const last = closed ? n : n - 1;
  for (let i = 0; i < last; i++) {
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    const c1 = add(p1, mul(sub(p2, p0), k));
    const c2 = sub(p2, mul(sub(p3, p1), k));
    d += ` C${f2(c1[0])},${f2(c1[1])} ${f2(c2[0])},${f2(c2[1])} ${f2(p2[0])},${f2(p2[1])}`;
  }
  return closed ? d + ' Z' : d;
}

/**
 * THE CENTRAL PRIMITIVE. A closed outline around a spine, with a width at every
 * spine point.
 *
 * This is what makes a limb read as a limb. The old rig drew arms as strokes of
 * one width, which is a PIPE: no bicep, no forearm taper, no wrist. Give the
 * same three joints widths of [46, 34, 22] and you get an arm.
 *
 * `capStart` / `capEnd` round the ends off (a shoulder is round, a cut end is
 * not). Widths are TOTAL width, not radius, because that is how a person thinks
 * about a limb.
 */
export function ribbon(
  spine: readonly Pt[],
  widths: readonly number[],
  opts: {capStart?: boolean; capEnd?: boolean; tension?: number} = {},
): string {
  const {capStart = true, capEnd = true, tension = 0} = opts;
  const n = spine.length;
  if (n < 2) return '';
  const w = (i: number) => (widths[Math.min(i, widths.length - 1)] ?? widths[widths.length - 1]) / 2;

  // Tangent at each point: the average of the incoming and outgoing directions,
  // so the outline does not kink where two segments meet at an angle.
  const tan: Pt[] = spine.map((p, i) => {
    const back = i > 0 ? norm(sub(p, spine[i - 1])) : null;
    const fwd = i < n - 1 ? norm(sub(spine[i + 1], p)) : null;
    if (back && fwd) return norm(add(back, fwd));
    return (back ?? fwd) as Pt;
  });

  const left: Pt[] = spine.map((p, i) => add(p, mul(perp(tan[i]), w(i))));
  const right: Pt[] = spine.map((p, i) => sub(p, mul(perp(tan[i]), w(i))));

  // Round caps become extra spine points pushed out along the tangent, so the
  // cap is part of the same smooth outline rather than a separate arc that has
  // to meet it exactly.
  const head: Pt[] = capEnd ? [add(spine[n - 1], mul(tan[n - 1], w(n - 1) * 0.85))] : [];
  const tail: Pt[] = capStart ? [sub(spine[0], mul(tan[0], w(0) * 0.85))] : [];

  const loop = [...left, ...head, ...right.slice().reverse(), ...tail];
  return spline(loop, true, tension);
}

/**
 * One EDGE of a ribbon, as an open path. Used for line-weight modulation: the
 * shadow side of a form gets a heavier stroke laid over the outline, which is
 * how ink drawing implies light without adding a single fill. `side` 1 is the
 * left-hand offset, -1 the right.
 */
export function edge(
  spine: readonly Pt[],
  widths: readonly number[],
  side: 1 | -1,
  from = 0,
  to = 1,
): string {
  const n = spine.length;
  const w = (i: number) => (widths[Math.min(i, widths.length - 1)] ?? 0) / 2;
  const tan: Pt[] = spine.map((p, i) => {
    const back = i > 0 ? norm(sub(p, spine[i - 1])) : null;
    const fwd = i < n - 1 ? norm(sub(spine[i + 1], p)) : null;
    if (back && fwd) return norm(add(back, fwd));
    return (back ?? fwd) as Pt;
  });
  const pts = spine.map((p, i) => add(p, mul(perp(tan[i]), w(i) * side)));
  const a = Math.max(0, Math.floor(from * (n - 1)));
  const b = Math.min(n - 1, Math.ceil(to * (n - 1)));
  return spline(pts.slice(a, b + 1));
}

/** Rotate `p` about `o` by `deg`. Poses are angles, not retyped coordinates. */
export function rot(p: Pt, o: Pt, deg: number): Pt {
  const r = (deg * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r);
  const d = sub(p, o);
  return [o[0] + d[0] * c - d[1] * s, o[1] + d[0] * s + d[1] * c];
}

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const lerpPt = (a: Pt, b: Pt, t: number): Pt => [lerp(a[0], b[0], t), lerp(a[1], b[1], t)];

/**
 * A limb spine that BENDS rather than folding. Given a start, an end and a bend
 * amount, produce the joint chain with the mid-joint pushed off the straight
 * line. This is "straight against curve": a limb is never two straight bones on
 * screen, it is a curve with a direction change in the middle, and the direction
 * change is what makes it read as jointed instead of as noodle.
 */
export function bent(a: Pt, b: Pt, bend: number, samples = 5): Pt[] {
  const mid = lerpPt(a, b, 0.5);
  const n = perp(norm(sub(b, a)));
  const ctrl = add(mid, mul(n, bend));
  const out: Pt[] = [];
  for (let i = 0; i < samples; i++) {
    const t = i / (samples - 1);
    const u = 1 - t;
    out.push([
      u * u * a[0] + 2 * u * t * ctrl[0] + t * t * b[0],
      u * u * a[1] + 2 * u * t * ctrl[1] + t * t * b[1],
    ]);
  }
  return out;
}
