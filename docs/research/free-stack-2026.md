# Sierra's Free / Open-Source Stack — May 2026

> Research synthesis (research-agent 2026-05-07). Operator preference:
> **add only free / open-source tools going forward, no new paid SaaS.**
> This doc maps every free alternative to the paid services Sierra
> currently uses + the gaps we never had coverage for.

---

## TL;DR — adopt these 5

If we adopt only 5 free/OSS additions, these are the highest-leverage:

1. **Postiz** (AGPL-3, ~30k stars) — fills the *entire* posting/scheduling
   gap we have zero coverage on today. 17+ platforms incl. TikTok, IG,
   YouTube, Threads, X, Bluesky. Self-host on a $5 VPS. Replaces
   Buffer/Hypefury entirely.
2. **MUSE ENGINE + DATASET-maker ComfyUI workflows** (Civitai) — once
   we own a Sierra LoRA generated locally, we drop Replicate Flux+LoRA
   spend.
3. **Pollinations.ai** (MIT) — free Flux endpoint, server keys give
   unlimited rate. Drop-in replacement for Replicate Flux on B-roll /
   non-LoRA images.
4. **F5-TTS** (MIT, ~3GB VRAM) — redundant voice fallback so Chatterbox
   isn't a single point of failure. Together they finish the case for
   killing ElevenLabs.
5. **LatentSync + MuseTalk** — primary lipsync (LatentSync 7.90 LSE-C
   on HDTF, best in 2026) + fast-iteration alt (MuseTalk 30 FPS @ 256²).
   Replaces Higgsfield video entirely.

**Net effect**: kill recurring spend on Replicate Flux+LoRA, ElevenLabs,
and Higgsfield. Gain a posting layer we never had.

---

## 1. End-to-end pipelines (orchestration reference)

| Repo | Stars | Last commit | License | What it does | Sierra-fit |
|---|---|---|---|---|---|
| [SamurAIGPT/AI-Influencer-Generator](https://github.com/SamurAIGPT/AI-Influencer-Generator) | ~200, 56 forks | Feb 6 2026 | MIT | SD image → gTTS voice → SadTalker lip-sync, all free | Closest 1:1 reference architecture; lift orchestration glue |
| [renefatuaki/influencer-ai](https://github.com/renefatuaki/influencer-ai) | small but active | 2026 | MIT | Spring Boot + Next.js Twitter bot using Ollama + SD | Best reference for **posting-loop** automation Sierra lacks |
| [SamurAIGPT/AI-Youtube-Shorts-Generator](https://github.com/samuraigpt/ai-youtube-shorts-generator) | active 2026 | 2026 | MIT | Long-form → 9:16 viral shorts via Whisper + LLM + auto-crop | Free Opus Clip replacement |
| [hacksider/Deep-Live-Cam](https://github.com/hacksider/Deep-Live-Cam) | ~73.6k | active | GPL-3 | Real-time face swap | **AVOID** — deepfake reputational risk + GPL |

Takeaway: SamurAIGPT/AI-Influencer-Generator is the only end-to-end MIT
scaffold with structurally identical shape to Sierra; copy its
orchestration, replace its components with our better ones below.

---

## 2. ComfyUI character-locked workflows (the actual JSONs)

| Workflow | Source | Use |
|---|---|---|
| **THE MUSE ENGINE** | [Civitai #19782](https://civitai.com/articles/19782/the-muse-engine-ai-influencer-workflow) | Full Flux+PuLID+upscale pipeline. **Most complete shared JSON.** |
| **AI Influencer DATASET maker (Flux.2 Klein)** | [Civitai #2182806](https://civitai.com/models/2182806/ai-influencer-dataset-maker-for-consistent-character) | Generates organized image sets for LoRA training |
| **InfiniteYou ZenAI + GGUF + LoRA** | [Civitai #1424364](https://civitai.com/models/1424364/infiniteyou-comfyui-node-of-zenai-workflow-gguf-lora-tested-on-16gb-vram-rtx4080-super) | 16GB VRAM-tested, ~2 min @ 1024². Confirms InfiniteYou on consumer GPU. |
| **CozyMantis SAL-VTON clothes-swap** | [github](https://github.com/cozymantis/clothes-swap-salvton-comfyui-workflow) | Dress same character in any clothes. Solves wardrobe variety. |
| **Datou "Fake Influencer" (InstantID)** | [openart](https://openart.ai/workflows/datou/fake-influencer/mVpxdSNipudZ8R5gvNIy) | Random face + pose + InstantID. Cheap fallback. |
| **MimicPC consistent-character** | [mimicpc](https://www.mimicpc.com/workflows/character-consistency-36652528042065921) | Free workflow page exposing the JSON |

Takeaway: pull MUSE ENGINE + DATASET-maker now; together they replace
the paid Replicate Flux+LoRA path once we own a Sierra LoRA.

---

## 3. Free image-gen alternatives

| Service | Cost | Rate | License | Quality |
|---|---|---|---|---|
| **Pollinations.ai** | **Free, no key for basic** | Server keys (`sk_`) = unlimited; client keys = 1/hr/IP | MIT ([github](https://github.com/pollinations/pollinations)) | Same Flux backbone as Replicate, near-identical |
| HuggingFace Inference free | Free credits | FLUX.1-dev users hit monthly cap in ~4 days at scale | varies | Same weights; prototyping only |
| fal.ai | Free credits then $0.003/img Schnell | Strict after credits | paid | Excellent — but not perpetually free |
| Together.ai | No real free Flux tier in 2026 | n/a | n/a | Skip |
| Local ComfyUI | $0 | Hardware-bound | open | Highest control. Already in plan. |

**Recommendation**: Pollinations.ai (server key) is the clear free-tier
winner for cloud bursts when local GPU is busy. Wired below.

---

## 4. Free voice-clone alternatives (drop ElevenLabs)

| Model | Repo | License | Quality | Notes |
|---|---|---|---|---|
| **Chatterbox / Chatterbox Turbo** | [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox) | MIT | 95/100; beats ElevenLabs in 63.75% blind tests | Already wired (`tools/voice_synth/chatterbox.py`). Verify Turbo variant. |
| **CosyVoice 2.0** | [FunAudioLLM/CosyVoice](https://github.com/FunAudioLLM/CosyVoice) | Apache-2 | Highest speaker-similarity 2026 | Best zero-shot clone; heavy GPU |
| **F5-TTS** | [SWivid/F5-TTS](https://github.com/SWivid/F5-TTS) | MIT | Top all-rounder, ~3GB VRAM | **Lowest hardware bar; great fallback** |
| **XTTS v2** | [coqui-ai/TTS](https://github.com/coqui-ai/TTS) | MPL-2 (v2 weights have separate Coqui CPL — **check before commercial**) | 75/100 | Lowest latency (~3.4s) |
| **Kokoro-82M** | [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | Apache-2 | #1 TTS Arena Jan 2026 despite 82M params | Cheap utility voice (intros, captions); NOT a Brielle clone |

**Recommendation**: keep Chatterbox primary, add F5-TTS as redundant
fallback (low VRAM, MIT), use Kokoro for short utility lines.

---

## 5. Free video / lipsync (drop Higgsfield video)

| Tool | License | Quality | Hardware | Notes |
|---|---|---|---|---|
| **LatentSync 1.6** | [bytedance/LatentSync](https://github.com/bytedance/LatentSync) Apache-2 | **Best LSE-C 7.90 on HDTF** (top 2026) | ~10-12 GB VRAM | Already in plan. Primary. |
| **MuseTalk** | [TMElyralab/MuseTalk](https://github.com/TMElyralab/MuseTalk) MIT | 30+ FPS @ 256², comparable lipsync, better visual fidelity | ~8 GB | Best real-time / streaming. |
| **LivePortrait** | [KwaiVGI/LivePortrait](https://github.com/KwaiVGI/LivePortrait) — **CC-BY-NC for some weights, check** | Best identity retention | ~8 GB | Use for expression retargeting, not commercial speech. |
| **SadTalker** | [OpenTalker/SadTalker](https://github.com/OpenTalker/SadTalker) Apache-2 | Older; head motion from audio | low | Cheap fallback / B-roll talking-head. |
| **Hallo3** | [fudan-generative-vision/hallo3](https://github.com/fudan-generative-vision/hallo3) MIT | Diffusion-transformer; dynamic | high VRAM | Keep on radar. |

**Recommendation**: LatentSync as core, MuseTalk as fast-iteration alt.

---

## 6. Free scheduling / posting (currently zero coverage)

| Tool | Stars | License | Platforms | Verdict |
|---|---|---|---|---|
| **Postiz** | [gitroomhq/postiz-app](https://github.com/gitroomhq/postiz-app) ~30k | AGPL-3 | 17+ incl. TikTok, IG, YouTube, Threads, X, Bluesky | **Clear winner**. Self-host. |
| **Mixpost** | [mixpost.app](https://mixpost.app/) ~3.1k | self-hosted (paid + free editions) | TikTok, IG Reels, YT Shorts, FB Reels | OK fallback |
| BrightBean Studio | small | OSS | TikTok/IG/YT + 7 more | Newer; multi-workspace (good if Sierra spawns siblings) |
| TryPost | small | AGPL-3 | modern creator focus | OK alternative |

**Recommendation**: Postiz. AGPL-3 is fine for self-hosted.

---

## What this replaces

| Currently paying | Free replacement | Savings |
|---|---|---|
| Replicate Flux + LoRA | Local ComfyUI + MUSE ENGINE workflow + Pollinations (cloud burst) | $5-15/mo when scaled |
| ElevenLabs Brielle | Chatterbox (already wired) + F5-TTS fallback | $22/mo |
| Higgsfield Soul + video | LatentSync + MuseTalk + Boreal LoRA | $30/mo |
| (Zero posting coverage) | Postiz | -$0 (was free, just adds capability) |

Total recurring savings if fully migrated: **~$70/mo**. Plus Sierra
gains a posting/scheduling layer she didn't have.

---

## What's NOT in this plan

- **Apify** — already paid; user explicitly intentionally keeping
- **Firecrawl** — already paid; same
- **Anthropic API** — still cheapest LLM for the planner work; no
  free replacement that won't cost MORE in time

These are kept as-is.

---

## Sources

See research-agent transcript at `~/.claude/skills/_session/research-2026-05-07-free-stack/`.
Highlights: SamurAIGPT pipelines on GitHub, Civitai #19782 / #2182806 /
#1424364, Pollinations.ai, BentoML/Inferless TTS surveys 2026,
github.com/lipsync.com / pixazo.ai lipsync surveys, gitroomhq/postiz-app.
