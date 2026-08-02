/**
 * Case0003.tsx — THE BIG FUNNY, case 0003.
 * "You Are Not The Customer."
 *
 * Angle (who-benefits, exactly one step): you are not the tenant screening
 * company's customer, the landlord is, and that one step explains every
 * allegation in US v. RentGrow.
 *
 * Every factual string on screen traces to out/dispatch/claims.json.
 *
 * GUARDS FROM THE FACT-CHECK GATE, all load-bearing:
 *   1. c10 is CUT. NOTHING may state or imply a number of people affected. The
 *      FTC does not give one and the complaint PDF has no text layer to check.
 *   2. c11 is CUT. No named individual was denied a home. Ray is the show's
 *      everyman reacting, never a case study, and no on-screen card claims one.
 *   3. c12 is CUT. This is a SETTLEMENT and a settlement is not an admission.
 *      Every card says ALLEGED. Saying otherwise is defamatory, not edgy.
 *
 * VISUAL SYSTEM (diverges from cases 0001 and 0002 on all five hard axes in
 * ledger/artwork.json):
 *   hero_structure   a stairwell landing with the shaft climbing BEHIND the
 *                    pair. Vertical emphasis, not case 0001's flat cabinet wall
 *                    and not case 0002's horizontal one-point recession. A
 *                    corridor of receding doors would have been 0002 in a hat.
 *   atmosphere       hard skylight bars falling DOWN the shaft, dust in the
 *                    light. Not fluorescent, not night exterior.
 *   palette_family   putty green / oxblood / brass. Not manila-carbon, not
 *                    night steel-sodium.
 *   continuity_device EDGE-TEASE. The door number sits at the frame edge and the
 *                    episode ends on a different one.
 *   camera_language  ORBIT. The camera arcs around the landing rather than
 *                    pushing into it or locking off.
 *
 * ONE-STAMP AUDIT: the Wordmark is BRAND.PAPER, the EndCard is BRAND.INK, and
 * the only BRAND.STAMP in the episode is the stamp on the filing at the button.
 *
 * MOUNTING CONTRACT: everything from src/lib/ that returns SVG MUST be inside
 * <svg viewBox=...>. brand.tsx and GradeLayer are HTML divs and MUST stay
 * outside it.
 */
import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {z} from 'zod';
import {Ray, Dee} from './lib/cast';
import type {Emotion} from './lib/Character';
import {Wordmark, CaseNumber, EndCard, Highlighter, Stamp, BRAND} from './lib/brand';
import {StairwellBG} from './lib/biomes';
import {GradeLayer} from './lib/lighting';
import {CAPTIONS, speakerAt, TOTAL as TOTAL_S} from './case0003_captions';
import {openAt, spreadAt} from './case0003_mouth';
import {emotionAt} from './case0003_faces';

export const case0003Schema = z.object({total: z.number().optional()});

const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);
const TOTAL = s(TOTAL_S);
const TAIL_AT = TOTAL - s(1.5);

/** Shot ladder as CUE INDICES, never hand-typed seconds. A re-fit of the VO
 *  retimes the picture for free; see the note in Case0002. */
const CUT_ON = [0, 3, 5, 6, 9, 11, 12, 14];

/* CUT_ON is hand-maintained INDICES into a generated array, which is the one
   seam the derived-timing system does not close: shortening the script silently
   orphans a cut point, TypeScript cannot see an out-of-range index, and the
   render dies mid-frame with "Cannot read properties of undefined". That is
   exactly what happened when this script went from 19 lines to 16. Fail at
   module load with a sentence that says what to do instead. */
if (CUT_ON.some((c) => c >= CAPTIONS.length)) {
  throw new Error(
    `Case0003 CUT_ON references cue ${CUT_ON.filter((c) => c >= CAPTIONS.length).join(', ')} ` +
    `but the script only has ${CAPTIONS.length} lines (0-${CAPTIONS.length - 1}). ` +
    `The script was rewritten and the shot ladder was not. Update CUT_ON.`);
}

const at = (cue: number) => s(CAPTIONS[cue].start);
const shot = (i: number) =>
  (i + 1 < CUT_ON.length ? at(CUT_ON[i + 1]) : TAIL_AT) - at(CUT_ON[i]);

const HEAD = 'Arial Black, DejaVu Sans, FreeSans, sans-serif';
const BODY = 'Arial, DejaVu Sans, FreeSans, sans-serif';

/**
 * THE ORBIT. The episode's continuity device and its point of difference from
 * case 0002's push.
 *
 * A push scales about a vanishing point and reads as walking forward. An orbit
 * TRANSLATES the plate laterally while rotating it a degree or two about a point
 * behind the figures, so the back wall slides against them and you feel the
 * camera travelling around the landing rather than into it. `rate` gives each
 * layer its own share, which is what makes it parallax instead of a pan.
 */
const Orbit: React.FC<{frame: number; rate?: number; children: React.ReactNode}> = ({
  frame, rate = 1, children,
}) => {
  // MEASURED, not guessed. At the first amplitude the plate travelled 3.5 px/s
  // and the figures 0.8 to 1.2 px/s across the whole episode, which is below
  // what anyone perceives as a camera move: the flow critic called the orbit
  // invisible and it was, arithmetically. 260px puts the plate near 9.5 px/s and
  // the near figures around 2 to 3, so the wall visibly slides against them.
  // The differential is what makes it an orbit rather than a pan.
  const a = interpolate(frame, [0, TOTAL], [-1, 1], {extrapolateRight: 'clamp'});
  const dx = a * 260 * rate;
  const rot = a * 2.4 * rate;
  return (
    <svg width="1080" height="1920" viewBox="0 0 1080 1920"
         style={{position: 'absolute', inset: 0}}>
      <g transform={`translate(${dx},0) rotate(${rot} 540 1240)`}>{children}</g>
    </svg>
  );
};

const SPEAKER_TINT: Record<string, string> = {
  RAY: '#F2B36B',
  DEE: '#8FD3E8',
  INSTITUTION: '#C9D2D8',
};

/** Burned-in caption from the MEASURED VO timings. The show is watched muted
 *  more often than not, so this is not a subtitle, it is the script. */
const Caption: React.FC<{frame: number; onLight?: boolean}> = ({frame, onLight = false}) => {
  const t = frame / FPS;
  const cue = CAPTIONS.find((c) => t >= c.start && t <= c.end + 0.14);
  if (!cue) return null;
  const tint = SPEAKER_TINT[cue.who] ?? BRAND.PAPER;
  return (
    <div style={{position: 'absolute', left: 54, right: 54, top: 1486, textAlign: 'center'}}>
      <div style={{
        fontFamily: BODY, fontSize: 27, fontWeight: 700, letterSpacing: '0.28em',
        color: onLight ? 'rgba(16,20,35,0.66)' : tint, marginBottom: 10,
        textShadow: onLight ? 'none' : '0 2px 0 rgba(16,20,35,0.95), 0 0 16px rgba(16,20,35,0.9)',
      }}>{cue.who}</div>
      <div style={{
        fontFamily: HEAD, fontWeight: 900, fontSize: 55, lineHeight: 1.14,
        color: onLight ? BRAND.INK : BRAND.PAPER,
        textShadow: onLight ? 'none' : '0 4px 0 rgba(16,20,35,0.92), 0 0 26px rgba(16,20,35,0.8)',
        letterSpacing: '-0.01em',
      }}>{cue.text}</div>
    </div>
  );
};

/** A notice taped to the door. The INSTITUTION speaks here and nowhere else, and
 *  it has no face, no voice of its own and no opinion: it is a process quoting
 *  the standard it is alleged to have missed. */
const Notice: React.FC<{frame: number}> = ({frame}) => {
  const op = interpolate(frame, [0, 7], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const dy = interpolate(frame, [0, 10], [18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{
      position: 'absolute', left: 132, right: 132, top: 470 + dy, opacity: op,
      background: BRAND.PAPER, color: BRAND.INK, transform: 'rotate(-1.2deg)',
      border: '2px solid rgba(16,20,35,0.5)', boxShadow: '5px 7px 0 rgba(16,20,35,0.34)',
      padding: '30px 34px 34px',
    }}>
      <div style={{fontFamily: BODY, fontSize: 26, letterSpacing: '0.22em', opacity: 0.72}}>
        THE STANDARD IT IS ALLEGED TO HAVE MISSED
      </div>
      <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 58, lineHeight: 1.1, marginTop: 14}}>
        REASONABLE PROCEDURES TO ASSURE MAXIMUM POSSIBLE ACCURACY
      </div>
      <div style={{fontFamily: BODY, fontSize: 25, marginTop: 18, opacity: 0.66}}>
        Fair Credit Reporting Act
      </div>
    </div>
  );
};

export const Case0003: React.FC<z.infer<typeof case0003Schema>> = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  /* The SPEAKER's mouth runs on their own voice, shaped on two axes (openness
     from loudness, spread from the spectral centroid). The LISTENER's mouth is
     shut and their idle is damped, so the only real motion belongs to whoever is
     talking. Expressions come from the FACE TRACK, authored per line in the
     script; never set `emotion=` as a per-shot constant here, face_check.py
     exists to catch that. */
  const who = speakerAt(frame / FPS);
  const spr = spreadAt(frame);
  const rayVoice = {
    mouth: who === 'RAY' ? openAt(frame) : undefined,
    mouthSpread: spr,
    idleGain: who === 'RAY' ? 1 : 0.32,
    emotion: emotionAt('RAY', frame) as Emotion,
  };
  const deeVoice = {
    mouth: who === 'DEE' ? openAt(frame) : undefined,
    mouthSpread: spr,
    idleGain: who === 'DEE' ? 1 : 0.32,
    emotion: emotionAt('DEE', frame) as Emotion,
  };

  const set = <StairwellBG f={frame} light={0.85} doorNo="4C" />;
  const grade = <GradeLayer f={frame} bloom={0.16} vignette={0.5} grain={0.06} warmth={0.05} />;

  return (
    <AbsoluteFill style={{backgroundColor: '#6d7767'}}>

      {/* ---------- S1  the hook, flat. Both of them, the door shut behind. ---------- */}
      <Sequence from={at(CUT_ON[0])} durationInFrames={shot(0)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.34}>
          <Ray frame={frame} x={392} y={1592} scale={1.42} {...rayVoice} />
          <Dee frame={frame} x={694} y={1586} scale={1.44} {...deeVoice} />
        </Orbit>
        {grade}
      </Sequence>

      {/* the wordmark STAMPS after the hook, never before it */}
      <Sequence from={s(2.0)} durationInFrames={s(2.4)}>
        <Wordmark frame={frame - s(2.0)} fps={fps} x={540} y={470} scale={0.9}
                  color={BRAND.PAPER} blend="normal" />
      </Sequence>

      {/* ---------- S2  closer. Dee lays it out, Ray is already narrowing. ---------- */}
      <Sequence from={at(CUT_ON[1])} durationInFrames={shot(1)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.34}>
          <Ray frame={frame} x={372} y={1672} scale={1.72} {...rayVoice} />
          <Dee frame={frame} x={724} y={1664} scale={1.74} {...deeVoice} />
        </Orbit>
        {grade}
      </Sequence>

      {/* ---------- S3  THE PIVOT. "They counted the same eviction twice."
           Dee dead flat and large. The funniest verified fact is the turn the
           episode is built to arrive at, not the fourth item in a data block. */}
      <Sequence from={at(CUT_ON[2])} durationInFrames={shot(2)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.22}>
          <Dee frame={frame} x={598} y={1806} scale={2.46} {...deeVoice} />
        </Orbit>
        {grade}
      </Sequence>

      {/* ---------- S4  and we sit on RAY. The listener's face is the joke. ---------- */}
      <Sequence from={at(CUT_ON[3])} durationInFrames={shot(3)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.22}>
          <Ray frame={frame} x={508} y={1822} scale={2.52} {...rayVoice} />
        </Orbit>
        {grade}
      </Sequence>

      {/* ---------- S5  they cannot even see where the record came from ---------- */}
      <Sequence from={at(CUT_ON[4])} durationInFrames={shot(4)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.34}>
          <Ray frame={frame} x={352} y={1700} scale={1.82} {...rayVoice} />
          <Dee frame={frame} x={742} y={1692} scale={1.84} {...deeVoice} />
        </Orbit>
        {grade}
      </Sequence>

      {/* ---------- S6  Ray states the ANGLE as a verdict, not an argument ---------- */}
      <Sequence from={at(CUT_ON[5])} durationInFrames={shot(5)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.2}>
          <Ray frame={frame} x={470} y={1846} scale={2.72} {...rayVoice} />
        </Orbit>
        {grade}
      </Sequence>

      {/* ---------- S7  THE INSTITUTION. A notice on a shut door. No face. ---------- */}
      <Sequence from={at(CUT_ON[6])} durationInFrames={shot(6)}>
        <Orbit frame={frame} rate={1}>{set}</Orbit>
        <Orbit frame={frame} rate={0.34}>
          <Ray frame={frame} x={300} y={1730} scale={1.5} {...rayVoice} />
          <Dee frame={frame} x={790} y={1724} scale={1.52} {...deeVoice} />
        </Orbit>
        <Notice frame={frame - at(CUT_ON[6])} />
        {grade}
      </Sequence>

      {/* ---------- S8  THE BUTTON. The real filing, and the camera stops. ---------- */}
      <Sequence from={at(CUT_ON[7])}>
        <AbsoluteFill style={{backgroundColor: BRAND.PAPER}} />
        <div style={{position: 'absolute', left: 84, right: 84, top: 300, color: BRAND.INK}}>
          <div style={{fontFamily: BODY, fontSize: 27, letterSpacing: '0.2em', opacity: 0.66}}>
            UNITED STATES DISTRICT COURT, DISTRICT OF COLUMBIA
          </div>
          <div style={{fontFamily: HEAD, fontWeight: 900, fontSize: 76, lineHeight: 1.04, marginTop: 16}}>
            UNITED STATES<br />v. RENTGROW, INC.
          </div>
          <div style={{
            fontFamily: BODY, fontSize: 34, marginTop: 30,
            opacity: interpolate(frame - at(CUT_ON[7]), [6, 16], [0, 0.82],
                                 {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
          }}>
            Civil action 1:26-cv-02415 &nbsp;/&nbsp; filed July 9, 2026
          </div>
          <div style={{
            marginTop: 54,
            opacity: interpolate(frame - at(CUT_ON[7]), [20, 30], [0, 1],
                                 {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
          }}>
            <div style={{fontFamily: BODY, fontSize: 27, letterSpacing: '0.2em', opacity: 0.66}}>
              CIVIL PENALTY
            </div>
            <div style={{position: 'relative', display: 'inline-block', marginTop: 8}}>
              <Highlighter frame={frame - at(CUT_ON[7]) - 26} width={430} height={82} x={-12} y={14} />
              <div style={{position: 'relative', fontFamily: HEAD, fontWeight: 900, fontSize: 96}}>
                $2,250,000
              </div>
            </div>
          </div>
          <div style={{
            fontFamily: BODY, fontSize: 30, lineHeight: 1.34, marginTop: 56,
            opacity: interpolate(frame - at(CUT_ON[7]), [34, 44], [0, 0.72],
                                 {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
          }}>
            Settled. A settlement is not an admission.<br />
            Every claim above is an FTC ALLEGATION.
          </div>
        </div>
        {/* the ONE stamp in the episode */}
        {/* The ONE stamp in the episode. scale is explicit: at the default it
            rendered as small red text rather than a rubber stamp, which spends
            the show's single red token on something nobody reads. */}
        <Stamp frame={frame - at(CUT_ON[7]) - s(1.9)} fps={fps} x={600} y={1180}
               rotate={-11} scale={3.4}>
          ALLEGED
        </Stamp>
      </Sequence>

      {/* Captions everywhere except under the Institution's notice, which already
          carries its words. Ray's closing lines get theirs back, inverted for the
          light button page. */}
      {(frame < at(CUT_ON[6]) || frame >= at(CUT_ON[7])) &&
        <Caption frame={frame} onLight={frame >= at(CUT_ON[7])} />}

      <Sequence from={TAIL_AT}>
        <EndCard n={3} frame={frame - TAIL_AT} fps={fps} color={BRAND.INK} />
      </Sequence>

      {frame < at(CUT_ON[7]) && <CaseNumber n={3} y={92} color={BRAND.PAPER} />}
    </AbsoluteFill>
  );
};
