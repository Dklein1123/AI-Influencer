# `tools.voice` — Sierra brand voice linter

Two-mode quality gate for any AI-generated text in Sierra's voice
(captions, scripts, replies, bios, newsletter copy, brand-pitch language).

- **Deterministic linter** — implements all 10 hard rules from
  `personas/sierra-frost/voice-profile.md §11`. Free, instant, ~80% of
  the failures the project will ever produce.
- **AI grader (optional)** — calls Claude Sonnet 4.6 with the full voice
  profile in a cached system prompt. Catches the harder
  *"would Sierra actually say this?"* judgments. ~$0.003 per call.

## Install

The deterministic mode is stdlib-only — nothing to install.

For AI grading:

```bash
.venv/bin/pip install -r tools/voice/requirements.txt
# Add to ~/.AI-Influencer.env:
echo "ANTHROPIC_API_KEY=sk-ant-..." >> ~/.AI-Influencer.env
```

## Use

```bash
# Lint stdin
echo "OMG girlies obsessed with this 🥺 #queen #slay" | python -m tools.voice

# Lint a file
python -m tools.voice --file draft.txt

# As a TikTok caption (also checks §5 hook library match)
python -m tools.voice --kind tiktok --file draft.txt

# Lint + AI grade (Claude judgment + suggested rewrites)
python -m tools.voice --grade --file draft.txt

# CI / pre-commit: verify lint constants and the markdown profile haven't drifted
python -m tools.voice --check-sync
```

## Exit codes

- `0` — passes all hard rules (and AI grade ≥7 if `--grade`)
- `1` — at least one hard-rule error, or AI grade <7
- `2` — empty input or other failure

## What the linter actually checks

| Rule | Severity | What |
|---|---|---|
| 11.1 block | error | Token list from voice-profile.md §4 (vocab + content/political) |
| 11.4 hook | warn | First sentence (TikTok/reel) matches a §5 hook pattern |
| 11.5 cadence | error | ≥70% of sentences ≤12 words |
| 11.6 punchline | error | At least one sentence ≤6 words |
| 11.7 hashtags | error | ≤4 hashtags total |
| 11.8 emoji | warn | Only 🌴 ✋ ✌️; ≤1 per caption |
| 11.10 preachy | warn | Heuristic patterns: "remember, ladies", "as a christian woman", etc |

The remaining rules (11.2 candidate names, 11.3 in-group declarations,
11.9 CTA distribution) are intentionally *not* enforced deterministically
— they require document-level context that's the AI grader's job.

## Suggested integration

- Pre-commit hook: lint every staged caption file
- Editor command: bind `python -m tools.voice` to a keystroke
- CI: `python -m tools.voice --check-sync` should be a required check
- Eventually: in-portal "lint-as-you-type" panel using the same rules
