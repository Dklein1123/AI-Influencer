"""Comment reply drafter — Sierra-voice replies to top comments.

Pulls top N comments from a target TikTok post (via Apify) and asks
Claude to draft Sierra-voice replies for each. Operator approves them
in the portal AI Outputs Vault before pasting back into TikTok.

Apify actor: `clockworks/free-tiktok-scraper` already returns post
metadata; comments require either `clockworks/tiktok-comments-scraper`
(paid, $0.30 per 1k comments) or scraping the post URL with the
comments flag.

Output: `personas/sierra-frost/replies/<post-id>-<date>.md` with each
comment + suggested reply, ready to copy. Best-effort sync to portal
so replies show up alongside other AI Outputs.

Usage:
    python -m tools.community.reply_drafter --url https://www.tiktok.com/@sierrafrostxyz/video/123456
    python -m tools.community.reply_drafter --url ... --max 15

Requires: ANTHROPIC_API_KEY for drafting (graceful fallback: dumps
comments without drafts so operator can hand-write).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
from typing import Any

from tools.research.common import (
    anthropic_key,
    apify_run_sync,
    claude_score,
    dump_json,
    write_markdown,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
REPLY_DIR = REPO_ROOT / "personas" / "sierra-frost" / "replies"
VOICE_PROFILE = REPO_ROOT / "personas" / "sierra-frost" / "voice-profile.md"


REPLY_PROMPT = """You are Sierra Frost, replying to comments on your latest
TikTok. Your voice is locked — match the cadence, hook, and CTA rules in
the voice profile excerpt below.

Reply rules:
- 1–2 sentences max per reply, ≤180 chars.
- Match the comment's energy: dry → dry, sincere → warm, hostile →
  declarative-not-defensive (acknowledge then reframe), bot/spam → skip
  (output {"skip": true}).
- Never argue politics. Never name a candidate. Never use "as a
  Christian woman" or huns/bestie/babes/queen.
- For genuine questions, give a real micro-answer.
- For praise, thank without sycophancy ("thank you" not "OMG queen").
- For disagreement, hold the line dryly.

Output: a JSON array, ONE OBJECT PER COMMENT, in input order. Each
object: {"id": <int>, "skip": <bool>, "reply": "<text or empty if skipped>",
"why": "<one-sentence rationale>"}

VOICE PROFILE (excerpt)
{voice_excerpt}

POST CONTEXT
Caption: {post_caption}
Theme: {post_theme}

COMMENTS
{comments_block}
"""


def fetch_post_meta(url: str) -> dict[str, Any]:
    """Use clockworks scraper in URL mode to get the post + caption."""
    try:
        rows = apify_run_sync(
            "clockworks/free-tiktok-scraper",
            {"postURLs": [url], "shouldDownloadVideos": False, "shouldDownloadCovers": False},
            max_items=1,
            timeout=180,
        )
    except Exception as e:
        print(f"[reply] post fetch failed: {e}", file=sys.stderr)
        return {}
    return rows[0] if rows else {}


def fetch_comments(url: str, *, max_comments: int = 15) -> list[dict[str, Any]]:
    """Pull comments via the dedicated comments actor."""
    try:
        rows = apify_run_sync(
            "clockworks/tiktok-comments-scraper",
            {"postURLs": [url], "commentsPerPost": max_comments},
            max_items=max_comments,
            timeout=240,
        )
    except Exception as e:
        print(f"[reply] comments fetch failed (may need paid actor): {e}", file=sys.stderr)
        return []
    return rows


def voice_excerpt() -> str:
    if not VOICE_PROFILE.is_file():
        return "(voice profile not found)"
    text = VOICE_PROFILE.read_text()
    # Pull §5 Hooks + §6 CTAs + §9 Reply patterns + §11 Linter rules.
    parts = []
    for marker in ("## 5.", "## 6.", "## 9.", "## 11."):
        m = re.search(rf"^{re.escape(marker)}\s.*?(?=^## )", text, re.M | re.S)
        if m:
            parts.append(m.group(0).strip())
    return "\n\n".join(parts) or text[:4000]


def draft_replies(post: dict[str, Any], comments: list[dict[str, Any]]) -> list[dict]:
    if not comments:
        return []

    # Free-by-default: Gemini text → Claude fallback if available.
    from tools.llm.gemini import is_enabled as gemini_ok, generate_text as gemini_text
    if gemini_ok():
        provider = "gemini"
    elif anthropic_key():
        provider = "claude"
    else:
        print("[reply] no LLM available — emitting comments without drafts", file=sys.stderr)
        return [
            {"id": i + 1, "skip": False, "reply": "", "why": "no LLM key (set GEMINI_API_KEY for free)"}
            for i, _ in enumerate(comments)
        ]

    block = "\n".join(
        f"{i+1}. @{c.get('uniqueId') or c.get('uid','?')}: {c.get('text','')}"
        for i, c in enumerate(comments)
    )
    prompt = (
        REPLY_PROMPT
        .replace("{voice_excerpt}", voice_excerpt())
        .replace("{post_caption}", (post.get("text") or "")[:400])
        .replace("{post_theme}", "(detected from caption)")
        .replace("{comments_block}", block)
    )
    if provider == "gemini":
        raw = gemini_text(prompt, model="gemini-2.5-flash", max_tokens=2400, temperature=0.7, json_mode=True).strip()
    else:
        raw = claude_score(prompt, model="claude-sonnet-4-6", max_tokens=2400).strip()
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip().rsplit("```", 1)[0].strip()
    try:
        return json.loads(raw)
    except Exception:
        print(f"[reply] could not parse {provider} JSON, returning empty", file=sys.stderr)
        print(raw[:500], file=sys.stderr)
        return []


def render_md(post: dict, comments: list[dict], drafts: list[dict]) -> str:
    cap = (post.get("text") or "(unknown caption)").replace("\n", " ").strip()
    url = post.get("webVideoUrl") or "(unknown url)"
    lines = [
        "# Reply Drafts",
        "",
        f"**Post:** [{cap[:140]}…]({url})",
        f"**Plays:** {post.get('playCount', 0):,} · **Comments:** {post.get('commentCount', 0):,}",
        "",
        "---",
        "",
    ]
    for i, c in enumerate(comments):
        d = next((x for x in drafts if x.get("id") == i + 1), {})
        author = c.get("uniqueId") or c.get("uid") or "?"
        text = (c.get("text") or "").strip()
        likes = c.get("diggCount") or 0
        lines.append(f"### {i+1}. @{author}  ·  {likes} ♥")
        lines.append(f"> {text}")
        if d.get("skip"):
            lines.append(f"_skip — {d.get('why','')}_\n")
        elif d.get("reply"):
            lines.append(f"**Reply:** {d['reply']}")
            lines.append(f"_{d.get('why','')}_\n")
        else:
            lines.append("_(no draft — operator hand-write)_\n")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True, help="TikTok post URL")
    p.add_argument("--max", type=int, default=15, help="Max comments to draft for")
    p.add_argument("--no-sync", action="store_true")
    args = p.parse_args()

    print("[reply] fetching post …")
    post = fetch_post_meta(args.url)
    if not post:
        return 1

    print(f"[reply] fetching up to {args.max} comments …")
    comments = fetch_comments(args.url, max_comments=args.max)
    if not comments:
        print("[reply] no comments returned (may need paid actor)", file=sys.stderr)
        # Still write the post stub so operator sees what was attempted.

    print(f"[reply] drafting replies for {len(comments)} comments …")
    drafts = draft_replies(post, comments)

    today = dt.date.today().isoformat()
    post_id = re.search(r"/video/(\d+)", args.url)
    post_id = post_id.group(1) if post_id else "unknown"
    md_path = REPLY_DIR / f"{post_id}-{today}.md"
    write_markdown(md_path, render_md(post, comments, drafts))
    dump_json(REPLY_DIR / f"{post_id}-{today}.json", {"post": post, "comments": comments, "drafts": drafts})
    print(f"[reply] wrote {md_path.relative_to(REPO_ROOT)}")

    if not args.no_sync:
        try:
            from tools.sync import supabase_client as sync
            n_drafted = sum(1 for d in drafts if d.get("reply"))
            sync.insert_ai_output(
                title=f"Reply drafts — post {post_id} ({today})",
                content=f"{n_drafted}/{len(comments)} drafts ready. Path: {md_path.relative_to(REPO_ROOT)}",
                kind="text",
                tags=["replies", "community", post_id],
                source_prompt="reply_drafter.py",
            )
        except Exception as e:
            print(f"[reply] sync skipped: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
