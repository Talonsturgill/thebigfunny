/**
 * CastSheet — the character sheet for the REBUILT cast. Look-dev only, never
 * rendered into an episode.
 *
 * WHY IT EXISTS
 * A prop that typechecks and renders successfully can still change nothing on
 * screen; this pipeline has already been burned by exactly that (a `mouth` prop
 * sat dead behind a `talking !== undefined` guard for a whole episode while
 * every gate stayed green and the speaker never opened their mouth). So a
 * figure change is not done until a human has looked at a PIXEL, and the sheet
 * is what they look at.
 *
 * It shows the two things that fail INDEPENDENTLY, at the size each one is
 * actually judged at:
 *   - the SILHOUETTE, small, because that is what decides who is speaking on a
 *     grid tile before a single feature is legible;
 *   - the FACE, large, because that is what decides whether anyone wants to
 *     keep looking.
 *
 *   npx remotion still src/index.ts CastSheet out/castsheet.png --frame=30
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Ray, Dee} from './lib/cast';
import {Pose} from './lib/Figure';

const POSES: Pose[] = ['stand', 'arms-crossed', 'point'];

export const CastSheet: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: '#efe7d8'}}>
      <svg width="1080" height="1920" viewBox="0 0 1080 1920">
        <text x={540} y={72} textAnchor="middle" fontSize={46} fontFamily="Georgia, serif" fill="#1a1a22">
          THE CAST
        </text>
        <text x={540} y={106} textAnchor="middle" fontSize={20} fontFamily="Georgia, serif" fill="#5a5a66">
          rebuilt from forms, not coordinates
        </text>

        {/* FULL FIGURES at the size a phone actually shows them. */}
        <g transform="translate(230,150) scale(0.62)">
          <Ray frame={f} pose="stand" emotion="neutral" />
        </g>
        <g transform="translate(700,150) scale(0.62)">
          <Dee frame={f} pose="stand" emotion="neutral" />
        </g>
        <text x={230} y={620} textAnchor="middle" fontSize={28} fontFamily="Georgia, serif" fill="#1a1a22">RAY</text>
        <text x={700} y={620} textAnchor="middle" fontSize={28} fontFamily="Georgia, serif" fill="#1a1a22">DEE</text>

        {/* SILHOUETTE TEST. Same figures, filled solid black. If you cannot tell
            who is who here, the design has failed and no amount of face work
            will rescue it, because this is all a grid tile transmits. */}
        <text x={540} y={700} textAnchor="middle" fontSize={26} fontFamily="Georgia, serif" fill="#5a5a66">
          silhouette test
        </text>
        <g style={{filter: 'brightness(0) saturate(0)'}}>
          <g transform="translate(300,730) scale(0.34)">
            <Ray frame={f} pose="stand" emotion="neutral" />
          </g>
          <g transform="translate(560,730) scale(0.34)">
            <Dee frame={f} pose="stand" emotion="neutral" />
          </g>
          <g transform="translate(800,730) scale(0.34)">
            <Ray frame={f} pose="point" emotion="angry" />
          </g>
        </g>

        {/* POSES. A pose here is three joint positions, so this row is also the
            check that the rig poses rather than being redrawn. */}
        <text x={540} y={1060} textAnchor="middle" fontSize={26} fontFamily="Georgia, serif" fill="#5a5a66">
          poses
        </text>
        {POSES.map((p, i) => (
          <g key={p} transform={`translate(${190 + i * 250},1080) scale(0.38)`}>
            <Ray frame={f} pose={p} emotion="angry" />
          </g>
        ))}
        <g transform="translate(940,1080) scale(0.38)">
          <Dee frame={f} pose="arms-crossed" emotion="smug" />
        </g>

        {/* FACES, big enough to actually judge. */}
        <text x={540} y={1400} textAnchor="middle" fontSize={26} fontFamily="Georgia, serif" fill="#5a5a66">
          faces
        </text>
        <g clipPath="url(#faceclip)">
          <g transform="translate(280,1440) scale(2.6)">
            <Ray frame={f} pose="stand" emotion="angry" />
          </g>
          <g transform="translate(780,1440) scale(2.6)">
            <Dee frame={f} pose="stand" emotion="smug" />
          </g>
        </g>
        <clipPath id="faceclip"><rect x={0} y={1420} width={1080} height={480} /></clipPath>
      </svg>
    </AbsoluteFill>
  );
};
