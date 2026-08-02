/**
 * CastSheet — the character sheet. NOT an episode, and never rendered into one.
 *
 * WHY IT EXISTS
 * A prop that typechecks and renders successfully can still change nothing on
 * screen; the rig has already been burned by exactly that (the `mouth` prop was
 * dead for a whole episode behind a `talking !== undefined` guard, and the whole
 * pipeline stayed green while the speaker's mouth never opened). The rule that
 * came out of it is that a new visual prop is not done until somebody has looked
 * at a PIXEL, so a silhouette change ships with the still that proves it.
 *
 * Column 1 is `broad`, the original path, and it is the control: if it ever
 * moves, a "safe default" refactor has silently redrawn the entire existing
 * library, which is the failure this composition is here to catch.
 *
 *   bash scripts/render.sh still 30 CastSheet   (or open the Remotion studio)
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Character, Build} from './lib/Character';
import {Ray, Dee, RAY_PALETTE, DEE_PALETTE} from './lib/cast';

const COLS: {build: Build; label: string; note: string}[] = [
  {build: 'broad', label: 'broad', note: 'CONTROL. must not move.'},
  {build: 'hourglass', label: 'hourglass', note: 'waist + hips + lashes'},
  {build: 'athletic', label: 'athletic', note: 'V-taper, square jaw'},
];

export const CastSheet: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: '#efe7d8'}}>
      <svg width="1080" height="1920" viewBox="0 0 1080 1920">
        <text x={540} y={90} textAnchor="middle" fontSize={54} fontFamily="Georgia, serif" fill="#1a1a22">
          BUILD SILHOUETTES
        </text>
        {COLS.map((col, i) => (
          <g key={col.build} transform={`translate(${200 + i * 340},420) scale(0.5)`}>
            <Character
              frame={f}
              build={col.build}
              outfit="flannel"
              pose="stand"
              emotion="neutral"
              hairstyle={col.build === 'hourglass' ? 'bob' : 'crop'}
              hair="#2b1d12"
              skin="#d8a07a"
            />
          </g>
        ))}
        {COLS.map((col, i) => (
          <g key={`${col.build}-t`}>
            <text x={200 + i * 340} y={490} textAnchor="middle" fontSize={34} fontFamily="Georgia, serif" fill="#1a1a22">
              {col.label}
            </text>
            <text x={200 + i * 340} y={524} textAnchor="middle" fontSize={22} fontFamily="Georgia, serif" fill="#5a5a66">
              {col.note}
            </text>
          </g>
        ))}
        {/* THE CAST AS ACTUALLY LOCKED, which is the pair that has to read apart
            at thumbnail size. Same scale, same pose, side by side: if you cannot
            tell them apart with the page squinted at, the silhouette work
            failed and no amount of face detail will save it. */}
        <text x={540} y={600} textAnchor="middle" fontSize={44} fontFamily="Georgia, serif" fill="#1a1a22">
          THE CAST
        </text>
        <g transform="translate(320,1014) scale(0.85)">
          <Ray frame={f} pose="stand" emotion="neutral" />
        </g>
        <g transform="translate(760,1014) scale(0.85)">
          <Dee frame={f} pose="stand" emotion="neutral" />
        </g>
        <text x={320} y={1100} textAnchor="middle" fontSize={32} fontFamily="Georgia, serif" fill="#1a1a22">
          RAY (athletic)
        </text>
        <text x={760} y={1100} textAnchor="middle" fontSize={32} fontFamily="Georgia, serif" fill="#1a1a22">
          DEE (hourglass)
        </text>
        <text x={540} y={1150} textAnchor="middle" fontSize={20} fontFamily="Georgia, serif" fill="#5a5a66">
          {`ray ${RAY_PALETTE.skin} / dee ${DEE_PALETTE.skin}`}
        </text>
      </svg>
    </AbsoluteFill>
  );
};
