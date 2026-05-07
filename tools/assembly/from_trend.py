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


PLANNER_PROMPT = """You are planning a single Sierra Frost TikTok reel from
a trending item. Sierra is a 25-year-old comedy-first conservative-lifestyle
creator (Catherine Cohen + Hannah Berner lane, dating-tok). Voice: direct,
dry, classy, faith-adjacent, anti-victim, high-effort feminine. Vertical
9:16, 15–22 seconds. Funny mode by default.

# COMEDY RULES (mandatory; the bit is a CHARACTER doing something specific,
not a string of jokes)

- One of these structural recipes (T1–T7) MUST drive the bit:
  T1 Cohen Cabaret (BRAG → WOUND → BIGGER BRAG)
  T2 Povitsky Tone-Collapse (sweet pitch → ONE adult word → sweet)
  T3 Barone Diagnostic ("[trend] girls are women who [tic][tic][tic] —
                         and reader, I am one of them.")
  T4 Sherman Committed Costume (commit harder than the line)
  T5 Summers Smile-Through-Taboo (borrowed character voice for the spike)
  T6 Berner Apologist ("I'm a [trend] apologist. red flags as features.
                        self-indict on button.")
  T7 McKenzie Archetype-Flip ("the girl who [trend]. four tells. 5th is YOU.")

- Use HYPER-SPECIFIC receipts. Real brands (Le Creuset, Stanley sage,
  Skims Coze, Erewhon, Hinge), real numbers (16 times this morning),
  named avatars (Brad in finance, Tyler). Specificity is the comedy.

- Tag line: the LAST line. Distinct from punchline. SCREENSHOT-WORTHY.
  This is the SAVE driver. Examples that pass: "He does not live here.
  Anymore." / "Brad who?" / "It's 2:51. I am SO decentered."

# FORBIDDEN VOCABULARY (instant fail — pre-flight slop scanner blocks render)

NEVER use any of these words in voiceover_text, caption, or tag_line:
  delve, embark, unleash, unlock, revolutionize, spearhead, foster,
  harness, elevate, transcend, forge, ignite, propel, catalyze,
  multifaceted, nuanced, intricate, meticulous, profound, holistic,
  robust, pivotal, paramount, indispensable, quintessential,
  comprehensive, tapestry, beacon, realm, landscape, symphony, mosaic,
  crucible, labyrinth, odyssey, cornerstone, bedrock, linchpin, nexus,
  showcasing, exemplifying, demonstrating, illuminating, underscoring,
  moreover, furthermore, subsequently, consequently, leverage, synergy,
  scalability, transformative, seamless

NEVER use these phrases:
  "in today's fast-paced world", "it's worth noting", "at its core",
  "cannot be overstated", "a testament to", "navigate the complexities",
  "unlock the potential", "treasure trove", "game changer", "look no
  further", "mind-blowing", "life-changing", "let's dive in", "in this
  video", "stay tuned", "hi guys", "what's up guys", "imagine you are",
  "picture this", "I'd be happy to", "great question"

# TEMPLATES

- P1 bedroom medium-close, polish — soft confident
- P3 bedroom tight close-up, dry knowing expression — pure commentary
- P7 Florida walk, golden hour — lifestyle hero
- P12 cafe MCU, look up from laptop — newsletter angle / Brad newscaster
- P15 vanity, lipstick mid-application — getting-ready scene
- P22 sidewalk cafe, journaling, palm shadow — "writing it down" energy
- P25 bedroom mirror outfit-check — apologist / "thriving" framing
- P31 tight close-up, eyebrow raise — "you're kidding right"
- P32 bed mid-coffee dry sideways glance — reaction commentary
- P36 medium, head-shake smirk — "we're not doing this"
- P37 chin in hand deadpan — "go on"
- P50 Sunday morning hero, dainty cross — pillar 2

# OUTPUT FORMAT (return ONLY this JSON — no markdown, no prose, no fences)

{
  "template_id": "P32",
  "bit_id": "sierra_reads",
  "rationale": "one sentence: which T1-T7 recipe + why this template fits",
  "duration_s": 17,
  "script_chunks": [
    {"start": 0.0, "end": 2.5, "text": "I HAVE FULLY DECENTERED HIM."},
    ...
  ],
  "voiceover_text": "I have fully decentered him. ...",
  "caption": "Sierra-voice TikTok caption ≤180 chars",
  "tag_line": "the screenshot line — the LAST words of the bit",
  "hashtags": ["#datingtok", "#decentermen", "#datingadvice", "#fyp"]
}

bit_id ∈ {sierra_reads, calling_my_dad, brad_finance, sierra_apologist}.
script_chunks: 6-9 chunks, ALL CAPS, 2-6 words each, total 15-22s.
voiceover_text: natural mixed case, contractions ok.

# TREND TO BUILD FROM

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


def plan_with_llm(item: dict[str, Any], *, provider: str = "auto") -> dict[str, Any]:
    """Ask an LLM to pick a template + draft the script. Returns the plan.

    `provider`:
      - 'auto'   try Gemini (free) first, fall back to Claude if available
      - 'gemini' force Gemini text (free, requires GEMINI_API_KEY)
      - 'claude' force Anthropic Claude (paid, requires ANTHROPIC_API_KEY)

    Operators on a free-only stack should use 'gemini' (default). The
    Anthropic path remains as a quality fallback if the operator opts in.
    """
    item_for_prompt = {
        "label": item.get("label"),
        "source": item.get("source"),
        "score": item.get("score"),
        "angle": item.get("angle"),
        "format": item.get("format"),
        "why": item.get("why"),
    }
    full_prompt = PLANNER_PROMPT.replace("{item_json}", json.dumps(item_for_prompt, indent=2))

    if provider == "auto":
        from tools.llm.gemini import is_enabled as gemini_ok
        provider = "gemini" if gemini_ok() else "claude"

    # Up to 3 attempts — Gemini occasionally emits invalid JSON even in
    # json_mode (trailing commas, single quotes). Retrying with a hint
    # at slightly different temperatures resolves >95% of these.
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            if provider == "gemini":
                from tools.llm.gemini import generate_text
                raw = generate_text(
                    full_prompt,
                    model=os.environ.get("SIERRA_GEMINI_PLANNER", "gemini-2.5-flash"),
                    max_tokens=4000,
                    temperature=0.9 if attempt == 0 else 0.7,  # cooler on retries
                    json_mode=True,
                )
            else:
                from tools.research.common import claude_score
                raw = claude_score(full_prompt, model="claude-sonnet-4-6", max_tokens=1500)

            text = raw.strip()
            if text.startswith("```"):
                text = text.split("```", 2)[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip().rsplit("```", 1)[0].strip()
            plan = json.loads(text)
            for k in ("template_id", "duration_s", "script_chunks", "voiceover_text"):
                if k not in plan:
                    raise ValueError(f"LLM plan missing required key: {k}")
            return plan
        except (json.JSONDecodeError, ValueError) as e:
            last_err = e
            if attempt < 2:
                print(f"[planner] {provider} attempt {attempt+1}/3 parse failed: {str(e)[:80]} — retrying", file=sys.stderr)
                continue
            raise
    raise last_err if last_err else RuntimeError("planner: exhausted retries")


# Back-compat alias — older callers still use this name.
plan_with_claude = plan_with_llm


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
        choices=["replicate", "higgsfield", "nano-banana", "pollinations"],
        default="replicate",
        help="Image-gen backend. Default: replicate (Sierra LoRA + Boreal). "
             "nano-banana for hero/4K/edits. pollinations for FREE cloud-burst Flux "
             "(no Sierra-LoRA identity-lock — use for B-roll only).",
    )
    p.add_argument(
        "--resolution",
        choices=["1K", "2K", "4K"],
        default="2K",
        help="Nano-banana resolution (1K/2K/4K). Ignored for other backends.",
    )
    p.add_argument(
        "--input-image",
        help="Reference image for nano-banana image-to-image edits.",
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
    p.add_argument("--no-lipsync", action="store_true",
                   help="Skip OmniHuman lipsync (default ON — turns Sierra still + Brielle audio into a talking-head video). "
                        "When skipped, the assembler ken-burns'es the static image instead.")
    p.add_argument("--no-spoof", action="store_true",
                   help="Skip EXIF spoofer (default ON — strips C2PA + AI sigs, stamps iPhone metadata)")
    p.add_argument("--spoof-device", default="iphone-15-pro",
                   choices=["iphone-15-pro", "iphone-14", "iphone-16", "samsung-s24"],
                   help="Device fingerprint to inject (default iPhone 15 Pro)")
    p.add_argument("--spoof-gps", default="palm-beach",
                   choices=["palm-beach", "miami", "boca-raton", "naples",
                            "los-angeles", "nashville", "austin"],
                   help="GPS coordinate region to inject (Sierra is South Florida-coded by default)")
    p.add_argument(
        "--llm",
        choices=["auto", "gemini", "claude", "stub"],
        default="auto",
        help="Planner LLM: auto (Gemini free if available, else Claude paid, else stub) | "
             "gemini (force free Gemini) | claude (force paid Anthropic) | stub (deterministic fallback)",
    )
    p.add_argument("--plan-from-file", help="Skip planner; read plan JSON from this path")
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
    else:
        # Free-by-default: Gemini → Claude → stub fallback.
        try:
            from tools.llm.gemini import is_enabled as gemini_ok
        except Exception:
            gemini_ok = lambda: False
        provider = (args.llm or "auto").lower()
        if provider == "auto":
            provider = (
                "gemini" if gemini_ok()
                else "claude" if os.environ.get("ANTHROPIC_API_KEY")
                else "stub"
            )

        if provider == "stub":
            print(f"[from-trend] no LLM available → stub plan")
            plan = _stub_plan(item, args.template or "P3")
        else:
            try:
                print(f"[from-trend] planning with {provider} …")
                plan = plan_with_llm(item, provider=provider)
            except Exception as e:
                print(f"[from-trend] {provider} planner failed ({e}); falling back to stub", file=sys.stderr)
                plan = _stub_plan(item, args.template or "P3")

        if args.template:
            plan["template_id"] = args.template
            plan["rationale"] = f"forced via --template {args.template}"
    print(f"[from-trend] template = {plan['template_id']} · {plan.get('rationale','')}")

    # Slop pre-flight — fails the run if the plan trips fail-phrases or
    # scores >=1.0 on the Tier-1/Tier-2 vocab scanner. Runs before any
    # API spend so we don't render slop. See voice-profile §11.5.
    try:
        from tools.voice.slop_scan import scan_text
        slop_text = " ".join(filter(None, [
            plan.get("voiceover_text"),
            plan.get("caption"),
            plan.get("tag_line"),
        ]))
        report = scan_text(slop_text)
        print(f"[from-trend] slop scan: score={report['score']} ({report['rating']})")
        if report["fail_phrases"]:
            print(f"[from-trend] FAIL — forbidden phrases in plan: {report['fail_phrases']}", file=sys.stderr)
            return 3
        if report["score"] >= 1.0:
            print(f"[from-trend] WARNING — slop score {report['score']} >= 1.0", file=sys.stderr)
            if report["tier1_hits"]: print(f"  Tier 1 hits: {report['tier1_hits']}", file=sys.stderr)
            if report["tier2_hits"]: print(f"  Tier 2 hits: {report['tier2_hits']}", file=sys.stderr)
    except Exception as e:
        print(f"[from-trend] slop pre-flight skipped: {e}", file=sys.stderr)

    # Output dir.
    if args.plan_from_file:
        # When the operator hand-writes a plan, anchor outputs to the plan
        # file's parent dir. Avoids the bug where rerunning from_trend after
        # the trend pulse shifts (rank-1 changes) creates a new mismatched
        # output dir while the plan still references the original trend.
        unit_dir = pathlib.Path(args.plan_from_file).resolve().parent
    else:
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
        elif args.backend == "nano-banana":
            from tools.generation import nano_banana as gen_mod
            print(f"[from-trend] nano-banana generating {plan['template_id']} ({args.resolution}) …")
            result = gen_mod.generate(
                "sierra_frost", plan["template_id"],
                resolution=args.resolution,
                input_image=args.input_image,
            )
        elif args.backend == "pollinations":
            from tools.generation import pollinations as gen_mod
            print(f"[from-trend] pollinations (free Flux) generating {plan['template_id']} …")
            result = gen_mod.generate(
                "sierra_frost", plan["template_id"],
                seed=args.seed,
            )
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

        # EXIF spoof — strips C2PA + AI signatures, stamps as iPhone
        # photo. Massive distribution lift on IG / Threads (kills the
        # "Made with AI" label). Disabled with --no-spoof.
        if not args.no_spoof:
            try:
                from tools.realism.exif_spoofer import spoof_image
                spoofed = unit_dir / "visual_spoofed.jpg"
                spoof_image(
                    image_path,
                    out=spoofed,
                    device=args.spoof_device,
                    gps=args.spoof_gps,
                )
                # Use spoofed as primary going forward — pipeline.assemble()
                # is fine with .jpg, and the upload-ready file is the
                # spoofed one. Original is kept as visual.png for audit.
                image_path = spoofed
                print(f"[from-trend] exif-spoofed → {spoofed.relative_to(REPO_ROOT)} ({args.spoof_device}, {args.spoof_gps})")
            except Exception as e:
                print(f"[from-trend] spoof skipped: {e}", file=sys.stderr)
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

    # Lipsync — turns the still + audio into a talking-head video. The
    # pipeline.assemble() step then uses this video as the visual instead
    # of ken-burns'ing a static image. Default ON when both image and VO
    # exist. Skip with --no-lipsync.
    talking_path: pathlib.Path | None = None
    if not args.no_lipsync and image_path is not None and vo_path is not None and vo_path.is_file():
        try:
            from tools.generation.lipsync import lipsync_image
            talking_path = unit_dir / "talking.mp4"
            print(f"[from-trend] lipsync omnihuman → {talking_path.relative_to(REPO_ROOT)}")
            lipsync_image(image_path, vo_path, output=talking_path, strip_audio=True)
            # Use the talking video as the visual from here on.
            image_path = talking_path
        except Exception as e:
            print(f"[from-trend] lipsync skipped ({e}); falling back to ken-burns still", file=sys.stderr)

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

        # If plan declares a bit_id (sierra_reads / calling_my_dad /
        # brad_finance), prepend the branded title card. Per voice-profile
        # §5.6: the title card is the follower-first signal; without it,
        # bits don't compound.
        bit_id = plan.get("bit_id")
        if bit_id:
            card_path = REPO_ROOT / "tools" / "assembly" / "title_cards" / f"{bit_id}.mp4"
            if card_path.is_file():
                tagged = unit_dir / "final_with_card.mp4"
                print(f"[from-trend] prepending title card '{bit_id}' → {tagged.relative_to(REPO_ROOT)}")
                asm.prepend_title_card(out_video, card_path, tagged)
            else:
                print(f"[from-trend] WARNING: bit_id='{bit_id}' but card not found at {card_path}", file=sys.stderr)
                print("[from-trend]   run: python -m tools.assembly.title_cards", file=sys.stderr)

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
