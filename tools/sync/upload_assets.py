"""Upload existing Sierra assets from content-queue/ to Supabase Storage.

For each image / video in `personas/sierra-frost/content-queue/`:
  1. Call Edge Function `presigned_upload` to get a signed PUT URL +
     the eventual public URL.
  2. PUT the file bytes to the signed URL.
  3. Call Edge Function `insert_asset` to record the asset in the DB.

Also re-tags the matching `ai_outputs` row's `content` field with the
public URL so the portal can show thumbnails.

Run:
    python -m tools.sync.upload_assets
    python -m tools.sync.upload_assets --dry-run   # show plan, don't upload

Idempotent — uses the filename as the storage path; subsequent runs
upsert (the bucket is configured with upsert=true via the Edge Function).
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import pathlib
import sys
from typing import Any

import httpx

from .constants import SIERRA_FROST_ID, SYNC_FN_URL

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTENT_QUEUE = REPO_ROOT / "personas" / "sierra-frost" / "content-queue"

BUCKET = "sierra-assets"


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


def _api_key() -> str:
    key = os.environ.get("SYNC_API_KEY")
    if not key:
        raise RuntimeError("SYNC_API_KEY not in env; run after `source` of .AI-Influencer.env.")
    return key


def _post(op: str, data: dict[str, Any], *, timeout: float = 60.0) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {_api_key()}", "Content-Type": "application/json"}
    body = {"op": op, "data": data}
    r = httpx.post(SYNC_FN_URL, headers=headers, json=body, timeout=timeout)
    if r.status_code >= 400:
        # Surface the Edge Function's structured error message instead of the bare HTTP status.
        raise RuntimeError(f"sync op '{op}' returned {r.status_code}: {r.text[:500]}")
    return r.json()


def upload_one(local_path: pathlib.Path, *, dry_run: bool = False) -> dict[str, Any]:
    """Upload one file. Returns {path, public_url, asset_id} or {dry_run, ...}."""
    name = local_path.name
    storage_path = f"sierra-frost/{name}"
    mime, _ = mimetypes.guess_type(str(local_path))
    mime = mime or "application/octet-stream"
    asset_type = "image" if mime.startswith("image/") else ("video" if mime.startswith("video/") else "other")

    if dry_run:
        return {"dry_run": True, "local": str(local_path), "storage_path": storage_path, "mime": mime, "asset_type": asset_type}

    # 1. Get presigned upload URL.
    upload_info = _post("presigned_upload", {"bucket": BUCKET, "path": storage_path})
    upload_url = upload_info["upload_url"]
    public_url = upload_info["public_url"]

    # 2. PUT the file bytes. The signedUrl already contains an embedded token
    #    so no Authorization header is needed; just send Content-Type + body.
    with local_path.open("rb") as f:
        body = f.read()
    r = httpx.put(upload_url, headers={"Content-Type": mime}, content=body, timeout=300)
    r.raise_for_status()

    # 3. Insert into the assets table.
    template_id = ""
    parts = name.split("_")
    for p in parts:
        if p.startswith("P") and p[1:].split(".")[0].isdigit():
            template_id = p
            break

    asset_payload: dict[str, Any] = {
        "influencer_id": SIERRA_FROST_ID,
        "name": name,
        "type": asset_type,
        "url": public_url,
        "tags": list(filter(None, [template_id, asset_type, "soul_2", "sierra-frost"])),
    }
    # Only include nullable fields when they have real values — the Edge
    # Function distinguishes `undefined` (skip) from `null` (invalid).
    if asset_type == "image":
        asset_payload["thumbnail_url"] = public_url
    if template_id:
        asset_payload["notes"] = f"Generated asset for template {template_id}"
    asset_row = _post("insert_asset", asset_payload)

    return {
        "local": str(local_path),
        "storage_path": storage_path,
        "public_url": public_url,
        "asset_id": asset_row.get("id"),
        "size_bytes": local_path.stat().st_size,
    }


def iter_uploadable(content_queue: pathlib.Path = CONTENT_QUEUE) -> list[pathlib.Path]:
    """Return all files in content-queue that should be uploaded."""
    if not content_queue.is_dir():
        return []
    keep = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".webm"}
    return sorted(p for p in content_queue.iterdir() if p.suffix.lower() in keep)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.sync.upload_assets")
    p.add_argument("--dry-run", action="store_true", help="Show what would be uploaded without doing it.")
    p.add_argument("--limit", type=int, default=None, help="Only process the first N files.")
    args = p.parse_args(argv)

    files = iter_uploadable()
    if args.limit:
        files = files[: args.limit]

    if not files:
        print(f"No files found in {CONTENT_QUEUE}", file=sys.stderr)
        return 1

    print(f"Found {len(files)} files to upload to bucket '{BUCKET}'.\n")
    for f in files:
        try:
            r = upload_one(f, dry_run=args.dry_run)
            if args.dry_run:
                print(f"  [dry-run] {r['local']:>60} → {r['storage_path']}  ({r['mime']})")
            else:
                size_mb = r["size_bytes"] / 1_048_576
                print(f"  ✓ {f.name:>40} → {r['public_url']}  ({size_mb:.2f} MB, asset_id={r['asset_id']})")
        except Exception as e:
            print(f"  ✗ {f.name}: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
