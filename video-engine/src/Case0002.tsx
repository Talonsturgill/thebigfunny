/**
 * Case0002.tsx — THE BIG FUNNY, case 0002.
 * "They Fixed It In October. It Came Back Bigger."
 *
 * Angle (ratio): Ford recalled 43,438 of these SUVs in October for a sound they
 * would not make, updated the software and mailed the letters; in June the same
 * recall came back covering 66,383, and the cars they already fixed have to be
 * fixed again.
 *
 * Every factual string on screen traces to out/dispatch/claims.json.
 *
 * GUARDS FROM THE FACT-CHECK GATE AND GATE 0, all load-bearing:
 *   1. claims.json c11 is CUT. Nothing may say or imply that the 28 speakers are
 *      what FAILED. Gate 0 killed the first board here: a lone "28 SPEAKERS"
 *      badge does not read as a window sticker, it reads as a callout on the
 *      broken part, and the viewer walks away believing the wrong thing. So S5
 *      draws the SORTING instead: a two-row eligibility list, both rows straight
 *      out of c3 and c4. The picture now says "this is how they decide who gets
 *      fixed", not "this is what broke".
 *   2. c2 says a software error MAY prevent the sound AT CERTAIN SPEEDS. The
 *      hook says "a warning sound" and Dee immediately supplies "it doesn't
 *      always play". Nothing here claims these SUVs are silent.
 *   3. No impact, no injury, no pedestrian, no car in motion anywhere.
 *
 * ONE-STAMP AUDIT (the rule is earned here, not asserted). Enumerated: the
 * Wordmark at t=2.0 is BRAND.PAPER, the EndCard is BRAND.INK, and the receipt
 * stamp in S7 is the default BRAND.STAMP. Both of the first two render through
 * Stamp, which defaults to red, so before they were passed an explicit colour
 * this episode was spending the red token THREE times and halving it twice.
 * Captions, the institution plate, the eligibility rows and the record cards
 * carry no red at all. Exactly one BRAND.STAMP survives, on the receipt.
 *
 * VISUAL SYSTEM (diverges from case 0001 on all five hard axes in
 * ledger/artwork.json): exterior night street in one-point recession instead of
 * an interior cabinet wall; rationed practical light instead of fluorescent
 * flatness; night steel and sodium amber instead of manila and carbon; the
 * camera as the continuity device instead of a motif; and a continuous PUSH
 * instead of a locked frame. The push runs the whole episode and stops dead on
 * the document, so the receipt is the only locked frame in the film.
 *
 * MOUNTING CONTRACT (case 0001's blank-frame lesson, knowledge/FIELD_NOTES.md):
 * everything in src/lib/ that returns SVG MUST be inside <svg viewBox=...>.
 * brand.tsx, NightGrade and GradeLayer are HTML divs and MUST stay outside it.
 */
import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {z} from 'zod';
import {Ray, Dee, DEE_CRACK} from './lib/cast';
import {Wordmark, CaseNumber, EndCard, Highlighter, Stamp, BRAND} from './lib/brand';
import {MainStreetBG} from './lib/biomes';
import {MachineShadow} from './lib/kit';
import {NightGrade, GradeLayer} from './lib/lighting';
import {CAPTIONS, speakerAt, TOTAL as TOTAL_S} from './case0002_captions';
import {openAt, accentAt} from './case0002_mouth';

export const case0002Schema = z.object({total: z.number().optional()});

const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);

/**
 * THE SHOT LADDER IS DERIVED FROM THE VOICE, NOT TYPED IN BESIDE IT.
 *
 * Every shot boundary used to be a hand-entered second: `from={s(13.66)}
 * durationInFrames={s(7.62)}`, eight of them, plus a TOTAL and a
 * durationInFrames in Root.tsx. Re-synthesizing the VO moves all twelve line
 * starts, so each re-fit meant retyping ten numbers across three files, and
 * nothing in the machine can see when one of them is stale: the render is
 * internally consistent and the picture simply cuts on the wrong word.
 *
 * That happened twice in one day, so the boundaries are now CUE INDICES. A shot
 * runs from the moment one line starts to the moment another does, which is what
 * the storyboard actually meant, and a re-fit retimes the picture for free.
 *
 * SHOTS[i] is the cue that shot i cuts in on. The last shot runs to TOTAL.
 */
const CUT_ON = [0, 1, 4, 6, 7, 9, 10];
const TOTAL = s(TOTAL_S);
/** The end card owns the tail, the same 1.5s vo_cast reserves after the last word. */
const TAIL_AT = TOTAL - s(1.5);
const at = (cue: number) => s(CAPTIONS[cue].start);
/** Frames from the cut-in of shot i to the cut-in of shot i+1 (or to the tail). */
const shot = (i: number) =>
  (i + 1 < CUT_ON.length ? at(CUT_ON[i + 1]) : TAIL_AT) - at(CUT_ON[i]);

const HEAD = 'Arial Black, DejaVu Sans, FreeSans, sans-serif';
const BODY = 'Arial, DejaVu Sans, FreeSans, sans-serif';

/** MainStreetBG's vanishing point. The push scales about it, so the camera walks
 *  INTO the street rather than merely enlarging the picture. */
const VPX = 540;
const VPY = 1030;

/**
 * The art layer, carrying the episode's continuity device.
 *
 * `rate` is what keeps this from being a zoom. Gate 0's sharpest craft note was
 * that a uniform scale-up of a flat biome reads as a slow crop-in, and 50
 * seconds of slow crop-in is worse than a locked camera because it advertises
 * that nothing is moving. So the street pushes harder than the cast does: the
 * background runs to 1.22 while the figures run to 1.06, and the differential is
 * real parallax separation between the plate and the people standing on it.
 */
const Art: React.FC<{frame: number; rate?: number; children: React.ReactNode}> = ({
  frame, rate = 1, children,
}) => {
  const k = 1 + (interpolate(frame, [0, TOTAL], [0, 0.22], {extrapolateRight: 'clamp'}) * rate);
  return (
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"
         style={{position: 'absolute', inset: 0}}>
      <g transform={`translate(${VPX * (1 - k)},${VPY * (1 - k)}) scale(${k})`}>
        {children}
      </g>
    </svg>
  );
};

/** Burned-in caption, driven from the MEASURED VO timings so the text cannot
 *  drift from the spoken word. Arial is NOT installed on the render host, so the
 *  weight is explicit and the stack names a face that exists (FIELD_NOTES: a
 *  silent font fallback is invisible in review and obvious on screen). */
const SPEAKER_TINT: Record<string, string> = {
  RAY: '#F2B36B',          // warm, like Ray
  DEE: '#8FD3E8',          // cool and precise, like Dee
  INSTITUTION: '#C9D2D8',  // no warmth at all
};

/**
 * Burned-in caption, driven from the MEASURED VO timings so the text cannot
 * drift from the spoken word. Arial is NOT installed on the render host, so the
 * weight is explicit and the stack names a face that exists (FIELD_NOTES: a
 * silent font fallback is invisible in review and obvious on screen).
 *
 * The speaker LABEL is the fix for the plainest note the first cut got: with
 * three voices and two near-identical figures you could not tell who was
 * talking. The name and its tint answer that in the one place a muted viewer is
 * already looking.
 */
const Caption: React.FC<{frame: number; onLight?: boolean}> = ({frame, onLight = false}) => {
  const t = frame / FPS;
  const cue = CAPTIONS.find((c) => t >= c.start && t <= c.end + 0.14);
  if (!cue) return null;
  const tint = SPEAKER_TINT[cue.who] ?? BRAND.PAPER;
  return (
    <div style={{position: 'absolute', left: 54, right: 54, top: 1476, textAlign: 'center'}}>
      <div style={{
        fontFamily: BODY, fontSize: 27, fontWeight: 700, letterSpacing: '0.28em',
        color: onLight ? 'rgba(16,20,35,0.66)' : tint, marginBottom: 10,
        textShadow: onLight ? 'none' : '0 2px 0 rgba(16,20,35,0.95), 0 0 16px rgba(16,20,35,0.9)',
      }}>{cue.who}</div>
      {/* The caption was authored for the NIGHT frames: paper-white text with a
          dark halo. The button card is a full-bleed CREAM page, and white on
          cream is barely legible. Restoring Ray's closing captions therefore
          dropped them straight onto the one light ground in the episode, so the
          fix for one legibility bug created another. Invert over paper. */}
      <div style={{
        fontFamily: HEAD, fontWeight: 900,
        fontSize: 55, lineHeight: 1.14, color: onLight ? BRAND.INK : BRAND.PAPER,
        textShadow: onLight
          ? 'none'
          : '0 4px 0 rgba(16,20,35,0.92), 0 0 26px rgba(16,20,35,0.8)',
        letterSpacing: '-0.01em',
      }}>{cue.text}</div>
    </div>
  );
};

/** A page from the printout Dee is holding. Real paper body: an offset drop
 *  shadow and a slight tilt, so numbers sit IN the world instead of floating as
 *  UI chips. Gate 0 called the first version captions over a background. */
const Page: React.FC<{
  frame: number; top: number; rot: number; children: React.ReactNode; delay?: number;
}> = ({frame, top, rot, children, delay = 0}) => {
  const op = interpolate(frame - delay, [0, 6], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const dy = interpolate(frame - delay, [0, 9], [22, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{
      position: 'absolute', left: 96, right: 96, top: top + dy, opacity: op,
      transform: `rotate(${rot}deg)`,
      background: BRAND.PAPER, color: BRAND.INK,
      border: `2px solid rgba(16,20,35,0.5)`,
      boxShadow: '4px 6px 0 rgba(16,20,35,0.34)',
      padding: '22px 30px 26px',
    }}>{children}</div>
  );
};

/** The Institution: policy text on a cold plate. NO FACE, EVER. A plate rather
 *  than a full-screen card, so the monolith stays in shot and the text reads as
 *  something EMITTED by it rather than a title card. */
const InstitutionPlate: React.FC<{frame: number; text: string}> = ({frame, text}) => {
  const up = interpolate(frame, [0, 10], [46, 0], {extrapolateRight: 'clamp'});
  const op = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <div style={{
      position: 'absolute', left: 0, right: 0, top: 1010 + up, opacity: op,
      background: BRAND.CARBON,
      borderTop: '3px solid rgba(242,234,218,0.26)',
      borderBottom: '3px solid rgba(242,234,218,0.26)',
      padding: '28px 70px 34px',
    }}>
      <div style={{
        fontFamily: BODY, fontSize: 21, letterSpacing: '0.32em',
        color: BRAND.PAPER, opacity: 0.5, marginBottom: 14,
      }}>NHTSA CAMPAIGN 26V415000, REMEDY</div>
      <div style={{fontFamily: BODY, fontSize: 44, lineHeight: 1.34, color: BRAND.PAPER}}>
        {text}
      </div>
    </div>
  );
};

export const Case0002: React.FC<z.infer<typeof case0002Schema>> = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  /* Who is talking right now. lib/voice.tsx deliberately refuses real lip-sync
     ("figures chat IN the scene, they do not mouth the voiceover"), so this is
     used only as a binary: the speaker's mouth moves, the listener's does not.
     Nothing has to stay in sync per word, which is the whole point. */
  const who = speakerAt(frame / FPS);

  /* The SPEAKER's mouth runs on their own voice (scripts/vo_envelope.py), their
     body hits the onsets, and they carry full idle. The LISTENER's mouth is shut
     and their idle is damped to a third, so at any instant the only real motion
     in frame belongs to whoever is talking. That is what makes a two-shot
     legible without lip-sync accuracy, and it is the half the first cut was
     missing: everything moved all the time, on sines that did not know a word
     was happening. */
  const rayMouth = who === 'RAY' ? openAt(frame) : undefined;
  const deeMouth = who === 'DEE' ? openAt(frame) : undefined;
  const rayAccent = who === 'RAY' ? accentAt(frame) : 0;
  const deeAccent = who === 'DEE' ? accentAt(frame) : 0;
  const rayIdle = who === 'RAY' ? 1 : 0.32;
  const deeIdle = who === 'DEE' ? 1 : 0.32;
  const rayVoice = {mouth: rayMouth, accent: rayAccent, idleGain: rayIdle};
  const deeVoice = {mouth: deeMouth, accent: deeAccent, idleGain: deeIdle};

  /* The night street, lit only by what the scene DECLARES. NightGrade blooms
     only at registered sources by design, so the warm shop windows are the one
     warmth in a cold frame, which is BRAND_BIBLE's warm-against-cold rule
     expressed as lighting. Nothing is registered on the monolith: the street
     light does not reach it. `banner` is off because MainStreetBG's pennant
     string reads county fair, and this show is a case file. */
  const night = (
    <>
      <NightGrade
        f={frame}
        color="#101C2A"
        amount={1.0}
        floor={0.62}
        horizon={0.08}
        sources={[
          {x: 196, y: 1128, r: 250, color: '#FFC46B', intensity: 0.82},
          {x: 884, y: 1112, r: 236, color: '#FFB65A', intensity: 0.78},
        ]}
      />
      <GradeLayer f={frame} bloom={0.24} vignette={0.62} grain={0.07} warmth={0.03} />
    </>
  );

  const street = <MainStreetBG f={frame} dusk={0.72} banner={false} />;

  return (
    <AbsoluteFill style={{background: '#0D141C'}}>

      {/* ---------- S1  the hook. cold open, NO logo. 0.00 - 6.54 ---------- */}
      <Sequence from={at(CUT_ON[0])} durationInFrames={shot(0)}>
        <Art frame={frame} rate={1}>{street}</Art>
        <Art frame={frame} rate={0.28}>
          <Ray frame={frame} x={540} y={1470} scale={1.5} emotion="angry" pose="arms-crossed" {...rayVoice} />
        </Art>
        {night}
      </Sequence>

      {/* The wordmark STAMPS at ~2s. Once, hard, never a fade. PAPER, not STAMP:
          the red token belongs to the receipt, and on a night frame INK reads as
          a smudge. */}
      <Sequence from={s(2.0)} durationInFrames={s(2.4)}>
        <Wordmark frame={frame - s(2.0)} fps={fps} x={540} y={548} scale={0.92} color={BRAND.PAPER} blend="normal" />
      </Sequence>

      {/* ---------- S2  the turn. Dee arrives with the printout. 6.54 - 17.88 ---------- */}
      <Sequence from={at(CUT_ON[1])} durationInFrames={shot(1)}>
        <Art frame={frame} rate={1}>{street}</Art>
        <Art frame={frame} rate={0.28}>
          <Ray frame={frame} x={348} y={1486} scale={1.32} facing={1} emotion="angry"
               pose={frame >= at(2) ? 'point' : 'stand'} {...rayVoice} />
          <Dee frame={frame} x={744} y={1468} scale={1.3}
               pose={frame >= at(3) ? 'raise' : 'stand'} {...deeVoice} />
        </Art>
        {night}
      </Sequence>

      {/* ---------- S3  THE RATIO. two counts, placed, no commentary. 17.88 - 26.48 ---------- */}
      <Sequence from={at(CUT_ON[2])} durationInFrames={shot(2)}>
        <Art frame={frame} rate={1}>{street}</Art>
        <Art frame={frame} rate={0.28}>
          <Dee frame={frame} x={648} y={1690} scale={1.86} {...deeVoice} />
        </Art>
        {night}

        {/* 43,438 lands first, on paper, and is NEVER marked. */}
        <Page frame={frame - at(4)} top={286} rot={-1.1}>
          <div style={{fontFamily: BODY, fontSize: 26, letterSpacing: '0.2em', opacity: 0.62}}>
            CAMPAIGN 25V691000, OCTOBER 2025
          </div>
          <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 96, marginTop: 6}}>43,438</div>
        </Page>

        {/* 66,383 lands beneath it at the SAME size and weight. The episode's one
            and only highlighter swipe goes here, on the worse number. */}
        <Sequence from={at(5) - at(CUT_ON[2])}>
          <Page frame={frame - at(5)} top={606} rot={0.9}>
            <div style={{fontFamily: BODY, fontSize: 26, letterSpacing: '0.2em', opacity: 0.62}}>
              CAMPAIGN 26V415000, JUNE 2026
            </div>
            <div style={{position: 'relative', display: 'inline-block', marginTop: 6}}>
              <Highlighter frame={frame - at(5) - s(1.31)} width={430} height={78} x={-10} y={16} />
              <div style={{position: 'relative', fontFamily: HEAD, fontWeight: 900, fontSize: 96}}>
                66,383
              </div>
            </div>
          </Page>
        </Sequence>
      </Sequence>

      {/* ---------- S4  Ray finds out. performance, not graphics. 26.48 - 35.77 ---------- */}
      <Sequence from={at(CUT_ON[3])} durationInFrames={shot(3)}>
        <Art frame={frame} rate={1}>{street}</Art>
        <Art frame={frame} rate={0.28}>
          <Ray frame={frame} x={498} y={1858} scale={2.52}
               emotion={frame >= at(6) ? 'shock' : 'angry'}
               pose={frame >= at(6) ? 'panic' : 'arms-crossed'} {...rayVoice} />
        </Art>
        {night}
      </Sequence>

      {/* ---------- S5  THE SORTING, and Dee's ONE crack. 35.77 - 45.00 ----------
          Gate 0 blocker: draw the SORTING, never the speakers. Two rows, both
          verbatim from the record, so the picture states the eligibility rule
          rather than pointing at a part. */}
      <Sequence from={at(CUT_ON[4])} durationInFrames={shot(4)}>
        <Art frame={frame} rate={1}>{street}</Art>
        <Art frame={frame} rate={0.28}>
          <Dee frame={frame} x={760} y={1606} scale={1.62} pose="raise"
               emotion={frame < at(8) ? DEE_CRACK : 'neutral'} {...deeVoice} />
          <Ray frame={frame} x={318} y={1628} scale={1.7} facing={1}
               emotion={frame >= at(8) ? 'smug' : 'angry'}
               pose={frame >= at(8) ? 'arms-crossed' : 'point'} {...rayVoice} />
        </Art>
        {night}

        <Page frame={frame - at(7)} top={430} rot={-0.7} delay={s(0.5)}>
          <div style={{fontFamily: BODY, fontSize: 25, letterSpacing: '0.2em', opacity: 0.6}}>
            REMEDY, BY VEHICLE
          </div>
          <div style={{marginTop: 20, display: 'flex', gap: 20, alignItems: 'baseline'}}>
            <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 40, flex: 1, lineHeight: 1.16}}>
              NAUTILUS HYBRID,<br />28 SPEAKERS
            </div>
            <div style={{fontFamily: BODY, fontSize: 33, opacity: 0.9, textAlign: 'right', flex: 1}}>
              module replaced
            </div>
          </div>
          <div style={{height: 2, background: 'rgba(16,20,35,0.28)', margin: '20px 0'}} />
          <div style={{display: 'flex', gap: 20, alignItems: 'baseline'}}>
            <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 40, flex: 1, lineHeight: 1.16}}>
              ALL OTHER<br />NAUTILUS &amp; EXPLORER
            </div>
            <div style={{fontFamily: BODY, fontSize: 33, opacity: 0.9, textAlign: 'right', flex: 1}}>
              remedy currently<br />under development
            </div>
          </div>
        </Page>
      </Sequence>

      {/* ---------- S6  the Institution answers. 45.00 - 51.28 ----------
          LOW ANGLE, the episode's one camera-height change, spent on the thesis:
          the monolith exceeds the top of frame and the pair are small at the
          bottom edge. Its shape language is "too large for frame", and eye level
          down a road made it read as a distant building. */}
      <Sequence from={at(CUT_ON[5])} durationInFrames={shot(5)}>
        <Art frame={frame} rate={1}>{street}</Art>
        <Art frame={frame} rate={0.5}>
          <MachineShadow x={540} y={1180} scale={3.1} f={frame} grow={1} />
        </Art>
        <Art frame={frame} rate={0.2}>
          <Ray frame={frame} x={286} y={1742} scale={0.72} facing={1} emotion="angry" pose="stand" {...rayVoice} />
          <Dee frame={frame} x={806} y={1734} scale={0.7} {...deeVoice} />
        </Art>
        {night}
        <InstitutionPlate
          frame={frame - at(9)}
          text={'"Interim letters notifying owners of the safety risk are expected to be mailed August 03, 2026. Additional letters will be sent once the remedy is available."'}
        />
      </Sequence>

      {/* ---------- S7  THE BUTTON: the receipt. 51.28 - 55.62 ----------
          The push STOPS. This is the only locked frame in the episode, which is
          what makes it read as evidence. It sits OUTSIDE NightGrade on purpose:
          the cold cast and black floor would drag PAPER to muddy blue-grey on
          the one frame that has to look like real paper. */}
      <Sequence from={at(CUT_ON[6])} durationInFrames={shot(6)}>
        <AbsoluteFill style={{background: BRAND.PAPER}}>
          <div style={{
            position: 'absolute', left: 74, right: 74, top: 372,
            fontFamily: BODY, color: BRAND.INK,
          }}>
            <div style={{fontSize: 23, letterSpacing: '0.28em', opacity: 0.56}}>
              NATIONAL HIGHWAY TRAFFIC SAFETY ADMINISTRATION
            </div>
            <div style={{
              fontSize: 52, fontFamily: HEAD, fontWeight: 900,
              marginTop: 14, lineHeight: 1.1,
            }}>
              SAME DEFECT. TWICE.
            </div>
          </div>

          {/* Two records, identical in weight. No arrow, no arithmetic. */}
          <div style={{position: 'absolute', left: 74, right: 74, top: 610}}>
            <div style={{
              borderLeft: `10px solid ${BRAND.CARBON}`, paddingLeft: 26,
              opacity: interpolate(frame - at(10), [4, 12], [0, 1],
                {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
            }}>
              <div style={{fontFamily: BODY, fontSize: 27, letterSpacing: '0.18em', color: BRAND.INK, opacity: 0.62}}>
                CAMPAIGN 25V691000
              </div>
              <div style={{display: 'flex', alignItems: 'baseline', gap: 24, marginTop: 6}}>
                <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 82, color: BRAND.INK}}>43,438</div>
                <div style={{fontFamily: BODY, fontSize: 34, color: BRAND.INK, opacity: 0.68}}>OCT 2025</div>
              </div>
            </div>

            <div style={{
              marginTop: 44, borderLeft: `10px solid ${BRAND.CARBON}`, paddingLeft: 26,
              opacity: interpolate(frame - at(10), [16, 24], [0, 1],
                {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
            }}>
              <div style={{fontFamily: BODY, fontSize: 27, letterSpacing: '0.18em', color: BRAND.INK, opacity: 0.62}}>
                CAMPAIGN 26V415000
              </div>
              <div style={{display: 'flex', alignItems: 'baseline', gap: 24, marginTop: 6}}>
                <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 82, color: BRAND.INK}}>66,383</div>
                <div style={{fontFamily: BODY, fontSize: 34, color: BRAND.INK, opacity: 0.68}}>JUN 2026</div>
              </div>
            </div>
          </div>

          {/* The verbatim, in sentence case, because the document must read as a
              document and not as a title card. */}
          <div style={{
            position: 'absolute', left: 74, right: 74, top: 1170,
            fontFamily: BODY, fontSize: 46, lineHeight: 1.4, color: BRAND.INK,
            opacity: interpolate(frame - at(10), [26, 34], [0, 0.9],
              {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
          }}>
            "Any vehicles previously repaired under 25V691 must have the new remedy completed."
          </div>

          {/* THE ONE STAMP. The only BRAND.STAMP red in the episode. */}
          <Stamp frame={frame - at(10) - s(1.66)} fps={fps} x={742} y={790} rotate={-12}>
            <div style={{fontSize: 66, border: '8px solid currentColor', padding: '8px 24px'}}>
              AGAIN
            </div>
          </Stamp>
        </AbsoluteFill>
      </Sequence>

      {/* Captions ride everything except the button and the end card: the receipt
          is evidence and must not be covered by burned-in type. */}
      {/* No caption under the Institution: that character speaks as the PLATE,
          and a caption would duplicate it. Ray's closing lines get theirs back.
          The old cutoff was a frozen s(36.97) and killed the last 15 seconds. */}
      {(frame < at(9) || frame >= at(10)) && <Caption frame={frame} onLight={frame >= at(10)} />}

      {/* End card: case number and the promise. Nothing else. INK, not red. */}
      <Sequence from={TAIL_AT}>
        <EndCard n={2} frame={frame - TAIL_AT} fps={fps} color={BRAND.INK} />
      </Sequence>

      {frame < at(10) && <CaseNumber n={2} y={92} color={BRAND.PAPER} />}
    </AbsoluteFill>
  );
};
