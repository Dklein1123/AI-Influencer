"""Inference against the trained Sierra LoRA on Replicate.

Usage:
    python -m tools.lora.generate P14
    python -m tools.lora.generate --persona sierra-frost --aspect 9:16 P1 P3 P7

Reads the persona's prompt template (from `tools/generation/<persona>.py`),
prepends the LoRA's trigger token, calls Replicate, downloads the result
into `personas/<persona>/content-queue/`, and appends to generation-log.md.

Requires:
    REPLICATE_API_TOKEN=r8_...
    SIERRA_LORA_VERSION=<owner>/<name>:<sha>      (printed by train.py)
    SIERRA_LORA_TRIGGER=SIERRA_FROST_V1            (defaults to this)

The interface deliberately mirrors `tools/generation/__main__.py` so that
once we're confident in LoRA quality, we can flip the default backend by
re-aliasing the CLI module. Same template IDs, same arguments, different
backend, ~30x cheaper.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib
import os
import pathlib
import sys
from types import ModuleType

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

DEFAULT_TRIGGER = "SIERRA_FROST_V1"

# Aspect ratio labels accepted by Replicate's Flux schedulers.
SUPPORTED_ASPECTS = {"1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21"}


def _load_env() -> None:
    env = pathlib.Path.home() / ".AI-Influencer.env"
    if env.is_file():
        try:
            from dotenv import load_dotenv

            load_dotenv(env)
        except ImportError:
            for line in env.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def _load_persona(name: str) -> ModuleType:
    return importlib.import_module(f"tools.generation.{name.replace('-', '_')}")


def _persona_dir(persona: ModuleType) -> pathlib.Path:
    return REPO_ROOT / "personas" / persona.NAME


def _content_queue(persona: ModuleType) -> pathlib.Path:
    d = _persona_dir(persona) / "content-queue"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _generation_log(persona: ModuleType) -> pathlib.Path:
    return _persona_dir(persona) / "generation-log.md"


def _today() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def _append_log(persona: ModuleType, template_id: str, prompt: str, args: dict, saved: list[pathlib.Path]) -> None:
    log = _generation_log(persona)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write(f"# {persona.DISPLAY_NAME} — Generation Log\n\n")
        f.write(f"## {dt.datetime.now().isoformat(timespec='seconds')} — {template_id} (LoRA)\n\n")
        f.write(f"- backend: replicate-flux-lora\n")
        f.write(f"- model: `{args.get('model')}`\n")
        f.write(f"- aspect: `{args.get('aspect_ratio')}`\n")
        f.write(f"- guidance: `{args.get('guidance')}`\n")
        f.write(f"- lora_scale: `{args.get('lora_scale')}`\n")
        if saved:
            f.write("- saved:\n")
            for p in saved:
                f.write(f"  - `{p.relative_to(REPO_ROOT)}`\n")
        f.write(f"- prompt:\n  ```\n  {prompt}\n  ```\n\n")


def generate(persona_name: str, template_id: str, *, aspect_ratio: str | None = None, lora_scale: float = 1.0, guidance: float = 3.5, dry_run: bool = False) -> dict:
    persona = _load_persona(persona_name)
    base_prompt = persona.build_prompt(template_id)
    trigger = os.environ.get("SIERRA_LORA_TRIGGER", DEFAULT_TRIGGER)
    prompt = f"{trigger}, {base_prompt}"

    aspect = aspect_ratio or persona.aspect_for(template_id)
    if aspect not in SUPPORTED_ASPECTS:
        # Replicate Flux maps 4:5 → 4:5 if we use "custom" w/h; for now snap to 3:4.
        aspect = "3:4"

    args = {
        "prompt": prompt,
        "aspect_ratio": aspect,
        "guidance": guidance,
        "lora_scale": lora_scale,
        "num_inference_steps": 28,
        "num_outputs": 1,
        "output_format": "png",
        "output_quality": 95,
    }

    if dry_run:
        return {"dry_run": True, "prompt": prompt, "args": args}

    version = os.environ.get("SIERRA_LORA_VERSION")
    if not version:
        raise RuntimeError("SIERRA_LORA_VERSION not set; train the LoRA first via tools.lora.train.")
    args["model"] = version

    import replicate
    import requests

    print(f"[{template_id}] submitting to {version} (aspect={aspect}, lora_scale={lora_scale})", flush=True)
    output = replicate.run(version, input=args)
    urls = list(output) if hasattr(output, "__iter__") and not isinstance(output, str) else [output]

    saved: list[pathlib.Path] = []
    queue = _content_queue(persona)
    for i, url in enumerate(urls):
        ext = "png"
        dest = queue / f"{_today()}_{template_id}_lora_v{i+1}.{ext}"
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 14):
                    f.write(chunk)
        saved.append(dest)
        print(f"[{template_id}] saved {dest.relative_to(REPO_ROOT)}", flush=True)

    _append_log(persona, template_id, prompt, args, saved)
    return {"saved": [str(p) for p in saved]}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.lora.generate")
    p.add_argument("templates", nargs="+", help="Template IDs (e.g. P1 P3).")
    p.add_argument("--persona", default="sierra-frost")
    p.add_argument("--aspect", default=None)
    p.add_argument("--lora-scale", type=float, default=1.0)
    p.add_argument("--guidance", type=float, default=3.5)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    _load_env()

    if args.dry_run:
        for tid in args.templates:
            r = generate(args.persona, tid, aspect_ratio=args.aspect, lora_scale=args.lora_scale, guidance=args.guidance, dry_run=True)
            print(f"\n=== {tid} (DRY RUN) ===")
            print("prompt:", r["prompt"][:200] + "...")
            for k, v in r["args"].items():
                if isinstance(v, str) and len(v) > 120:
                    v = v[:120] + "..."
                print(f"  {k}: {v}")
        return 0

    for tid in args.templates:
        try:
            generate(args.persona, tid, aspect_ratio=args.aspect, lora_scale=args.lora_scale, guidance=args.guidance)
        except Exception as e:
            print(f"[{tid}] FAILED: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
