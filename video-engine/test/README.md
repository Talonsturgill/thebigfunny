# Engine unit tests

Plain node, no framework, no dependency. `node test/<file>.mjs`, exit 0 or 1.

These exist because the two bugs they caught were both invisible to `tsc` and
would have been invisible in a render too:

- **`pose_blend.test.mjs`** caught the gesture resolver advancing past a key the
  instant its time arrived, so the blend TO that pose never happened and every
  gesture SNAPPED. A snapped gesture in a 30fps render is one frame; nobody would
  have seen it in a still and it would have shipped as "the arms are a bit
  janky". It also caught two wrong expectations of my own, and in both cases the
  code was right and the fixture was wrong, which is the order this repo checks
  them in.
- **`resample.test.mjs`** proves the arc-length resampler keeps endpoints exact,
  spaces by distance rather than index (index-lerping slides the elbow ALONG the
  arm as it blends, so a joint stops being a joint), and does not divide by zero
  on a degenerate polyline.

- **`mannerisms.test.mjs`** proves the two acting helpers build sane tracks
  from real cue shapes: a character faces out on their OWN lines and turns
  toward the speaker on everyone else's, every turn ANTICIPATES its line rather
  than lagging it, a line too short to read as a gesture is skipped, and every
  gesture releases back to rest.

Run all three:

```
node test/resample.test.mjs && node test/pose_blend.test.mjs && node test/mannerisms.test.mjs
```
