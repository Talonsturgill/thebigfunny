#!/usr/bin/env python3
"""tts_budget.py — the run cannot spend TTS credits it does not have.

WHY THIS EXISTS
On 2026-08-02 a single session exhausted the entire daily TTS quota (100 calls)
iterating one episode, and the run only found out when the API started returning
429. Nothing in the machine knew how many calls it had made, nothing warned as it
approached the wall, and nothing refused to start a pass it could not finish. So
the failure was silent right up until it was total, and the last thing it cost
was the ability to render the very cut the iteration had produced.

FOUR CAUSES, and this file is aimed at all of them:

1. SIX RE-SYNTHESIS PASSES. The take cache keys on the whole director's brief,
   correctly, because changing the brief changes the audio. But that means one
   word edited in a brief silently re-rolls EVERY line in the episode. Nothing
   said so before it happened. `preview()` now prices a pass before it runs.

2. A DIAGNOSTIC LOOP THAT DID NOT CACHE. A probe written to find one blocked
   line called synth() directly instead of take(), paying for six takes and
   keeping none. Fixed at the source (`vo_cast.py --probe`), and this file makes
   the waste visible either way, because every call is counted.

3. NO BUDGET AWARENESS ANYWHERE. Now there is a ledger, a cap, and a refusal.

4. SYNTHESIZING BEFORE THE SCRIPT WAS SETTLED. The script gates and the funny
   critic are FREE. Audio is the only expensive step in this pipeline, and it was
   being spent on drafts. See `enforce_order()`.

THE RULE THIS ENCODES
  Iterate the SCRIPT against the free gates. Synthesize ONCE, at the end.

  python3 scripts/tts_budget.py            # what has today cost so far
  python3 scripts/tts_budget.py --self-test
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(REPO, "ledger", "tts_spend.json")

# The daily ceiling observed on this account. Not a guess: it is the number in
# the 429 the run actually hit, on a PAID project, not the free tier.
#
# Google does not publish per-day limits for TTS models in the rate-limit docs
# (they list batch token limits only), so the live number lives at
# https://aistudio.google.com/rate-limit and nowhere else. Preview TTS models are
# capped far tighter than the stable text models. The next lever is Tier 2,
# which requires $100 paid AND 3 days elapsed, so it cannot be bought same-day.
# PER-MODEL, because that is how the provider counts. The first cut of this file
# used one global daily number, which is wrong in both directions: it would
# refuse a model with budget left because a different model was exhausted, and it
# would authorise calls on a 50/day model using a 100/day allowance. Confirmed
# from the account's own rate-limit dashboard 2026-08-02.
MODEL_CAPS = {
    "gemini-3.1-flash-tts-preview": {"rpd": 100, "rpm": 10},
    "gemini-2.5-flash-preview-tts": {"rpd": 100, "rpm": 10},
    "gemini-2.5-pro-preview-tts":   {"rpd": 50,  "rpm": 10},
}
# An unknown model is assumed to be the STRICTEST thing on the shelf, never the
# most generous, so a new model id cannot quietly buy itself a bigger allowance.
DEFAULT_CAP = {"rpd": 50, "rpm": 10}

HARD_CAP = int(os.environ.get("BIGFUNNY_TTS_DAILY_CAP", "100"))
# Stop here instead, so a run always keeps enough headroom to finish ONE clean
# synthesis of a whole episode after whatever it has already spent. An episode
# is ~13 to 20 lines; 25 covers it with room for a retry or two.
RESERVE = int(os.environ.get("BIGFUNNY_TTS_RESERVE", "25"))
SOFT_CAP = HARD_CAP - RESERVE

# One pass over a whole episode is fine. Anything much past that in a single
# command means something is re-rolling the world, which is what happened.
WARN_PER_RUN = 22


# WHICH DAY IS IT, ACCORDING TO THE PROVIDER?
#
# This ledger originally keyed on the UTC date, which is a guess dressed as a
# fact. Google does not document the reset boundary for TTS per-day quotas, and
# if it resets at midnight PACIFIC then between 00:00 and 08:00 UTC this file
# would call it a new day, hand out a full budget, and walk straight into the
# 429 it exists to prevent. That is the failure mode this whole module was built
# for, reintroduced one layer down.
#
# So the default is the CONSERVATIVE one: assume the later boundary (Pacific),
# which holds the previous day's count longer. If the real reset is UTC, the only
# cost is being cautious for eight hours; if it is Pacific, being wrong the other
# way costs a dead run. Set BIGFUNNY_TTS_RESET_UTC_OFFSET=0 if you confirm UTC.
RESET_UTC_OFFSET = int(os.environ.get("BIGFUNNY_TTS_RESET_UTC_OFFSET", "-8"))


def _today():
    return (datetime.now(timezone.utc)
            + timedelta(hours=RESET_UTC_OFFSET)).strftime("%Y-%m-%d")


def _load():
    """The ledger, or a fresh one IF AND ONLY IF the file is genuinely absent.

    2026-08-02, repo-wide review: this was `except Exception: return <empty>`,
    and `record()` below writes a non-atomic json.dump straight to the final
    path. So a process killed mid-write produces exactly the corruption this
    handler swallowed, and the next run reads a truncated ledger, gets a fresh
    100-call allowance, and spends it. Verified: spent=95 remaining=0 REFUSED,
    truncate the file, spent=0 remaining=75 ALLOWED. The whole budget came back.

    ABSENT means never written and is fine. PRESENT AND UNPARSEABLE means the
    count is lost, and a lost count is not a zero count.
    """
    if not os.path.exists(LEDGER):
        return _blank()
    try:
        with open(LEDGER) as fh:
            doc = json.load(fh)
    except Exception as e:
        raise LedgerCorrupt(
            f"{LEDGER} exists and cannot be parsed ({e}). This is what a process "
            f"killed mid-write leaves behind, and treating it as an empty ledger "
            f"hands this run the whole daily quota a second time. Restore it from "
            f"git, or delete it deliberately if today's count really is lost."
        ) from e
    if not isinstance(doc, dict) or not isinstance(doc.get("days"), dict):
        raise LedgerCorrupt(f"{LEDGER} parsed but has no `days` object.")
    return doc


class LedgerCorrupt(RuntimeError):
    """Present and unreadable. Never confused with absent."""


def _blank():
    return {
            "_spec": {
                "purpose": "TTS call ledger. Every real API call is counted here so a "
                           "run can be refused BEFORE it hits a 429 and loses the "
                           "episode it was in the middle of.",
                "written_by": "scripts/tts_budget.py, called from vo_gemini.synth",
                "note": "Cached takes cost nothing and are never counted.",
            },
            "days": {},
        }


def caps(model):
    c = MODEL_CAPS.get(model, DEFAULT_CAP)
    if model is None:
        c = {"rpd": HARD_CAP, "rpm": 10}
    return c


def spent(day=None, model=None):
    """Calls today. Per MODEL when one is named, which is how the provider counts."""
    rec = _load()["days"].get(day or _today(), {})
    if model is None:
        return int(rec.get("calls", 0))
    return int(rec.get("by_model", {}).get(model, 0))


def reserve_for(model):
    """Hold back enough to synthesize one finished episode on THIS model."""
    return min(RESERVE, max(0, caps(model)["rpd"] // 3))


def remaining(day=None, model=None):
    if model is None:
        return max(0, SOFT_CAP - spent(day))
    working = caps(model)["rpd"] - reserve_for(model)
    return max(0, working - spent(day, model))


def best_model_with_budget(preferred, day=None):
    """The preferred model if it can pay, else any that can, else None.

    Exists because on 2026-08-02 the 3.1 preview was exhausted at 105/100 while
    2.5 Flash still had 54 calls, and the run stopped anyway because nothing knew
    the limits were per model."""
    if remaining(day, preferred) > 0:
        return preferred
    for m in sorted(MODEL_CAPS, key=lambda k: -remaining(day, k)):
        if remaining(day, m) > 0:
            return m
    return None


# --- RPM ------------------------------------------------------------------
# Every TTS model here is 10 requests per MINUTE, and the dashboard showed the
# 3.1 preview at 13/10, so this run was over the per-minute limit as well as the
# daily one. Nothing in the code spaced its calls. A per-minute 429 looks exactly
# like an exhausted quota and is not one, which is the worst kind of error to
# read at 2am.
_recent = []


def throttle(model, sleep=True):
    """Block until another call would be within the per-minute limit."""
    import time
    global _recent
    rpm = caps(model)["rpm"]
    now = time.monotonic()
    _recent = [x for x in _recent if now - x < 60.0]
    if len(_recent) >= rpm:
        wait = 60.0 - (now - _recent[0]) + 0.25
        if sleep and wait > 0:
            print(f"  tts: {len(_recent)} calls in the last minute (limit {rpm}), "
                  f"waiting {wait:.0f}s", flush=True)
            time.sleep(wait)
            now = time.monotonic()
            _recent = [x for x in _recent if now - x < 60.0]
        # THE THROTTLED CALL IS STILL A CALL. This returned without appending,
        # so every call that had to wait was invisible to the limiter that made
        # it wait, and the window under-counted by one each time. The real rate
        # drifts above the limit this function exists to hold.
        _recent.append(now)
        return wait
    _recent.append(now)
    return 0.0


def record(model="unknown", n=1, day=None):
    """Count real API calls. Called AFTER a call succeeds or is billed."""
    d = day or _today()
    doc = _load()
    rec = doc["days"].setdefault(d, {"calls": 0, "by_model": {}})
    rec["calls"] = int(rec.get("calls", 0)) + n
    rec["by_model"][model] = int(rec["by_model"].get(model, 0)) + n
    # ATOMIC. A torn write here is the corruption _load refuses to read, and it
    # is self-inflicted: the ledger is rewritten after every single billed call,
    # which is the most likely moment in the run for the process to be killed.
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    tmp = LEDGER + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(doc, fh, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, LEDGER)
    return rec["calls"]


class BudgetExceeded(RuntimeError):
    pass


def check(n=1, day=None, model=None, ship=False):
    """Raise BEFORE spending if this call would cross the reserve line.

    `ship=True` RELEASES THE RESERVE, and that is what the reserve is for.

    2026-08-03: the reserve is described in this module as "held back so a
    finished episode is always renderable", and there was no way to spend it. A
    reserve that can never be released is not a reserve, it is a lower cap with a
    reassuring docstring, and it would have blocked the one synthesis it exists
    to protect: script locked, every gate green, board done, picture verified on
    a contact sheet, 17 lines to buy.

    It is deliberately not a flag on the daily cap. The HARD_CAP still holds, so
    releasing the reserve can never spend past the account's real quota; it only
    lets a finished episode reach into the buffer that was set aside for exactly
    this call. Iteration keeps the old wall.
    """
    r = caps(model)["rpd"] - spent(day, model) if (ship and model) else remaining(day, model)
    if ship and not model:
        r = HARD_CAP - spent(day)
    if n > r:
        raise BudgetExceeded(
            f"TTS budget: {model or 'global'} would go to "
            f"{spent(day, model) + n} calls today.\n"
            f"  cap {caps(model)['rpd']}/day, {reserve_for(model)} held back so a "
            f"finished episode is always renderable.\n"
            f"  spent on this model: {spent(day, model)}   remaining: {r}\n"
            f"  ship mode: {'ON, reserve released' if ship else 'off'}\n"
            f"  This is a REFUSAL, not an outage. Iterate the script against the "
            f"free gates (script_check, face_check, the funny critic) and "
            f"synthesize once. Raise BIGFUNNY_TTS_DAILY_CAP only if the account "
            f"quota actually went up.")


def preview(uncached, label="synthesis", model=None, ship=False):
    """Price a pass BEFORE it runs. Returns (ok, message).

    Takes a MODEL. The first cut asked the global counter, which is the very bug
    the per-model rewrite existed to kill: it refused a pass on a model with
    plenty of budget because a DIFFERENT model was exhausted."""
    # SHIP releases the reserve here too. preview() and check() disagreeing about
    # the budget is the same class of defect as two gates enforcing one rule:
    # the pass would be priced as refused and then permitted, or the reverse.
    if ship:
        r = (caps(model)["rpd"] - spent(model=model)) if model else (HARD_CAP - spent())
        cap = caps(model)["rpd"] if model else HARD_CAP
    else:
        r = remaining(model=model)
        cap = caps(model)["rpd"] - reserve_for(model) if model else SOFT_CAP
    lines = [f"TTS budget: {label} needs {uncached} call(s) on "
             f"{model or 'the default model'}; {spent(model=model)} spent on it today, "
             f"{r} left of a {cap} working cap."]
    if uncached > WARN_PER_RUN:
        lines.append(
            f"  WARNING: {uncached} uncached lines is more than one episode's worth "
            f"({WARN_PER_RUN}). A director's brief probably changed, which busts the "
            f"cache for EVERY line. That is what exhausted the quota on 2026-08-02.")
    if uncached > r:
        lines.append(f"  REFUSED: not enough budget. See the rule in scripts/tts_budget.py.")
        return False, "\n".join(lines)
    return True, "\n".join(lines)


def enforce_order(script_path=None):
    """Audio is the only expensive step, so it goes LAST.

    Returns a list of problems; empty means the free gates are clean and it is
    safe to spend. Deliberately shells out rather than importing, so a gate can
    never be half-run by an import side effect."""
    import subprocess
    probs = []
    for name, cmd in (("script_check", [sys.executable, os.path.join(REPO, "scripts", "script_check.py")]),
                      ("face_check", [sys.executable, os.path.join(REPO, "scripts", "face_check.py")])):
        if script_path:
            cmd = cmd + ([script_path] if name == "face_check" else ["--script", script_path])
        try:
            if subprocess.run(cmd, capture_output=True, cwd=REPO).returncode != 0:
                probs.append(f"{name} is RED. Fix the script before paying for audio.")
        except Exception as e:
            probs.append(f"{name} could not run: {e}")
    return probs


def self_test():
    import tempfile
    global LEDGER
    ok = True
    keep = LEDGER
    with tempfile.TemporaryDirectory() as d:
        LEDGER = os.path.join(d, "spend.json")
        day = "2026-01-01"

        checks = [("starts at zero", spent(day) == 0)]
        record("m", 10, day)
        checks.append(("counts calls", spent(day) == 10))
        checks.append(("remaining subtracts spend", remaining(day) == SOFT_CAP - 10))

        # RED: refuse before the wall, not at it.
        try:
            check(SOFT_CAP, day)
            checks.append(("REFUSES a pass it cannot finish", False))
        except BudgetExceeded:
            checks.append(("REFUSES a pass it cannot finish", True))

        try:
            check(1, day)
            checks.append(("allows a call it can afford", True))
        except BudgetExceeded:
            checks.append(("allows a call it can afford", False))

        # The reserve is the point: it exists so a finished episode is always
        # renderable even after a day of iterating.
        checks.append(("holds back a whole episode's worth", HARD_CAP - SOFT_CAP >= 20))

        okp, msg = preview(3, "test")
        checks.append(("prices a small pass and allows it", okp))
        # 60 would have FIT in the remaining budget, so refusing it would have
        # been the bug. Use a number that genuinely cannot be afforded.
        okp2, msg2 = preview(200, "test")
        checks.append(("warns when a pass re-rolls the world", "WARNING" in msg2))
        checks.append(("refuses a pass bigger than the budget", not okp2))
        okp3, _ = preview(30, "test")
        checks.append(("allows a pass that fits, even if it warns", okp3))

        # The day boundary must follow the PROVIDER, not UTC convenience.
        checks.append(("day boundary is provider-relative, not bare UTC",
                       RESET_UTC_OFFSET != 0 or
                       os.environ.get("BIGFUNNY_TTS_RESET_UTC_OFFSET") == "0"))
        # This asserted `len(_today()) == 10` and computed utc_day without ever
        # using it, so it tested that a date is ten characters long and NOT what
        # its own name claims. Shift the offset far enough that the two dates
        # must differ, and check that they do.
        import datetime as _dt
        keep_off = globals()["RESET_UTC_OFFSET"]
        try:
            now = _dt.datetime.now(_dt.timezone.utc)
            globals()["RESET_UTC_OFFSET"] = -(now.hour + 1)
            utc_day = now.strftime("%Y-%m-%d")
            checks.append(("and it can differ from the UTC date", _today() != utc_day))
        finally:
            globals()["RESET_UTC_OFFSET"] = keep_off

        # The reserve must be RELEASABLE, or it is a lower cap wearing a
        # reassuring docstring. Spent to the reserve line, a ship synthesis gets
        # through and an iteration pass does not.
        globals()["_recent"] = []
        m2 = "gemini-2.5-flash-preview-tts"
        day2 = "2026-01-02"
        record(m2, caps(m2)["rpd"] - reserve_for(m2), day2)      # exactly at the line
        try:
            check(3, day=day2, model=m2)
            checks.append(("the reserve line refuses an ITERATION pass", False))
        except BudgetExceeded:
            checks.append(("the reserve line refuses an ITERATION pass", True))
        try:
            check(3, day=day2, model=m2, ship=True)
            checks.append(("...and RELEASES for a ship synthesis", True))
        except BudgetExceeded:
            checks.append(("...and RELEASES for a ship synthesis", False))
        # But never past the account's real cap, even in ship mode.
        try:
            check(reserve_for(m2) + 5, day=day2, model=m2, ship=True)
            checks.append(("ship mode still stops at the HARD cap", False))
        except BudgetExceeded:
            checks.append(("ship mode still stops at the HARD cap", True))

        # RED on purpose: a ledger that is PRESENT and unreadable must never read
        # as an empty one. A torn write is what a killed process leaves behind,
        # and swallowing it hands the run a second full daily quota.
        record("m", SOFT_CAP - 5, day)
        before = spent(day)
        open(LEDGER, "w").write('{"days": {"2026-01-01": {"calls": 9')  # truncated
        try:
            spent(day)
            checks.append(("refuses a CORRUPT ledger instead of resetting to zero", False))
        except LedgerCorrupt:
            checks.append(("refuses a CORRUPT ledger instead of resetting to zero", True))

        # And the other half: absent is still fine, because it is the first run.
        os.remove(LEDGER)
        checks.append(("an ABSENT ledger is still an empty one", spent(day) == 0))
        checks.append(("the corrupt case was really at the wall", before >= SOFT_CAP - 5))

        # The throttled call is still a call. Before this, throttle() returned
        # without recording the call it had just made room for, so the window
        # under-counted by one every time it fired.
        globals()["_recent"] = []
        for _ in range(caps("gemini-2.5-flash-preview-tts")["rpm"]):
            throttle("gemini-2.5-flash-preview-tts", sleep=False)
        n_before = len(_recent)
        throttle("gemini-2.5-flash-preview-tts", sleep=False)   # this one waits
        checks.append(("a THROTTLED call still counts against the window",
                       len(_recent) == n_before + 1))

        for name, good in checks:
            print(f"  {'ok  ' if good else 'FAIL'} {name}")
            ok &= bool(good)
    LEDGER = keep
    print("\nself-test: " + ("both directions correct, as designed" if ok else "THE GATE IS WRONG"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    doc = _load()
    print(f"TTS spend, working cap {SOFT_CAP} of {HARD_CAP} ({RESERVE} held back)")
    for day in sorted(doc["days"])[-7:]:
        r = doc["days"][day]
        by = ", ".join(f"{k}={v}" for k, v in sorted(r.get("by_model", {}).items()))
        print(f"  {day}  {r['calls']:>4} call(s)   {by}")
    print(f"\ntoday: {spent()} spent, {remaining()} remaining")
    return 0


if __name__ == "__main__":
    sys.exit(main())
