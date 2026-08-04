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
  /** How far the head drops toward the shoulders. Chin minus shoulder was 58
   *  units on a 100-unit head; visible neck should be about a quarter of a
   *  head. His drops less: a thick short neck reads powerful, not stumpy. */
  neckDrop: number;
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
    eyeRx: 10.2, eyeRy: 6.3, eyeX: 18, tilt: 7,
    browGap: 9.0, browW: 2.7,        // 0.048 H measured, same correction
    noseHalf: 7.5, mouthHalf: 13.5, lipMass: 6.2,
    jawRatio: 0.72, chinW: 0.2, headTension: 0, neckDrop: 24,
  },
  m: {
    headW: 68, waistY: 302,
    // no flare at the bottom: a V that widens again at the hip reads as a gut.
    shoulder: 211, bust: 194, underbust: 156, waist: 132, upperHip: 142, hip: 145,
    neckW: 45,                       // 0.65 of head width
    armW: [56, 42, 29], legW: [98, 72, 78, 38],
    shoulderJoint: 88, hipJoint: 30,
    eyeRx: 9.2, eyeRy: 3.7, eyeX: 18, tilt: 3,
    browGap: 8.5, browW: 4.4,        // neat and CLEAR of the eye, not a shelf over it
    noseHalf: 8, mouthHalf: 14, lipMass: 4.4,
    jawRatio: 0.8, chinW: 0.30, headTension: 0.04, neckDrop: 16,
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
  /** 'skirt' bares the legs and puts her in heels. 'suit' puts him in a jacket
   *  with lapels, a shirt and a tie, and covers the arms in sleeves. */
  garment?: 'trousers' | 'skirt' | 'suit';
  /** 0..1 per frame from the VO envelope. */
  mouth?: number;
  mouthSpread?: number;
  talking?: boolean;
  idleGain?: number;
  /** OPT-OUT of the moving hold. Deliberately not the default: a rig where
   *  stillness is free keeps producing frozen film. Use only when a shot needs
   *  a genuinely frozen figure as a deliberate effect. */
  still?: boolean;
};

const EYES: Record<Emotion, {open: number; lid: number; brow: number; browTilt: number}> = {
  // `open` scales the fissure, `lid` drops the upper lid over it, `brow` raises
  // the bar, `browTilt` angles it. Narrowing is done with the LID rather than by
  // closing the eye, so a mood never reads as a blink.
  neutral: {open: 1, lid: 0, brow: 0, browTilt: 0},
  angry: {open: 0.92, lid: 0.14, brow: -4.5, browTilt: -17},
  worried: {open: 1.1, lid: -0.1, brow: 3.5, browTilt: 16},
  shock: {open: 1.45, lid: -0.25, brow: 8, browTilt: -6},
  smug: {open: 0.88, lid: 0.28, brow: 1.5, browTilt: -3},
  flat: {open: 0.9, lid: 0.3, brow: 0.5, browTilt: 0},
  squint: {open: 0.8, lid: 0.4, brow: -1.5, browTilt: -11},
};

export const Figure: React.FC<FigureProps> = ({
  frame: f, sex,
  x = 0, y = 0, scale = 1, facing = 1,
  emotion = 'neutral', pose = 'stand', still = false,
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
  /* THE MOVING HOLD. Replaces a 3.4px sway that was the ENTIRE body-movement
     vocabulary of this show and was invisible at 1080 wide. Measured on case
     0003: 59% of the film registered as a held drawing, and the owner watched it
     and said "no character motion, no scene motion, no camera motion".

     Three things make this a moving hold rather than a bigger sine:

     1. INCOMMENSURABLE PERIODS. 2.7s / 3.9s / 6.1s at 30fps. Summed sines whose
        periods share no common multiple never visibly repeat, so the eye cannot
        latch onto a cycle and read it as machinery. One sine at one period is
        what "a computer made this" looks like.
     2. PER-INSTANCE PHASE, derived from x so Ray and Dee are never in lockstep.
        Two figures breathing in unison reads as one puppet with two heads.
     3. AMPLITUDE THAT REGISTERS ON PIXELS. The old 3.4px over a 2.07s period is
        a peak velocity of about 10 px/s. knowledge/MOTION_BIBLE.md derives ~40
        px/s as the floor for ambient motion to read at all on this canvas, so
        the previous idle was roughly four times too slow to be seen even in
        principle. Amplitude alone says nothing; velocity is what is visible.

     `still` exists as an OPT-OUT and is deliberately not the default. A rig
     where stillness is free will keep producing frozen film no matter how many
     gates are added downstream: gates catch the failure, defaults prevent it. */
  const ph = (x * 0.013) % 6.283;            // per-instance, stable across frames
  const g = still ? 0 : idleGain;
  const breathe = Math.sin(f / 34 + ph);
  // The weight shift, now three summed periods instead of one.
  const shift = g * (6.2 * Math.sin(f / 81 + ph)
                   + 2.4 * Math.sin(f / 117 + ph * 1.7)
                   + 1.3 * Math.sin(f / 183 + ph * 0.4));
  // The head LAGS the torso. That lag is the whole difference between a figure
  // that is alive and one that is being translated.
  const headLag = g * (4.1 * Math.sin(f / 81 + ph - 0.55)
                     + 1.6 * Math.sin(f / 117 + ph * 1.7 - 0.4));
  // WHOLE-BODY DRIFT, in screen pixels on the root transform. This is the
  // component that actually moves enough area to register on a frame-difference
  // metric; a blink changes about 0.05% of the frame and never will.
  const driftX = g * (2.9 * Math.sin(f / 97 + ph * 1.3)
                    + 1.1 * Math.sin(f / 151 + ph));
  const driftY = g * (1.8 * Math.sin(f / 113 + ph * 0.8)
                    + 0.9 * Math.sin(f / 179 + ph * 2.1));
  // Blink interval jittered per instance and per cycle so it is not metronomic.
  // Human rate is 15-20/min; the +/-40% variation is what stops a viewer feeling
  // the clock. Never blink on `shock`: the held-open eye IS the expression.
  const blinkPeriod = 96 + Math.floor(26 * Math.sin(f / 401 + ph * 3.1));
  const blink = (f + 17 + Math.floor(ph * 11)) % blinkPeriod < 5
                && emotion !== 'shock';
  // THE THREE-QUARTER CUE. A face dead-on is a passport photo; every reference
  // is turned a little and tilted a little. In a flat rig the turn is a
  // horizontal squeeze of the head plus a shift of the features inside it, so
  // the far cheek compresses. Small on purpose: past about 0.5 the flat
  // features stop selling it and you need a real redraw.
  const headTurn = 0;
  const headTilt = 0;

  /* ---- CONTRAPPOSTO. Weight on the figure's right (screen left when facing 1).
     The hip on the weight side rides UP, the shoulders counter-tilt the other
     way, and the free leg goes slack. Three numbers, and they are most of what
     separates a standing person from a placed figure. */
  const hipTilt = sex === 'f' ? 7.5 : 4.5;
  const shTilt = sex === 'f' ? -5 : -3.2;
  const waistY = s.waistY;
  // S-curve amplitude. Hers is nearly double: the pose SHOWS the curves.
  const sway = sex === 'f' ? 1.9 : 1;

  /* ---- TORSO. A ribbon down an S-curved spine, with the shoulder:waist:hip
     ratios as its widths. The hourglass is not a special case here: it is three
     numbers, and the male V-taper is the same three numbers with no flare at
     the bottom. */
  // THE EIGHT-POINT SPINE. The Spec has carried underbust and upperHip since
  // the curves pass, and a silent string-replace failure meant the spine never
  // grew the points to USE them: the cinch numbers sat dead in the table while
  // the torso interpolated straight from bust to waist to hip. Same lesson as
  // every silent failure in this repo: a replace without an assert is a hope.
  // Curves are RATE OF CHANGE, and rate of change needs points close together.
  const spine: Pt[] = [
    [3.6 * sway + shift * 0.2, Y.shoulder - 2],
    [3.0 * sway + shift * 0.25, Y.shoulder + 6],
    [1.6 * sway + shift * 0.45, Y.chest - 4],      // bust, full
    [-0.4 * sway + shift * 0.7, Y.chest + 38],     // underbust, dropping fast
    [-3.2 * sway + shift, waistY],                 // the cinch
    [0.6 * sway + shift * 0.8, waistY + 32],       // hip flare starts HIGH
    [1.8 * sway + shift * 0.7, Y.hip],
    [2.2 * sway + shift * 0.7, Y.hip + 40],        // past the hip: flat cut hides
  ];
  const torsoW = [s.shoulder * 0.66, s.shoulder, s.bust, s.underbust,
                  s.waist, s.upperHip, s.hip, s.hip * 0.92];

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
    // The free leg travels INBOARD, its ankle crossing past the weight leg's.
    // Hers goes further: the reference poses all cross, and a crossed ankle
    // narrows the base, which is what makes the hips read wide by contrast.
    const cross = sex === 'f' ? 1.9 : 0.5;
    const kneeX = weight ? side * (s.hipJoint + 3)
                         : side * (s.hipJoint - 9 * cross);
    const ankleX = weight ? side * (s.hipJoint + 1)
                          : side * (s.hipJoint - 15 * cross);
    const kneeY = Y.knee + (weight ? 0 : -6);
    return [
      [hipX, Y.hip - 10 + (weight ? -hipTilt : hipTilt)],
      [kneeX, kneeY],
      // calf belly, a third of the way down the shin
      [kneeX + side * (weight ? 3 : 4), kneeY + (Y.ankle - kneeY) * 0.34],
      // In heels the ankle sits well ABOVE the ground and the shoe spans the gap.
      [ankleX, heels ? Y.ankle - 18 : Y.ankle],
    ];
  };

  const headY = Y.chin;   // head group is translated so the CHIN sits at y=0
  const outline = headOutline(s);

  /* ---- FACE ------------------------------------------------------------- */
  const face = () => {
    const eyeY = 50, rx = s.eyeRx, ry = s.eyeRy * E.open;
    const hw = s.headW / 2;
    const sk = (k: number) => warmShade(skin, k);
    const fx = 0;   // features do NOT get their own offset: see headTurn
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
              {/* UPPER LASH LINE, and the reason the old one looked deranged:
                  it was written in +x relative units, so its 3-unit extension
                  and its whole flick landed on the +x end of BOTH eyes. On the
                  right eye that is the outer corner and correct; on the LEFT eye
                  +x is the NOSE, so the lash overshot the inner corner and
                  hooked back around it. One curl, pointing inward, on one eye.
                  Lashes are anatomically OUTBOARD, so everything here is signed
                  by `side`: inner corner -> over the eye -> past the OUTER
                  corner -> flick up and away from the nose. */}
              <path d={`M${cx - side * rx * 0.98},${eyeY - ry * 0.2}
                        Q${cx},${eyeY - ry * 1.55}
                         ${cx + side * (rx + (sex === 'f' ? 3.5 : 1.2))},${eyeY - ry * 0.55}`}
                    fill="none" stroke={INK} strokeLinecap="round"
                    strokeWidth={sex === 'f' ? rx * 0.3 : rx * 0.2} />
              {sex === 'f' && (
                <path d={`M${cx + side * (rx + 1.8)},${eyeY - ry * 0.5}
                          q${side * 3.4},${-1.8} ${side * 5.4},${-4.2}`}
                      fill="none" stroke={INK} strokeWidth={rx * 0.24} strokeLinecap="round" />
              )}
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
      <g transform={`translate(${fx},0)`}>
        <clipPath id={`${uid}_headclip`}><path d={spline(outline, true, s.headTension)} /></clipPath>
        <g clipPath={`url(#${uid}_headclip)`}>
          {/* THE VALUE SYSTEM. Every shape in here is a SOLID darker-or-lighter
              SKIN, never black at low opacity. Reference faces read dimensional
              because their planes are committed value steps in the colour of the
              flesh itself; ink washes read as dirt on paper. The clip lets every
              shape overshoot and still end exactly at the silhouette. */}
          {/* the shadow side of the whole head, one hard-edged plane */}
          <path d={spline([[hw * 0.22, -10], [hw * 0.62, 34], [hw * 0.44, 70],
                           [hw * 0.1, 104], [hw * 3, 104], [hw * 3, -10]], true)}
                fill={sk(0.86)} />
          {/* reflected light where the dark side turns back toward the room */}
          <path d={spline([[hw * 0.88, 6], [hw * 1.02, 52], [hw * 0.7, 92],
                           [hw * 3, 92], [hw * 3, 6]], true)} fill={sk(0.95)} />
          {/* the hair's cast shadow across the forehead */}
          <path d={spline([[-hw * 3, -30], [hw * 3, -30], [hw * 3, 2],
                           [hw * 0.5, 22], [-hw * 0.5, 15], [-hw * 3, 0]], true)}
                fill={sk(0.8)} />
          {/* EYE SOCKETS. The reference eyes read deep-set because they sit IN a
              value, under the brow, instead of lying white on the surface. The
              male socket is deeper; hers stays soft or it reads tired. */}
          {[-1, 1].map((sd) => (
            <g key={sd}>
              {sex === 'm' ? (
                <ellipse cx={sd * s.eyeX} cy={eyeY - 2} rx={rx + 7} ry={ry + 8}
                         fill={sk(0.87)} />
              ) : (
                <>
                  {/* the crease shadow ABOVE the eye only; below it stays LIGHT.
                      Dark under an eye is what tired literally is, and every
                      reference face is bright there. */}
                  <ellipse cx={sd * s.eyeX} cy={eyeY - ry * 0.9} rx={rx + 5} ry={ry * 0.9}
                           fill={sk(0.92)} />
                  <ellipse cx={sd * s.eyeX} cy={eyeY + ry + 3} rx={rx * 0.8} ry={3.4}
                           fill={sk(1.07)} />
                </>
              )}
            </g>
          ))}
          {/* BLUSH. Warmth high on the cheek, outboard of the nose. Its colour is
              the skin pushed toward rose, not a paint dab. */}
          {sex === 'f' && [-1, 1].map((sd) => (
            <ellipse key={sd} cx={sd * hw * 0.52} cy={64} rx={hw * 0.26} ry={7.5}
                     fill="#d9808a" opacity={0.19}
                     transform={`rotate(${sd * -10} ${sd * hw * 0.52} 64)`} />
          ))}
          {/* lit planes: forehead, near cheekbone, chin. Warm light, never white. */}
          <ellipse cx={-hw * 0.18} cy={20} rx={hw * 0.5} ry={13} fill={sk(1.05)} />
          <ellipse cx={-hw * 0.48} cy={54} rx={hw * 0.38} ry={10} fill={sk(1.07)}
                   transform={`rotate(-14 ${-hw * 0.48} 54)`} />
          <ellipse cx={-2} cy={93} rx={hw * 0.2} ry={5.5} fill={sk(1.08)} />
          {/* NOSE, built from value: a side plane, nostril darks, and a light
              down the bridge. No outline; an outlined nose on a value face is
              the detail-density mismatch that tips a face uncanny. */}
          {sex === 'm' ? (
            <>
              <path d={spline([[facing * 2, 46], [facing * 8, 62], [facing * 10.5, 72],
                               [facing * 3, 78], [facing * 0.5, 60]], true)} fill={sk(0.84)} />
              <path d={spline([[facing * -1, 46], [facing * -2.5, 62], [facing * -1, 72]])}
                    fill="none" stroke={sk(1.16)} strokeWidth={3} strokeLinecap="round" />
              <circle cx={-s.noseHalf * 0.38 + facing * 2} cy={73} r={1.5} fill={sk(0.68)} />
              <circle cx={s.noseHalf * 0.38 + facing * 2} cy={73.5} r={1.3} fill={sk(0.68)} />
            </>
          ) : (
            /* A pretty female nose is barely STATED: a short side plane, a dot of
               shadow at each nostril, and nothing else. Nose prominence is the
               fastest way to age or masculinize a face, so the whole feature is
               about a third the value-weight of his. */
            <>
              <path d={spline([[facing * 1.5, 54], [facing * 4, 62], [facing * 5, 68],
                               [facing * 1.5, 70.5], [facing * 0.5, 61]], true)} fill={sk(0.93)} />
              <circle cx={-s.noseHalf * 0.34 + facing * 1.5} cy={69.5} r={1.1} fill={sk(0.74)} />
              <circle cx={s.noseHalf * 0.34 + facing * 1.5} cy={70} r={1.0} fill={sk(0.74)} />
            </>
          )}
          {/* the shelf under the lower lip, in value */}
          <ellipse cx={0} cy={81 + s.lipMass * 1.5} rx={s.mouthHalf * 0.7} ry={3.2}
                   fill={sk(0.87)} />
          {/* STUBBLE. A slightly cool value over the whole jaw and chin. It does
              two jobs: models the jaw as a plane, and is a masculinity cue that
              costs one shape. The plain (unwarmed) shade goes bluish against the
              warm shadows, which is exactly what beard shadow does. */}
          {sex === 'm' && (
            <path d={spline([[-hw * 1.2, 64], [-hw * 0.5, 92], [0, 103], [hw * 0.5, 92],
                             [hw * 1.2, 64], [hw * 1.2, 130], [-hw * 1.2, 130]], true)}
                  fill={shade(skin, 0.88)} opacity={0.75} />
          )}
        </g>
        {/* cheekbone contour: a shade running down and IN under the cheek, with a
            lit plane above it. Only works on a narrowed skull; on a circle the
            same shape reads as a smudge. */}
        {sex === 'm' && (
          <path d={spline([[s.headW / 2 - 2, 48], [s.headW * 0.30, 66], [s.headW * 0.22, 76]])}
                fill="none" stroke={INK} strokeWidth={3} opacity={0.12} strokeLinecap="round" />
        )}
        {[-1, 1].map((sd) => eye(sd as 1 | -1))}
        {/* BROWS. The GAP is the cue, not the bar: a clean 0.048H of skin between
            brow and lid reads instantly at tile scale where a thin arched line
            does not. Female bar is thin and arched with its apex over the outer
            third; male bar is heavy and essentially flat. */}
        {[-1, 1].map((sd) => (
          sex === 'f' ? (
            <path key={sd}
                  d={`M${sd * (s.eyeX - 12)},${browY + 0.5}
                      Q${sd * (s.eyeX - 1)},${browY - 3.2} ${sd * (s.eyeX + 9)},${browY - 2.2}
                      L${sd * (s.eyeX + 13)},${browY - 0.8}
                      Q${sd * (s.eyeX + 1)},${browY - 0.2} ${sd * (s.eyeX - 12)},${browY + 2.4} Z`}
                  fill="#241a18" transform={`rotate(${sd * E.browTilt} ${sd * s.eyeX} ${browY})`} />
          ) : (
            <path key={sd}
                  d={`M${sd * (s.eyeX - 12)},${browY + 1} L${sd * (s.eyeX + 11)},${browY - 0.5}`}
                  fill="none" stroke={INK} strokeWidth={s.browW} strokeLinecap="round"
                  transform={`rotate(${sd * E.browTilt} ${sd * s.eyeX} ${browY})`} />
          )
        ))}
        {/* NOSE. Two marks, never a bridge line. A drawn bridge on an otherwise
            flat face is a detail-density mismatch, and over-defined noses and
            eyelids are the two most-cited causes of a stylized face tipping
            uncanny. */}

        {/* MOUTH */}
        {mouth !== undefined || talking ? (
          <TalkingMouth open={mouth ?? 0} spread={mouthSpread} half={s.mouthHalf}
                        lip={sex === 'f' ? '#a63a55' : INK} full={sex === 'f'} />
        ) : (
          <StaticMouth emotion={emotion} half={s.mouthHalf} mass={s.lipMass}
                       lip={sex === 'f' ? '#a63a55' : INK} full={sex === 'f'} />
        )}
      </g>
    );
  };

  return (
    <g transform={`translate(${x + driftX},${y + driftY}) scale(${scale * facing},${scale})`}>
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
      <Foot at={legSpine(1)[3]} side={1} col={garment === 'skirt' ? (wear.accent ?? INK) : shade(wear.bottom, 0.55)} heel={garment === 'skirt'} shadow />
      <Foot at={legSpine(-1)[3]} side={-1} col={garment === 'skirt' ? (wear.accent ?? INK) : shade(wear.bottom, 0.55)} heel={garment === 'skirt'} />

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
        {garment === 'suit' && (
          <g>
            {/* SHIRT wedge under the opening. Drawn first so the lapels sit on
                top of it, which is the actual layering of a jacket. */}
            <path d={spline([[-s.neckW * 0.56, Y.shoulder], [0, Y.shoulder + 14],
                             [s.neckW * 0.56, Y.shoulder],
                             [8, Y.chest + 56], [-8, Y.chest + 56]], true)}
                  fill="#f0ece2" stroke={INK} strokeWidth={3} strokeLinejoin="round" />
            {/* collar points folding down over the shirt */}
            <path d={`M${-s.neckW * 0.56},${Y.shoulder - 2} l${s.neckW * 0.36},14 l${-s.neckW * 0.5},6 Z`}
                  fill="#f0ece2" stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
            <path d={`M${s.neckW * 0.56},${Y.shoulder - 2} l${-s.neckW * 0.36},14 l${s.neckW * 0.5},6 Z`}
                  fill="#f0ece2" stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
            {/* TIE. The one place the accent colour is allowed to shout, and it
                sits on the centre line so it also reads the figure's lean. */}
            <path d={spline([[-9, Y.shoulder + 18], [9, Y.shoulder + 18], [13, Y.chest + 26],
                             [1, Y.chest + 54], [-12, Y.chest + 26]], true)}
                  fill={wear.accent ?? '#7a2430'} stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
            <path d={spline([[-9, Y.shoulder + 12], [9, Y.shoulder + 12], [7, Y.shoulder + 27],
                             [-7, Y.shoulder + 27]], true)}
                  fill={shade(wear.accent ?? '#7a2430', 0.8)} stroke={INK} strokeWidth={2.4} />
            {/* LAPELS. Notched, asymmetric in weight (the near one catches the
                light, the far one is in shade), and running down to the button
                stance, which is what nips the jacket at the waist. */}
            <path d={spline([[-s.shoulder * 0.34, Y.shoulder + 4], [-s.neckW * 0.52, Y.shoulder + 4],
                             [-10, Y.chest + 50], [-s.bust * 0.22, Y.chest + 34],
                             [-s.shoulder * 0.3, Y.chest - 12]], true)}
                  fill={shade(wear.top, 1.1)} stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
            <path d={spline([[s.shoulder * 0.34, Y.shoulder + 4], [s.neckW * 0.52, Y.shoulder + 4],
                             [10, Y.chest + 50], [s.bust * 0.22, Y.chest + 34],
                             [s.shoulder * 0.3, Y.chest - 12]], true)}
                  fill={shade(wear.top, 0.82)} stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
            {/* button stance and the front edge below it, which is what makes a
                jacket read as CUT rather than as a painted panel */}
            <circle cx={0} cy={Y.chest + 58} r={4.4} fill={shade(wear.top, 0.7)} stroke={INK} strokeWidth={2.4} />
            <path d={spline([[0, Y.chest + 64], [3, waistY + 26], [10, Y.hip + 30]])}
                  fill="none" stroke={INK} strokeWidth={2.8} opacity={0.55} />
            {/* BUILT SHOULDERS. The pad is what makes a jacket read tailored:
                a firm corner WIDER than the arm below it, with the sleeve-head
                seam where the arm is set in. Without it the sleeve and the body
                are one balloon, which is pajamas. */}
            {[-1, 1].map((sd) => (
              <g key={sd}>
                <path d={spline([[sd * s.neckW * 0.9, Y.shoulder - 10],
                                 [sd * s.shoulder * 0.5, Y.shoulder - 8],
                                 [sd * (s.shoulder * 0.5 + 7), Y.shoulder + 14],
                                 [sd * s.shoulder * 0.42, Y.shoulder + 26],
                                 [sd * s.neckW * 1.05, Y.shoulder + 6]], true)}
                      fill={sd < 0 ? shade(wear.top, 1.12) : shade(wear.top, 0.86)}
                      stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
                <path d={spline([[sd * s.shoulder * 0.44, Y.shoulder + 24],
                                 [sd * s.shoulder * 0.47, Y.chest + 4]])}
                      fill="none" stroke={INK} strokeWidth={2.6} opacity={0.5} />
              </g>
            ))}
            {/* pocket welts */}
            <path d={spline([[-s.waist * 0.52, waistY + 16], [-s.waist * 0.16, waistY + 20]])}
                  fill="none" stroke={INK} strokeWidth={3} opacity={0.5} strokeLinecap="round" />
            <path d={spline([[s.waist * 0.18, waistY + 20], [s.waist * 0.54, waistY + 16]])}
                  fill="none" stroke={INK} strokeWidth={3} opacity={0.5} strokeLinecap="round" />
          </g>
        )}
        {sex === 'm' && garment !== 'suit' && (
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
      <path d={ribbon([[2, Y.chin - 6 + s.neckDrop], [1, Y.shoulder + 14]], [s.neckW, s.neckW * 1.18], {capEnd: false})}
            fill={INK} stroke={INK} strokeWidth={17} strokeLinejoin="round" />
      {/* the jaw's shadow down the throat: without it the neck is a pasted
          cylinder rather than something under a chin */}
      <path d={`M${-s.neckW * 0.44},${Y.chin - 4 + s.neckDrop} q${s.neckW * 0.44},${10} ${s.neckW * 0.88},0 l0,13 q${-s.neckW * 0.44},${9} ${-s.neckW * 0.88},0 Z`}
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
      <g transform={`translate(${headLag},0) translate(0,${Y.chin - 100 + s.neckDrop}) rotate(${-shTilt * 0.5 + headTilt} 0 100) translate(${headTurn * 4},0) scale(${1 - Math.abs(headTurn) * 0.1},1)`}>
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
      <Foot at={legSpine(1)[3]} side={1} col={garment === 'skirt' ? (wear.accent ?? INK) : shade(wear.bottom, 0.55)} heel={garment === 'skirt'} shadow />
      <Foot at={legSpine(-1)[3]} side={-1} col={garment === 'skirt' ? (wear.accent ?? INK) : shade(wear.bottom, 0.55)} heel={garment === 'skirt'} />

      {/* FAR ARM behind the torso, near arm in front of it. */}
      <Limb spine={armSpine(1)} w={s.armW} fill={garment === 'suit' ? `url(#${uid}_top)` : `url(#${uid}_skin)`} shadow />

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
        {garment === 'suit' && (
          <g>
            {/* SHIRT wedge under the opening. Drawn first so the lapels sit on
                top of it, which is the actual layering of a jacket. */}
            <path d={spline([[-s.neckW * 0.56, Y.shoulder], [0, Y.shoulder + 14],
                             [s.neckW * 0.56, Y.shoulder],
                             [8, Y.chest + 56], [-8, Y.chest + 56]], true)}
                  fill="#f0ece2" stroke={INK} strokeWidth={3} strokeLinejoin="round" />
            {/* collar points folding down over the shirt */}
            <path d={`M${-s.neckW * 0.56},${Y.shoulder - 2} l${s.neckW * 0.36},14 l${-s.neckW * 0.5},6 Z`}
                  fill="#f0ece2" stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
            <path d={`M${s.neckW * 0.56},${Y.shoulder - 2} l${-s.neckW * 0.36},14 l${s.neckW * 0.5},6 Z`}
                  fill="#f0ece2" stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
            {/* TIE. The one place the accent colour is allowed to shout, and it
                sits on the centre line so it also reads the figure's lean. */}
            <path d={spline([[-9, Y.shoulder + 18], [9, Y.shoulder + 18], [13, Y.chest + 26],
                             [1, Y.chest + 54], [-12, Y.chest + 26]], true)}
                  fill={wear.accent ?? '#7a2430'} stroke={INK} strokeWidth={2.6} strokeLinejoin="round" />
            <path d={spline([[-9, Y.shoulder + 12], [9, Y.shoulder + 12], [7, Y.shoulder + 27],
                             [-7, Y.shoulder + 27]], true)}
                  fill={shade(wear.accent ?? '#7a2430', 0.8)} stroke={INK} strokeWidth={2.4} />
            {/* LAPELS. Notched, asymmetric in weight (the near one catches the
                light, the far one is in shade), and running down to the button
                stance, which is what nips the jacket at the waist. */}
            <path d={spline([[-s.shoulder * 0.34, Y.shoulder + 4], [-s.neckW * 0.52, Y.shoulder + 4],
                             [-10, Y.chest + 50], [-s.bust * 0.22, Y.chest + 34],
                             [-s.shoulder * 0.3, Y.chest - 12]], true)}
                  fill={shade(wear.top, 1.1)} stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
            <path d={spline([[s.shoulder * 0.34, Y.shoulder + 4], [s.neckW * 0.52, Y.shoulder + 4],
                             [10, Y.chest + 50], [s.bust * 0.22, Y.chest + 34],
                             [s.shoulder * 0.3, Y.chest - 12]], true)}
                  fill={shade(wear.top, 0.82)} stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
            {/* button stance and the front edge below it, which is what makes a
                jacket read as CUT rather than as a painted panel */}
            <circle cx={0} cy={Y.chest + 58} r={4.4} fill={shade(wear.top, 0.7)} stroke={INK} strokeWidth={2.4} />
            <path d={spline([[0, Y.chest + 64], [3, waistY + 26], [10, Y.hip + 30]])}
                  fill="none" stroke={INK} strokeWidth={2.8} opacity={0.55} />
            {/* BUILT SHOULDERS. The pad is what makes a jacket read tailored:
                a firm corner WIDER than the arm below it, with the sleeve-head
                seam where the arm is set in. Without it the sleeve and the body
                are one balloon, which is pajamas. */}
            {[-1, 1].map((sd) => (
              <g key={sd}>
                <path d={spline([[sd * s.neckW * 0.9, Y.shoulder - 10],
                                 [sd * s.shoulder * 0.5, Y.shoulder - 8],
                                 [sd * (s.shoulder * 0.5 + 7), Y.shoulder + 14],
                                 [sd * s.shoulder * 0.42, Y.shoulder + 26],
                                 [sd * s.neckW * 1.05, Y.shoulder + 6]], true)}
                      fill={sd < 0 ? shade(wear.top, 1.12) : shade(wear.top, 0.86)}
                      stroke={INK} strokeWidth={3.2} strokeLinejoin="round" />
                <path d={spline([[sd * s.shoulder * 0.44, Y.shoulder + 24],
                                 [sd * s.shoulder * 0.47, Y.chest + 4]])}
                      fill="none" stroke={INK} strokeWidth={2.6} opacity={0.5} />
              </g>
            ))}
            {/* pocket welts */}
            <path d={spline([[-s.waist * 0.52, waistY + 16], [-s.waist * 0.16, waistY + 20]])}
                  fill="none" stroke={INK} strokeWidth={3} opacity={0.5} strokeLinecap="round" />
            <path d={spline([[s.waist * 0.18, waistY + 20], [s.waist * 0.54, waistY + 16]])}
                  fill="none" stroke={INK} strokeWidth={3} opacity={0.5} strokeLinecap="round" />
          </g>
        )}
        {sex === 'm' && garment !== 'suit' && (
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
      <path d={ribbon([[2, Y.chin - 6 + s.neckDrop], [1, Y.shoulder + 14]], [s.neckW, s.neckW * 1.18], {capEnd: false})}
            fill={`url(#${uid}_skin)`} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
      {/* the jaw's shadow down the throat: without it the neck is a pasted
          cylinder rather than something under a chin */}
      <path d={`M${-s.neckW * 0.44},${Y.chin - 4 + s.neckDrop} q${s.neckW * 0.44},${10} ${s.neckW * 0.88},0 l0,13 q${-s.neckW * 0.44},${9} ${-s.neckW * 0.88},0 Z`}
            fill={INK} opacity={0.2} />
      <path d={sex === 'f'
        ? spline([[-s.neckW * 0.86, Y.shoulder - 6], [0, Y.shoulder + 30], [s.neckW * 0.86, Y.shoulder - 6],
                  [s.neckW * 1.02, Y.shoulder + 4], [0, Y.shoulder + 44], [-s.neckW * 1.02, Y.shoulder + 4]], true)
        : spline([[-s.neckW * 0.72, Y.shoulder - 2], [0, Y.shoulder + 16], [s.neckW * 0.72, Y.shoulder - 2],
                  [s.neckW * 0.88, Y.shoulder + 8], [0, Y.shoulder + 30], [-s.neckW * 0.88, Y.shoulder + 8]], true)}
            fill={`url(#${uid}_top)`} stroke={INK} strokeWidth={3.6} strokeLinejoin="round" />
      <Limb spine={armSpine(-1)} w={s.armW} fill={garment === 'suit' ? `url(#${uid}_top)` : `url(#${uid}_skin)`} />
      <Hand at={armSpine(-1)[armSpine(-1).length - 1]} r={s.armW[2] * 0.78} fill={skin} />
      <Hand at={armSpine(1)[armSpine(1).length - 1]} r={s.armW[2] * 0.74} fill={skin} shadow />

      {/* HEAD. Counter-rotated against the weight shift, and lagging it. */}
      <g transform={`translate(${headLag},0) translate(0,${Y.chin - 100 + s.neckDrop}) rotate(${-shTilt * 0.5 + headTilt} 0 100) translate(${headTurn * 4},0) scale(${1 - Math.abs(headTurn) * 0.1},1)`}>
        {/* hair BEHIND the skull */}
        <Hair style={hairstyle} s={s} col={hair} back />
        {/* EARS, under the head fill so only the outer rim shows. A head with no
            ears reads as a mask; every reference face has them even when the
            hair covers one. */}
        {[-1, 1].map((sd) => (
          <g key={sd}>
            <ellipse cx={sd * s.headW * 0.5} cy={56} rx={8} ry={13}
                     fill={skin} stroke={INK} strokeWidth={3.4} />
            <path d={`M${sd * s.headW * 0.5 - sd * 3},52 q${sd * 4},4 ${sd * 2.5},9`}
                  fill="none" stroke={warmShade(skin, 0.78)} strokeWidth={2.6} strokeLinecap="round" />
          </g>
        ))}
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
    {/* thumb */}
    <path d={`M${-r * 0.75},${-r * 0.1} q${-r * 0.5},${r * 0.4} ${-r * 0.05},${r * 0.75}`}
          fill="none" stroke={INK} strokeWidth={3.2} strokeLinecap="round" />
    {/* KNUCKLE LINE, and fingers of DIFFERENT LENGTHS. A mitten becomes a hand
        at exactly these two marks: the knuckles say where the fingers begin,
        and unequal lengths say they are fingers and not a paddle. */}
    <path d={`M${-r * 0.5},${r * 0.12} q${r * 0.55},${-r * 0.22} ${r * 1.1},${r * 0.04}`}
          fill="none" stroke={INK} strokeWidth={2} opacity={0.45} strokeLinecap="round" />
    <path d={`M${-r * 0.2},${r * 0.28} v${r * 0.66}`} stroke={INK} strokeWidth={1.7} opacity={0.4} strokeLinecap="round" />
    <path d={`M${r * 0.24},${r * 0.24} v${r * 0.74}`} stroke={INK} strokeWidth={1.7} opacity={0.4} strokeLinecap="round" />
    <path d={`M${r * 0.66},${r * 0.3} v${r * 0.56}`} stroke={INK} strokeWidth={1.7} opacity={0.4} strokeLinecap="round" />
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
        {/* the pump: an instep sweeping from the raised ankle down to a pointed
            toe ON the ground, with a slim post under the heel seat. The old
            version arched to y58 off a 32-unit lift and drew as a black hook; a
            real pump is mostly FOOT and its hardware is small. */}
        <path d={spline([[-12, -8], [6, -10], [16, 4], [27, 26], [40, 42], [43, 46],
                         [22, 44], [4, 32], [-11, 10]], true)}
              fill={shadow ? shade(col, 0.82) : col} stroke={INK} strokeWidth={3} strokeLinejoin="round" />
        <path d="M-6,28 L-11,46 L-5,47 L1,31 Z" fill={shadow ? shade(col, 0.75) : shade(col, 0.9)}
              stroke={INK} strokeWidth={2.4} strokeLinejoin="round" />
        <path d="M-3,0 q13,14 24,32" fill="none" stroke="#fff" strokeWidth={2.6} opacity={0.3} strokeLinecap="round" />
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
        {/* sweep lines following the part, so the crop reads as combed hair
            rather than a painted cap */}
        {[0, 1, 2].map((i) => (
          <path key={i}
                d={spline([[-w * (0.62 - i * 0.1), 6 + i * 5],
                           [w * (0.1 + i * 0.14), -6 + i * 5],
                           [w * (0.76 - i * 0.06), 8 + i * 6]])}
                fill="none" stroke={i % 2 ? INK : '#fff'} strokeWidth={i % 2 ? 2.6 : 3}
                opacity={i % 2 ? 0.18 : 0.14} strokeLinecap="round" />
        ))}
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
      <path d={spline([[-w * 1.0, 26], [-w * 1.04, 0], [-w * 0.24, -16], [w * 0.8, -6],
                       [w * 1.16, 28], [w * 1.1, 40],
                       [w * 0.78, 22], [w * 0.18, 12], [-w * 0.36, 18], [-w * 0.8, 34]], true)}
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
      {/* STRAND FLOW. A mass with two highlights is a wig. Hair reads as hair
          when the interior is broken into LOCKS that follow the same curve as
          the outer edge and diverge slightly from each other, so the eye can
          trace a path from root to tip. Four locks, alternating light and dark,
          drawn along the fall. */}
      {[0, 1, 2, 3].map((i) => {
        const t = 0.24 + i * 0.2;
        const dark = i % 2 === 1;
        return (
          <path key={i}
                d={spline([[w * (0.92 + t * 0.5), 30 + i * 9],
                           [w * (1.0 + t * 0.52), 90 + i * 7],
                           [w * (0.98 + t * 0.5), 150 + i * 5],
                           [w * (0.86 + t * 0.44), 192 - i * 4]])}
                fill="none" stroke={dark ? INK : '#fff'} strokeWidth={dark ? 4 : 5}
                opacity={dark ? 0.16 : 0.12} strokeLinecap="round" />
        );
      })}
      {/* tip separations: the silhouette breaks into points at the bottom, which
          is what stops the fall reading as a cut sheet of paper */}
      {[0, 1, 2].map((i) => (
        <path key={`t${i}`}
              d={spline([[w * (1.0 + i * 0.16), 178], [w * (1.06 + i * 0.16), 200],
                         [w * (0.94 + i * 0.16), 196]], true)}
              fill={INK} opacity={0.14} />
      ))}
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
        <path d={spline([[-half, y], [-half * 0.45, y - mass * 0.6], [-half * 0.18, y - mass * 0.7],
                         [0, y - mass * 0.42], [half * 0.18, y - mass * 0.7], [half * 0.45, y - mass * 0.6],
                         [half, y],
                         [half * 0.45, y + mass * 0.9 + curve * 0.4], [0, y + mass * 1.05 + curve * 0.5],
                         [-half * 0.45, y + mass * 0.9 + curve * 0.4]], true)}
              fill={lip} stroke={INK} strokeWidth={1.8} strokeLinejoin="round" />
        {/* gloss on the lower lip: the single highlight that makes a lip read
            full instead of painted on */}
        <ellipse cx={half * 0.1} cy={y + mass * 0.62} rx={half * 0.34} ry={mass * 0.24}
                 fill="#fff" opacity={0.4} />
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

/** Shade SKIN the way a painter does: darker AND warmer, because black at low
 *  opacity is not shadow, it is grime. Multiplying all three channels equally
 *  desaturates; pushing red up and blue down as it darkens is what keeps a
 *  shadow looking like flesh turning away from light. Same shift upward for
 *  lights: warm, never white. This one function is most of the difference the
 *  owner named between "coding" and "drawing". */
function warmShade(hex: string, k: number): string {
  const n = parseInt(hex.replace('#', ''), 16);
  const ch = (v: number, f: number) => Math.max(0, Math.min(255, Math.round(v * k * f)));
  const r = ch((n >> 16) & 255, 1.08), g = ch((n >> 8) & 255, 0.97), b = ch(n & 255, 0.86);
  return `#${[r, g, b].map((v) => v.toString(16).padStart(2, '0')).join('')}`;
}

/** Multiply a hex colour's lightness. Keeps a palette to ONE authored value per
 *  garment instead of three that can drift apart. */
function shade(hex: string, k: number): string {
  const n = parseInt(hex.replace('#', ''), 16);
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255]
    .map((v) => Math.max(0, Math.min(255, Math.round(v * k))));
  return `#${c.map((v) => v.toString(16).padStart(2, '0')).join('')}`;
}
