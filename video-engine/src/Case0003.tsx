/**
 * Case0003.tsx — THE BIG FUNNY, case 0003.
 * "One eviction case, counted nine times."
 *
 * REWRITTEN 2026-08-02 against out/dispatch/storyboard.json, the first board
 * produced by the Phase 4.4 director room. The previous version of this file was
 * a different episode ("You Are Not The Customer", staged in a stairwell) and it
 * is in git history if anyone wants it back.
 *
 * Angle, from out/dispatch/story.json: the report wrote the same eviction case
 * out again and again, and counted each copy as another time he was sued. It is
 * not wrong about anything. Every copy is accurate, and being accurate that many
 * times is what makes the total false.
 *
 * ========================= THE FACT-CHECK GUARDS ==========================
 * All load-bearing, all board-enforced, none of them squeamishness:
 *
 *   c10 is CUT. NOTHING may state or imply a number of people affected. The FTC
 *   does not give one.
 *   c11 is CUT. No named individual was denied a home. Ray is the show's everyman
 *   reacting, never a case study.
 *   c12 is CUT. This is a SETTLEMENT and a settlement is NOT an admission. The
 *   button carries the case caption and the word ALLEGED, and FilingPlate
 *   defaults `alleged` to true so a scene has to work to turn it off.
 *   c3 ($2.25M) is CLEARED and deliberately EXCLUDED. The verdict ledger recorded
 *   that the number reverses the irony: a settlement figure invites the viewer to
 *   read the story as resolved, and nothing cleared says the count was corrected.
 *
 *   THE ODOMETER MAY ONLY EVER DISPLAY THE NUMBER OF CARDS VISIBLE IN THE SAME
 *   FRAME. That is the ALLEGED guard drawn rather than written down: the wheel
 *   captions the picture and asserts nothing beyond it. It tops out at 9.
 *
 * ============================ THE VISUAL SYSTEM ===========================
 * Diverges from cases 0001 and 0002 on every axis in ledger/artwork.json:
 *   world             THE COUNT ROOM, the inside of the machine that assembles
 *                     the report. Not a room the story is discussed in.
 *   hero_structure    a flat machine FACE parallel to camera. Not 0001's cabinet
 *                     wall, not 0002's one-point recession, not a stairwell.
 *   atmosphere        ONE hard practical over the intake and nothing else. Every
 *                     other surface falls to the crushed floor.
 *   palette_family    enamel teal / brass. Not manila-carbon, not night steel.
 *   continuity_device EDGE-TEASE. The plated chute sits at the lower right frame
 *                     edge from second five and does nothing for thirty-eight
 *                     seconds, which is what makes S15 a reveal and not an
 *                     introduction.
 *   camera_language   HEIGHT LADDER. The camera changes ELEVATION rather than
 *                     arcing or pushing: floor, eye, crane, floor again. S7 and
 *                     S8 are the highest and lowest cameras in the film, back to
 *                     back, so the fall itself is the measurement.
 *
 * ONE-STAMP AUDIT: the Wordmark stamps at 2.6s over the odometer's cream digit
 * field, which is the one light surface in the room (multiply vanishes on teal),
 * and the only BRAND Stamp in the episode is the red mark on the filing at the
 * button.
 *
 * MOUNTING CONTRACT: everything from src/lib/ that returns SVG MUST be inside
 * <svg viewBox=...>. brand.tsx and GradeLayer are HTML and MUST stay outside it.
 *
 * SELF-TIMED, like cases 0001 and 0002: the Sequences below carry their own
 * frame numbers from the FROZEN script times the board is cut to, so there is no
 * episode_props.json for this composition and build_scenes.py's scene map is
 * never consulted.
 */
import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame} from 'remotion';
import {z} from 'zod';
import {Ray, Dee} from './lib/cast';
import type {Emotion} from './lib/Figure';
import {Wordmark, CaseNumber, EndCard, Stamp, BRAND} from './lib/brand';
import {GradeLayer} from './lib/lighting';
import {TallyCounter} from './lib/props';
import {
  CountRoomBG, DocketCard, CardPile, CardChute, VerifyDie, FilingPlate,
  COUNTROOM, CAST_TO_CARD,
} from './lib/countroom';
import {CAPTIONS, speakerAt, TOTAL as TOTAL_S} from './case0003_captions';
import {emotionAt} from './case0003_faces';

export const case0003Schema = z.object({total: z.number().optional()});

const FPS = 30;
const W = 1080;
const H = 1920;
const s = (sec: number) => Math.round(sec * FPS);

/** The card long edge in the wide shots. Ray's crown is CAST_TO_CARD of this. */
const CARD_W = 620;

/**
 * FIGURE DRAWS DOWNWARD FROM ITS CROWN. lib/Figure.tsx line 59:
 * Y = {crown: 0, ... ground: 680}, so `y` is the CROWN line and a whole body is
 * 680 local units.
 *
 * The proof sheet put both of the cast off the bottom of frame by assuming a
 * -440..+10 bbox, which belongs to Character, the RETIRED crowd rig. Measured
 * off a render rather than read off the source, because reading it has now been
 * wrong three separate times. To stand somebody ON a line:
 *
 *   scale = wanted crown height / 680,  y = that line minus the crown height.
 */
const stand = (crownPx: number, x: number, groundY: number) => ({
  x, y: groundY - crownPx, scale: crownPx / 680,
});

const CASE_NO = 'C-2026-4417';
const HEAD = 'EVICTION ACTION';
/** ONE spelling of the case number, everywhere. A second spelling anywhere and
    the repetition stops reading, which is the whole thesis. */
const card = {head: HEAD, caseNo: CASE_NO};

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

/**
 * THE CAMERA, and it is the difference between a board and a render.
 *
 * The first full render of this episode put every shot at the same framing: the
 * whole wall, square on, from the same distance, eighteen times. The board's
 * camera language is a HEIGHT LADDER (floor, eye, crane, floor again) and none
 * of it existed on screen, because the set was drawn full-frame in every shot
 * with no transform. Twelve cells of a contact sheet that all look identical is
 * the owner's original complaint arriving through a different door: "the scenes
 * are boring and not actually illustrating anything".
 *
 * A shot is therefore a POSITION, not just a time window. `cy` is the height the
 * camera is at expressed in fractions of the wall, `zoom` is how close, and the
 * world is transformed under it. That makes the ladder a thing that renders
 * rather than a thing the board asserts.
 *
 * Scale about the frame CENTRE, then translate, so zooming does not also slide
 * the shot sideways. Getting that order wrong is why the S6 macro landed on the
 * odometer instead of the panel.
 */
const Cam: React.FC<{
  /** 0 = the top of the wall, 1 = the floor line. */
  cy?: number;
  /** 0 = frame centre, 1 = the right edge. */
  cx?: number;
  zoom?: number;
  children: React.ReactNode;
}> = ({cx = 0.5, cy = 0.5, zoom = 1, children}) => (
  <g transform={
    `translate(${W / 2},${H / 2}) scale(${zoom}) ` +
    `translate(${-W * cx},${-H * cy})`
  }>
    {children}
  </g>
);

/** A shot. Every one carries its own window from the board, so a retimed script
    moves one number in one place. */
const Shot: React.FC<{from: number; to: number; children: React.ReactNode}> = ({
  from, to, children,
}) => (
  <Sequence from={s(from)} durationInFrames={s(to) - s(from)} layout="none">
    {children}
  </Sequence>
);

/** The cast, wired to the generated face track so nobody holds an expression. */
const Cast: React.FC<{
  f: number; crown: number; ground: number; rayX: number; deeX: number;
  rayPose?: 'stand' | 'arms-crossed' | 'point' | 'panic' | 'raise';
  deePose?: 'stand' | 'arms-crossed' | 'point' | 'panic' | 'raise';
  show?: 'both' | 'ray' | 'dee';
}> = ({f, crown, ground, rayX, deeX, rayPose = 'arms-crossed', deePose = 'stand', show = 'both'}) => (
  <>
    {show !== 'dee' && (
      <Ray frame={f} {...stand(crown, rayX, ground)}
           emotion={emotionAt('RAY', f) as Emotion} pose={rayPose} />
    )}
    {show !== 'ray' && (
      <Dee frame={f} {...stand(crown, deeX, ground)}
           emotion={emotionAt('DEE', f) as Emotion} pose={deePose} />
    )}
  </>
);

export const Case0003: React.FC<z.infer<typeof case0003Schema>> = () => {
  const f = useCurrentFrame();
  const t = f / FPS;

  // THE COUNT. It only ever equals the cards visible in the same frame, and it
  // stops at 9 and never rolls again: S10's wheel topping out is what makes the
  // silence after it feel like something stopped rather than like a pause.
  const landed = Math.min(9, Math.max(1, Math.round(interpolate(
    t, [0.4, 7.0, 11.6, 21.2, 28.8], [1, 3, 5, 8, 9], clamp))));
  const count = String(landed).padStart(4, '0');

  // How buried the tile is. The pattern going completely IS the turn.
  const pile = interpolate(t, [4.6, 7.4, 11.6, 21.2], [0.05, 0.35, 0.75, 1], clamp);

  return (
    <AbsoluteFill style={{background: COUNTROOM.ink}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}
           style={{position: 'absolute', inset: 0}}>
        {/* ============================================================
            S1  0.0-2.4  THE HOOK. The fact drawn, at tile level.
            A court case being MANUFACTURED, at furniture size, before anyone
            has said the word report. No people, no wide, no title.
            ============================================================ */}
        <Shot from={0} to={2.4}>
          <Cam cy={0.82} zoom={1.35}>
            <CountRoomBG f={f} w={W} h={H} light={0.9} pile={0.02} />
            {/* The card is sized so BOTH legible strings sit inside the frame at
                this zoom. Cropping a case number mid-word reads as a mistake and
                not as a choice, and it is the one string the whole film asks the
                viewer to match. */}
            <DocketCard x={W * 0.06} y={H * 0.78} w={W * 0.88} {...card} light={1} />
          </Cam>
        </Shot>

        {/* ============================================================
            S2  2.4-4.6  THE COUNT IS AN OBJECT.
            The digit and the thing it counts, in ONE frame at ONE moment, so
            the room's only rule is taught before anybody explains it: one slab
            equals one click. Every later wheel reads without a caption.
            ============================================================ */}
        <Shot from={2.4} to={4.6}>
          <Cam cy={0.44} zoom={2.6}>
            <CountRoomBG f={f} w={W} h={H} light={1} pile={0.05} />
            <g transform={`translate(${W * 0.5},${H * 0.42})`}>
              <TallyCounter x={-62} y={-22} s={0.78} f={f} variant="odometer" count={count} />
            </g>
            <CardPile x={W * 0.5 - CARD_W * 0.42} y={H * 0.66} w={CARD_W * 0.84}
                      count={2} mode="stacked" {...card} />
          </Cam>
        </Shot>

        {/* ============================================================
            S3  4.6-7.4  THE ESTABLISHING IMAGE.
            The whole apparatus in one frame: where the case goes in, where the
            count is kept, where copies come out, and one output bolted shut
            since before the film started. And how small a person is against
            one court case.
            ============================================================ */}
        <Shot from={4.6} to={7.4}>
          {/* THE ONLY SHOT THAT SEES THE WHOLE WALL. Everything before and
              after it is a fragment, which is what makes this one land. */}
          <Cam cy={0.5} zoom={1}>
            <CountRoomBG f={f} w={W} h={H} light={1} pile={pile} intake={0.5} />
            <g transform={`translate(${W * 0.5},${H * 0.42})`}>
              <TallyCounter x={-62} y={-22} s={0.78} f={f} variant="odometer" count={count} />
            </g>
            <CardPile x={W * 0.5 - CARD_W / 2} y={H * 0.88} w={CARD_W} count={landed}
                      mode="stacked" {...card} />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD} ground={H * 0.955}
                  rayX={W * 0.13} deeX={W * 0.88} />
          </Cam>
        </Shot>

        {/* ============================================================
            S4  7.4-11.6  THE TURN. The count becomes the floor.
            Cards land FLUSH on the beat of the repeated word, so the picture on
            the floor does not change at all and the only measurable change in
            the frame is the height of the man standing on it.
            ============================================================ */}
        <Shot from={7.4} to={11.6}>
          <Cam cy={0.82} zoom={1.45}>
            <CountRoomBG f={f} w={W} h={H} light={0.85} pile={pile} />
            <CardPile x={W * 0.5 - CARD_W / 2} y={H * 0.92} w={CARD_W} count={landed}
                      mode="flush" {...card} />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD}
                  ground={H * 0.92 - landed * (CARD_W * 0.018)}
                  rayX={W * 0.10} deeX={W * 0.90} rayPose="point" />
          </Cam>
        </Shot>

        {/* ============================================================
            S5  11.6-14.0  THE SCALE REFERENCE.
            Dee raises her letter-size dispute form beside a card 8.2x its long
            edge. The ONLY true-human-size object in the film, and it is also
            the document c6 and c7 are about. Do not cut it for pace.
            ============================================================ */}
        <Shot from={11.6} to={14.0}>
          <Cam cy={0.76} zoom={1.5}>
            <CountRoomBG f={f} w={W} h={H} light={0.9} pile={0.85} />
            <CardPile x={W * 0.14} y={H * 0.86} w={CARD_W * 1.2} count={3}
                      mode="stacked" {...card} />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD} ground={H * 0.955}
                  rayX={W * 0.06} deeX={W * 0.90} deePose="raise" />
            {/* THE DISPUTE FORM, at real letter scale against the card. It is the
                only true-human-size object in the film and the conceit is
                invisible without it. */}
            <rect x={W * 0.84} y={H * 0.60} width={(CARD_W * 1.2) / 8.2}
                  height={((CARD_W * 1.2) / 8.2) * 1.29}
                  fill={COUNTROOM.card} stroke={COUNTROOM.ink} strokeWidth={3} />
          </Cam>
        </Shot>

        {/* ============================================================
            S6  14.0-18.2  THE PANEL THAT WILL NOT OPEN.
            No keyhole, no lock, no sign, no notice, and the enamel brush stroke
            runs unbroken across the hinge knuckle. It is not locked. Somebody
            painted it shut, and the paint proves it has not opened since. That
            is meaner than a sign because there is nobody to appeal it to.
            Line 6 rides on AUDIO here: c6 licenses a failure to disclose
            SOURCES, not a payment, so drawing the payment would assert an
            uncleared transaction. The board files this as a note to the
            writers room rather than a rejection.
            ============================================================ */}
        <Shot from={14.0} to={18.2}>
          <Cam cx={0.84} cy={0.53} zoom={2.9}>
            <CountRoomBG f={f} w={W} h={H} light={0.9} pile={0.9}
                         panel={interpolate(f, [s(14.6), s(15.2), s(15.8), s(16.6), s(17.2)],
                                            [0, 1, 0, 1, 0], clamp)} />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD * 0.62} ground={H * 0.615}
                  rayX={W * 0.1} deeX={W * 0.64} deePose="raise" show="dee" />
          </Cam>
        </Shot>

        {/* ============================================================
            S7  18.2-21.2  THE THESIS SHOT. Silent by design.
            The film's ONLY high angle, spent proving the INPUT never changed.
            Exactly one card goes in, the same single card the slot has taken
            since second one. No dialogue anywhere in this shot.
            ============================================================ */}
        <Shot from={18.2} to={21.2}>
          {/* THE ONLY HIGH ANGLE IN THE FILM, and it is pointed at the INTAKE,
              which lives upper LEFT. The first cut craned to the middle of the
              wall and proved nothing: the shot's whole job is that exactly one
              card goes in, the same single card the slot has taken since second
              one, and you have to be able to SEE the slot for that to land. */}
          <Cam cx={0.22} cy={0.22} zoom={2.0}>
            <CountRoomBG f={f} w={W} h={H} light={1} pile={1}
                         intake={interpolate(f, [s(19.4), s(20.6)], [0, 1], clamp)} />
          </Cam>
        </Shot>

        {/* ============================================================
            S8  21.2-23.8  THE STACK EDGE.
            A whip from the highest camera in the film to the LOWEST, back to
            back, so the fall itself is the measurement. Eight identical head
            lines at one offset is a PATTERN; eight different documents is a
            mess. This is the only place SAME and MANY can be told apart.
            ============================================================ */}
        <Shot from={21.2} to={23.8}>
          <Cam cy={0.88} zoom={1.25}>
            <CountRoomBG f={f} w={W} h={H} light={0.75} pile={1} />
            <g transform={`translate(${W * 0.5},${H * 0.42})`}>
              <TallyCounter x={-62} y={-22} s={0.9} f={f} variant="odometer" count={count} />
            </g>
            <CardPile x={W * 0.06} y={H * 1.14} w={W * 0.88} count={8}
                      mode="stacked" reveal={0.38} {...card} />
          </Cam>
        </Shot>

        {/* ============================================================
            S9  23.8-26.6  he did nothing and it happened to him.
            The line claims stillness and the picture proves it by making him
            move WITHOUT moving. The only thing acting in the frame is the
            floor, and he does not look down.
            ============================================================ */}
        <Shot from={23.8} to={26.6}>
          <Cam cy={0.72} zoom={1.6}>
            <CountRoomBG f={f} w={W} h={H} light={0.7} pile={1} />
            <CardPile x={W * 0.08} y={H * 0.96} w={W * 0.84} count={4} mode="flush" {...card} />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD}
                  ground={H * 0.72 - interpolate(f, [s(24.7), s(24.95)], [0, 14], clamp)}
                  rayX={W * 0.26} deeX={W * 0.84} />
          </Cam>
        </Shot>

        {/* ============================================================
            S10  26.6-30.0  THE ONLY FLOATING TWO-SHOT, and it is 3.4s.
            Spent on the one thing a two-hander can buy: two people NOT reacting
            while the world moves them. It ends on a hard geometric event, Ray's
            crown crossing the odometer boss, and the wheel tops out at 9 and
            never rolls again.
            ============================================================ */}
        <Shot from={26.6} to={30.0}>
          <Cam cy={interpolate(f, [s(26.6), s(30.0)], [0.66, 0.58], clamp)} zoom={1.5}>
            <CountRoomBG f={f} w={W} h={H} light={0.7} pile={1} />
            <g transform={`translate(${W * 0.5},${H * 0.42})`}>
              <TallyCounter x={-62} y={-22} s={0.78} f={f} variant="odometer" count={count} />
            </g>
            <CardPile x={W * 0.02} y={H * 1.02} w={W * 0.96} count={3} mode="flush" {...card} />
            {/* Ray RISES until his crown crosses the odometer boss at 28.8s.
                The wheel stops at 9 there and never rolls again. */}
            <Cast f={f} crown={CARD_W * CAST_TO_CARD * 1.15}
                  ground={interpolate(f, [s(26.6), s(30.0)], [H * 0.90, H * 0.70], clamp)}
                  rayX={W * 0.30} deeX={W * 0.74} />
          </Cam>
        </Shot>

        {/* ============================================================
            S11  30.0-32.6  THE PUNCHLINE, delivered BEFORE the euphemism.
            One frame split by the machine's own geometry, no cut. Left: a brass
            die embosses VERIFIED on a copy. Right, SAME FRAME: the intake still
            holding the ONE original it has held since second one, the wheel
            above it reading nine.
            The only frame that holds true and false about the same object at
            once, which is the difference between an absurdity and a complaint
            about volume.
            ============================================================ */}
        <Shot from={30.0} to={32.6}>
          {/* ONE FRAME, split by the machine's own geometry. No cut, both
              halves in focus. Left: VERIFIED going onto a copy. Right, same
              frame: the intake still holding the ONE original. */}
          <CountRoomBG f={f} w={W} h={H} light={0.9} pile={1} intake={0.55} />
          <rect x={W * 0.5 - 4} y={0} width={8} height={H} fill={COUNTROOM.brassLo} opacity={0.9} />
          <DocketCard x={W * 0.015} y={H * 0.34} w={W * 0.46} {...card} light={1} />
          <VerifyDie x={W * 0.06} y={H * 0.47} w={W * 0.16}
                     press={interpolate(f, [s(30.5), s(31.0), s(32.0)], [0, 1, 1], clamp)} />
          <g transform={`translate(${W * 0.75},${H * 0.30}) scale(1.15)`}>
            <TallyCounter x={-62} y={-22} s={0.9} f={f} variant="odometer" count={count} />
          </g>
          <g transform={`translate(${W * 0.52},${H * 0.52}) scale(0.9)`}>
            <CardChute f={f} x={0} y={0} w={W * 0.42} state="running" emit={0.15} />
          </g>
        </Shot>

        {/* ============================================================
            S12  32.6-35.2  the Institution speaks and is NOT given a face.
            The euphemism is answered by the equipment it describes, doing
            precisely what it claims, politely and on time. Nothing brightens,
            nothing flickers, no aperture opens, no part of the wall turns
            toward camera. Refusing to editorialise is what makes the
            politeness menacing: there is nothing to negotiate with.
            ============================================================ */}
        <Shot from={32.6} to={35.2}>
          <Cam cx={0.16} cy={0.20} zoom={3.2}>
            <CountRoomBG f={f} w={W} h={H} light={1} pile={0}
                         intake={interpolate(f, [s(33.1), s(34.0)], [0, 1], clamp)} />
          </Cam>
        </Shot>

        {/* ============================================================
            S13  35.2-37.8  the dispute goes in, and the answer lands on the
            LISTENER. The refusal is the fastest thing in the film: every copy
            took a beat to make and this returns before he has got his arms
            down. The machine's only line with a reaction shot, and the
            reaction belongs to Dee. This is where her single crack is spent.
            ============================================================ */}
        <Shot from={35.2} to={37.8}>
          <Cam cx={0.34} cy={0.52} zoom={1.55}>
            <CountRoomBG f={f} w={W} h={H} light={0.95} pile={1}
                         intake={interpolate(f, [s(36.1), s(36.8)], [0, 1], clamp)} />
            {/* The card comes STRAIGHT back out, before he has got his arms down. */}
            {f > s(37.15) && (
              <DocketCard x={W * 0.10} y={H * 0.66} w={W * 0.52} {...card}
                          differs="INVALID" rot={-4} light={1} />
            )}
            <Cast f={f} crown={CARD_W * CAST_TO_CARD * 0.62} ground={H * 0.32}
                  rayX={W * 0.06} deeX={W * 0.62} rayPose="raise" show="ray" />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD * 0.72} ground={H * 0.80}
                  rayX={W * 0.06} deeX={W * 0.56} show="dee" />
          </Cam>
        </Shot>

        {/* ============================================================
            S14  37.8-42.2  THE ONLY STILL WHEEL IN THE FILM.
            The odometer in the identical framing used at 2.6s, except nine card
            edges are stacked into the bottom of frame instead of two. Fifty
            seconds of a wheel that turns for every copy, and the one thing that
            will not make it turn is a person disagreeing.
            ============================================================ */}
        <Shot from={37.8} to={42.2}>
          {/* MATCHED EXACTLY to S2's framing. Same lens, same boss. The only
              two differences are a number and a floor, and that comparison is
              the whole shot. */}
          <Cam cy={0.44} zoom={2.6}>
            <CountRoomBG f={f} w={W} h={H} light={1} pile={1} />
            <g transform={`translate(${W * 0.5},${H * 0.42})`}>
              <TallyCounter x={-62} y={-22} s={0.78} f={f} variant="odometer" count={count} />
            </g>
            <CardPile x={W * 0.5 - CARD_W * 0.42} y={H * 0.70} w={CARD_W * 0.84}
                      count={5} mode="stacked" reveal={0.4} {...card} />
          </Cam>
        </Shot>

        {/* ============================================================
            S15  42.2-45.4  THE ONE REVEAL, and the edge-tease pays after
            thirty-eight seconds. Three fasteners drop and the cover plate falls
            off the second chute. It reverses an ABSENCE rather than introducing
            an object: there were always two exits and he was only ever standing
            in front of one of them.
            ============================================================ */}
        <Shot from={42.2} to={45.4}>
          <Cam cx={0.86} cy={0.70} zoom={2.2}>
            <CountRoomBG f={f} w={W} h={H} light={0.7} pile={1} />
            {/* THE PLATE COMES OFF the chute that has been at the lower right
                frame edge since second five. Thirty-eight seconds of absence,
                reversed. */}
            <g transform={`translate(${W * 0.80},${H * 0.62})`}>
              <CardChute f={f} x={0} y={0} w={W * 0.3} state="plated"
                         open={interpolate(f, [s(43.2), s(44.1)], [0, 1], clamp)} />
            </g>
            {f > s(44.5) && (
              <DocketCard x={W * 0.62} y={H * 0.80} w={W * 0.42} {...card}
                          differs="RESOLVED" rot={3} light={1} />
            )}
          </Cam>
        </Shot>

        {/* ============================================================
            S16  45.4-49.4  THE PAYOFF, and the ONLY overhead in the film,
            held back forty-five seconds for this. Forty-five seconds have
            proved this machine can only make identical things, and this is the
            one frame where two of its outputs are not identical, in the single
            place it was ever asked to be consistent.
            ============================================================ */}
        <Shot from={45.4} to={49.4}>
          <rect x={0} y={0} width={W} height={H} fill={COUNTROOM.ink} />
          <DocketCard x={W * 0.04} y={H * 0.20} w={W * 0.92} {...card}
                      differs="RESOLVED" light={1} />
          <DocketCard x={W * 0.04} y={H * 0.56} w={W * 0.92} {...card}
                      differs="INVALID" light={1} />
        </Shot>

        {/* ============================================================
            S17  49.4-51.4  he has to live in one of them.
            The question is a joke until the frame turns it into a floor plan,
            and then it is an address. Straddling both cards makes a rhetorical
            line a physical impossibility.
            ============================================================ */}
        <Shot from={49.4} to={51.4}>
          <Cam cy={0.74} zoom={1.5}>
            <CountRoomBG f={f} w={W} h={H} light={0.7} pile={1} />
            {/* ONE BOOT ON EACH ANSWER. The question is a joke until the frame
                turns it into a floor plan, and then it is an address. */}
            <DocketCard x={-W * 0.04} y={H * 0.86} w={W * 0.56} {...card}
                        differs="RESOLVED" light={0.92} />
            <DocketCard x={W * 0.48} y={H * 0.86} w={W * 0.56} {...card}
                        differs="INVALID" light={0.92} />
            <Cast f={f} crown={CARD_W * CAST_TO_CARD * 0.85} ground={H * 0.88}
                  rayX={W * 0.5} deeX={W * 0.9} rayPose="stand" show="ray" />
          </Cam>
        </Shot>

        {/* ============================================================
            S18  51.4-56.0  THE BUTTON. No cast in frame.
            The document that finally contradicts the machine came from a court
            and has nothing to do with his dispute, and the frame proves it by
            BURYING his card instead of correcting it. One corner stays visible
            under the filing's bottom edge, unchanged, which is the place the
            last line points at.
            ============================================================ */}
        <Shot from={51.4} to={56.0}>
          <rect x={0} y={0} width={W} height={H} fill={COUNTROOM.ink} />
          {/* HIS CARD, unchanged, and the filing lands ON it rather than
              correcting it. Only a corner stays visible under the bottom edge,
              which is the place the last line points at. */}
          <DocketCard x={W * 0.05} y={H * 0.86} w={W * 0.9} {...card}
                      differs="INVALID" light={0.95} />
          <FilingPlate
            w={W} h={H}
            enter={interpolate(f, [s(51.7), s(52.5)], [0, 1], clamp)}
            highlight={interpolate(f, [s(53.1), s(54.0)], [0, 1], clamp)}
            alleged
          />
        </Shot>
      </svg>

      {/* ==== HTML layers, OUTSIDE the svg, per the mounting contract. ==== */}

      {/* THE WORDMARK stamps at 2.6s over the odometer's cream digit field, the
          one light surface in the room. Multiply vanishes on teal, which is why
          it is spent here and nowhere else. */}
      {t >= 2.5 && t < 4.6 && (
        <Wordmark frame={f - s(2.6)} fps={FPS} x={540} y={700} scale={0.94}
                  color={BRAND.INK} blend="multiply" />
      )}

      {/* THE ONE STAMP IN THE EPISODE, on the filing at the button. */}
      {t >= 54.3 && (
        <Stamp frame={f - s(54.4)} fps={FPS} x={640} y={1120} rotate={-8} scale={3.2}>
          ALLEGED
        </Stamp>
      )}

      {t < 9 && <CaseNumber n={3} y={92} color={BRAND.PAPER} />}

      <CaptionLayer f={f} />

      <GradeLayer f={f} bloom={0.14} vignette={0.52} grain={0.06} warmth={0.04} />

      {t > TOTAL_S - 1.5 && (
        <EndCard n={3} frame={f - s(TOTAL_S - 1.5)} fps={FPS} color={BRAND.INK} />
      )}
    </AbsoluteFill>
  );
};

/**
 * THE BURNED-IN CAPTION. Tinted by speaker, because this show has no narrator
 * and three voices reading in one colour is a podcast with drawings over it.
 *
 * Direction tags are stripped at GENERATION, in scripts/captions_text.py, which
 * is the one definition of what a viewer is allowed to read. Two copies of that
 * rule drifted apart once already and put "[sarcasm, medium pause]" on screen.
 */
const SPEAKER_TINT: Record<string, string> = {
  RAY: '#F2EADA',
  DEE: '#F6D9E4',
  INSTITUTION: '#9FD8D2',
};

const CaptionLayer: React.FC<{f: number}> = ({f}) => {
  const t = f / FPS;
  const cue = CAPTIONS.find((c) => t >= c.start && t <= c.end);
  if (!cue) return null;
  const who = speakerAt(t) ?? 'RAY';
  return (
    <div style={{
      position: 'absolute', left: 0, right: 0, bottom: 132,
      display: 'flex', justifyContent: 'center', padding: '0 44px',
    }}>
      {/* A PLATE UNDER THE TYPE, not a text shadow.
      
          The first full render put white captions straight over the cards and
          the two fought: cream type on a cream card, with the card's own
          printing behind it. A drop shadow does not fix that, it just makes two
          unreadable things. The plate is the show's ink at 78%, so the caption
          always has its own value band no matter what is behind it. */}
      <div style={{
        background: 'rgba(16,20,35,0.78)',
        borderRadius: 6,
        padding: '14px 26px 18px',
        maxWidth: 940,
      }}>
        <div style={{
          fontFamily: 'Barlow Condensed, Impact, sans-serif',
          fontWeight: 800, fontSize: 62, lineHeight: 1.06,
          color: SPEAKER_TINT[who] ?? '#F2EADA',
          textAlign: 'center',
          textShadow: '0 3px 0 rgba(16,20,35,0.9)',
        }}>
          {cue.text}
        </div>
      </div>
    </div>
  );
};
