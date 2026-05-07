"""Multi-platform repurpose for one Sierra content unit.

Implements the content-engine skill (~/.claude/skills/content-engine/)
mechanically — takes one rendered content-unit dir and emits platform-
native copy variants for TikTok, IG Reels, IG Still/Carousel, X, Newsletter,
and YouTube Shorts. Each variant lives at:

    <unit-dir>/repurpose/<platform>.md

Quality posture: this is the COMPLIANT-TEMPLATES pass — it produces
correct, platform-shaped, slop-free copy that the operator (or a future
LLM polish step) can ship as-is or refine. It enforces the content-engine
quality gate where it can:

  - Each draft reads native for its platform (length, structure, CTA shape)
  - Hooks are pulled from plan.caption / plan.tag_line, never duplicated
  - No generic hype language (slop_scan validates this on the source plan)
  - Copy varies across platforms — no cross-post twin-text

Inputs (read from <unit-dir>/plan.json):
  - voiceover_text  — full natural read of the bit
  - caption         — TikTok caption (already in Sierra voice)
  - tag_line        — the screenshot driver
  - script_chunks   — timestamped subtitle chunks
  - hashtags        — list
  - bit_id          — sierra_reads / calling_my_dad / brad_finance / sierra_apologist

Plus the rendered files (used as cross-references in the copy):
  - visual.png
  - final_with_card.mp4

Usage:
    python -m tools.scheduler.repurpose path/to/unit-dir
    python -m tools.scheduler.repurpose path/to/unit-dir --platforms tiktok,x,newsletter
    python -m tools.scheduler.repurpose path/to/unit-dir --quote-card  # also emit X quote-card PNG
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# ---- Platform rendering ----------------------------------------------------

def _hashtag_str(plan: dict[str, Any], extra: list[str] | None = None) -> str:
    tags = list(plan.get("hashtags", []))
    if extra:
        tags = tags + [t for t in extra if t not in tags]
    return " ".join(tags[:4])  # voice-profile §11 max 4 hashtags


def _bit_handle(bit_id: str | None) -> str:
    return {
        "sierra_reads": "Sierra Reads",
        "calling_my_dad": "Calling My Dad",
        "brad_finance": "Brad From Finance",
        "sierra_apologist": "Sierra Apologist",
    }.get(bit_id or "", "Sierra")


def render_tiktok(plan: dict[str, Any]) -> str:
    """TikTok caption: ≤150 chars, plus pinned-comment + hashtags."""
    cap = plan.get("caption", "")
    if len(cap) > 150:
        cap = cap[:147].rstrip() + "..."
    pinned = "Newsletter goes out Sunday — link in bio. 🌴"
    return f"""# TikTok — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## Caption (≤150 chars; paste into TikTok directly)

{cap}

## Hashtags (max 4)

{_hashtag_str(plan)}

## Pinned comment (post immediately after publish)

{pinned}

## Posting slot

Per voice-profile §5.6: 80% comedy / 15% bit-and-pivot / 5% serious. Run
this bit ~2x/week. Best slot: weekday 8:45–9:15 PM ET (peak lane window)
or Sunday 9:30–10 AM ET if it's a soft-mode post.

## Source files

- video: ../final_with_card.mp4 (1.5s title card + reel)
- raw:   ../final.mp4 (no title card)
- still: ../visual.png
"""


def render_ig_reel(plan: dict[str, Any]) -> str:
    """IG Reel caption — longer-form, multi-paragraph, soft CTA."""
    vo = plan.get("voiceover_text", "")
    tag = plan.get("tag_line", "")
    bit = _bit_handle(plan.get("bit_id"))
    cap = (
        f"{vo}\n\n"
        f"{tag}\n\n"
        f"More {bit} on TikTok. Sunday newsletter has the unfiltered cut — link in bio. 🌴"
    )
    return f"""# Instagram Reel — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## Caption (multi-paragraph, IG-native)

{cap}

## First-comment (auto-post immediately after publish)

If you saw yourself in this, the newsletter goes deeper. Link in bio.

## Hashtags

{_hashtag_str(plan)} #fyp #relatable #datingtok

## Posting slot

1–2 hours after the TikTok cross-post. Do NOT post simultaneously —
TikTok algorithm favors first-publish content; IG cross-posts >1h
later don't trip the duplicate-content suppression.

## Source files

- video: ../final_with_card.mp4
- still: ../visual.png
"""


def render_ig_still(plan: dict[str, Any]) -> str:
    """IG single still/quote-card with the tag_line as the screenshot."""
    tag = plan.get("tag_line", "")
    cap = plan.get("caption", "")
    return f"""# Instagram Still / Quote Card — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## Quote card text (overlay on visual.png)

> {tag}

## Caption (under the image)

{cap}

## Hashtags

{_hashtag_str(plan)}

## Posting slot

Wednesday 6:30 PM ET (IG single-post peak per voice-profile §7).
Use only if the bit's tag_line is fridge-line worthy on its own;
otherwise skip and lean carousel.

## How to render the card

```bash
python -m tools.scheduler.repurpose <unit-dir> --quote-card
# → writes repurpose/x_quote_card.png (1080x1920 visual + tag overlay)
```
"""


def render_ig_carousel(plan: dict[str, Any]) -> str:
    """IG carousel — one slide per script chunk."""
    chunks = plan.get("script_chunks", [])
    tag = plan.get("tag_line", "")
    bit = _bit_handle(plan.get("bit_id"))

    slides = []
    for i, c in enumerate(chunks):
        slides.append(f"### Slide {i+1}\n> {c['text']}")
    if not chunks:
        slides.append("_(No script_chunks in plan; skip carousel.)_")
    if chunks:
        slides.append(f"### Slide {len(chunks)+1}\n_(End card)_\n\n**{bit}** · Sunday newsletter in bio 🌴")

    cap = (
        f"{tag}\n\n"
        f"Swipe the receipts. Newsletter Sunday — link in bio."
    )

    return f"""# Instagram Carousel — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## Slide-by-slide

{chr(10).join(slides)}

## Caption (under the carousel)

{cap}

## Hashtags

{_hashtag_str(plan)}

## Posting slot

Friday afternoon, 4:30 PM ET (per voice-profile §7 — primes the
weekend scroll). Carousels save more than single posts; this is
the format to use when the tag_line earns the screenshot.
"""


def render_x(plan: dict[str, Any]) -> str:
    """Single tweet + thread option."""
    tag = plan.get("tag_line", "")
    cap = plan.get("caption", "")
    chunks = plan.get("script_chunks", [])

    # Split the script into a thread — one chunk per tweet so each beat
    # gets its own reveal. Cap at 6 to avoid spamming; if more than 6
    # chunks, fold the middle chunks together. Always reserve the last
    # tweet for the tag_line on its own (the screenshot driver).
    thread_tweets: list[str] = []
    if chunks:
        chunk_texts = [c.get("text", "").strip() for c in chunks]
        chunk_texts = [t for t in chunk_texts if t]
        if len(chunk_texts) <= 6:
            thread_tweets = chunk_texts[:-1] if len(chunk_texts) > 1 else chunk_texts[:]
        else:
            # Keep first 4 separate, fold middle, keep last separate.
            thread_tweets = chunk_texts[:4] + [" ".join(chunk_texts[4:-1])]
        # Always end with the tag_line as its own tweet (the punch).
        if tag and (not thread_tweets or thread_tweets[-1] != tag):
            thread_tweets.append(tag)
    if not thread_tweets:
        thread_tweets = [tag or cap]

    thread_block = "\n\n".join(f"**{i+1}/** {t}" for i, t in enumerate(thread_tweets))

    return f"""# X (Twitter) — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## Single tweet (default — Sierra's tag is screenshot-bait)

{tag}

## Thread option (use when bit needs setup → payoff)

{thread_block}

## Quote-card alternative

Post the visual.png with `{tag}` overlaid as a quote card. X rewards
image-based posts in the algo and Sierra's faces compound recognition.

## Hashtags

Use 1–2 max on X. Skip the TikTok hashtags (different algo). Suggested:
{_hashtag_str(plan, extra=[])}

## Posting slot

X works on a different schedule. For Sierra's lane: weekday morning
(7–9 AM ET) when the conservative commentary feed wakes up. Pin the
tweet for 24 hours if it's the bit's signature line.
"""


def render_newsletter(plan: dict[str, Any]) -> str:
    """Newsletter blurb — 2–3 sentences pointing back to the reel."""
    tag = plan.get("tag_line", "")
    bit = _bit_handle(plan.get("bit_id"))
    rationale = (plan.get("rationale", "") or "").split(".")[0]
    return f"""# Newsletter snippet — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## In-issue blurb (drop into Sunday newsletter)

> **{bit}, EP. {plan.get('episode', 1)}.**
>
> {tag}
>
> [Watch the full bit →](https://tiktok.com/@sierrafrostxyz)

## Section context

Use under the "This Week On TikTok" section of the newsletter. If
multiple bits posted that week, list 2–3 max. For longer treatment:

> {rationale}

## CTA

The newsletter is the funnel destination — keep TikTok→email pinned
on the reel and the reel→newsletter pinned in the issue. Bidirectional
loop.
"""


def render_youtube_short(plan: dict[str, Any]) -> str:
    tag = plan.get("tag_line", "")
    vo = plan.get("voiceover_text", "")
    bit = _bit_handle(plan.get("bit_id"))
    title = (tag if len(tag) <= 60 else tag[:57] + "...") + " #shorts"
    return f"""# YouTube Short — `{plan.get('bit_id','sierra')}` ep {plan.get('episode',1)}

## Title (≤100 chars; YouTube indexes hard on title)

{title}

## Description

{vo}

—

{bit}, ep {plan.get('episode', 1)}. Newsletter Sunday: [link]

## Tags

{_hashtag_str(plan)} #shorts #datingtok

## Posting slot

YouTube Shorts run on a longer half-life than TikTok — daytime
weekday upload (10 AM – 1 PM ET) catches the YT algo's 24h push.
"""


# ---- Optional: quote-card PNG (visual + tag_line overlay) ------------------

def render_quote_card(unit_dir: pathlib.Path, plan: dict[str, Any]) -> pathlib.Path | None:
    """Render visual.png + tag_line overlay as a 1080x1920 quote card.

    Used for X / IG single-post / Pinterest. Returns the path or None
    if visual.png is missing.

    Uses drawtext's `textfile=` parameter to avoid the ffmpeg-quoting
    nightmare with colons (e.g. '2:51'), apostrophes, and special chars
    in tag_lines.
    """
    visual = unit_dir / "visual.png"
    if not visual.is_file():
        return None
    tag = plan.get("tag_line", "")
    if not tag:
        return None
    out_dir = unit_dir / "repurpose"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "quote_card.png"

    # Write the tag_line to a temp text file — drawtext reads it via
    # `textfile=`, sidestepping ffmpeg filter-string escaping entirely.
    tag_file = out_dir / ".quote_card_text.txt"
    tag_file.write_text(tag)

    font = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Black.ttf"
    fc = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,setsar=1,format=rgb24,"
        f"drawbox=x=0:y=h-180:w=iw:h=180:color=black@0.7:t=fill,"
        f"drawtext=fontfile={font}:textfile={tag_file}:"
        f"fontcolor=white:fontsize=64:x=(w-text_w)/2:y=h-text_h-58"
        f"[v]"
    )
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(visual),
        "-filter_complex", fc,
        "-map", "[v]",
        "-frames:v", "1",
        str(out),
    ]
    try:
        subprocess.run(cmd, check=True)
        return out
    except subprocess.CalledProcessError as e:
        print(f"[repurpose] quote-card render failed: {e}", file=sys.stderr)
        return None
    finally:
        # Clean up temp text file (don't let it pollute the repurpose dir).
        try:
            tag_file.unlink()
        except FileNotFoundError:
            pass


# ---- Orchestration ---------------------------------------------------------

PLATFORMS = {
    "tiktok":         render_tiktok,
    "ig_reel":        render_ig_reel,
    "ig_still":       render_ig_still,
    "ig_carousel":    render_ig_carousel,
    "x":              render_x,
    "newsletter":     render_newsletter,
    "youtube_short":  render_youtube_short,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("unit_dir", type=pathlib.Path, help="Path to a content-units/ subdir")
    p.add_argument("--platforms", help="Comma-separated subset; default = all")
    p.add_argument("--quote-card", action="store_true", help="Also render quote_card.png")
    p.add_argument("--clean", action="store_true", help="Delete existing repurpose/ first")
    args = p.parse_args()

    unit = args.unit_dir.resolve()
    plan_path = unit / "plan.json"
    if not plan_path.is_file():
        print(f"[repurpose] no plan.json at {plan_path}", file=sys.stderr)
        return 1
    plan = json.loads(plan_path.read_text())

    out_dir = unit / "repurpose"
    if args.clean and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected = args.platforms.split(",") if args.platforms else list(PLATFORMS.keys())
    written = []
    for plat in selected:
        plat = plat.strip()
        renderer = PLATFORMS.get(plat)
        if not renderer:
            print(f"[repurpose] unknown platform '{plat}'; skipping", file=sys.stderr)
            continue
        body = renderer(plan)
        f = out_dir / f"{plat}.md"
        f.write_text(body)
        written.append(f.relative_to(REPO_ROOT))

    if args.quote_card:
        qc = render_quote_card(unit, plan)
        if qc:
            written.append(qc.relative_to(REPO_ROOT))

    print(f"[repurpose] wrote {len(written)} file(s):")
    for w in written:
        print(f"  {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
