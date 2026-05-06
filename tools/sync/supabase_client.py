"""Best-effort sync from this repo's tooling to the Lovable/Supabase portal.

Every successful generation should call `sync.insert_ai_output(...)` so the
operator portal sees it in seconds. Sync failures are logged but never
break the caller — generation always wins.

Auth: shared `SYNC_API_KEY` between this client and the Lovable Edge
Function. Stored in `~/.AI-Influencer.env` (mode 600); never committed.
"""

from __future__ import annotations

import os
import pathlib
import sys
from typing import Any, Iterable

import httpx

from .constants import SIERRA_FROST_ID, SYNC_FN_URL


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


class SyncDisabledError(Exception):
    """Raised when sync is intentionally disabled (env vars missing)."""


def _api_key() -> str:
    key = os.environ.get("SYNC_API_KEY")
    if not key:
        raise SyncDisabledError("SYNC_API_KEY not in env; sync disabled.")
    return key


def _post(op: str, data: dict[str, Any], *, timeout: float = 30.0) -> dict[str, Any]:
    """Low-level POST. Raises httpx.HTTPStatusError on non-2xx."""
    headers = {"Authorization": f"Bearer {_api_key()}", "Content-Type": "application/json"}
    body = {"op": op, "data": data}
    r = httpx.post(SYNC_FN_URL, headers=headers, json=body, timeout=timeout)
    r.raise_for_status()
    return r.json() if r.content else {}


# ---- public API ---------------------------------------------------------

def insert_ai_output(
    *,
    title: str,
    content: str,
    kind: str = "image",
    source_prompt: str | None = None,
    tags: Iterable[str] | None = None,
    starred: bool = False,
    influencer_id: str = SIERRA_FROST_ID,
    quiet: bool = False,
) -> dict[str, Any] | None:
    """Insert a row into ai_outputs. Best-effort — returns None on failure."""
    try:
        return _post("insert_ai_output", {
            "influencer_id": influencer_id,
            "kind": kind,
            "title": title,
            "content": content,
            "source_prompt": source_prompt or "",
            "tags": list(tags or []),
            "starred": starred,
        })
    except SyncDisabledError as e:
        if not quiet:
            print(f"[sync] disabled: {e}", file=sys.stderr)
        return None
    except Exception as e:
        if not quiet:
            print(f"[sync] insert_ai_output failed: {e}", file=sys.stderr)
        return None


def insert_asset(
    *,
    name: str,
    type: str,  # 'image' | 'video' | etc.
    url: str,
    thumbnail_url: str | None = None,
    notes: str | None = None,
    tags: Iterable[str] | None = None,
    influencer_id: str = SIERRA_FROST_ID,
    quiet: bool = False,
) -> dict[str, Any] | None:
    """Insert a row into assets. Best-effort."""
    try:
        return _post("insert_asset", {
            "influencer_id": influencer_id,
            "name": name,
            "type": type,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "notes": notes or "",
            "tags": list(tags or []),
        })
    except SyncDisabledError as e:
        if not quiet:
            print(f"[sync] disabled: {e}", file=sys.stderr)
        return None
    except Exception as e:
        if not quiet:
            print(f"[sync] insert_asset failed: {e}", file=sys.stderr)
        return None


def update_influencer_notes(
    *,
    internal_notes: str,
    influencer_id: str = SIERRA_FROST_ID,
    quiet: bool = False,
) -> dict[str, Any] | None:
    """Update the influencers.internal_notes field. Best-effort."""
    try:
        return _post("update_influencer_notes", {
            "influencer_id": influencer_id,
            "internal_notes": internal_notes,
        })
    except SyncDisabledError as e:
        if not quiet:
            print(f"[sync] disabled: {e}", file=sys.stderr)
        return None
    except Exception as e:
        if not quiet:
            print(f"[sync] update_influencer_notes failed: {e}", file=sys.stderr)
        return None


def is_enabled() -> bool:
    """Cheap check — returns True iff SYNC_API_KEY is present."""
    return bool(os.environ.get("SYNC_API_KEY"))
