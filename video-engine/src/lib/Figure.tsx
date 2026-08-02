/**
 * Figure.tsx — the cast, rebuilt from first principles.
 *
 * The old cast was deleted. This is not a refactor of it and it shares no
 * geometry with it, because the problem was never any individual number.
 *
 * WHAT WAS ACTUALLY WRONG, so it does not get rebuilt by accident
 * The previous rig was a hand-authored paper doll, and three properties of that
 * approach produced every failure it had:
 *   1. Every form was an axis-aligned box or a CONSTANT-WIDTH stroke. A limb
 *      drawn as a stroke is a pipe: it cannot have a bicep, a forearm taper or a
 *      wrist. A torso drawn as one path cannot have a waist unless somebody
 *      types one in.
 *   2. Perfect bilateral symmetry, because mirroring is the only cheap way to
 *      hand-author a figure. A perfectly symmetric standing figure reads as a
 *      mannequin no matter how good its proportions are.
 *   3. Uniform ink weight, which is the loudest single tell of clip art.
 * Seven passes of fixing those one path at a time produced a mannequin with a
 * waist. So this file describes FORMS (see draw.ts) and poses them, and the
 * three properties above are structurally impossible here.
 *
 * WHAT IT IS BUILT ON
 *   - PROPORTION, from anthropometry rather than from taste. 6.8 heads. Torso
 *     widths straight off the shoulder:waist:hip ratios. Head landmarks off a
 *     measured model. Every number is annotated with what it came from.
 *   - LINE OF ACTION. The spine is an S, not a segment. Nothing here is drawn
 *     on the vertical axis.
 *   - CONTRAPPOSTO. Weight on one leg, hips tilted, shoulders counter-tilted.
 *     This is the single largest difference between "a person standing" and "a
 *     figure placed."
 *   - OVERLAP. Arms cross in front of the torso, hair falls over the shoulder,
 *     the far leg sits behind the near one. Depth in a flat medium is entirely
 *     made of things being in front of other things.
 *   - LINE WEIGHT. Heavy under forms and on the shadow side, light on the lit
 *     side. This is what carries light in ink drawing.
 */
import React from 'react';
import {Pt, ribbon, edge, band, spline, bent, lerp} from './draw';

export type Emotion =
  | 'neutral' | 'angry' | 'worried' | 'shock' | 'smug' | 'flat' | 'squint';
export type Pose = 'stand' | 'arms-crossed' | 'point' | 'panic' | 'raise';
export type Sex = 'f' | 'm';

const INK = '#141420';

/* ===========================================================================
   PROPORTION TABLES
   Head height H = 100 units. Total figure 680 = 6.8 H.

   6.8 is chosen, not inherited: the adult floor is 6.0 (below it a figure reads
   as a teenager and below 5.5 as a child), the appealing band is 6.5 to 7.5, and
   the low end of that band keeps the head large enough for facial acting to be
   legible on a phone. The old rig was 3.9 heads, which is the canon for a
   toddler, and that alone was most of why nothing about it read as an adult.

   Vertical landmarks are the standard 8-head figure's, rescaled to 6.8.
   =========================================================================== */
const Y = {
  crown: 0,
  chin: 100,
  shoulder: 158,
  chest: 212,
  hip: 345,     // crotch at 0.507 of height, the classic mid-point
  knee: 500,
  ankle: 652,
  ground: 680,
} as const;

type Spec = {
  headW: number;          // bizygomatic (cheekbone) width
  waistY: number;         // the female waist sits measurably higher
  shoulder: number; bust: number; underbust: number; waist: number; upperHip: number; hip: number;
  neckW: number;
  armW: readonly number[];   // bicep, elbow, wrist
  legW: readonly number[];   // thigh, knee, ankle
  shoulderJoint: number; hipJoint: number;
  eyeRx: number; eyeRy: number; eyeX: number;
  tilt: number;           // canthal tilt, degrees
  browGap: number; browW: number;
  noseHalf: number; mouthHalf: number; lipMass: number;
  jawRatio: number;       // bigonial / bizygomatic
  chinW: number;          // menton width as a fraction of bizygomatic
  headTension: number;    // 0 = pure curve (female), higher = straighter (male)
};

/* Torso widths are the measured attractiveness ratios, with hip width as 1.00.
   Female 1.02 : 0.70 : 1.00 (the 0.70 waist-hip is Singh, replicated
   cross-culturally). Male 1.44 : 0.90 : 1.00 (the 1.6 shoulder-to-waist figure
   usually quoted is fitness-industry convention with much weaker support, so
   this uses the more defensible number). */
const SPEC: Record<Sex, Spec> = {
  f: {
    headW: 66, waistY: 288,
    // bust as wide as the shoulder, then a hard drop to a 0.62 waist over a
    // SHORT span, then a hip wider than the shoulder. Waist-to-hip lands at
    // 0.62, tighter than the 0.70 average-preference figure on purpose: this is
    // a caricature, and silhouette is the one place caricature is right.
    shoulder: 142, bust: 158, underbust: 100, waist: 78, upperHip: 150, hip: 178,
    neckW: 33,                       // 0.50 of head width
    armW: [37, 28, 20], legW: [78, 41, 51, 22],
    shoulderJoint: 66, hipJoint: 32,
    // Palpebral fissure LENGTH is not dimorphic (2.71 vs 2.73 cm, ns). What
    // differs is roundness and tilt, so the eye is not enlarged here; the face
    // around it is smaller. h/w 0.47, at the round end of the adult band (over
    // 0.55 reads infantile, which is where the old rig sat at 1.16).
    eyeRx: 9.2, eyeRy: 4.4, eyeX: 18, tilt: 7,
    browGap: 9.0, browW: 2.7,        // 0.048 H measured, same correction
    noseHalf: 7.5, mouthHalf: 13.5, lipMass: 6.2,
    jawRatio: 0.72, chinW: 0.2, headTension: 0,
  },
  m: {
    headW: 68, waistY: 302,
    // no flare at the bottom: a V that widens again at the hip reads as a gut.
    shoulder: 211, bust: 194, underbust: 156, waist: 132, upperHip: 142, hip: 145,
    neckW: 45,                       // 0.65 of head width
    armW: [56, 42, 29], legW: [90, 50, 62, 29],
    shoulderJoint: 88, hipJoint: 30,
    eyeRx: 9.2, eyeRy: 3.7, eyeX: 18, tilt: 3,
    browGap: 8.5, browW: 4.4,        // neat and CLEAR of the eye, not a shelf over it
    noseHalf: 8, mouthHalf: 14, lipMass: 4.4,
    jawRatio: 0.8, chinW: 0.30, headTension: 0.04,
  },
};

/* ===========================================================================
   THE HEAD OUTLINE
   Built as landmarks, not as a path string, so the sex difference is a ratio
   rather than a redraw.

   The male/female difference is bigonial WIDTH and whether the lower border
   runs STRAIGHT before it turns. It is NOT the gonial angle: radiography
   consistently finds the female angle is the more obtuse one, which is the
   opposite of what every drawing tutorial implies. So the female border is one
   continuous curve and the male's is the same landmark chain pulled toward
   straight lines by `headTension`.

   The pull-IN between cheekbone and jaw is the ogee. It encodes "prominent
   cheekbones plus narrow cheeks", which is the validated maturity pair, and it
   is what stops a big-eyed face from reading as a child.
   =========================================================================== */
function headOutline(s: Spec): Pt[] {
  const w = s.headW / 2;
  const jaw = w * s.jawRatio;
  const ogee = lerp(jaw, w, s.jawRatio > 0.78 ? 0.62 : 0.25);   // males pull in less
  const chin = w * s.chinW;
  const R: Pt[] = [
    [0, 0],
    [w * 0.60, 5],
    [w * 0.93, 25],
    [w, 50],            // bizygomatic: widest point, at the eyeline
    [ogee, 65],         // the ogee pull-in, at 0.65 H
    [jaw, 81],          // bigonial, at 0.81 H
    // The male gets one extra landmark COLLINEAR with the two above it, which
    // makes the mandibular border a straight run before it turns. That, and not
    // the gonial angle, is what a "square jaw" actually is.
    ...(s.jawRatio > 0.78 ? [[lerp(chin, jaw, 0.8), 90] as Pt] : []),
    [lerp(chin, jaw, 0.55), 93],
    [chin, 99],
    [0, 100],           // menton
  ];
  return [...R, ...R.slice(1, -1).reverse().map(([x, y]) => [-x, y] as Pt)];
}

/* =========================================================================== */

export type FigureProps = {
  frame: number;
  sex: Sex;
  x?: number; y?: number; scale?: number; facing?: 1 | -1;
  emotion?: Emotion;
  pose?: Pose;
  skin?: string; hair?: string; eyes?: string;
  /** garment + accent. Two colours is all a flat figure should carry. */
  wear?: {top: string; bottom: string; accent?: string};
  hairstyle?: 'long' | 'short' | 'wave';
  /** 'skirt' bares the legs and puts her in heels. */
  garment?: 'trousers' | 'skirt';
  /** 0..1 per frame from the VO envelope. */
  mouth?: number;
  mouthSpread?: number;
  talking?: boolean;
  idleGain?: number;
};

const EYES: Record<Emotion, {open: number; lid: number; brow: number; browTilt: number}> = {
  // `open` scales the fissure, `lid` drops the upper lid over it, `brow` raises
  // the bar, `browTilt` angles it. Narrowing is done with the LID rather than by
  // closing the eye, so a mood never reads as a blink.
  neutral: {open: 1, lid: 0, brow: 0, browTilt: 0},
  angry: {open: 0.92, lid: 0.14, brow: -4.5, browTilt: -17},
  worried: {open: 1.1, lid: -0.1, brow: 3.5, browTilt: 16},
  shock: {open: 1.45, lid: -0.25, brow: 8, browTilt: -6},
  smug: {open: 0.86, lid: 0.34, brow: 1.5, browTilt: -6},
  flat: {open: 0.9, lid: 0.3, brow: 0.5, browTilt: 0},
  squint: {open: 0.8, lid: 0.4, brow: -1.5, browTilt: -11},
};

export const Figure: React.FC<FigureProps> = ({
  frame: f, sex,
  x = 0, y = 0, scale = 1, facing = 1,
  emotion = 'neutral', pose = 'stand',
  skin = '#e0a882', hair = '#2a1c16', eyes = '#3d5a72',
  wear = {top: '#3f6f8f', bottom: '#2f3a52', accent: '#e8dcc8'},
  hairstyle = 'short',
  garment = 'trousers',
  mouth, mouthSpread = 0.5, talking, idleGain = 1,
}) => {
  const s = SPEC[sex];
  const uid = `fg${React.useId().replace(/:/g, '')}`;
  const E = EYES[emotion] ?? EYES.neutral;

  /* ---- IDLE. A slow weight shift, a breath, and a head delay.
     The head lags the torso by a fraction of a cycle. That lag is the whole
     difference between a figure that is alive and one that is being translated:
     a rigid body has every part moving in lockstep, and a person does not. */
  const breathe = Math.sin(f / 34);
  const shift = 3.4 * idleGain * Math.sin(f / 62);
  const headLag = 2.2 * idleGain * Math.sin(f / 62 - 0.55);
  const blink = (f + 17) % 104 < 5 && emotion !== 'shock';

  /* ---- CONTRAPPOSTO. Weight on the figure's right (screen left when facing 1).
     The hip on the weight side rides UP, the shoulders counter-tilt the other
     way, and the free leg goes slack. Three numbers, and they are most of what
     separates a standing person from a placed figure. */
  const hipTilt = 4.5;
  const shTilt = -3.2;
  const waistY = s.waistY;

  /* ---- TORSO. A ribbon down an S-curved spine, with the shoulder:waist:hip
     ratios as its widths. The hourglass is not a special case here: it is three
     numbers, and the male V-taper is the same three numbers with no flare at
     the bottom. */
  const spine: Pt[] = [
    [3.6 + shift * 0.2, Y.shoulder - 2],    // shoulder slope, NOT a collar: at
    [3.0 + shift * 0.25, Y.shoulder + 6],   // -38 the garment climbed the neck
    [1.0 + shift * 0.5, Y.chest],
    [-2.6 + shift, waistY],
    [1.6 + shift * 0.7, Y.hip],
    [2.2 + shift * 0.7, Y.hip + 40],        // runs PAST the hip so the flat end
  ];                                        // cut lands where the legs hide it
  const torsoW = [s.shoulder * 0.66, s.shoulder, s.bust, s.waist, s.hip, s.hip * 0.9];

  /* ---- ARMS. A pose is three joint positions, not a redrawn path. */
  const armSpine = (side: 1 | -1): Pt[] => {
    const far = side > 0;
    const sh: Pt = [side * (s.shoulderJoint - (far ? 16 : 0)) + shift * 0.4,
                    Y.shoulder + 6 + (far ? 16 : 0) + side * shTilt];
    switch (pose) {
      case 'arms-crossed': {
        // Forearms stacked at DIFFERENT heights, each hand tucked at the
        // opposite elbow. Two mirrored arcs at the same height close into an
        // oval and read as a barrel, which is the classic version of this pose
        // going wrong.
        const yOff = side > 0 ? 0 : 16;
        return [sh, [side * (s.shoulderJoint + 12), Y.chest + 34],
                [side * 26, Y.chest + 74 + yOff], [-side * 40, Y.chest + 70 + yOff]];
      }
      case 'point':
        return side === facing
          ? [sh, [side * (s.shoulderJoint + 26), Y.chest + 10], [side * (s.shoulderJoint + 96), Y.chest - 26]]
          : [sh, ...bent(sh, [side * (s.shoulderJoint + 16), Y.hip + 42], side * 13, 4).slice(1)];
      case 'raise':
        return [sh, [side * (s.shoulderJoint + 30), Y.chest - 30], [side * (s.shoulderJoint + 22), Y.shoulder - 96]];
      case 'panic':
        return [sh, [side * (s.shoulderJoint + 40), Y.chest - 6], [side * (s.shoulderJoint + 54), Y.shoulder - 62]];
      default:
        // Hanging, and NOT mirrored: one arm slightly further forward and a
        // touch more bent. Symmetry is the thing being avoided.
        return bent(sh, [side * (s.hip * 0.5 + 16 + (side > 0 ? 4 : 0)), Y.hip + 62],
                    side * (side > 0 ? 15 : 11), 4);
    }
  };

  /* ---- LEGS. The weight leg carries the body and stays near-straight; the free
     leg bends and its knee falls inward. Both feet stay on the ground line. */
  const heels = garment === 'skirt';
  const legSpine = (side: 1 | -1): Pt[] => {
    const weight = side < 0;
    const hipX = side * s.hipJoint + shift * 0.5 + (weight ? -1 : 2);
    const kneeX = side * (s.hipJoint + (weight ? 3 : -5));
    const ankleX = side * (s.hipJoint + (weight ? 1 : 9));
    const kneeY = Y.knee + (weight ? 0 : -6);
    return [
      [hipX, Y.hip - 10 + (weight ? -hipTilt : hipTilt)],
      [kneeX, kneeY],
      // calf belly, a third of the way down the shin
      [kneeX + side * (weight ? 3 : 4), kneeY + (Y.ankle - kneeY) * 0.34],
      // In heels the ankle sits well ABOVE the ground and the shoe spans the gap.
      [ankleX, heels ? Y.ankle - 32 : Y.ankle],
    ];
  };

  const headY = Y.chin;   // head group is translated so the CHIN sits at y=0
  const outline = headOutline(s);

  /* ---- FACE ------------------------------------------------------------- */
  const face = () => {
    const eyeY = 50, rx = s.eyeRx, ry = s.eyeRy * E.open;
    const hw = s.headW / 2;
    const lidDrop = ry * E.lid;
    const browY = eyeY - ry - s.browGap - E.brow;
    const eye = (side: 1 | -1) => {
      const cx = side * s.eyeX;
      const tilt = side * s.tilt;
      return (
        <g key={side} transform={`rotate(${tilt} ${cx} ${eyeY})`}>
          {blink ? (
            <path d={`M${cx - rx},${eyeY} q${rx},${ry * 1.1} ${rx * 2},0`}
                  fill="none" stroke={INK} strokeWidth={2.6} strokeLinecap="round" />
          ) : (
            <>
              <ellipse cx={cx} cy={eyeY} rx={rx} ry={ry} fill="#fdfbf6" />
              {/* IRIS mass at 60% of eye height. Facial contrast (the luminance
                  gap between eyes/lips and skin) is measurably higher in female
                  faces, flips perceived sex on its own, and unlike lashes it is
                  a LOW-frequency property, so it is the one feminine cue that
                  survives a thumbnail intact. It is also free in flat fill. */}
              <circle cx={cx + 0.8 * facing} cy={eyeY - ry * 0.1} r={ry * 1.02} fill={eyes} />
              <circle cx={cx + 0.8 * facing} cy={eyeY - ry * 0.1} r={ry * 0.55} fill={INK} />
              <circle cx={cx + 0.8 * facing - ry * 0.3} cy={eyeY - ry * 0.5} r={ry * 0.26} fill="#fff" />
              {lidDrop > 0 && (
                <path d={`M${cx - rx},${eyeY - ry + lidDrop} a${rx},${ry} 0 0 1 ${rx * 2},0 Z`}
                      fill={skin} />
              )}
              {/* UPPER LID as a weighted stroke, extending past the outer canthus.
                  Lash MASS, never individual lashes: a lash is sub-2px on a grid
                  tile and turns to mud. The lower lid is omitted entirely on the
                  female, because asymmetric lid weight reads both feminine and
                  open-eyed. */}
              <path d={`M${cx - rx - 1},${eyeY - ry * 0.35} q${rx},${-ry * 1.5} ${rx * 2 + (sex === 'f' ? 3 : 1)},${-ry * 0.1}`}
                    fill="none" stroke={INK} strokeLinecap="round"
                    strokeWidth={sex === 'f' ? 3.4 : 2.2} />
              {sex === 'm' && (
                <path d={`M${cx - rx * 0.7},${eyeY + ry * 0.85} q${rx * 0.7},${ry * 0.5} ${rx * 1.4},0`}
                      fill="none" stroke={INK} strokeWidth={1.2} opacity={0.5} strokeLinecap="round" />
              )}
            </>
          )}
        </g>
      );
    };
    return (
      <g>
        <clipPath id={`${uid}_headclip`}><path d={spline(outline, true, s.headTension)} /></clipPath>
        <g clipPath={`url(#${uid}_headclip)`}>
          {/* THE SHADOW SIDE. One hard-edged shape whose boundary follows the
              form: out over the cheekbone, in under it, out again at the jaw.
              That boundary IS the drawing; a soft gradient in the same place
              reads as a stain. */}
          <path d={spline([[hw * 0.26, -10], [hw * 0.66, 34], [hw * 0.46, 70],
                           [hw * 0.12, 104], [hw * 3, 104], [hw * 3, -10]], true)}
                fill={INK} opacity={0.13} />
          {/* reflected light at the very edge of the shadow side, where the form
              turns back toward the room */}
          <path d={spline([[hw * 0.9, 6], [hw * 1.02, 52], [hw * 0.72, 92],
                           [hw * 3, 92], [hw * 3, 6]], true)} fill="#fff" opacity={0.09} />
          {/* CAST SHADOW OF THE HAIR onto the forehead. Hair sits ON a head and
              blocks light; without this the hairline reads as a sticker. */}
          <path d={spline([[-hw * 3, -30], [hw * 3, -30], [hw * 3, 4],
                           [hw * 0.5, 24], [-hw * 0.5, 17], [-hw * 3, 2]], true)}
                fill={INK} opacity={0.15} />
          {/* brow ridge: a shelf the eyes sit under */}
          <path d={spline([[-hw * 0.85, 40], [0, 45], [hw * 0.85, 40],
                           [hw * 0.85, 33], [0, 37], [-hw * 0.85, 33]], true)}
                fill={INK} opacity={0.08} />
          {/* the lit cheekbone, the single plane that says the skull has one */}
          <ellipse cx={-hw * 0.46} cy={50} rx={hw * 0.42} ry={11} fill="#fff" opacity={0.17}
                   transform={`rotate(-12 ${-hw * 0.46} 50)`} />
          {/* nose plane on the shadow side, and the shelf under the lower lip */}
          <path d={spline([[facing * 3, 56], [facing * 11, 71], [facing * 2, 77]], true)}
                fill={INK} opacity={0.13} />
          <ellipse cx={0} cy={81 + s.lipMass * 1.5} rx={s.mouthHalf * 0.72} ry={3.4}
                   fill={INK} opacity={0.11} />
          {/* temple hollow, which is what stops a forehead reading as a dome */}
          <ellipse cx={hw * 0.74} cy={30} rx={9} ry={13} fill={INK} opacity={0.08} />
        </g>
        {/* cheekbone contour: a shade running down and IN under the cheek, with a
            lit plane above it. Only works on a narrowed skull; on a circle the
            same shape reads as a smudge. */}
        <path d={spline([[-s.headW / 2 + 2, 48], [-s.headW * 0.30, 66], [-s.headW * 0.22, 76]])}
              fill="none" stroke={INK} strokeWidth={3} opacity={0.1} strokeLinecap="round" />
        <path d={spline([[s.headW / 2 - 2, 48], [s.headW * 0.30, 66], [s.headW * 0.22, 76]])}
              fill="none" stroke={INK} strokeWidth={3.4} opacity={0.14} strokeLinecap="round" />
        {[-1, 1].map((sd) => eye(sd as 1 | -1))}
        {/* BROWS. The GAP is the cue, not the bar: a clean 0.048H of skin between
            brow and lid reads instantly at tile scale where a thin arched line
            does not. Female bar is thin and arched with its apex over the outer
            third; male bar is heavy and essentially flat. */}
        {[-1, 1].map((sd) => (
          <path key={sd}
                d={sex === 'f'
                  ? `M${sd * (s.eyeX - 11)},${browY + 2.5} q${sd * 7},${-4.5} ${sd * 21},${-0.5}`
                  : `M${sd * (s.eyeX - 12)},${browY + 1} L${sd * (s.eyeX + 11)},${browY - 0.5}`}
                fill="none" stroke={INK} strokeWidth={s.browW} strokeLinecap="round"
                transform={`rotate(${sd * E.browTilt} ${sd * s.eyeX} ${browY})`} />
        ))}
        {/* NOSE. Two marks, never a bridge line. A drawn bridge on an otherwise
            flat face is a detail-density mismatch, and over-defined noses and
            eyelids are the two most-cited causes of a stylized face tipping
            uncanny. */}
        {sex === 'm' && (
          <path d={`M${facing * 3},${46} L${facing * 4},${63}`} fill="none" stroke={INK}
                strokeWidth={2.2} opacity={0.32} strokeLinecap="round" />
        )}
        <path d={`M${facing * 2},${64} q${facing * s.noseHalf * 0.7},${8} ${facing * -1},${9}`}
              fill="none" stroke={INK} strokeWidth={sex === 'f' ? 2 : 2.6}
              opacity={0.55} strokeLinecap="round" />
        {/* MOUTH */}
        {mouth !== undefined || talking ? (
          <TalkingMouth open={mouth ?? 0} spread={mouthSpread} half={s.mouthHalf}
                        lip={sex === 'f' ? '#8d3347' : INK} full={sex === 'f'} />
        ) : (
          <StaticMouth emotion={emotion} half={s.mouthHalf} mass={s.lipMass}
                       lip={sex === 'f' ? '#8d3347' : INK} full={sex === 'f'} />
        )}
      </g>
    );
  };

  return (
    <g transform={`translate(${x},${y}) scale(${scale * facing},${scale})`}>
      <defs>
        <linearGradient id={`${uid}_top`} x1="0" y1="0" x2="1" y2="0.35">
          <stop offset="0%" stopColor={shade(wear.top, 1.14)} />
          <stop offset="62%" stopColor={wear.top} />
          <stop offset="100%" stopColor={shade(wear.top, 0.76)} />
        </linearGradient>
        <linearGradient id={`${uid}_skin`} x1="0" y1="0" x2="1" y2="0.3">
          <stop offset="0%" stopColor={shade(skin, 1.1)} />
          <stop offset="60%" stopColor={skin} />
          <stop offset="100%" stopColor={shade(skin, 0.82)} />
        </linearGradient>
      </defs>

      <ellipse cx={shift} cy={Y.ground + 4} rx={s.hip * 0.62} ry={13} fill={INK} opacity={0.16} />
      {/* ============ THE SILHOUETTE PASS ============
          Every part is drawn TWICE. First in solid ink with a fat stroke, which
          unions all the overlapping outlines into one merged blob; then again
          normally on top, which covers the interior and leaves that blob showing
          only as a rim.

          This is the single biggest thing separating a drawing from an assembly
          of parts. Drawn once, each limb carries its own closed outline, so a
          shoulder reads as a blob stuck ON a torso rather than as part of the
          same body: the detached epaulette that was visible on the far shoulder.
          Professional flat vector characters all do this, and it is why their
          figures read as one form with detail inside rather than as components.
          The alternative is a real boolean union (paper.js `unite()` at build
          time), which is cleaner but needs an offline step; two passes gets the
          same read at the cost of drawing the tree twice. */}
      <g className="sil" style={{
        // every fill and stroke forced to ink; the fat stroke is what merges
      }}>
        <g style={{stroke: INK, strokeWidth: 17, fill: INK}} strokeLinejoin="round">
          <g style={{visibility: 'visible'}}>

      {/* FAR LEG first: it goes BEHIND. Depth in a flat medium is made entirely
          of things being in front of other things. */}
      <Limb spine={legSpine(1)} w={s.legW} fill={INK} shadow />
      <Limb spine={legSpine(-1)} w={s.legW} fill={INK} />
      <Foot at={legSpine(1)[3]} side={1} col={wear.accent ?? INK} heel={garment === 'skirt'} shadow />
      <Foot at={legSpine(-1)[3]} side={-1} col={wear.accent ?? INK} heel={garment === 'skirt'} />

      {/* FAR ARM behind the torso, near arm in front of it. */}
      <Limb spine={armSpine(1)} w={s.armW} fill={INK} shadow />

      <g transform={`scale(1,${1 + 0.007 * breathe})`}>
        <path d={ribbon(spine, torsoW, {capStart: true, capEnd: false})}
              fill={INK} stroke={INK} strokeWidth={17}
              strokeLinejoin="round" />
        {/* LINE WEIGHT. A heavier stroke down the shadow side of the torso and a
            lighter one down the lit side. Uniform ink is the loudest tell of
            clip art, and this is two paths. */}
        <path d={band(spine, torsoW, -1, 0.22, 1)} fill={INK} opacity={0.19} />
        <path d={band(spine, torsoW, -1, 0.84, 1)} fill="#fff" opacity={0.09} />
        <path d={band(spine, torsoW, 1, 0.26, 0.72)} fill="#fff" opacity={0.13} />
        <path d={edge(spine, torsoW, -1)} fill="none" stroke={INK} strokeWidth={7}
              opacity={0.5} strokeLinecap="round" />
        {/* CAST SHADOW of the head onto the chest. Contact shadows are what tell
            you two forms are touching rather than merely overlapping, and a
            figure has the same two every time: head on chest, arm on body. */}
        <ellipse cx={2} cy={Y.shoulder + 26} rx={s.neckW * 1.5} ry={16} fill={INK} opacity={0.16} />
        {sex === 'f' && (
          // Bust and waist as the garment's own seams. The silhouette already
          // carries the shape; this is the fabric acknowledging it.
          <>
            <path d={spline([[-s.bust * 0.34, Y.chest - 14], [0, Y.chest + 10], [s.bust * 0.34, Y.chest - 14]])}
                  fill="none" stroke={INK} strokeWidth={2.4} opacity={0.28} />
            <path d={spline([[-s.waist * 0.46, waistY - 6], [0, waistY + 3], [s.waist * 0.46, waistY - 6]])}
                  fill="none" stroke={INK} strokeWidth={2.6} opacity={0.3} />
          </>
        )}
        {sex === 'm' && (
          // Pec shelf and the two lat lines the V-taper needs in order to explain
          // itself. A taper with nothing inside it reads as a garment, not a body.
          <>
            <path d={spline([[-s.bust * 0.34, Y.chest - 18], [0, Y.chest + 2], [s.bust * 0.34, Y.chest - 18]])}
                  fill="none" stroke={INK} strokeWidth={3} opacity={0.3} />
            <path d={spline([[0, Y.chest - 28], [0, Y.chest + 10]])}
                  fill="none" stroke={INK} strokeWidth={2.6} opacity={0.22} />
            <path d={spline([[-s.shoulder * 0.42, Y.shoulder + 20], [-s.waist * 0.5, waistY - 30]])}
                  fill="none" stroke={INK} strokeWidth={2.4} opacity={0.16} />
            <path d={spline([[s.shoulder * 0.42, Y.shoulder + 20], [s.waist * 0.5, waistY - 30]])}
                  fill="none" stroke={INK} strokeWidth={2.4} opacity={0.2} />
          </>
        )}
      </g>

      {/* SKIRT. Flares from the cinch and stops above the knee: the flare is what
          reads the waist-to-hip curve, and the short hem is what keeps the legs
          long. Both halves matter, and a long hem cancels a waist however hard
          you nip it, which is how the previous attempt went wrong. */}
      {garment === 'skirt' && (
        <g>
          <path d={ribbon([[-1.6 + shift, waistY + 6], [1.2 + shift * 0.8, Y.hip],
                           [2.4 + shift * 0.7, Y.hip + 74]],
                          [s.waist * 1.04, s.hip * 1.0, s.hip * 1.06], {capStart: false, capEnd: false})}
                fill={`url(#${uid}_top)`} stroke={INK} strokeWidth={4.5} strokeLinejoin="round" />
          <path d={edge([[-1.6 + shift, waistY + 6], [1.2 + shift * 0.8, Y.hip],
                         [2.4 + shift * 0.7, Y.hip + 74]],
                        [s.waist * 1.04, s.hip * 1.0, s.hip * 1.06], -1)}
                fill="none" stroke={INK} strokeWidth={7} opacity={0.45} strokeLinecap="round" />
          <path d={spline([[-s.hip * 0.34, Y.hip + 30], [-s.hip * 0.28, Y.hip + 80]])}
                fill="none" stroke="#fff" strokeWidth={5} opacity={0.13} strokeLinecap="round" />
        </g>
      )}
      {/* NECK, over the garment. Then a COLLAR RIM laid back over its base, so
          the neck comes THROUGH the opening instead of the opening being a patch
          of skin painted on a chest. */}
      <path d={ribbon([[2, Y.chin - 6], [1, Y.shoulder + 14]], [s.neckW, s.neckW * 1.18], {capEnd: false})}
            fill={INK} stroke={INK} strokeWidth={17} strokeLinejoin="round" />
      {/* the jaw's shadow down the throat: without it the neck is a pasted
          cylinder rather than something under a chin */}
      <path d={`M${-s.neckW * 0.44},${Y.chin - 4} q${s.neckW * 0.44},${10} ${s.neckW * 0.88},0 l0,13 q${-s.neckW * 0.44},${9} ${-s.neckW * 0.88},0 Z`}
            fill={INK} opacity={0.2} />
      <path d={sex === 'f'
        ? spline([[-s.neckW * 0.86, Y.shoulder - 6], [0, Y.shoulder + 30], [s.neckW * 0.86, Y.shoulder - 6],
                  [s.neckW * 1.02, Y.shoulder + 4], [0, Y.shoulder + 44], [-s.neckW * 1.02, Y.shoulder + 4]], true)
        : spline([[-s.neckW * 0.72, Y.shoulder - 2], [0, Y.shoulder + 16], [s.neckW * 0.72, Y.shoulder - 2],
                  [s.neckW * 0.88, Y.shoulder + 8], [0, Y.shoulder + 30], [-s.neckW * 0.88, Y.shoulder + 8]], true)}
            fill={INK} stroke={INK} strokeWidth={17} strokeLinejoin="round" />
      <Limb spine={armSpine(-1)} w={s.armW} fill={INK} />
      <Hand at={armSpine(-1)[armSpine(-1).length - 1]} r={s.armW[2] * 0.78} fill={skin} />
      <Hand at={armSpine(1)[armSpine(1).length - 1]} r={s.armW[2] * 0.74} fill={skin} shadow />

      {/* HEAD. Counter-rotated against the weight shift, and lagging it. */}
      <g transform={`translate(${headLag},0) translate(0,${Y.chin - 100}) rotate(${-shTilt * 0.5} 0 100)`}>
        {/* hair BEHIND the skull */}
        <Hair style={hairstyle} s={s} col={hair} back />
        <path d={spline(outline, true, s.headTension)} fill={INK}
              stroke={INK} strokeWidth={17} strokeLinejoin="round" />
        {/* shadow-side head contour, heavier than the lit side */}
        <path d={spline(outline.slice(0, 9), false, s.headTension)} fill="none"
              stroke={INK} strokeWidth={6} opacity={0.35} strokeLinecap="round" />
        {face()}
        {/* hair OVER the skull and over the near shoulder: the overlap is what
            makes it sit on a head rather than behind one */}
        <Hair style={hairstyle} s={s} col={hair} />
      </g>
          </g>
        </g>
      </g>

      {/* FAR LEG first: it goes BEHIND. Depth in a flat medium is made entirely
          of things being in front of other things. */}
      <Limb spine={legSpine(1)} w={s.legW} fill={garment === 'skirt' ? `url(#${uid}_skin)` : wear.bottom} shadow />
      <Limb spine={legSpine(-1)} w={s.legW} fill={garment === 'skirt' ? `url(#${uid}_skin)` : wear.bottom} />
      <Foot at={legSpine(1)[3]} side={1} col={wear.accent ?? INK} heel={garment === 'skirt'} shadow />
      <Foot at={legSpine(-1)[3]} side={-1} col={wear.accent ?? INK} heel={garment === 'skirt'} />

      {/* FAR ARM behind the torso, near arm in front of it. */}
      <Limb spine={armSpine(1)} w={s.armW} fill={`url(#${uid}_skin)`} shadow />

      <g transform={`scale(1,${1 + 0.007 * breathe})`}>
        <path d={ribbon(spine, torsoW, {capStart: true, capEnd: false})}
              fill={`url(#${uid}_top)`} stroke={INK} strokeWidth={4.5}
              strokeLinejoin="round" />
        {/* LINE WEIGHT. A heavier stroke down the shadow side of the torso and a
            lighter one down the lit side. Uniform ink is the loudest tell of
            clip art, and this is two paths. */}
        <path d={band(spine, torsoW, -1, 0.22, 1)} fill={INK} opacity={0.19} />
        <path d={band(spine, torsoW, -1, 0.84, 1)} fill="#fff" opacity={0.09} />
        <path d={band(spine, torsoW, 1, 0.26, 0.72)} fill="#fff" opacity={0.13} />
        <path d={edge(spine, torsoW, -1)} fill="none" stroke={INK} strokeWidth={7}
              opacity={0.5} strokeLinecap="round" />
        {/* CAST SHADOW of the head onto the chest. Contact shadows are what tell
            you two forms are touching rather than merely overlapping, and a
            figure has the same two every time: head on chest, arm on body. */}
        <ellipse cx={2} cy={Y.shoulder + 26} rx={s.neckW * 1.5} ry={16} fill={INK} opacity={0.16} />
        {sex === 'f' && (
          // Bust and waist as the garment's own seams. The silhouette already
          // carries the shape; this is the fabric acknowledging it.
          <>
            <path d={spline([[-s.bust * 0.34, Y.chest - 14], [0, Y.chest + 10], [s.bust * 0.34, Y.chest - 14]])}
                  fill="none" stroke={INK} strokeWidth={2.4} opacity={0.28} />
            <path d={spline([[-s.waist * 0.46, waistY - 6], [0, waistY + 3], [s.waist * 0.46, waistY - 6]])}
                  fill="none" stroke={INK} strokeWidth={2.6} opacity={0.3} />
          </>
        )}
        {sex === 'm' && (
          // Pec shelf and the two lat lines the V-taper needs in order to explain
          // itself. A taper with nothing inside it reads as a garment, not a body.
          <>
            <path d={spline([[-s.bust * 0.34, Y.chest - 18], [0, Y.chest + 2], [s.bust * 0.34, Y.chest - 18]])}
                  fill="none" stroke={INK} strokeWidth={3} opacity={0.3} />
            <path d={spline([[0, Y.chest - 28], [0, Y.chest + 10]])}
                  fill="none" stroke={INK} strokeWidth={2.6} opacity={0.22} />
            <path d={spline([[-s.shoulder * 0.42, Y.shoulder + 20], [-s.waist * 0.5, waistY - 30]])}
                  fill="none" stroke={INK} strokeWidth={2.4} opacity={0.16} />
            <path d={spline([[s.shoulder * 0.42, Y.shoulder + 20], [s.waist * 0.5, waistY - 30]])}
                  fill="none" stroke={INK} strokeWidth={2.4} opacity={0.2} />
          </>
        )}
      </g>

      {/* SKIRT. Flares from the cinch and stops above the knee: the flare is what
          reads the waist-to-hip curve, and the short hem is what keeps the legs
          long. Both halves matter, and a long hem cancels a waist however hard
          you nip it, which is how the previous attempt went wrong. */}
      {garment === 'skirt' && (
        <g>
          <path d={ribbon([[-1.6 + shift, waistY + 6], [1.2 + shift * 0.8, Y.hip],
                           [2.4 + shift * 0.7, Y.hip + 74]],
                          [s.waist * 1.04, s.hip * 1.0, s.hip * 1.06], {capStart: false, capEnd: false})}
                fill={`url(#${uid}_top)`} stroke={INK} strokeWidth={4.5} strokeLinejoin="round" />
          <path d={edge([[-1.6 + shift, waistY + 6], [1.2 + shift * 0.8, Y.hip],
                         [2.4 + shift * 0.7, Y.hip + 74]],
                        [s.waist * 1.04, s.hip * 1.0, s.hip * 1.06], -1)}
                fill="none" stroke={INK} strokeWidth={7} opacity={0.45} strokeLinecap="round" />
          <path d={spline([[-s.hip * 0.34, Y.hip + 30], [-s.hip * 0.28, Y.hip + 80]])}
                fill="none" stroke="#fff" strokeWidth={5} opacity={0.13} strokeLinecap="round" />
        </g>
      )}
      {/* NECK, over the garment. Then a COLLAR RIM laid back over its base, so
          the neck comes THROUGH the opening instead of the opening being a patch
          of skin painted on a chest. */}
      <path d={ribbon([[2, Y.chin - 6], [1, Y.shoulder + 14]], [s.neckW, s.neckW * 1.18], {capEnd: false})}
            fill={`url(#${uid}_skin)`} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
      {/* the jaw's shadow down the throat: without it the neck is a pasted
          cylinder rather than something under a chin */}
      <path d={`M${-s.neckW * 0.44},${Y.chin - 4} q${s.neckW * 0.44},${10} ${s.neckW * 0.88},0 l0,13 q${-s.neckW * 0.44},${9} ${-s.neckW * 0.88},0 Z`}
            fill={INK} opacity={0.2} />
      <path d={sex === 'f'
        ? spline([[-s.neckW * 0.86, Y.shoulder - 6], [0, Y.shoulder + 30], [s.neckW * 0.86, Y.shoulder - 6],
                  [s.neckW * 1.02, Y.shoulder + 4], [0, Y.shoulder + 44], [-s.neckW * 1.02, Y.shoulder + 4]], true)
        : spline([[-s.neckW * 0.72, Y.shoulder - 2], [0, Y.shoulder + 16], [s.neckW * 0.72, Y.shoulder - 2],
                  [s.neckW * 0.88, Y.shoulder + 8], [0, Y.shoulder + 30], [-s.neckW * 0.88, Y.shoulder + 8]], true)}
            fill={`url(#${uid}_top)`} stroke={INK} strokeWidth={3.6} strokeLinejoin="round" />
      <Limb spine={armSpine(-1)} w={s.armW} fill={`url(#${uid}_skin)`} />
      <Hand at={armSpine(-1)[armSpine(-1).length - 1]} r={s.armW[2] * 0.78} fill={skin} />
      <Hand at={armSpine(1)[armSpine(1).length - 1]} r={s.armW[2] * 0.74} fill={skin} shadow />

      {/* HEAD. Counter-rotated against the weight shift, and lagging it. */}
      <g transform={`translate(${headLag},0) translate(0,${Y.chin - 100}) rotate(${-shTilt * 0.5} 0 100)`}>
        {/* hair BEHIND the skull */}
        <Hair style={hairstyle} s={s} col={hair} back />
        <path d={spline(outline, true, s.headTension)} fill={`url(#${uid}_skin)`}
              stroke={INK} strokeWidth={4.5} strokeLinejoin="round" />
        {/* shadow-side head contour, heavier than the lit side */}
        <path d={spline(outline.slice(0, 9), false, s.headTension)} fill="none"
              stroke={INK} strokeWidth={6} opacity={0.35} strokeLinecap="round" />
        {face()}
        {/* hair OVER the skull and over the near shoulder: the overlap is what
            makes it sit on a head rather than behind one */}
        <Hair style={hairstyle} s={s} col={hair} />
      </g>
    </g>
  );
};

/* ---------- parts ---------------------------------------------------------- */

const Limb: React.FC<{spine: Pt[]; w: readonly number[]; fill: string; shadow?: boolean}> = ({
  spine: sp, w, fill, shadow,
}) => (
  <g opacity={shadow ? 0.82 : 1}>
    <path d={ribbon(sp, w)} fill={fill} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
    {/* CORE SHADOW, hard-edged, along the form's own axis. */}
    <path d={band(sp, w, -1, 0.24, 1)} fill={INK} opacity={0.2} />
    {/* REFLECTED LIGHT outboard of it. Without this the core shadow runs all the
        way to the outline and the limb reads as a flat shape with a dirty edge
        instead of a cylinder turning away. */}
    <path d={band(sp, w, -1, 0.82, 1)} fill="#fff" opacity={0.1} />
    {/* the key-light band on the lit side, kept narrow and off the centre line */}
    <path d={band(sp, w, 1, 0.3, 0.78)} fill="#fff" opacity={0.15} />
    {/* the heavy edge goes on the shadow side only. One extra path per limb, and
        it is the difference between an inked drawing and an outline. */}
    <path d={edge(sp, w, -1, 0.08, 0.94)} fill="none" stroke={INK} strokeWidth={6}
          opacity={0.42} strokeLinecap="round" />
    {shadow && <path d={ribbon(sp, w)} fill={INK} opacity={0.16} />}
  </g>
);

const Hand: React.FC<{at: Pt; r: number; fill: string; shadow?: boolean}> = ({at, r, fill, shadow}) => (
  <g transform={`translate(${at[0]},${at[1] + r * 0.5})`} opacity={shadow ? 0.84 : 1}>
    {/* A hand is a wedge with a thumb, not a disc. A circle at the end of an arm
        is the single most common amateur tell in flat character art. */}
    <path d={spline([[-r, -r * 0.7], [r * 0.85, -r * 0.75], [r * 1.05, r * 0.5],
                     [r * 0.2, r * 1.15], [-r * 0.85, r * 0.6]], true)}
          fill={shadow ? shade(fill, 0.8) : fill} stroke={INK} strokeWidth={3.6} strokeLinejoin="round" />
    <path d={`M${-r * 0.75},${-r * 0.1} q${-r * 0.5},${r * 0.4} ${-r * 0.05},${r * 0.75}`}
          fill="none" stroke={INK} strokeWidth={3.2} strokeLinecap="round" />
    <path d={`M${r * 0.1},${r * 0.1} v${r * 0.7}`} stroke={INK} strokeWidth={1.6} opacity={0.35} />
  </g>
);

const Foot: React.FC<{at: Pt; side: 1 | -1; col: string; heel?: boolean; shadow?: boolean}> = ({
  at, side, col, heel, shadow,
}) => (
  <g transform={`translate(${at[0]},${at[1]})`} opacity={shadow ? 0.85 : 1}>
    {heel ? (
      // A pointed pump on a raised heel, with an ARCHED instep. The arch is the
      // functional part: it is what visually lengthens a leg, which is the whole
      // reason heels read the way they do.
      <g>
        {/* the arched foot: topline at the ankle, vamp sweeping forward and DOWN
            to a pointed toe on the floor, sole running back to the heel seat */}
        <path d={spline([[-13, -8], [-11, 10], [4, 30], [24, 46], [42, 55],
                         [46, 49], [30, 28], [13, 6], [9, -9]], true)}
              fill={shadow ? shade(col, 0.82) : col} stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
        {/* the spike. Thin is the point: a thick heel is a boot. */}
        <path d="M1,38 L-7,57 L-1,58 L9,41 Z" fill={shadow ? shade(col, 0.75) : shade(col, 0.9)}
              stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
        {/* patent highlight down the vamp */}
        <path d="M-4,2 q12,12 22,26" fill="none" stroke="#fff" strokeWidth={3} opacity={0.3} strokeLinecap="round" />
      </g>
    ) : (
      <g>
        <path d={spline([[-17, -2], [-21, 22], [side * 6, 34], [31, 31], [19, 2]], true)}
              fill={shadow ? shade(col, 0.82) : col} stroke={INK} strokeWidth={3.6} strokeLinejoin="round" />
        <path d="M-21,26 q26,9 50,2" fill="none" stroke={INK} strokeWidth={2.2} opacity={0.4} />
      </g>
    )}
  </g>
);

const Hair: React.FC<{style: string; s: Spec; col: string; back?: boolean}> = ({style, s, col, back}) => {
  const w = s.headW / 2;
  if (style === 'short') {
    if (back) return null;
    // A swept crop with a visible PART and a break in the fringe. A hairline
    // drawn as one arc is a swim cap; the break is the whole difference.
    return (
      <g>
        <path d={spline([[-w * 1.06, 30], [-w * 1.12, -6], [-w * 0.5, -26], [w * 0.5, -22],
                         [w * 1.08, 4], [w * 1.06, 32],
                         // the fringe SWEEPS: a peak on the part side, a hard
                         // temple corner on the other. One smooth arc here is
                         // the difference between hair and a swim cap.
                         [w * 0.74, 18], [w * 0.2, 26], [-w * 0.26, 10],
                         [-w * 0.66, 24], [-w * 0.9, 18]], true)}
              fill={col} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
        <path d={spline([[-w * 0.86, 2], [-w * 0.2, -18], [w * 0.6, -10], [w * 0.78, 4],
                         [w * 0.1, -6], [-w * 0.7, 14]], true)} fill="#fff" opacity={0.19} />
        <path d={spline([[-w * 0.98, 20], [-w * 0.3, 2], [w * 0.72, 12], [w * 0.9, 28],
                         [w * 0.1, 16], [-w * 0.86, 34]], true)} fill={INK} opacity={0.2} />
        <path d={spline([[-w * 0.5, 0], [w * 0.2, -6], [w * 0.72, 4]])}
              fill="none" stroke="#fff" strokeWidth={4} opacity={0.24} strokeLinecap="round" />
      </g>
    );
  }
  // LONG. The mass widens ABOVE the cheekbone and pinches in BELOW it, which
  // manufactures the face taper before the jaw is even drawn: the cheapest trick
  // flat design has. It falls well past the shoulder, because LENGTH is the cue,
  // and it never crosses the jawline, because covering the jaw is what made the
  // last version read as a man with long hair.
  if (back) {
    return (
      // The long fall, entirely on ONE side. It clears the far jaw and runs well
      // past the shoulder, because LENGTH is the cue and hair that stops at the
      // jaw reads as a bob.
      <path d={spline([[-w * 1.02, 24], [-w * 1.06, -4], [-w * 0.3, -14], [w * 0.86, -2],
                       [w * 1.3, 44], [w * 1.62, 118], [w * 1.54, 186], [w * 1.16, 206],
                       [w * 0.86, 176], [w * 0.94, 108], [w * 0.72, 54], [w * 0.24, 28]], true)}
            fill={col} stroke={INK} strokeWidth={4.5} strokeLinejoin="round" />
    );
  }
  return (
    <g>
      {/* the near fall, over the shoulder */}
      {/* The crown and the fringe, with a real PART. The near side is TUCKED: it
          comes down only to the cheekbone and stops, so the jawline and the neck
          on that side are completely open. That open side is the whole design. */}
      <path d={spline([[-w * 1.0, 30], [-w * 1.04, 0], [-w * 0.24, -16], [w * 0.8, -6],
                       [w * 1.16, 34], [w * 1.06, 62],
                       [w * 0.72, 30], [w * 0.18, 16], [-w * 0.36, 24], [-w * 0.78, 46]], true)}
            fill={col} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
      {/* specular band across the crown, plus a dark root under it */}
      <path d={spline([[-w * 0.78, 10], [-w * 0.1, -12], [w * 0.72, 0], [w * 0.86, 12],
                       [w * 0.2, 1], [-w * 0.6, 22]], true)} fill="#fff" opacity={0.2} />
      <path d={spline([[-w * 0.95, 26], [-w * 0.2, 8], [w * 0.7, 18], [w * 0.9, 34],
                       [w * 0.1, 22], [-w * 0.82, 40]], true)} fill={INK} opacity={0.22} />
      <path d={spline([[-w * 0.5, -2], [w * 0.2, -10], [w * 0.86, 6]])}
            fill="none" stroke="#fff" strokeWidth={4} opacity={0.28} strokeLinecap="round" />
      {/* the fall: a broad sheen down the lit side of the mass, a dark seam down
          the inner side where it turns away, and lighter tips */}
      <path d={spline([[w * 1.14, 62], [w * 1.34, 118], [w * 1.28, 176], [w * 1.06, 172],
                       [w * 1.14, 116], [w * 0.98, 66]], true)} fill="#fff" opacity={0.16} />
      <path d={spline([[w * 0.9, 74], [w * 0.98, 132], [w * 0.94, 184], [w * 0.82, 176],
                       [w * 0.86, 128], [w * 0.8, 76]], true)} fill={INK} opacity={0.2} />
      <path d={spline([[w * 1.44, 156], [w * 1.5, 186], [w * 1.2, 202], [w * 1.32, 172]], true)}
            fill="#fff" opacity={0.1} />
    </g>
  );
};

const StaticMouth: React.FC<{emotion: Emotion; half: number; mass: number; lip: string; full: boolean}> = ({
  emotion, half, mass, lip, full,
}) => {
  const y = 81;
  const curve = {neutral: 3, angry: -1, worried: -5, shock: 0, smug: 5, flat: 0, squint: 1}[emotion] ?? 0;
  if (emotion === 'shock') {
    return <ellipse cx={0} cy={y + 4} rx={half * 0.5} ry={mass * 1.5} fill="#5e2430" stroke={INK} strokeWidth={2.6} />;
  }
  if (full) {
    // A lip SHAPE, not a line. Lip anthropometry is genuinely inconsistent
    // between populations, so fuller lips here are a convention rather than a
    // finding; the reason to draw them is that they raise eye-and-lip facial
    // contrast, which IS a finding and which flips perceived sex on its own.
    return (
      <g>
        <path d={spline([[-half, y], [-half * 0.4, y - mass * 0.55], [0, y - mass * 0.3],
                         [half * 0.4, y - mass * 0.55], [half, y],
                         [half * 0.45, y + mass * 0.9 + curve * 0.4], [0, y + mass * 1.05 + curve * 0.5],
                         [-half * 0.45, y + mass * 0.9 + curve * 0.4]], true)}
              fill={lip} stroke={INK} strokeWidth={1.8} strokeLinejoin="round" />
        <path d={spline([[-half * 0.9, y + 0.5], [0, y + curve * 0.35], [half * 0.9, y + 0.5]])}
              fill="none" stroke={INK} strokeWidth={1.8} opacity={0.7} />
        <path d={spline([[-half * 0.25, y + mass * 0.72], [half * 0.2, y + mass * 0.72]])}
              fill="none" stroke="#fff" strokeWidth={2} opacity={0.28} strokeLinecap="round" />
      </g>
    );
  }
  return (
    <path d={spline([[-half * 0.85, y], [0, y + curve], [half * 0.85, y - curve * 0.25]])}
          fill="none" stroke={lip} strokeWidth={3.4} strokeLinecap="round" />
  );
};

const TalkingMouth: React.FC<{open: number; spread: number; half: number; lip: string; full: boolean}> = ({
  open, spread, half, lip, full,
}) => {
  // TWO AXES. Openness alone draws the same shape for every sound at a given
  // loudness, which is a hinge flapping at a volume meter; spread (round for
  // oo/oh/w, wide for ee/s/t) is the cheap approximation of a viseme set and is
  // most of what the eye reads at this size.
  const o = Math.max(0, Math.min(1, open));
  const w = half * (0.66 + 0.34 * spread);
  const h = 1.6 + o * 13;
  const y = 81;
  return (
    <g>
      <path d={spline([[-w, y], [-w * 0.45, y - h * 0.34], [0, y - h * 0.42], [w * 0.45, y - h * 0.34],
                       [w, y], [w * 0.5, y + h * 0.8], [0, y + h], [-w * 0.5, y + h * 0.8]], true)}
            fill="#5e2430" stroke={INK} strokeWidth={2.4} strokeLinejoin="round" />
      {o > 0.4 && (
        <path d={spline([[-w * 0.72, y - h * 0.12], [0, y - h * 0.2], [w * 0.72, y - h * 0.12],
                         [w * 0.6, y + h * 0.12], [0, y + h * 0.06], [-w * 0.6, y + h * 0.12]], true)}
              fill="#f3ece0" opacity={0.92} />
      )}
      {full && (
        <path d={spline([[-w * 1.04, y - 1], [0, y - h * 0.5], [w * 1.04, y - 1]])}
              fill="none" stroke={lip} strokeWidth={3.4} strokeLinecap="round" opacity={0.95} />
      )}
    </g>
  );
};

/** Multiply a hex colour's lightness. Keeps a palette to ONE authored value per
 *  garment instead of three that can drift apart. */
function shade(hex: string, k: number): string {
  const n = parseInt(hex.replace('#', ''), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255]
    .map((v) => Math.max(0, Math.min(255, Math.round(v * k))));
  return `#${c.map((v) => v.toString(16).padStart(2, '0')).join('')}`;
}
