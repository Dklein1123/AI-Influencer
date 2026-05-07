"""Image + audio → talking video via Replicate's bytedance/omni-human.

This is the missing piece in Sierra's pipeline. Without it she's a
ken-burns still with a voiceover — i.e. AI-mid TikTok content. With it
she's actually moving her mouth and head while delivering the bit.

The pipeline:
  Sierra still (Replicate Flux + Sierra LoRA + Boreal)
      + Brielle voiceover (ElevenLabs)
      → OmniHuman v1.5 (this module)
      → talking-Sierra mp4 (audio baked in)
      → strip audio → use as visual in tools.assembly.pipeline
      → ffmpeg adds Brielle VO + subs + film grain + title card

Cost: ~$0.10–0.30 per gen (varies w/ duration). Adds to the existing
Replicate spend for the LoRA gen + ElevenLabs synth.

Quality note: OmniHuman v1.5 (ByteDance) is the SOTA in 2026 for
photorealistic single-image-to-talking-head per reviews on
replicate.com/collections/lipsync, GoTranscript Aurora-vs-OmniHuman-
vs-WAN benchmark, and TeamDay 2026 ranking. Beats Hedra (better for
cartoons), Kling (better for body motion), and SadTalker (older).

Usage:
    from tools.generation.lipsync import lipsync_image
    out_mp4 = lipsync_image(
        image=Path("sierra_still.png"),
        audio=Path("brielle_vo.wav"),
        output=Path("sierra_talking.mp4"),
    )
"""

from __future__ import annotations

import os
import pathlib
import subprocess
from typing import Any

REPLICATE_MODEL = "bytedance/omni-human"


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


def _replicate_token() -> str:
    tok = os.environ.get("REPLICATE_API_TOKEN")
    if not tok:
        raise RuntimeError("REPLICATE_API_TOKEN missing — needed for OmniHuman lipsync")
    return tok


def lipsync_image(
    image: pathlib.Path,
    audio: pathlib.Path,
    *,
    output: pathlib.Path,
    strip_audio: bool = True,
) -> pathlib.Path:
    """Generate a talking-head video from a still + audio.

    `strip_audio=True` (default) removes OmniHuman's baked-in audio
    track. Reason: tools.assembly.pipeline.assemble() takes its OWN
    voiceover input and re-mixes it cleanly with subtitles + film
    grain. Letting OmniHuman audio through to the assembler causes
    double-tracking. Pass strip_audio=False if calling outside the
    standard pipeline.

    Returns the output path.
    """
    image = pathlib.Path(image).resolve()
    audio = pathlib.Path(audio).resolve()
    output = pathlib.Path(output)
    if not image.is_file():
        raise FileNotFoundError(image)
    if not audio.is_file():
        raise FileNotFoundError(audio)
    output.parent.mkdir(parents=True, exist_ok=True)

    _replicate_token()
    import replicate

    print(f"[lipsync] omnihuman: {image.name} + {audio.name} (silent={strip_audio}) …", flush=True)
    out = replicate.run(
        REPLICATE_MODEL,
        input={
            "image": image.open("rb"),
            "audio": audio.open("rb"),
        },
    )

    # replicate.run returns a FileOutput object (or list/iter of them).
    if hasattr(out, "read"):
        raw_video = out.read()
    elif isinstance(out, str):
        import httpx
        with httpx.stream("GET", out, timeout=600) as r:
            r.raise_for_status()
            raw_video = b"".join(r.iter_bytes())
    elif hasattr(out, "__iter__"):
        first = next(iter(out))
        if hasattr(first, "read"):
            raw_video = first.read()
        else:
            import httpx
            with httpx.stream("GET", str(first), timeout=600) as r:
                r.raise_for_status()
                raw_video = b"".join(r.iter_bytes())
    else:
        raise RuntimeError(f"Unexpected OmniHuman output type: {type(out)}")

    # Write raw mp4 (with audio).
    with_audio_path = output.with_suffix(".raw.mp4")
    with_audio_path.write_bytes(raw_video)

    if strip_audio:
        # Drop the audio track — assembler adds its own VO + subs + grain.
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(with_audio_path),
             "-c:v", "copy", "-an",
             str(output)],
            check=True,
        )
        with_audio_path.unlink(missing_ok=True)
    else:
        with_audio_path.rename(output)

    print(f"[lipsync] saved {output} ({output.stat().st_size:,} bytes)", flush=True)
    return output


def is_enabled() -> bool:
    return bool(os.environ.get("REPLICATE_API_TOKEN"))


def _cli() -> int:
    import argparse, sys
    p = argparse.ArgumentParser(description="OmniHuman lipsync wrapper for Sierra")
    p.add_argument("--image", required=True, type=pathlib.Path)
    p.add_argument("--audio", required=True, type=pathlib.Path)
    p.add_argument("--out", required=True, type=pathlib.Path)
    p.add_argument("--keep-audio", action="store_true",
                   help="Don't strip OmniHuman's audio (off by default — assembler adds VO)")
    args = p.parse_args()
    out = lipsync_image(args.image, args.audio, output=args.out, strip_audio=not args.keep_audio)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
