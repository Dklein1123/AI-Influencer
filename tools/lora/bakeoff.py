"""Run the LoRA v1 bake-off.

Generates the 4-prompt × 2-LoRA-scale matrix (8 LoRA images) on the
trained Sierra LoRA and downloads them all to
personas/sierra-frost/lora-bakeoff/. Then builds a 2x6 contact sheet
combining the 8 LoRA outputs with the 4 existing Soul-2 references
(P1, P7, P12, PROFILE) for side-by-side review.

Run this immediately after the training succeeds:

    python -m tools.lora.bakeoff

Requires:
    REPLICATE_API_TOKEN
    SIERRA_LORA_VERSION=dklein1123/sierra-frost-v1:<sha>
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BAKEOFF_DIR = REPO_ROOT / "personas" / "sierra-frost" / "lora-bakeoff"
SOUL2_REFS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "content-queue"

PROMPTS = {
    "B1_bedroom": "SIERRA_FROST_V1, sitting at edge of bed, navy midi dress with cream blazer, scandinavian bedroom, soft morning light, polished editorial",
    "B2_palmbeach": "SIERRA_FROST_V1, walking forward at golden hour, white linen sundress, Palm Beach waterfront walkway, palm trees, white classical architecture, polished editorial",
    "B3_cafe": "SIERRA_FROST_V1, looking up from MacBook directly to camera, navy dress and cream blazer, marble cafe table, soft window light, polished editorial",
    "B4_profile": "SIERRA_FROST_V1, three-quarter profile portrait looking thoughtfully off to the side, hair tucked behind one ear, soft window light, intimate, polished editorial",
}

# Soul 2 references already in the content-queue (for the contact sheet).
SOUL2_REFS = {
    "B1_bedroom": "2026-05-06_P1_v1.png",
    "B2_palmbeach": "2026-05-06_P7_v1.png",
    "B3_cafe": "2026-05-06_P12_v1.png",
    "B4_profile": "2026-05-06_PROFILE_v1.png",
}

LORA_SCALES = (1.0, 0.85)


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


def run() -> int:
    _load_env()
    version = os.environ.get("SIERRA_LORA_VERSION")
    if not version:
        print("SIERRA_LORA_VERSION missing. Train the LoRA first.", file=sys.stderr)
        return 2

    try:
        import replicate
        import requests
    except ImportError:
        print("pip install -r tools/lora/requirements.txt", file=sys.stderr)
        return 2

    BAKEOFF_DIR.mkdir(parents=True, exist_ok=True)

    submitted: list[tuple[str, float, object]] = []
    for slot, prompt in PROMPTS.items():
        for scale in LORA_SCALES:
            print(f"Submitting {slot} (lora_scale={scale})...", flush=True)
            args = {
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "lora_scale": scale,
                "guidance": 3.5,
                "num_inference_steps": 28,
                "num_outputs": 1,
                "output_format": "png",
                "output_quality": 95,
            }
            for attempt in range(5):
                try:
                    pred = replicate.predictions.create(version=version, input=args)
                    break
                except replicate.exceptions.ReplicateError as e:
                    if "429" in str(e) or "throttled" in str(e).lower():
                        wait = 12 + attempt * 4
                        print(f"  rate-limited, sleeping {wait}s...", flush=True)
                        time.sleep(wait)
                        continue
                    raise
            else:
                raise RuntimeError(f"giving up on {slot} s={scale} after 5 throttle retries")
            submitted.append((slot, scale, pred))
            # Stay polite under the 6/min + burst 1 throttle.
            time.sleep(11)

    print(f"\nSubmitted {len(submitted)} predictions. Polling...")
    saved: dict[tuple[str, float], pathlib.Path] = {}
    while submitted:
        still_running = []
        for slot, scale, pred in submitted:
            pred.reload()
            if pred.status in ("succeeded", "failed", "canceled"):
                if pred.status == "succeeded":
                    output = pred.output
                    url = output[0] if isinstance(output, list) else output
                    if hasattr(url, "url"):
                        url = url.url
                    dest = BAKEOFF_DIR / f"{slot}_lora_s{int(scale*100):03d}.png"
                    print(f"  {slot} s={scale} → {dest.name}", flush=True)
                    with requests.get(url, stream=True, timeout=120) as r:
                        r.raise_for_status()
                        with dest.open("wb") as f:
                            for chunk in r.iter_content(chunk_size=1 << 14):
                                f.write(chunk)
                    saved[(slot, scale)] = dest
                else:
                    print(f"  {slot} s={scale} → {pred.status}: {pred.error}", file=sys.stderr)
            else:
                still_running.append((slot, scale, pred))
        submitted = still_running
        if submitted:
            time.sleep(5)

    if not saved:
        print("No images saved; aborting.", file=sys.stderr)
        return 3

    # Build a 4-row × 3-column contact sheet (Soul 2 | LoRA s=1.0 | LoRA s=0.85)
    inputs: list[str] = []
    for slot in PROMPTS:
        soul = SOUL2_REFS_DIR / SOUL2_REFS[slot]
        l10 = saved.get((slot, 1.0))
        l085 = saved.get((slot, 0.85))
        if not (soul.is_file() and l10 and l085):
            continue
        inputs.extend(["-i", str(soul), "-i", str(l10), "-i", str(l085)])

    n = len(inputs) // 2
    if n == 0:
        print("Couldn't build contact sheet — missing inputs.", file=sys.stderr)
        return 0
    # Each row: 3 images × scale=288. Layout 3 cols × N rows.
    filt_parts = [f"[{i}:v]scale=320:-1[v{i}]" for i in range(n)]
    rows = []
    for r_idx in range(n // 3):
        a, b, c = r_idx * 3, r_idx * 3 + 1, r_idx * 3 + 2
        rows.append(f"[v{a}][v{b}][v{c}]hstack=inputs=3[r{r_idx}]")
    stack = "".join(f"[r{i}]" for i in range(n // 3)) + f"vstack=inputs={n // 3}"
    filt = ";".join(filt_parts + rows + [stack])

    contact = REPO_ROOT / "personas" / "sierra-frost" / "lora-bakeoff-contact.png"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt, "-frames:v", "1", str(contact)]
    subprocess.run(cmd, check=True)
    print(f"\nContact sheet: {contact}")
    print("\nReview the contact sheet, fill in lora-bakeoff-rubric.md §Results,")
    print("then commit the rubric + the contact sheet.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
