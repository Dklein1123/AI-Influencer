"""Nano Banana Pro (Google Gemini 3 Pro Image) backend for Sierra.

Mirrors `tools/lora/generate.py` interface so `from_trend.py` can swap
backends via `--backend nano-banana`.

When to use this backend over Replicate Flux + LoRA:
  - Hero / close-up shots where Sierra v1 LoRA has identity drift
    (per `tools/lora/v1-decision.md` slot B4: 2/10 identity).
  - Image-to-image edits the LoRA can't do (background swap, prop add/
    remove, style transfer) — pass `input_image=...`.
  - 4K hero shots for landing-page / press use where Flux's 1024² ceiling
    isn't enough.

Caveats:
  - Nano Banana Pro doesn't expose aspect_ratio. We append composition
    language to the prompt ("9:16 vertical portrait..."). The downstream
    ffmpeg pipeline does aspect-fit cropping so non-9:16 inputs still
    render as 1080x1920 reels.
  - Identity isn't locked the way our trained LoRA is. To approximate
    Sierra, the prompt + a Sierra reference image (image-to-image) is
    the production move.
  - Costs more per gen than Replicate Flux + LoRA (~$0.04 vs ~$0.01)
    but unlocks edits + 4K. Use selectively.

Env:
    GEMINI_API_KEY   (required; get at aistudio.google.com)
    SIERRA_REFERENCE_IMAGE  (optional path/URL — Sierra ref to seed identity)
"""

from __future__ import annotations

import datetime as dt
import importlib
import io
import os
import pathlib
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


def _api_key() -> str:
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        raise RuntimeError(
            "GEMINI_API_KEY missing — needed for Nano Banana Pro. "
            "Get one at https://aistudio.google.com/apikey and add to "
            "~/.AI-Influencer.env."
        )
    return k


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


# Nano-Banana doesn't have an aspect_ratio param — fold composition into prompt.
ASPECT_TO_COMPOSITION = {
    "9:16": "vertical 9:16 portrait composition, full subject in frame, "
            "TikTok / Reel native framing, head and shoulders dominant",
    "16:9": "horizontal 16:9 landscape composition, cinematic framing",
    "4:5": "vertical 4:5 portrait composition, Instagram feed native framing",
    "1:1": "square 1:1 composition, centered subject",
}


def _resolution_for_aspect(aspect: str, requested: str | None) -> str:
    """Return one of '1K', '2K', '4K'. Default 2K for hero, 1K for batch."""
    if requested in ("1K", "2K", "4K"):
        return requested
    return "2K"


def generate(
    persona_name: str,
    template_id: str,
    *,
    aspect_ratio: str | None = None,
    resolution: str | None = None,
    input_image: str | pathlib.Path | None = None,
    extra_prompt: str = "",
    dry_run: bool = False,
) -> dict:
    """Generate a Sierra image via Nano Banana Pro. Returns {'saved': [paths]}.

    Mirrors `tools.lora.generate.generate(...)` shape. Drop-in for
    `from_trend.py` when called with `--backend nano-banana`.

    `input_image` enables image-to-image editing (e.g. Sierra-ref
    + 'change background to South Florida marina, golden hour'). When
    set, falls back to `SIERRA_REFERENCE_IMAGE` env if not provided.

    `resolution` ∈ {None, '1K', '2K', '4K'}. Default 2K (good middle).
    """
    persona = _load_persona(persona_name)
    base_prompt = persona.build_prompt(template_id)
    aspect = aspect_ratio or persona.aspect_for(template_id)
    composition = ASPECT_TO_COMPOSITION.get(
        aspect,
        ASPECT_TO_COMPOSITION["9:16"],
    )
    res = _resolution_for_aspect(aspect, resolution)

    # Compose the final prompt: persona template + composition + extra.
    prompt_parts = [base_prompt, composition]
    if extra_prompt:
        prompt_parts.append(extra_prompt)
    final_prompt = ". ".join(prompt_parts)

    # Resolve reference image for image-to-image (if any).
    ref = input_image or os.environ.get("SIERRA_REFERENCE_IMAGE")
    if ref:
        ref = str(ref)

    if dry_run:
        return {
            "dry_run": True,
            "model": "gemini-3-pro-image-preview",
            "prompt": final_prompt,
            "resolution": res,
            "input_image": ref,
        }

    # Hot import — avoid slow load on dry runs / when not using this backend.
    from google import genai
    from google.genai import types
    from PIL import Image as PILImage

    client = genai.Client(api_key=_api_key())

    # Build contents: [ref_img, prompt] for img2img, or just prompt for txt2img.
    contents: Any
    if ref:
        if ref.startswith("http"):
            import httpx
            with httpx.stream("GET", ref, timeout=60) as r:
                r.raise_for_status()
                ref_bytes = b"".join(r.iter_bytes())
            ref_img = PILImage.open(io.BytesIO(ref_bytes))
        else:
            ref_img = PILImage.open(ref)
        contents = [ref_img, final_prompt]
        print(f"[{template_id}] nano-banana editing from ref ({res}) …", flush=True)
    else:
        contents = final_prompt
        print(f"[{template_id}] nano-banana generating ({res}, aspect={aspect}) …", flush=True)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(image_size=res),
        ),
    )

    saved: list[pathlib.Path] = []
    queue = _content_queue(persona)
    for part in response.parts:
        if getattr(part, "text", None):
            # Surfaces any model commentary; not useful in production.
            pass
        elif getattr(part, "inline_data", None):
            data = part.inline_data.data
            if isinstance(data, str):
                import base64
                data = base64.b64decode(data)
            img = PILImage.open(io.BytesIO(data))
            if img.mode != "RGB":
                bg = PILImage.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = bg
            dest = queue / f"{_today()}_{template_id}_nbp_{len(saved)+1}.png"
            img.save(str(dest), "PNG")
            saved.append(dest)
            print(f"[{template_id}] saved {dest.relative_to(REPO_ROOT)}", flush=True)

    if not saved:
        raise RuntimeError("Nano Banana Pro returned no images")

    # Log + best-effort sync to portal.
    log = _generation_log(persona)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(
            f"\n## {dt.datetime.now().isoformat(timespec='seconds')} — {template_id} (nano-banana-pro)\n"
            f"- model: gemini-3-pro-image-preview\n"
            f"- resolution: {res}\n"
            f"- prompt: {final_prompt}\n"
            f"- input_image: {ref or '(none)'}\n"
            f"- saved: {', '.join(str(p) for p in saved)}\n"
        )

    try:
        from tools.sync import supabase_client as sync
        if sync.is_enabled():
            sync.insert_ai_output(
                title=f"{template_id} — Nano Banana Pro {res}",
                content=f"prompt: {final_prompt}\nresolution: {res}\noutput: {saved[0]}",
                kind="image",
                source_prompt=template_id,
                tags=[template_id, "nano-banana", res, f"persona-{persona.NAME}"],
            )
    except Exception:
        pass

    return {"saved": [str(p) for p in saved]}


# CLI for quick smoke-tests
def _cli() -> int:
    import argparse, sys
    p = argparse.ArgumentParser(description="Nano Banana Pro generation for Sierra")
    p.add_argument("--persona", default="sierra_frost")
    p.add_argument("--template", required=True, help="e.g. P32")
    p.add_argument("--resolution", choices=["1K", "2K", "4K"], default="2K")
    p.add_argument("--input-image", help="Optional reference image for img2img")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    res = generate(
        args.persona, args.template,
        resolution=args.resolution,
        input_image=args.input_image,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        print(res)
    else:
        for p_ in res["saved"]:
            print(p_)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
