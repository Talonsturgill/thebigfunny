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
