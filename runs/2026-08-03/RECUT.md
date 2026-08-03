# CASE No. 0003 — RECUT, 2026-08-03

`case0003_recut.mp4` is the cut to post. `case0003.mp4` is the original ship and
is left byte-for-byte untouched, because shipped run artifacts are not this
routine's to overwrite.

Not one claim, not one line of dialogue and not one word of the caption has
changed. What changed is where the camera was pointed, and how long the film
waits between lines.

## Why there is a recut at all

Case 0003 was merged to `main` without Phase 6 ever running. There is no scorer
verdict and no score card for it, and all six funny reads in
`ledger/verdicts.json` predate the count-room rewrite the episode actually
shipped with. Every objective gate was green, which is exactly the problem:
those gates ask about the FILE, and the panel is the only thing that asks about
the EPISODE.

Run cold the next morning against the shipped cut:

| critic | shipped cut | after pass 1 | after pass 2 |
| --- | --- | --- | --- |
| funny (script, unchanged) | 64 | 64 | 64 |
| flow | 58, `recut` | — | — |
| storyboard (craft) | 44, `fix-then-proceed` | 62, `fix-then-proceed` | see panel/ |
| reader-sim, first scroll risk | 19.0s | 10.1s | see panel/ |
| reader-sim, "stopped being new" | 16.2s | 25.2s | see panel/ |

## What was actually wrong, and what was not

Two of the three graded critics reported the episode's central image as missing.
Both were wrong, and the record should say so.

> flow: "S8 promised eight identical head lines ... Neither is in the render."
> storyboard: `pile-never-rendered` — "in twelve frames spanning the whole
> episode, the floor is an empty black band."

The eight stacked head lines render at 22.2s and fill the frame. The VERIFIED
emboss renders at 31.0s. Both figures stand full-figure in a clean two-shot at
27.6s and 29.0s. The RESOLVED-vs-INVALID payoff is clean and legible at 48.5s.
Every one falls in a gap between cells of a twelve-cell contact sheet, which
samples once every 4.8s. The critics reported what the grid showed. The grid was
the defect, and it is fixed in the same commit: 24 cells, and the sampling
interval now prints on the sheet itself.

## Pass 1: the camera was pointed at nothing

Four defects, all confirmed by opening frames, all camera arithmetic. `Cam` maps
the visible band to `W/2 ± (W/2)/zoom` around `W*cx`, and nobody had computed it.

1. **The funniest line, with no one in shot.** At zoom 1.45 the visible band is
   x 168..912. Ray sat at 108 and Dee at 972, so **both figures were outside the
   frame** and all that rendered was a floating forearm and a footless leg. Now
   0.28W and 0.72W.
2. **Dee's best line over an empty panel.** "Sorry, is there a second word?"
   played against a closed plate that does not start moving for another second.
   Widened from cx 0.86 / zoom 2.2 to cx 0.66 / zoom 1.5, and Ray is in it: the
   joke lands on the face of the person who is NOT talking, and a reaction costs
   zero runtime.
3. **The turn, with Ray decapitated by a shelf.** The brass chute lip passed
   exactly through his crown, and the two payoff words rendered as `LVED` and a
   cropped `INVALID` because the cards ran -43..605 and 518..1166 through a
   window of 180..900. Pulled to zoom 1.15 with both cards inside the band and
   still meeting at 0.5W so he straddles the seam.
4. **The button, out-typed by the thing it buries.** The buried card was 0.9W
   wide, so its head type set larger than the filing's own case caption and
   collided with the burned-in subtitle. Smaller, higher, and the filing wins.

## Pass 2: the pacing, and the rest of the craft

The first recut fixed the frames and did not fix the clock. Both simulated
viewers said the same thing in different words: the film is full of picture and
empty of momentum in the middle. In the shipped cut, **16.2s to 32.6s carried
two lines and eight words**, with wordless holds of 7.6s and 6.0s.

Re-synthesis had been blocked earlier in the run by an HTTP 429 from the TTS
provider. That turned out to be a **per-minute** limit rather than a daily one,
and it replenished: all 17 lines were re-synthesized, `vo_cast --fit` measured
the real takes, and the tight layout came back at 39.22s spoken. That is the
same performance with every silence removed, and it is too tight to be the film.

The shipped timeline is that fit with air added back deliberately, capped:

- **No wordless gap exceeds 2.4s**, against 7.6s and 6.0s before.
- The two longest holds are spent where the sight gags actually are: the
  painted-shut panel into the high-angle intake, and the eight-card wall.
- Spoken ends 51.78s, +1.5s tail = **53.27s**, inside the 50 to 58 target band
  and comfortably under the sixty-second law.

The scene was retimed by mapping every one of its 79 time literals through the
same old-to-new anchor mapping as the script, piecewise linear between line
starts. No shot was cut, reordered or dropped, which preserves the director's
do-not-cut list by construction: S7 and S8 remain one move, S11 still lands
before the euphemism S12 answers, S5 is still the only human-scale object, and
S14 still matches the framing of second 2.6.

Craft fixes from the pass-1 panel, all of them the same body-integrity class:

- **The card type collision, which was on every card in the episode.** The head
  line sat at 0.17h and the case number at 0.325h, a gap of exactly 0.155h,
  which is exactly the case number's cap height. Zero leading by construction,
  so the digits' cap-tops landed on the head line's baseline. On the eight-card
  wall that is visible eight times at once, and legible paperwork is the brand's
  entire promise. Now 0.155h and 0.34h, giving 0.03h of real leading, with the
  printed band still ending by 0.34h so CardPile's 0.36 reveal floor is intact.
- **Ray headless at the top of frame, Dee cut by the chute lip** in the same
  shot: at zoom 1.55 the band was y 379..1618 and his crown sat at 338. Pulled
  to 1.30 and both are whole.
- **Dee sliced by the right frame edge** in the two-shot: same arithmetic as
  defect 1, one shot along. She sat at 0.84W in a band ending at 0.81W.
- **The filing's ALLEGED footer stacking on the buried card's INVALID**, dropped
  clear.

## What is still true of this cut

The funny score is a **script** judgement read cold, and no line changed, so it
is still 64. The panel's own evidence is that this reads worse on the page than
it plays: the funny critic wanted "He got sued once." cut, and both simulated
viewers laughed at it, because the picture has already said nine. That is worth
knowing before anyone treats 64 as the last word, and it is also not an excuse.
The next real move on this episode is a rewrite of the first thirty seconds,
which is a writers-room job and not a camera one.

## Verification

- `retime_check`: PASS, 18 shots, 0.0 to 53.3s unbroken, no holes and no
  degenerate ranges.
- `script_check`: PASS, including the new restatement guard.
- `face_check`: PASS.
- `vo_soundcheck --episode`: PASS on all 17 takes.
- `gen_captions_ts --check`, `gen_faces_ts --check`, `vo_envelope --check`: all
  regenerated from this cut's takes.
- `mux_and_verify`: MUX OK.
- `render_gate`: PASS.
- `caption_check`: PASS.
- TTS: 20 calls of a 75 working cap.

`vo_lines.json` is committed here for the first time. Without it `render.sh
final` correctly refuses to rebuild this episode at all, because
`case0003_captions.ts` is committed and nothing could prove its source still
matched. `out/dispatch/` is gitignored scratch that does not survive the
container, so an episode whose only copy of that file lived there was
unrebuildable the moment its session ended.

## Pass 3: the cold open was a frozen frame

The retimed cut fixed the middle and the final viewer read confirmed it in
those words: three laughs where there had been two (9.2s, 34.6s, 39.2s), scroll
risks down from six to three, and "the middle you asked about mostly holds now."

It also moved the worst remaining hold to the front of the film. The first 2.4s
had no animated property at all, and the viewer's first scroll risk landed at
3.0s with the note "pixel-for-pixel what it was at 0.0". On short form those are
the only three seconds that decide anything, and the shot was spending them on a
still life.

The board's own description of the shot is "a court case being MANUFACTURED", so
it is now manufactured: the card rides up into frame and settles under a slow
push, and the premise is stated by motion before it is stated by a word.
Frame-to-frame delta across the cold open went from zero to 58.4 between 0.3s
and 1.0s. `stills/cold_open_0.3_1.0_2.0.png` is the proof.

## Known and open, in priority order

1. **The first thirty seconds still read as fog on the page.** Funny 64 is a cold
   script read and no recut changed a line. This is a writers-room rewrite and it
   is the only thing standing between this episode and the 78 threshold.
2. **The institution beat, around 27.4s to 31.8s**, is an empty lectern holding a
   teal-on-teal legal caption the viewer could not finish reading. Last remaining
   wordless-and-static stretch.
3. The caption overlaps the buried card slightly at ~52s.
