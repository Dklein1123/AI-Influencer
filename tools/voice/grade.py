"""Optional Claude-API-backed voice grader.

For drafts that pass the deterministic linter but might still fail the
"would Sierra actually say this?" sniff test. Costs ~$0.003 per call
on Sonnet 4.6; trivial vs. the value of catching off-voice posts.

Requires `ANTHROPIC_API_KEY` in `~/.AI-Influencer.env` and the `anthropic`
package (`pip install anthropic`).

Returns a structured grade with score (0–10), specific issues, and
suggested rewrites if score < 7.
"""

from __future__ import annotations

import json
import os
import pathlib
import textwrap
from typing import TypedDict

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
VOICE_PROFILE = REPO_ROOT / "personas" / "sierra-frost" / "voice-profile.md"


class Grade(TypedDict):
    score: int
    on_voice: bool
    issues: list[str]
    rewrites: list[str]
    reasoning: str


def _load_env() -> None:
    env = pathlib.Path.home() / ".AI-Influencer.env"
    if env.is_file():
        try:
            from dotenv import load_dotenv

            load_dotenv(env)
        except ImportError:
            for line in env.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())


def grade(draft: str, *, kind: str = "tiktok-caption") -> Grade:
    """Grade a draft against Sierra's voice profile via the Claude API.

    Uses prompt caching on the (large, stable) voice profile so repeated
    calls only pay for the (tiny) draft tokens.
    """
    _load_env()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Add to ~/.AI-Influencer.env to use AI grading."
        )

    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise RuntimeError("`pip install anthropic` to use AI grading.") from e

    if not VOICE_PROFILE.is_file():
        raise FileNotFoundError(f"voice profile not found: {VOICE_PROFILE}")

    profile_text = VOICE_PROFILE.read_text()

    system_prompt = textwrap.dedent(
        """\
        You are the Brand Voice Editor for Sierra Frost, an AI persona. The
        following document defines her voice canonically. Treat it as the
        source of truth — a draft is "on voice" only if a person familiar
        with this document would believe Sierra wrote it.

        For each draft, return ONLY a JSON object with this schema:
        {
          "score": <integer 0-10, where 10 = indistinguishable from Sierra,
                   7+ = ships as-is, 4-6 = needs revision, <4 = throw away>,
          "on_voice": <bool, true iff score >= 7>,
          "issues": <array of short strings, each naming one specific way
                    the draft deviates from the profile>,
          "rewrites": <array of 1-3 alternative drafts that would score 9+,
                      shorter array if the original was already strong>,
          "reasoning": <one sentence explaining the score>
        }

        Be strict. The voice is observational, not preachy. Confident, not
        cute. Dry, not bubbly. If the draft sounds like a generic creator
        bot, that's an automatic <5.
        """
    )

    user_message = textwrap.dedent(
        f"""\
        Voice profile:
        ---
        {profile_text}
        ---

        Draft kind: {kind}
        Draft:
        ---
        {draft}
        ---

        Grade this draft. Reply with the JSON object only.
        """
    )

    client = Anthropic()
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    raw = msg.content[0].text.strip()
    # Strip code fences if present.
    if raw.startswith("```"):
        raw = raw.strip("`").lstrip("json").strip()
    parsed = json.loads(raw)
    return Grade(
        score=int(parsed.get("score", 0)),
        on_voice=bool(parsed.get("on_voice", False)),
        issues=list(parsed.get("issues", [])),
        rewrites=list(parsed.get("rewrites", [])),
        reasoning=str(parsed.get("reasoning", "")),
    )
