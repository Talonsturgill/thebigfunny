"""Gemini TTS backend for the Dispatch VO — a PRESET-voice option (not a clone).

Quick-start narrator voice while the owner's cloned voice (Chatterbox / later
ElevenLabs) is set up separately. Drop-in for vo_qc.synth_qc: returns
(float32 mono @ 44100, report). No speaker-similarity gate applies because this
is a prebuilt Google voice, not the owner's voice — the report says so plainly.

SETUP (do this once, in the routine env at claude.ai/code/routines):
  1. Get a Gemini API key: https://aistudio.google.com/apikey
  2. Set env var  GEMINI_API_KEY = <your key>   (GOOGLE_API_KEY also accepted)
  3. Set env var  DISPATCH_VOICE = gemini        (flips the whole pipeline to this backend)
  4. Make sure the routine's network policy allows  generativelanguage.googleapis.com
Optional env:
  DISPATCH_GEMINI_TTS_MODEL   default gemini-2.5-flash-preview-tts
  DISPATCH_GEMINI_VOICE       default Charon  (calm, informative; 30 voices, see docs)
  DISPATCH_GEMINI_STYLE       optional style instruction, e.g. "in a calm, factual news tone"

Audition:  python vo_gemini.py "One or two full sentences." out.wav
"""
import os, sys, json, base64, urllib.request, urllib.error
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from vo_backends import normalize_for_tts, SR  # SR = 44100; shared number/text normalizer

# THE MODEL. gemini-3.1-flash-tts-preview, chosen 2026-08-02 by owner A/B on real
# takes of real lines. It is the newest TTS model, supports single and multi
# speaker, and was the only one whose tagged takes the owner described as having
# "real fluctuation". Do not quietly downgrade this to a 2.5 preview.
MODEL = os.environ.get("DISPATCH_GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")

# Tags Google documents as PERFORMED rather than spoken. Anything outside this
# set risks being read aloud as a word, which the docs warn about explicitly.
KNOWN_TAGS = {
    "sarcasm", "sigh", "sighs", "laughs", "laughing", "giggles", "gasp", "uhm",
    "whispers", "whispering", "shouting", "excited", "amazed", "curious",
    "serious", "tired", "panicked", "trembling", "crying", "mischievously",
    "scoffs", "flat", "extremely fast", "short pause", "medium pause", "long pause",
}

# BANNED. [robotic] was tested on 2026-08-02 and the owner's verdict was
# "a robot sound and horrid". It is the one tag that makes a prebuilt voice sound
# synthetic on purpose, which is the exact defect this show was just fixing.
BANNED_TAGS = {"robotic"}
VOICE = os.environ.get("DISPATCH_GEMINI_VOICE", "Charon")
STYLE = os.environ.get("DISPATCH_GEMINI_STYLE", "").strip()
PCM_RATE = 24000  # Gemini TTS returns signed 16-bit PCM, mono, 24 kHz


def _api_key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        raise RuntimeError(
            "No GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment. Set it in the routine env "
            "at claude.ai/code/routines, then set DISPATCH_VOICE=gemini.")
    return k


def _resample_to_sr(pcm_i16):
    """int16 PCM @ 24kHz -> float32 mono @ 44100."""
    a = (pcm_i16.astype(np.float32)) / 32768.0
    if PCM_RATE != SR:
        from math import gcd
        from scipy.signal import resample_poly
        g = gcd(PCM_RATE, SR)
        a = resample_poly(a, SR // g, PCM_RATE // g).astype(np.float32)
    return a


def _check_tags(text):
    """Refuse a banned tag, warn on an undocumented one.

    Google warns that a tag it does not recognise may be VOCALISED rather than
    performed, so an invented tag does not fail loudly, it quietly says the word
    "grumpily" in the middle of a line and ships."""
    import re as _re
    for raw in _re.findall(r"\[([^\]]{1,20})\]", text):
        t = raw.strip().lower()
        if t in BANNED_TAGS:
            raise ValueError(
                f"vo_gemini: [{t}] is banned. Tested 2026-08-02 and the verdict was "
                f"'a robot sound and horrid'. It makes a prebuilt voice sound "
                f"synthetic, which is the defect this show fixed.")
        if t not in KNOWN_TAGS:
            print(f"    warn: [{t}] is not a documented tag; Gemini may SPEAK it "
                  f"aloud rather than perform it. Verify the take.")


# Set once a cooled 429 retry has PROVEN the daily wall, so the remaining
# lines of an episode fail fast instead of each paying its own 65s.
_HARD_WALL = False


def synth(text, voice=None, style=None, direction=None):
    """Synthesize one or two whole sentences -> float32 mono @ 44100.

    voice/style override the module defaults PER CALL. That is what lets one
    episode carry three different characters: The Big Funny has no narrator, and
    a single-voice read collapses Ray, Dee and the Institution into a podcast.
    See scripts/vo_cast.py for the casting table."""
    spoken = normalize_for_tts(text)
    v = voice or VOICE
    st = style if style is not None else STYLE

    # BANNED TAGS ARE CHECKED ON EVERY PATH, not only the directed one.
    #
    # 2026-08-02, repo-wide review: this call lived inside `if direction:`, and
    # both synth_qc() and the __main__ audition call synth() with no direction.
    # So the one tag this module raises on by design went unchecked on exactly
    # the calls that paste markup into the bare `Say {style}: {text}` prompt,
    # which is the prompt shape Google's docs warn will be read aloud.
    _check_tags(spoken)

    # THE PROMPT. Google's own advanced-prompting format: an audio profile, the
    # scene, director's notes broken into style/pace/accent, and a clearly
    # labelled transcript. This replaced a flat "Say <style>: <text>", which the
    # owner correctly identified as leaving most of the API on the table: a bare
    # style string gets a READING, the structured brief gets a PERFORMANCE.
    #
    # The preamble is not decoration. The docs warn that a vague prompt fails to
    # trigger the speech classifier and the model then reads your director's
    # notes ALOUD as dialogue. Naming the transcript boundary is what prevents
    # that, and scripts/vo_soundcheck.py's overrun check is the backstop.
    if direction:
        prompt = (
            "Perform this line of scripted audio drama. Read ALOUD only the text "
            "under the heading TRANSCRIPT. Everything above that heading is "
            "direction for you and must NOT be spoken.\n\n"
            f"# AUDIO PROFILE: {direction.get('name', 'Narrator')}\n"
            f"## THE SCENE\n{direction.get('scene', '')}\n"
            f"### DIRECTOR'S NOTES\n"
            f"Style: {direction.get('style', st or '')}\n"
            f"Pace: {direction.get('pace', '')}\n"
            f"Accent: {direction.get('accent', 'General American.')}\n"
            f"#### TRANSCRIPT\n{spoken}"
        )
    else:
        prompt = f"Say {st}: {spoken}" if st else spoken
    # THE ONE PLACE A CALL IS BILLED, so it is the one place the budget is
    # enforced. Cached takes never reach here and cost nothing.
    # sys.path is extended ONCE per process, not once per line. This ran inside
    # synth() and grew the path unboundedly across a run.
    _scripts = os.path.abspath(os.path.join(HERE, "..", "..", "..", "scripts"))
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)
    try:
        import tts_budget
    except ImportError:
        tts_budget = None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": v}}},
        },
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers={
        "Content-Type": "application/json",
        "x-goog-api-key": _api_key(),
    })
    # honor the container's proxy CA bundle when present (agent proxy), else default TLS
    ca = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    import ssl, time
    ctx = ssl.create_default_context(cafile=ca) if os.path.exists(ca) else ssl.create_default_context()
    # retry on 429 (rate limit) / 503 (overloaded) with exponential backoff — the free tier
    # throttles the preview TTS model hard, so short spacing often clears a transient 429.
    # EVERY ATTEMPT IS A BILLED CALL, so every attempt is authorised and throttled
    # on its own.
    #
    # 2026-08-02, repo-wide review: check(1) and throttle() ran ONCE above the
    # loop and record() ran INSIDE it, so one line could issue five requests
    # having authorised one. vo_cast.take() wraps this in its own four-attempt
    # loop for empty responses, which made the worst case twenty billed calls
    # against a budget that had approved one.
    #
    # 429 gets exactly ONE cooled retry, not four (see the handler below): the
    # per-minute limiter and the daily wall both surface as 429 and only a wait
    # longer than a minute tells them apart. The per-minute limiter is also
    # throttle()'s job and it runs before every attempt.
    delays = [0, 4, 10, 20, 35]
    last = None
    for d in delays:
        if d:
            time.sleep(d)
        if tts_budget is not None:
            # SHIP mode releases the reserve, which is what the reserve is for:
            # a finished episode, script locked and every gate green. Set by
            # vo_cast --ship. Iteration never sees it.
            tts_budget.check(1, model=MODEL,
                             ship=os.environ.get("BIGFUNNY_TTS_SHIP") == "1")
            tts_budget.throttle(MODEL)
        try:
            if tts_budget is not None:
                tts_budget.record(MODEL, 1)     # billed on the REQUEST, not the result
            with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
                resp = json.loads(r.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")[:400]
            last = f"HTTP {e.code}: {body}"
            if e.code == 429:
                # 2026-08-03: THIS USED TO RAISE IMMEDIATELY, saying "a 429 is the
                # quota wall, not a transient error". That is wrong, and being
                # wrong about it cost a run the better part of an hour.
                #
                # A 429 on this model is EITHER the per-minute request limit or
                # the daily wall, and the message body does not reliably say
                # which: the one that stopped case 0003's retime read
                # `limit: 10`, which is the PER-MINUTE limit. The run believed
                # its own error text, abandoned the retime, and only found out
                # by accident an hour later that the quota had replenished the
                # whole time.
                #
                # The two cases are distinguishable by exactly one thing: wait
                # longer than a minute and try once more. So do that ONCE, and
                # remember the answer for the rest of the process, because if it
                # IS the daily wall then paying 65s per line across seventeen
                # lines is twenty minutes spent proving the same sentence.
                global _HARD_WALL
                if _HARD_WALL:
                    raise RuntimeError(
                        f"Gemini TTS {last}\n"
                        f"  Daily wall, already proven this process: a cooled "
                        f"retry got a second 429.")
                _HARD_WALL = True
                time.sleep(65)
                try:
                    if tts_budget is not None:
                        tts_budget.record(MODEL, 1)
                    with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
                        resp = json.loads(r.read().decode("utf-8"))
                    _HARD_WALL = False      # it was the per-minute limiter
                    break
                except urllib.error.HTTPError as e2:
                    if e2.code != 429:
                        raise RuntimeError(f"Gemini TTS HTTP {e2.code} after cooling")
                    raise RuntimeError(
                        f"Gemini TTS {last}\n"
                        f"  Still 429 after a 65s cool-down, so this is the DAILY "
                        f"wall and not the per-minute limiter. Takes already "
                        f"synthesized are cached on disk and cost nothing to reuse.")
            if e.code in (500, 503):
                continue
            raise RuntimeError(f"Gemini TTS {last}")
    else:
        raise RuntimeError(f"Gemini TTS still failing after retries. Last: {last}. "
                           f"A persistent 429 means the DAILY TTS quota for this model is exhausted.\n"
                           f"  Do NOT assume this is the free tier. The rate-limit docs do not publish\n"
                           f"  per-day limits for TTS models at all, and a PAID Tier 1 project hit a\n"
                           f"  100/day wall on this preview model on 2026-08-02. Preview TTS is capped\n"
                           f"  far tighter than the stable text models.\n"
                           f"  Real limits: https://aistudio.google.com/rate-limit\n"
                           f"  Tier 2 (the next lever) needs $100 paid AND 3 days elapsed, so it is\n"
                           f"  time-gated as well as spend-gated and cannot be bought same-day.")
    try:
        b64 = resp["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
    except (KeyError, IndexError):
        block = (resp.get("promptFeedback") or {}).get("blockReason")
        if block:
            # A SAFETY BLOCK is not a transient failure and retrying is pointless.
            # Observed 2026-08-02 on the single word "Invalid.", which is not
            # remotely prohibited: a one-word prompt gives the classifier nothing
            # to anchor on, and this cast's director brief mentions swearing, so
            # short lines can trip it. Name the line and say what to do, because
            # the raw JSON sent the last run hunting through the whole script.
            raise RuntimeError(
                f"Gemini TTS refused this line ({block}). It is a CONTENT BLOCK, not an "
                f"outage, so retrying will not help. Very short lines trip this most "
                f"often because the classifier has no context. Lengthen the line or "
                f"rephrase it, then re-run.\n  line: {spoken!r}")
        raise RuntimeError(f"Gemini TTS: no audio in response: {json.dumps(resp)[:500]}")
    pcm = np.frombuffer(base64.b64decode(b64), dtype="<i2")
    return _resample_to_sr(pcm)


def synth_qc(text, **_ignored):
    """Drop-in for vo_qc.synth_qc. Returns (audio, report). No similarity gate:
    this is a prebuilt Google voice, not the owner's clone."""
    audio = synth(text)
    report = {
        "similarity": None, "wer": 0.0, "attempts": 1,
        "backend": "gemini-tts", "model": MODEL, "voice": VOICE,
        "warning": "PRESET Gemini voice (not the owner's cloned voice) — no speaker-similarity gate applies.",
    }
    return audio, report


def backend_report():
    return {"backend": "gemini-tts", "voice": f"{MODEL}/{VOICE}",
            "license": "Google Gemini API (preset voice; per-use billing)"}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python vo_gemini.py \"text to speak\" out.wav", file=sys.stderr)
        sys.exit(2)
    from scipy.io import wavfile
    a = synth(sys.argv[1])
    wavfile.write(sys.argv[2], SR, (np.clip(a, -1, 1) * 32767).astype(np.int16))
    print(f"wrote {sys.argv[2]}  {len(a)/SR:.2f}s  model={MODEL} voice={VOICE}")
