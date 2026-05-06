"""Curate reference images and write captions for a Sierra LoRA training run.

Usage:
    python -m tools.lora.select_and_prepare \\
        --persona sierra-frost \\
        --trigger SIERRA_FROST_V1 \\
        --output tools/lora/training_set

This walks `personas/<persona>/content-queue/*.png`, lets you (interactively
or via --auto) include/exclude each, center-crops to 1024x1024, generates
a caption from the matching prompt in the generation log (best-effort
parser), and writes the pair as `<n>.png + <n>.txt` to the output dir.
The result is a directory ready to zip and upload to Replicate.

We keep this lightweight (stdlib + Pillow only). Pillow is added to
tools/lora/requirements.txt.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import Iterable

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _content_queue(persona: str) -> pathlib.Path:
    return REPO_ROOT / "personas" / persona / "content-queue"


def _generation_log(persona: str) -> pathlib.Path:
    return REPO_ROOT / "personas" / persona / "generation-log.md"


_PROMPT_BLOCK_RE = re.compile(
    r"### (P\d+)[^\n]*\n(?:.*?\n)*?- pose:\s*([^\n]+)",
    re.MULTILINE,
)


def parse_log_poses(log_path: pathlib.Path) -> dict[str, str]:
    """Return a dict of template_id -> short pose description (best-effort)."""
    if not log_path.is_file():
        return {}
    text = log_path.read_text()
    return {m.group(1): m.group(2).strip() for m in _PROMPT_BLOCK_RE.finditer(text)}


def caption_for(image: pathlib.Path, trigger: str, poses: dict[str, str]) -> str:
    """Compose a Replicate-style caption from filename + pose info.

    Caption rules from PLAN.md:
    - Trigger token first, no description of face/body
    - Wardrobe + setting + lighting only, ~8-20 words
    """
    # Filenames look like 2026-05-06_P7_v1.png
    stem = image.stem
    parts = stem.split("_")
    template = next((p for p in parts if re.fullmatch(r"P\d+", p)), None)
    pose = poses.get(template, "") if template else ""
    pose_short = pose.split(",")[0].strip()  # first phrase of pose
    if not pose_short:
        pose_short = "candid editorial portrait"
    return f"{trigger}, {pose_short}, soft natural lighting, polished editorial"


def center_crop_square(src: pathlib.Path, dst: pathlib.Path, size: int = 1024) -> None:
    from PIL import Image  # local import so the rest of the module still imports

    im = Image.open(src)
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)
    im.convert("RGB").save(dst, format="PNG", optimize=True)


def iter_candidates(persona: str, exts: Iterable[str] = (".png", ".jpg", ".jpeg")) -> list[pathlib.Path]:
    cq = _content_queue(persona)
    if not cq.is_dir():
        return []
    return sorted(p for p in cq.iterdir() if p.suffix.lower() in exts)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--persona", default="sierra-frost")
    p.add_argument("--trigger", default="SIERRA_FROST_V1")
    p.add_argument("--output", type=pathlib.Path, default=pathlib.Path("tools/lora/training_set"))
    p.add_argument("--auto", action="store_true", help="Skip interactive include/exclude; use everything.")
    p.add_argument("--max", type=int, default=20)
    args = p.parse_args(argv)

    candidates = iter_candidates(args.persona)
    if not candidates:
        print(f"No images found under personas/{args.persona}/content-queue/", file=sys.stderr)
        return 1

    poses = parse_log_poses(_generation_log(args.persona))
    args.output.mkdir(parents=True, exist_ok=True)

    selected: list[pathlib.Path] = []
    for img in candidates:
        if args.auto:
            selected.append(img)
            continue
        ans = input(f"include {img.relative_to(REPO_ROOT)}? [Y/n/q] ").strip().lower()
        if ans == "q":
            break
        if ans in ("", "y", "yes"):
            selected.append(img)
        if len(selected) >= args.max:
            break
    selected = selected[: args.max]
    if not selected:
        print("No images selected; nothing to do.", file=sys.stderr)
        return 1

    print(f"Preparing {len(selected)} training images → {args.output}")
    for i, src in enumerate(selected, start=1):
        dst_img = args.output / f"img_{i:03d}.png"
        dst_cap = args.output / f"img_{i:03d}.txt"
        center_crop_square(src, dst_img)
        cap = caption_for(src, args.trigger, poses)
        dst_cap.write_text(cap + "\n")
        print(f"  {dst_img.name} ← {src.name}  |  {cap}")

    # Roll up into a single zip for Replicate upload.
    import zipfile

    zip_path = args.output.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(args.output.iterdir()):
            zf.write(f, arcname=f.name)
    print(f"\nZipped: {zip_path}  ({zip_path.stat().st_size // 1024} KB)")
    print(f"Upload to Replicate via:\n  python -m tools.lora.train --zip {zip_path} --trigger {args.trigger}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
