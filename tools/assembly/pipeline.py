"""Core assembly pipeline.

Takes a visual source (image or video), an optional voiceover, an optional
music bed, and a script (with per-line timestamps) and produces a TikTok /
IG Reels ready 1080x1920 9:16 mp4 — H.264 + AAC, 30fps, loudness normalized
to -14 LUFS, burn-in subtitles via libass.

Design notes:

- We use libass (ffmpeg `subtitles=` filter) for subtitle rendering rather
  than `drawtext` because we need styled multi-chunk text with per-chunk
  timing. ASS gives us that with a single filter call.
- Audio mixing is sidechain-compressed: the music bed is ducked to ~-22 dB
  under the voiceover. Source-video audio (e.g. ambient room tone from
  Seedance) is mixed in at -30 dB if both are present, else preserved.
- Final loudness target is -14 LUFS / -1 dBTP per TikTok's normalization
  spec. This keeps the post at roughly the same volume as everything else
  on the FYP.
"""

from __future__ import annotations

import dataclasses
import pathlib
import re
import shlex
import subprocess
import textwrap
from typing import Sequence

# Module shape: keep absolute path so the same code works whether you run
# the CLI from the repo root, the tools/ dir, or anywhere else.
DEFAULT_FONT_PATH = pathlib.Path(
    "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Black.ttf"
)
DEFAULT_FONT_NAME = "Roboto Black"

OUT_W = 1080
OUT_H = 1920
OUT_FPS = 30


@dataclasses.dataclass(frozen=True)
class Chunk:
    """One timed subtitle chunk."""

    start: float
    end: float
    text: str


_CHUNK_RE = re.compile(
    r"^\s*\[(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\]\s*(.*\S)\s*$"
)


def parse_script(script_text: str) -> list[Chunk]:
    """Parse the `[start-end] TEXT` line format used in content-units.

    Examples of accepted lines:
        [00.0-02.0] UNPOPULAR OPINION:
        [02.0–05.5] STANDARDS AREN'T

    Lines not matching the pattern are joined onto the previous chunk
    (so multi-line chunks work). Blank lines reset.
    """
    chunks: list[Chunk] = []
    cur: Chunk | None = None
    for raw in script_text.splitlines():
        line = raw.strip()
        if not line:
            if cur is not None:
                chunks.append(cur)
                cur = None
            continue
        m = _CHUNK_RE.match(line)
        if m:
            if cur is not None:
                chunks.append(cur)
            start, end, text = float(m.group(1)), float(m.group(2)), m.group(3)
            cur = Chunk(start=start, end=end, text=text)
        elif cur is not None:
            # Continuation line for the same chunk.
            cur = dataclasses.replace(cur, text=f"{cur.text}\\N{line}")
    if cur is not None:
        chunks.append(cur)
    return chunks


def _ass_time(seconds: float) -> str:
    """Convert seconds → ASS H:MM:SS.cs timestamp."""
    cs = int(round(seconds * 100))
    h, rem = divmod(cs, 360_000)
    m, rem = divmod(rem, 6_000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def build_ass(
    chunks: Sequence[Chunk],
    *,
    font_name: str = DEFAULT_FONT_NAME,
    font_size: int = 96,
    margin_v_pct: float = 0.30,  # 30% from bottom = ~70% from top of frame
    play_res_x: int = OUT_W,
    play_res_y: int = OUT_H,
) -> str:
    """Build a libass-compatible .ass subtitle file as a string.

    Style choices match the voice-profile §8 spec:
    - Bold sans (Roboto Black ~ Anton-equivalent)
    - White fill, thick black outline for stop-scroll legibility
    - Centered horizontally, lower-third vertically
    """
    margin_v = int(play_res_y * margin_v_pct)
    header = textwrap.dedent(
        f"""\
        [Script Info]
        ScriptType: v4.00+
        PlayResX: {play_res_x}
        PlayResY: {play_res_y}
        ScaledBorderAndShadow: yes

        [V4+ Styles]
        Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
        Style: Sierra,{font_name},{font_size},&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,8,3,2,80,80,{margin_v},1

        [Events]
        Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        """
    )
    lines = [header]
    for c in chunks:
        text = c.text.replace("\n", "\\N").replace(",", r"\,")
        lines.append(
            f"Dialogue: 0,{_ass_time(c.start)},{_ass_time(c.end)},Sierra,,0,0,0,,{text}"
        )
    return "\n".join(lines) + "\n"


def _video_filter(visual_is_image: bool, duration: float) -> str:
    """Build the video filter chain.

    For images: scale, pad to 1080x1920 9:16, slow ken-burns zoom for life.
    For videos: scale + pad only — let the original motion carry the piece.
    """
    fit = (
        f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H},setsar=1"
    )
    if visual_is_image:
        # Slow ken-burns: 1.0 → 1.06 over the duration. zoompan needs frames.
        n_frames = int(duration * OUT_FPS)
        kb = (
            f"zoompan=z='min(zoom+0.0002,1.06)':d={n_frames}"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":s={OUT_W}x{OUT_H}:fps={OUT_FPS}"
        )
        return f"{kb},{fit},format=yuv420p"
    return f"{fit},fps={OUT_FPS},format=yuv420p"


def _audio_graph(
    has_vo: bool,
    has_music: bool,
    has_source_audio: bool,
) -> tuple[str, str]:
    """Build the audio filter graph + return the final audio label.

    Inputs labels in the assembled ffmpeg invocation:
      [vid] = visual stream, possibly with audio at [vid:a]
      [vo]  = voiceover wav
      [mus] = music bed

    Returns: (filter_complex_audio, final_label)
    """
    nodes: list[str] = []
    sources: list[str] = []

    if has_vo:
        # We split the cleaned-up voiceover so it can both trigger the music
        # ducking sidechain AND survive into the final mix.
        nodes.append(
            "[vo:a]aresample=48000,aformat=channel_layouts=stereo,"
            "highpass=f=80,lowpass=f=12000,acompressor=threshold=-18dB:ratio=3:attack=10:release=120,volume=2.5dB,"
            "asplit=2[VO][VO_SC]"
        )
        sources.append("[VO]")
    if has_music:
        if has_vo:
            # Sidechain-duck the music using the dedicated split copy.
            nodes.append(
                "[mus:a]aresample=48000,aformat=channel_layouts=stereo,"
                "volume=-12dB[MUS_PRE]"
            )
            nodes.append(
                "[MUS_PRE][VO_SC]sidechaincompress=threshold=0.08:ratio=8:attack=10:release=400[MUS_DUCKED]"
            )
            sources.append("[MUS_DUCKED]")
        else:
            nodes.append("[mus:a]aresample=48000,aformat=channel_layouts=stereo,volume=-9dB[MUS]")
            sources.append("[MUS]")
    if has_source_audio:
        # Keep source ambient at low level if we have other layers, full-bore otherwise.
        if has_vo or has_music:
            nodes.append("[vid:a]aresample=48000,aformat=channel_layouts=stereo,volume=-22dB[SRC]")
        else:
            nodes.append("[vid:a]aresample=48000,aformat=channel_layouts=stereo[SRC]")
        sources.append("[SRC]")

    if not sources:
        return "", ""  # caller should -an

    if len(sources) == 1:
        nodes.append(f"{sources[0]}loudnorm=I=-14:TP=-1:LRA=11[AOUT]")
    else:
        srcs = "".join(sources)
        nodes.append(
            f"{srcs}amix=inputs={len(sources)}:duration=longest:dropout_transition=0,"
            f"loudnorm=I=-14:TP=-1:LRA=11[AOUT]"
        )
    return ";".join(nodes), "[AOUT]"


def assemble(
    *,
    visual: pathlib.Path,
    output: pathlib.Path,
    voiceover: pathlib.Path | None = None,
    music: pathlib.Path | None = None,
    script_text: str | None = None,
    duration: float | None = None,
    font_path: pathlib.Path | None = None,
    font_size: int = 96,
    dry_run: bool = False,
) -> dict:
    """Run the assembly. Returns a dict summary; raises CalledProcessError on ffmpeg failure."""
    visual = pathlib.Path(visual).resolve()
    if not visual.is_file():
        raise FileNotFoundError(f"visual not found: {visual}")

    visual_is_image = visual.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    has_source_audio = False
    if not visual_is_image:
        # Probe for an audio stream.
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(visual)],
            capture_output=True, text=True, check=False,
        )
        has_source_audio = bool(probe.stdout.strip())

    # Resolve duration: explicit override > video duration > 15s default.
    if duration is None:
        if visual_is_image:
            duration = 15.0
        else:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(visual)],
                capture_output=True, text=True, check=True,
            )
            duration = float(probe.stdout.strip())

    has_vo = voiceover is not None
    has_music = music is not None

    # Build subtitle file if a script was given.
    ass_path: pathlib.Path | None = None
    if script_text:
        chunks = parse_script(script_text)
        if chunks:
            ass_text = build_ass(
                chunks, font_name=DEFAULT_FONT_NAME, font_size=font_size
            )
            ass_path = output.with_suffix(".ass")
            ass_path.write_text(ass_text)

    # ffmpeg invocation.
    inputs: list[str] = []
    input_idx_map: dict[str, int] = {}

    def add_input(args: list[str], label: str) -> int:
        idx = len(input_idx_map)
        input_idx_map[label] = idx
        inputs.extend(args)
        return idx

    # Visual input.
    if visual_is_image:
        add_input(["-loop", "1", "-t", f"{duration:.3f}", "-i", str(visual)], "vid")
    else:
        add_input(["-t", f"{duration:.3f}", "-i", str(visual)], "vid")
    if has_vo:
        add_input(["-i", str(voiceover)], "vo")
    if has_music:
        add_input(["-i", str(music)], "mus")

    # Build video filter chain. Use [0:v] for the visual stream.
    vf = _video_filter(visual_is_image, duration)
    video_chain = f"[{input_idx_map['vid']}:v]{vf}[V0]"

    # Subtitle filter (operates on labelled video stream).
    if ass_path is not None:
        sub_filter = (
            f"[V0]subtitles=filename='{ass_path}'"
            f":fontsdir='{(font_path or DEFAULT_FONT_PATH).parent}'"
            f"[VOUT]"
        )
    else:
        sub_filter = "[V0]copy[VOUT]"

    audio_graph, audio_label = _audio_graph(
        has_vo=has_vo,
        has_music=has_music,
        has_source_audio=has_source_audio,
    )

    # Stitch filter_complex.
    fc_parts = [video_chain, sub_filter]
    if audio_graph:
        # Replace [vo:a]/[mus:a]/[vid:a] symbolic labels with [N:a] real labels.
        replacements = {
            "[vid:a]": f"[{input_idx_map['vid']}:a]",
        }
        if has_vo:
            replacements["[vo:a]"] = f"[{input_idx_map['vo']}:a]"
        if has_music:
            replacements["[mus:a]"] = f"[{input_idx_map['mus']}:a]"
        ag = audio_graph
        for k, v in replacements.items():
            ag = ag.replace(k, v)
        fc_parts.append(ag)
    filter_complex = ";".join(fc_parts)

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    cmd.extend(inputs)
    cmd.extend(["-filter_complex", filter_complex])
    cmd.extend(["-map", "[VOUT]"])
    if audio_label:
        cmd.extend(["-map", audio_label])
    else:
        cmd.append("-an")
    cmd.extend([
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
        "-r", str(OUT_FPS),
        "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", f"{duration:.3f}",
        str(output),
    ])

    if dry_run:
        return {
            "dry_run": True,
            "duration": duration,
            "visual": str(visual),
            "output": str(output),
            "filter_complex": filter_complex,
            "ffmpeg_cmd": " ".join(shlex.quote(a) for a in cmd),
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(cmd, check=True)
    return {
        "duration": duration,
        "visual": str(visual),
        "output": str(output),
        "subtitles_path": str(ass_path) if ass_path else None,
        "size_bytes": output.stat().st_size,
    }
