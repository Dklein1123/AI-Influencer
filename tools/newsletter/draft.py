"""Beehiiv-ready newsletter drafter for Sierra Frost.

Reads the last 7 days of trends + content units, then asks Claude
(Sonnet) to draft a 600-word newsletter issue in Sierra's locked voice
(per `personas/sierra-frost/voice-profile.md`). Output is markdown
ready to paste into Beehiiv / Substack / ConvertKit.

Lints the draft against the voice profile's §11 linter rules; surfaces
any failures inline so the operator can edit before publishing.

Usage:
    python -m tools.newsletter.draft
    python -m tools.newsletter.draft --days 14
    python -m tools.newsletter.draft --topic "this week's tradwife discourse"

Requires: ANTHROPIC_API_KEY.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
TRENDS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "trends"
UNITS_DIR = REPO_ROOT / "personas" / "sierra-frost" / "content-units"
NL_DIR = REPO_ROOT / "personas" / "sierra-frost" / "newsletter"
VOICE_PROFILE = REPO_ROOT / "personas" / "sierra-frost" / "voice-profile.md"


PROMPT = """You are Sierra Frost, drafting this week's newsletter issue.
Your voice is locked: read VOICE PROFILE below before writing a single
word. Match the cadence rules, hook library, and CTA library exactly.
600 words ± 50. One section. No bullet-list filler. No subheadings
unless the issue genuinely has 2 movements.

Structure:
- Open with a §5 hook that earns the read (1-2 sentences max).
- One central observation tied to this week's trend signal.
- Two supporting lines or one short personal anecdote (no last names,
  no real-person identification).
- A landing — the dry payoff.
- A §6 CTA pointing to the new TikTok / Reel queued this week.

Tone: dry, direct, classy. Faith-adjacent ok, never sermon. Anti-
victim, anti-hookup. Do NOT name politicians. Do NOT use "as a
Christian woman". Do NOT use "huns / bestie / babes / queen".

Output format: pure markdown body. No frontmatter. First line is the
opening hook. Last line is the CTA + signature ("— Sierra").

VOICE PROFILE
{voice_profile}

THIS WEEK'S TRENDS (top items, scored)
{trends_summary}

THIS WEEK'S CONTENT UNITS (already shipped or queued)
{content_summary}

OPERATOR TOPIC HINT (optional, weight lightly)
{topic_hint}
"""

LINT_PROMPT = """Lint the following draft against the rules in §11 of the
Sierra Frost voice profile (provided below). For each rule, output one
line: PASS or FAIL with a one-sentence reason. End with a final line
"VERDICT: PASS" or "VERDICT: FAIL".

RULES (§11)
{rules}

DRAFT
{draft}
"""


def load_recent_trends(days: int) -> list[dict]:
    cutoff = dt.date.today() - dt.timedelta(days=days)
    trends: list[dict] = []
    for p in sorted(TRENDS_DIR.glob("*.json"), reverse=True):
        try:
            day = dt.date.fromisoformat(p.stem)
        except ValueError:
            continue
        if day < cutoff:
            break
        items = json.loads(p.read_text())
        for it in items:
            if (it.get("score") or 0) >= 7:
                trends.append({"date": p.stem, **it})
    return trends


def load_recent_units(days: int) -> list[str]:
    cutoff = dt.datetime.now() - dt.timedelta(days=days)
    out = []
    for d in sorted(UNITS_DIR.iterdir(), reverse=True):
        if not d.is_dir() and not d.name.endswith(".md"):
            continue
        try:
            mtime = dt.datetime.fromtimestamp(d.stat().st_mtime)
        except OSError:
            continue
        if mtime < cutoff:
            continue
        out.append(d.name)
    return out


def summarize_trends(trends: list[dict]) -> str:
    if not trends:
        return "(no high-scoring trends in window)"
    lines = []
    for t in trends[:10]:
        score = t.get("score", "?")
        label = (t.get("label") or "")[:140]
        angle = (t.get("angle") or "")[:140]
        lines.append(f"- [{score}/10] ({t.get('date')}) {label} — angle: {angle}")
    return "\n".join(lines)


def extract_voice_section(text: str, section_marker: str) -> str:
    """Extract a numbered section like '## 11.' through to next '## '."""
    import re
    m = re.search(rf"^{re.escape(section_marker)}\s.*?(?=^## )", text, re.M | re.S)
    return m.group(0).strip() if m else ""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--topic", default="", help="Optional operator topic hint")
    p.add_argument("--no-sync", action="store_true")
    p.add_argument("--no-lint", action="store_true")
    args = p.parse_args()

    if not VOICE_PROFILE.is_file():
        print(f"[nl] voice profile missing at {VOICE_PROFILE}", file=sys.stderr)
        return 1

    voice_profile = VOICE_PROFILE.read_text()
    trends = load_recent_trends(args.days)
    units = load_recent_units(args.days)
    print(f"[nl] {len(trends)} high-scoring trends + {len(units)} units in last {args.days}d")

    from tools.research.common import claude_score, anthropic_key
    if not anthropic_key():
        print("[nl] ANTHROPIC_API_KEY missing — cannot draft. Add to ~/.AI-Influencer.env", file=sys.stderr)
        return 2

    prompt = (
        PROMPT
        .replace("{voice_profile}", voice_profile)
        .replace("{trends_summary}", summarize_trends(trends))
        .replace("{content_summary}", "\n".join(f"- {u}" for u in units) or "(none)")
        .replace("{topic_hint}", args.topic or "(none)")
    )
    print("[nl] sonnet drafting …")
    draft = claude_score(prompt, model="claude-sonnet-4-6", max_tokens=2200).strip()

    lint_report = ""
    if not args.no_lint:
        rules = extract_voice_section(voice_profile, "## 11.") or "(rules section not found)"
        lint_prompt = LINT_PROMPT.replace("{rules}", rules).replace("{draft}", draft)
        try:
            lint_report = claude_score(lint_prompt, model="claude-haiku-4-5-20251001", max_tokens=800).strip()
        except Exception as e:
            lint_report = f"(lint skipped: {e})"

    today = dt.date.today().isoformat()
    out_md = NL_DIR / f"{today}.md"
    body = (
        f"# Sierra Frost — Newsletter draft ({today})\n\n"
        f"_Generated by tools.newsletter.draft over the last {args.days} days._\n\n"
        f"---\n\n{draft}\n\n---\n\n"
        f"## Lint report\n\n```\n{lint_report}\n```\n"
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(body)
    print(f"[nl] wrote {out_md.relative_to(REPO_ROOT)}")

    if not args.no_sync:
        try:
            from tools.sync import supabase_client as sync
            sync.insert_ai_output(
                title=f"Newsletter draft — {today}",
                content=f"600w newsletter draft from {len(trends)} top trends. Lint: "
                        f"{'PASS' if 'VERDICT: PASS' in lint_report else 'see file'}. "
                        f"Path: {out_md.relative_to(REPO_ROOT)}",
                kind="text",
                tags=["newsletter", "draft", today],
                source_prompt="newsletter.draft",
            )
        except Exception as e:
            print(f"[nl] sync skipped: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
