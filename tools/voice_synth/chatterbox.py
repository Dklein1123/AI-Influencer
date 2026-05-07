"""Chatterbox TTS wrapper (resemble-ai/chatterbox-multilingual on Replicate).

Drop-in alternative to `tools.voice_synth.client` (ElevenLabs). Same
interface, ~3x cheaper at scale, MIT license. Beats ElevenLabs in 63.75%
blind A/B per Podonos study (see docs/research/ai-influencer-community.md).

Voice clone: Chatterbox is zero-shot from a 10s reference clip. To match
Sierra's locked Brielle voice, host a 10s Brielle reference clip somewhere
URL-accessible (Supabase Storage works) and set:

    SIERRA_VOICE_REFERENCE_URL=https://gmjnprjeffcdwlkripux.supabase.co/...wav

Without a reference, Chatterbox falls back to a default voice — usable
for ad-hoc tests but NOT for production Sierra reels.

Caveat: 300-char text limit per call. For longer copy, the
`synthesize_chunks` function fan-outs across calls.

Watermark note: Chatterbox embeds an inaudible Perth watermark for
provenance tracking. This is a feature, not a bug — disclose to brand
partners during pitches.

Usage:
    from tools.voice_synth import chatterbox
    chatterbox.synthesize("Hello world.", output_path=Path("vo.mp3"))
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import tempfile
from typing import Iterable

# Two flavors:
#   "resemble-ai/chatterbox"             — English-only, no length cap.
#                                          DEFAULT for Sierra (English audience).
#   "resemble-ai/chatterbox-multilingual" — 23 languages, 300-char cap per call.
#
# Pin versions to avoid 404 when calling `replicate.run("owner/name")`.
# Bump when Resemble ships a new version worth testing.
MODELS = {
    "en":   ("resemble-ai/chatterbox",
             "1b8422bc49635c20d0a84e387ed20879c0dd09254ecdb4e75dc4bec10ff94e97"),
    "multi": ("resemble-ai/chatterbox-multilingual",
              "9cfba4c265e685f840612be835424f8c33bdee685d7466ece7684b0d9d4c0b1c"),
}


def _model_ref(flavor: str = "en") -> str:
    name, ver = MODELS[flavor]
    return f"{name}:{ver}"


def _replicate_token() -> str:
    tok = os.environ.get("REPLICATE_API_TOKEN")
    if not tok:
        raise RuntimeError(
            "REPLICATE_API_TOKEN missing — needed to call Chatterbox. "
            "Add to ~/.AI-Influencer.env."
        )
    return tok


def _ref_url() -> str | None:
    """Returns a configured Brielle reference URL or None."""
    return os.environ.get("SIERRA_VOICE_REFERENCE_URL") or None


def synthesize(
    text: str,
    *,
    output_path: pathlib.Path,
    reference_audio: str | None = None,
    language: str = "en",
    flavor: str | None = None,
    cfg_weight: float = 0.5,
    temperature: float = 0.8,
    exaggeration: float = 0.5,
    seed: int = 0,
) -> pathlib.Path:
    """Generate audio for `text` via Chatterbox; save to `output_path`.

    Defaults match Sierra's tuned ElevenLabs band:
      - cfg_weight 0.5  (Chatterbox calls this "pace"; 0.5 is conversational)
      - temperature 0.8 (default; lower = more deterministic)
      - exaggeration 0.5 (neutral; Sierra is dry, don't push above 0.6)

    `flavor`:
      - 'en' (default) — uses resemble-ai/chatterbox, English-only,
        no length cap, params: prompt + audio_prompt
      - 'multi' — uses resemble-ai/chatterbox-multilingual, 23 languages,
        300-char cap per call, params: text + reference_audio + language

    Use 'multi' only when language != 'en'; auto-selects.
    """
    use_flavor = flavor or ("multi" if language != "en" else "en")
    _replicate_token()
    import replicate

    if use_flavor == "multi":
        if len(text) > 300:
            raise ValueError(
                f"chatterbox-multilingual 300-char limit exceeded "
                f"({len(text)} chars). Use synthesize_chunks()."
            )
        args = {
            "text": text,
            "language": language,
            "cfg_weight": cfg_weight,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "seed": seed,
        }
        ref = reference_audio or _ref_url()
        if ref:
            args["reference_audio"] = ref
    else:
        args = {
            "prompt": text,
            "cfg_weight": cfg_weight,
            "temperature": temperature,
            "exaggeration": exaggeration,
            "seed": seed,
        }
        ref = reference_audio or _ref_url()
        if ref:
            args["audio_prompt"] = ref

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = replicate.run(_model_ref(use_flavor), input=args)
    # replicate.run returns a FileOutput-ish object or URL.
    if hasattr(output, "read"):
        output_path.write_bytes(output.read())
    elif isinstance(output, str):
        import httpx
        with httpx.stream("GET", output, timeout=120) as r:
            r.raise_for_status()
            with output_path.open("wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
    elif hasattr(output, "__iter__"):
        first = next(iter(output))
        if hasattr(first, "read"):
            output_path.write_bytes(first.read())
        else:
            import httpx
            with httpx.stream("GET", str(first), timeout=120) as r:
                r.raise_for_status()
                with output_path.open("wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
    else:
        raise RuntimeError(f"Unexpected Chatterbox output type: {type(output)}")
    return output_path


def synthesize_chunks(
    chunks: Iterable[tuple[float, float, str]],
    *,
    output_path: pathlib.Path,
    reference_audio: str | None = None,
    **kwargs,
) -> pathlib.Path:
    """Synthesize per-chunk; mix into a single track at exact timings.

    Mirrors `tools.voice_synth.client.synthesize_chunks` exactly so
    `tools.assembly.from_trend` can swap providers via a single flag.

    Each chunk is rendered independently (respecting the 300-char limit
    by splitting on sentence boundaries if needed) and placed at its
    `start` second in the output.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks = list(chunks)
    if not chunks:
        raise ValueError("synthesize_chunks needs at least one chunk")
    total_duration = max(end for _, end, _ in chunks)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = pathlib.Path(tmp)
        per_chunk_files: list[tuple[float, pathlib.Path]] = []
        for i, (start, _end, text) in enumerate(chunks):
            wav = tmp_dir / f"chunk_{i:03d}.mp3"
            # Split chunks > 300 chars on sentence boundaries.
            if len(text) > 300:
                parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", text) if p.strip()]
                sub_files = []
                for j, p in enumerate(parts):
                    if len(p) > 300:
                        # Hard truncate fallback (shouldn't happen at our scale)
                        p = p[:297] + "..."
                    sub = tmp_dir / f"chunk_{i:03d}_{j:02d}.mp3"
                    synthesize(p, output_path=sub, reference_audio=reference_audio, **kwargs)
                    sub_files.append(sub)
                # Concat the sub-files into one chunk mp3.
                concat_list = tmp_dir / f"chunk_{i:03d}_list.txt"
                concat_list.write_text("\n".join(f"file '{p}'" for p in sub_files))
                subprocess.run(
                    ["ffmpeg", "-y", "-loglevel", "error",
                     "-f", "concat", "-safe", "0", "-i", str(concat_list),
                     "-c", "copy", str(wav)],
                    check=True,
                )
            else:
                synthesize(text, output_path=wav, reference_audio=reference_audio, **kwargs)
            per_chunk_files.append((start, wav))

        # Mix chunks at their start times.
        inputs: list[str] = []
        filt_parts: list[str] = []
        labels: list[str] = []
        for i, (start, wav) in enumerate(per_chunk_files):
            inputs.extend(["-i", str(wav)])
            filt_parts.append(f"[{i}:a]adelay={int(start*1000)}|{int(start*1000)}[d{i}]")
            labels.append(f"[d{i}]")
        merge = "".join(labels) + f"amix=inputs={len(per_chunk_files)}:duration=longest:dropout_transition=0[out]"
        filt = ";".join(filt_parts + [merge])
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            *inputs,
            "-filter_complex", filt,
            "-map", "[out]",
            "-t", f"{total_duration:.3f}",
            "-c:a", "pcm_s16le", "-ar", "48000",
            str(output_path),
        ]
        subprocess.run(cmd, check=True)
    return output_path


# CLI for quick smoke-tests
def _cli() -> int:
    import argparse, sys
    p = argparse.ArgumentParser(description="Chatterbox TTS smoke test")
    p.add_argument("text")
    p.add_argument("--out", default="/tmp/chatterbox_test.mp3")
    p.add_argument("--ref", default=None, help="reference audio URL for voice clone")
    args = p.parse_args()
    out = pathlib.Path(args.out)
    synthesize(args.text, output_path=out, reference_audio=args.ref)
    print(f"wrote {out} ({out.stat().st_size:,} bytes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
