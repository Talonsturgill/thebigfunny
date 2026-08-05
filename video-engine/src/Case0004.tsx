/**
 * Case0004.tsx — THE BIG FUNNY, case 0004.
 * "A no that folds 99.7 percent of the time."
 *
 * Angle, from out/dispatch/story.json (type `number`, beat `machine-said-no`):
 * HHS OIG found UnitedHealth overturned 99.7 percent of the skilled-nursing
 * prior-authorization denials that were appealed, and that only 18 percent were
 * ever appealed. A no that folds that completely was never an answer. It was a
 * question, and the question is "are you going to argue?"
 *
 * ========================= THE FACT-CHECK GUARDS ==========================
 *
 *   NOTHING may state or imply a number of people harmed. OIG gives none. c7 is
 *   QUOTED as the report's own list of what MAY have happened to the 82 percent
 *   and is never illustrated.
 *   NOTHING may assert INTENT. OIG found the reversal rate, not a reason, and
 *   claims.json cuts motive explicitly. The arithmetic is funnier than the
 *   accusation and it is also the only half that is proven.
 *   NOTHING about algorithms or AI. That is an allegation in ongoing private
 *   litigation, not an OIG finding, and neither report attributes these denials
 *   to one.
 *   NO NAMED INDIVIDUAL. The target is the institution, always.
 *   THE BACK OFFICE IS NEVER DRAWN. `ApertureDepth` is unlit depth and nothing
 *   else, because nothing in the record describes what is back there.
 *
 * ============================ THE VISUAL SYSTEM ===========================
 * Diverges from 0001, 0002 and 0003 on every axis in ledger/artwork.json:
 *   world             THE WINDOW. Not the machine and not the office: the room
 *                     the machine makes you sit in.
 *   hero_structure    a service window at COUNTER HEIGHT, human scale.
 *   atmosphere        flat overhead fluorescent, no falloff, no moving shadow.
 *   palette_family    municipal oxblood and cream.
 *   continuity_device THE BELL. In frame from second one, untouched for twenty
 *                     seconds, and the last thing on screen still unrung.
 *   camera_language   SHOT / REVERSE at seated eye height, with exactly ONE
 *                     wide. The show has never cut a conversation before,
 *                     because until 2026-08-05 the cast were too small to cut
 *                     to. `face_size.py` is the reason this episode is staged
 *                     the way it is.
 *
 * SELF-TIMED, like 0001 through 0003: the Sequences carry frame numbers from the
 * FITTED VO times, so there is no episode_props.json for this composition.
 *
 * MOUNTING CONTRACT: everything from src/lib/ that returns SVG MUST be inside
 * <svg viewBox=...>. brand.tsx and GradeLayer are HTML and MUST stay outside it.
 */
import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {z} from 'zod';
import {Ray, Dee, watchSpeaker, gestureOnLines, RAY_TELL, DEE_TELL} from './lib/cast';
import type {Emotion} from './lib/Figure';
import {Wordmark, CaseNumber, EndCard, Stamp, BRAND} from './lib/brand';
import {GradeLayer} from './lib/lighting';
import {
  WaitingRoomBG, ServiceWindow, CounterBell, ChairRow, StampPair, OIGPlate,
  WallClock, WINDOW, CAST_TO_COUNTER,
} from './lib/window';
import {entrance, holdPayoff, SNAP} from './lib/motion';
import {CAPTIONS, TOTAL as TOTAL_S} from './case0004_captions';
import {emotionAt} from './case0004_faces';

export const case0004Schema = z.object({total: z.number().optional()});

const FPS = 30;
const W = 1080;
const H = 1920;
const s = (sec: number) => Math.round(sec * FPS);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/** LOOK AT WHOEVER IS TALKING. Built in cast.tsx, wired in case 0003, and left
    out of the first cut of this scene entirely, which is a third of why
    motion_check found a five-second bucket with nothing happening in it. */
const RAY_LOOK = watchSpeaker(CAPTIONS, 'RAY', 1);
const DEE_LOOK = watchSpeaker(CAPTIONS, 'DEE', -1);
/** AND THEY GESTURE ON THEIR OWN LINES. Ray's tell is the point; Dee's is that
    she does not gesture, she looks. Both were built in cast.tsx for exactly the
    dead bucket motion_check found at 10-15s, where Ray talks for seven seconds
    with nothing in frame that moves. */
const RAY_POSES = gestureOnLines(CAPTIONS, 'RAY', RAY_TELL, 'stand');
const DEE_POSES = gestureOnLines(CAPTIONS, 'DEE', DEE_TELL, 'stand');

/** The counter-to-floor height the cast are scaled against. HUMAN, and the
    deliberate inverse of case 0003. See lib/window.tsx's header. */
const COUNTER_H = 620;

/** THE CAMERA. Same contract as case 0003: a shot is a POSITION, not just a
    time window, and every shot breathes unless it refuses to. */
const Cam: React.FC<{
  cx?: number; cy?: number; zoom?: number; locked?: boolean; hold?: number;
  children: React.ReactNode;
}> = ({cx = 0.5, cy = 0.5, zoom = 1, locked = false, hold, children}) => {
  const sf = useCurrentFrame();
  const t = sf / FPS;
  const HOLD_S = 0.6;
  const held = hold !== undefined && holdPayoff(sf, FPS, s(hold), HOLD_S) === 1;
  const te = hold === undefined || t < hold ? t : held ? hold : t - HOLD_S;
  const ease = 1 - Math.pow(1 - Math.min(1, te / 4.2), 3);
  const push = locked ? 1 : 1 + 0.045 * ease + 0.009 * te;
  const slideX = locked ? 0 : 9 * ease + 2.4 * te;
  return (
    <g transform={
      `translate(${W / 2 + slideX},${H / 2}) scale(${zoom * push}) ` +
      `translate(${-W * cx},${-H * cy})`
    }>
      {children}
    </g>
  );
};

const Shot: React.FC<{from: number; to: number; children: React.ReactNode}> = ({
  from, to, children,
}) => (
  <Sequence from={s(from)} durationInFrames={s(to) - s(from)} layout="none">
    {children}
  </Sequence>
);

/** Stand a figure ON a line. Figure draws downward from its crown and is 680
    local units tall; see the note in Case0003.tsx, which was read wrong three
    separate times before it was measured off a render. */
const stand = (crownPx: number, x: number, groundY: number) => ({
  x, y: groundY - crownPx, scale: crownPx / 680,
});

/** The cast, wired to the generated face track so nobody holds an expression. */
const Cast: React.FC<{
  f: number; crown: number; ground: number; rayX: number; deeX: number;
  /** A single pose HOLDS and overrides the gesture track. Omit it and the
      figure gestures on its own lines (Figure.pose takes Pose | PoseTrack). */
  rayPose?: 'stand' | 'arms-crossed' | 'point' | 'panic' | 'raise';
  deePose?: 'stand' | 'arms-crossed' | 'point' | 'panic' | 'raise';
  show?: 'both' | 'ray' | 'dee';
}> = ({f, crown, ground, rayX, deeX, rayPose, deePose, show = 'both'}) => (
  <>
    {show !== 'dee' && (
      <Ray frame={f} {...stand(crown, rayX, ground)} look={RAY_LOOK}
           emotion={emotionAt('RAY', f) as Emotion} pose={rayPose ?? RAY_POSES} />
    )}
    {show !== 'ray' && (
      <Dee frame={f} {...stand(crown, deeX, ground)} look={DEE_LOOK}
           emotion={emotionAt('DEE', f) as Emotion} pose={deePose ?? DEE_POSES} />
    )}
  </>
);

export const Case0004: React.FC<z.infer<typeof case0004Schema>> = () => {
  const f = useCurrentFrame();
  const t = f / FPS;

  // THE SHUTTER. Down at the top of the film, and it goes up ONCE, on the bell,
  // and never comes back down. That single parameter is the episode: the no is
  // only a no until somebody touches the thing on the counter.
  const shut = interpolate(t, [0, 0.9, 20.82, 21.35], [0.55, 1, 1, 0], clamp);
  // THE BELL. Struck at 20.82, on "Are you gonna argue." Note the shutter above
  // is already moving at 20.82 too: world.json's handoff says the hand and the
  // rising curtain must be in ONE FRAME, because the point is that there is no
  // time between them.
  const struck = interpolate(t, [20.75, 20.9, 21.6], [0, 1, 0], clamp);

  const counterY = H * 0.62;
  const crown = COUNTER_H * CAST_TO_COUNTER;

  return (
    <AbsoluteFill style={{background: WINDOW.ink}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}
           style={{position: 'absolute', inset: 0}}>

        {/* ============================================================
            S1  0.0-3.9  THE HOOK. The shutter comes down.
            No people, no wide, no title. A word assembling itself out of
            slats, which is the only thing this room does.
            ============================================================ */}
        <Shot from={0} to={3.91}>
          <Cam cy={0.52} zoom={1.5}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * 0.18} y={H * 0.30} w={W * 0.64} h={H * 0.26}
                           shut={shut} />
            {/* THE BELL IS ALREADY HERE, at the near edge, and nobody touches
                it for twenty seconds. It is the continuity device and the
                answer, sitting in shot the entire time. */}
            <CounterBell x={W * 0.72} y={counterY} w={W * 0.12} struck={struck} />
          </Cam>
        </Shot>

        {/* ============================================================
            S2  3.9-8.6  DEE, and the show's first reverse.
            She has read it. She says the measured version first.
            ============================================================ */}
        <Shot from={3.91} to={8.56}>
          <Cam cx={0.40} cy={0.60} zoom={1.35}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * 0.42} y={H * 0.30} w={W * 0.52} h={H * 0.26} shut={shut} />
            <Cast f={f} crown={crown} ground={counterY + H * 0.30}
                  rayX={W * -0.5} deeX={W * 0.30} show="dee" />
            <CounterBell x={W * 0.66} y={counterY} w={W * 0.11} struck={struck} />
          </Cam>
        </Shot>

        {/* ============================================================
            S3  8.6-15.5  RAY, the reverse of the reverse.
            He arrives at a verdict twice: they were wrong, and then the
            number is a hundred percent with a typo.
            ============================================================ */}
        <Shot from={8.56} to={10.25}>
          <Cam cx={0.62} cy={0.60} zoom={1.4}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.92} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * -0.10} y={H * 0.30} w={W * 0.52} h={H * 0.26} shut={shut} />
            <Cast f={f} crown={crown} ground={counterY + H * 0.30}
                  rayX={W * 0.70} deeX={W * 1.5} show="ray" />
          </Cam>
        </Shot>

        {/* ============================================================
            S3b  10.3-14.6  DEE HAS THE NUMBER, SO DEE IS ON SCREEN.
            The first cut of this held on Ray's face for the four seconds
            Dee spends delivering 99.7, which is the biggest number in the
            episode, said by the person the camera was not pointed at.
            motion_check found it as a dead five-second bucket; it was a
            coverage error first and a motion problem second.
            ============================================================ */}
        <Shot from={10.25} to={14.57}>
          <Cam cx={0.38} cy={0.59}
               zoom={interpolate(t, [10.25, 14.57], [1.42, 1.55], clamp)}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * 0.44} y={H * 0.30} w={W * 0.52} h={H * 0.26} shut={shut} />
            <Cast f={f} crown={crown} ground={counterY + H * 0.30}
                  rayX={W * -0.5} deeX={W * 0.28} show="dee" />
          </Cam>
        </Shot>

        {/* ============================================================
            S3c  14.6-15.5  BACK ON RAY, silent, taking it.
            A beat with no line in it. He gets the number and says nothing
            for nine tenths of a second, which is the only place in the film
            anybody is allowed to just sit there.
            ============================================================ */}
        <Shot from={14.57} to={15.46}>
          <Cam cx={0.64} cy={0.58}
               zoom={interpolate(t, [14.57, 15.46], [1.62, 1.70], clamp)}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <Cast f={f} crown={crown * 1.15} ground={counterY + H * 0.32}
                  rayX={W * 0.66} deeX={W * 1.6} show="ray" />
          </Cam>
        </Shot>

        {/* ============================================================
            S4  15.5-17.8  THE STAMPS. Two seconds, no dialogue over them
            except the tail of Ray's typo line.
            NO and YES in one tray, worn to exactly the same shine. The same
            hand does both, all day, to the same piece of paper. An earlier
            design had the YES still in its wrapper: funnier, and FALSE.
            ============================================================ */}
        <Shot from={15.46} to={17.80}>
          <Cam cx={0.46} cy={0.63} zoom={2.6}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <StampPair x={W * 0.30} y={counterY - H * 0.005} w={W * 0.42} />
          </Cam>
        </Shot>

        {/* ============================================================
            S5  17.8-20.8  RAY SAYS THE UNSAYABLE, close.
            "So it was never a no. It was a question." This is a character's
            verdict, not a claim the film makes, and keeping it in his mouth
            rather than in a caption is what keeps the episode inside the
            fact-check gate. It gets the closest framing so far.
            ============================================================ */}
        <Shot from={17.80} to={20.82}>
          <Cam cx={0.58} cy={0.58} zoom={1.9}>
            <WaitingRoomBG f={f} w={W} h={H} light={0.98} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <Cast f={f} crown={crown * 1.35} ground={counterY + H * 0.36}
                  rayX={W * 0.56} deeX={W * 1.6} show="ray" />
          </Cam>
        </Shot>

        {/* ============================================================
            S6  20.8-25.6  THE TURN. The hand and the shutter, ONE FRAME.
            He rings it on "are you gonna argue" and the curtain is already
            going up before his hand leaves the dome. The no had no mass.
            DO NOT CUT BETWEEN THESE. world.json's handoff, in capitals: if
            the board cuts, the gag becomes cause and effect over time, and
            the entire point is that there is no time.
            The camera HOLDS for the doctrine band after the curtain lands.
            ============================================================ */}
        <Shot from={20.82} to={25.61}>
          <Cam cx={0.52} cy={0.56} zoom={1.28} hold={0.75}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * 0.16} y={H * 0.30} w={W * 0.60} h={H * 0.26} shut={shut} />
            <Cast f={f} crown={crown} ground={counterY + H * 0.30}
                  rayX={W * 0.30} deeX={W * 1.5} show="ray" rayPose="point" />
            <CounterBell x={W * 0.78} y={counterY} w={W * 0.13} struck={struck} />
          </Cam>
        </Shot>

        {/* ============================================================
            S7  25.6-32.8  THE WIDE, and the only one in the film.
            Every chair occupied and not one of those people at the counter.
            The 82 percent, drawn, never named in dialogue. The seated
            figures are SILHOUETTES and stay silhouettes: give one a face and
            the shot becomes a story about that person.
            ============================================================ */}
        <Shot from={25.61} to={32.82}>
          <Cam cy={0.54} zoom={interpolate(t, [25.61, 32.82], [1.0, 1.075], clamp)}>
            <WaitingRoomBG f={f} w={W} h={H} wear={0.85} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * 0.30} y={H * 0.30} w={W * 0.46} h={H * 0.22} shut={shut} />
            <CounterBell x={W * 0.84} y={counterY} w={W * 0.09} struck={struck} />
            {/* y 0.86 -> 0.795: at 0.86 the seat backs ran straight through the
                burned-in caption, which sits at bottom 190. */}
            {/* CAST FIRST, CHAIRS OVER THEM. The chairs are nearer camera than
                the counter, so drawing the cast last put two people standing in
                front of the front row and flattened the room. Lapping the
                chairs over their legs is the only depth cue a flat SVG has. */}
            <Cast f={f} crown={crown * 0.62} ground={counterY + H * 0.19}
                  rayX={W * 0.20} deeX={W * 0.34} />
            <ChairRow x={W * 0.04} y={H * 0.795} w={W * 0.92} seats={6} occupied={6} />
          </Cam>
        </Shot>

        {/* ============================================================
            S8  32.8-35.7  RAY names the paint.
            "It's on the list like an option." He is pointing at the SHAPE of
            the sentence, not re-quoting it: the horror is item three, in the
            same tone as items one and two.
            ============================================================ */}
        <Shot from={32.82} to={35.65}>
          <Cam cx={0.60} cy={0.58} zoom={1.85}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <Cast f={f} crown={crown * 1.3} ground={counterY + H * 0.35}
                  rayX={W * 0.60} deeX={W * 1.6} show="ray" />
          </Cam>
        </Shot>

        {/* ============================================================
            S9  35.7-39.9  THE INSTITUTION ANSWERS, and has no face.
            Its line comes off a laminated notice taped to the slats. Nothing
            brightens, no aperture irises, no part of the wall turns to
            camera. It answers a question nobody asked, politely.
            ============================================================ */}
        <Shot from={35.65} to={39.95}>
          {/* NOT `locked`. The shutter settles by 36.2 and then this shot was a
              held drawing for three and a half seconds, which is the identical
              failure case 0003's S12 had on the Institution's only line, found
              the same morning. The fix is the same and the reasoning is the
              same: the machine must not emote, and refusing to editorialise is
              a rule about the SUBJECT, never a licence for a frozen frame. So
              the camera crawls across the slats instead. */}
          <Cam cx={interpolate(t, [35.65, 39.95], [0.46, 0.52], clamp)}
               cy={0.44} zoom={interpolate(t, [35.65, 39.95], [2.10, 2.22], clamp)}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <ServiceWindow x={W * 0.20} y={H * 0.30} w={W * 0.58} h={H * 0.26}
                           shut={interpolate(t, [35.65, 36.2], [0, 0.62], clamp)}
                           notice />
          </Cam>
        </Shot>

        {/* ============================================================
            S10  39.9-43.7  RAY'S VERDICT, the closest framing in the film.
            He stops arguing with it and states the record instead.
            ============================================================ */}
        <Shot from={39.95} to={43.73}>
          <Cam cx={0.54} cy={0.55} zoom={2.15}>
            <WaitingRoomBG f={f} w={W} h={H} light={0.96} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <Cast f={f} crown={crown * 1.5} ground={counterY + H * 0.40}
                  rayX={W * 0.52} deeX={W * 1.7} show="ray" />
          </Cam>
        </Shot>

        {/* ============================================================
            S11  43.7-48.9  DEE, the receipt.
            She has the 2018 finding. She is the one who cites the date.
            ============================================================ */}
        <Shot from={43.73} to={48.86}>
          <Cam cx={0.42} cy={0.57} zoom={1.75}>
            <WaitingRoomBG f={f} w={W} h={H} />
            <WallClock x={W * 0.13} y={H * 0.235} r={W * 0.075} f={f} fps={FPS} />
            <Cast f={f} crown={crown * 1.28} ground={counterY + H * 0.34}
                  rayX={W * -0.6} deeX={W * 0.42} show="dee" deePose="raise" />
          </Cam>
        </Shot>

        {/* ============================================================
            S12  48.9-END  THE BUTTON. The document, and Ray does not win.
            2018 above 2026, both highlighted, so the receipt reads as a
            COMPARISON and not as a citation: eight years of federal
            attention and the number went UP. The bell is still in frame at
            the edge, still unrung by anybody else.
            ============================================================ */}
        <Shot from={48.86} to={TOTAL_S}>
          <rect x={0} y={0} width={W} height={H} fill={WINDOW.ink} />
          {(() => {
            const e = entrance(f, FPS, s(0.15), {drop: H * 0.10, preset: SNAP});
            return (
              <g transform={`translate(0,${e.dy})`}>
                <OIGPlate w={W} h={H * 0.74}
                          hiA={interpolate(t, [49.6, 50.3], [0, 1], clamp)}
                          hiB={interpolate(t, [50.4, 51.1], [0, 1], clamp)} />
              </g>
            );
          })()}
          <CounterBell x={W * 0.88} y={H * 0.88} w={W * 0.12} struck={0} />
        </Shot>
      </svg>

      {/* ==== HTML layers, OUTSIDE the svg, per the mounting contract. ==== */}

      {/* THE WORDMARK stamps at 3.0s over the cream wall above the dado, which
          is the one light surface in the room. Multiply dies on the ochre. */}
      {t >= 2.9 && t < 3.91 && (
        <Wordmark frame={f - s(2.95)} fps={FPS} x={540} y={620} scale={0.94}
                  color={BRAND.INK} blend="multiply" />
      )}

      {/* THE ONE STAMP IN THE EPISODE, on the button plate. */}
      {t >= 50.9 && (
        <Stamp frame={f - s(50.95)} fps={FPS} x={620} y={1140} rotate={-7} scale={3.0}>
          ALLEGED
        </Stamp>
      )}

      {t < 8.0 && <CaseNumber n={4} y={92} color={BRAND.INK} />}

      <CaptionLayer f={f} />

      <GradeLayer f={f} bloom={0.10} vignette={0.42} grain={0.05} warmth={0.06} />

      {t > TOTAL_S - 1.5 && (
        <EndCard n={4} frame={f - s(TOTAL_S - 1.5)} fps={FPS} color={BRAND.INK} />
      )}
    </AbsoluteFill>
  );
};

/** Burned-in captions, from the forced-aligned track. */
const CaptionLayer: React.FC<{f: number}> = ({f}) => {
  const t = f / FPS;
  const cue = CAPTIONS.find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  const speaker = (cue as {speaker?: string}).speaker;
  const color = speaker === 'DEE' ? '#FBE9EC'
    : speaker === 'INSTITUTION' ? '#BFE7E2' : BRAND.PAPER;
  return (
    <div style={{
      position: 'absolute', left: 0, right: 0, bottom: 190,
      padding: '0 64px', textAlign: 'center',
      fontFamily: 'Archivo Black, Impact, sans-serif',
      fontSize: 58, lineHeight: 1.14, color,
      textShadow: '0 3px 0 rgba(0,0,0,0.55)',
    }}>
      {cue.text}
    </div>
  );
};
