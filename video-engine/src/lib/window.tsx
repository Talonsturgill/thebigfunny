/**
 * window.tsx — THE WINDOW. Case 0004, Medicare Advantage prior-authorization.
 *
 * WHY THIS SET, from out/dispatch/world.json.
 *
 * The mechanism here is not assembly, the way case 0003's was. It is A BARRIER
 * WITH NO MASS. HHS OIG (OEI-09-24-00331, June 2026) found that UnitedHealth
 * overturned 99.7 percent of the skilled-nursing denials that were appealed, and
 * that only 18 percent were ever appealed. So the no folds instantly and
 * completely the moment anybody pushes, and it keeps working, because it only
 * ever had to hold against the people who never touched it.
 *
 * The set is therefore the barrier, and every element of the argument is one
 * prop you can point at:
 *
 *   the SHUTTER is the no          it comes down, it has NO stencilled on it
 *   the BELL is the appeal          it opens the shutter, every time, instantly
 *   the CHAIRS are the 82 percent   occupied, and nobody is at the counter
 *
 * None of that needs a caption, and none of it needs the cast to explain it.
 *
 * ========================== THE SIZE LAW, INVERTED ==========================
 *
 * Case 0003 put Ray's crown at 0.72 of a court case's long edge, so ONE COURT
 * CASE WAS 1.39x A MAN, because that episode's point was being outnumbered by
 * paperwork.
 *
 * THIS EPISODE DOES THE OPPOSITE ON PURPOSE. The counter is at 1.05m, the
 * aperture is a little wider than a man's shoulders, the chairs are at real seat
 * height. The machine is exactly as big as a man.
 *
 * That is not a neutral choice and it is not laziness. A barrier that collapses
 * in under a second was never monumental, and drawing it monumental would
 * FLATTER IT. Cathedral lighting on a roller shutter tells the viewer the thing
 * is formidable, and the entire finding is that it is not.
 *
 * It has a second effect the show needed anyway. `scripts/face_size.py` (added
 * 2026-08-05) found every character in case 0003 rendering under 8 percent of
 * frame height, median 4.7, which is about seven millimetres on a phone. At
 * counter height in conversation coverage the faces clear that floor by STAGING
 * rather than by rescue close-ups, which is the first time this show has been
 * able to say that.
 *
 * ======================== THE INSTITUTION HAS NO FACE ========================
 *
 * Its one line comes off a laminated notice taped to the shutter. Nothing here
 * brightens, no aperture irises, no part of the wall turns toward camera.
 *
 * THE SHUTTER RISING IS NOT AN EXPRESSION. It is a mechanism doing the one thing
 * it does, indifferently, and that indifference is the joke. `handoff_to_board`
 * in world.json says this explicitly because the first draft of that document
 * banned "nothing opens" in an episode whose turn is a shutter opening.
 *
 * ===================== WHAT IS BEHIND THE SHUTTER: NOTHING =====================
 *
 * NEVER DRAW THE BACK OFFICE. Neither OIG report describes who or what issues
 * these denials, so an office, a clerk or a machine on the far side asserts a
 * mechanism the documents do not contain. `ApertureDepth` renders unlit depth
 * and that is all it will ever render. This is a fact-check guard wearing the
 * costume of a design decision.
 */
import React from 'react';
import {INK, tones, RimLight, ContactShadow} from './lighting';

// ===========================================================================
// THE PALETTE. Municipal oxblood and cream, from out/dispatch/world.json.
//
// Diverges from 0001 manila/carbon, 0002 night steel, 0003 enamel teal/brass.
// Authored as value LADDERS rather than as colours that look nice together, so
// every surface has form under one flat light instead of being a flat rectangle
// with lines on it.
//
// Worn and forty years old on purpose: the room is not futuristic and neither is
// the finding. OIG named this pattern in 2018 and the number went UP.
// ===========================================================================
export const WINDOW = {
  ink: INK,
  // the wall, ochre to shoulder height over cream
  ochreKey: '#C8A24E',
  ochre: '#A8842F',
  ochreLo: '#7C6122',
  creamKey: '#F2ECDD',
  cream: '#E2D9C4',
  creamLo: '#C4B99F',
  // oxblood vinyl
  oxKey: '#8E3B3B',
  ox: '#6E2B2B',
  oxLo: '#4A1C1C',
  // dull aluminium shutter
  alKey: '#B9BDBE',
  al: '#93999B',
  alLo: '#666C6E',
  // formica counter
  formicaKey: '#EDE7D6',
  formica: '#D8D0BA',
  formicaLo: '#ADA48D',
  // the brass bell
  brassKey: '#E4C06A',
  brass: '#B8912F',
  brassLo: '#7E611C',
} as const;

/** Ray's crown as a fraction of the counter-to-floor height. HUMAN scale: the
    counter comes to a bit above his waist, like every counter you have stood
    at. This is the number `face_size.py` reads through. */
export const CAST_TO_COUNTER = 1.62;

/** The counter top, as a fraction of frame height, in the default staging. */
export const COUNTER_Y = 0.62;

const uid = () => `w${React.useId().replace(/:/g, '')}`;

// ===========================================================================
// WaitingRoomBG — the wall, the dado rail, the counter, the floor.
//
// ONE flat overhead fluorescent, no falloff, and NO SHADOW EVER MOVES. Case
// 0001 had a dust column, 0002 had night, 0003 had one hard practical. This
// refuses all three, because a waiting room has no time of day and nothing in
// it tells you how long you have been there.
// ===========================================================================
export const WaitingRoomBG: React.FC<{
  f: number; w: number; h: number;
  /** 0..1 overall light. Never used to dramatise; only to sit a shot back. */
  light?: number;
  /** 0..1 how grubby the wall reads. Scuffs at chair-back height. */
  wear?: number;
}> = ({f, w, h, light = 1, wear = 0.7}) => {
  const id = uid();
  const L = Math.max(0, Math.min(1, light));
  const dado = h * 0.44;
  const counterY = h * COUNTER_Y;
  return (
    <g>
      <defs>
        <linearGradient id={`${id}wall`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={WINDOW.creamKey} />
          <stop offset="100%" stopColor={WINDOW.cream} />
        </linearGradient>
        <linearGradient id={`${id}och`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={WINDOW.ochreKey} />
          <stop offset="55%" stopColor={WINDOW.ochre} />
          <stop offset="100%" stopColor={WINDOW.ochreLo} />
        </linearGradient>
        <linearGradient id={`${id}form`} x1="0" y1="0" x2="0.2" y2="1">
          <stop offset="0%" stopColor={WINDOW.formicaKey} />
          <stop offset="60%" stopColor={WINDOW.formica} />
          <stop offset="100%" stopColor={WINDOW.formicaLo} />
        </linearGradient>
      </defs>

      {/* cream above the rail */}
      <rect x={-w} y={-h} width={w * 3} height={dado + h} fill={`url(#${id}wall)`} opacity={L} />
      {/* ochre below it, to shoulder height */}
      <rect x={-w} y={dado} width={w * 3} height={counterY - dado} fill={`url(#${id}och)`} opacity={L} />
      {/* the dado rail itself, the one horizontal that reads at thumbnail size */}
      <rect x={-w} y={dado - h * 0.008} width={w * 3} height={h * 0.012} fill={WINDOW.ochreLo} opacity={L} />
      <rect x={-w} y={dado - h * 0.008} width={w * 3} height={h * 0.004} fill={WINDOW.creamLo} opacity={L * 0.8} />

      {/* SCUFFS at chair-back height. Static, and they never move, because
          nothing in this room moves except the shutter and the people. */}
      {wear > 0 && Array.from({length: 9}).map((_, i) => {
        const x = w * (0.04 + i * 0.115);
        return (
          <rect key={i} x={x} y={dado + h * 0.055} width={w * (0.03 + (i % 3) * 0.02)}
                height={h * 0.006} rx={h * 0.003}
                fill={WINDOW.ochreLo} opacity={L * wear * 0.35} />
        );
      })}

      {/* THE COUNTER. Formica top with a worn front edge. */}
      <rect x={-w} y={counterY} width={w * 3} height={h * 0.03} fill={`url(#${id}form)`} opacity={L} />
      {/* THE FRONT OF THE COUNTER, which was a blank cream slab filling the
          bottom half of every shot and reading as a floor. A counter has a lip,
          a modesty panel with seams, and a kick recess at the bottom, and those
          three lines are the difference between a surface and a wall. */}
      <rect x={-w} y={counterY + h * 0.03} width={w * 3} height={h * 0.5} fill={WINDOW.creamLo} opacity={L * 0.9} />
      <rect x={-w} y={counterY + h * 0.028} width={w * 3} height={h * 0.005} fill={WINDOW.formicaLo} opacity={L} />
      {/* the shadow the overhang throws on the panel below it */}
      <rect x={-w} y={counterY + h * 0.033} width={w * 3} height={h * 0.014}
            fill={WINDOW.ochreLo} opacity={L * 0.22} />
      {/* panel seams, every third of the frame width */}
      {[0.18, 0.5, 0.82].map((r, i) => (
        <rect key={i} x={w * r} y={counterY + h * 0.045} width={h * 0.0025} height={h * 0.16}
              fill={WINDOW.formicaLo} opacity={L * 0.5} />
      ))}
      {/* the kick recess, which is what makes it read as furniture */}
      <rect x={-w} y={counterY + h * 0.205} width={w * 3} height={h * 0.03}
            fill={WINDOW.ochreLo} opacity={L * 0.35} />
      <rect x={-w} y={counterY + h * 0.235} width={w * 3} height={h * 0.5}
            fill={WINDOW.formicaLo} opacity={L * 0.55} />
      <ContactShadow cx={w * 0.5} cy={counterY + h * 0.03} rx={w} ry={h * 0.006} opacity={0.18 * L} />
    </g>
  );
};

// ===========================================================================
// ApertureDepth — what is on the far side of the shutter.
//
// UNLIT DEPTH, AND NOTHING ELSE, EVER. See the header. This component exists
// so that "draw nothing back there" is a thing a scene CALLS rather than a
// thing a scene has to remember not to do.
// ===========================================================================
export const ApertureDepth: React.FC<{x: number; y: number; w: number; h: number}> =
({x, y, w, h}) => {
  const id = uid();
  return (
    <g>
      <defs>
        <linearGradient id={`${id}d`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0B0C0E" />
          <stop offset="100%" stopColor="#16181C" />
        </linearGradient>
        <linearGradient id={`${id}fall`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={WINDOW.creamLo} stopOpacity={0.20} />
          <stop offset="100%" stopColor={WINDOW.creamLo} stopOpacity={0} />
        </linearGradient>
      </defs>
      <rect x={x} y={y} width={w} height={h} fill={`url(#${id}d)`} />
      {/* IT READ AS A BLACKBOARD. First render put a flat black rectangle in the
          wall and the eye filed it as a panel, not as an opening, which loses
          the only thing the aperture has to say: that there is a space back
          there and nothing is coming out of it.
          Depth WITHOUT CONTENT: the overhead fluorescent falls off into the
          reveal, a faint back plane sits at the bottom, and the sill catches
          light. None of that draws an office, a clerk or a machine, which the
          fact-check guard forbids. It only says the room continues. */}
      <rect x={x} y={y} width={w} height={h * 0.30} fill={`url(#${id}fall)`} />
      <rect x={x} y={y + h * 0.62} width={w} height={h * 0.38} fill="#1B1E23" opacity={0.75} />
      <rect x={x} y={y + h * 0.62} width={w} height={h * 0.012} fill={WINDOW.alLo} opacity={0.30} />
      {/* the reveal: the wall has thickness, and the left jamb catches the key */}
      <rect x={x} y={y} width={w * 0.018} height={h} fill={WINDOW.creamLo} opacity={0.22} />
      <rect x={x} y={y} width={w} height={h * 0.02} fill={INK} opacity={0.55} />
      <rect x={x} y={y + h - h * 0.06} width={w} height={h * 0.06} fill={WINDOW.alLo} opacity={0.62} />
      <rect x={x} y={y + h - h * 0.06} width={w} height={h * 0.018} fill={WINDOW.alKey} opacity={0.45} />
    </g>
  );
};

// ===========================================================================
// ServiceWindow — the aperture and its roller shutter.
//
// `shut` 0..1 drives the slats down over the opening. THE STENCILLED NO is
// painted across the slats and is only legible once they are down, which means
// the word assembles itself as the shutter closes and disassembles as it opens.
// That is the whole episode in one parameter.
// ===========================================================================
export const ServiceWindow: React.FC<{
  x: number; y: number; w: number; h: number;
  /** 0 = fully open, 1 = fully down. */
  shut: number;
  /** the laminated notice taped to the slats, for the Institution's one line. */
  notice?: boolean;
  light?: number;
}> = ({x, y, w, h, shut, notice = false, light = 1}) => {
  const id = uid();
  const s = Math.max(0, Math.min(1, shut));
  const L = Math.max(0, Math.min(1, light));
  const SLATS = 11;
  const slatH = h / SLATS;
  const drop = h * s;
  const al = tones(WINDOW.al);
  return (
    <g>
      <defs>
        <linearGradient id={`${id}sl`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={al.key} />
          <stop offset="45%" stopColor={WINDOW.al} />
          <stop offset="100%" stopColor={WINDOW.alLo} />
        </linearGradient>
        <clipPath id={`${id}clip`}>
          <rect x={x} y={y} width={w} height={h} />
        </clipPath>
      </defs>

      <ApertureDepth x={x} y={y} w={w} h={h} />

      <g clipPath={`url(#${id}clip)`}>
        {/* THE SLATS. They ride down from above the aperture, so at shut=0 the
            whole curtain is stacked out of frame and the opening is clean. */}
        <g transform={`translate(0,${drop - h})`}>
          {Array.from({length: SLATS}).map((_, i) => (
            <g key={i}>
              <rect x={x} y={y + i * slatH} width={w} height={slatH - 1}
                    fill={`url(#${id}sl)`} opacity={L} />
              <rect x={x} y={y + i * slatH} width={w} height={slatH * 0.16}
                    fill={al.key} opacity={L * 0.5} />
            </g>
          ))}
          {/* THE WORD. Painted across the curtain, so it only reads whole when
              the curtain is whole. Stencil weight, wide tracking, worn. */}
          <text x={x + w / 2} y={y + h * 0.58} textAnchor="middle"
                fontFamily="Archivo Black, Impact, sans-serif"
                fontSize={h * 0.34} letterSpacing={h * 0.05}
                fill={WINDOW.ochreLo} opacity={L * 0.88}>NO</text>
          {/* the bottom rail, heavier than the slats */}
          <rect x={x - w * 0.01} y={y + h - slatH * 0.9} width={w * 1.02} height={slatH * 0.9}
                fill={WINDOW.alLo} opacity={L} />
        </g>

        {notice && s > 0.5 && (
          <g transform={`translate(${x + w * 0.58},${y + drop - h * 0.42})`}>
            <rect x={0} y={0} width={w * 0.34} height={h * 0.2} rx={2}
                  fill={WINDOW.creamKey} opacity={L * 0.95} />
            <rect x={0} y={0} width={w * 0.34} height={h * 0.2} rx={2}
                  fill="none" stroke={WINDOW.alLo} strokeWidth={1.5} opacity={L} />
            {[0.28, 0.5, 0.72].map((r, i) => (
              <rect key={i} x={w * 0.03} y={h * 0.2 * r} width={w * (0.28 - i * 0.06)}
                    height={h * 0.016} fill={WINDOW.alLo} opacity={L * 0.55} />
            ))}
          </g>
        )}
      </g>

      {/* the frame, drawn last so the curtain runs behind it */}
      <rect x={x - w * 0.02} y={y - h * 0.03} width={w * 1.04} height={h * 1.06}
            fill="none" stroke={WINDOW.alLo} strokeWidth={Math.max(3, w * 0.012)} opacity={L} />
      <RimLight d={`M ${x} ${y - h * 0.03} L ${x + w} ${y - h * 0.03}`} w={2} opacity={0.22 * L} />
    </g>
  );
};

// ===========================================================================
// CounterBell — the appeal, as an object.
//
// On screen from second one and untouched for twenty seconds. `struck` 0..1
// compresses the dome about 3px and wobbles the ring, which is all a bell needs
// to read as rung at this size.
//
// THE SHUTTER MUST ALREADY BE MOVING IN THE SAME FRAME AS THE HAND ON THIS.
// world.json's handoff says it in capitals: if a board cuts between the two,
// the gag becomes cause and effect over time, and the point is that there is no
// time. One frame, both things.
// ===========================================================================
export const CounterBell: React.FC<{
  x: number; y: number; w: number;
  /** 0..1, a short kick. */
  struck?: number;
  light?: number;
}> = ({x, y, w, struck = 0, light = 1}) => {
  const id = uid();
  const k = Math.max(0, Math.min(1, struck));
  const L = Math.max(0, Math.min(1, light));
  const squash = 1 - k * 0.06;
  const br = tones(WINDOW.brass);
  return (
    <g transform={`translate(${x},${y})`}>
      <defs>
        <radialGradient id={`${id}dome`} cx="0.35" cy="0.28" r="0.85">
          <stop offset="0%" stopColor={br.key} />
          <stop offset="55%" stopColor={WINDOW.brass} />
          <stop offset="100%" stopColor={WINDOW.brassLo} />
        </radialGradient>
      </defs>
      <ContactShadow cx={0} cy={w * 0.06} rx={w * 0.55} ry={w * 0.06} opacity={0.3 * L} />
      {/* base */}
      <rect x={-w * 0.5} y={-w * 0.02} width={w} height={w * 0.09} rx={w * 0.03}
            fill={WINDOW.brassLo} opacity={L} />
      {/* dome */}
      <g transform={`scale(${1 + k * 0.03},${squash})`}>
        <path d={`M ${-w * 0.44} 0 A ${w * 0.44} ${w * 0.40} 0 0 1 ${w * 0.44} 0 Z`}
              fill={`url(#${id}dome)`} opacity={L} />
        <path d={`M ${-w * 0.26} ${-w * 0.16} A ${w * 0.28} ${w * 0.2} 0 0 1 ${-w * 0.02} ${-w * 0.3}`}
              fill="none" stroke={br.key} strokeWidth={w * 0.045}
              strokeLinecap="round" opacity={L * 0.75} />
        {/* the plunger */}
        <rect x={-w * 0.035} y={-w * 0.46} width={w * 0.07} height={w * 0.09} rx={w * 0.03}
              fill={WINDOW.brassLo} opacity={L} />
      </g>
    </g>
  );
};

// ===========================================================================
// ChairRow — the 82 percent.
//
// Oxblood vinyl on a rail. The seated figures are SILHOUETTES and stay
// silhouettes: world.json's handoff says giving one of them a face turns the
// wide into a story about that person, and this episode is about a mechanism.
//
// They also never move. Not a budget decision. A room where nobody is doing
// anything is the finding.
// ===========================================================================
export const ChairRow: React.FC<{
  x: number; y: number; w: number; seats?: number;
  /** how many of them are taken, from the left. */
  occupied?: number;
  light?: number;
}> = ({x, y, w, seats = 5, occupied = 0, light = 1}) => {
  const L = Math.max(0, Math.min(1, light));
  const sw = w / seats;
  const ox = tones(WINDOW.ox);
  return (
    <g transform={`translate(${x},${y})`}>
      {/* the rail the seats hang off */}
      <rect x={0} y={sw * 0.62} width={w} height={sw * 0.06} fill={WINDOW.alLo} opacity={L} />
      {Array.from({length: seats}).map((_, i) => {
        const cx = i * sw;
        const taken = i < occupied;
        return (
          <g key={i} transform={`translate(${cx},0)`}>
            {/* SILHOUETTE FIRST, so the chair laps over the body and the person
                reads as sitting IN it rather than pasted on top. */}
            {taken && (
              <g opacity={L * 0.9}>
                {/* THE HEAD USED TO FLOAT. It sat at -0.52 with the torso
                    topping out at -0.30, so every silhouette had a gap at the
                    neck and read as a balloon over a coat. Head lowered, torso
                    raised, and a neck between them. */}
                {/* SHOULDERS HAVE TO CLEAR THE SEAT BACK. The chair back is
                    drawn AFTER this and tops out at -0.26, so a torso topping
                    out at -0.34 left eight hundredths of a seat-width showing
                    and the head read as a ball resting on the upholstery.
                    Torso to -0.50, head to -0.62: now a head, a neck and two
                    shoulders emerge, which is what a person in a chair is. */}
                <path d={`M ${sw * 0.5 - sw * 0.28} ${sw * 0.14}
                          C ${sw * 0.5 - sw * 0.30} ${-sw * 0.50},
                            ${sw * 0.5 + sw * 0.30} ${-sw * 0.50},
                            ${sw * 0.5 + sw * 0.28} ${sw * 0.14} Z`}
                      fill={INK} opacity={0.82} />
                <rect x={sw * 0.44} y={-sw * 0.58} width={sw * 0.12} height={sw * 0.14}
                      fill={INK} opacity={0.82} />
                <ellipse cx={sw * 0.5} cy={-sw * 0.62} rx={sw * 0.145} ry={sw * 0.16}
                         fill={INK} opacity={0.82} />
              </g>
            )}
            {/* seat pan and back */}
            <rect x={sw * 0.1} y={sw * 0.1} width={sw * 0.8} height={sw * 0.14} rx={sw * 0.05}
                  fill={ox.key} opacity={L} />
            <rect x={sw * 0.1} y={sw * 0.1} width={sw * 0.8} height={sw * 0.05} rx={sw * 0.03}
                  fill={WINDOW.oxKey} opacity={L * 0.7} />
            <rect x={sw * 0.14} y={-sw * 0.26} width={sw * 0.72} height={sw * 0.3} rx={sw * 0.06}
                  fill={WINDOW.ox} opacity={L} />
            {/* legs */}
            <rect x={sw * 0.16} y={sw * 0.24} width={sw * 0.05} height={sw * 0.4} fill={WINDOW.alLo} opacity={L} />
            <rect x={sw * 0.79} y={sw * 0.24} width={sw * 0.05} height={sw * 0.4} fill={WINDOW.alLo} opacity={L} />
            <ContactShadow cx={sw * 0.5} cy={sw * 0.64} rx={sw * 0.45} ry={sw * 0.05} opacity={0.16 * L} />
          </g>
        );
      })}
    </g>
  );
};

// ===========================================================================
// StampPair — NO and YES in one tray, worn to exactly the same shine.
//
// The same hand does both, all day, to the same piece of paper. This is the
// mechanism as a still life and it asserts nothing about motive: OIG found the
// reversal rate, not the reason, and claims.json CUT intent explicitly.
//
// AN EARLIER DESIGN had the YES stamp still in its wrapper. It was funnier and
// it was FALSE: they say yes constantly, just later. The wear has to match.
// ===========================================================================
export const StampPair: React.FC<{
  x: number; y: number; w: number; light?: number;
}> = ({x, y, w, light = 1}) => {
  const L = Math.max(0, Math.min(1, light));
  const one = (dx: number, label: string) => (
    <g transform={`translate(${dx},0)`}>
      <ContactShadow cx={w * 0.11} cy={w * 0.3} rx={w * 0.14} ry={w * 0.022} opacity={0.28 * L} />
      {/* handle, worn to the same shine on both */}
      <rect x={w * 0.045} y={-w * 0.2} width={w * 0.13} height={w * 0.2} rx={w * 0.055}
            fill={WINDOW.oxLo} opacity={L} />
      <rect x={w * 0.06} y={-w * 0.185} width={w * 0.045} height={w * 0.17} rx={w * 0.02}
            fill={WINDOW.oxKey} opacity={L * 0.55} />
      {/* block */}
      <rect x={0} y={0} width={w * 0.22} height={w * 0.1} rx={w * 0.014}
            fill={WINDOW.ink} opacity={L} />
      <text x={w * 0.11} y={w * 0.235} textAnchor="middle"
            fontFamily="Archivo Black, Impact, sans-serif" fontSize={w * 0.085}
            fill={WINDOW.oxLo} opacity={L * 0.9}>{label}</text>
    </g>
  );
  return (
    <g transform={`translate(${x},${y})`}>
      {/* the tray they share. One tray is the point. */}
      <rect x={-w * 0.04} y={w * 0.06} width={w * 0.62} height={w * 0.1} rx={w * 0.02}
            fill={WINDOW.alLo} opacity={L * 0.9} />
      {one(0, 'NO')}
      {one(w * 0.3, 'YES')}
    </g>
  );
};

// ===========================================================================
// OIGPlate — the button.
//
// The report page, with TWO highlightable sentences at fixed rows so the 2018
// finding sits directly above the 2026 one and the receipt reads as a
// comparison rather than as a citation. world.json's legibility gate: both
// percentages must be the largest type on the plate.
// ===========================================================================
export const OIGPlate: React.FC<{
  w: number; h: number;
  /** 0..1 wipe on the upper (2018) row. */
  hiA?: number;
  /** 0..1 wipe on the lower (2026) row. */
  hiB?: number;
  reportNo?: string;
}> = ({w, h, hiA = 0, hiB = 0, reportNo = 'OEI-09-24-00331'}) => {
  const id = uid();
  const pad = w * 0.07;
  const rowA = h * 0.42;
  const rowB = h * 0.63;
  return (
    <g>
      <defs>
        <linearGradient id={`${id}pg`} x1="0" y1="0" x2="0.3" y2="1">
          <stop offset="0%" stopColor={WINDOW.creamKey} />
          <stop offset="100%" stopColor={WINDOW.cream} />
        </linearGradient>
      </defs>
      <rect x={pad * 0.5} y={h * 0.06} width={w - pad} height={h * 0.86} rx={4}
            fill={`url(#${id}pg)`} />
      <rect x={pad * 0.5} y={h * 0.06} width={w - pad} height={h * 0.86} rx={4}
            fill="none" stroke={WINDOW.creamLo} strokeWidth={2} />

      <text x={pad} y={h * 0.155} fontFamily="Archivo, Helvetica, sans-serif"
            fontSize={h * 0.028} letterSpacing={h * 0.006} fill={WINDOW.ochreLo}>
        HHS OFFICE OF INSPECTOR GENERAL
      </text>
      <text x={pad} y={h * 0.205} fontFamily="Archivo Black, Impact, sans-serif"
            fontSize={h * 0.042} fill={WINDOW.ink}>
        {reportNo}
      </text>
      <rect x={pad} y={h * 0.235} width={w - pad * 2} height={2} fill={WINDOW.creamLo} />

      {/* THE TWO SENTENCES, one above the other, so the comparison is the shot. */}
      {[[rowA, hiA, '2018', '75%'], [rowB, hiB, '2026', '95%']].map(
        ([row, hi, year, pct], i) => (
          <g key={i}>
            <rect x={pad * 0.8} y={(row as number) - h * 0.075}
                  width={(w - pad * 1.6) * Math.max(0, Math.min(1, hi as number))}
                  height={h * 0.115} rx={3} fill={WINDOW.brassKey} opacity={0.42} />
            <text x={pad} y={row as number} fontFamily="Archivo, Helvetica, sans-serif"
                  fontSize={h * 0.03} fill={WINDOW.ochreLo}>{year as string}</text>
            <text x={pad + w * 0.13} y={(row as number) + h * 0.012}
                  fontFamily="Archivo Black, Impact, sans-serif"
                  fontSize={h * 0.082} fill={WINDOW.ink}>{pct as string}</text>
            <text x={pad + w * 0.34} y={row as number}
                  fontFamily="Archivo, Helvetica, sans-serif"
                  fontSize={h * 0.026} fill={WINDOW.ochreLo}>
              {i === 0 ? 'of appealed denials overturned' : 'of appealed SNF denials overturned'}
            </text>
          </g>
        ))}

      {[0.75, 0.79, 0.83].map((r, i) => (
        <rect key={i} x={pad} y={h * r} width={(w - pad * 2) * (0.92 - i * 0.13)}
              height={h * 0.008} fill={WINDOW.creamLo} />
      ))}
    </g>
  );
};


// ===========================================================================
// WallClock — the only thing in this room that moves on its own.
//
// ADDED AFTER THE FIRST FINAL RENDER, because motion_check measured 34 percent
// frozen, a 4.5 second held drawing, and a five-second bucket with nothing
// happening in it at all. Case 0003 had an odometer, a chute and falling cards;
// this room has a shutter that moves twice and a bell struck once, and between
// those events the frame was a photograph.
//
// A clock is the right answer rather than a convenient one. It belongs in a
// municipal waiting room more than anything else that could go on that wall, it
// is the object the room is ABOUT (this episode is 18 percent of people
// deciding it is not worth their afternoon), and a sweeping second hand is
// continuous motion that costs one transform and never repeats a position.
//
// It is NOT the Institution emoting. It does not react, brighten or acknowledge
// anybody. It is furniture doing what furniture does while nothing happens.
// ===========================================================================
export const WallClock: React.FC<{
  x: number; y: number; r: number; f: number; fps?: number;
  /** minutes past the hour at frame 0. The hands are decorative, not a claim. */
  startMin?: number;
  light?: number;
}> = ({x, y, r, f, fps = 30, startMin = 37, light = 1}) => {
  const L = Math.max(0, Math.min(1, light));
  const t = f / fps;
  // A REAL SWEEP, not a tick. A tick lands on the same 60 positions forever and
  // a frame differ scores it as a still between ticks, which is also how it
  // reads: the second hand is the one thing here that is never in the same
  // place twice.
  const secA = (t / 60) * 360;
  const minA = ((startMin + t / 60) / 60) * 360;
  const hourA = ((10 + (startMin + t / 60) / 60) / 12) * 360;
  return (
    <g transform={`translate(${x},${y})`}>
      <circle cx={0} cy={0} r={r * 1.06} fill={WINDOW.alLo} opacity={L} />
      <circle cx={0} cy={0} r={r} fill={WINDOW.creamKey} opacity={L} />
      <circle cx={0} cy={0} r={r} fill="none" stroke={WINDOW.creamLo} strokeWidth={r * 0.04} opacity={L} />
      {Array.from({length: 12}).map((_, i) => (
        <rect key={i} x={-r * 0.025} y={-r * 0.88} width={r * 0.05} height={r * 0.16}
              rx={r * 0.02} fill={WINDOW.ochreLo} opacity={L * 0.8}
              transform={`rotate(${i * 30})`} />
      ))}
      <rect x={-r * 0.045} y={-r * 0.5} width={r * 0.09} height={r * 0.54} rx={r * 0.04}
            fill={WINDOW.ink} opacity={L} transform={`rotate(${hourA})`} />
      <rect x={-r * 0.035} y={-r * 0.74} width={r * 0.07} height={r * 0.78} rx={r * 0.03}
            fill={WINDOW.ink} opacity={L} transform={`rotate(${minA})`} />
      <rect x={-r * 0.016} y={-r * 0.82} width={r * 0.032} height={r * 0.94} rx={r * 0.016}
            fill={WINDOW.ox} opacity={L} transform={`rotate(${secA})`} />
      <circle cx={0} cy={0} r={r * 0.07} fill={WINDOW.ink} opacity={L} />
    </g>
  );
};
