/**
 * countroom.tsx — THE COUNT ROOM. Case 0003, tenant screening record assembly.
 *
 * WHY THIS FILE EXISTS, which is the same reason the whole Phase 4.2 exists.
 *
 * The art library was ported from an Alaska show. It is a shelf of parkas, snow,
 * spruce and boreal night, and `ASSET_MANIFEST.md` says to cast from the shelf
 * before drawing anything new. That is a good rule that was doing enormous
 * damage: the shelf is a PLACE and the stories are national, so every board cast
 * an Alaska set for a story that had nothing to do with Alaska, the set
 * therefore could not illustrate anything, and once the set is inert the only
 * thing left for an episode to do is HAVE TWO PEOPLE TALK.
 *
 * "Two people talking and doing nothing" was never a staging failure. It is what
 * is left over after the world has been amputated from the story.
 *
 * So: THE WORLD OF THE STORY BECOMES THE SET. This is the inside of the machine
 * that ASSEMBLES a tenant screening report. Not the office that sells it, not
 * the counter where you dispute it. The face of the assembler, with its intake,
 * its count and BOTH of its outputs in one frame, so the whole allegation is one
 * image and the film never travels.
 *
 * ================= THE INSTITUTION IS A WALL HERE, AND WHY =================
 *
 * `kit.MachineShadow` is the show's standing Institution and CAST_BIBLE says
 * "same silhouette, new livery". This case deviates, on a director's ruling
 * recorded in out/dispatch/storyboard.json, and the reason is better than the
 * one the fallback existed for:
 *
 *   A tower standing behind the intake puts something BEHIND the process, and
 *   this case's thesis is that nothing is. A tapered tower reads as a BODY, and
 *   an eye looks for a face on a body. MachineShadow's antenna array is a
 *   broadcast affordance this story does not have.
 *
 * The deviation is bound rather than free: this wall is authored to
 * MachineShadow's tone triple, so it is the same MATERIAL in a different form,
 * and it inherits the one rule that never bends.
 *
 * **NO FACE. NOT EVER.** No aperture is paired, symmetric about centre, or
 * placed above the odometer boss. Give the Institution an expression and it
 * becomes something you could negotiate with, and the premise dies.
 *
 * ============================= THE SIZE LAW ===============================
 *
 * Ray's crown sits at 0.72 of a DocketCard's long edge, so ONE COURT CASE IS
 * 1.39x A MAN. WORLD_KIT calls this "cast normal, world enormous around them:
 * use it when the point is that they are outnumbered." At working scale a person
 * is bigger than the thing they handle and reads as an employee of the
 * mechanism. Here he is shorter than one court case.
 *
 * The conceit is invisible unless one true-human-size object shares a frame with
 * a card, which is what Dee's letter-size dispute form is for in S5. That is
 * also the document c6 and c7 are about, so the size reference is a story beat
 * rather than a prop tax. Do not cut it for pace.
 */
import React from 'react';
import {INK, tones, RimLight, ContactShadow} from './lighting';

// ===========================================================================
// THE PALETTE. Enamel teal and brass, from out/dispatch/world.json.
//
// The teal family is authored as a value LADDER, not as three teals that happen
// to look nice: `key` to `fill` to `shade` is a real lightness descent, so the
// wall has form under one light source instead of being a flat teal rectangle
// with lines on it. INK is the show's black and is shared with brand.tsx.
// ===========================================================================
export const COUNTROOM = {
  key: '#3E8F8C',        // lit enamel, only where the practical reaches
  fill: '#1F5E5E',       // the body of the wall
  shade: '#123C3E',      // the turn away from the light
  ink: '#101423',        // outline and the crushed floor
  brass: '#A8763E',      // every joint, every lip, the odometer boss
  brassLo: '#7C5628',
  brassHi: '#D9A868',
  card: '#E8E2D4',       // DocketCard face. paper.PAPER.front, deliberately the
                         // same cream, because the paper is the only bright
                         // value in the room and it has to stay the show's.
  cardEdge: '#BBAF96',   // the extruded slab edge
  cardShade: '#9C917B',
} as const;

/**
 * FIT TEXT TO ITS BOX. The general fix for a defect the proof sheet found twice
 * in one render: "EVICTION ACTION" ran past the card's right edge and the
 * filing's caption ran past the plate's.
 *
 * Both had the same cause, and it is the kind that recurs forever if you fix it
 * with a tuned number. The font size was a fraction of the CONTAINER and never a
 * function of the STRING, so it is correct for whatever text happened to be
 * there when somebody eyeballed it and wrong for the next string. A case number
 * one character longer, an institution with a longer name, and it spills.
 *
 * THE EM CONSTANT IS MEASURED, AND IT WAS WRONG ONCE ALREADY. The first value
 * was 0.44, taken from Barlow Condensed's real metrics, and the button still
 * overflowed: "UNITED STATES v. RENTGROW, INC." ran off the plate. The reason is
 * that BARLOW CONDENSED IS NOT INSTALLED IN THE RENDER CONTAINER, so every
 * `fontFamily: 'Barlow Condensed, Impact, sans-serif'` in this repo falls back
 * to a NON-CONDENSED sans, whose glyphs are about 40% wider.
 *
 * So the number that matters is not the font we asked for, it is the font that
 * renders. 0.62 em per character, measured off the overflowing frame: 30
 * characters at 56px filled just over 1000px.
 *
 * If a condensed face is ever actually installed, this becomes conservative
 * rather than wrong, which is the correct direction for a fitting constant to
 * fail in.
 */
export const fitText = (text: string, boxW: number, designSize: number, em = 0.62) =>
  Math.min(designSize, boxW / Math.max(1, text.length * em));

/** The card is 2:1, plywood-proportioned. One number, everywhere. */
export const CARD_ASPECT = 0.5;

/**
 * Ray's crown over a card's long edge. The director's board is cut to this and
 * the legibility gate measures against it, so it is exported rather than
 * repeated: a scene that wants a different scale is describing a different film.
 */
export const CAST_TO_CARD = 0.72;

// ---------------------------------------------------------------------------
// A note on ids. Every def below is keyed per INSTANCE with React.useId, never
// per position. `msLit-${x}-${y}` style ids meant two instances at the same
// coordinates shared a definition and the second silently took the first's,
// which is the ghost-parka bug and it was live in ten components until
// 2026-08-02. Position is not identity. See ASSET_MANIFEST.
// ---------------------------------------------------------------------------

// ===========================================================================
// DocketCard — THE COURT CASE AS FURNITURE.
//
// Drawn as a SLAB and not as a sheet. `paper.Sheet` is the right component for
// paper at paper size and the wrong one here: its drop shadow is proportional
// now, but a shadow is not an EDGE, and at 2.44m the thing has thickness you can
// see. A giant sheet with a soft shadow reads as a flat rectangle, which is
// exactly the note the funny critic gave about a pile that looked like "a lot of
// paperwork" instead of the same case again.
//
// EXACTLY TWO LEGIBLE STRINGS, at fixed cap heights and fixed positions, over
// ruled noise. That is the whole design. The legibility gate's STILL A asks
// whether a pile reads as SAME or merely as MANY, and the only thing that can
// answer it is one string appearing at the same offset in card after card. Add a
// third string and the eye starts reading documents instead of repetition.
// ===========================================================================
export const DocketCard: React.FC<{
  x: number; y: number;
  /** Long edge in px. Height follows from CARD_ASPECT. */
  w: number;
  rot?: number;
  head?: string;
  caseNo?: string;
  /** Swaps ONE word at ONE fixed position, so two cards differ in one place. */
  differs?: string;
  /** Slab depth as a fraction of w. The visible extrusion. */
  thickness?: number;
  /** 0..1 how much of the practical reaches this card. */
  light?: number;
}> = ({
  x, y, w, rot = 0, head = 'EVICTION ACTION', caseNo = 'C-2026-4417',
  differs, thickness = 0.018, light = 1,
}) => {
  const uid = `dc${React.useId().replace(/:/g, '')}`;
  const h = w * CARD_ASPECT;
  const d = w * thickness;
  const L = Math.max(0, Math.min(1, light));
  const face = tones(COUNTROOM.card);

  // Cap heights are FRACTIONS OF THE CARD, never px, so the gate's "within 15%
  // of each other in glyph height" holds for two cards at two depths without
  // anybody hand-tuning a font size per shot.
  const headCap = h * 0.115;
  const noCap = h * 0.155;

  return (
    <g transform={`translate(${x},${y}) rotate(${rot})`}>
      <defs>
        <linearGradient id={`${uid}f`} x1="0" y1="0" x2="0.35" y2="1">
          <stop offset="0%" stopColor={face.key} />
          <stop offset="62%" stopColor={COUNTROOM.card} />
          <stop offset="100%" stopColor={face.core} />
        </linearGradient>
      </defs>

      {/* THE EXTRUSION, drawn before the face so the face laps over it. Two
          planes and not one: a bottom edge catching nothing and a right edge
          catching a little, which is what makes it a slab rather than a card
          with a border. */}
      <path d={`M0,${h} L${d},${h + d} L${w + d},${h + d} L${w},${h} Z`}
            fill={COUNTROOM.cardShade} stroke={INK} strokeWidth={w * 0.004} strokeLinejoin="round" />
      <path d={`M${w},0 L${w + d},${d} L${w + d},${h + d} L${w},${h} Z`}
            fill={COUNTROOM.cardEdge} stroke={INK} strokeWidth={w * 0.004} strokeLinejoin="round" />

      {/* The face. */}
      <rect x={0} y={0} width={w} height={h} fill={`url(#${uid}f)`}
            stroke={INK} strokeWidth={w * 0.005} />

      {/* Ruled noise. Everything that is NOT one of the two strings is texture,
          because a card covered in readable text is a document and the joke
          needs it to be a unit. */}
      <g opacity={0.5 * (0.55 + 0.45 * L)}>
        {[0.40, 0.47, 0.54, 0.68, 0.75, 0.82, 0.89].map((fy, i) => (
          <rect key={i} x={w * 0.07} y={h * fy}
                width={w * (i % 3 === 2 ? 0.42 : i % 3 === 1 ? 0.71 : 0.83)}
                height={h * 0.022} fill={COUNTROOM.cardShade} />
        ))}
      </g>

      {/* STRING ONE: the head line. FITTED, never merely scaled. */}
      <text x={w * 0.07} y={h * 0.17}
            fontSize={fitText(head, w * 0.86, headCap / 0.7)} fontWeight={800}
            fill={INK} letterSpacing={w * 0.003}
            style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
        {head}
      </text>

      {/* STRING TWO: the case number. THE one that has to repeat. It is set
          larger than the head line on purpose: it is the string the eye is being
          asked to match card to card, and the gate wants it at 22% or more of
          the long edge. */}
      <text x={w * 0.07} y={h * 0.325}
            fontSize={fitText(caseNo, w * 0.86, noCap / 0.7)} fontWeight={900}
            fill={INK} letterSpacing={w * 0.006}
            style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
        {caseNo}
      </text>

      {/* THE ONE WORD THAT MAY DIFFER, at ONE fixed x on ONE fixed line. Two
          cards laid side by side differ in exactly this spot and nowhere else,
          which is what makes S16's overhead readable in under a second without a
          line asking the viewer to compare. */}
      {differs && (
        <text x={w * 0.07} y={h * 0.94}
              fontSize={fitText(differs, w * 0.5, (h * 0.135) / 0.7)} fontWeight={900}
              fill={INK} letterSpacing={w * 0.005}
              style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
          {differs}
        </text>
      )}

      {/* Only where the light reaches. */}
      {L > 0.02 && (
        <RimLight d={`M0,0 L${w},0`} w={w * 0.006} color="#FFF6E2" opacity={0.5 * L} />
      )}
    </g>
  );
};

/**
 * CardPile — THE ANSWER TO STILL A, and the reason it is a component.
 *
 * The first proof render stacked three cards at an 11px offset and produced ONE
 * card with a thick edge, carrying exactly one case number. The legibility gate
 * wants at least TWO case numbers visible simultaneously, because that is the
 * only way a viewer can tell SAME from MANY, and SAME is the entire thesis: the
 * machine copied one court case, it did not find several.
 *
 * The resolution is that FLUSH and READABLE are two different shots, not a
 * contradiction to be split the difference on:
 *
 *   `flush` (the turn, S4) is the gag. Cards land edge-exact so the picture on
 *   the floor does not change at all, and the only thing that moves in frame is
 *   the height of the man standing on it.
 *
 *   `stacked` (the establishing image, and STILL A) offsets each card by enough
 *   to expose the PRINTED BAND of the one beneath, so the same string appears
 *   again and again down the pile at the same offset within each card. Eight
 *   repetitions of one string is a pattern. Eight different documents is a mess.
 *   The eye can tell those apart instantly and no caption is needed.
 *
 * `reveal` is the fraction of a card's height that the next one leaves showing.
 * Below about 0.34 the case number is clipped and the pile silently goes back to
 * failing the gate, so it is floored rather than trusted to a caller.
 */
export const CardPile: React.FC<{
  x: number; y: number; w: number;
  count?: number;
  mode?: 'flush' | 'stacked';
  head?: string;
  caseNo?: string;
  /** Fraction of card height left showing. Floored at the legible minimum. */
  reveal?: number;
  light?: number;
}> = ({
  x, y, w, count = 3, mode = 'stacked',
  head = 'EVICTION ACTION', caseNo = 'C-2026-4417', reveal = 0.42, light = 0.9,
}) => {
  const h = w * CARD_ASPECT;
  // The printed band runs to 0.34 of the card height. Anything tighter clips the
  // case number, which is the one string the whole gate is about.
  const step = mode === 'flush' ? w * 0.018 : h * Math.max(0.36, reveal);
  return (
    <g>
      {/* Bottom card first, so each one laps over the one beneath and the pile
          reads as a stack rather than as a fan. */}
      {Array.from({length: count}).map((_, i) => {
        const k = count - 1 - i;
        return (
          <DocketCard
            key={k}
            x={x}
            y={y - k * step}
            w={w}
            head={head}
            caseNo={caseNo}
            light={Math.max(0.35, light - k * 0.06)}
          />
        );
      })}
    </g>
  );
};

// ===========================================================================
// CardChute — ONE component, TWO states, and that is the point.
//
// `running` cams a card out and lets it fall. `plated` bolts a cover over THE
// SAME MOUTH and emits nothing. They have to be one component with one geometry,
// because S15's reveal is that the dead chute is visibly the same machine as the
// working one. Two separate components would let them drift, and the drift would
// quietly delete the reveal.
// ===========================================================================
export const CardChute: React.FC<{
  f: number; x: number; y: number; w: number;
  state?: 'running' | 'plated';
  /** 0..1 through one ejection cycle. Only read when state is 'running'. */
  emit?: number;
  /** 0..1 fasteners dropped and cover falling. Only read when 'plated'. */
  open?: number;
}> = ({f, x, y, w, state = 'running', emit = 0, open = 0}) => {
  const uid = `cc${React.useId().replace(/:/g, '')}`;
  const h = w * 0.42;
  const e = Math.max(0, Math.min(1, emit));
  const o = Math.max(0, Math.min(1, open));
  const tB = tones(COUNTROOM.brass);

  return (
    <g transform={`translate(${x},${y})`}>
      <defs>
        <linearGradient id={`${uid}l`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={COUNTROOM.brassHi} />
          <stop offset="55%" stopColor={COUNTROOM.brass} />
          <stop offset="100%" stopColor={COUNTROOM.brassLo} />
        </linearGradient>
      </defs>

      {/* The recess, always the darkest thing in its neighbourhood. */}
      <rect x={0} y={0} width={w} height={h} rx={h * 0.06}
            fill={COUNTROOM.ink} stroke={INK} strokeWidth={w * 0.012} />

      {/* The rubber curtain. It hangs, and when a card comes through it lifts
          and drops back. Nothing else in the room is soft. */}
      <path
        d={`M${w * 0.08},${h * 0.18}
            Q${w * 0.5},${h * (0.18 + 0.52 * (1 - 0.55 * (e > 0.15 && e < 0.6 ? 1 : 0)))}
             ${w * 0.92},${h * 0.18}
            L${w * 0.92},${h * 0.1} L${w * 0.08},${h * 0.1} Z`}
        fill="#0C1018" stroke={INK} strokeWidth={w * 0.008} strokeLinejoin="round"
      />

      {/* THE BRASS LIP. The one bright joint, and the thing the eye tracks. */}
      <path d={`M${-w * 0.03},${h} L${w * 1.03},${h} L${w * 1.0},${h * 1.13} L${0},${h * 1.13} Z`}
            fill={`url(#${uid}l)`} stroke={INK} strokeWidth={w * 0.014} strokeLinejoin="round" />

      {state === 'running' && e > 0.02 && (
        // The card on its way out, clipped by the mouth so it emerges rather
        // than appearing. The cam pushes it, it tips past the lip, it falls.
        <g clipPath={`url(#${uid}clip)`}>
          <defs>
            <clipPath id={`${uid}clip`}>
              <rect x={-w * 0.6} y={h * 0.1} width={w * 2.2} height={h * 3.4} />
            </clipPath>
          </defs>
          <g transform={`translate(${w * 0.08},${h * (0.28 + 0.5 * e)}) rotate(${6 * e})`}>
            <DocketCard x={0} y={0} w={w * 0.84} light={0.9} />
          </g>
        </g>
      )}

      {state === 'plated' && (
        <>
          {/* THE COVER. The darkest value in the frame, bolted over a mouth that
              is visibly the same mouth. It has been shut since before the film
              started, which is why nobody is looking at it. */}
          <g transform={`translate(0,${o * h * 2.6}) rotate(${o * 14},${w * 0.5},${h * 0.5})`}
             opacity={o > 0.9 ? 0 : 1}>
            <rect x={-w * 0.04} y={-h * 0.08} width={w * 1.08} height={h * 1.24} rx={h * 0.05}
                  fill="#0A0D14" stroke={INK} strokeWidth={w * 0.016} />
            {[0.12, 0.88].map((fx, i) => (
              <g key={i} opacity={o > 0.05 ? 0 : 1}>
                <circle cx={w * fx} cy={h * 0.12} r={w * 0.026} fill={COUNTROOM.brassLo}
                        stroke={INK} strokeWidth={w * 0.009} />
                <circle cx={w * fx} cy={h * 1.06} r={w * 0.026} fill={COUNTROOM.brassLo}
                        stroke={INK} strokeWidth={w * 0.009} />
              </g>
            ))}
          </g>
          {/* The fasteners, after they have dropped. */}
          {o > 0.05 && [0.16, 0.5, 0.84].map((fx, i) => (
            <circle key={i} cx={w * fx} cy={h * (1.3 + 1.9 * Math.min(1, o * 1.6))}
                    r={w * 0.022} fill={COUNTROOM.brassLo} stroke={INK} strokeWidth={w * 0.008} />
          ))}
        </>
      )}
    </g>
  );
};

// ===========================================================================
// VerifyDie — the brass die that embosses VERIFIED on a copy.
//
// Not in the designer's asset list. Added by the director for S11, which is the
// PUNCHLINE shot: the machine congratulating itself for being right about every
// single copy, while in the same frame the intake still holds the one original.
//
// It is a die and not a stamp on purpose. A stamp puts ink ON something, which
// reads as annotation; a die presses INTO it, which reads as manufacture. The
// machine is not commenting on the card, it is finishing it.
// ===========================================================================
export const VerifyDie: React.FC<{
  x: number; y: number; w: number;
  /** 0..1. Drops, presses, lifts. The emboss it leaves does not lift. */
  press?: number;
  label?: string;
}> = ({x, y, w, press = 0, label = 'VERIFIED'}) => {
  const uid = `vd${React.useId().replace(/:/g, '')}`;
  const p = Math.max(0, Math.min(1, press));
  // Down fast, hold, up slow. A die that rises as fast as it falls reads as a
  // bounce, and this thing is not playful.
  const drop = p < 0.35 ? (p / 0.35) : p < 0.6 ? 1 : 1 - (p - 0.6) / 0.4;
  const h = w * 0.62;

  return (
    <g transform={`translate(${x},${y})`}>
      <defs>
        <linearGradient id={`${uid}b`} x1="0" y1="0" x2="0.3" y2="1">
          <stop offset="0%" stopColor={COUNTROOM.brassHi} />
          <stop offset="50%" stopColor={COUNTROOM.brass} />
          <stop offset="100%" stopColor={COUNTROOM.brassLo} />
        </linearGradient>
      </defs>
      {/* THE EMBOSS, which stays. It does not fade, because nothing in this room
          is ever corrected.
          
          IT SITS BELOW THE DIE'S TRAVEL, which the first proof render got wrong:
          the emboss was centred under the die face, so at press the block landed
          on top of it and VERIFIED rendered as "VI....D". A die that hides its
          own impression is a brass rectangle. The impression is offset clear of
          the block and the type is FITTED, so a longer label cannot spill. */}
      {p > 0.3 && (
        <g opacity={Math.min(1, (p - 0.3) * 5)}
           transform={`translate(${w * 1.22},${h * 1.02})`}>
          <text x={0} y={2} fontSize={fitText(label, w * 1.5, w * 0.3)} fontWeight={900}
                fill={COUNTROOM.cardShade} letterSpacing={w * 0.012}
                style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
            {label}
          </text>
          <text x={0} y={0} fontSize={fitText(label, w * 1.5, w * 0.3)} fontWeight={900}
                fill="#FFFDF6" opacity={0.72} letterSpacing={w * 0.012}
                style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
            {label}
          </text>
        </g>
      )}
      {/* The die itself: a shank and a face, no decoration. */}
      <g transform={`translate(0,${drop * h * 1.05})`}>
        <rect x={w * 0.33} y={-h * 0.9} width={w * 0.34} height={h * 0.92}
              fill={COUNTROOM.brassLo} stroke={INK} strokeWidth={w * 0.03} />
        <rect x={0} y={0} width={w} height={h} rx={w * 0.03}
              fill={`url(#${uid}b)`} stroke={INK} strokeWidth={w * 0.035} strokeLinejoin="round" />
        <rect x={w * 0.1} y={h * 0.72} width={w * 0.8} height={h * 0.16}
              fill={COUNTROOM.brassLo} opacity={0.8} />
      </g>
    </g>
  );
};

// ===========================================================================
// CountRoomBG — THE INSTITUTION AS A WALL.
//
// Full bleed, parallel to camera, teal enamel with brass at every joint. Four
// tiled steps to a lit intake at upper left, the odometer boss at centre, a
// hinged panel on the right flank whose HINGES ARE PAINTED OVER, a working chute
// at lower centre and a plated dead chute at the lower right EDGE, half out of
// frame, from second five, so S15's reveal pays off an absence the viewer has
// been looking past for thirty-eight seconds.
//
// ONE registered practical, over the intake. Everything else falls to black. A
// second light source would make this a room, and it is not a room, it is the
// front of a machine.
// ===========================================================================
export const CountRoomBG: React.FC<{
  f: number;
  w?: number; h?: number;
  /** 0..1 the practical over the intake. */
  light?: number;
  /** 0..1 how far the pile has buried the tiled floor. */
  pile?: number;
  /** 0..1 a card being drawn into the intake. */
  intake?: number;
  /** 0..1 Dee pulling the panel that does not open. It never exceeds a shudder. */
  panel?: number;
}> = ({f, w = 1080, h = 1920, light = 1, pile = 0, intake = 0, panel = 0}) => {
  const uid = `cr${React.useId().replace(/:/g, '')}`;
  const L = Math.max(0, Math.min(1, light));
  const P = Math.max(0, Math.min(1, pile));
  const pull = Math.max(0, Math.min(1, panel));
  // The panel gives about a millimetre and stops. It is not locked; it is
  // painted shut, and the difference is the whole gag.
  const give = Math.sin(pull * Math.PI) * w * 0.004;

  const floorY = h * 0.78;
  const stepW = w * 0.34;
  const stepH = h * 0.038;

  return (
    <g>
      <defs>
        {/* The wall's form: lit near the practical, falling away everywhere
            else. This is one gradient doing the job a second light would
            otherwise be brought in to do. */}
        <radialGradient id={`${uid}w`} cx="0.26" cy="0.19" r="0.95">
          <stop offset="0%" stopColor={COUNTROOM.key} stopOpacity={0.95 * L} />
          <stop offset="42%" stopColor={COUNTROOM.fill} />
          <stop offset="100%" stopColor={COUNTROOM.shade} />
        </radialGradient>
        <linearGradient id={`${uid}b`} x1="0" y1="0" x2="0.4" y2="1">
          <stop offset="0%" stopColor={COUNTROOM.brassHi} />
          <stop offset="50%" stopColor={COUNTROOM.brass} />
          <stop offset="100%" stopColor={COUNTROOM.brassLo} />
        </linearGradient>
      </defs>

      {/* THE WALL. */}
      <rect x={0} y={0} width={w} height={floorY} fill={`url(#${uid}w)`} />

      {/* Enamel panel joints. Brass at every one, because the brass is what
          makes it manufactured rather than architectural. */}
      {[0.17, 0.34, 0.51, 0.68].map((fy, i) => (
        <rect key={i} x={0} y={floorY * fy} width={w} height={h * 0.0045}
              fill={COUNTROOM.brassLo} opacity={0.55} />
      ))}
      {[0.29, 0.71].map((fx, i) => (
        <rect key={i} x={w * fx} y={0} width={w * 0.004} height={floorY}
              fill={COUNTROOM.brassLo} opacity={0.4} />
      ))}

      {/* FOUR TILED STEPS, upper left, rising to the intake. They are the only
          thing in the room a person can climb, and S13 is Ray at the top of them
          with the slot still slightly too high for him. */}
      {[0, 1, 2, 3].map((i) => (
        <g key={i}>
          <rect x={0} y={h * 0.30 - i * stepH} width={stepW - i * (stepW * 0.06)}
                height={stepH} fill={i % 2 ? COUNTROOM.fill : COUNTROOM.shade}
                stroke={INK} strokeWidth={w * 0.003} />
          <rect x={0} y={h * 0.30 - i * stepH} width={stepW - i * (stepW * 0.06)}
                height={h * 0.003} fill={COUNTROOM.brassLo} opacity={0.7} />
        </g>
      ))}

      {/* THE INTAKE, at the top of the steps, under the one practical. It is a
          SLOT: horizontal, off-centre, and single. Nothing about it is paired or
          symmetric, because a pair of anything at this height on a wall is a set
          of eyes and the Institution never gets a face. */}
      <g transform={`translate(${w * 0.055},${h * 0.185})`}>
        <rect x={-w * 0.012} y={-h * 0.012} width={w * 0.234} height={h * 0.05} rx={h * 0.006}
              fill={`url(#${uid}b)`} stroke={INK} strokeWidth={w * 0.006} />
        <rect x={0} y={0} width={w * 0.21} height={h * 0.026} rx={h * 0.004}
              fill="#080B12" stroke={INK} strokeWidth={w * 0.005} />
        {/* the card going in */}
        {intake > 0.02 && (
          <rect x={w * 0.012 + w * 0.17 * (1 - intake)} y={h * 0.004}
                width={w * 0.055} height={h * 0.018} fill={COUNTROOM.card}
                opacity={0.85} stroke={INK} strokeWidth={w * 0.002} />
        )}
        {/* THE PRACTICAL. One source, registered here, breathing very slightly
            so the room is never perfectly static. */}
        <ellipse cx={w * 0.105} cy={-h * 0.03} rx={w * 0.17 * L} ry={h * 0.055 * L}
                 fill="#FFE9B8" opacity={0.16 * L * (0.95 + 0.05 * Math.sin(f / 23))} />
      </g>

      {/* THE ODOMETER BOSS, dead centre. The mount only; props.TallyCounter is
          cast into it by the scene, because the count is a PROP that changes and
          this file draws the machine it is bolted to. */}
      <g transform={`translate(${w * 0.5},${h * 0.42})`}>
        <circle r={w * 0.115} fill={`url(#${uid}b)`} stroke={INK} strokeWidth={w * 0.009} />
        <circle r={w * 0.093} fill={COUNTROOM.shade} stroke={INK} strokeWidth={w * 0.006} />
        {Array.from({length: 8}).map((_, i) => {
          const a = (Math.PI * 2 * i) / 8;
          return <circle key={i} cx={Math.cos(a) * w * 0.104} cy={Math.sin(a) * w * 0.104}
                         r={w * 0.008} fill={COUNTROOM.brassLo} stroke={INK}
                         strokeWidth={w * 0.003} />;
        })}
      </g>

      {/* THE PANEL THAT WILL NOT OPEN, right flank. A sensible height, a real
          handle, visible hinges, and NO keyhole, NO lock, NO sign and NO notice.
          It is not locked. The hinges have been painted over in the same teal and
          the brush stroke runs unbroken across the knuckle, which is proof the
          door has not opened since. That is meaner than a sign, because there is
          nobody to appeal a paint job to. */}
      <g transform={`translate(${w * 0.755},${h * 0.47})`}>
        <rect x={give} y={0} width={w * 0.19} height={h * 0.14} rx={w * 0.004}
              fill={COUNTROOM.fill} stroke={INK} strokeWidth={w * 0.005} />
        {/* hinges, and the brush stroke straight across both knuckles */}
        {[0.2, 0.8].map((fy, i) => (
          <g key={i}>
            <rect x={give - w * 0.008} y={h * 0.14 * fy - h * 0.012}
                  width={w * 0.018} height={h * 0.024} rx={w * 0.003}
                  fill={COUNTROOM.shade} stroke={INK} strokeWidth={w * 0.004} />
            {/* THE BRUSH STROKE, straight across the knuckle and UNBROKEN.
                This is the whole gag and it has to survive a downscale: the
                stroke is the proof the door has not opened since it was
                painted, so it runs wider than the hinge and carries a lit edge
                so it reads as wet paint rather than as a gap in the hinge. */}
            <rect x={give - w * 0.019} y={h * 0.14 * fy - h * 0.0075}
                  width={w * 0.044} height={h * 0.014}
                  fill={COUNTROOM.key} opacity={0.95} />
            <rect x={give - w * 0.019} y={h * 0.14 * fy - h * 0.0075}
                  width={w * 0.044} height={h * 0.004}
                  fill="#6FB3AE" opacity={0.75} />
          </g>
        ))}
        <rect x={give + w * 0.15} y={h * 0.06} width={w * 0.028} height={h * 0.018} rx={w * 0.004}
              fill={COUNTROOM.brass} stroke={INK} strokeWidth={w * 0.004} />
      </g>

      {/* THE WORKING CHUTE, lower centre. */}
      <CardChute f={f} x={w * 0.38} y={h * 0.62} w={w * 0.26} state="running" emit={0} />

      {/* THE PLATED CHUTE, lower RIGHT EDGE, half out of frame. It is here from
          the establishing image onward and it does nothing for thirty-eight
          seconds, which is what makes S15 a reveal and not an introduction. */}
      <CardChute f={f} x={w * 0.86} y={h * 0.66} w={w * 0.26} state="plated" open={0} />

      {/* THE FLOOR, and the pile burying it. The tile pattern going completely
          is the turn: the count stops being a number and becomes terrain. */}
      <rect x={0} y={floorY} width={w} height={h - floorY} fill={COUNTROOM.ink} />
      <g opacity={1 - P}>
        {Array.from({length: 7}).map((_, i) => (
          <rect key={i} x={0} y={floorY + (h - floorY) * (i / 7)} width={w}
                height={h * 0.0035} fill={COUNTROOM.shade} opacity={0.7} />
        ))}
        {Array.from({length: 5}).map((_, i) => (
          <rect key={i} x={w * (i / 5)} y={floorY} width={w * 0.0035} height={h - floorY}
                fill={COUNTROOM.shade} opacity={0.5} />
        ))}
      </g>
      <ContactShadow cx={w * 0.5} cy={floorY} rx={w * 0.62} ry={h * 0.012} opacity={0.5} />
    </g>
  );
};

// ===========================================================================
// FilingPlate — THE BUTTON.
//
// Not in the designer's asset list either. The board's S18: the FTC filing
// enters flat over the two contradicting cards and covers them, one line
// highlighted, one red stamp off-square, the word ALLEGED present, NO CAST IN
// FRAME.
//
// THE ALLEGED GUARD LIVES HERE, and it is not decoration. c4 and c5 are
// ALLEGATIONS and this film depicts them happening, so the one frame that
// carries the case caption is the frame that has to say so. `alleged` defaults
// TRUE and a scene has to work to turn it off, which is the right direction for
// a default to fail in.
//
// Ray does not win. The paper that finally contradicts the machine is not his:
// he put a dispute in twice and got one word back. One corner of his card stays
// visible under the filing's bottom edge, unchanged, and the count is never
// shown being corrected, because nothing cleared says it was.
// ===========================================================================
export const FilingPlate: React.FC<{
  w?: number; h?: number;
  caption?: string;
  line?: string;
  /** 0..1 the filing entering flat over the cards. */
  enter?: number;
  /** 0..1 the highlighter swipe. One crooked pass that overshoots. */
  highlight?: number;
  alleged?: boolean;
}> = ({
  w = 1080, h = 1920,
  caption = 'UNITED STATES v. RENTGROW, INC.',
  line = 'reasonable procedures to ensure maximum possible accuracy',
  enter = 1, highlight = 0, alleged = true,
}) => {
  const uid = `fp${React.useId().replace(/:/g, '')}`;
  const e = Math.max(0, Math.min(1, enter));
  const hl = Math.max(0, Math.min(1, highlight));

  return (
    <g transform={`translate(0,${(1 - e) * h * 0.35})`} opacity={e}>
      <rect x={w * 0.06} y={h * 0.12} width={w * 0.88} height={h * 0.7}
            fill={COUNTROOM.card} stroke={INK} strokeWidth={w * 0.006} />

      {/* The caption, the only thing set large. */}
      <text x={w * 0.11} y={h * 0.2}
            fontSize={fitText(caption, w * 0.78, w * 0.052)} fontWeight={900} fill={INK}
            letterSpacing={w * 0.002}
            style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
        {caption}
      </text>
      <rect x={w * 0.11} y={h * 0.215} width={w * 0.62} height={h * 0.0035} fill={INK} />

      {/* Body, as ruled noise. Nobody reads a filing on a phone. */}
      {Array.from({length: 14}).map((_, i) => (
        <rect key={i} x={w * 0.11} y={h * (0.26 + i * 0.026)}
              width={w * (i % 4 === 3 ? 0.38 : i % 3 === 1 ? 0.66 : 0.74)}
              height={h * 0.0075} fill={COUNTROOM.cardShade} opacity={0.75} />
      ))}

      {/* THE HIGHLIGHTED LINE. One crooked swipe that overshoots the end of the
          line, because a highlighter held by a person does. */}
      {hl > 0.01 && (
        <rect x={w * 0.105} y={h * 0.484} width={w * 0.70 * hl} height={h * 0.026}
              fill="#F2D45A" opacity={0.62}
              transform={`rotate(-0.5 ${w * 0.105} ${h * 0.484})`} />
      )}
      <text x={w * 0.11} y={h * 0.503}
            fontSize={fitText(line, w * 0.72, w * 0.034)} fontWeight={700} fill={INK}
            style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
        {line}
      </text>

      {/* ALLEGED. Default on. */}
      {alleged && (
        <text x={w * 0.11} y={h * 0.77} fontSize={w * 0.042} fontWeight={900}
              fill={INK} letterSpacing={w * 0.012}
              style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
          ALLEGED
        </text>
      )}
    </g>
  );
};
