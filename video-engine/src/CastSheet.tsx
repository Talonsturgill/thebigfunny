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
 * `broad` was the CONTROL, and it no longer is: the 'stand' arms had to be
 * re-authored (they attached at HALF the shoulder width, i.e. across the chest,
 * which no amount of scaling could fix) and that moved every existing figure.
 * Saying so here rather than leaving the label claiming a guarantee it stopped
 * providing. Everything else about `broad` is still the original path.
 *
 * LAYOUT NOTE: a Character's local bbox is y -440..+10 centered on x=0. That is
 * MEASURED off a render, not read off the source; reading the source and
 * reasoning about the nested transforms got it wrong twice.
 *
 *   npx remotion still src/index.ts CastSheet out/castsheet.png --frame=30
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {Character, Build} from './lib/Character';
import {Ray, Dee, RAY_PALETTE, DEE_PALETTE} from './lib/cast';

const COLS: {build: Build; label: string; note: string}[] = [
  {build: 'broad', label: 'broad', note: 'baseline. arms re-authored.'},
  {build: 'hourglass', label: 'hourglass', note: 'waist + hips + lashes'},
  {build: 'athletic', label: 'athletic', note: 'V-taper, square jaw'},
];

export const CastSheet: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{backgroundColor: '#efe7d8'}}>
      <svg width="1080" height="1920" viewBox="0 0 1080 1920">
        <text x={540} y={80} textAnchor="middle" fontSize={50} fontFamily="Georgia, serif" fill="#1a1a22">
          BUILD SILHOUETTES
        </text>
        {COLS.map((col, i) => (
          <g key={col.build} transform={`translate(${200 + i * 340},400) scale(0.46)`}>
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
            <text x={200 + i * 340} y={470} textAnchor="middle" fontSize={32} fontFamily="Georgia, serif" fill="#1a1a22">
              {col.label}
            </text>
            <text x={200 + i * 340} y={502} textAnchor="middle" fontSize={20} fontFamily="Georgia, serif" fill="#5a5a66">
              {col.note}
            </text>
          </g>
        ))}
        {/* THE CAST AS ACTUALLY LOCKED, which is the pair that has to read apart
            at thumbnail size. Same scale, same pose, side by side: if you cannot
            tell them apart with the page squinted at, the silhouette work failed
            and no amount of face detail will save it. */}
        <text x={540} y={570} textAnchor="middle" fontSize={40} fontFamily="Georgia, serif" fill="#1a1a22">
          THE CAST
        </text>
        <g transform="translate(300,990) scale(0.82)">
          <Ray frame={f} pose="stand" emotion="neutral" />
        </g>
        <g transform="translate(780,990) scale(0.82)">
          <Dee frame={f} pose="stand" emotion="neutral" />
        </g>
        <text x={300} y={1060} textAnchor="middle" fontSize={30} fontFamily="Georgia, serif" fill="#1a1a22">
          RAY (athletic)
        </text>
        <text x={780} y={1060} textAnchor="middle" fontSize={30} fontFamily="Georgia, serif" fill="#1a1a22">
          DEE (hourglass)
        </text>
        {/* FACES AT SIZE. The silhouette decides who is speaking; the face decides
            whether you want to look at them. They fail independently, so they get
            looked at independently, big enough to actually judge. */}
        <text x={540} y={1160} textAnchor="middle" fontSize={40} fontFamily="Georgia, serif" fill="#1a1a22">
          FACES
        </text>
        <g transform="translate(300,1800) scale(2.1)">
          <Ray frame={f} pose="stand" emotion="neutral" />
        </g>
        <g transform="translate(780,1800) scale(2.1)">
          <Dee frame={f} pose="stand" emotion="neutral" />
        </g>
        <text x={540} y={1900} textAnchor="middle" fontSize={18} fontFamily="Georgia, serif" fill="#5a5a66">
          {`ray ${RAY_PALETTE.skin} / dee ${DEE_PALETTE.skin}`}
        </text>
      </svg>
    </AbsoluteFill>
  );
};
