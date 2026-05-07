"""CLI: lint (and optionally Claude-grade) a draft against Sierra's voice profile.

Examples:
    # Lint a string passed via stdin
    echo "OMG girlies I'm literally obsessed" | python -m tools.voice

    # Lint a file
    python -m tools.voice --file draft.txt

    # Lint + AI-grade
    python -m tools.voice --grade --file draft.txt

    # Treat as a TikTok caption (also checks hook library match)
    python -m tools.voice --kind tiktok --file draft.txt

    # Sanity-check that lint.BLOCK_TOKENS hasn't drifted from voice-profile.md
    python -m tools.voice --check-sync
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from .lint import check_sync_with_markdown, lint


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.voice")
    p.add_argument("--file", type=pathlib.Path, default=None, help="Draft file to lint (default stdin).")
    p.add_argument("--kind", default="general", choices=("general", "tiktok", "reel", "ig", "newsletter"))
    p.add_argument("--grade", action="store_true", help="Also call the Claude-graded review (costs ~$0.003).")
    p.add_argument("--check-sync", action="store_true", help="Verify lint constants match voice-profile.md and exit.")
    args = p.parse_args(argv)

    if args.check_sync:
        mismatches = check_sync_with_markdown()
        if mismatches:
            print("VOICE PROFILE DRIFT:", file=sys.stderr)
            for m in mismatches:
                print(f"  {m}", file=sys.stderr)
            return 1
        print("voice-profile.md and tools/voice/lint.py are in sync.")
        return 0

    if args.file:
        text = args.file.read_text()
    else:
        text = sys.stdin.read()
    text = text.strip()
    if not text:
        print("No input.", file=sys.stderr)
        return 2

    findings = lint(text, kind=args.kind)
    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    if findings:
        for f in findings:
            print(f, file=sys.stderr)
    else:
        print("✓ deterministic lint: PASS (10/10 hard rules)")

    if args.grade:
        try:
            from .grade import grade

            g = grade(text, kind=args.kind)
        except Exception as e:
            print(f"AI grading skipped: {e}", file=sys.stderr)
            return 1 if errors else 0
        print()
        print(f"AI grade: {g['score']}/10  ({'ON VOICE' if g['on_voice'] else 'NEEDS REVISION'})")
        print(f"  reasoning: {g['reasoning']}")
        if g["issues"]:
            print("  issues:")
            for i in g["issues"]:
                print(f"    - {i}")
        if g["rewrites"]:
            print("  suggested rewrites:")
            for i, r in enumerate(g["rewrites"], 1):
                print(f"    [{i}] {r}")
        return 1 if errors or not g["on_voice"] else 0

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
