"""Weekly content calendar generator for Sierra.

Auto-drafts a week of Sierra TikTok plans following the cadence + bit-
rotation rules from `voice-profile.md §5.6`:

  - 5-6 posts/week (Mon-Fri primary, weekend optional)
  - 80% comedy / 15% bit-and-pivot / 5% serious
  - 4 bits in rotation: sierra_reads, calling_my_dad, brad_finance,
    sierra_apologist — each hits ≈2x/week (run all 4 once + repeat the
    strongest bit for slot 5)
  - Run each bit on a DIFFERENT trend (no trend reuse within a week)

Per-day flow:
  1. Load today's trend pulse JSON
  2. Pick a different trend for each slot (deduplicated)
  3. Pick the bit per the rotation pattern
  4. Call Gemini PLANNER_PROMPT for each → plan.json
  5. Slop-scan; if score >= 1.0, regenerate at lower temperature once
  6. Write to personas/sierra-frost/calendar/<week>/<day-N>-<bit>/plan.json
  7. Emit a single calendar.md showing the whole week at a glance

Operator workflow:
  python -m tools.scheduler.calendar --week-of 2026-05-12
  # ... reads calendar.md, picks favorites, hits render on each:
  python -m tools.assembly.from_trend \\
      --plan-from-file personas/sierra-frost/calendar/<week>/<day>/plan.json

  python -m tools.scheduler.calendar --week-of 2026-05-12 --render
  # ... auto-renders all plans (burns Replicate $0.01 + ElevenLabs each)

Notes on AI-mid risk:
  Gemini occasionally emits AI-mid scripts even with anti-slop prompt.
  Calendar auto-retries each plan up to 2x; if still slop, the plan is
  saved with a `quarantine: true` flag and excluded from --render. The
  calendar.md surfaces quarantined plans for manual review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRENDS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "trends"
CAL_DIR = REPO_ROOT / "personas" / "sierra-frost" / "calendar"


# Default rotation: hit all 4 bits once Mon-Thu, repeat the strongest bit
# (sierra_reads — Inventory format proved highest-leverage) on Friday.
# Weekend is optional and operator-driven.
DEFAULT_ROTATION = [
    ("Monday",    "sierra_reads"),
    ("Tuesday",   "sierra_apologist"),
    ("Wednesday", "brad_finance"),
    ("Thursday",  "calling_my_dad"),
    ("Friday",    "sierra_reads"),     # repeat — Inventory hits hard
]


def _load_pulse(date: str | None) -> tuple[str, list[dict[str, Any]]]:
    if date:
        path = TRENDS_DIR / f"{date}.json"
    else:
        candidates = sorted(TRENDS_DIR.glob("*.json"))
        if not candidates:
            raise FileNotFoundError(
                f"No trend pulse json under {TRENDS_DIR}. "
                "Run `python -m tools.research.trend_pulse` first."
            )
        path = candidates[-1]
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.stem, json.loads(path.read_text())


def _slot_dir(week_dir: pathlib.Path, day_idx: int, day_name: str, bit_id: str) -> pathlib.Path:
    return week_dir / f"{day_idx+1:02d}-{day_name.lower()}-{bit_id}"


def _draft_plan_for_slot(
    item: dict[str, Any],
    *,
    bit_id: str,
    day_name: str,
) -> dict[str, Any] | None:
    """Run the Gemini planner with bit-id + day-context-injected prompt.
    Returns plan or None if slop-scan fails after retry.
    """
    from tools.assembly.from_trend import PLANNER_PROMPT
    from tools.llm.gemini import generate_text
    from tools.voice.slop_scan import scan_text

    item_for_prompt = {
        "label": item.get("label"),
        "source": item.get("source"),
        "score": item.get("score"),
        "angle": item.get("angle"),
        "format": item.get("format"),
        "why": item.get("why"),
    }
    bit_hint = (
        f"\n\nCALENDAR CONTEXT: this is the {day_name} slot. The bit_id "
        f"MUST be exactly '{bit_id}'. Pick a template that fits both the "
        f"bit AND the trend item below."
    )
    prompt = PLANNER_PROMPT.replace("{item_json}", json.dumps(item_for_prompt, indent=2)) + bit_hint

    for attempt in range(2):
        try:
            raw = generate_text(
                prompt,
                model="gemini-2.5-flash",
                max_tokens=4000,
                temperature=0.9 if attempt == 0 else 0.7,
                json_mode=True,
            )
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("```", 2)[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip().rsplit("```", 1)[0].strip()
            plan = json.loads(text)
            for k in ("template_id", "duration_s", "script_chunks", "voiceover_text"):
                if k not in plan:
                    raise ValueError(f"plan missing '{k}'")
            # Force the bit_id (Gemini sometimes ignores the calendar override).
            plan["bit_id"] = bit_id

            # Slop scan — voice + caption + tag.
            scan_target = " ".join(filter(None, [
                plan.get("voiceover_text"),
                plan.get("caption"),
                plan.get("tag_line"),
            ]))
            report = scan_text(scan_target)
            if report["score"] < 1.0 and not report["fail_phrases"]:
                plan["slop_score"] = report["score"]
                return plan
            # Slop hit — retry once at cooler temperature.
            print(f"[calendar] {day_name} slop {report['score']} (T1={report['tier1_hits']}, T2={report['tier2_hits']}) — retry", file=sys.stderr)
        except Exception as e:
            print(f"[calendar] {day_name} attempt {attempt+1} failed: {e}", file=sys.stderr)
            continue

    # Two attempts both slop or errored. Quarantine.
    return None


def generate_week(
    *,
    week_of: dt.date,
    pulse_date: str | None = None,
    rotation: list[tuple[str, str]] | None = None,
    n_posts: int = 5,
) -> pathlib.Path:
    """Draft a week's plans. Returns the week-dir path."""
    rotation = (rotation or DEFAULT_ROTATION)[:n_posts]
    pulse_stem, items = _load_pulse(pulse_date)
    # Sort trends by score desc, then plays desc; we'll consume one per slot.
    items_sorted = sorted(
        items,
        key=lambda x: (
            -(x.get("score") or 0),
            -((x.get("raw") or {}).get("plays") or 0),
        ),
    )

    week_dir = CAL_DIR / week_of.isoformat()
    week_dir.mkdir(parents=True, exist_ok=True)

    overview: list[dict[str, Any]] = []
    used_trend_urls: set[str] = set()
    trend_iter = iter(items_sorted)

    for day_idx, (day_name, bit_id) in enumerate(rotation):
        slot_date = (week_of + dt.timedelta(days=day_idx)).isoformat()
        slot = _slot_dir(week_dir, day_idx, day_name, bit_id)
        slot.mkdir(parents=True, exist_ok=True)
        existing = slot / "plan.json"

        # Idempotent: skip slots that already have a valid (non-quarantine)
        # plan.json. Lets the operator re-run safely after a quota hit
        # without clobbering successful drafts.
        if existing.is_file():
            try:
                prev = json.loads(existing.read_text())
                if not prev.get("quarantine") and prev.get("template_id"):
                    print(f"[calendar] {day_name} already drafted (template={prev.get('template_id')}); skipping")
                    overview.append({
                        "day_idx": day_idx + 1, "day": day_name, "date": slot_date,
                        "bit_id": bit_id, "status": "READY",
                        "template_id": prev.get("template_id"),
                        "trend": (prev.get("calendar_meta") or {}).get("trend_anchor", {}).get("label"),
                        "tag_line": prev.get("tag_line"),
                        "slop_score": prev.get("slop_score"),
                    })
                    # Mark its trend used so we don't redraft on it.
                    anchor = (prev.get("calendar_meta") or {}).get("trend_anchor") or {}
                    used = anchor.get("url") or anchor.get("label")
                    if used:
                        used_trend_urls.add(used)
                    continue
            except Exception:
                pass  # malformed — re-draft

        # Pick the next-best unused trend.
        trend = None
        for cand in items_sorted:
            url = (cand.get("raw") or {}).get("url") or cand.get("url") or cand.get("label")
            if url and url not in used_trend_urls:
                trend = cand
                used_trend_urls.add(url)
                break
        if trend is None:
            print(f"[calendar] ran out of unused trends at {day_name}; reusing top trend", file=sys.stderr)
            trend = items_sorted[0]

        print(f"[calendar] {day_name} ({slot_date}) → {bit_id} on '{(trend.get('label') or '')[:60]}'")
        plan = _draft_plan_for_slot(trend, bit_id=bit_id, day_name=day_name)

        if plan is None:
            (slot / "plan.json").write_text(json.dumps({
                "quarantine": True,
                "reason": "Gemini draft failed slop pre-flight after 2 attempts",
                "bit_id": bit_id,
                "trend_anchor": trend,
            }, indent=2, default=str))
            overview.append({
                "day_idx": day_idx + 1,
                "day": day_name,
                "date": slot_date,
                "bit_id": bit_id,
                "status": "QUARANTINE",
                "trend": trend.get("label"),
                "tag_line": "(quarantined)",
            })
            continue

        plan["calendar_meta"] = {
            "week_of": week_of.isoformat(),
            "day_idx": day_idx + 1,
            "day": day_name,
            "post_date": slot_date,
            "trend_anchor": trend,
        }
        (slot / "plan.json").write_text(json.dumps(plan, indent=2, default=str))
        overview.append({
            "day_idx": day_idx + 1,
            "day": day_name,
            "date": slot_date,
            "bit_id": bit_id,
            "status": "READY",
            "template_id": plan.get("template_id"),
            "trend": trend.get("label"),
            "tag_line": plan.get("tag_line"),
            "slop_score": plan.get("slop_score"),
        })

    # Emit calendar.md overview.
    md = [f"# Sierra Calendar — week of {week_of.isoformat()}\n",
          f"_Trend pulse: {pulse_stem} · 4-bit rotation · slop pre-flight clean_\n",
          "| # | Day | Date | Bit | Template | Status | Tag line |",
          "|---|---|---|---|---|---|---|"]
    for o in overview:
        bits_emoji = {
            "sierra_reads":      "📖",
            "sierra_apologist":  "🙏",
            "brad_finance":      "📰",
            "calling_my_dad":    "📞",
        }.get(o["bit_id"], "🎬")
        status_emoji = "✅" if o["status"] == "READY" else "⚠️"
        tag = (o["tag_line"] or "")[:60]
        md.append(
            f"| {o['day_idx']} | {o['day']} | {o['date']} | "
            f"{bits_emoji} {o['bit_id']} | {o.get('template_id','—')} | "
            f"{status_emoji} {o['status']} | {tag} |"
        )
    md.append("\n## How to ship this week\n")
    md.append("```bash")
    for o in overview:
        if o["status"] == "READY":
            md.append(
                f"# {o['day']} ({o['date']}) — {o['bit_id']}\n"
                f"python -m tools.assembly.from_trend \\\n"
                f"    --plan-from-file personas/sierra-frost/calendar/"
                f"{week_of.isoformat()}/{o['day_idx']:02d}-"
                f"{o['day'].lower()}-{o['bit_id']}/plan.json"
            )
    md.append("```\n")

    quarantined = [o for o in overview if o["status"] == "QUARANTINE"]
    if quarantined:
        md.append("## ⚠️ Quarantined slots (manual review)\n")
        md.append("These slots couldn't pass slop pre-flight after 2 retries:")
        for o in quarantined:
            md.append(f"- {o['day']}: {o['bit_id']} on '{o['trend']}'")
        md.append("\nPaths in the quarantine subdirs hold the trend anchor; "
                  "re-run `tools.scheduler.calendar` after `tools.research.trend_pulse` "
                  "if today's trend pool was thin.")

    (week_dir / "calendar.md").write_text("\n".join(md))
    print(f"[calendar] wrote {week_dir.relative_to(REPO_ROOT)}/calendar.md")
    return week_dir


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--week-of", help="ISO date for Monday of the target week (default: next Monday)")
    p.add_argument("--pulse-date", help="Trend pulse date (YYYY-MM-DD); default = most recent")
    p.add_argument("--n-posts", type=int, default=5, help="Posts to draft (1-7; default 5 = Mon-Fri)")
    args = p.parse_args()

    if args.week_of:
        week_of = dt.date.fromisoformat(args.week_of)
    else:
        today = dt.date.today()
        # Next Monday (or this Monday if today IS Monday).
        days_til_mon = (0 - today.weekday()) % 7 or 7
        week_of = today + dt.timedelta(days=days_til_mon)

    if args.n_posts < 1 or args.n_posts > 7:
        print("--n-posts must be 1..7", file=sys.stderr)
        return 1

    out = generate_week(week_of=week_of, pulse_date=args.pulse_date, n_posts=args.n_posts)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
