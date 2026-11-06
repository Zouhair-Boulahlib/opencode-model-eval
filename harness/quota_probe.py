#!/usr/bin/env python3
"""Check the OpenCode free-tier quota and when it resets, without launching opencode.

opencode's `opencode/*` models are served by an OpenAI-compatible endpoint
(https://opencode.ai/inference/openai/v1, from models.dev). When the free allowance is
exhausted it answers HTTP 429 with a `Retry-After` header (seconds) and a JSON body
{"type":"error","error":{"type":"FreeUsageLimitError",...}}. This script sends one
minimal request and prints the status, the Retry-After value and the local reset time.

Usage:
  python harness/quota_probe.py            # one check
  python harness/quota_probe.py --watch    # re-check at the reset time (and every 10 min after) until OK
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta

ENDPOINT = "https://opencode.ai/inference/openai/v1/chat/completions"
MODEL = "pulse-alpha-free"


def probe(timeout: int = 40) -> dict:
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": "Reply with the word PONG."}],
                       "max_tokens": 5}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                 headers={"content-type": "application/json", "user-agent": "opencode/1.19.5"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
            text = ((data.get("choices") or [{}])[0].get("message") or {}).get("content", "")
            return {"ok": True, "status": resp.status, "text": text, "elapsed": round(time.time() - t0, 1),
                    "log_id": resp.headers.get("x-opencode-log-id")}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(raw).get("error", {})
        except json.JSONDecodeError:
            err = {"message": raw[:200]}
        retry = e.headers.get("Retry-After")
        out = {"ok": False, "status": e.code, "error_type": err.get("type"), "message": err.get("message"),
               "retry_after_s": int(retry) if retry and retry.isdigit() else None,
               "log_id": e.headers.get("x-opencode-log-id"), "elapsed": round(time.time() - t0, 1)}
        if out["retry_after_s"] is not None:
            out["reset_at_local"] = (datetime.now() + timedelta(seconds=out["retry_after_s"])).strftime("%Y-%m-%d %H:%M:%S")
        return out
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "status": None, "message": repr(e), "elapsed": round(time.time() - t0, 1)}


def report(r: dict) -> None:
    now = datetime.now().strftime("%H:%M:%S")
    if r["ok"]:
        print(f"[{now}] quota OK: HTTP {r['status']} in {r['elapsed']}s, model answered {r['text']!r}")
    elif r.get("retry_after_s") is not None:
        h, m = divmod(r["retry_after_s"] // 60, 60)
        print(f"[{now}] quota EXHAUSTED: HTTP {r['status']} {r.get('error_type')}; Retry-After {r['retry_after_s']}s "
              f"(~{h}h{m:02d}m) -> resets about {r['reset_at_local']} local time")
    else:
        print(f"[{now}] request failed: HTTP {r.get('status')} {r.get('message')}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="sleep until Retry-After, then re-check until the quota is back")
    a = ap.parse_args()
    while True:
        r = probe()
        report(r)
        if r["ok"] or not a.watch:
            sys.exit(0 if r["ok"] else 1)
        wait = r.get("retry_after_s") or 600
        time.sleep(min(wait + 30, 6 * 3600))
        # after the announced reset, poll every 10 minutes in case the window slides
        while True:
            r = probe()
            report(r)
            if r["ok"]:
                sys.exit(0)
            time.sleep(600)


if __name__ == "__main__":
    main()
