"""Post-performance analyzer for Sierra Frost.

Closes the data feedback loop: pulls the last N TikTok posts from
Sierra's own profile, buckets them by template/hook-style/music type,
and writes a ranked report to
`personas/sierra-frost/analytics/YYYY-MM.md`.

Without a Metricool subscription this uses Apify's free TikTok scraper
on Sierra's public profile. Once Metricool is wired we'll add an
adapter (richer data: saves, profile views, follow rate per post).

Bucketing heuristics (no labels needed):
- Template: pulled from caption tags (we tag posts with `#P3`, `#P32`,
  etc. when we publish — see content-units convention).
- Hook style: detected by first 4 words pattern-matched against
  voice-profile §5 hook library.
- Music type: original / trending / silent (from `musicMeta`).

Output also auto-updates `viral-playbook.md` with a "Last 30-day
top 3 patterns" block at the top, so future generations bias toward
what's actually working.

Usage:
    python -m tools.analytics.post_perf --handle sierrafrostxyz
    python -m tools.analytics.post_perf --handle sierrafrostxyz --max 60
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from typing import Any

from tools.research.common import apify_run_sync, dump_json, write_markdown

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ANALYTICS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "analytics"
PLAYBOOK = REPO_ROOT / "personas" / "sierra-frost" / "viral-playbook.md"


HOOK_PATTERNS = {
    "Unpopular opinion": re.compile(r"^\s*unpopular\s+opinion", re.I),
    "Standards aren't": re.compile(r"^\s*standards\s+aren'?t", re.I),
    "Real take": re.compile(r"^\s*real\s+take", re.I),
    "Stop calling": re.compile(r"^\s*stop\s+calling", re.I),
    "Nobody asked": re.compile(r"^\s*nobody\s+asked", re.I),
    "Question reframe": re.compile(r"^\s*\w+,\s*\w+\?\s*(no|yes)\.", re.I),
    "If you": re.compile(r"^\s*if\s+you('re|\s+are)\s+", re.I),
    "Direct claim": re.compile(r"^\s*[A-Z][a-z]+\s+is\s+", re.I),
}

TEMPLATE_RE = re.compile(r"#(P[1-9]\d?)\b", re.I)


def fetch_profile(handle: str, *, max_videos: int = 30) -> list[dict[str, Any]]:
    payload = {
        "profiles": [handle.lstrip("@")],
        "resultsPerPage": max_videos,
        "shouldDownloadCovers": False,
        "shouldDownloadVideos": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }
    try:
        return apify_run_sync(
            "clockworks/free-tiktok-scraper", payload, max_items=max_videos, timeout=300
        )
    except Exception as e:
        print(f"[perf] scrape failed: {e}", file=sys.stderr)
        return []


def detect_template(caption: str) -> str | None:
    m = TEMPLATE_RE.search(caption or "")
    return m.group(1).upper() if m else None


def detect_hook(caption: str) -> str:
    first = (caption or "").splitlines()[0] if caption else ""
    for label, rx in HOOK_PATTERNS.items():
        if rx.search(first):
            return label
    return "Other"


def detect_music_kind(row: dict) -> str:
    mm = row.get("musicMeta") or {}
    name = (mm.get("musicName") or "").lower()
    if mm.get("musicOriginal"):
        return "original"
    if name and ("original sound" in name or "sonido original" in name):
        return "original"
    if mm.get("playCount") and mm.get("playCount") > 50_000:
        return "trending"
    return "trending" if name else "silent"


def engagement(row: dict) -> int:
    return (
        (row.get("playCount") or 0)
        + (row.get("diggCount") or 0) * 5
        + (row.get("commentCount") or 0) * 25
        + (row.get("shareCount") or 0) * 50
    )


def bucket_stats(rows: list[dict], key_fn) -> list[tuple[str, int, float]]:
    """Returns [(bucket, n_posts, mean_engagement), ...] sorted desc by mean eng."""
    buckets: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        buckets[key_fn(r)].append(engagement(r))
    out = [
        (k, len(v), sum(v) / max(len(v), 1))
        for k, v in buckets.items()
    ]
    out.sort(key=lambda t: t[2], reverse=True)
    return out


def render_md(rows: list[dict], *, handle: str, month: str) -> str:
    n = len(rows)
    if not n:
        return f"# Post Performance — @{handle} ({month})\n\nNo posts returned. Check the handle.\n"

    by_template = bucket_stats(rows, lambda r: detect_template(r.get("text") or "") or "untagged")
    by_hook = bucket_stats(rows, lambda r: detect_hook(r.get("text") or ""))
    by_music = bucket_stats(rows, lambda r: detect_music_kind(r))

    top_posts = sorted(rows, key=engagement, reverse=True)[:5]

    lines = [
        f"# Post Performance — @{handle} ({month})",
        "",
        f"**Posts analyzed:** {n} · _via Apify clockworks/free-tiktok-scraper_",
        "",
        "## By template",
        "| Template | Posts | Mean engagement |",
        "|---|---|---|",
    ]
    for k, c, m in by_template:
        lines.append(f"| {k} | {c} | {int(m):,} |")

    lines += ["", "## By hook style", "| Hook | Posts | Mean engagement |", "|---|---|---|"]
    for k, c, m in by_hook:
        lines.append(f"| {k} | {c} | {int(m):,} |")

    lines += ["", "## By music kind", "| Kind | Posts | Mean engagement |", "|---|---|---|"]
    for k, c, m in by_music:
        lines.append(f"| {k} | {c} | {int(m):,} |")

    lines += ["", "## Top 5 posts"]
    for r in top_posts:
        cap = (r.get("text") or "").replace("\n", " ").strip()
        lines.append(
            f"- {engagement(r):,} eng · {r.get('playCount',0):,} plays · "
            f"[{cap[:90]}…]({r.get('webVideoUrl','')})"
        )

    lines += ["", "## Recommended biases for next 30 days"]
    if by_template[0][1] >= 2:
        lines.append(f"- Lean into template **{by_template[0][0]}** — top mean eng.")
    if by_hook[0][1] >= 2:
        lines.append(f"- Lean into hook style **{by_hook[0][0]}** — top mean eng.")
    if by_music[0][1] >= 2:
        lines.append(f"- Lean into music kind **{by_music[0][0]}** — top mean eng.")
    lines.append("")
    return "\n".join(lines)


def update_playbook(rows: list[dict]) -> None:
    """Inject a 'Last 30-day top patterns' block at top of viral-playbook.md."""
    if not PLAYBOOK.is_file():
        return
    by_template = bucket_stats(rows, lambda r: detect_template(r.get("text") or "") or "untagged")
    by_hook = bucket_stats(rows, lambda r: detect_hook(r.get("text") or ""))
    if not by_template or not by_hook:
        return
    block = (
        "<!-- AUTO-GENERATED post_perf.py — last 30-day top patterns -->\n"
        f"_Updated {dt.date.today().isoformat()}_\n\n"
        f"**Top template:** {by_template[0][0]} (mean {int(by_template[0][2]):,} eng across {by_template[0][1]} posts)\n"
        f"**Top hook:** {by_hook[0][0]} (mean {int(by_hook[0][2]):,} eng across {by_hook[0][1]} posts)\n"
        "<!-- END AUTO-GENERATED -->\n\n"
    )
    text = PLAYBOOK.read_text()
    if "<!-- AUTO-GENERATED post_perf.py" in text:
        text = re.sub(
            r"<!-- AUTO-GENERATED post_perf\.py.*?<!-- END AUTO-GENERATED -->\n\n",
            block,
            text,
            flags=re.S,
        )
    else:
        text = block + text
    PLAYBOOK.write_text(text)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--handle", required=True, help="Sierra's TikTok handle (no @)")
    p.add_argument("--max", type=int, default=30)
    p.add_argument("--no-sync", action="store_true")
    p.add_argument("--no-playbook-update", action="store_true")
    args = p.parse_args()

    rows = fetch_profile(args.handle, max_videos=args.max)
    if not rows:
        return 1
    print(f"[perf] pulled {len(rows)} posts for @{args.handle}")

    month = dt.date.today().strftime("%Y-%m")
    md = render_md(rows, handle=args.handle, month=month)
    md_path = ANALYTICS_DIR / f"{month}.md"
    write_markdown(md_path, md)
    dump_json(ANALYTICS_DIR / f"{month}.json", rows)
    print(f"[perf] wrote {md_path.relative_to(REPO_ROOT)}")

    if not args.no_playbook_update:
        update_playbook(rows)
        print("[perf] updated viral-playbook.md auto-block")

    if not args.no_sync:
        try:
            from tools.sync import supabase_client as sync
            sync.insert_ai_output(
                title=f"Post Performance — {month}",
                content=f"@{args.handle} · {len(rows)} posts. Report: {md_path.relative_to(REPO_ROOT)}",
                kind="text",
                tags=["analytics", "performance", month],
                source_prompt="post_perf.py",
            )
        except Exception as e:
            print(f"[perf] sync skipped: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
