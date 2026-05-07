# Sierra Toolkit — Installed Claude Code Skills

> User uploaded 20 skills (May 7 2026). All installed at `~/.claude/skills/`
> and live in the current Claude Code session via the `Skill` tool. This
> doc maps each skill to where it plugs into Sierra's workflow.

## Tier 1 — direct-fit, used daily

| Skill | What it does | Where it plugs in |
|---|---|---|
| **ai-slop-detector** (`ai-slop-detector-1`) | Vocabulary + structural + phrase patterns to detect AI tells in prose. Tier1/Tier2/Tier3 marker lists, density score 0–10, remediation guidance. | **Wired into `from_trend.py` as a pre-flight check.** Every render auto-fails if the plan trips a fail-phrase OR scores >=1.0. Also: standalone CLI at `tools/voice/slop_scan.py PATH`. |
| **viral-reel-generator** | Hook-pattern library (negative urgency / curiosity gap / counter-intuitive / specificity slam / visual interrupt). "Punchy" vs "Deep Dive" style profiles. Strict anti-slop rules (no 3-word loops, no rhetorical lists, no meta-commentary, no hype adjectives, no fake scenarios). | **Anti-slop rules baked into `voice-profile.md §11.5`.** Hook patterns extend the §5 hook library. The "test" for rhetorical lists encoded explicitly: "if removing the pattern keeps the joke, it was filler — kill it." |
| **social-media-algorithm-strategist** (`viral-video-platform-algorithms`) | TikTok/YT/IG/FB algorithm 2025–2026 deep dive. Cold-start mechanics, faceless content stats (340% subscriber-growth advantage), AI-tool comparisons. | Backs the algorithm intel in `viral-genius.md` and the new `voice-profile.md §0a`. Faceless-content note: AI influencers (like Sierra) get a 3x engagement advantage. |
| **tiktok-manager** | TikTok-specific: caption/hook/script writing, FYP optimization, trend research. | Plug into `tools/research/trend_pulse.py` workflow when a trend needs deeper TikTok-specific analysis. Use when drafting captions for the 4 bit-rotation slots. |
| **content-engine** | One-source-asset → many-platforms. Adapt one Sierra reel into TikTok + IG Reel + LinkedIn (eventually) + newsletter snippet + Twitter quote-card. | Future build: `tools/scheduler/repurpose.py` reads a content-unit dir and emits platform-specific cuts. Not yet wired. |

## Tier 2 — periodic / on-demand

| Skill | What it does | Where it plugs in |
|---|---|---|
| **anysite-trend-analysis** | Multi-platform trend detection (Twitter / Reddit / YT / LinkedIn / IG) via anysite MCP. | Alternative trend-pulse source. Currently we use Apify for TikTok; this skill covers cross-platform when we want broader trend signals. |
| **anysite-influencer-discovery** | Same MCP but for finding creators/competitors. | Replaces or supplements `tools/research/competitor_tracker.py` for non-TikTok platforms. |
| **apify-influencer-discovery** (`-copy` variant) | Apify-based competitor discovery (IG/FB/YT/TikTok). | We already use Apify directly in `tools/research/competitor_tracker.py`. Skill provides a structured workflow + reference scripts. |
| **apify-audience-analysis** | Audience demographics + behavior across FB/IG/YT/TikTok via Apify. | NEW capability — we don't have audience analysis yet. Plug into `tools/analytics/post_perf.py` once Sierra has posts to analyze. |
| **social-media-manager** | Strategic social media planning. Calendars, community management, audit framing. Includes a `social_calendar_generator.py` script. | Plug into the weekly content-calendar build. Future: `tools/scheduler/calendar.py` extends this. |
| **social-media-strategist-2** (`social-content`) | Per-post drafting across LinkedIn/X/IG/TikTok/FB. Includes scheduling integration. | Use when Sierra expands beyond TikTok-primary into LinkedIn/X distribution. Lower priority right now. |
| **social-persona-creator** | Interactive prompt to design a new AI persona. | Future: when we add a SECOND persona to the AI-Influencer stable. |

## Tier 3 — image / video gen alternatives

| Skill | What it does | Where it plugs in |
|---|---|---|
| **nano-banana-pro** (Google Gemini 3 Pro Image) | Text-to-image + image-to-image edit via Google's Nano Banana Pro. 1K/2K/4K resolutions. | **Alt image-gen backend.** Currently we use Replicate Flux + Sierra LoRA. Nano Banana Pro is good for: (1) hero shots where v1 LoRA fails close-up identity, (2) image-edits (add/remove elements, change background) we can't do in Flux without ControlNet, (3) 4K versions for landing-page hero use. Wire as `--backend nano-banana` in `from_trend.py`. |
| **nanobanana-gemini-image-generator** | Same Google Gemini 3 Pro Image, different wrapper (Python `nanobanana.py` script, GEMINI_API_KEY in `~/.nanobanana.env`). | Duplicate of above; pick whichever is easier to wire. |
| **nanobanana-visual-content-generator** | Korean-language wrapper for Instagram card-news + YouTube thumbnails. | SKIP — language not aligned with Sierra. |
| **ai-social-media-content-generator** | inference.sh CLI for FLUX/Veo/Seedance/Wan/Kokoro TTS. | We're already on Replicate for these models. Could swap to inference.sh later if pricing wins. Lower priority. |
| **ai-video-production-pipeline** (`video-editing`) | AI-assisted video editing — FFmpeg / Remotion / ElevenLabs / fal.ai / Descript / CapCut. | Mostly reference for assembly best practices. We already have `tools/assembly/pipeline.py` doing this. |
| **videodb-for-claude-code** | VideoDB for video understanding + indexing + real-time alerts on streams. Capture desktop sessions. | Future: when Sierra has 50+ posted reels, use VideoDB to index them all and enable retrieval-by-content. Not yet justified. |

## Tier 4 — automation / posting

| Skill | What it does | Where it plugs in |
|---|---|---|
| **tiktok-automation** | TikTok upload/publish/comment management via Rube MCP (Composio). | **HIGH-VALUE** when Sierra is ready to auto-post. Wire after the first 10 manually-posted reels prove the format. |
| **reddit-automation-toolkit** | Reddit posting + comment management via Rube MCP. | Future: Sierra newsletter promo on conservative-women subreddits (r/RedPillWomen, r/Conservatives, r/femalefashionadvice). Skill marked `risk: critical` so disclose AI-persona before posting. |

## Wiring Status (this commit)

✅ **Slop-detector**: integrated as auto pre-flight in `from_trend.py`. Standalone CLI at `tools/voice/slop_scan.py`. All 4 current plans pass clean (0.00).

✅ **Anti-slop rules from viral-reel-generator**: codified into `voice-profile.md §11.5` with the "rhetorical lists OK in character-driven comedy" exception explicitly documented.

🟡 **Nano-banana-pro**: skill-installed but not wired. TODO: `tools/generation/nano_banana.py` mirroring `tools/lora/generate.py` interface, with `--backend nano-banana` exposed in `from_trend.py`.

🟡 **TikTok-automation**: skill-installed, not yet activated. Activate when Sierra is publishing daily.

🟡 **Apify audience analysis**: skill-installed, not yet wired. Plug into `tools/analytics/post_perf.py` when Sierra has follower data to analyze.

✅ **All 20 skills available via `Skill` tool** in this and future Claude Code sessions.

## How to invoke a skill mid-session

```
Skill(slop-detector) "Audit personas/sierra-frost/.../plan.json"
Skill(viral-reel-generator) "Write 3 hook variants for this trend"
Skill(tiktok-manager) "Optimize this caption for FYP"
Skill(nano-banana-pro) "Generate a 4K hero shot of Sierra at the beach"
```

The Skill tool reads `~/.claude/skills/<name>/SKILL.md` and applies it
in-context. For repeated workflows, prefer building dedicated tools in
`tools/` that bake the skill's logic in (like we did with `slop_scan.py`).
