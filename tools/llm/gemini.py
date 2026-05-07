"""Gemini text-LLM wrapper — free planner for Sierra.

Mirrors the `tools.research.common.claude_score(prompt, ...)` interface
so it's a drop-in for any tool that previously needed Anthropic. Use
this by default; fall back to claude_score only when explicitly asked.

Why this exists:
  Operator opted out of paying for Anthropic API. Gemini text models
  (`gemini-2.5-flash`, `gemini-3-pro`, etc.) are FREE on the operator's
  Google project even though Gemini IMAGE models are billing-gated.
  This unlocks the full LLM-driven planner work the rest of Sierra's
  toolchain has been blocked on (from_trend planner, newsletter draft,
  reply drafter, voice profile lints).

Usage:
    from tools.llm.gemini import generate_text
    plan = generate_text(
        "Draft a Sierra Frost Inventory-style script on the trend …",
        model="gemini-2.5-flash",
        max_tokens=1500,
    )

CLI:
    python -m tools.llm.gemini "Write a Sierra-voice cold open about ..."
    python -m tools.llm.gemini --model gemini-3-pro "Explain X"
"""

from __future__ import annotations

import os
import pathlib
import sys


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


# Default to flash — cheapest, fastest, fits 99% of Sierra-script work.
# Override via SIERRA_GEMINI_TEXT_MODEL env or per-call `model=` arg.
DEFAULT_MODEL = "gemini-2.5-flash"


def _key() -> str:
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        raise RuntimeError(
            "GEMINI_API_KEY (or GOOGLE_API_KEY) missing — needed for free LLM. "
            "Get one at https://aistudio.google.com/apikey."
        )
    return k


def generate_text(
    prompt: str,
    *,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.8,
    system: str | None = None,
    retries: int = 3,
    json_mode: bool = False,
) -> str:
    """Generate text from Gemini. Returns the text body.

    `model`: gemini-2.5-flash (default, fastest free) | gemini-3-pro
             (slower but stronger) | any current text-capable model.
    `system`: optional system instruction.
    `retries`: number of retries on 5xx (Gemini free tier hits transient
               503 'high demand' spikes; 3 retries with exponential
               backoff resolves >95% of them).
    """
    from google import genai
    from google.genai import types
    import time

    client = genai.Client(api_key=_key())
    chosen = model or os.environ.get("SIERRA_GEMINI_TEXT_MODEL") or DEFAULT_MODEL

    cfg_kwargs = {
        "max_output_tokens": max_tokens,
        "temperature": temperature,
    }
    if system:
        cfg_kwargs["system_instruction"] = system
    if json_mode:
        # Forces Gemini to emit valid JSON only — no markdown fences, no
        # trailing prose, parsable directly with json.loads.
        cfg_kwargs["response_mime_type"] = "application/json"

    last_err: Exception | None = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=chosen,
                contents=prompt,
                config=types.GenerateContentConfig(**cfg_kwargs),
            )
            return (response.text or "").strip()
        except Exception as e:
            msg = str(e)
            # Retry on transient server errors (503 / 500 / overloaded);
            # don't retry on auth (401/403) or quota (429 = real fail).
            transient = "503" in msg or "500" in msg or "UNAVAILABLE" in msg or "high demand" in msg.lower()
            if transient and attempt < retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"[gemini] transient {msg.split(chr(10))[0][:60]} — retry in {wait}s", file=sys.stderr)
                time.sleep(wait)
                last_err = e
                continue
            raise
    raise last_err if last_err else RuntimeError("gemini: exhausted retries")


# Drop-in alias that matches `tools.research.common.claude_score` shape so
# existing code can swap providers via a single import-line change:
#
#   from tools.research.common import claude_score
#   ↓
#   from tools.llm.gemini import score as claude_score
#
def score(prompt: str, *, model: str | None = None, max_tokens: int = 1024) -> str:
    return generate_text(prompt, model=model, max_tokens=max_tokens)


def is_enabled() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))


def _cli() -> int:
    import argparse
    p = argparse.ArgumentParser(description="Free Gemini text wrapper for Sierra")
    p.add_argument("prompt", help="prompt text")
    p.add_argument("--model", default=None, help="defaults to gemini-2.5-flash")
    p.add_argument("--max-tokens", type=int, default=1024)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--system", help="optional system instruction")
    args = p.parse_args()

    text = generate_text(
        args.prompt,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        system=args.system,
    )
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
