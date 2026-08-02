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
  {start: 0.0, end: 5.049, who: 'RAY', text: 'Ford recalled its hybrid SUVs over a noise they\'re required to make.'},
  {start: 5.31, end: 9.282, who: 'DEE', text: 'It doesn\'t always play. That\'s the recall.'},
  {start: 9.54, end: 11.285, who: 'RAY', text: 'So fix it.'},
  {start: 11.55, end: 17.789, who: 'DEE', text: 'They did. Software update in October, letters mailed November fifth.'},
  {start: 18.05, end: 21.37, who: 'DEE', text: 'Forty-three thousand, four hundred thirty-eight.'},
  {start: 21.62, end: 26.375, who: 'DEE', text: 'It\'s back. Sixty-six thousand, three hundred eighty-three.'},
  {start: 26.64, end: 32.151, who: 'DEE', text: 'NHTSA calls it an expansion. The ones they fixed have to be fixed again.'},
  {start: 32.41, end: 37.147, who: 'DEE', text: 'The only fix they have is for the version with twenty-eight speakers.'},
  {start: 37.41, end: 42.24, who: 'RAY', text: 'Twenty-eight speakers. That\'s how they decide who gets fixed.'},
  {start: 42.5, end: 48.522, who: 'INSTITUTION', text: 'Interim letters notifying owners of the safety risk are expected to be mailed August third.'},
  {start: 48.78, end: 50.13, who: 'RAY', text: 'That\'s tomorrow.'},
  {start: 50.39, end: 53.028, who: 'RAY', text: 'I still have the first letter.'}
];

/** Who is speaking at time t, or null. */
export const speakerAt = (t: number): string | null => {
  const c = CAPTIONS.find((x) => t >= x.start && t <= x.end);
  return c ? c.who : null;
};
