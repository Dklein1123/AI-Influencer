"""Exa neural search for Sierra research.

Exa (formerly Metaphor) is a semantic search API. For Sierra's lane,
it's the better tool than Firecrawl /search when:

  - Looking for similar creators by content (semantic, not keyword)
  - Finding niche newsletters / Substacks Sierra could pitch to or
    reference
  - Surfacing high-engagement comedy clips by vibe rather than tag
  - Backfilling research for the comedy-anatomy doc with new comedians
    in adjacent lanes

Firecrawl is still the right tool for: scraping a known URL, search
by query string, plain SERP. Exa is for: "find me sites that feel like
this site" / neural relevance.

Usage:
    from tools.research.exa_search import find_similar, search

    # neural search by query
    results = search("conservative comedy female creator dating commentary",
                     num_results=10)

    # find sites/articles similar to a known anchor
    similar = find_similar("https://www.alexclark.com/podcast",
                           num_results=10)

CLI:
    python -m tools.research.exa_search "feminine energy tiktok creators 2026"
    python -m tools.research.exa_search --similar https://example.com/article
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


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


EXA_BASE = "https://api.exa.ai"


def _key() -> str:
    k = os.environ.get("EXA_API_KEY")
    if not k:
        raise RuntimeError("EXA_API_KEY missing from env. Get one at https://exa.ai")
    return k


def _post(endpoint: str, body: dict[str, Any]) -> dict[str, Any]:
    """Direct REST call — bypasses exa_py SDK because its DNS lookup
    fails in some sandboxed environments. The SDK is fine in normal
    setups; this implementation just doesn't depend on it.
    """
    import httpx
    r = httpx.post(
        f"{EXA_BASE}{endpoint}",
        headers={"x-api-key": _key(), "content-type": "application/json"},
        json=body,
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def search(
    query: str,
    *,
    num_results: int = 10,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    text: bool = True,
    type: str = "neural",
) -> list[dict[str, Any]]:
    """Neural / keyword search.

    `type='neural'` (default) = embedding-based. `'keyword'` = traditional
    SERP. `'auto'` lets Exa choose. Neural is the move for Sierra-lane
    creator discovery.
    """
    body: dict[str, Any] = {
        "query": query,
        "numResults": num_results,
        "type": type,
    }
    if include_domains:
        body["includeDomains"] = include_domains
    if exclude_domains:
        body["excludeDomains"] = exclude_domains
    if text:
        body["contents"] = {"text": True}
    return _normalize(_post("/search", body))


def find_similar(
    url: str,
    *,
    num_results: int = 10,
    text: bool = True,
) -> list[dict[str, Any]]:
    """Given a URL, find semantically similar pages."""
    body: dict[str, Any] = {"url": url, "numResults": num_results}
    if text:
        body["contents"] = {"text": True}
    return _normalize(_post("/findSimilar", body))


def _normalize(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten Exa REST response into a list of dicts."""
    out = []
    for r in response.get("results", []) or []:
        text = (r.get("text") or "")
        out.append({
            "title":   r.get("title") or "",
            "url":     r.get("url") or "",
            "score":   r.get("score"),
            "published_date": r.get("publishedDate") or r.get("published_date"),
            "author":  r.get("author") or "",
            "text":    (text[:600] + "…") if len(text) > 600 else text,
        })
    return out


# ---- CLI -------------------------------------------------------------------

def _print_results(results: list[dict[str, Any]]) -> None:
    if not results:
        print("(no results)", file=sys.stderr)
        return
    for i, r in enumerate(results, 1):
        score = f" [score={r['score']:.2f}]" if r.get("score") is not None else ""
        date = f" ({r['published_date'][:10]})" if r.get("published_date") else ""
        print(f"\n{i}. {r['title']}{score}{date}")
        print(f"   {r['url']}")
        if r.get("author"):
            print(f"   by {r['author']}")
        if r.get("text"):
            snippet = r["text"].replace("\n", " ").strip()
            print(f"   {snippet[:240]}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("query", nargs="?", help="search query")
    p.add_argument("--similar", help="URL to find similar pages for (overrides query)")
    p.add_argument("--num", type=int, default=10)
    p.add_argument("--type", choices=["neural", "keyword", "auto"], default="neural")
    p.add_argument("--include", action="append", help="restrict to these domains (repeatable)")
    p.add_argument("--exclude", action="append", help="exclude these domains (repeatable)")
    p.add_argument("--no-text", action="store_true", help="skip page-text retrieval (faster)")
    args = p.parse_args()

    if args.similar:
        results = find_similar(args.similar, num_results=args.num, text=not args.no_text)
    elif args.query:
        results = search(
            args.query,
            num_results=args.num,
            include_domains=args.include,
            exclude_domains=args.exclude,
            type=args.type,
            text=not args.no_text,
        )
    else:
        print("Provide a query or --similar URL", file=sys.stderr)
        return 1

    _print_results(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
