/**
 * brand.tsx — The Big Funny identity, as components.
 *
 * The brand lives in code rather than in a style guide because a style guide is
 * a suggestion and a component is a fact. Every episode composes these, so the
 * show cannot drift by one storyboard deciding the stamp should fade in this
 * time.
 *
 * See knowledge/BRAND_BIBLE.md for the reasoning. The short version: the visual
 * language is the paperwork used against you (manila, carbon, rubber stamps,
 * docket numbers) pointed back at the institution that sent it.
 *
 * Palette is built ON the library's existing tokens, not beside them. INK and
 * HIGHLIGHT are already in Character.tsx and FX.tsx, CARBON is already
 * PaperOfficeBG's dark anchor. A parallel palette would drift within a month.
 */
import React from 'react';
import {interpolate, spring} from 'remotion';

export const INK = '#101423';        // matches Character.tsx
export const MANILA = '#E3D4B0';     // the folder. the show's ground.
export const CARBON = '#4A5A66';     // the Institution. matches PaperOfficeBG.
export const STAMP = '#C0392B';      // used ONCE per episode. see the one-stamp rule.
export const HIGHLIGHT = '#FFE24A';  // matches FX.tsx
export const PAPER = '#F2EADA';

export const BRAND = {INK, MANILA, CARBON, STAMP, HIGHLIGHT, PAPER} as const;

export const PROMISE = "WE DIDN'T MAKE THIS UP. WE HAVE THE FILING.";

const HEAD = 'Arial Black, DejaVu Sans, FreeSans, sans-serif';
const BODY = 'Arial, sans-serif';

/**
 * A rubber stamp landing. NEVER a fade.
 *
 * A stamp is a verdict, and a verdict does not ease in. It overshoots, hits, and
 * settles with a tiny recoil, at a slight rotation that is deliberately not
 * square to the frame, because a perfectly aligned stamp reads as a logo and a
 * crooked one reads as something a person did to a document.
 */
export const Stamp: React.FC<{
  frame: number;          // frames since the stamp fires
  fps?: number;
  children: React.ReactNode;
  rotate?: number;        // degrees, default a deliberate few off square
  color?: string;
  x?: number; y?: number;
  scale?: number;
  /** Ink bleeding into paper is a MULTIPLY, which is right on a light ground and
   *  wrong on a dark one: multiply can only darken, so a pale stamp on a night
   *  frame disappears entirely. An episode set at night passes 'normal' so the
   *  wordmark still reads without having to spend the red token on it. */
  blend?: 'multiply' | 'normal';
}> = ({frame, fps = 30, children, rotate = -7, color = STAMP, x = 0, y = 0, scale = 1,
       blend = 'multiply'}) => {
  const s = spring({frame, fps, config: {damping: 9, mass: 0.55, stiffness: 190}});
  // Overshoot from big to settled: the hit.
  const k = interpolate(s, [0, 1], [2.2, 1]) * scale;
  const opacity = interpolate(frame, [0, 2], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{
      position: 'absolute', left: x, top: y,
      transform: `translate(-50%,-50%) rotate(${rotate}deg) scale(${k})`,
      opacity, color,
      fontFamily: HEAD, letterSpacing: '-0.02em',
      /* Ink bleed: a stamp is never crisp. Two offset shadows in the same hue
         read as ink spreading into paper tooth. */
      textShadow: `0.5px 0.5px 0 ${color}, -0.5px 0.5px 0 ${color}`,
      mixBlendMode: blend,
    }}>{children}</div>
  );
};

/**
 * The wordmark. Stamps once, around 2s, after the hook has already landed.
 *
 * It is NOT at the top of the episode. Branding before the hook is how a
 * short-form video loses the audience, and no brand survives not being watched.
 */
export const Wordmark: React.FC<{
  frame: number; fps?: number; x?: number; y?: number; scale?: number; color?: string;
  blend?: 'multiply' | 'normal';
}> =
({frame, fps = 30, x = 540, y = 960, scale = 1, color = STAMP, blend = 'multiply'}) => (
  <Stamp frame={frame} fps={fps} x={x} y={y} scale={scale} rotate={-6} color={color} blend={blend}>
    <div style={{textAlign: 'center', lineHeight: 0.86}}>
      <div style={{fontSize: 74, letterSpacing: '0.06em'}}>THE BIG</div>
      <div style={{fontSize: 128, letterSpacing: '-0.03em'}}>FUNNY</div>
    </div>
  </Stamp>
);

/**
 * The case number. A serial, not a headline, so it is small and letter-spaced
 * wide. It makes the archive read as a RECORD: case 400 implies 399 before it
 * and implies somebody kept them.
 *
 * Never reused, never skipped, including for killed runs. A gap would be the
 * show lying about its own record on the one axis its credibility sits on.
 */
export const caseNo = (n: number) => `CASE No. ${String(n).padStart(4, '0')}`;

export const CaseNumber: React.FC<{n: number; x?: number; y?: number; color?: string; size?: number}> =
({n, x = 540, y = 120, color = INK, size = 26}) => (
  <div style={{
    position: 'absolute', left: x, top: y, transform: 'translate(-50%,-50%)',
    fontFamily: BODY, fontSize: size, letterSpacing: '0.34em',
    color, opacity: 0.75, whiteSpace: 'nowrap',
  }}>{caseNo(n)}</div>
);

/**
 * The highlighter. ONE per episode, on the single worst number.
 *
 * Hand-drawn, not a rectangle: it overshoots the text on one end and sits at a
 * slight angle, because a marker held by a person does not stop where the word
 * stops. A clean rectangle reads as a UI highlight and kills the whole conceit.
 */
export const Highlighter: React.FC<{
  frame: number; width: number; height?: number;
  x?: number; y?: number; color?: string; durationFrames?: number;
}> = ({frame, width, height = 42, x = 0, y = 0, color = HIGHLIGHT, durationFrames = 8}) => {
  const p = interpolate(frame, [0, durationFrames], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  const over = 14; // the overshoot a real marker leaves
  return (
    <div style={{
      position: 'absolute', left: x - over / 2, top: y,
      width: (width + over) * p, height,
      background: color, opacity: 0.62,
      transform: 'rotate(-1.2deg)',
      borderRadius: 2,
      mixBlendMode: 'multiply',
      transformOrigin: 'left center',
    }} />
  );
};

/**
 * The end card. Case number, the promise, nothing else.
 *
 * No subscribe animation and no end-screen clutter, deliberately. The restraint
 * is the flex, and a show whose whole pitch is "we have the receipt" should not
 * end by begging.
 */
/**
 * `color` exists so an episode can HONOUR the one-stamp rule instead of merely
 * asserting it. Wordmark and EndCard both render through Stamp, which defaults
 * to STAMP red, so an episode that also stamps its receipt was spending the red
 * token three times and halving it twice over. Pass INK here and keep the red
 * for the thing that matters most. The default is unchanged so nothing already
 * shipped moves.
 */
export const EndCard: React.FC<{n: number; frame: number; fps?: number; color?: string}> =
({n, frame, fps = 30, color = STAMP}) => {
  const fade = interpolate(frame, [0, 6], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{
      position: 'absolute', inset: 0, background: MANILA, opacity: fade,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', gap: 26,
    }}>
      <Wordmark frame={frame} fps={fps} x={540} y={860} scale={0.82} color={color} />
      <div style={{
        position: 'absolute', top: 1120, width: '100%', textAlign: 'center',
        fontFamily: BODY, fontSize: 25, letterSpacing: '0.20em',
        color: INK, opacity: 0.8,
      }}>{PROMISE}</div>
      <CaseNumber n={n} y={1230} />
    </div>
  );
};
