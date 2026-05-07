"""Trend → Sierra reel: end-to-end build from a top-scored trend item.

Pipeline:
    1. Load today's (or specified date's) trend pulse JSON.
    2. Pick the top-scored item (or by --id flag).
    3. Ask Claude to pick the best Sierra template (P1-P50) and draft a
       15-22s timestamped script in Sierra's voice.
    4. Generate the visual via Higgsfield Soul 2 (sierra_frost persona).
    5. Synthesize voiceover via ElevenLabs (Sierra's voice ID).
    6. Render the final 1080x1920 9:16 reel via tools.assembly.pipeline.
    7. Best-effort sync the manifest + final video URL to the portal.

Outputs land under:
    personas/sierra-frost/content-units/from-trend-<date>-<slug>/

Usage:
    # plan only (no API spend, no render)
    python -m tools.assembly.from_trend --dry-run

    # full build of today's #1 trend
    python -m tools.assembly.from_trend

    # build a specific trend by 1-indexed rank
    python -m tools.assembly.from_trend --rank 3

    # build from yesterday's pulse, force template P32
    python -m tools.assembly.from_trend --date 2026-05-06 --template P32

Requires:
    ANTHROPIC_API_KEY  (for the planner)
    HF_KEY + SIERRA_SOUL_ID  (for image gen)
    ELEVEN_API_KEY + ELEVEN_SIERRA_VOICE_ID  (for VO)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRENDS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "trends"
UNITS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "content-units"


PLANNER_PROMPT = """You are planning a single Sierra Frost TikTok reel from a
trending item. Sierra is a 25-year-old conservative-leaning lifestyle/dating
commentator. Voice: direct, dry-witty, classy, faith-adjacent, anti-victim,
high-effort feminine. Vertical 9:16, 15-22 seconds.

Pick ONE template from this list and draft the script.

Templates available (id → vibe):
- P1  bedroom medium-close, polish, off-camera glance — soft confident
- P2  cafe medium, dolly push, mid-typing look-up — newsletter angle
- P3  bedroom tight close-up, dolly push, dry knowing expression — pure commentary
- P7  Florida walk, golden hour, walking toward camera — lifestyle hero
- P12 cafe MCU, dolly push, look up from laptop, faint smile — newsletter funnel
- P31 tight close-up, eyebrow raise, "you're kidding right" — reaction
- P32 bed, mid-coffee dry sideways glance — reaction commentary
- P33 mid-typing dry "really?" look up — reaction
- P34 soft eye-roll knowing patient — reaction
- P36 medium, slow head shake smirk arms crossed — "we're not doing this"
- P37 chin in hand deadpan straight to camera — "go on"
- P40 slow blink deadpan — "the audacity"
- P41 over-the-shoulder writing newsletter, Sunday energy — funnel
- P50 Sunday morning hero, soft pastel light, dainty cross — pillar 2

Script format — output EXACTLY this JSON (no prose outside the array):
{
  "template_id": "P3",
  "rationale": "one sentence why this template fits the trend's format/angle",
  "duration_s": 18,
  "script_chunks": [
    {"start": 0.0, "end": 2.5, "text": "STANDARDS AREN'T"},
    {"start": 2.5, "end": 5.0, "text": "RED FLAGS."},
    ...
  ],
  "voiceover_text": "Standards aren't red flags. ... full sentence read.",
  "caption": "Sierra-voice IG/TikTok caption, ≤200 chars",
  "hashtags": ["#highvaluewoman", "#femininity", "#datingadvice"]
}

Subtitle chunks should be SHORT (2-6 words, ALL CAPS), one strong line per
chunk, totaling 6-9 chunks. The voiceover_text is the full natural read of
the same script (mixed case, contractions ok). Total duration 15-22s.

Trend item to build from:
{item_json}
"""


def load_pulse(date: str | None) -> tuple[str, list[dict[str, Any]]]:
    if date:
        path = TRENDS_DIR / f"{date}.json"
    else:
        # Most recent JSON in the dir.
        candidates = sorted(TRENDS_DIR.glob("*.json"))
        if not candidates:
            raise FileNotFoundError(
                f"No trend pulse json under {TRENDS_DIR}. "
                f"Run `python -m tools.research.trend_pulse` first."
            )
        path = candidates[-1]
    if not path.is_file():
        raise FileNotFoundError(f"No trend pulse at {path}")
    items = json.loads(path.read_text())
    return path.stem, items


def slugify(s: str, *, max_len: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "trend").lower()).strip("-")
    return s[:max_len] or "trend"


def plan_with_claude(item: dict[str, Any]) -> dict[str, Any]:
    """Ask Claude to pick a template + draft the script. Returns the plan."""
    from tools.research.common import claude_score

    item_for_prompt = {
        "label": item.get("label"),
        "source": item.get("source"),
        "score": item.get("score"),
        "angle": item.get("angle"),
        "format": item.get("format"),
        "why": item.get("why"),
    }
    raw = claude_score(
        PLANNER_PROMPT.replace("{item_json}", json.dumps(item_for_prompt, indent=2)),
        model="claude-sonnet-4-6",
        max_tokens=1500,
    )
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip().rsplit("```", 1)[0].strip()
    plan = json.loads(text)
    # Light validation.
    for k in ("template_id", "duration_s", "script_chunks", "voiceover_text"):
        if k not in plan:
            raise ValueError(f"Claude plan missing required key: {k}")
    return plan


def _stub_plan(item: dict[str, Any], template_id: str) -> dict[str, Any]:
    """Deterministic placeholder plan for dry-run without Claude."""
    label = (item.get("label") or "")[:80]
    return {
        "template_id": template_id,
        "rationale": "stub plan (dry-run, no Claude key)",
        "duration_s": 16,
        "script_chunks": [
            {"start": 0.0, "end": 2.5, "text": "REAL TAKE:"},
            {"start": 2.5, "end": 6.5, "text": "(Sierra response to trend)"},
            {"start": 6.5, "end": 10.5, "text": "(supporting line)"},
            {"start": 10.5, "end": 14.0, "text": "(payoff line)"},
            {"start": 14.0, "end": 16.0, "text": "FOLLOW FOR MORE"},
        ],
        "voiceover_text": (
            f"Real take. Sierra response to: {label}. Supporting line. Payoff. Follow for more."
        ),
        "caption": f"[stub] Sierra take on: {label[:120]}",
        "hashtags": ["#stub", "#dryrun"],
    }


def render_script_text(plan: dict[str, Any]) -> str:
    """Render plan.script_chunks as the [start-end] TEXT lines pipeline expects."""
    out = []
    for c in plan["script_chunks"]:
        out.append(f"[{float(c['start']):.1f}-{float(c['end']):.1f}] {c['text']}")
    return "\n".join(out)


def chunks_for_vo(plan: dict[str, Any]) -> list[tuple[float, float, str]]:
    """Use Sierra's natural voiceover_text aligned to the chunk timings.

    We split voiceover_text by sentence-ish punctuation to roughly map to
    each subtitle chunk. If the count doesn't match, we just speak the
    full VO across the whole duration as a single chunk.
    """
    chunks = plan["script_chunks"]
    vo_full = plan["voiceover_text"].strip()

    # Try sentence-level split.
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", vo_full) if p.strip()]
    if len(parts) == len(chunks):
        return [(float(c["start"]), float(c["end"]), p) for c, p in zip(chunks, parts)]

    # Fallback: one chunk for the entire duration.
    total = max(float(c["end"]) for c in chunks)
    return [(0.0, total, vo_full)]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--date", help="Trend pulse date (YYYY-MM-DD); defaults to most recent")
    p.add_argument("--rank", type=int, default=1, help="1-indexed rank in scored items")
    p.add_argument("--template", help="Force a specific template id (overrides Claude pick)")
    p.add_argument("--seed", type=int, help="Higgsfield seed")
    p.add_argument(
        "--backend",
        choices=["replicate", "higgsfield"],
        default="replicate",
        help="Image-gen backend. Default: replicate (Sierra LoRA, ~30x cheaper than Higgsfield).",
    )
    p.add_argument(
        "--extra-lora",
        help="Realism LoRA to stack on top of Sierra (HF repo or Replicate model). "
             "Defaults to env SIERRA_EXTRA_LORA. Examples: 'kudzueye/Boreal'.",
    )
    p.add_argument("--extra-lora-scale", type=float, default=0.65,
                   help="Scale for the extra realism LoRA (default 0.65; community 0.5–0.8)")
    p.add_argument("--guidance", type=float, default=2.5,
                   help="Flux guidance_scale (default 2.5; lower = more realistic, less prompt-adherent)")
    p.add_argument("--lora-scale", type=float, default=0.9,
                   help="Sierra LoRA strength (default 0.9; >1.0 over-fits)")
    p.add_argument("--plan-from-file", help="Skip Claude planner; read plan JSON from this path")
    p.add_argument("--dry-run", action="store_true", help="Plan only — no API spend")
    p.add_argument("--no-image", action="store_true", help="Skip image gen (use existing)")
    p.add_argument("--no-vo", action="store_true", help="Skip VO synth")
    p.add_argument("--no-render", action="store_true", help="Skip ffmpeg assemble")
    p.add_argument("--no-sync", action="store_true", help="Skip portal sync")
    args = p.parse_args()

    pulse_date, items = load_pulse(args.date)
    print(f"[from-trend] loaded {len(items)} items from {pulse_date}")
    if args.rank < 1 or args.rank > len(items):
        print(f"[from-trend] rank {args.rank} out of range (1-{len(items)})", file=sys.stderr)
        return 1
    # Items are pre-sorted descending by score in trend_pulse.render_markdown,
    # but JSON dump may or may not preserve that. Re-sort defensively.
    sorted_items = sorted(items, key=lambda x: (x.get("score") or 0), reverse=True)
    item = sorted_items[args.rank - 1]
    print(f"[from-trend] rank {args.rank}: [{item.get('score')}/10] {item.get('label','')[:90]}")

    # Plan.
    if args.plan_from_file:
        plan_path = pathlib.Path(args.plan_from_file)
        if not plan_path.is_file():
            print(f"[from-trend] plan file not found: {plan_path}", file=sys.stderr)
            return 1
        plan = json.loads(plan_path.read_text())
        if args.template:
            plan["template_id"] = args.template
        plan.setdefault("rationale", f"plan-from-file: {plan_path}")
        print(f"[from-trend] plan loaded from {plan_path}")
    elif args.dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        print("[from-trend] dry-run + no ANTHROPIC_API_KEY → stub plan")
        plan = _stub_plan(item, args.template or "P3")
    else:
        print("[from-trend] planning with Claude …")
        plan = plan_with_claude(item)
        if args.template:
            plan["template_id"] = args.template
            plan["rationale"] = f"forced via --template {args.template}"
    print(f"[from-trend] template = {plan['template_id']} · {plan.get('rationale','')}")

    # Output dir.
    slug = slugify(item.get("label") or item.get("source") or "trend")
    unit_dir = UNITS_DIR / f"from-trend-{pulse_date}-{slug}"
    unit_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "pulse_date": pulse_date,
        "rank": args.rank,
        "trend_item": item,
        "plan": plan,
    }
    (unit_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    (unit_dir / "script.txt").write_text(render_script_text(plan))
    print(f"[from-trend] wrote {unit_dir.relative_to(REPO_ROOT)}/manifest.json")
    print(f"[from-trend] wrote {unit_dir.relative_to(REPO_ROOT)}/script.txt")

    if args.dry_run:
        print("[from-trend] --dry-run set, stopping before API spend")
        return 0

    # Image.
    image_path: pathlib.Path | None = None
    if not args.no_image:
        if args.backend == "higgsfield":
            from tools.generation import higgsfield as gen_mod
            print(f"[from-trend] higgsfield generating {plan['template_id']} …")
            result = gen_mod.generate("sierra_frost", plan["template_id"], seed=args.seed)
        else:
            from tools.lora import generate as gen_mod
            print(f"[from-trend] replicate-lora generating {plan['template_id']} (anti-slop config) …")
            result = gen_mod.generate(
                "sierra_frost", plan["template_id"],
                lora_scale=args.lora_scale,
                guidance=args.guidance,
                extra_lora=args.extra_lora,
                extra_lora_scale=args.extra_lora_scale,
            )
        saved = [pathlib.Path(p) for p in result.get("saved", [])]
        if not saved:
            print("[from-trend] image gen produced no assets; aborting", file=sys.stderr)
            return 2
        image_path = saved[0]
        # Copy into the unit dir for atomic packaging.
        target = unit_dir / f"visual{image_path.suffix}"
        target.write_bytes(image_path.read_bytes())
        image_path = target
        print(f"[from-trend] image → {image_path.relative_to(REPO_ROOT)}")
    else:
        existing = sorted(unit_dir.glob("visual.*"))
        if not existing:
            print("[from-trend] --no-image but no visual.* in unit dir", file=sys.stderr)
            return 2
        image_path = existing[0]

    # Voiceover.
    vo_path: pathlib.Path | None = None
    if not args.no_vo:
        from tools.voice_synth import client as vs
        voice_id = os.environ.get("ELEVEN_SIERRA_VOICE_ID")
        if not voice_id:
            print("[from-trend] ELEVEN_SIERRA_VOICE_ID missing; skipping VO", file=sys.stderr)
        else:
            vo_chunks = chunks_for_vo(plan)
            vo_path = unit_dir / "voiceover.wav"
            print(f"[from-trend] elevenlabs synth {len(vo_chunks)} chunk(s) …")
            vs.synthesize_chunks(vo_chunks, voice_id=voice_id, output_path=vo_path)
            print(f"[from-trend] vo → {vo_path.relative_to(REPO_ROOT)}")

    # Assemble.
    if not args.no_render:
        from tools.assembly import pipeline as asm
        out_video = unit_dir / "final.mp4"
        script_text = render_script_text(plan)
        duration = max(float(c["end"]) for c in plan["script_chunks"])
        print(f"[from-trend] ffmpeg assemble → {out_video.relative_to(REPO_ROOT)}")
        asm.assemble(
            visual=image_path,
            output=out_video,
            voiceover=vo_path,
            script_text=script_text,
            duration=duration,
        )
        print(f"[from-trend] rendered {out_video.relative_to(REPO_ROOT)}")

        if not args.no_sync:
            try:
                from tools.sync import supabase_client as sync
                sync.insert_ai_output(
                    title=f"From-trend reel · {plan['template_id']} · {pulse_date}",
                    content=(
                        f"Trend: {item.get('label','')[:200]}\n"
                        f"Score: {item.get('score')}/10 · Format: {item.get('format')}\n"
                        f"Template: {plan['template_id']} — {plan.get('rationale','')}\n"
                        f"Duration: {duration:.1f}s · Caption: {plan.get('caption','')}"
                    ),
                    kind="video",
                    source_prompt=f"from_trend.py rank={args.rank}",
                    tags=["from-trend", plan["template_id"], pulse_date],
                )
                print("[from-trend] synced to portal AI Outputs")
            except Exception as e:
                print(f"[from-trend] sync skipped: {e}", file=sys.stderr)

    print(f"[from-trend] done → {unit_dir.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
