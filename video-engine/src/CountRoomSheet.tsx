/**
 * CountRoomSheet.tsx — PROOF OF PIXELS for the case 0003 set.
 *
 * This exists because of a lesson that has cost this repo a render three
 * separate times: MEASURE GEOMETRY, DO NOT REASON ABOUT IT. The Orbit amplitude
 * (96px, invisible), the athletic shoulder (+8 units, invisible) and the
 * CastSheet bbox (wrong twice from reading the source) were each argued
 * correctly from the code and each wrong on screen.
 *
 * And the harder one: A PROP THAT TYPECHECKS AND RENDERS CAN STILL CHANGE
 * NOTHING. The `mouth` prop was dead for a whole episode behind a
 * `talking !== undefined` guard while every gate stayed green.
 *
 * So this sheet is rendered and LOOKED AT before a line of episode code is
 * written against these components, and before a cent of TTS is spent.
 *
 * IT ANSWERS ONE QUESTION, the one the whole episode rides on. From
 * out/dispatch/world.json, STILL A:
 *
 *   "whether a pile of identical court cases reads as SAME or merely as MANY.
 *    This is the producer's whole thesis and the funny critic's whole objection."
 *
 * The pass conditions are numeric and they are checked against this frame:
 *   - at least TWO DocketCard faces show the case number simultaneously
 *   - the two instances within 15% of each other in glyph height
 *   - the case number occupies >= 22% of the card's long edge
 *   - at 270x480 the two number blocks remain two dark blocks of EQUAL LENGTH
 *     at the same offset within their cards
 *
 * That last one is why the sheet carries a 25% downscale panel: a thing that is
 * legible at 1080 and mush at 270 has failed, because 270 is nearer to where
 * this gets watched.
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CountRoomBG, DocketCard, CardChute, VerifyDie, FilingPlate, COUNTROOM, CAST_TO_CARD} from './lib/countroom';
import {Ray, Dee} from './lib/cast';
import {TallyCounter} from './lib/props';

const W = 1080;
const H = 1920;

/** The card long edge used in the wide shots. Ray's crown is 0.72 of this. */
const CARD_W = 620;

const Label: React.FC<{x: number; y: number; text: string}> = ({x, y, text}) => (
  <text x={x} y={y} fontSize={20} fontWeight={800} fill="#F2EADA" opacity={0.85}
        style={{fontFamily: 'Barlow Condensed, Impact, sans-serif'}}>
    {text}
  </text>
);

export const CountRoomSheet: React.FC = () => {
  const f = useCurrentFrame();

  return (
    <AbsoluteFill style={{background: '#0A0D14'}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {/* ---- PANEL 1: the set, full bleed, with the cast at real scale ---- */}
        <CountRoomBG f={f} w={W} h={H} light={1} pile={0.55} intake={0.4} panel={0} />

        {/* The odometer, cast into the boss. The count may only ever show the
            number of cards visible in the same frame: this is the ALLEGED guard
            drawn rather than written down, so the wheel captions the picture and
            asserts nothing beyond it. Three cards below, so the wheel reads 3. */}
        <g transform={`translate(${W * 0.5},${H * 0.42})`}>
          <TallyCounter x={-92} y={-34} s={0.62} f={f} variant="odometer" count="0003" />
        </g>

        {/* THE PILE. Three cards landed dead flush, edges exactly aligned, which
            is the entire gag: the picture on the floor does not change, and the
            only thing that moves is the height of the man standing on it. */}
        {[0, 1, 2].map((i) => (
          <DocketCard
            key={i}
            x={W * 0.5 - CARD_W / 2}
            y={H * 0.80 - i * (CARD_W * 0.018)}
            w={CARD_W}
            head="EVICTION ACTION"
            caseNo="C-2026-4417"
            light={0.85 - i * 0.05}
          />
        ))}

        {/* The cast at the size law: crown at 0.72 of a card's long edge. */}
        <g transform={`translate(${W * 0.22},${H * 0.79}) scale(${(CARD_W * CAST_TO_CARD) / 680})`}>
          <Ray frame={f} emotion="angry" pose="arms-crossed" />
        </g>
        <g transform={`translate(${W * 0.78},${H * 0.79}) scale(${(CARD_W * CAST_TO_CARD) / 680})`}>
          <Dee frame={f} emotion="flat" pose="stand" />
        </g>

        <Label x={28} y={44} text="1. THE SET, cast at the size law: one court case is 1.39x a man" />
      </svg>
    </AbsoluteFill>
  );
};

/**
 * The second sheet: the props alone, on a flat ground, at the sizes the
 * legibility gate measures. Separated from the set because a component that
 * only ever appears inside a lit wall cannot be judged for its own contrast.
 */
export const CountRoomProps: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: COUNTROOM.shade}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        <Label x={28} y={44} text="2. TWO CARDS, side by side. One word differs, at one fixed position." />

        {/* THE COMPARISON the whole button rests on: same head line, same case
            number, same offsets, differing in exactly one place. If the eye
            cannot find that place in under a second, S16 does not work. */}
        <DocketCard x={40} y={90} w={480} head="EVICTION ACTION" caseNo="C-2026-4417"
                    differs="RESOLVED" light={0.95} />
        <DocketCard x={560} y={90} w={480} head="EVICTION ACTION" caseNo="C-2026-4417"
                    differs="INVALID" light={0.95} />

        <Label x={28} y={430} text="3. THE CHUTE, both states. Same mouth, same geometry." />
        <CardChute f={f} x={60} y={470} w={420} state="running" emit={0.55} />
        <CardChute f={f} x={580} y={470} w={420} state="plated" open={0} />

        <Label x={28} y={900} text="4. THE DIE. A die presses IN; a stamp puts ink ON." />
        <VerifyDie x={120} y={950} w={220} press={0.5} />
        <DocketCard x={420} y={1000} w={520} head="EVICTION ACTION" caseNo="C-2026-4417"
                    light={0.95} />

        <Label x={28} y={1320} text="5. THE BUTTON. ALLEGED is on by default." />
        <g transform="translate(180,1330) scale(0.36)">
          <FilingPlate w={W} h={H} enter={1} highlight={0.9} />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
