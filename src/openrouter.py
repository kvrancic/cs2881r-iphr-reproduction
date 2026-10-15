"""Minimal async OpenRouter client with on-disk caching and a hard spend cap.

Every completed call is appended to a JSONL cache keyed by a request id, so
re-running a script never pays twice for the same sample. Spend is summed from
the `usage.cost` field OpenRouter returns and checked before each call.
"""

import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
SPEND_LOG = ROOT / "data" / "spend.jsonl"
SPEND_CAP_USD = float(os.environ.get("SPEND_CAP_USD", "100"))


def total_spend() -> float:
    if not SPEND_LOG.exists():
        return 0.0
    return sum(json.loads(line)["cost"] for line in SPEND_LOG.open())


class SpendCapReached(RuntimeError):
    pass


def load_cache(path: Path) -> dict:
    """Return {request_id: record} for every cached call in a JSONL file."""
    if not path.exists():
        return {}
    out = {}
    for line in path.open():
        rec = json.loads(line)
        out[rec["id"]] = rec
    return out


async def _call(client, sem, model, messages, params, retries=6):
    body = {"model": model, "messages": messages, "usage": {"include": True}, **params}
    for attempt in range(retries):
        async with sem:
            try:
                r = await client.post(API_URL, json=body, timeout=600)
                if r.status_code == 200:
                    d = r.json()
                    if "choices" in d and d["choices"]:
                        return d
                elif r.status_code in (400, 401, 402, 403, 404):
                    raise RuntimeError(f"{r.status_code}: {r.text[:300]}")
            except (httpx.HTTPError, json.JSONDecodeError):
                pass
        await asyncio.sleep(2 ** attempt)
    return None


async def run_requests(requests, cache_path: Path, model: str, params: dict,
                       concurrency: int = 32, tag: str = ""):
    """requests: list of (request_id, messages). Returns {request_id: record}.

    A record holds the response text, the reasoning text (if any), token usage
    and cost. Requests already in the cache are skipped.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    SPEND_LOG.parent.mkdir(parents=True, exist_ok=True)
    cache = load_cache(cache_path)
    todo = [(rid, m) for rid, m in requests if rid not in cache]
    if not todo:
        return cache
    spent = total_spend()
    if spent >= SPEND_CAP_USD:
        raise SpendCapReached(f"spent ${spent:.2f} >= cap ${SPEND_CAP_USD}")

    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    state = {"spent": spent, "done": 0, "failed": 0}

    async with httpx.AsyncClient(headers=headers) as client:
        async def one(rid, messages):
            if state["spent"] >= SPEND_CAP_USD:
                return
            d = await _call(client, sem, model, messages, params)
            if d is None:
                state["failed"] += 1
                return
            msg = d["choices"][0]["message"]
            usage = d.get("usage") or {}
            rec = {
                "id": rid,
                "model": model,
                "content": msg.get("content") or "",
                "reasoning": msg.get("reasoning") or "",
                "finish_reason": d["choices"][0].get("finish_reason"),
                "provider": d.get("provider"),
                "usage": usage,
            }
            cost = float(usage.get("cost") or 0.0)
            async with lock:
                with cache_path.open("a") as f:
                    f.write(json.dumps(rec) + "\n")
                with SPEND_LOG.open("a") as f:
                    f.write(json.dumps({"tag": tag or model, "cost": cost}) + "\n")
                state["spent"] += cost
                state["done"] += 1
                cache[rid] = rec
                if state["done"] % 500 == 0:
                    print(f"  [{tag or model}] {state['done']}/{len(todo)} "
                          f"total spend ${state['spent']:.2f}", flush=True)

        await asyncio.gather(*(one(rid, m) for rid, m in todo))
    print(f"  [{tag or model}] finished {state['done']} new, {state['failed']} failed, "
          f"total spend ${state['spent']:.2f}", flush=True)
    return cache
