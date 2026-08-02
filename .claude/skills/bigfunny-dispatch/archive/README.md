# archive/ — NOT the pipeline. Do not run these.

Three episode scripts ported from `alaska-ai-weekly`, kept because the prompt
construction and the mixing arithmetic in them were paid for and are worth
reading, and deleted from the skill manifest because they were listed there as
the live tools.

What they actually are, as of 2026-08-02:

- `build_vo.py` — 22 hardcoded caribou-counting phrases, no CLI, writes into
  this committed skill directory rather than `out/dispatch/`.
- `audio_build.py` — 5 hardcoded beluga sentences, and it mixes no music and no
  sfx despite the manifest line that said "Mix narration with music and sfx".
- `vo60.py` — 9 hardcoded permafrost sentences.

`audio_build.py` and `vo60.py` also force
`SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`, which overrides the agent
proxy's CA bundle that this environment requires.

A run following the old manifest table would have produced an Alaska caribou VO
for a national story and been confused about why. The live path is
`scripts/vo_cast.py`, which casts Ray, Dee and the Institution to three
different voices, caches takes on disk and lays the timeline out from measured
durations.

Same rule as the rest of the ported library: nothing is deleted, and nothing
place-locked is the default.
