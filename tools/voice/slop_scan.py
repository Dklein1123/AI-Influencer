"""Slop-density scanner for Sierra drafts.

Mirrors the rules in `~/.claude/skills/ai-slop-detector/` + the additional
anti-slop list in `personas/sierra-frost/voice-profile.md §11.5`. Run on
any plan.json before render.

Usage:
    python -m tools.voice.slop_scan PATH/TO/plan.json
    python -m tools.voice.slop_scan PATH/TO/plan.json --strict   # fail on score >= 1.0
    python -m tools.voice.slop_scan personas/.../plan.json --field voiceover_text
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

# ---- Tier 1 — high-confidence AI markers (3 points each) -------------------

TIER1 = {
    # Power verbs (overinflated)
    "delve", "embark", "unleash", "unlock", "revolutionize", "spearhead",
    "spearheaded", "foster", "harness", "elevate", "transcend", "forge",
    "ignite", "propel", "catalyze", "galvanize", "amplify",
    # Sophistication signals
    "multifaceted", "nuanced", "intricate", "meticulous", "meticulously",
    "profound", "holistic", "robust", "pivotal", "paramount",
    "indispensable", "quintessential", "comprehensive",
    # Metaphor abuse
    "tapestry", "beacon", "realm", "landscape", "symphony", "mosaic",
    "crucible", "labyrinth", "odyssey", "cornerstone", "bedrock",
    "linchpin", "nexus",
    # Display verbs
    "showcasing", "exemplifying", "demonstrating", "illuminating",
    "underscoring", "epitomizing",
}

# ---- Tier 2 — medium-confidence (2 points each) ----------------------------

TIER2 = {
    # Transition overuse
    "moreover", "furthermore", "subsequently", "consequently",
    "additionally", "likewise", "nonetheless", "henceforth", "thereby",
    "whereby",
    # Hedging stacks
    "potentially", "arguably", "presumably", "ostensibly", "conceivably",
    "seemingly",
    # Intensity
    "significantly", "substantially", "fundamentally", "profoundly",
    "dramatically", "tremendously", "remarkably", "exceedingly",
    "immensely", "vastly",
    # Business jargon
    "leverage", "synergy", "scalability", "actionable", "deliverables",
    "stakeholders", "paradigm", "disruptive", "ecosystem",
    # Tech buzzwords (avoid as adjectives)
    "transformative", "seamless", "best-in-class",
}

# ---- Tier 3 — phrase patterns (instant-fail / -4 each) ---------------------

PHRASES_FAIL = [
    "in today's fast-paced",
    "it's worth noting",
    "at its core",
    "cannot be overstated",
    "a testament to",
    "navigate the complexities",
    "unlock the potential",
    "treasure trove",
    "game changer", "game-changing",
    "look no further",
    "nestled in the heart",
    "embark on a journey",
    "ever-evolving landscape",
    "hustle and bustle",
    # Sycophant filler
    "i'd be happy to",
    "great question",
    "wonderful point",
    "you're absolutely right",
    # Meta-commentary openers
    "let's dive in",
    "in this video",
    "stay tuned",
    "without further ado",
    "hi guys",
    "what's up guys",
    "welcome back",
    # Imaginary scenarios
    "imagine you are",
    "imagine you're",
    "picture this",
    # Hype adjectives
    "mind-blowing",
    "life-changing",
]

# ---- Run --------------------------------------------------------------------

def scan_text(text: str) -> dict:
    text_low = text.lower()
    words = re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", text_low)
    n_words = len(words) or 1

    t1 = [w for w in words if w in TIER1]
    t2 = [w for w in words if w in TIER2]
    fails = [p for p in PHRASES_FAIL if p in text_low]
    em = text.count("—")

    score = (len(t1) * 3 + len(t2) * 2 + len(fails) * 4) / n_words * 100
    em_per_1k = em * 1000 / n_words

    if score < 1.0:
        rating = "Clean"
    elif score < 2.5:
        rating = "Light — spot remediation"
    elif score < 5.0:
        rating = "Moderate — section rewrite"
    else:
        rating = "Heavy — full review"

    return {
        "n_words": n_words,
        "tier1_hits": t1,
        "tier2_hits": t2,
        "fail_phrases": fails,
        "em_dashes": em,
        "em_per_1k": round(em_per_1k, 1),
        "score": round(score, 2),
        "rating": rating,
    }


def scan_plan(plan_path: pathlib.Path, *, fields: list[str] | None = None) -> dict:
    data = json.loads(plan_path.read_text())
    fields = fields or ["voiceover_text", "caption", "tag_line"]
    parts = [str(data.get(f, "")) for f in fields if data.get(f)]
    text = " ".join(parts)
    return scan_text(text)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("plan", type=pathlib.Path, help="path to a plan.json")
    p.add_argument("--field", action="append", help="scan specific field(s); default: voiceover_text + caption + tag_line")
    p.add_argument("--strict", action="store_true", help="exit 1 if score >= 1.0")
    args = p.parse_args()

    if not args.plan.is_file():
        print(f"plan file not found: {args.plan}", file=sys.stderr)
        return 1

    report = scan_plan(args.plan, fields=args.field)
    plan_rel = args.plan.name
    print(f"\nSlop scan: {plan_rel}")
    print(f"  words={report['n_words']}")
    print(f"  Tier 1 hits ({len(report['tier1_hits'])}): {report['tier1_hits']}")
    print(f"  Tier 2 hits ({len(report['tier2_hits'])}): {report['tier2_hits']}")
    print(f"  Fail phrases ({len(report['fail_phrases'])}): {report['fail_phrases']}")
    print(f"  Em-dashes: {report['em_dashes']} ({report['em_per_1k']}/1k words)")
    print(f"  SCORE: {report['score']}  →  {report['rating']}")
    if args.strict and report["score"] >= 1.0:
        print("\nFAIL (--strict): score >= 1.0", file=sys.stderr)
        return 2
    if report["fail_phrases"]:
        print("\nFAIL: forbidden phrases present", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
