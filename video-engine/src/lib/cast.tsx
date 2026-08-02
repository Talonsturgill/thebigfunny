/**
 * cast.tsx — RAY and DEE, the two fixed characters of The Big Funny.
 *
 * WHY THIS IS A THIN WRAPPER AND NOT A NEW RIG
 * The ported Character rig already does poses, emotions, outfits, idle sway,
 * blink, walk cycles and the ambient talk mouth, and it has been through a lot
 * of production notes to get there (see its own comments: the burglar-mask
 * headgear fix, the no-lip-sync ruling, the idleGain escape hatch). Rebuilding
 * any of that to get two characters would be throwing away paid-for craft.
 *
 * So the cast is a LOCK, not a redraw. These wrappers fix the identity
 * constants (palette, build, default outfit) so Ray reads as Ray in every
 * episode without a storyboard having to remember six props. Everything an
 * episode legitimately varies (pose, emotion, position, scale, facing) stays
 * open.
 *
 * THIS IS THE CAST LAW IN CODE. The show's variety comes from staging, camera
 * and set, never from redrawing the cast, because comedy needs you to already
 * know who is about to speak. See knowledge/CAST_BIBLE.md and the library
 * mandate in ASSET_MANIFEST.md, which said the same thing before this show
 * existed: "Composition freshness comes from the storyboard fingerprint +
 * camera + staging, not from re-drawing the cast."
 *
 * THE INSTITUTION IS NOT HERE ON PURPOSE. It is MachineShadow, it has no face,
 * and it never gets one. Giving it an expression makes it something you could
 * negotiate with and the premise dies. Do not add it to this file.
 */
import React from 'react';
import {Character, CharacterProps, Emotion, Pose} from './Character';

/** What a scene is allowed to vary. Identity props are deliberately absent. */
type CastProps = Omit<CharacterProps, 'outfit' | 'hair' | 'skin' | 'eyes' | 'glasses'> & {
  /** Escape hatch for a genuine story reason (a costume gag). Use it rarely; an
      episode that re-dresses Ray for no reason is breaking the cast law. */
  outfitOverride?: CharacterProps['outfit'];
};

/**
 * RAY — the Id. Warm, round, slightly too small for the world he is in, which is
 * the deliberate shape-language opposite of the Institution's cold rectilinear
 * bulk. The same Sourdough-vs-ServerMachine opposition the library already
 * encodes, pointed at a person.
 *
 * He is RIGHT, not a fool. Default emotion is angry rather than neutral because
 * that is his resting state by the time a scene starts: he has already found
 * out.
 */
export const RAY_PALETTE = {
  hair: '#2b1d12',
  skin: '#d8a07a',
  eyes: '#3a6b52',
} as const;

export const Ray: React.FC<CastProps> = ({
  outfitOverride,
  emotion = 'angry',
  pose = 'arms-crossed',
  scale = 1,
  ...rest
}) => (
  <Character
    {...rest}
    pose={pose}
    emotion={emotion}
    /* JEANS AND A TEE. Never a suit; a suit reads as management and Ray is never
       management. The flannel was ported from an Alaska show and dressed
       him for a plow; nothing about a national story needs cold-weather workwear,
       and a coat sleeve is a tube by definition so it can never show an arm. */
    outfit={outfitOverride ?? 'tee'}
    headgear="bare"
    /* ATHLETIC: wide shoulders tapering to a narrow waist, square jaw, planted
       stance. Ray was the same shapeless sack as everyone else, which is half of
       why the cast read as one person in different jackets. The taper also does
       real staging work: it points Ray's shape-language AT the Institution's
       rectilinear bulk instead of echoing it. */
    build="athletic"
    hair={RAY_PALETTE.hair}
    skin={RAY_PALETTE.skin}
    eyes={RAY_PALETTE.eyes}
    /* Slightly under scale on purpose. The world is bigger than him. */
    scale={scale * 0.96}
  />
);

/**
 * DEE — the Straight Man. Upright and more vertical than Ray, angular but still
 * warm, because she is on his side and must never read as institutional.
 *
 * Glasses USED to be her one fixed differentiator, from back when she and Ray
 * shared a body and a face and there was nothing else to tell them apart. The
 * silhouette does that job now, and far better, so the glasses are gone: they
 * were the loudest shape on her face and they were solving a problem that no
 * longer exists. Default emotion neutral, because her comedy is deadpan delivery of something
 * insane and a pre-loaded expression spends the crack early.
 */
export const DEE_PALETTE = {
  hair: '#1d1a26',
  skin: '#8d5f43',
  eyes: '#2f4a6b',
} as const;

export const Dee: React.FC<CastProps> = ({
  outfitOverride,
  emotion = 'neutral',
  pose = 'stand',
  scale = 1,
  ...rest
}) => (
  <Character
    {...rest}
    pose={pose}
    emotion={emotion}
    /* HOURGLASS: narrow shoulders, a belted waist, hip flare, tapered chin,
       lashes, narrow stance. The bob was the right instinct at the wrong layer.
       Hair sits on top of a BODY, and the body was the shared sack, so a bob on
       it read exactly as the owner put it (2026-08-02): "a dudes face, on a fat
       chick in a parka, with long hair, looking like a man with long hair."
       Silhouette is what reads at thumbnail size; it decides who is speaking
       before a single feature is legible. */
    build="hourglass"
    /* A DRESS AND HEELS. The vest was a quilted box, which is the one garment
       guaranteed to cancel a waist. */
    outfit={outfitOverride ?? 'dress'}
    headgear="bare"
    /* LONG. Length is the cue, and the reference is consistent: the mass falls
       well past the shoulder while leaving the whole face open. The earlier bob
       covered the jawline, which is the one line that makes a face read female,
       so it was actively cancelling the silhouette work underneath it. */
    hairstyle="long"
    hair={DEE_PALETTE.hair}
    skin={DEE_PALETTE.skin}
    eyes={DEE_PALETTE.eyes}
    scale={scale * 1.02}
  />
);

/**
 * The beat where Dee's composure cracks. ONE per episode; the bible is explicit
 * that saving it is the point. Exposed as a named helper rather than left to a
 * storyboard's judgement so it is countable in review: grep the scene for
 * DEE_CRACK and if there are two, the episode is spending it wrong.
 */
export const DEE_CRACK: Emotion = 'shock';

/**
 * Ray's escalation ladder. He starts angry and goes up, he does not start
 * neutral and warm up, because a 60 second episode has no room for a warm-up.
 */
export const RAY_LADDER: readonly Emotion[] = ['angry', 'shock', 'smug'] as const;

/** Poses that read at thumbnail size, which is where the platform decides. */
export const RAY_HERO_POSES: readonly Pose[] = ['panic', 'point', 'raise'] as const;
