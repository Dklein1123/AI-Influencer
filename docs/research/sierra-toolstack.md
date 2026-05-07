# Sierra Frost Toolstack — May 2026

> Opinionated reference of every tool, plugin, MCP, GitHub repo, and SaaS
> worth using to run Sierra at the level of a professional influencer team.
> Each entry: **what**, **why for Sierra specifically**, **cost**, **how to
> wire it in**. Skip generic listicles — this is a working playbook.

---

## TL;DR — the 12-tool stack

| # | Tool | Lane | Cost | Status |
|---|------|------|------|--------|
| 1 | **Higgsfield Soul 2** | Image gen w/ Soul ID | $30/mo subscription, already on | ✅ wired |
| 2 | **Replicate (Flux LoRA)** | Identity-locked image gen, retraining | pay-per-second, ~$5–10/mo | ✅ wired |
| 3 | **fal.ai** | Faster/cheaper Flux + new models (Hedra, AuraFlow) | pay-per-second | ⏳ recommend |
| 4 | **ElevenLabs** | Voice clone + synthesis | $22/mo Creator | ✅ wired |
| 5 | **Hedra Character-3** | Talking-head video, more lifelike than Wan | pay-per-credit | ⏳ recommend |
| 6 | **Suno v4 / Udio** | Original tracks for transitions/outros | $10–24/mo | ⏳ recommend |
| 7 | **Apify** | TikTok / IG / YouTube scraping | $49/mo Creator | ✅ wired |
| 8 | **Firecrawl** | News + brand research, markdown extraction | $19/mo Hobby | ✅ wired |
| 9 | **Anthropic Claude API** | Trend scoring, pitch drafting, voice grading | pay-per-token | ✅ wired |
| 10 | **Metricool** *or* **Buffer** | Cross-platform scheduling + DMs + analytics | $18–24/mo | ⏳ recommend |
| 11 | **Notion** *(or Lovable portal — already built)* | Brand bible + ops board | free / $8 | ✅ Lovable equiv. |
| 12 | **Cloudinary** | Image/video CDN + on-the-fly transforms | free tier ample | ⏳ recommend |

**Total monthly burn (recommended additions):** ~$90 incremental on top of
existing ~$60 = **~$150/mo all-in** for a full 1-influencer pro stack.

---

## 1. Generation tools

### Already in the stack

- **Higgsfield Soul 2** — current primary. Soul ID
  `87b6278b-8407-479d-b127-a8f2bc064ed1` covers Pillars 1/2/4 with strong
  identity carryover. Wired in `tools/generation/higgsfield.py`.
- **Replicate (`ostris/flux-dev-lora-trainer`)** — Sierra LoRA v1
  (`dklein1123/sierra-frost-v1:3225c5c8…`) lives here. v2 retrain queued
  (5 off-axis refs needed). Wired in `tools/lora/`.
- **ElevenLabs** — voice ID `6u6JbqKdaQy89ENzLSju`. Wired in
  `tools/voice_synth/client.py`.
- **Wan 2.7** — current talking-head lipsync. Works but lifeless on
  long takes (>8s).

### Worth adding

- **fal.ai** ([`fal.ai`](https://fal.ai)) — Flux Dev / Flux Pro / Pro 1.1
  Ultra at lower latency + price than Replicate. Same LoRA file format, so
  swap path `fal-ai/flux-lora` keeps Sierra v1 working. Best for batch
  generation (50+ images for content calendars).
  - **API:** Bearer token, ~3s avg per image at 1024² Flux Dev.
  - **Action:** add `tools/generation/fal_client.py` that mirrors
    `higgsfield.py`'s interface.
- **Hedra Character-3** ([`hedra.com`](https://www.hedra.com)) — talking
  head with significantly better mouth shapes + micro-expressions than
  Wan 2.7. Direct competition with Synthesia/HeyGen but doesn't lock you
  into a stock avatar.
  - **API:** REST, $30/mo for ~300 credits. ~1 credit per 10s of video.
  - **Action:** prototype P3 + P7 hooks side-by-side with Wan, pick
    winner, lock in.
- **Suno v4** ([`suno.com/api`](https://suno.com)) — original
  music/jingles. Sierra's brand voice ≠ trending-sound roulette;
  custom-scored snippets for stings, outros, newsletter audio.
  - $10/mo Pro, 500 generations.
- **Udio v1.5** — alternative to Suno; better for sung captions.
- **Krea AI** ([`krea.ai`](https://www.krea.ai)) — real-time generation
  with sliders; useful for moodboarding before committing to a
  Higgsfield/LoRA gen. $35/mo all-you-can-eat.
- **Runway Gen-4** — premium video; consider only when Hedra isn't enough.
  $35/mo Plus.

### Free / open-source local fallbacks (for when API budgets bite)

- **ComfyUI + Flux + LoRA** ([github.com/comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI))
  — local Flux with Sierra LoRA on a 24GB GPU. Free.
- **AUTOMATIC1111** — older but still useful for SDXL ControlNet poses.
- **Wan 2.7 weights** ([Wan-AI/Wan2.1-T2V](https://huggingface.co/Wan-AI))
  — release the Wan model locally if rate-limited.
- **AnimateDiff** — local lip-sync alternative.

---

## 2. Scraping & research (Apify + Firecrawl)

This is the layer most amateur creator-stacks lack. We have it now.

### Apify — actor recommendations

Saved separately in [`apify-actors.md`](./apify-actors.md). Highlights:

- **`clockworks/free-tiktok-scraper`** — by hashtag, profile, or
  trending. Free tier covers daily trend pulse for Sierra's lane.
- **`apify/instagram-scraper`** — paid, $0.20 per 1k results. Use for
  competitor weekly snapshots, NOT daily.
- **`apify/youtube-scraper`** — useful for long-form competitor tracking
  (Allie Beth Stuckey, Jubilee debates, etc.)
- **`apidojo/twitter-scraper-lite`** — replaces dead Twitter API for
  quote-tweet research.
- **`drobnikj/google-search-scraper`** — free, generic, faster than
  Firecrawl for plain SERP scraping.
- **`misceres/google-trends-scraper`** — verify a hashtag has search
  volume before doing a Sierra take on it.

Run them via `tools/research/common.py:apify_run_sync`. Already wired.

### Firecrawl — when to use vs. Apify

- **Firecrawl** = "give me clean markdown of any web page, fast." Use
  for news sites, blog posts, brand About pages, anything that
  isn't a hard-anti-bot target.
- **Apify** = "give me structured data behind login walls or aggressive
  anti-bot." Use for TikTok, Instagram, LinkedIn, Twitter.

Don't pay both for the same job. Firecrawl is $19/mo for 3000 scrapes
which covers 100/day; that's plenty.

### Custom scrapers (already shipped here)

- `tools/research/trend_pulse.py` — daily Sierra trend digest
- `tools/research/competitor_tracker.py` — competitor weekly snapshots
- `tools/research/pitch_research.py` — brand outreach research

---

## 3. MCP servers worth installing

MCPs the operator should add to Claude Code (or a Claude Desktop config).
Each is a force-multiplier for Sierra's workflow.

See [`mcp-recommendations.md`](./mcp-recommendations.md) for install
commands. Top picks:

- **GitHub MCP** — already installed; commits/PRs to AI-Influencer.
- **Filesystem MCP** — read/write the entire `personas/` tree from a
  Claude conversation without copy-paste.
- **Apify MCP** ([github.com/apify/actors-mcp-server](https://github.com/apify/actors-mcp-server))
  — lets Claude pick actors and run them inline. Replaces ~30% of the
  Python wrapper code we've written.
- **Firecrawl MCP** ([github.com/mendableai/firecrawl-mcp-server](https://github.com/mendableai/firecrawl-mcp-server))
  — same idea for Firecrawl. Pair with the Apify one.
- **Brave Search MCP** — free SERP for casual research, conserves
  Firecrawl quota.
- **Anthropic Computer Use MCP** — browser-controllable agent for
  scheduling/posting flows that have no API (Threads, BlueSky, some IG
  flows).
- **Notion MCP** *(if not using the Lovable portal)* — sync brand bible.
- **Slack MCP** — alerts when a competitor posts a viral hit, when a
  Sierra item passes review, when LoRA training finishes.
- **Linear MCP** *(or use Lovable Tasks)* — backlog management.
- **Higgsfield MCP** — already wired. Generate images from chat.

---

## 4. Scheduling, posting, comment management

This is the biggest gap in the current stack. We generate; we don't
distribute.

### Scheduler picks

- **Metricool** ($18/mo Starter) — best for Sierra. TikTok + Reels +
  Stories + Pinterest + Newsletter teasers in one queue. Native AI
  caption assistant (ignore it; we have our own voice). Best-in-class
  reporting per-post.
- **Buffer** ($6/channel/mo) — cheaper, simpler, weaker analytics. Good
  if Sierra stays on 2 platforms.
- **Later** — strong for IG-specific. Skip if cross-platform.
- **Publer** ($12/mo) — best AI features but UI is busy.

**Recommendation:** **Metricool**. The $18/mo single-brand plan is
fine, and the analytics are needed to feed back into the trend pulse.

### Comment management

- **Manychat** ($15/mo Pro) — DM autoresponders for Instagram + TikTok.
  Worth setting up the moment Sierra crosses 1k followers, before then
  it's overkill.
- **SocialBee** ($29/mo) — combined scheduler + comment moderation;
  consider if Metricool's DM workflow feels weak.
- **Instagram + TikTok native auto-replies** — free, weak, but enough
  for now.

### Posting via API (advanced)

- **Meta Graph API** (Instagram) — official, requires business account
  + app review. ~2 weeks setup, then full automation. Worth it for
  programmatic Reels uploads from `tools/assembly/pipeline.py`.
- **TikTok Content Posting API** — open as of 2025; Sierra qualifies
  once she has a business account. Same value: render → upload via
  `ffmpeg → curl`.
- **YouTube Data API v3** — free, official; for any long-form Shorts.
- **Threads API** — official since 2024. Cheap to wire.
- **BlueSky / Mastodon / X (paid tier)** — APIs exist; lower priority.

When wired, the dream is: ffmpeg renders a reel → uploads to Cloudinary
→ posts to all 4 platforms via APIs → schedules a follow-up DM autoresponder
→ writes the analytics summary back to the portal. Estimate: **2 days
to build all of this** once Sierra has business accounts. Save for v2.

---

## 5. Analytics + feedback loop

The point: every post should make the NEXT generation cycle smarter.

- **Metricool** — covers most platforms (above).
- **Tella** ([tella.tv](https://www.tella.tv)) — for studio recordings
  if Sierra ever does long-form.
- **Beehiiv** ($39/mo Scale) — best newsletter platform for analytics,
  ahead of Substack on growth tools.
- **Substack** — free, weaker analytics, stronger discovery for a
  conservative-leaning lane.
- **Posthog** (free OSS) — for a Sierra landing page if she gets one.

### Custom analytics worth building

`tools/research/post_perf.py` (not built yet — TODO):
- Pull last 30 days of Sierra's posts via Metricool API
- Bucket by template (P1, P3, P7, …) + by hook style + by music type
- Output `personas/sierra-frost/analytics/2026-MM.md` with rankings
- Auto-update `viral-playbook.md` with the top 5 patterns

This closes the loop. **High-priority next build.**

---

## 6. Operations + infra

### Already built

- **Lovable Cloud Backend** — Supabase wrapper, RLS, Edge Functions,
  Storage. Portal is the team UI for Sierra.
- **Edge Function `sync`** — bridges this repo's Python tools to the
  portal. Auth via `SYNC_API_KEY`.
- **GitHub Contents API + PAT** — cross-repo writes from AI-Influencer
  to content-command for Lovable-deployable changes.

### Worth adding

- **Cloudinary** — free tier = 25 credits/mo (~25k transformations).
  Sierra renders go here, get auto-thumbnails + WebP/AVIF for the
  newsletter, and hot-link from the portal. Beats raw Supabase Storage
  because of the on-the-fly transforms.
- **Doppler** ([doppler.com](https://www.doppler.com)) — secrets
  manager for the env file. Rotates `~/.AI-Influencer.env` keys via
  CLI; syncs to GitHub Actions and the Lovable runtime in one command.
  Free tier covers a 1-person team. **Recommend.**
- **GitHub Actions** — CI for the Python tools (lint + voice-lint runs
  on every PR). 2000 min/mo free.
- **Tailscale** (free, 3 nodes) — so Sierra's GPU box at home (if there
  is one) is reachable from CI for local LoRA training.

---

## 7. GitHub repos worth cloning

Battle-tested OSS that solves real Sierra-stack problems:

- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** — local Flux
  + LoRA + ControlNet pipelines. Mandatory if doing local generation.
- **[ostris/ai-toolkit](https://github.com/ostris/ai-toolkit)** — same
  trainer behind Replicate's `flux-dev-lora-trainer`. Train Sierra v2
  locally for $0 if there's a GPU available. Saves ~$5/retrain.
- **[fofr/cog-comfyui](https://github.com/fofr/cog-comfyui)** — wraps
  ComfyUI workflows as Replicate models. Good for one-click sharing.
- **[Mintplex-Labs/anything-llm](https://github.com/Mintplex-Labs/anything-llm)**
  — local RAG over the brand bible + voice profile + viral playbook so
  every prompt has full Sierra context.
- **[run-llama/llama_index](https://github.com/run-llama/llama_index)**
  — alternative RAG; pair with Claude API for graded brand-voice checks.
- **[mendableai/firecrawl](https://github.com/mendableai/firecrawl)** —
  self-host if Firecrawl's hosted prices ever bite.
- **[apify/crawlee](https://github.com/apify/crawlee)** — TypeScript/
  Python web crawling lib. Foundation for custom scrapers when an
  Apify actor doesn't exist.
- **[Synthesia / HeyGen alternatives: SadTalker / EchoMimic](https://github.com/antgroup/echomimic)**
  — open-source talking-head; experimental but free.
- **[FFmpeg](https://github.com/FFmpeg/FFmpeg)** — already used in
  `tools/assembly/pipeline.py`. Underused — compile with `--enable-libfreetype
  --enable-libass` for our subtitle stack, which we already do.
- **[Lavinia-Codes / chatterbox-tts](https://github.com/resemble-ai/chatterbox)**
  — OSS voice clone if ElevenLabs becomes a problem. Lower quality but
  free.
- **[BerriAI/litellm](https://github.com/BerriAI/litellm)** — unified
  client for OpenAI/Anthropic/Gemini/local models. Lets `claude_score`
  swap providers when one rate-limits.

---

## 8. Browser extensions + manual tools

Things the OPERATOR (you) installs once and gains 30% throughput:

- **Loom** — for recording how-to walkthroughs of new tools (saved to
  `docs/runbooks/`).
- **Bardeen** — browser automation; chains "scrape this profile → draft
  Sierra angle in Notion → DM" without code. Free tier.
- **Save to Notion / Save to Lovable** — clip articles into the portal
  inbox.
- **Tweet Hunter / Hypefury** — only if Sierra goes hard on X.
- **CapCut Web** — fallback video editor. Free, surprisingly capable.
  Use when ffmpeg is overkill (manual cuts).
- **Descript** — transcript + AI-edited video. Worth $24/mo if you do
  any long-form podcast-style content.
- **TweetDeck (X Pro)** — multi-column listening. Skip unless X-heavy.

---

## 9. Specific Sierra use-cases (workflows that compose tools)

Each is a real one-command flow we should automate.

### A. "Daily trend pulse" (built ✅)
```
python -m tools.research.trend_pulse
```
Output → portal AI Outputs Vault + `personas/sierra-frost/trends/`

### B. "Competitor weekly check-in" (built ✅)
```
python -m tools.research.competitor_tracker
```

### C. "Brand pitch in 60s" (built ✅)
```
python -m tools.research.pitch_research "Vuori"
```

### D. "Generate today's content from this trend" (TODO)
- Read top-scored trend from today's pulse
- Pick best Sierra template (P-X) for the format
- Generate image (Higgsfield) + caption (Claude w/ brand bible RAG) +
  voiceover (ElevenLabs) + subtitles (auto)
- Render reel via `tools/assembly/pipeline.py`
- Upload to Cloudinary + portal
- Queue in Metricool for tomorrow 11am ET

### E. "Lipsync version of this caption" (built ✅, Wan 2.7)
Replace with Hedra once subscribed.

### F. "Newsletter from last 7 days of trends" (TODO)
- Read 7 days of `trends/*.md`
- Claude drafts a 600-word Beehiiv issue in Sierra's voice
- Lint with `tools/voice/lint.py`
- Push as draft to Beehiiv API

### G. "Reply to my top comment in Sierra's voice" (TODO)
- Pull top comment via Metricool API
- Claude drafts reply in Sierra's voice
- Lint + push reply

---

## 10. What I'd skip (and why)

Saving time on tools that look promising but burn budget for marginal gain:

- **Synthesia / HeyGen** — Sierra has identity locked already; their
  stock-avatar model is worse than Hedra + our LoRA.
- **Jasper / Copy.ai** — Claude is strictly better and we already have
  a brand-bible RAG in mind.
- **ChatGPT-Plus operator account** — Claude is the agent of record;
  don't fragment.
- **Pictory / InVideo** — generic creator-tier video tools; ffmpeg +
  Hedra covers everything they do, with better quality.
- **Submagic / Captions** — auto-captioning. Our `pipeline.py` already
  does libass subs; no value-add.
- **Repurpose.io** — solves a problem we don't have (we render
  9:16 native; no need to repurpose 16:9 down).
- **AI influencer "platforms" (Glambase, Captions AI Twin, etc.)** —
  black boxes. We have full control with our own pipeline.

---

## 11. Cost ladder

Three sane stages of investment:

### Lean ($60/mo) — what we have today
- Higgsfield $30 + ElevenLabs $22 + ad-hoc Replicate ~$8

### Pro ($150/mo) — recommended next
- + Apify $49 (already added, sub'd to Creator)
- + Firecrawl $19 (already added, Hobby)
- + Metricool $18
- + Hedra $30
- + Suno $10
- + Anthropic API ~$15 in token usage at current research scripts

### Studio ($350/mo) — when Sierra hits 100k followers
- + Beehiiv $39 (newsletter)
- + Manychat $15 (DM autoresponders)
- + Cloudinary Plus $99
- + Krea $35 (moodboarding all the things)
- + Linear $8 / Notion $8 (project mgmt)
- + Doppler Team $7 (secrets)
- + Domain + landing page hosting $10

---

## 12. Where to start tomorrow

1. **Run `python -m tools.research.trend_pulse`** and review the first
   day's output. Calibrate the hashtag list.
2. **Init the competitor roster** with `python -m tools.research.competitor_tracker --init`,
   fill in 5–8 handles, run weekly.
3. **Subscribe to Metricool**, connect TikTok + IG + Beehiiv, schedule
   the next 7 days of content from `personas/sierra-frost/content-units/`.
4. **Add the Apify + Firecrawl MCPs** to the Claude Code config so the
   research scripts are also available as in-chat tools. (Instructions
   in `mcp-recommendations.md`.)
5. **Decide on Hedra** — generate one P3 with Wan and one with Hedra.
   Compare. If Hedra wins (it will), swap.
6. **Pick the final voice** from the talking-head A/B (still pending).
7. **Build `tools/assembly/from_trend.py`** that turns a top-scored
   trend pulse item into a fully rendered reel using existing
   pipeline pieces. This is the highest-leverage 1-day build left.

---

_Last updated 2026-05-07. Maintained as a living doc — add new tools
inline as they're vetted. Keep the "what I'd skip" section honest._
