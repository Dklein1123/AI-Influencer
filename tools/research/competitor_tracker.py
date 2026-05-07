"""Competitor tracker for Sierra Frost.

Snapshots a list of competitor accounts (TikTok + Instagram) on demand
via Apify, then writes a comparative brief under
`personas/sierra-frost/competitors/YYYY-MM-DD.md`.

The brief is for the OPERATOR — not for posting. It surfaces:
  - which competitor posted today + engagement
  - their best-performing post in the snapshot window
  - hooks/captions worth borrowing (Sierra-translated)

Apify actors used:
  - `clockworks/free-tiktok-scraper`  (free)
  - `apify/instagram-scraper`         (paid; pay-per-result)

Roster lives in `personas/sierra-frost/competitors.json` so it's editable
without touching code. Format:

    [
      {"platform": "tiktok",    "handle": "exampleuser", "lane": "tradwife"},
      {"platform": "instagram", "handle": "exampleuser", "lane": "modest-fashion"}
    ]

Usage:
    python -m tools.research.competitor_tracker
    python -m tools.research.competitor_tracker --no-instagram --max 8
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys
from typing import Any

from .common import apify_run_sync, dump_json, write_markdown

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ROSTER = REPO_ROOT / "personas" / "sierra-frost" / "competitors.json"
OUT_DIR = REPO_ROOT / "personas" / "sierra-frost" / "competitors"


def load_roster() -> list[dict[str, str]]:
    if not ROSTER.is_file():
        print(f"[comp] no roster at {ROSTER} — run with --init to scaffold", file=sys.stderr)
        return []
    return json.loads(ROSTER.read_text())


def init_roster() -> None:
    if ROSTER.is_file():
        print(f"[comp] roster already exists at {ROSTER}")
        return
    sample = [
        {"platform": "tiktok", "handle": "examplehandle", "lane": "conservative-lifestyle", "notes": "edit me"},
        {"platform": "instagram", "handle": "examplehandle", "lane": "modest-fashion", "notes": "edit me"},
    ]
    ROSTER.parent.mkdir(parents=True, exist_ok=True)
    ROSTER.write_text(json.dumps(sample, indent=2))
    print(f"[comp] wrote roster scaffold to {ROSTER}")


# ---- TikTok ---------------------------------------------------------------

def scrape_tiktok_profile(handle: str, *, max_videos: int = 10) -> list[dict[str, Any]]:
    payload = {
        "profiles": [handle.lstrip("@")],
        "resultsPerPage": max_videos,
        "shouldDownloadCovers": False,
        "shouldDownloadVideos": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }
    try:
        rows = apify_run_sync("clockworks/free-tiktok-scraper", payload, max_items=max_videos, timeout=240)
    except Exception as e:
        print(f"[comp] tiktok @{handle} failed: {e}", file=sys.stderr)
        return []
    out = []
    for r in rows:
        out.append({
            "platform": "tiktok",
            "handle": handle,
            "url": r.get("webVideoUrl"),
            "caption": r.get("text"),
            "plays": r.get("playCount"),
            "likes": r.get("diggCount"),
            "comments": r.get("commentCount"),
            "shares": r.get("shareCount"),
            "created_at": r.get("createTimeISO") or r.get("createTime"),
            "music": (r.get("musicMeta") or {}).get("musicName"),
        })
    return out


# ---- Instagram ------------------------------------------------------------

def scrape_instagram_profile(handle: str, *, max_posts: int = 10) -> list[dict[str, Any]]:
    payload = {
        "directUrls": [f"https://www.instagram.com/{handle.lstrip('@')}/"],
        "resultsType": "posts",
        "resultsLimit": max_posts,
        "addParentData": False,
    }
    try:
        rows = apify_run_sync("apify/instagram-scraper", payload, max_items=max_posts, timeout=300)
    except Exception as e:
        print(f"[comp] instagram @{handle} failed: {e}", file=sys.stderr)
        return []
    out = []
    for r in rows:
        out.append({
            "platform": "instagram",
            "handle": handle,
            "url": r.get("url"),
            "caption": r.get("caption"),
            "likes": r.get("likesCount"),
            "comments": r.get("commentsCount"),
            "video_views": r.get("videoViewCount"),
            "type": r.get("type"),
            "created_at": r.get("timestamp"),
        })
    return out


# ---- Aggregation + render -------------------------------------------------

def best_post(posts: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not posts:
        return None
    def score(p: dict[str, Any]) -> int:
        return (p.get("plays") or 0) + (p.get("likes") or 0) * 10 + (p.get("comments") or 0) * 50
    return max(posts, key=score)


def render(snapshots: dict[str, list[dict[str, Any]]], *, date: str) -> str:
    lines = [
        f"# Competitor Snapshot — {date}",
        "",
        "_Operator-facing only. Hooks / captions worth borrowing in **bold**._",
        "",
    ]
    for key, posts in snapshots.items():
        platform, handle = key.split(":", 1)
        lines.append(f"## {platform} · @{handle} ({len(posts)} posts)")
        if not posts:
            lines.append("- _No posts pulled. Check the handle._")
            lines.append("")
            continue
        bp = best_post(posts)
        if bp:
            engage = (bp.get("plays") or 0) + (bp.get("likes") or 0) + (bp.get("comments") or 0)
            cap = (bp.get("caption") or "").replace("\n", " ").strip()
            lines.append(f"- **Top post** ({engage:,} engagement): [{cap[:100]}…]({bp.get('url')})")
        recent = sorted(posts, key=lambda p: p.get("created_at") or "", reverse=True)[:5]
        lines.append("- Recent:")
        for p in recent:
            cap = (p.get("caption") or "").replace("\n", " ").strip()
            stats = f"{p.get('plays') or p.get('video_views') or 0:,}p · {p.get('likes') or 0:,}♥"
            lines.append(f"  - [{stats}] {cap[:120]}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--init", action="store_true", help="Write a roster scaffold and exit")
    p.add_argument("--max", type=int, default=10, help="Posts per profile")
    p.add_argument("--no-tiktok", action="store_true")
    p.add_argument("--no-instagram", action="store_true")
    p.add_argument("--filter-handle", help="Only scrape this single handle")
    p.add_argument("--no-sync", action="store_true")
    args = p.parse_args()

    if args.init:
        init_roster()
        return 0

    roster = load_roster()
    if not roster:
        return 1
    if args.filter_handle:
        roster = [r for r in roster if r["handle"].lstrip("@") == args.filter_handle.lstrip("@")]
        if not roster:
            print(f"[comp] no roster entry for @{args.filter_handle}", file=sys.stderr)
            return 1

    today = dt.date.today().isoformat()
    snapshots: dict[str, list[dict[str, Any]]] = {}
    for entry in roster:
        plat, handle = entry["platform"], entry["handle"]
        if plat == "tiktok" and args.no_tiktok:
            continue
        if plat == "instagram" and args.no_instagram:
            continue
        print(f"[comp] {plat} @{handle} …")
        if plat == "tiktok":
            snapshots[f"tiktok:{handle}"] = scrape_tiktok_profile(handle, max_videos=args.max)
        elif plat == "instagram":
            snapshots[f"instagram:{handle}"] = scrape_instagram_profile(handle, max_posts=args.max)
        else:
            print(f"[comp] unknown platform '{plat}' for @{handle}", file=sys.stderr)

    md = render(snapshots, date=today)
    md_path = OUT_DIR / f"{today}.md"
    json_path = OUT_DIR / f"{today}.json"
    write_markdown(md_path, md)
    dump_json(json_path, snapshots)
    print(f"[comp] wrote {md_path.relative_to(REPO_ROOT)}")
    print(f"[comp] wrote {json_path.relative_to(REPO_ROOT)}")

    if not args.no_sync:
        try:
            from tools.sync import supabase_client
            count = sum(len(v) for v in snapshots.values())
            supabase_client.insert_ai_output(
                title=f"Competitor Snapshot — {today}",
                content=f"{len(snapshots)} accounts, {count} posts. Report: {md_path.relative_to(REPO_ROOT)}",
                kind="text",
                tags=["research", "competitors"],
                source_prompt="competitor_tracker.py",
                quiet=False,
            )
        except Exception as e:
            print(f"[comp] sync skipped: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
