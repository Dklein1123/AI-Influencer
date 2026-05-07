"""Brand-pitch research for Sierra Frost.

Given a brand name (or list), uses Firecrawl to:
  1. Search the web for the brand's official site, recent press, and any
     existing influencer-program signals.
  2. Scrape the most relevant pages (homepage, about, partnerships, contact).
  3. Ask Claude to draft a Sierra-tailored pitch with the specific angle.

Output: `personas/sierra-frost/pitches/<brand-slug>.md`

Usage:
    python -m tools.research.pitch_research "Vuori"
    python -m tools.research.pitch_research --brands "Vuori" "Athleta" "Free People"
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

from .common import claude_score, firecrawl_scrape, firecrawl_search, write_markdown

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "personas" / "sierra-frost" / "pitches"


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


PITCH_PROMPT = """You are drafting an influencer-partnership pitch on behalf of
Sierra Frost — a 25-year-old conservative-leaning lifestyle/dating-commentary
creator. Voice: direct, dry-witty, classy, faith-adjacent, anti-hookup-culture,
high-effort feminine. Audience leans 22–35 women, college-educated, traditional
values, high engagement on dating + lifestyle commentary. Newsletter +
TikTok + Instagram Reels, 9:16 native.

You are given research about a target brand. Output sections, in markdown:

## Brand fit (1-10) + reasoning
## Concrete partnership angles (3 options, ranked)
   For each: format (Reel / TikTok stitch / newsletter feature / UGC),
   specific Sierra-voice hook (one line), deliverables, why it works for
   THIS brand specifically.
## Outreach email draft
   Subject + body, written in Sierra's tone (or in operator's tone if more
   appropriate — say which). Personal references to the brand's actual
   marketing language picked up from the research.
## Risks / things to verify
## Citations
   Links to the pages you used.

Brand: {brand}

Research dump:
{dump}
"""


def research_brand(brand: str, *, max_pages: int = 4) -> dict[str, object]:
    print(f"[pitch] searching '{brand}' …")
    queries = [
        f"{brand} official site",
        f"{brand} influencer program",
        f"{brand} brand partnerships contact",
        f"{brand} marketing campaign 2025 2026",
    ]
    hits: list[dict] = []
    seen_urls: set[str] = set()
    for q in queries:
        try:
            for h in firecrawl_search(q, limit=4, scrape=False):
                u = h.get("url")
                if u and u not in seen_urls:
                    hits.append({"q": q, **h})
                    seen_urls.add(u)
        except Exception as e:
            print(f"[pitch] search '{q}' failed: {e}", file=sys.stderr)
    pages = []
    for h in hits[:max_pages]:
        u = h.get("url")
        if not u:
            continue
        try:
            doc = firecrawl_scrape(u)
            md = doc.get("markdown") or ""
            pages.append({
                "url": u,
                "title": (doc.get("metadata") or {}).get("title") or h.get("title"),
                "markdown": md[:6000],
            })
            print(f"[pitch]   scraped {u} ({len(md)} chars)")
        except Exception as e:
            print(f"[pitch]   scrape {u} failed: {e}", file=sys.stderr)
    return {"brand": brand, "hits": hits, "pages": pages}


def draft_pitch(brand: str, research: dict) -> str:
    pages = research.get("pages") or []
    dump_lines = []
    for p in pages:
        dump_lines.append(f"### {p['title']} — {p['url']}")
        dump_lines.append(p["markdown"])
        dump_lines.append("")
    dump = "\n".join(dump_lines) or "(no pages scraped)"
    try:
        return claude_score(
            PITCH_PROMPT.format(brand=brand, dump=dump),
            model="claude-sonnet-4-6",
            max_tokens=2400,
        )
    except Exception as e:
        return f"_Claude draft failed: {e}_\n\nRaw research:\n\n{dump}"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("brand", nargs="?", help="Single brand name")
    p.add_argument("--brands", nargs="+", help="Multiple brand names")
    p.add_argument("--max-pages", type=int, default=4)
    args = p.parse_args()

    targets = args.brands or ([args.brand] if args.brand else [])
    if not targets:
        print("[pitch] usage: pitch_research.py BRAND  OR  --brands A B C", file=sys.stderr)
        return 1

    today = dt.date.today().isoformat()
    for brand in targets:
        slug = slugify(brand)
        research = research_brand(brand, max_pages=args.max_pages)
        pitch = draft_pitch(brand, research)
        md = f"# {brand} — Pitch Brief ({today})\n\n{pitch}\n\n---\n\n## Search hits\n\n"
        for h in research.get("hits", []):
            md += f"- [{h.get('title','(untitled)')}]({h.get('url')}) — _{h.get('q')}_\n"
        out = OUT_DIR / f"{slug}.md"
        write_markdown(out, md)
        (OUT_DIR / f"{slug}.json").write_text(json.dumps(research, indent=2, default=str))
        print(f"[pitch] wrote {out.relative_to(REPO_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
