"""Shared API clients for research tooling.

Provides thin wrappers around Apify and Firecrawl. Reads keys from
~/.AI-Influencer.env (mode 600).

Apify: https://docs.apify.com/api/v2
Firecrawl: https://docs.firecrawl.dev/api-reference
"""

from __future__ import annotations

import json
import os
import pathlib
import time
from typing import Any

import httpx


def _load_env() -> None:
    env = pathlib.Path.home() / ".AI-Influencer.env"
    if not env.is_file():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env)
    except ImportError:
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


_load_env()


# ---- Apify ----------------------------------------------------------------

APIFY_BASE = "https://api.apify.com/v2"


def apify_token() -> str:
    tok = os.environ.get("APIFY_API_TOKEN")
    if not tok:
        raise RuntimeError("APIFY_API_TOKEN missing from env")
    return tok


def apify_run_sync(
    actor: str,
    payload: dict[str, Any],
    *,
    timeout: float = 240.0,
    max_items: int = 50,
) -> list[dict[str, Any]]:
    """Run an Apify actor synchronously and return dataset items.

    `actor` is the slug (e.g. 'clockworks~free-tiktok-scraper') OR the
    user/name form ('clockworks/free-tiktok-scraper'). We normalize to
    the slug used by the API.
    """
    slug = actor.replace("/", "~")
    url = f"{APIFY_BASE}/acts/{slug}/run-sync-get-dataset-items"
    params = {"token": apify_token(), "limit": max_items, "format": "json"}
    r = httpx.post(url, params=params, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json() if r.content else []


def apify_start_run(actor: str, payload: dict[str, Any]) -> str:
    """Start an actor run async; returns run id. Use for long jobs."""
    slug = actor.replace("/", "~")
    url = f"{APIFY_BASE}/acts/{slug}/runs"
    params = {"token": apify_token()}
    r = httpx.post(url, params=params, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["data"]["id"]


def apify_run_status(run_id: str) -> dict[str, Any]:
    url = f"{APIFY_BASE}/actor-runs/{run_id}"
    r = httpx.get(url, params={"token": apify_token()}, timeout=30)
    r.raise_for_status()
    return r.json()["data"]


def apify_dataset_items(dataset_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
    url = f"{APIFY_BASE}/datasets/{dataset_id}/items"
    r = httpx.get(url, params={"token": apify_token(), "limit": limit, "format": "json"}, timeout=60)
    r.raise_for_status()
    return r.json() if r.content else []


def apify_wait(run_id: str, *, poll: float = 5.0, timeout: float = 600.0) -> dict[str, Any]:
    """Poll until run finishes; returns final run record."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        run = apify_run_status(run_id)
        if run["status"] in {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}:
            return run
        time.sleep(poll)
    raise TimeoutError(f"Apify run {run_id} timed out after {timeout}s")


# ---- Firecrawl -------------------------------------------------------------

FIRECRAWL_BASE = "https://api.firecrawl.dev/v2"


def firecrawl_key() -> str:
    k = os.environ.get("FIRECRAWL_API_KEY")
    if not k:
        raise RuntimeError("FIRECRAWL_API_KEY missing from env")
    return k


def firecrawl_scrape(url: str, *, formats: list[str] | None = None, only_main: bool = True) -> dict[str, Any]:
    """Scrape a single URL. Returns markdown + metadata by default."""
    headers = {"Authorization": f"Bearer {firecrawl_key()}", "Content-Type": "application/json"}
    body = {
        "url": url,
        "formats": formats or ["markdown"],
        "onlyMainContent": only_main,
    }
    r = httpx.post(f"{FIRECRAWL_BASE}/scrape", headers=headers, json=body, timeout=120)
    r.raise_for_status()
    return r.json().get("data", {})


def firecrawl_search(query: str, *, limit: int = 10, scrape: bool = False) -> list[dict[str, Any]]:
    """Web-search via Firecrawl. Optionally scrape each hit's markdown."""
    headers = {"Authorization": f"Bearer {firecrawl_key()}", "Content-Type": "application/json"}
    body: dict[str, Any] = {"query": query, "limit": limit}
    if scrape:
        body["scrapeOptions"] = {"formats": ["markdown"], "onlyMainContent": True}
    r = httpx.post(f"{FIRECRAWL_BASE}/search", headers=headers, json=body, timeout=120)
    r.raise_for_status()
    payload = r.json().get("data", {})
    if isinstance(payload, list):
        return payload
    return payload.get("web", []) or []


# ---- Claude scoring (Anthropic API via stdlib httpx) ----------------------

ANTHROPIC_BASE = "https://api.anthropic.com/v1"


def anthropic_key() -> str | None:
    return os.environ.get("ANTHROPIC_API_KEY")


def claude_score(prompt: str, *, model: str = "claude-haiku-4-5-20251001", max_tokens: int = 1024) -> str:
    """Send a prompt to Claude and return text. Raises if no key."""
    key = anthropic_key()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY missing — score skipped")
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = httpx.post(f"{ANTHROPIC_BASE}/messages", headers=headers, json=body, timeout=120)
    r.raise_for_status()
    return "".join(b.get("text", "") for b in r.json().get("content", []) if b.get("type") == "text")


# ---- Output helpers --------------------------------------------------------

def write_markdown(path: pathlib.Path, content: str) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def dump_json(path: pathlib.Path, obj: Any) -> pathlib.Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str))
    return path
