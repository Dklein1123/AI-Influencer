"""CLI entry: python -m tools.generation [options] TEMPLATE_ID [TEMPLATE_ID ...]

Examples:
    # Single generation for Sierra
    python -m tools.generation P1

    # Batch generation
    python -m tools.generation P1 P3 P7 P12

    # Different persona (when added)
    python -m tools.generation --persona avery-cole P1

    # Dry run — show the prompt and arguments without submitting
    python -m tools.generation --dry-run P1

    # Override aspect or seed
    python -m tools.generation --aspect 4:5 --seed 42 P3

    # List all templates with their pillars
    python -m tools.generation --list
"""

from __future__ import annotations

import argparse
import importlib
import sys

from . import higgsfield


def _list_templates(persona_name: str) -> int:
    persona = higgsfield._load_persona(persona_name)
    print(f"{persona.DISPLAY_NAME} — {len(persona.TEMPLATES)} templates\n")
    print(f"{'ID':<6}{'Pillar':<8}{'Kind':<10}{'Setting':<10}{'Wardrobe':<12}Pose")
    print("-" * 100)
    for tid, t in persona.TEMPLATES.items():
        print(
            f"{tid:<6}{t['pillar']:<8}{t['kind']:<10}{t['setting']:<10}"
            f"{t['wardrobe']:<12}{t['pose'][:60]}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.generation")
    p.add_argument("templates", nargs="*", help="Template IDs (e.g. P1 P3 P7).")
    p.add_argument("--persona", default="sierra-frost", help="Persona name (default: sierra-frost).")
    p.add_argument("--seed", type=int, default=None, help="Override seed for all generations in this batch.")
    p.add_argument("--aspect", default=None, help="Override aspect ratio (e.g. 9:16, 4:5, 16:9).")
    p.add_argument("--application", default=None, help="Override Higgsfield API application path.")
    p.add_argument("--dry-run", action="store_true", help="Print prompt and args without submitting.")
    p.add_argument("--list", action="store_true", help="List all templates for the persona and exit.")
    args = p.parse_args(argv)

    if args.list:
        return _list_templates(args.persona)

    if not args.templates:
        p.print_help()
        return 1

    if args.dry_run:
        for tid in args.templates:
            try:
                result = higgsfield.generate(
                    args.persona,
                    tid,
                    seed=args.seed,
                    application=args.application,
                    aspect_ratio=args.aspect,
                    dry_run=True,
                )
                print(f"\n=== {tid} (DRY RUN) ===")
                print(f"application: {result['application']}")
                params = result["arguments"].get("params", result["arguments"])
                for k, v in params.items():
                    if isinstance(v, str) and len(v) > 200:
                        v = v[:200] + "..."
                    print(f"  {k}: {v}")
            except Exception as e:
                print(f"[{tid}] ERROR: {e}", file=sys.stderr)
        return 0

    # Live generation.
    results = higgsfield.generate_batch(
        args.persona,
        args.templates,
        seed=args.seed,
    )

    print("\n=== summary ===")
    ok = sum(1 for r in results if "error" not in r and r.get("saved"))
    print(f"  successes: {ok}/{len(results)}")
    for r in results:
        tid = r.get("template_id")
        if "error" in r:
            print(f"  {tid}: ERROR — {r['error']}")
        elif r.get("saved"):
            print(f"  {tid}: {len(r['saved'])} file(s)")
        else:
            print(f"  {tid}: completed, no assets extracted (check generation-log.md)")
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    sys.exit(main())
