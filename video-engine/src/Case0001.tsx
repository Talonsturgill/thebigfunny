/**
 * Case0001.tsx — THE BIG FUNNY, case 0001.
 * "The Pricing Update With No Pricing In It"
 *
 * Angle (euphemism): Microsoft raised the price of Office, called it a
 * "packaging and pricing update", and the official FAQ explaining it contains
 * no prices.
 *
 * Every factual string on screen traces to out/dispatch/claims.json. The
 * Institution's line is verbatim c3 and must not be paraphrased.
 *
 * This is the FIRST episode composition, so it doubles as the proof that
 * brand.tsx and cast.tsx render at all. Deliberately built from the shelf:
 * PaperOfficeBG (the library's only interior), Ray, Dee, MachineShadow-as-text,
 * and the brand components. Nothing new was drawn for it.
 */
import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {z} from 'zod';
import {Ray, Dee, DEE_CRACK} from './lib/cast';
import {Wordmark, CaseNumber, EndCard, Highlighter, Stamp, BRAND, PROMISE} from './lib/brand';
import {PaperOfficeBG} from './lib/paper';

export const case0001Schema = z.object({total: z.number().optional()});

const FPS = 30;
const s = (sec: number) => Math.round(sec * FPS);

/**
 * The art layer.
 *
 * MOUNTING CONTRACT, learned the hard way on case 0001: everything in src/lib/
 * (Character, the biomes, props, fauna) returns SVG elements and MUST be inside
 * an <svg viewBox="0 0 1080 1920">. Put them in a plain div and React happily
 * renders them into an HTML context where they are invisible. It typechecks, it
 * exits 0, and the frame comes out empty.
 *
 * brand.tsx is the opposite: those are HTML divs and must stay OUTSIDE this.
 */
const Art: React.FC<{children: React.ReactNode}> = ({children}) => (
  <svg width="1080" height="1920" viewBox="0 0 1080 1920"
       style={{position: 'absolute', inset: 0}}>{children}</svg>
);

/** Burned-in caption. The show is watched muted more often than not. */
const Caption: React.FC<{text: string; y?: number}> = ({text, y = 1500}) => (
  <div style={{
    position: 'absolute', left: 60, right: 60, top: y,
    textAlign: 'center', fontFamily: 'Arial Black, DejaVu Sans, FreeSans, sans-serif', fontWeight: 900,
    fontSize: 58, whiteSpace: 'pre-line', lineHeight: 1.12, color: BRAND.PAPER,
    textShadow: '0 4px 0 rgba(16,20,35,0.85), 0 0 22px rgba(16,20,35,0.6)',
    letterSpacing: '-0.01em',
  }}>{text}</div>
);

/** The Institution: policy text on a cold plate. NO FACE, EVER. */
const InstitutionPlate: React.FC<{frame: number; text: string}> = ({frame, text}) => {
  const up = interpolate(frame, [0, 10], [40, 0], {extrapolateRight: 'clamp'});
  const op = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: BRAND.CARBON, opacity: op}}>
      <div style={{
        position: 'absolute', left: 90, right: 90, top: 720 + up,
        fontFamily: 'Arial, sans-serif', fontSize: 46, lineHeight: 1.42,
        color: BRAND.PAPER, opacity: 0.96,
      }}>{text}</div>
      <div style={{
        position: 'absolute', left: 90, top: 640,
        fontFamily: 'Arial, sans-serif', fontSize: 22, letterSpacing: '0.34em',
        color: BRAND.PAPER, opacity: 0.5,
      }}>MICROSOFT, ON THE RECORD</div>
    </AbsoluteFill>
  );
};

export const Case0001: React.FC<z.infer<typeof case0001Schema>> = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  return (
    <AbsoluteFill style={{background: BRAND.MANILA}}>
      {/* The set: the library's interior. An office story belongs in the office. */}
      <Art><PaperOfficeBG f={frame} parallax={0.4} drift={0.5} /></Art>

      {/* Cold open, NO logo. The first two seconds are the fact, flat. */}
      <Sequence from={0} durationInFrames={s(5.4)}>
        <Art><Ray frame={frame} x={540} y={1180} scale={1.25} emotion="angry" pose="arms-crossed" /></Art>
        <Caption text={"Microsoft put the price of Office up.\nThey're calling it a packaging and pricing update."} y={1440} />
      </Sequence>

      {/* The wordmark STAMPS at ~2s. Once. Never a fade. */}
      <Sequence from={s(2.0)} durationInFrames={s(2.2)}>
        <Wordmark frame={frame - s(2.0)} fps={fps} x={540} y={620} scale={0.9} />
      </Sequence>

      {/* The turn: Dee supplies the detail that makes it worse. */}
      <Sequence from={s(5.4)} durationInFrames={s(11.4)}>
        <Art><Dee frame={frame - s(5.4)} x={700} y={1180} scale={1.18} /></Art>
        <Art><Ray frame={frame - s(5.4)} x={330} y={1180} scale={1.12} facing={1} emotion="worried" pose="stand" /></Art>
        <Caption text={'"Packaging and Pricing Updates for Microsoft 365 Commercial Suites. Public FAQs."'} y={1420} />
      </Sequence>

      {/* Dee's ONE crack: she has to say the absurd thing out loud. */}
      <Sequence from={s(16.8)} durationInFrames={s(6.4)}>
        <Art><Dee frame={frame - s(16.8)} x={700} y={1180} scale={1.18} emotion={DEE_CRACK} /></Art>
        <Art><Ray frame={frame - s(16.8)} x={330} y={1180} scale={1.12} emotion="shock" pose="panic" /></Art>
        <Caption text={'The FAQ about the price increase\nhas no prices in it.'} y={1420} />
      </Sequence>

      {/* Ray finds out. The show. */}
      <Sequence from={s(23.2)} durationInFrames={s(6.8)}>
        <Art><Ray frame={frame - s(23.2)} x={540} y={1180} scale={1.3} emotion="angry" pose="point" /></Art>
        <Caption text={"That's not an FAQ.\nThat's a hostage video."} y={1440} />
      </Sequence>

      {/* The only number in the episode, and the only highlighter swipe. */}
      <Sequence from={s(30.0)} durationInFrames={s(4.2)}>
        <Art><Dee frame={frame - s(30.0)} x={540} y={1180} scale={1.2} /></Art>
        <div style={{position: 'absolute', left: 0, right: 0, top: 780, textAlign: 'center'}}>
          <div style={{position: 'relative', display: 'inline-block'}}>
            <Highlighter frame={frame - s(30.0)} width={620} height={64} x={-10} y={4} />
            <div style={{
              position: 'relative', fontFamily: 'Arial Black, DejaVu Sans, FreeSans, sans-serif', fontWeight: 900,
              fontSize: 62, color: BRAND.INK, padding: '0 12px',
            }}>$23 &rarr; $26 A SEAT</div>
          </div>
        </div>
        <Caption text={'Office 365 E3, per user, per month.'} y={1440} />
      </Sequence>

      <Sequence from={s(34.2)} durationInFrames={s(7.8)}>
        <Art><Ray frame={frame - s(34.2)} x={540} y={1180} scale={1.3} emotion="smug" pose="arms-crossed" /></Art>
        <Caption text={'Somebody wrote the whole explanation\nand took the number out.\nThat’s not an oversight. That’s a craft.'} y={1360} />
      </Sequence>

      {/* The Institution answers. Verbatim c3. Politely. It does not budge. */}
      <Sequence from={s(42.0)} durationInFrames={s(8.4)}>
        <InstitutionPlate
          frame={frame - s(42.0)}
          text={'"This change reflects the significant innovation delivered over the last several years and the expanded value customers will gain with new additions to the suites."'}
        />
      </Sequence>

      <Sequence from={s(50.4)} durationInFrames={s(2.0)}>
        <Art><Ray frame={frame - s(50.4)} x={540} y={1180} scale={1.3} emotion="neutral" pose="stand" /></Art>
        <Caption text={'I gained a bill.'} y={1440} />
      </Sequence>

      {/* THE BUTTON: the real receipt, and the episode's ONE stamp. */}
      <Sequence from={s(52.4)} durationInFrames={s(3.6)}>
        <AbsoluteFill style={{background: BRAND.PAPER}}>
          <div style={{
            position: 'absolute', left: 70, right: 70, top: 520,
            fontFamily: 'Arial, sans-serif', color: BRAND.INK,
          }}>
            <div style={{fontSize: 20, letterSpacing: '0.28em', opacity: 0.55}}>MICROSOFT.COM / LICENSING</div>
            <div style={{fontSize: 52, fontFamily: 'Arial Black, DejaVu Sans, sans-serif', fontWeight: 900, marginTop: 18, lineHeight: 1.1}}>
              Packaging and Pricing Updates for Microsoft 365 Commercial Suites Public FAQs
            </div>
            <div style={{marginTop: 34, fontSize: 30, opacity: 0.75, lineHeight: 1.5}}>
              Effective July 1, 2026.<br />
              <span style={{opacity: 0.55}}>No price appears on this page.</span>
            </div>
          </div>
          <Stamp frame={frame - s(53.4)} fps={fps} x={700} y={1180} rotate={-11}>
            <div style={{fontSize: 96, border: '9px solid currentColor', padding: '10px 26px'}}>NO PRICES</div>
          </Stamp>
        </AbsoluteFill>
      </Sequence>

      {/* End card: case number and the promise. Nothing else. */}
      <Sequence from={s(56.0)}>
        <EndCard n={1} frame={frame - s(56.0)} fps={fps} />
      </Sequence>

      {/* The case number rides the whole episode except the end card. */}
      {frame < s(56.0) && <CaseNumber n={1} y={96} color={BRAND.PAPER} />}
    </AbsoluteFill>
  );
};
