"""Submit a Sierra LoRA training job to Replicate.

Usage:
    # First time:
    pip install -r tools/lora/requirements.txt
    # Add REPLICATE_API_TOKEN=r8_... to ~/.AI-Influencer.env
    # Curate training set:
    python -m tools.lora.select_and_prepare --auto
    # Kick off training:
    python -m tools.lora.train --zip tools/lora/training_set.zip --owner YOUR_REPLICATE_USERNAME

The script submits to `ostris/flux-dev-lora-trainer` with the hyperparameters
from PLAN.md. It prints the training run URL so you can watch progress in
the Replicate web UI, then polls for completion and prints the final model ID
which becomes the inference target.

Stays small on purpose. The gnarly part of LoRA training (dataset prep,
captioning, post-train evaluation) lives in sibling scripts.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--zip", type=pathlib.Path, required=True, help="Training set zip from select_and_prepare.")
    p.add_argument("--trigger", default="SIERRA_FROST_V1")
    p.add_argument("--owner", required=True, help="Your Replicate username (where the trained model will live).")
    p.add_argument("--name", default="sierra-frost-v1", help="Destination model name (created if absent).")
    p.add_argument("--steps", type=int, default=1750)
    p.add_argument("--lora-rank", type=int, default=32)
    p.add_argument("--learning-rate", default="1e-4")
    p.add_argument("--resolution", type=int, default=1024)
    p.add_argument("--caption-dropout-rate", type=float, default=0.05)
    p.add_argument("--no-wait", action="store_true", help="Submit and exit, don't poll.")
    args = p.parse_args(argv)

    _load_env()
    if not os.environ.get("REPLICATE_API_TOKEN"):
        print(
            "REPLICATE_API_TOKEN missing. Get one at https://replicate.com/account/api-tokens "
            "and add `REPLICATE_API_TOKEN=r8_...` to ~/.AI-Influencer.env",
            file=sys.stderr,
        )
        return 2

    if not args.zip.is_file():
        print(f"zip not found: {args.zip}", file=sys.stderr)
        return 2

    try:
        import replicate  # noqa: F401
    except ImportError:
        print("`replicate` package missing. Run: pip install -r tools/lora/requirements.txt", file=sys.stderr)
        return 2

    import replicate

    destination = f"{args.owner}/{args.name}"

    print(f"Uploading training zip ({args.zip.stat().st_size // 1024} KB)...")
    with args.zip.open("rb") as f:
        training = replicate.trainings.create(
            destination=destination,
            version="ostris/flux-dev-lora-trainer:e440909d3512c31646ee2e0c7d6f6f4923224863a6a10c494606e79fb5844497",
            input={
                "input_images": f,
                "trigger_word": args.trigger,
                "steps": args.steps,
                "lora_rank": args.lora_rank,
                "learning_rate": args.learning_rate,
                "batch_size": 1,
                "resolution": args.resolution,
                "caption_dropout_rate": args.caption_dropout_rate,
                "autocaption": False,  # we provide captions in the zip
            },
        )

    print(f"Training submitted. Watch live at: https://replicate.com/p/{training.id}")
    print(f"Destination: replicate.com/{destination}")

    if args.no_wait:
        print("\nReturning immediately (--no-wait).")
        print(f"To check status later:\n  replicate trainings get {training.id}")
        return 0

    print("\nPolling every 30s. Typical run ≈ 22–28 min...")
    while True:
        training.reload()
        print(f"  status={training.status}  elapsed={int(training.metrics.get('elapsed_seconds', 0))}s")
        if training.status in ("succeeded", "failed", "canceled"):
            break
        time.sleep(30)

    if training.status != "succeeded":
        print(f"\nTraining ended in status: {training.status}", file=sys.stderr)
        if training.error:
            print(f"Error: {training.error}", file=sys.stderr)
        return 3

    print("\n✅ Training complete.")
    print(f"  Inference model: replicate.com/{destination}")
    print(f"  Trigger token: {args.trigger}")
    print("\nNext: copy the version hash from the model page into ~/.AI-Influencer.env as")
    print("  SIERRA_LORA_VERSION=<owner>/<name>:<sha>")
    print("then run: python -m tools.lora.generate <template_id>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
