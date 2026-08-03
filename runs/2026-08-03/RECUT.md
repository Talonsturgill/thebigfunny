# CASE No. 0003 — RECUT, 2026-08-03

`case0003_recut.mp4` is the cut to post. `case0003.mp4` is the original ship and
is left byte-for-byte untouched, because shipped run artifacts are not this
routine's to overwrite.

Nothing in this cut changes a claim, a line of dialogue, a timing or the audio.
Every change is where the CAMERA was pointed. The audio track is the original,
unmodified, and the burned-in captions are the same generated cue file.

## Why there is a recut at all

Case 0003 was merged to `main` without Phase 6 ever running. There is no scorer
verdict and no score card for it, and all six funny reads in `ledger/verdicts.json`
predate the count-room rewrite the episode actually shipped with. Every objective
gate was green, which is exactly the problem: those gates ask about the FILE, and
the panel is the only thing that asks about the EPISODE.

Run cold the next morning against the shipped cut:

| critic | score |
| --- | --- |
| funny | 64 |
| flow | 58, verdict `recut` |
| storyboard (craft) | 44, verdict `fix-then-proceed` |
| reader-sim | first scroll risk at **19.0s** |

## What was actually wrong, and what was not

Two of the three graded critics reported the episode's central image as missing.
Both were wrong, and it matters that the record says so.

> flow: "S8 promised eight identical head lines ... Neither is in the render."
> storyboard: `pile-never-rendered` — "in twelve frames spanning the whole
> episode, the floor is an empty black band."

The eight stacked head lines render at 22.2s and fill the frame. The VERIFIED
emboss renders at 31.0s. Both figures stand full-figure in a clean two-shot at
27.6s and 29.0s. The RESOLVED-vs-INVALID payoff is clean and legible at 48.5s.
Every one of those falls in a gap between cells of a twelve-cell contact sheet,
which samples once every 4.8s. The critics reported what the grid showed. The
grid was the defect, and it is fixed in the same commit (24 cells, and the
sampling interval now prints on the sheet).

### The four defects that were real

All four were confirmed by opening the frames, and all four are camera geometry.

1. **7.4s, the film's own `funniest_line_intended`.** `Cam` at zoom 1.45 makes
   the visible band x = 168..912. Ray sat at `W*0.10` (108) and Dee at `W*0.90`
   (972), so **both figures were outside the frame** and all that rendered was a
   floating forearm and a footless leg. Now `W*0.28` and `W*0.72`: two whole
   people, Ray standing on the pile the shot is about.

2. **43.1s, Dee's best line.** "Sorry, is there a second word?" played over a
   closed panel with nobody in frame; the plate does not start moving until
   44.1s, so the first second of the shot was inert wall. Widened from cx 0.86 /
   zoom 2.2 to cx 0.66 / zoom 1.5 and Ray is in it. The house rule is that the
   joke lands on the face of the person who is NOT talking, and a reaction costs
   zero runtime.

3. **50.3s, the turn.** The brass chute lip passed exactly through Ray's crown;
   he read as decapitated by a shelf. Separately the two payoff words rendered as
   `LVED` and a cropped `INVALID`, because the cards ran -43..605 and 518..1166
   through a window of 180..900. Pulled back to zoom 1.15 with both cards inside
   the band and still meeting at `0.5W` so he straddles the seam, and his ground
   dropped to `0.910H` to clear the lip. Both words are now fully legible.

4. **52.3s, the button.** The buried card was `0.9W` wide, so its head type set
   LARGER than the filing's own case caption and collided with the burned-in
   subtitle. The thing being buried was out-typing the thing burying it. Now
   `0.55W` and higher, so its type sits in the band between the filing's bottom
   edge and the caption, and the filing wins the frame.

## What is still true of this cut

The pacing note stands and is not fixed here, because fixing it means moving the
timeline and this cut deliberately does not touch the audio: **from 16.2s to
32.6s the script has two lines and eight words**, with silences of 7.6s and 6.0s.
That stretch is full of picture but empty of momentum, and it is where the
simulated viewer's thumb left the screen. The frames are fixed; the pacing is a
retime and it is the next thing to do.

## Verification

- `retime_check`: PASS, 18 shots, 0.0 to 56.9s unbroken, no holes.
- `script_check`: PASS, including the new restatement guard.
- `face_check`: PASS, 31 expression changes, 18 listener reactions.
- `mux_and_verify`: MUX OK, mean volume -20.2 dB.
- `render_gate`: PASS. 58.26s, 1080x1920, both tracks present.
- `caption_check`: PASS.
- Captions verified against the SHIPPED AUDIO rather than against another
  derived file: all 17 cue starts land 0.04 to 0.06s before measured speech
  onset, a constant decoder priming offset.

`vo_lines.json` is committed here for the first time. Without it `render.sh
final` correctly refuses to rebuild this episode at all, because
`case0003_captions.ts` is committed and nothing could prove its source still
matched. `out/dispatch/` is gitignored scratch and does not survive the
container, so an episode whose only copy of that file lived there was
unrebuildable the moment its session ended.
