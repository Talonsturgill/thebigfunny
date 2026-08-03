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

### 2026-08-02: three bugs, one shape, and none of them failed anything

Case 0002 shipped, cleared every gate, and was then watched by the owner, whose
first note was that the voices sounded robotic. Chasing that turned up three
separate defects that share a shape worth naming, because the shape is what the
gates cannot see.

**A silent downgrade beats a loud one every time.** `vo_cast.py` set
`DISPATCH_GEMINI_TTS_MODEL` at module scope; `vo_gemini` reads that variable when
it is imported, which happens later. So the older model won on IMPORT ORDER
alone, every take of the episode was synthesized on it, and the run reported the
newer model in a commit message, a ledger entry and a cast bible. Nothing threw.
The audio was fine, the render was fine, the gates were fine, and the claim was
false. **Two defaults for one setting is the bug.** If a setting matters, one
place owns it and something READS BACK what actually resolved.

**Then the cache would have covered for the fix.** The take key covered the
voice and the whole director's brief but not the model, so correcting the model
would have replayed the old audio off disk under the new model's name. The key
was also written out twice, in two functions, which is why the omission survived:
duplicated keys have to be edited in lockstep forever and never are.

**Then the picture would have gone stale silently.** Twenty-odd hand-typed
seconds across three files described one thing, the shot ladder, and
re-synthesizing the VO moves all of them. A stale one is invisible in review AND
in the render, because every file stays internally consistent and the cut simply
lands on the wrong word.

The common shape: **an input that changes the OUTPUT without changing anything
that is checked.** Every gate in this machine asks "did it render, is it under
sixty, is it sourced, is it funny". None of them asks "is this the thing you said
it was". So when a value decides how the show sounds or looks, derive it, key on
it, or assert it. Do not write it down twice and trust the copies.

**And the casting one, which is its own lesson.** Dee was cast as Schedar, whose
one-word descriptor in the roster is "Even", and her brief then asked for
"completely deadpan" with "no rising intonation". The flattest voice available,
instructed to flatten. Two causes stacked, both authored here, neither visible to
any gate. Cast for ECCENTRICITY, and never direct the ABSENCE of prosody: dry and
deadpan describe a withheld REACTION, not a withheld melody. Both are now
refused mechanically in `vo_cast.casting_problems()`, with the Institution
exempt because a phone tree is supposed to sound like one.

The honest coda: a seven-voice sweep measured every candidate between 3.46 and
4.12 semitones of pitch variance, INCLUDING the one already judged robotic. The
soundcheck cannot rank voices. It refuses known causes; the ear picks.

### 2026-08-02, later: I re-rendered five times without looking at a frame

The owner watched the rebuilt episode and said the mouths were floating and the
bodies were not aligned with the speaking. Three defects, all real, all visible
in ONE still once anybody actually opened one:

- The head was never attached to the body. Torso bobbed by `bob`, head by
  `bob * 1.4`, so the head's offset from the shoulders changed every frame.
- The default pose's right arm was a solid black bar, because its ink stroke was
  painted after the colour stroke and 12px wider. `stand` is the default pose, so
  this was in nearly every shot of every episode ever rendered here.
- Nothing in the rig knew a word was being spoken. Bob, sway and mouth were all
  free-running sines. Constant motion unrelated to speech reads as drift.

**The process failure is the lesson, not the three bugs.** I rendered this
episode five times in one session and did not open a single frame until the owner
complained. Every objective gate passed every time, because every objective gate
asks about the FILE: does it parse, is it 1080x1920, is it under sixty, does it
carry audio. Not one of them can see a character.

The repo already has the answer and I skipped it: `storyboard-critic` exists
precisely for this, and it is the agent that caught the red arc across Ray's legs
earlier the same day. It works when it runs.

So: **a render is not finished until a human or the storyboard critic has LOOKED
at frames from it.** Not the codec report, the frames. If a rebuild changes the
rig, the cast, the staging or the timing, pull stills at a speaking beat and at a
held beat and look at them before shipping or before sending anything to the
owner.

The animation lesson underneath it, from the viral formats worth copying: the
body ACCENTS the voice and is otherwise still, and only the speaker moves. A
listener that keeps swaying steals the eye and makes a two-shot unreadable. That
is why `mouth` and `accent` are gated on `speakerAt()` and the listener's idle is
damped rather than everyone being alive at once.

### 2026-08-02: check the frame is not a BLINK before you judge a face

While tuning per-emotion eyes I pulled a still of Dee on `smug`, saw two closed
crescents, concluded the register was too narrow, and retuned the whole eye
table. Then I computed her blink phase: `((f + 11 + floor(swayPhase*13)) % 92)`
put frame 590 three frames into her five-frame closure. **I had tuned an
expression from a frame that was not showing the expression.**

The desync fix (per-figure blink phase, same day) makes this MORE likely, not
less: figures used to blink in unison so a blink frame was obvious, and now one
character can be mid-blink while the other is not, which looks exactly like an
expression difference.

So when judging a face from a still, compute the blink window first and pick a
frame outside it, or pull two frames ten apart. "Look at the frames" is only
worth anything if you looked at the right ones.

(The retune was not wasted, as it happens: keeping the pupil visible in every
register is correct on its own terms. But it was decided for the wrong reason,
which is luck and not method.)

## The Alaska shelf was why episodes were two people talking (2026-08-02)

Four complaints arrived as one diagnosis: the speed, the boring scenes, the
incoherent story, "two ppl talking and doing nothing." They are ONE fault.

The art library was ported from an Alaska show. It is parkas, snow, spruce,
wolves, glaciers. ASSET_MANIFEST told every run to cast from the shelf before
drawing anything new, which is a good rule that was doing quiet damage: the
shelf is a PLACE and the stories are national. So every board dressed an Alaska
set for a story with nothing to do with Alaska, the set could not illustrate
anything, and once the set is inert the only thing left for an episode to do is
have two people talk.

"Two people talking" is not a staging failure. It is what is left after the
world has been amputated from the story.

It also explains the standing repeat offenders. `carried_by_fact` and
`agreement_not_comedy` appeared in both runs on file and the funny critic blamed
the STORY each time. Half right. The fact was carrying the episode because
nothing else was allowed to: not the set, not the props, not the world. A joke
that lives only in the dialogue is a podcast with drawings over it.

THE FIX: the world of the story becomes the set. A Ford engine story is staged
INSIDE a Ford engine. The shelf becomes a KIT of parametric primitives and every
episode BUILDS its world instead of shopping for one. See knowledge/WORLD_KIT.md
and knowledge/DIRECTING.md.

THE SECOND LESSON, about gates: none of this was visible to any gate, because
nothing in the machine ever LOOKED at the episode. Every critic graded JSON.
`scripts/contact_sheet.py` now renders a grid the critics grade, and
`scripts/visual_check.py` refuses talking heads mechanically on the BOARD,
before a cent of audio is bought. A critic downstream of a decision never fixes
the decision.

## An absent input is not a passing input (2026-08-02)

Third time this class bit in one session, and the third one shipped in a gate
whose own docstring promised it did not.

`coherence_check.py` exists to catch the plan and the world describing different
films. Pointed at the real artifacts on its first live run, it returned PASS,
while two independent agents had already found the fork in those same two files.
The bug: `if plan_turn and world_turn:` emitted NO ROW when neither document
declared the field. Silence scored as agreement. Two documents that both fail to
declare the most load-bearing beat in the episode have not agreed, they have not
decided.

THE RULE: when the thing a guard grades is missing, the guard FAILS. It never
skips. A row that is not emitted is indistinguishable from a row that passed, in
the report and in the exit code, and the phase downstream reads both as
permission.

THE COROLLARY, which is how it got caught: verify a gate by RUNNING it against
an empty document, not by reading it. Every gate here now has that test on
record, and story_check and visual_check both survived it because a required
field row fires before the deeper guards get a chance to skip. Reading the code
would have flagged all three as suspects and been wrong about two of them.

A gate whose comment is a lie is worse than one with no comment, because the
comment is what the next author trusts instead of testing.

## Launching an agent and writing its inputs in the same block is a race (2026-08-02)

The Phase 4.4 dry run reported that the script and the world staged two
different mechanisms, and it was right about the bytes on disk and wrong about
the cause. `script.json` was written in the SAME tool block that launched the
director, and the launch went first, so the agent read the previous run's
script. The mismatch was self-inflicted.

WRITE THE INPUTS, THEN LAUNCH. An agent starts reading immediately, and "same
message" is not "before".

What makes this worth writing down rather than just fixing: the director's
BEHAVIOUR under the fault was exactly right, and that is real evidence. It
detected the mismatch, refused to blame the writer, said plainly "that is not a
shot-plan defect I can fix with better shots", and identified that the schema
would have routed the repair to the wrong phase. A fault injected by accident
tested the failure path better than a fixture would have, because nobody wrote
the fixture to be survivable.

## The repo-wide review found 43 defects and 40 of them were one bug (2026-08-02)

A full `/code-review` across `scripts/`, `video-engine/src/lib/` and the
dispatch skill. It ran every gate against empty, blank-but-present and
hollow-but-well-formed documents, and it mutation-tested each self-test by
disabling one guard at a time to see whether the test noticed.

The findings sort into two piles and one of them is enormous.

**A CHECK THAT DID NOT RUN READS EXACTLY LIKE A CHECK THAT PASSED.** This is
already written above as a lesson about missing inputs. The review found it in
thirteen more places, in every layer, wearing different clothes each time:

- `mux_and_verify.sh` discarded ffmpeg's exit code, so a failed mux measured the
  file already at the output path, WHICH IS THE PREVIOUS EPISODE, and printed
  MUX OK. Its own staleness guard was written `[ -f "$VIDEO" ] && [ -f "$AUDIO" ]
  && ...`, so a MISSING input skipped the guard rather than failing it, and the
  render not existing is the most common way for a render to fail.
- `script_check` passed a script citing NOTHING against an EMPTY claims.json:
  "0 distinct id(s), all found". Vacuous truth on the house's first law.
- `coherence_check` had four rows inside `if a and b:` after I had fixed the
  same hole in two others.
- `vo_soundcheck` returned True on zero rows, dropped empty audio slices from
  its own report so the DEAD verdict was unreachable, and returned 0 with
  `--json` on a take it failed without it.
- `visual_check` certified a board with no `staging` anywhere.
- `contact_sheet` exited 0 when 11 of 12 stills failed.
- `vo_qc`'s ship floor was a literal `pass` under a comment saying "only warn",
  emitting no warning, plus a `report["warning"]` string no caller ever read.
- `align_captions` warned about a 40%-wrong transcript and wrote its file anyway.
- Two ledgers did `except Exception: return <empty>` and wrote non-atomically, so
  a killed process created precisely the corruption the handler swallowed: the
  TTS budget handed back a full daily quota and `retro` reported "PASS, every
  repeat offender has an upgrade logged against it" with an unreadable ledger.

**THE SELF-TESTS DID NOT PROVE WHAT THEY CLAIMED.** `face_check` stayed GREEN
with two of its three guards neutered, because every red fixture also tripped
the change counter and the assertion was `bool(problems)`. `render_gate`'s tiny
encode fixture proved the parse row, not `MIN_BYTES`. `gen_captions_ts`'s
staleness case asserted that `str.replace` works. `tts_budget`'s day-boundary
case asserted that a date is ten characters long. And `coherence_check`'s
self-contradiction guard was DEAD for every ban this repo actually writes, and
stayed green because I had reworded the fixture to a verb that survived the
filter instead of fixing the guard.

That last one is the one to remember. **When a self-test goes red, the fixture
is the suspect only after the guard has been cleared.** Changing the fixture
until it passes is how a dead guard gets a green light and a comment saying it
works.

THE THIRD PILE, small and expensive: things that were never wired up at all.
`run_guard.py` implemented the freshness invariant correctly and had NO CALLERS
in the entire repo, while three separate opportunistic reads did exactly what it
was written to prevent. `resume_render.sh` `cd`ed to another machine's path,
failed, and exited 0 with a fake PID. Three hardcoded Alaska episode scripts
were listed in SKILL.md as the live VO tools. A protection nobody calls, and a
manifest that points at the wrong file, both read as working.

**HOW TO USE THIS.** Two questions, cheap, and they found forty defects between
them. Run the gate on `{}`. Then break the guard on purpose and check that the
self-test notices.

## A phase whose output cannot fit in its return channel fails at the last step (2026-08-02)

The first live Phase 4.4 ran for twenty-five minutes, did the work correctly,
and produced NOTHING. The director agent had `tools: Read`, so its only way out
was the final message, and the board it was asked for is nineteen shots with
eight prose fields each plus a per-shot event array. It stalled part-way through
emitting the JSON. Everything it had figured out was still right and is now
gone.

Two things make this worth an entry rather than a one-line fix.

**It fails silently and it fails LAST.** A stalled message looks exactly like a
slow one, so there is nothing to react to until the task simply disappears from
the runtime. The owner noticed it was gone before the machine did. And it burns
the entire cost of the phase before failing, which is the most expensive place
in a run to lose something.

**The production designer never hit this**, because it writes its own artifact
and has `Write`. Same brief size, same prose density, no problem. The difference
was never the work, it was the channel.

THE RULE: **if a phase produces an artifact, it WRITES the artifact.** The
return message is a receipt, not the deliverable: a verdict, the counts, and
anything that needs a ruling. Read-only is correct for critics, who return a
judgement, and wrong for any room whose output is a document.

The corollary, for the file it writes: write it ONCE and complete. A
half-written `storyboard.json` at the right path is byte-for-byte
indistinguishable from a finished one, and `build_scenes.py` will derive a scene
map from it without knowing.

## Editing an agent's frontmatter does not affect the running session (2026-08-02)

Phase 4.4 died because the director had `tools: Read` and could not write the
board it was asked for. I added `Write` to `.claude/agents/director.md`,
committed it, and relaunched. **The relaunched agent still had no Write.** It did
the whole job again, twenty-five minutes of it, and reported the same blocker.

The agent registry is read once, at session start. A frontmatter edit is
correct, it is durable, and it applies to the NEXT session, not this one. Two
identical failures for one root cause, and the second one was avoidable.

WHAT TO DO INSTEAD, when a capability is missing mid-run and the work is already
done: do not relaunch, and do not rewrite the agent's job around the gap. RESUME
it and change the CHANNEL. A resumed agent still has everything in context, so
ask for the artifact in numbered chunks, one per reply, and persist each chunk
yourself. Three round trips beat redoing the thinking, and the chunking also
happens to fix the original stall, because no single message has to carry the
whole board.

The general shape, which is worth more than the specific fact: **a config change
and a runtime change are not the same change.** Committing the config is not
deploying it. Ask what is loaded RIGHT NOW, not what the file says.

And the corollary that cost the second run: when a fix does not take, the next
step is to verify the fix took, not to assume the tool was flaky and retry. I
relaunched on the assumption the first death was a fluke. It was not, and the
agent told me so precisely and immediately both times.

## Audio is not the only input to a picture (2026-08-03)

`mux_and_verify.sh` had a staleness guard that refused a video older than its
audio, added the day before after a failed render was muxed onto a fresh voice
track. It passed a mux of a render that was three minutes out of date.

The scene file had just been fixed (a 0.9 second hole that would have rendered
black), the re-render was still running, and the mux ran against the PREVIOUS
render. Video newer than audio, which is all the guard knew how to ask, and
older than the only change that mattered.

A self-timed episode is drawn by its SCENE FILE and its generated sidecars.
Those are inputs. A render older than any of them is a render of code that no
longer exists, and it is indistinguishable from a correct one by every check
that asks about the file rather than about the cut.

THE GENERAL SHAPE: when you add a freshness guard, enumerate ALL the inputs, not
the one that burned you. A guard that covers one input reads exactly like a
guard that covers the category, and the next input to go stale is the one nobody
listed.

Two more from the same hour, both the same shape:

**A background wrapper exiting is not the job finishing.** A command launched
with `&` inside a backgrounded shell notifies on the WRAPPER's exit, which is
immediate. I read "completed, exit 0" and muxed against a render that was 191
frames into 1748. Wait on the ARTIFACT, and specifically on the artifact being
newer than the thing that changed.

**A contact sheet samples; it does not cover.** Twelve cells across 58 seconds
is one frame every 4.8s, and the black hole was 0.9s wide. It was invisible to
the only thing in this machine that looks at the episode. Sampling finds what is
wrong with the frames it lands on, and a gate that reads the SOURCE is what
finds a hole narrower than the sampling interval. That is why `retime_check.py`
exists and why it runs on the scene file rather than on stills.
