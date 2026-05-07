"""Daily trend pulse for Sierra Frost.

Pulls signal from three lanes Sierra cares about:
  1. TikTok hashtags    – via Apify (clockworks/free-tiktok-scraper or paid)
  2. Conservative news  – via Firecrawl /search across vetted publications
  3. Cultural pulse     – Firecrawl scrape on a few aggregators

Then asks Claude to score each item for Sierra-fit on a 1–10 scale and
output the top picks as a markdown digest under
`personas/sierra-frost/trends/YYYY-MM-DD.md`.

Best-effort sync: pushes a TL;DR row into the portal's ai_outputs
via tools.sync.supabase_client so it shows up in the AI Outputs Vault.

Usage:
    python -m tools.research.trend_pulse
    python -m tools.research.trend_pulse --hashtags conservativewomen tradlife --max 30

Env (in ~/.AI-Influencer.env):
    APIFY_API_TOKEN       (required for TikTok)
    FIRECRAWL_API_KEY     (required for news)
    ANTHROPIC_API_KEY     (optional — without it, scoring is skipped)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

from .common import (
    apify_run_sync,
    claude_score,
    dump_json,
    firecrawl_search,
    write_markdown,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRENDS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "trends"


# Sierra's lane: conservative-leaning lifestyle, dating commentary, faith-adjacent
DEFAULT_HASHTAGS = [
    "conservativewomen",
    "tradwife",
    "highvaluewoman",
    "femininity",
    "datingadvice",
    "modestfashion",
]

DEFAULT_NEWS_QUERIES = [
    "conservative dating culture trend 2026",
    "viral tradwife discourse this week",
    "high value woman dating advice viral",
    "modest fashion trend tiktok",
    "feminine energy commentary going viral",
]


# ---- TikTok via Apify -----------------------------------------------------

def fetch_tiktok_hashtag(hashtag: str, *, max_items: int = 20) -> list[dict[str, Any]]:
    """Use the free clockworks TikTok scraper. Returns trimmed records."""
    payload = {
        "hashtags": [hashtag],
        "resultsPerPage": max_items,
        "shouldDownloadCovers": False,
        "shouldDownloadVideos": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }
    try:
        rows = apify_run_sync("clockworks/free-tiktok-scraper", payload, max_items=max_items, timeout=240)
    except Exception as e:
        print(f"[trend] tiktok scrape failed for #{hashtag}: {e}", file=sys.stderr)
        return []
    out = []
    for r in rows:
        out.append({
            "hashtag": hashtag,
            "url": r.get("webVideoUrl") or r.get("videoUrl"),
            "author": (r.get("authorMeta") or {}).get("name"),
            "caption": r.get("text"),
            "plays": r.get("playCount"),
            "likes": r.get("diggCount"),
            "comments": r.get("commentCount"),
            "shares": r.get("shareCount"),
            "created_at": r.get("createTimeISO") or r.get("createTime"),
            "music": (r.get("musicMeta") or {}).get("musicName"),
        })
    return out


# ---- News via Firecrawl ---------------------------------------------------

def fetch_news(queries: list[str], *, per_query: int = 5) -> list[dict[str, Any]]:
    items = []
    for q in queries:
        try:
            hits = firecrawl_search(q, limit=per_query, scrape=False)
        except Exception as e:
            print(f"[trend] firecrawl search failed for '{q}': {e}", file=sys.stderr)
            continue
        for h in hits:
            items.append({
                "query": q,
                "title": h.get("title"),
                "url": h.get("url"),
                "snippet": h.get("description") or h.get("snippet"),
            })
    return items


# ---- Sierra-fit scoring via Claude ---------------------------------------

SCORING_PROMPT = """You are a content strategist for Sierra Frost — a 25-year-old
conservative-leaning lifestyle/dating-commentary AI influencer. Her voice:
direct, dry-witty, classy, faith-adjacent, anti-victim-mentality, pro-traditional
dating, anti-hookup-culture, high-effort feminine. She uses TikTok, Instagram
Reels, and a newsletter. No politics-explicit takes. No mocking.

Below is a list of trending items (hashtags, posts, news headlines). For each
one, output a JSON object with:
  - id (1-indexed)
  - score (1-10) — how strong a Sierra-fit it is
  - angle — one sentence for how Sierra would cover it (her voice)
  - format — best format (Reel hook / TikTok stitch / Newsletter take / Skip)
  - why — one sentence why it scored that way

Return a JSON array, one object per input item, in input order. No prose
outside the array.

Items:
{items}
"""


def score_with_claude(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Returns scored items sorted descending by score."""
    if not items:
        return []
    numbered = "\n".join(
        f"{i+1}. [{it.get('source','?')}] {it.get('label','')}" for i, it in enumerate(items)
    )
    try:
        raw = claude_score(SCORING_PROMPT.format(items=numbered))
    except Exception as e:
        print(f"[trend] scoring skipped: {e}", file=sys.stderr)
        return [{**it, "score": None, "angle": None, "format": None} for it in items]
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip().rsplit("```", 1)[0].strip()
    try:
        scored = json.loads(text)
    except Exception:
        print("[trend] could not parse Claude JSON; raw output below:", file=sys.stderr)
        print(text[:500], file=sys.stderr)
        return [{**it, "score": None, "angle": None, "format": None} for it in items]
    out = []
    for i, it in enumerate(items):
        match = next((s for s in scored if s.get("id") == i + 1), {})
        out.append({**it, **{k: match.get(k) for k in ("score", "angle", "format", "why")}})
    out.sort(key=lambda x: (x.get("score") or 0), reverse=True)
    return out


# ---- Markdown render -------------------------------------------------------

def render_markdown(items: list[dict[str, Any]], *, date: str) -> str:
    top = [it for it in items if (it.get("score") or 0) >= 7]
    skip = [it for it in items if it.get("format") == "Skip"]
    lines = [
        f"# Trend Pulse — {date}",
        "",
        f"_Generated by tools/research/trend_pulse.py — sources: Apify TikTok, Firecrawl search, Claude Haiku scoring._",
        "",
        f"**Items scanned:** {len(items)} · **Top picks (≥7):** {len(top)} · **Skipped:** {len(skip)}",
        "",
        "## Top picks",
        "",
    ]
    if not top:
        lines.append("_No items scored ≥7 today. Lower-tier picks below._")
        lines.append("")
    for it in top:
        lines.extend(_render_item(it))
    if items and not top:
        lines.append("## Lower-tier")
        lines.append("")
        for it in items[:10]:
            lines.extend(_render_item(it))
    lines.append("---")
    lines.append("## Raw items (JSON)")
    lines.append("")
    lines.append("See `trends/<date>.json` for the full data dump.")
    return "\n".join(lines)


def _render_item(it: dict[str, Any]) -> list[str]:
    score = it.get("score")
    label = it.get("label", "")
    url = it.get("url", "")
    src = it.get("source", "?")
    angle = it.get("angle") or "_(no angle)_"
    fmt = it.get("format") or "_(no format)_"
    why = it.get("why") or ""
    return [
        f"### [{score}/10] {label}",
        f"- **Source:** {src}" + (f" · [link]({url})" if url else ""),
        f"- **Angle:** {angle}",
        f"- **Format:** {fmt}",
        f"- **Why:** {why}",
        "",
    ]


# ---- Orchestration --------------------------------------------------------

def normalize_tiktok(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        cap = (r.get("caption") or "").replace("\n", " ").strip()
        plays = r.get("plays") or 0
        out.append({
            "source": f"TikTok #{r.get('hashtag')}",
            "label": f"@{r.get('author','?')} · {plays:,} plays · {cap[:140]}",
            "url": r.get("url"),
            "raw": r,
        })
    return out


def normalize_news(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        out.append({
            "source": "News",
            "label": f"{r.get('title','(untitled)')} — {(r.get('snippet') or '')[:140]}",
            "url": r.get("url"),
            "raw": r,
        })
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Daily trend pulse for Sierra Frost")
    p.add_argument("--hashtags", nargs="+", default=DEFAULT_HASHTAGS, help="TikTok hashtags to scan")
    p.add_argument("--max", type=int, default=15, help="Max TikTok items per hashtag")
    p.add_argument("--news-queries", nargs="+", default=DEFAULT_NEWS_QUERIES)
    p.add_argument("--per-query", type=int, default=4, help="News results per query")
    p.add_argument("--no-tiktok", action="store_true")
    p.add_argument("--no-news", action="store_true")
    p.add_argument("--no-score", action="store_true", help="Skip Claude scoring")
    p.add_argument("--no-sync", action="store_true", help="Skip portal sync")
    args = p.parse_args()

    today = dt.date.today().isoformat()
    print(f"[trend] {today} — hashtags={len(args.hashtags)} news={len(args.news_queries)}")

    items: list[dict[str, Any]] = []
    if not args.no_tiktok:
        for tag in args.hashtags:
            print(f"[trend] tiktok #{tag} …")
            items += normalize_tiktok(fetch_tiktok_hashtag(tag, max_items=args.max))
    if not args.no_news:
        print("[trend] firecrawl news …")
        items += normalize_news(fetch_news(args.news_queries, per_query=args.per_query))

    if not items:
        print("[trend] no items collected — check API keys / quotas", file=sys.stderr)
        return 1

    print(f"[trend] collected {len(items)} items, scoring …")
    scored = items if args.no_score else score_with_claude(items)

    md = render_markdown(scored, date=today)
    md_path = TRENDS_DIR / f"{today}.md"
    json_path = TRENDS_DIR / f"{today}.json"
    write_markdown(md_path, md)
    dump_json(json_path, scored)
    print(f"[trend] wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"[trend] wrote {json_path.relative_to(REPO_ROOT)}")

    if not args.no_sync:
        try:
            from tools.sync import supabase_client
            top = [s for s in scored if (s.get("score") or 0) >= 7]
            tldr_lines = [f"- [{s.get('score')}/10] {s.get('label','')[:160]}" for s in top[:5]]
            tldr = "\n".join(tldr_lines) or "_No high-fit picks today._"
            supabase_client.insert_ai_output(
                title=f"Trend Pulse — {today}",
                content=f"Top picks ({len(top)} ≥7):\n\n{tldr}\n\nFull report: {md_path.relative_to(REPO_ROOT)}",
                kind="text",
                tags=["research", "trends", "daily"],
                source_prompt="trend_pulse.py",
                quiet=False,
            )
            print("[trend] synced summary to portal AI Outputs")
        except Exception as e:
            print(f"[trend] portal sync skipped: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
