/**
 * cast.tsx — RAY and DEE.
 *
 * THE PREVIOUS CAST WAS DELETED, not refactored. It was a parameter set bolted
 * onto `Character.tsx`, which is the crowd rig ported from an ALASKA show: a
 * hand-authored paper doll of axis-aligned boxes and constant-width strokes,
 * built for a weekly educational dispatch about a cold place. Seven passes of
 * patching it produced a mannequin with a waist, which is the correct outcome
 * of patching, and the wrong outcome full stop.
 *
 * Owner, 2026-08-02: "if its Alaska stuff don't patch it, we are creating a
 * better show that's more engaging as opposed to educational."
 *
 * So the cast is built on `Figure.tsx`, which knows about proportion, line of
 * action, contrapposto, overlap and line weight, and knows nothing about
 * parkas. `Character.tsx` stays exactly where it is and keeps serving the crowd
 * and the back catalogue. It is not the cast any more.
 *
 * WHAT A SCENE MAY VARY: pose, emotion, position, scale, facing, and the mouth
 * track. Identity is fixed here, because comedy needs you to already know who
 * is about to speak.
 *
 * THE INSTITUTION IS NOT HERE ON PURPOSE. It is MachineShadow, it has no face,
 * and it never gets one. Give it an expression and it becomes something you
 * could negotiate with, and the premise dies.
 */
import React from 'react';
import {Figure, FigureProps, Emotion, Pose, PoseTrack, ScalarKey} from './Figure';

type CastProps = Omit<FigureProps, 'sex' | 'skin' | 'hair' | 'eyes' | 'wear' | 'hairstyle'> & {
  /** Escape hatch for a genuine costume gag. Rare: a cast that gets re-dressed
      for no reason is not a cast. */
  wearOverride?: FigureProps['wear'];
};

/**
 * RAY — the Id. He is RIGHT, not a fool, and his default emotion is angry
 * because that is his resting state by the time a scene starts: he has already
 * found out.
 *
 * Built athletic on purpose, and not only because the owner asked for it. The
 * taper does staging work: it points his shape language AT the Institution's
 * cold rectilinear bulk instead of echoing it.
 */
export const RAY = {
  skin: '#dda274',
  hair: '#3a2418',
  eyes: '#4a6f57',
  wear: {top: '#2f3f5e', bottom: '#26324a', accent: '#8e2f38'},
} as const;

export const Ray: React.FC<CastProps> = ({
  wearOverride, emotion = 'angry', pose = 'arms-crossed', scale = 1, ...rest
}) => (
  <Figure
    {...rest}
    sex="m"
    pose={pose}
    emotion={emotion}
    /* Jeans and a t-shirt. Never a suit: a suit reads as management and Ray is
       never management. Bare forearms because a sleeve is a tube by definition
       and can never show an arm. */
    wear={wearOverride ?? RAY.wear}
    hairstyle="short"
    /* A SUIT, on the athletic build. The point is the contrast: the jacket is
       cut to the V-taper rather than hiding it, which is what a suit is FOR.
       An episode can drop him to a tee with garment="trousers" when the staging
       wants it, but the default is dressed. */
    garment="suit"
    skin={RAY.skin}
    hair={RAY.hair}
    eyes={RAY.eyes}
    scale={scale}
  />
);

/**
 * DEE — the Straight Man. Her comedy is deadpan delivery of something insane,
 * so her default is neutral: a pre-loaded expression spends the crack early.
 *
 * She used to be differentiated by GLASSES, from back when she and Ray shared
 * one body and one face and there was nothing else to tell them apart. The
 * silhouette does that job now and does it at thumbnail size, which glasses
 * never did.
 */
export const DEE = {
  skin: '#e3ac7e',
  hair: '#26191c',
  eyes: '#4a3327',
  wear: {top: '#a8355a', bottom: '#7a2440', accent: '#1d1a22'},
} as const;

export const Dee: React.FC<CastProps> = ({
  wearOverride, emotion = 'neutral', pose = 'stand', scale = 1, ...rest
}) => (
  <Figure
    {...rest}
    sex="f"
    pose={pose}
    emotion={emotion}
    wear={wearOverride ?? DEE.wear}
    hairstyle="long"
    /* Skirt and heels. */
    garment="skirt"
    skin={DEE.skin}
    hair={DEE.hair}
    eyes={DEE.eyes}
    scale={scale}
  />
);

/**
 * The beat where Dee's composure cracks. ONE per episode; the bible is explicit
 * that saving it is the point. Named rather than left to a storyboard's
 * judgement so it is countable: grep a scene for DEE_CRACK, and if there are
 * two, the episode is spending it wrong.
 */
export const DEE_CRACK: Emotion = 'shock';

/**
 * Ray's escalation ladder. He starts angry and goes UP. He does not start
 * neutral and warm up, because sixty seconds has no room for a warm-up.
 */
export const RAY_LADDER: readonly Emotion[] = ['angry', 'shock', 'smug'] as const;

/** Poses that read at thumbnail size, which is where the platform decides. */
export const RAY_HERO_POSES: readonly Pose[] = ['panic', 'point', 'raise'] as const;

/* ===========================================================================
   MANNERISMS. How they MOVE, which CAST_BIBLE never said.

   The bible defines how Ray and Dee TALK in detail and says nothing about how
   they carry themselves, so every episode staged them as two posed statues that
   breathe. A recurring cast is the show's whole production model (it is what
   makes daily output survivable), and a recurring cast that has no physical
   signature is not recurring, it is just reused.

   A mannerism has to be legible at thumbnail size, which means SILHOUETTE. Eye
   darts and finger work are LIFE and read as nothing on a phone.
   =========================================================================== */

/**
 * RAY'S TELL: he points. His whole function is arriving at a verdict, and the
 * arm going out is that verdict with a body attached. It is also the pose
 * RAY_HERO_POSES already lists as reading at thumbnail size, which is where the
 * platform decides.
 */
export const RAY_TELL: Pose = 'point';

/**
 * DEE'S TELL: she does not gesture, she LOOKS. Her power in a scene is that she
 * already knows, so the move is the head turning to the thing before Ray has
 * caught up. Costs no silhouette change and reads as authority.
 */
export const DEE_TELL: Pose = 'arms-crossed';

/** A caption cue, which is the timing source every episode already generates. */
export type Cue = {start: number; end: number; who: string};

/**
 * LOOK AT WHOEVER IS TALKING.
 *
 * The cheapest acting beat that exists and the one this show has never had. A
 * character who never looks at the thing being discussed is not in the scene,
 * and until `look` was wired the rig physically could not do it.
 *
 * `me` turns toward `otherSide` while somebody else speaks, and returns to
 * roughly front while speaking themselves, because a person addressing a room
 * faces out and a person listening faces the speaker.
 */
export function watchSpeaker(
  cues: Cue[], me: string, otherSide: -1 | 1, amount = 0.34,
): ScalarKey[] {
  const out: ScalarKey[] = [{t: 0, v: 0}];
  for (const c of cues) {
    // Turn slightly BEFORE the line starts. Anticipation is what makes a head
    // turn read as attention rather than as a delayed reaction.
    out.push({t: Math.max(0, c.start - 0.18),
              v: c.who === me ? 0.06 * otherSide : amount * otherSide});
  }
  return out;
}

/**
 * GESTURE ON YOUR OWN LINES.
 *
 * Builds a PoseTrack that moves a character into their tell while they speak and
 * releases afterwards, so the body does something on the beat the voice does.
 * `hold` is the default resting pose.
 *
 * This is deliberately mechanical rather than expressive: a per-line director's
 * gesture is better and this is the floor, so that no episode ever again ships
 * with a cast that never moves because nobody hand-authored every beat.
 */
export function gestureOnLines(
  cues: Cue[], me: string, tell: Pose, hold: Pose = 'stand',
): PoseTrack {
  const out: PoseTrack = [{t: 0, pose: hold}];
  for (const c of cues) {
    if (c.who !== me) continue;
    if (c.end - c.start < 0.7) continue;   // too short to read as a gesture
    out.push({t: Math.max(0, c.start - 0.12), pose: tell});
    out.push({t: c.end + 0.10, pose: hold});
  }
  return out;
}
