# Field Notes

Living lessons. Every rule in this repo that looks arbitrary is probably in
here with the reason attached. Read this before overriding anything.

Phase 8 appends to this file every run. A lesson that only exists in a run's
context dies with that context, which is the whole reason the file exists.

---

## Inherited scar tissue (from the two upstream machines, before episode 1)

These were paid for by `alaska-ai-weekly` and `alaskaaicarousels`. They cost
real runs. We start with them rather than rediscovering them.

### A rubric that always passes measures nothing
The upstream publication found its scorer grading its own homework and calling
everything shippable. The fix was hard gates that cannot be averaged away, plus
a critic that never sees the threshold it is being graded against. That is why
`funny-critic` is deliberately blind to the ship threshold and why the scorer is
forbidden from revising its number upward.

### The gate that cannot fail certifies nothing
A regression test built only from currently-passing material will certify
whatever the code does today. Upstream, both the date gate and the beacon gate
grew a `--self-test` that deliberately reintroduces the original bug and
requires the gate to go red. **Any gate added here needs the same.** If you
cannot make it fail on purpose, you have not tested anything.

### Verified with the wrong tool is not verified
A reader-counter upstream was "verified" with curl and recorded zero from every
real visit for an hour, because the bug was a CORS preflight and curl never
sends one. Every check that passed did so because it was not a browser.
**Verify with the thing that will actually be used.** For this repo that means:
a VO is verified by word-error-rate against the audio, not by reading the
script; a render is verified by watching frames, not by the render exiting 0.

### 204 to everything means you cannot see your own failures
The same collector answered success to every outcome including all its silent
drops, so a working system and a broken one looked identical from outside. When
you add a stage that can discard work, **make it record WHY**. A run that dies
should always leave the reason behind.

### Sort keys lie
A homepage upstream paired one item's title with a different item's date because
the sort key and the rendered value were computed separately. The reasoning at
the time ("a sort key cannot lie because it is not rendered") was wrong.
**Derive the displayed thing and the ordering thing from the same resolved
object.**

### Squash merges can land the same code twice
A squash merge upstream landed a tracking beacon twice and double-counted every
event for a day. It was missed because the check used `grep -c`, which counts
LINES not OCCURRENCES. Count occurrences with `.count()` and diff live against
local before believing a deploy.

### The library mandate exists because redrawing is where runs die
`ASSET_MANIFEST.md`: compose from the shelf first, grow it only on a real gap,
register additions in the same commit. Two upstream runs failed a gate because
an asset file existed but was never registered, so the gate could not find it.
**Manifest drift is a real bug class.** Register in the same commit or not at
all.

### Cones read as lollipops
Twice upstream, a cone drawn face-on as an ellipse over a body read as a flat
disc, once as a "black satellite dish". The fix each time: flatten the rim
ellipse so the camera looks ALONG the cone, inset the dark interior down the
throat, and draw the two taper walls as separate lit and shaded faces. Applies
to any 3/4 cone this show ever draws.

### The gag belongs to whoever owns it
A creative gate upstream rejected a cartoon envelope that pulled a face, on the
grounds that the gag belonged to the institution and not to the paper. That
ruling became this show's hardest rule: **the Institution has no face, ever.**

---

## The Big Funny, episode 1 onward

*(Phase 8 appends below. Newest first. One entry per run, pass or fail.)*

### Case 0002 (2026-08-02): the first delivered episode, and four things that nearly stopped it

**A words-per-second constant cannot time a script. Measure the takes.**
`vo_cast.py`'s static check assumes 3.6 w/s. Real measured delivery on this
cast is 1.85 to 2.81 w/s, and it varies BY LINE, because a full stop mid-line
buys a pause no word count can see: the same voice ran 2.07 w/s on one line and
2.43 on another. The first synthesis died with Ray's opening line needing 7.33s
in a 4.20s slot, AFTER the take was paid for. Guess-and-fail does not converge,
because each edit changes the rate. `--fit` now synthesizes once, caches every
take on disk by (voice, style, text), measures, and lays the timeline out from
what the takes actually are. Use it. Iterating on the script after that is free.

Gemini also pads every take with about 0.25s of lead and 0.30s of tail. Over a
dozen lines that is most of a beat spent saying nothing, and worse, the padding
lands INSIDE the slot, so a take that fits perfectly well overruns and fails the
run for a reason that has nothing to do with the writing. `trim_silence()`
strips it, which also makes captions.json honest: the cue ends when the SPEECH
ends, not when the file does.

**A gate that fails for the wrong reason is worse than no gate.**
`mux_and_verify.sh` measured audio with `-af volumedetect`. The ffmpeg Remotion
vendors is built `--disable-filters` with a whitelist that has neither
`volumedetect` nor `astats`. So on any host without a system ffmpeg, the
documented fallback measured NOTHING, and the script reported "has no audio
stream at all" on a perfectly good mux. The fallback that exists precisely so
the mux always works could never pass, and its error message pointed at
entirely the wrong problem. It now decodes to PCM and computes RMS in stdlib
python, which needs no filters at all.

Corollary, learned while writing that gate's self-test: **the vendored ffmpeg
has no `wrapped_avframe` decoder**, so every lavfi VIDEO source (`nullsrc`,
`testsrc`) fails to encode there. Build fixture video from a generated PNG
instead. The first cut of the self-test used nullsrc and printed "THE GATE IS
WRONG" when the gate was fine and only the fixture was unbuildable.

**Draw the rule, not the part.** Gate 0 killed a shot that would have taught
viewers something the fact-checker had explicitly CUT. The story's funniest
detail is that the federal record sorts repairable cars by speaker count, and
the board staged it as a lone "28 SPEAKERS" badge. A single isolated spec chip
does not read as a window sticker, it reads as a CALLOUT ON THE BROKEN PART, so
the viewer would have walked away believing the 28 speakers failed, which the
record never says. The fix was to draw the SORTING: a two-row eligibility list
quoting the remedy field on both sides. **When a claim is cut for being an
unprovable inference, check that the PICTURE cannot imply it either.** Prose
guards do not bind the storyboard.

**Look at the whole figure, not the frame.** A stray dark red arc rendered
across Ray's thighs in every shot for two full renders before the craft panel
caught it. Root cause: the flannel plaid's third horizontal stripe sits at
y=30, the coat silhouette bottoms out at y=10, and the stripes are drawn
unclipped and AFTER the legs. It had presumably been there since the outfit was
authored. On a show whose law is one red per episode it also put an unintended
STAMP-adjacent red on screen for the entire runtime. Two lessons: unclipped
decoration inside a `<g>` leaks past the silhouette it belongs to, and
"verified by looking at the frame" means looking at the whole figure, because
the eye goes to the face and the bug was at the knees.

**The one-stamp rule was asserted rather than earned.** `Wordmark` and `EndCard`
both render through `Stamp`, which defaults to STAMP red, so any episode that
also stamps its receipt spends the red token three times and halves it twice.
Both now take an explicit `color`. `Stamp` also needed a `blend`, because
ink-into-paper is a multiply, which is right on a light ground and INVISIBLE on
a dark one: the first night-set wordmark vanished completely. If a brand rule is
stated in prose but nothing in code enforces it, assume it is being violated.

**A self-test that cannot ISOLATE cannot detect a dead guard.** Found in this
run's phase 8, one level up from the rule it refines. `script_check.py` shipped
with four guards and a self-test whose cases each asserted "some row went red".
Disabling the Ray-gap guard entirely (`MAX_RAY_GAP_S = 999`) still printed all
green, because that case's fixture also had no Ray in the middle third and the
neighbouring guard covered for the dead one. The repo's oldest rule says a gate
that cannot fail certifies nothing; the corollary is that each case must name
the guard it trips and the fixture must trip ONLY that guard, or the self-test
is measuring the union of the guards rather than any of them. Verify a new
self-test by breaking each guard in turn and requiring the corresponding case,
not merely the suite, to go red.

**KNOWN GAP: the funny gate still has no self-test.** It is the heaviest
criterion at 35 percent and the only one whose verdict is a model judgement, so
it cannot be self-tested the way `render_gate` and `script_check` are. The
obvious design is a committed known-unfunny fixture script that `funny-critic`
must score under 60, read blind alongside the real one. That is worth building,
and it was not built here because it cannot be verified without spending the
model call the gate exists to grade, and this repo does not log a change it has
not run. Until it exists, the funny score is the one number in the rubric with
nothing behind it but the critic's own discipline.

### Case 0001 (2026-08-01): the mounting contract nobody wrote down

**Everything in `src/lib/` returns SVG and MUST be inside an
`<svg viewBox="0 0 1080 1920">`.** `brand.tsx` is the opposite: those are HTML
divs and must stay OUTSIDE it.

Case 0001's first render was a nearly empty frame. Ray, Dee and the whole office
set drew nothing, because they were mounted in plain `<div>`s. React renders SVG
elements into an HTML context perfectly happily: no warning, no error, `tsc`
exits 0, `remotion still` exits 0, and the PNG is blank where the art should be.
The only signal was the file size, 230KB instead of 900KB.

This is the sharpest possible version of a lesson already in this file twice
over: a thing that typechecks is not a thing that works, and verification has to
use the tool that will actually be used. Nothing short of looking at the frame
would have caught it. Use `Art` in `Case0001.tsx` as the reference mount.

**No Arial on the render host.** fontconfig has DejaVu and FreeSans only, so
`Arial Black` silently fell back to a regular weight and every caption rendered
thin. Always pair the family with an explicit `fontWeight: 900` and a stack that
names an installed face. Silent font fallback is invisible in code review and
obvious on screen.

**Two stories died at the fact-check gate, and that is the gate working.**
A real estate "junk fees" report was dropped because its primary PDF used
multiple subset fonts with different CMaps and could not be quoted verbatim, and
the trade press described it as "based largely on anecdotal evidence". Then the
widely repeated "Microsoft 365 prices up to 43 percent" was cut because it had
one source and CONFLICTED with a per-SKU table attributed to Microsoft showing a
maximum of 14. The episode is stronger without it. Killing a number is cheap.

### Before the first run: what we expect to get wrong

Written in advance so we can check our own predictions honestly rather than
retrofitting a story to whatever happens.

1. **Funny will score lower than we want, for a while.** The predicted failure
   is agreement-not-comedy: a true infuriating fact everyone already knows,
   restated with attitude, and no actual joke. The angle taxonomy's first law
   exists to catch it and it will still get through.
2. **Sixty seconds will feel short and that is the point.** Expect early scripts
   to run 75 to 90 seconds and expect the cut to improve them. If a script only
   works at 80, the angle is too broad.
3. **Ray will drift into ranting.** Ranting is not concluding. The tell is a
   line that explains why the previous line was outrageous.
4. **Someone will want to give the Institution a face.** It will seem like a
   great gag. It is the one that kills the premise.
5. **The temptation to soften a claim to save an angle will arrive early.** That
   is the move that ends channels. Kill the story instead; there are seven
   beats and something happened in one of them today.
