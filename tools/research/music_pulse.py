"""Trending TikTok sounds for Sierra Frost.

Daily list of 10–30 viral sounds Sierra could borrow, with usage counts
and rough mood tags. Plugs into `tools/assembly/from_trend.py` so reels
can auto-suggest a music bed.

Apify actor: `epctex/tiktok-music-scraper` (paid, ~$2 per 1k results).
For free fallback, we also support pulling sounds OFF the trend pulse
JSON — every TikTok scrape includes `musicMeta.musicName`, so we can
aggregate the most-used sounds across today's hashtag pull at zero cost.

Usage:
    # free path: aggregate today's trend pulse music data
    python -m tools.research.music_pulse --from-pulse

    # paid path: dedicated TikTok music scraper
    python -m tools.research.music_pulse --keywords "feminine" "soft girl"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from collections import Counter
from typing import Any

from .common import apify_run_sync, dump_json, write_markdown

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRENDS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "trends"
MUSIC_DIR = REPO_ROOT / "personas" / "sierra-frost" / "music-pulse"


def aggregate_from_pulse(date: str | None) -> list[dict[str, Any]]:
    """Free path — aggregate music_meta from today's trend pulse JSON.

    Counts sounds across all TikTok items in the pulse, returns top 30.
    """
    if date:
        path = TRENDS_DIR / f"{date}.json"
    else:
        candidates = sorted(TRENDS_DIR.glob("*.json"))
        if not candidates:
            print(f"[music] no pulse JSON in {TRENDS_DIR}", file=sys.stderr)
            return []
        path = candidates[-1]
    items = json.loads(path.read_text())

    counter: Counter[str] = Counter()
    examples: dict[str, dict[str, Any]] = {}
    for it in items:
        raw = it.get("raw") or {}
        music = raw.get("music")
        if not music:
            continue
        counter[music] += 1
        # Keep best example by play count.
        if music not in examples or (raw.get("plays") or 0) > (examples[music].get("plays") or 0):
            examples[music] = {
                "music": music,
                "plays": raw.get("plays"),
                "url": raw.get("url"),
                "author": raw.get("author"),
                "caption": (raw.get("caption") or "")[:140],
            }
    out = []
    for music, count in counter.most_common(30):
        ex = examples[music]
        out.append({
            "music": music,
            "uses_in_pulse": count,
            "best_example": ex,
        })
    return out


def scrape_keyword_sounds(keywords: list[str], *, max_per: int = 20) -> list[dict[str, Any]]:
    """Paid path — dedicated TikTok music keyword scraper."""
    items: list[dict[str, Any]] = []
    for kw in keywords:
        try:
            rows = apify_run_sync(
                "epctex/tiktok-music-scraper",
                {"search": kw, "maxItems": max_per},
                max_items=max_per,
                timeout=300,
            )
        except Exception as e:
            print(f"[music] scrape '{kw}' failed: {e}", file=sys.stderr)
            continue
        for r in rows:
            items.append({
                "keyword": kw,
                "music": r.get("title") or r.get("musicName"),
                "author": r.get("author") or r.get("authorName"),
                "uses": r.get("videoCount") or r.get("usesCount"),
                "duration_s": r.get("duration"),
                "url": r.get("url") or r.get("playUrl"),
                "raw": r,
            })
    return items


def render_md(items: list[dict[str, Any]], *, date: str, mode: str) -> str:
    lines = [
        f"# Music Pulse — {date} ({mode})",
        "",
        "_Trending TikTok sounds Sierra could borrow. Pair with from_trend._",
        "",
    ]
    if not items:
        lines.append("_No sounds aggregated. Run trend_pulse first or pass --keywords._")
        return "\n".join(lines)
    for it in items:
        if "uses_in_pulse" in it:
            ex = it.get("best_example", {})
            lines.append(f"### {it['music']}  ·  {it['uses_in_pulse']} uses today")
            if ex.get("url"):
                lines.append(f"- Best example: [@{ex.get('author')} · {ex.get('plays', 0):,} plays]({ex['url']})")
                lines.append(f"  > {ex.get('caption','')}")
        else:
            lines.append(f"### {it.get('music')}  ·  {it.get('uses', 0):,} total uses")
            lines.append(f"- Keyword: `{it.get('keyword')}`")
            lines.append(f"- Author: {it.get('author','?')} · Duration: {it.get('duration_s','?')}s")
            if it.get("url"):
                lines.append(f"- [open]({it['url']})")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from-pulse", action="store_true", help="Aggregate music from today's trend_pulse JSON (free)")
    p.add_argument("--date", help="Pulse date (YYYY-MM-DD)")
    p.add_argument("--keywords", nargs="+", help="TikTok music keyword search (paid Apify)")
    p.add_argument("--max-per", type=int, default=20)
    p.add_argument("--no-sync", action="store_true")
    args = p.parse_args()

    today = dt.date.today().isoformat()

    if not args.from_pulse and not args.keywords:
        print("[music] pass --from-pulse OR --keywords ...", file=sys.stderr)
        return 1

    items: list[dict[str, Any]] = []
    if args.from_pulse:
        items += aggregate_from_pulse(args.date)
        mode = "from-pulse"
    if args.keywords:
        items += scrape_keyword_sounds(args.keywords, max_per=args.max_per)
        mode = "keyword-scrape" if not args.from_pulse else "combined"

    md = render_md(items, date=today, mode=mode)
    md_path = MUSIC_DIR / f"{today}.md"
    write_markdown(md_path, md)
    dump_json(MUSIC_DIR / f"{today}.json", items)
    print(f"[music] wrote {md_path.relative_to(REPO_ROOT)} ({len(items)} sounds)")

    if not args.no_sync and items:
        try:
            from tools.sync import supabase_client as sync
            top5 = items[:5]
            tldr = "\n".join(f"- {it.get('music','?')}" for it in top5)
            sync.insert_ai_output(
                title=f"Music Pulse — {today}",
                content=f"Top 5 sounds today:\n\n{tldr}\n\nFull: {md_path.relative_to(REPO_ROOT)}",
                kind="text",
                tags=["research", "music", "daily"],
                source_prompt="music_pulse.py",
            )
        except Exception as e:
            print(f"[music] sync skipped: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
