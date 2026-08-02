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
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LEDGER = os.path.join(REPO, "ledger", "tts_spend.json")

# The provider's real daily ceiling for the preview TTS model. Not a guess: it
# is the number in the 429 the run actually hit.
HARD_CAP = int(os.environ.get("BIGFUNNY_TTS_DAILY_CAP", "100"))
# Stop here instead, so a run always keeps enough headroom to finish ONE clean
# synthesis of a whole episode after whatever it has already spent. An episode
# is ~13 to 20 lines; 25 covers it with room for a retry or two.
RESERVE = int(os.environ.get("BIGFUNNY_TTS_RESERVE", "25"))
SOFT_CAP = HARD_CAP - RESERVE

# One pass over a whole episode is fine. Anything much past that in a single
# command means something is re-rolling the world, which is what happened.
WARN_PER_RUN = 22


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load():
    try:
        return json.load(open(LEDGER))
    except Exception:
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


def spent(day=None):
    return int(_load()["days"].get(day or _today(), {}).get("calls", 0))


def remaining(day=None):
    return max(0, SOFT_CAP - spent(day))


def record(model="unknown", n=1, day=None):
    """Count real API calls. Called AFTER a call succeeds or is billed."""
    d = day or _today()
    doc = _load()
    rec = doc["days"].setdefault(d, {"calls": 0, "by_model": {}})
    rec["calls"] = int(rec.get("calls", 0)) + n
    rec["by_model"][model] = int(rec["by_model"].get(model, 0)) + n
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    json.dump(doc, open(LEDGER, "w"), indent=2)
    open(LEDGER, "a").write("\n")
    return rec["calls"]


class BudgetExceeded(RuntimeError):
    pass


def check(n=1, day=None):
    """Raise BEFORE spending if this call would cross the reserve line."""
    r = remaining(day)
    if n > r:
        raise BudgetExceeded(
            f"TTS budget: this would be call {spent(day) + n} of a {SOFT_CAP} "
            f"working cap ({HARD_CAP} hard, {RESERVE} held back so a finished "
            f"episode can always be synthesized).\n"
            f"  spent today: {spent(day)}   remaining: {r}\n"
            f"  This is a REFUSAL, not an outage. Iterate the script against the "
            f"free gates (script_check, face_check, the funny critic) and "
            f"synthesize once. Raise BIGFUNNY_TTS_DAILY_CAP only if the account "
            f"quota actually went up.")


def preview(uncached, label="synthesis"):
    """Price a pass BEFORE it runs. Returns (ok, message)."""
    r = remaining()
    lines = [f"TTS budget: {label} needs {uncached} call(s); {spent()} spent today, "
             f"{r} left of a {SOFT_CAP} working cap."]
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
