"""CLI: python -m tools.voice_synth --script CONTENT_UNIT.script.txt --output VO.wav

Two modes:

1. Plain prose → single audio file
       python -m tools.voice_synth \\
           --text "Unpopular opinion: standards aren't asking too much." \\
           --output /tmp/vo.mp3

2. Chunked script with timing (matches the assembly pipeline format)
       python -m tools.voice_synth \\
           --script personas/sierra-frost/content-units/2026-05-06_P7.script.txt \\
           --output personas/sierra-frost/content-queue/2026-05-06_P7_vo.wav

Voice ID resolution order:
    --voice-id flag → ELEVEN_SIERRA_VOICE_ID env → error.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

from . import client


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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.voice_synth")
    p.add_argument("--text", help="Inline text to synthesize.")
    p.add_argument("--script", type=pathlib.Path, help="Path to a chunked script file.")
    p.add_argument("--output", required=True, type=pathlib.Path)
    p.add_argument("--voice-id", default=None)
    p.add_argument("--model", default="eleven_multilingual_v2")
    p.add_argument("--stability", type=float, default=0.55)
    p.add_argument("--similarity-boost", type=float, default=0.80)
    p.add_argument("--style", type=float, default=0.20)
    p.add_argument("--list-voices", action="store_true", help="List voices on the account and exit.")
    args = p.parse_args(argv)

    _load_env()
    if args.list_voices:
        for v in client.list_voices():
            print(f"{v['voice_id']}  {v['name']}  ({v.get('category','')})")
        return 0

    voice_id = args.voice_id or os.environ.get("ELEVEN_SIERRA_VOICE_ID")
    if not voice_id:
        print("--voice-id missing and ELEVEN_SIERRA_VOICE_ID not set in ~/.AI-Influencer.env", file=sys.stderr)
        return 2

    common = dict(
        voice_id=voice_id,
        output_path=args.output,
        model=args.model,
        stability=args.stability,
        similarity_boost=args.similarity_boost,
        style=args.style,
    )

    if args.script:
        # Reuse the assembly module's chunk parser — same format, single source of truth.
        from tools.assembly.pipeline import parse_script

        text = args.script.read_text()
        chunks = parse_script(text)
        if not chunks:
            print(f"No chunks parsed from {args.script}", file=sys.stderr)
            return 2
        # Strip ASS line-break sentinels for spoken text.
        triples = [(c.start, c.end, c.text.replace("\\N", " ")) for c in chunks]
        client.synthesize_chunks(triples, **common)
    elif args.text:
        client.synthesize(args.text, **common)
    else:
        print("Pass --text or --script", file=sys.stderr)
        return 2

    print(f"OK  {args.output}  ({args.output.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
