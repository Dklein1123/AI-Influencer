"""Thin ElevenLabs API wrapper.

Auth via `ELEVEN_API_KEY` (or the older `ELEVENLABS_API_KEY`) in
`~/.AI-Influencer.env`. We use the REST API directly with httpx rather
than the official SDK so the dep tree stays minimal — the SDK pulls in
pydantic + a deep audio stack we don't need for synth-and-save.
"""

from __future__ import annotations

import os
import pathlib
from typing import Iterable

import httpx

BASE_URL = "https://api.elevenlabs.io/v1"


def _api_key() -> str:
    key = os.environ.get("ELEVEN_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError(
            "ELEVEN_API_KEY missing. Add to ~/.AI-Influencer.env "
            "(get one at elevenlabs.io/app/settings/api-keys)."
        )
    return key


def _headers(json: bool = False) -> dict[str, str]:
    h = {"xi-api-key": _api_key()}
    if json:
        h["Content-Type"] = "application/json"
    h["Accept"] = "audio/mpeg"
    return h


def list_voices() -> list[dict]:
    """Return the user's voice library."""
    r = httpx.get(f"{BASE_URL}/voices", headers={"xi-api-key": _api_key()}, timeout=30)
    r.raise_for_status()
    return r.json().get("voices", [])


def synthesize(
    text: str,
    *,
    voice_id: str,
    output_path: pathlib.Path,
    model: str = "eleven_multilingual_v2",
    stability: float = 0.55,
    similarity_boost: float = 0.80,
    style: float = 0.20,
    use_speaker_boost: bool = True,
    output_format: str = "mp3_44100_128",
) -> pathlib.Path:
    """Generate audio for `text` using `voice_id`, save to `output_path`.

    Default settings come from `voice-profile.md §10` (Sierra's tuned
    parameter band: stability 0.55, similarity 0.80, style 0.20).

    Returns the path to the saved file.
    """
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        },
    }
    url = f"{BASE_URL}/text-to-speech/{voice_id}?output_format={output_format}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("POST", url, headers=_headers(json=True), json=payload, timeout=120) as r:
        r.raise_for_status()
        with output_path.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return output_path


def synthesize_chunks(
    chunks: Iterable[tuple[float, float, str]],
    *,
    voice_id: str,
    output_path: pathlib.Path,
    **kwargs,
) -> pathlib.Path:
    """Synthesize a list of (start, end, text) chunks and assemble them
    into a single audio file with precise timing using ffmpeg.

    Each chunk is rendered independently and placed at its `start` second
    in the output, padded with silence between/around chunks. This keeps
    the spoken voice aligned to the on-screen subtitle timing in
    `tools/assembly/`.
    """
    import subprocess
    import tempfile

    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks = list(chunks)
    if not chunks:
        raise ValueError("synthesize_chunks needs at least one chunk")
    total_duration = max(end for _, end, _ in chunks)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = pathlib.Path(tmp)
        per_chunk_files: list[tuple[float, float, pathlib.Path]] = []
        for i, (start, end, text) in enumerate(chunks):
            wav = tmp_dir / f"chunk_{i:03d}.mp3"
            synthesize(text, voice_id=voice_id, output_path=wav, **kwargs)
            per_chunk_files.append((start, end, wav))

        # Build ffmpeg filter graph: each chunk is delayed by start*1000ms,
        # all chunks mixed into a single stream of length total_duration.
        inputs: list[str] = []
        filt_parts: list[str] = []
        labels: list[str] = []
        for i, (start, _end, wav) in enumerate(per_chunk_files):
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
