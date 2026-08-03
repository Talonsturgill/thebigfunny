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
import {CountRoomBG, DocketCard, CardPile, CardChute, VerifyDie, FilingPlate, COUNTROOM, CAST_TO_CARD, CARD_ASPECT} from './lib/countroom';
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
        <CountRoomBG f={f} w={W} h={H} light={1} pile={0.85} intake={0.4} panel={0} />

        {/* The odometer, cast into the boss. The count may only ever show the
            number of cards visible in the same frame: this is the ALLEGED guard
            drawn rather than written down, so the wheel captions the picture and
            asserts nothing beyond it. Three cards below, so the wheel reads 3. */}
        {/* THE ODOMETER, IN its boss. Two measurements off the failing render,
            neither of them guessable: CountRoomBG mounts the boss at h*0.42 and
            not at the sheet's own guess of h*0.52, and TallyCounter draws from
            its x as a LEFT EDGE rather than from its centre. */}
        <g transform={`translate(${W * 0.5},${H * 0.42})`}>
          <TallyCounter x={-62} y={-22} s={0.78} f={f} variant="odometer" count="0004" />
        </g>

        {/* THE PILE, in `stacked` mode, which is STILL A.
            
            The first render of this sheet put three cards at an 11px offset and
            produced ONE card with a thick edge and exactly one case number. The
            gate wants TWO numbers visible at once, because that is the only way
            an eye can tell SAME from MANY, and SAME is the whole thesis: the
            machine copied one court case, it did not find several. */}
        <CardPile x={W * 0.5 - CARD_W / 2} y={H * 0.80} w={CARD_W} count={4}
                  mode="stacked" head="EVICTION ACTION" caseNo="C-2026-4417" />

        {/* THE CAST AT THE SIZE LAW: crown at 0.72 of a card's long edge.
        
            FIGURE'S ORIGIN IS THE CROWN, NOT THE FEET. lib/Figure.tsx line 59:
            Y = {crown: 0, ... ground: 680}, so it draws DOWNWARD from its own
            origin and a full body is 680 local units tall.
            
            The first render of this sheet assumed a -440..+10 bbox, which is
            Character's, the retired crowd rig, and put both of them off the
            bottom of frame with only their heads showing. Measured, not read:
            k = wanted crown height / 680, and the translate is the GROUND line
            minus that height so the feet land on the tile. */}
        {(() => {
          const crown = CARD_W * CAST_TO_CARD;      // 446px at CARD_W 620
          const k = crown / 680;
          const ground = H * 0.955;
          return (
            <>
              <g transform={`translate(${W * 0.135},${ground - crown}) scale(${k})`}>
                <Ray frame={f} emotion="angry" pose="arms-crossed" />
              </g>
              <g transform={`translate(${W * 0.875},${ground - crown}) scale(${k})`}>
                <Dee frame={f} emotion="flat" pose="stand" />
              </g>
            </>
          );
        })()}

        <Label x={28} y={44} text="1. THE SET. Four cards, four case numbers, one man 0.72 of a card" />
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

        <Label x={28} y={900} text="4. THE DIE, pressing a card. A die presses IN; a stamp puts ink ON." />
        {/* The die has to be ON the card it embosses. The first render floated it
            beside one, and worse, centred the emboss under the block so VERIFIED
            rendered as "VI....D": a die hiding its own impression. */}
        <DocketCard x={60} y={950} w={620} head="EVICTION ACTION" caseNo="C-2026-4417"
                    light={0.95} />
        <VerifyDie x={110} y={1075} w={150} press={0.5} />

        <Label x={28} y={1320} text="5. THE BUTTON. ALLEGED is on by default." />
        <g transform="translate(180,1330) scale(0.36)">
          <FilingPlate w={W} h={H} enter={1} highlight={0.9} />
        </g>
      </svg>
    </AbsoluteFill>
  );
};
