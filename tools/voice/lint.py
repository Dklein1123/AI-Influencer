"""Deterministic voice-profile linter.

Implements `voice-profile.md §11` — the 10 hard rules that every draft
must pass before it ships. The block-list and allow-list are hard-coded
here for speed; they MUST stay in sync with voice-profile.md §4.
A `--check-sync` mode re-reads the markdown and complains if drift is
detected (run in CI / pre-commit).
"""

from __future__ import annotations

import dataclasses
import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
VOICE_PROFILE = REPO_ROOT / "personas" / "sierra-frost" / "voice-profile.md"


# Hard block list — phrases that must NEVER appear in Sierra-voiced output.
# Mirrors voice-profile.md §4 "Block" + "Block — content / political".
BLOCK_TOKENS: tuple[str, ...] = (
    # Vocabulary block
    "hun", "y'all", "blessed", "girlies", "manifesting", "vibes", "slay",
    "iconic", "queen", "periodt", "no thoughts just",
    "main character", "let her cook", "lowkey", "highkey", "besties",
    "the giggles", "pookie", "spilling", "the receipts", "omg",
    "ugh literally", "i can't", "so real for that",
    # Tribal / political
    "woke", "based", "redpilled", "libtard", "magat",
    "as a christian woman",
    # Catchphrases that signal off-character cheap energy
    "soft girl era", "manifesting my", "ate that",
)

# Multi-word patterns where simple substring matching is too aggressive.
# Use full-word/phrase regex anchored at word boundaries (case-insensitive).
BLOCK_REGEXES: tuple[re.Pattern[str], ...] = tuple(
    re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE) for p in BLOCK_TOKENS
)

# Allowed emoji set (voice-profile §11.8). Sierra uses palm-tree emoji, sparingly.
ALLOWED_EMOJI: frozenset[str] = frozenset({"🌴", "✋", "✌️"})

# Hashtag cap (rule 11.7).
MAX_HASHTAGS: int = 4

# Sentence-length distribution (rule 11.5/11.6).
SHORT_SENTENCE_MAX_WORDS = 12
SHORT_RATIO_REQUIRED = 0.70
ABSOLUTE_SHORT_REQUIRED_AT_OR_OVER_SENTENCES = 2
ABSOLUTE_SHORT_MAX_WORDS = 6


# Phrasing patterns that smell preachy (rule 11.10). Heuristic only — flag,
# don't auto-block, since context can save them.
PREACHY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bremember,?\s+ladies\b", re.IGNORECASE),
    re.compile(r"\bas\s+a\s+(christian|conservative|godly|good)\s+woman\b", re.IGNORECASE),
    re.compile(r"\bI'?ll\s+be\s+praying\s+for\s+", re.IGNORECASE),
    re.compile(r"\bcalled\s+to\s+say\b", re.IGNORECASE),
    re.compile(r"\bif\s+you\s+don'?t\s+agree\s+(you\s+can\s+)?unfollow\b", re.IGNORECASE),
)

# Hook-library signatures (rule 11.4). If a draft is being graded as a TikTok
# voiceover or caption opener, at least one of these patterns should match
# the first sentence. The linter only checks this when --kind=tiktok|reel.
HOOK_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^hot take incoming", re.IGNORECASE),
    re.compile(r"^let me explain this (to you )?slowly", re.IGNORECASE),
    re.compile(r"^make it make sense", re.IGNORECASE),
    re.compile(r"^things conservative women don'?t say", re.IGNORECASE),
    re.compile(r"^pov: ", re.IGNORECASE),
    re.compile(r"^i'?ll say what nobody (else )?will", re.IGNORECASE),
    re.compile(r"^notice how nobody talks about", re.IGNORECASE),
    re.compile(r"^the bar is on the floor", re.IGNORECASE),
    re.compile(r"^three\s+(things|reasons|ways)", re.IGNORECASE),
    re.compile(r"^tell me you'?ve never .* without telling me", re.IGNORECASE),
    re.compile(r"^we need to have a conversation about", re.IGNORECASE),
    re.compile(r"^unpopular opinion:", re.IGNORECASE),
    re.compile(r"^stop trying to make .* happen", re.IGNORECASE),
    re.compile(r"^your reminder that ", re.IGNORECASE),
    re.compile(r"^here'?s what nobody told you", re.IGNORECASE),
    re.compile(r"^i'?m going to need everyone to ", re.IGNORECASE),
    re.compile(r"^quietly judging", re.IGNORECASE),
    re.compile(r"^.* is not a personality", re.IGNORECASE),
    re.compile(r"^pro tip: ", re.IGNORECASE),
    re.compile(r"^\d+\s+\w+\s+I'?m not doing", re.IGNORECASE),
)


@dataclasses.dataclass
class Finding:
    rule: str
    severity: str  # "error" | "warn" | "info"
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper():5}] {self.rule}: {self.message}"


def _split_sentences(text: str) -> list[str]:
    # Cheap sentence splitter — splits on . ! ? followed by whitespace/end,
    # not on `Mr.` / `e.g.` (we don't expect those in captions).
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _word_count(s: str) -> int:
    return len(re.findall(r"\b[\w']+\b", s))


def _emoji_chars(text: str) -> list[str]:
    # Match anything in the supplementary planes that looks like an emoji.
    # Imperfect but good enough for our captions.
    return re.findall(r"[\U0001F300-\U0001FAFF☀-➿✀-➿]", text)


def lint(text: str, *, kind: str = "general") -> list[Finding]:
    """Run all hard rules. Returns a list of findings (empty if perfect)."""
    findings: list[Finding] = []
    if not text or not text.strip():
        findings.append(Finding("11.0", "error", "Empty input."))
        return findings

    # Rule 11.1 — block tokens.
    for pat in BLOCK_REGEXES:
        m = pat.search(text)
        if m:
            findings.append(
                Finding("11.1-block", "error", f"contains blocked phrase: {m.group(0)!r}")
            )

    # Rule 11.10 — preachy patterns (warn, not error).
    for pat in PREACHY_PATTERNS:
        m = pat.search(text)
        if m:
            findings.append(
                Finding("11.10-preachy", "warn", f"sounds preachy: {m.group(0)!r}")
            )

    # Rule 11.7 — hashtag cap.
    hashtags = re.findall(r"#\w+", text)
    if len(hashtags) > MAX_HASHTAGS:
        findings.append(
            Finding(
                "11.7-hashtags",
                "error",
                f"{len(hashtags)} hashtags, max {MAX_HASHTAGS} (found: {' '.join(hashtags)})",
            )
        )

    # Rule 11.8 — emoji policy.
    emojis = _emoji_chars(text)
    bad_emojis = [e for e in emojis if e not in ALLOWED_EMOJI]
    if bad_emojis:
        findings.append(
            Finding(
                "11.8-emoji",
                "warn",
                f"non-allowlisted emojis: {''.join(set(bad_emojis))} (allowed: {''.join(ALLOWED_EMOJI)})",
            )
        )
    if len(emojis) > 1:
        findings.append(
            Finding("11.8-emoji-count", "warn", f"{len(emojis)} emojis used (cap: 1 per caption)")
        )

    # Rule 11.5 / 11.6 — sentence length distribution.
    sentences = _split_sentences(text)
    if len(sentences) >= ABSOLUTE_SHORT_REQUIRED_AT_OR_OVER_SENTENCES:
        wcs = [_word_count(s) for s in sentences]
        short = sum(1 for w in wcs if w <= SHORT_SENTENCE_MAX_WORDS)
        ratio = short / max(1, len(wcs))
        if ratio < SHORT_RATIO_REQUIRED:
            findings.append(
                Finding(
                    "11.5-cadence",
                    "error",
                    f"only {short}/{len(wcs)} ({ratio:.0%}) sentences ≤{SHORT_SENTENCE_MAX_WORDS} words; need ≥{SHORT_RATIO_REQUIRED:.0%}",
                )
            )
        if not any(w <= ABSOLUTE_SHORT_MAX_WORDS for w in wcs):
            findings.append(
                Finding(
                    "11.6-no-punchline",
                    "error",
                    f"no sentence ≤{ABSOLUTE_SHORT_MAX_WORDS} words; Sierra always lands on a short.",
                )
            )

    # Rule 11.4 — hook library check (only when caption-as-hook).
    if kind in ("tiktok", "reel"):
        first = sentences[0] if sentences else ""
        # Strip leading on-screen-text artifacts and emojis.
        first_clean = re.sub(r"^[^\w]+", "", first)
        if not any(p.search(first_clean) for p in HOOK_PATTERNS):
            findings.append(
                Finding(
                    "11.4-hook",
                    "warn",
                    f"opening sentence doesn't match a §5 hook pattern: {first_clean[:60]!r}",
                )
            )

    return findings


def passes(text: str, *, kind: str = "general") -> bool:
    return not any(f.severity == "error" for f in lint(text, kind=kind))


def check_sync_with_markdown() -> list[str]:
    """Re-read voice-profile.md and surface any drift between its block lists
    (vocab block + content/political block + catchphrases in §13 anti-examples)
    and BLOCK_TOKENS hardcoded here.

    The check is one-directional: every BLOCK_TOKENS entry must appear
    somewhere in the document's block-related sections. (We don't require
    the doc to have nothing extra — markdown can list patterns the linter
    can't yet detect deterministically.)

    Returns a list of mismatch messages (empty if synced).
    """
    if not VOICE_PROFILE.is_file():
        return [f"voice profile not found at {VOICE_PROFILE}"]
    text = VOICE_PROFILE.read_text().lower()
    mismatches: list[str] = []
    for tok in BLOCK_TOKENS:
        if tok.lower() not in text:
            mismatches.append(f"BLOCK_TOKENS contains {tok!r} not present anywhere in voice-profile.md")
    return mismatches
