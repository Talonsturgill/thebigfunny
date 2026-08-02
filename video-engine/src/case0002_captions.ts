/**
 * case0002_captions.ts — GENERATED from out/dispatch/vo_lines.json.
 *
 * Do not hand-edit. Each cue's start is the frozen script time the storyboard is
 * also cut to, and each end is the MEASURED duration of the take that was
 * actually synthesized, so the burned-in caption cannot drift from the spoken
 * word.
 *
 * `who` carries the SPEAKER, which does two jobs: it colours and labels the
 * caption, and it drives which character's mouth is moving. The engine forbids
 * real lip-sync on purpose (see the owner rule in lib/voice.tsx: figures chat IN
 * the scene, they do not mouth the voiceover), so `who` is used as a binary
 * is-this-one-talking signal and lib/voice.tsx's ambientMouth supplies the
 * generic conversational cycle. Nothing here needs to stay in sync per word.
 */
export type Cue = {start: number; end: number; who: string; text: string};

export const CAPTIONS: Cue[] = [
  {start: 0.0, end: 4.374, who: 'RAY', text: 'Ford recalled its hybrid SUVs over a noise they\'re required to make.'},
  {start: 4.63, end: 7.506, who: 'DEE', text: 'It doesn\'t always play. That\'s the recall.'},
  {start: 7.77, end: 8.918, who: 'RAY', text: 'So fix it.'},
  {start: 9.18, end: 13.401, who: 'DEE', text: 'They did. Software update in October, letters mailed November fifth.'},
  {start: 13.66, end: 16.329, who: 'DEE', text: 'Forty-three thousand, four hundred thirty-eight.'},
  {start: 16.59, end: 21.022, who: 'DEE', text: 'It\'s back. Sixty-six thousand, three hundred eighty-three.'},
  {start: 21.28, end: 27.276, who: 'DEE', text: 'NHTSA calls it an expansion. The ones they fixed have to be fixed again.'},
  {start: 27.54, end: 31.485, who: 'DEE', text: 'The only fix they have is for the version with twenty-eight speakers.'},
  {start: 31.74, end: 36.708, who: 'RAY', text: 'Twenty-eight speakers. That\'s how they decide who gets fixed.'},
  {start: 36.97, end: 43.281, who: 'INSTITUTION', text: 'Interim letters notifying owners of the safety risk are expected to be mailed August third.'},
  {start: 43.54, end: 44.389, who: 'RAY', text: 'That\'s tomorrow.'},
  {start: 44.65, end: 47.373, who: 'RAY', text: 'I still have the first letter.'}
];

/** Who is speaking at time t, or null. */
export const speakerAt = (t: number): string | null => {
  const c = CAPTIONS.find((x) => t >= x.start && t <= x.end);
  return c ? c.who : null;
};
