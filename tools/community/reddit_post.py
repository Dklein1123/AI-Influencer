"""Reddit posting via PRAW (free, official API, ~30 req/min).

Implements the Reddit-funnel strategy from
`docs/research/free-stack-deep-2026.md §5`. Free OSS, Apache-2 license.

CONFIG

Add to ~/.AI-Influencer.env (one-time):

    REDDIT_CLIENT_ID=...        # from reddit.com/prefs/apps "script" type
    REDDIT_CLIENT_SECRET=...
    REDDIT_USERNAME=...         # Sierra's reddit handle
    REDDIT_PASSWORD=...
    REDDIT_USER_AGENT=sierra-frost-bot/0.1

WORKFLOW (per voice-profile §1.5 + research-agent §5)

  Days 1-30: comment-only. Use `comment` mode in target subs to build
             500+ comment karma. Lead with substance, not links.
  Days 30-60: text-self posts referencing TikTok content
             ("Got asked about X on TikTok, what do you all think?")
  Days 60+:  pivot — selfposts that mention TikTok handle organically.

SAFE SUBS (Sierra's lane, AI-tolerant or text-first)
  r/RedPillWomen, r/AskWomenOver30, r/datingoverthirty, r/dating_advice
  r/Femcels, r/conservative, r/ConservativeDating

RISK SUBS (image rules — comment-only, never image-post)
  r/femalefashionadvice (real-person OOTD only since 2021)
  r/AmIUgly, r/AmIPretty (real-photo verification)

Usage:
    # Submit a text post
    python -m tools.community.reddit_post submit RedPillWomen \\
        "Anyone else feel like 'decenter men' is just... cope?" \\
        --body "Got into a debate with a friend on TikTok about this..."

    # Comment on the latest hot post in a sub
    python -m tools.community.reddit_post comment-on-hot RedPillWomen \\
        --comment-text "Hard agree on point 3. The hardest part is..." \\
        --rank 1

    # Post the Sunday newsletter blurb to a list of subs
    python -m tools.community.reddit_post cross-post-newsletter \\
        --md personas/sierra-frost/newsletter/2026-05-07.md \\
        --subs RedPillWomen ConservativeDating
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
import textwrap
from typing import Any


def _load_env() -> None:
    env = pathlib.Path.home() / ".AI-Influencer.env"
    if not env.is_file():
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(env)
    except ImportError:
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())


_load_env()


# Sub fitness — encoded from research-agent + voice-profile §1.5.
# image_ok = whether AI image posts are allowed (True for most text-first
# subs; False for OOTD/photo-verification subs).
SUB_PROFILE = {
    "RedPillWomen":      {"image_ok": False, "tier": "primary",  "lane": "trad-feminine"},
    "AskWomenOver30":    {"image_ok": False, "tier": "primary",  "lane": "lifestyle-advice"},
    "datingoverthirty":  {"image_ok": False, "tier": "primary",  "lane": "dating-advice"},
    "dating_advice":     {"image_ok": False, "tier": "primary",  "lane": "dating-advice"},
    "Femcels":           {"image_ok": False, "tier": "secondary","lane": "venting-text"},
    "conservative":      {"image_ok": False, "tier": "primary",  "lane": "political"},
    "ConservativeDating":{"image_ok": False, "tier": "primary",  "lane": "trad-feminine"},
    "femalefashionadvice":{"image_ok": False,"tier": "comment-only","lane": "fashion (real-person OOTD only)"},
    "AmIUgly":           {"image_ok": False, "tier": "skip",     "lane": "real-photo verification"},
    "AmIPretty":         {"image_ok": False, "tier": "skip",     "lane": "real-photo verification"},
}


def _client() -> Any:
    """Build a PRAW Reddit client from env. Raises if not configured."""
    import praw
    cfg = {
        "client_id":     os.environ.get("REDDIT_CLIENT_ID"),
        "client_secret": os.environ.get("REDDIT_CLIENT_SECRET"),
        "username":      os.environ.get("REDDIT_USERNAME"),
        "password":      os.environ.get("REDDIT_PASSWORD"),
        "user_agent":    os.environ.get("REDDIT_USER_AGENT", "sierra-frost-bot/0.1"),
    }
    missing = [k for k, v in cfg.items() if not v and k != "user_agent"]
    if missing:
        raise RuntimeError(
            "Reddit env not configured. Missing: " + ", ".join(missing) +
            "\n\nAdd these to ~/.AI-Influencer.env:\n" +
            "  REDDIT_CLIENT_ID=... (from reddit.com/prefs/apps, type=script)\n"
            "  REDDIT_CLIENT_SECRET=...\n"
            "  REDDIT_USERNAME=...\n"
            "  REDDIT_PASSWORD=...\n"
            "  REDDIT_USER_AGENT=sierra-frost-bot/0.1"
        )
    return praw.Reddit(**cfg)


def is_enabled() -> bool:
    return bool(
        os.environ.get("REDDIT_CLIENT_ID")
        and os.environ.get("REDDIT_CLIENT_SECRET")
        and os.environ.get("REDDIT_USERNAME")
        and os.environ.get("REDDIT_PASSWORD")
    )


def submit(
    sub: str,
    title: str,
    *,
    body: str | None = None,
    url: str | None = None,
    flair: str | None = None,
) -> str:
    """Submit a text or link post. Returns the new submission's permalink."""
    profile = SUB_PROFILE.get(sub, {})
    if profile.get("tier") == "skip":
        raise RuntimeError(f"Sub '{sub}' is in the skip tier ({profile.get('lane')})")
    if profile.get("tier") == "comment-only" and url:
        print(f"[reddit] WARNING: r/{sub} prefers comment-only — link post will likely get removed",
              file=sys.stderr)

    reddit = _client()
    sr = reddit.subreddit(sub)
    if url:
        s = sr.submit(title, url=url, flair_id=flair)
    elif body is not None:
        s = sr.submit(title, selftext=body, flair_id=flair)
    else:
        raise ValueError("Need either --body or --url")
    return f"https://reddit.com{s.permalink}"


def comment_on_hot(
    sub: str,
    *,
    rank: int = 1,
    comment_text: str,
) -> str:
    """Comment on the Nth hottest post in a sub. Returns comment permalink."""
    reddit = _client()
    sr = reddit.subreddit(sub)
    posts = list(sr.hot(limit=max(rank, 5)))
    if rank < 1 or rank > len(posts):
        raise ValueError(f"rank {rank} out of range — got {len(posts)} hot posts")
    target = posts[rank - 1]
    c = target.reply(comment_text)
    return f"https://reddit.com{c.permalink}"


def cross_post_newsletter(md_path: pathlib.Path, subs: list[str]) -> list[str]:
    """Cross-post a newsletter blurb to multiple subs.

    Reads the first 'h1' as the title and the body as selftext.
    Truncates to first 5000 chars (Reddit selftext limit is 40k but
    long posts under-perform).
    """
    text = pathlib.Path(md_path).read_text()
    lines = text.splitlines()
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "Sierra weekly")
    # Strip the H1 line + trailing whitespace/lint blocks.
    body_lines = []
    in_lint = False
    for l in lines:
        if l.startswith("# "):
            continue
        if l.startswith("## Lint"):
            in_lint = True
            continue
        if in_lint:
            continue
        body_lines.append(l)
    body = "\n".join(body_lines).strip()[:5000]
    body = textwrap.dedent(body)

    permalinks = []
    for sub in subs:
        try:
            url = submit(sub, title, body=body)
            permalinks.append(url)
            print(f"[reddit] posted to r/{sub} → {url}")
        except Exception as e:
            print(f"[reddit] r/{sub} failed: {e}", file=sys.stderr)
    return permalinks


def list_safe_subs() -> None:
    """Print the safe / risky / skip tiers for Sierra's reference."""
    by_tier: dict[str, list[str]] = {}
    for sub, info in SUB_PROFILE.items():
        by_tier.setdefault(info["tier"], []).append(sub)
    for tier in ("primary", "secondary", "comment-only", "skip"):
        if tier not in by_tier:
            continue
        print(f"\n{tier.upper()}:")
        for sub in by_tier[tier]:
            info = SUB_PROFILE[sub]
            print(f"  r/{sub:24s} {info['lane']}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("submit", help="submit a text or link post")
    s.add_argument("sub")
    s.add_argument("title")
    s.add_argument("--body")
    s.add_argument("--url")
    s.add_argument("--flair")

    c = sp.add_parser("comment-on-hot", help="comment on the Nth hottest post")
    c.add_argument("sub")
    c.add_argument("--rank", type=int, default=1)
    c.add_argument("--comment-text", required=True)

    x = sp.add_parser("cross-post-newsletter", help="cross-post a newsletter md")
    x.add_argument("--md", type=pathlib.Path, required=True)
    x.add_argument("--subs", nargs="+", required=True)

    sp.add_parser("list-subs", help="show the curated sub list")

    args = p.parse_args()

    if args.cmd == "list-subs":
        list_safe_subs()
        return 0
    if args.cmd == "submit":
        url = submit(args.sub, args.title, body=args.body, url=args.url, flair=args.flair)
        print(url)
    elif args.cmd == "comment-on-hot":
        url = comment_on_hot(args.sub, rank=args.rank, comment_text=args.comment_text)
        print(url)
    elif args.cmd == "cross-post-newsletter":
        urls = cross_post_newsletter(args.md, args.subs)
        for u in urls:
            print(u)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
