"""CLI: python -m tools.assembly --visual VIDEO --vo VO.wav --script SCRIPT.txt --output OUT.mp4

Examples:
    # Pure visual passthrough (no overlays, no replacement audio).
    python -m tools.assembly --visual personas/sierra-frost/content-queue/2026-05-06_P7_v1.mp4 --output /tmp/p7_clean.mp4

    # Full assembly with voiceover, music, and burn-in script.
    python -m tools.assembly \\
        --visual personas/sierra-frost/content-queue/2026-05-06_P7_v1.mp4 \\
        --vo voice/p7_take1.wav \\
        --music music/calm-piano.mp3 \\
        --script personas/sierra-frost/content-units/2026-05-06_P7.script.txt \\
        --output personas/sierra-frost/content-queue/2026-05-06_P7_assembled.mp4

    # Image-driven (slow ken-burns over a still).
    python -m tools.assembly \\
        --visual personas/sierra-frost/content-queue/2026-05-06_P12_v1.png \\
        --vo voice/p12_take1.wav \\
        --script personas/sierra-frost/content-units/2026-05-06_P12.script.txt \\
        --output personas/sierra-frost/content-queue/2026-05-06_P12_assembled.mp4
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from .pipeline import assemble


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.assembly")
    p.add_argument("--visual", required=True, type=pathlib.Path, help="Source video or image (mp4/mov/png/jpg).")
    p.add_argument("--vo", type=pathlib.Path, default=None, help="Voiceover audio (wav/mp3/m4a). Optional.")
    p.add_argument("--music", type=pathlib.Path, default=None, help="Music bed audio. Optional.")
    p.add_argument("--script", type=pathlib.Path, default=None, help="Path to a script file using `[start-end] TEXT` lines.")
    p.add_argument("--script-text", default=None, help="Inline script text (alternative to --script).")
    p.add_argument("--output", required=True, type=pathlib.Path, help="Output mp4.")
    p.add_argument("--duration", type=float, default=None, help="Override output duration in seconds.")
    p.add_argument("--font-size", type=int, default=96, help="Burn-in subtitle font size (default 96 for 1080p output).")
    p.add_argument("--dry-run", action="store_true", help="Print the ffmpeg command without running it.")
    args = p.parse_args(argv)

    script_text: str | None = None
    if args.script and args.script.is_file():
        script_text = args.script.read_text()
    elif args.script_text:
        script_text = args.script_text

    try:
        result = assemble(
            visual=args.visual,
            output=args.output,
            voiceover=args.vo,
            music=args.music,
            script_text=script_text,
            duration=args.duration,
            font_size=args.font_size,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print("DRY RUN")
        print(f"  visual:   {result['visual']}")
        print(f"  duration: {result['duration']:.2f}s")
        print(f"  output:   {result['output']}")
        print()
        print("ffmpeg command:")
        print(f"  {result['ffmpeg_cmd']}")
    else:
        size_mb = result["size_bytes"] / 1_048_576
        print(f"OK  {result['output']}  ({size_mb:.2f} MB, {result['duration']:.2f}s)")
        if result.get("subtitles_path"):
            print(f"    subtitles: {result['subtitles_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
