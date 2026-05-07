"""Pollinations.ai (free Flux endpoint) image-gen backend for Sierra.

Mirrors `tools/lora/generate.py` interface so `from_trend.py` can use
this as `--backend pollinations` for FREE generations. No API key
required for basic use; optional bearer token for unlimited rate +
nologo.

When to use this backend:
  - Cloud burst when local ComfyUI is busy
  - Anything where Sierra-LoRA identity-lock isn't critical (B-roll,
    backgrounds, stills with no face, etc.)
  - Smoke-tests / dry runs where you don't want to spend $0.01 on
    Replicate

Caveats:
  - No LoRA stack support — this is pure Flux without the Sierra v1
    + Boreal stack. Identity-lock won't be as tight as Replicate path.
  - Rate-limited per IP without a server key (1 req/hr on client tier).
  - Default has a small Pollinations watermark unless you have a key
    + nologo=true.

Env (optional, all free):
    POLLINATIONS_KEY            server key (sk_...) — unlimited, no watermark
    POLLINATIONS_REFERRER       'sierra-frost' identifier shown in their feed

Usage:
    python -m tools.generation.pollinations --template P50 --width 1024 --height 1820
    python -m tools.generation.pollinations --template P12 --model turbo
    # Or via from_trend:
    python -m tools.assembly.from_trend --plan-from-file ... --backend pollinations
"""

from __future__ import annotations

import datetime as dt
import importlib
import os
import pathlib
import urllib.parse
from types import ModuleType
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


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


POLLINATIONS_BASE = "https://image.pollinations.ai/prompt"


def _load_persona(name: str) -> ModuleType:
    return importlib.import_module(f"tools.generation.{name}")


def _persona_dir(persona: ModuleType) -> pathlib.Path:
    return REPO_ROOT / "personas" / persona.NAME


def _content_queue(persona: ModuleType) -> pathlib.Path:
    d = _persona_dir(persona) / "content-queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _generation_log(persona: ModuleType) -> pathlib.Path:
    return _persona_dir(persona) / "generation-log.md"


def _today() -> str:
    return dt.date.today().isoformat()


# Map Sierra's aspect strings to (width, height) pairs Pollinations accepts.
ASPECT_TO_WH = {
    "9:16":  (1024, 1820),
    "16:9":  (1820, 1024),
    "4:5":   (1024, 1280),
    "1:1":   (1024, 1024),
    "3:4":   (1024, 1365),
}


def generate(
    persona_name: str,
    template_id: str,
    *,
    aspect_ratio: str | None = None,
    model: str = "flux",
    seed: int | None = None,
    width: int | None = None,
    height: int | None = None,
    enhance: bool = False,
    extra_prompt: str = "",
    dry_run: bool = False,
) -> dict:
    """Generate one Sierra image via Pollinations (free Flux). Returns
    `{'saved': [paths]}` matching the lora.generate / nano_banana.generate
    interface so from_trend.py can dispatch to any backend uniformly.

    Note: no LoRA stack — identity won't be as locked as the Replicate
    Sierra-LoRA path. Use this for B-roll / cloud bursts, not for daily
    Sierra-face content.
    """
    persona = _load_persona(persona_name)
    base_prompt = persona.build_prompt(template_id)

    aspect = aspect_ratio or persona.aspect_for(template_id)
    if width is None or height is None:
        w, h = ASPECT_TO_WH.get(aspect, ASPECT_TO_WH["9:16"])
        width = width or w
        height = height or h

    parts = [base_prompt]
    if extra_prompt:
        parts.append(extra_prompt)
    final_prompt = ". ".join(parts)

    params: dict[str, Any] = {
        "model": model,
        "width": width,
        "height": height,
        "private": "true",       # don't surface in public feed
        "nologo": "true",        # only honored if a key is present
    }
    if seed is not None:
        params["seed"] = seed
    if enhance:
        params["enhance"] = "true"
    referrer = os.environ.get("POLLINATIONS_REFERRER", "sierra-frost")
    if referrer:
        params["referrer"] = referrer

    encoded_prompt = urllib.parse.quote(final_prompt, safe="")
    qs = urllib.parse.urlencode(params)
    url = f"{POLLINATIONS_BASE}/{encoded_prompt}?{qs}"

    if dry_run:
        return {
            "dry_run": True,
            "url": url,
            "model": model,
            "size": f"{width}x{height}",
        }

    import httpx
    headers = {}
    key = os.environ.get("POLLINATIONS_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"

    print(
        f"[{template_id}] pollinations generating ({width}x{height}, model={model}"
        f"{', authed' if key else ''}) …",
        flush=True,
    )
    r = httpx.get(url, headers=headers, timeout=180, follow_redirects=True)
    r.raise_for_status()

    queue = _content_queue(persona)
    dest = queue / f"{_today()}_{template_id}_pollinations.png"
    dest.write_bytes(r.content)
    print(f"[{template_id}] saved {dest.relative_to(REPO_ROOT)} ({len(r.content):,} bytes)", flush=True)

    # Log + best-effort sync.
    log = _generation_log(persona)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(
            f"\n## {dt.datetime.now().isoformat(timespec='seconds')} — "
            f"{template_id} (pollinations / {model})\n"
            f"- size: {width}x{height}\n"
            f"- prompt: {final_prompt}\n"
            f"- seed: {seed}\n"
            f"- saved: {dest}\n"
        )

    try:
        from tools.sync import supabase_client as sync
        if sync.is_enabled():
            sync.insert_ai_output(
                title=f"{template_id} — Pollinations {model}",
                content=f"prompt: {final_prompt}\nsize: {width}x{height}\noutput: {dest}",
                kind="image",
                source_prompt=template_id,
                tags=[template_id, "pollinations", model, f"persona-{persona.NAME}"],
            )
    except Exception:
        pass

    return {"saved": [str(dest)]}


def _cli() -> int:
    import argparse, sys
    p = argparse.ArgumentParser(description="Pollinations.ai backend for Sierra")
    p.add_argument("--persona", default="sierra_frost")
    p.add_argument("--template", required=True, help="e.g. P32")
    p.add_argument("--model", default="flux", help="flux | turbo")
    p.add_argument("--seed", type=int)
    p.add_argument("--width", type=int)
    p.add_argument("--height", type=int)
    p.add_argument("--enhance", action="store_true", help="server-side prompt enhancement")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    res = generate(
        args.persona, args.template,
        model=args.model, seed=args.seed,
        width=args.width, height=args.height,
        enhance=args.enhance, dry_run=args.dry_run,
    )
    if args.dry_run:
        print(res["url"])
    else:
        for f in res["saved"]:
            print(f)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
