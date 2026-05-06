"""Higgsfield SDK wrapper.

Loads credentials from ~/.AI-Influencer.env, exposes a generate() entry
point that takes a persona module and a template id, and handles polling,
download, and logging.
"""

from __future__ import annotations

import datetime as dt
import importlib
import os
import pathlib
import re
import sys
from types import ModuleType
from typing import Any

import requests
from dotenv import load_dotenv

# Load env from ~/.AI-Influencer.env (the canonical location for keys).
ENV_PATH = pathlib.Path.home() / ".AI-Influencer.env"
if ENV_PATH.is_file():
    load_dotenv(ENV_PATH)

import higgsfield_client as hf  # noqa: E402  — import after env load


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# Soul 2's API only accepts these literal width_and_height strings, not free-form
# aspect ratios. Map persona aspects (e.g. "9:16") to the closest supported size.
# 4:5 has no exact Soul 2 size — we use 3:4 (1536x2048) as the closest portrait.
ASPECT_TO_WH = {
    "9:16": "1152x2048",
    "16:9": "2048x1152",
    "1:1": "1536x1536",
    "3:4": "1536x2048",
    "4:3": "2048x1536",
    "4:5": "1536x2048",
}


def _load_persona(name: str) -> ModuleType:
    """Import a persona module by name (e.g. 'sierra-frost' or 'sierra_frost')."""
    module_name = f"tools.generation.{name.replace('-', '_')}"
    return importlib.import_module(module_name)


def _client() -> hf.SyncClient:
    """Construct a SyncClient. Raises if HF_KEY isn't set."""
    return hf.SyncClient()


def _persona_dir(persona: ModuleType) -> pathlib.Path:
    """Path to personas/<name>/ in the repo."""
    return REPO_ROOT / "personas" / persona.NAME


def _content_queue_dir(persona: ModuleType) -> pathlib.Path:
    d = _persona_dir(persona) / "content-queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _generation_log(persona: ModuleType) -> pathlib.Path:
    return _persona_dir(persona) / "generation-log.md"


def _soul_id(persona: ModuleType) -> str | None:
    return os.getenv(persona.SOUL_ID_ENV_VAR) or None


def _today() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def _safe_filename(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s)[:40]


def _download(url: str, dest: pathlib.Path) -> None:
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with dest.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 14):
                f.write(chunk)


def _extract_assets(result: Any) -> list[tuple[str, str]]:
    """Pull (url, ext) tuples from a Higgsfield result payload.

    The exact shape varies by endpoint (image vs video, sync vs async).
    We walk the structure and collect anything that looks like a media URL.
    """
    found: list[tuple[str, str]] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            url = (
                node.get("rawUrl")
                or node.get("url")
                or node.get("image_url")
                or node.get("video_url")
            )
            if isinstance(url, str) and url.startswith("http"):
                ext = "png" if ".png" in url else ("mp4" if any(k in url for k in (".mp4", "video")) else "jpg")
                found.append((url, ext))
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)

    visit(result)
    return found


def _append_log(
    persona: ModuleType,
    template_id: str,
    prompt: str,
    application: str,
    arguments: dict,
    result_summary: str,
    saved_files: list[pathlib.Path],
    seed: int | None,
) -> None:
    log = _generation_log(persona)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write(f"# {persona.DISPLAY_NAME} — Generation Log\n\n")
            f.write("Append-only log of every generation. Do not edit history.\n\n")
        f.write(f"## {dt.datetime.now().isoformat(timespec='seconds')} — {template_id}\n\n")
        f.write(f"- application: `{application}`\n")
        f.write(f"- seed: `{seed}`\n")
        f.write(f"- aspect: `{arguments.get('aspect_ratio', '?')}`\n")
        f.write(f"- soul_id: `{arguments.get('custom_reference_id', '(none)')}`\n")
        f.write(f"- result: {result_summary}\n")
        if saved_files:
            f.write("- saved:\n")
            for p in saved_files:
                f.write(f"  - `{p.relative_to(REPO_ROOT)}`\n")
        f.write(f"- prompt:\n  ```\n  {prompt}\n  ```\n\n")


def generate(
    persona_name: str,
    template_id: str,
    *,
    seed: int | None = None,
    extra_prompt: str = "",
    application: str | None = None,
    aspect_ratio: str | None = None,
    dry_run: bool = False,
) -> dict:
    """Run a single generation. Returns a dict summary.

    For video templates we use Higgsfield's image-to-video DoP endpoint
    only when an input image is provided; otherwise we fall back to Soul
    text-to-image, which produces a static image. Video pipelines that
    take prompt-only inputs are added per-template if/when needed.
    """
    persona = _load_persona(persona_name)
    prompt = persona.build_prompt(template_id)
    if extra_prompt:
        prompt = f"{prompt}, {extra_prompt}"

    aspect = aspect_ratio or persona.aspect_for(template_id)
    if aspect not in ASPECT_TO_WH:
        raise ValueError(
            f"unsupported aspect '{aspect}' for {template_id}; "
            f"Soul 2 accepts {sorted(ASPECT_TO_WH)}"
        )
    width_and_height = ASPECT_TO_WH[aspect]
    soul = _soul_id(persona)

    app = application or "/v1/text2image/soul"
    inner: dict = {
        "model": "soul_2",
        "prompt": prompt,
        "width_and_height": width_and_height,
    }
    if seed is not None:
        inner["seed"] = seed
    if soul:
        inner["soul_id"] = soul
    args = {"params": inner}

    if dry_run:
        return {
            "dry_run": True,
            "application": app,
            "arguments": args,
        }

    client = _client()
    print(f"[{template_id}] submitting to {app} (size={width_and_height}, soul={'yes' if soul else 'no'})", flush=True)
    result = client.subscribe(
        app,
        args,
        on_enqueue=lambda rid: print(f"[{template_id}] queued: {rid}", flush=True),
        on_queue_update=lambda s: print(f"[{template_id}] status: {type(s).__name__}", flush=True),
    )

    assets = _extract_assets(result)
    saved: list[pathlib.Path] = []
    queue = _content_queue_dir(persona)
    for i, (url, ext) in enumerate(assets):
        name = _safe_filename(f"{_today()}_{template_id}_v{i+1}.{ext}")
        dest = queue / name
        _download(url, dest)
        saved.append(dest)
        print(f"[{template_id}] saved {dest.relative_to(REPO_ROOT)}", flush=True)

    summary = "ok" if assets else "completed but no assets extracted (inspect log)"
    _append_log(persona, template_id, prompt, app, args, summary, saved, seed)
    return {
        "template_id": template_id,
        "saved": [str(p) for p in saved],
        "result": result,
    }


def generate_batch(
    persona_name: str,
    template_ids: list[str],
    *,
    seed: int | None = None,
    dry_run: bool = False,
) -> list[dict]:
    out: list[dict] = []
    for tid in template_ids:
        try:
            out.append(generate(persona_name, tid, seed=seed, dry_run=dry_run))
        except Exception as e:
            print(f"[{tid}] FAILED: {e}", file=sys.stderr, flush=True)
            out.append({"template_id": tid, "error": str(e)})
    return out
