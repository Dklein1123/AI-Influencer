# AI-Influencer Operator Playbook — May 2026

> Field intel from operators who actually shipped successful AI
> influencers in Sierra's lane. Synthesized from the May 2026 deep-
> research agent (Reddit / HN / X / YouTube / press disclosures).

The single highest-leverage finding: the documented "Sam → Emily Hart"
playbook gives Sierra a **direct lane analogue** with explicit tool
disclosure, and all of it is free except for one paid step we already
have a free alternative for.

---

## The Sam / Emily Hart playbook (the direct analogue)

**Operator:** "Sam," anonymous 22-year-old Indian medical student.
**Persona:** "Emily Hart" — a MAGA-coded female AI influencer.
**Result:** 3M–10M views per reel, "thousands per month" before
Instagram banned the account in Feb 2026.

**Disclosed stack** (from Wired transcript reproduced across moneywise,
theprint.in, multiple coverages):

| Step | Sam's tool | Cost | Sierra equivalent |
|---|---|---|---|
| Strategy / niche selection | Google Gemini free chat | $0 | Same — `gemini-2.5-flash` for hooks |
| Image generation | Gemini Nano Banana Pro | small free tier | Replicate Flux + Sierra LoRA + Boreal (better identity-lock) |
| Adult-content branch | xAI Grok | small free tier | NOT pursuing (Sierra is SFW) |
| Video / motion | Wan 2.2 Animate | $0 local | Same when local install |
| Posting | Manual on IG / TikTok | $0 | Postiz when self-hosted |

**Why this matters**: Sam never solved face-consistency (Gemini doesn't
hold identity across calls). Sierra HAS solved this with the trained
LoRA. Sierra running this same operator pattern with locked identity is
the upgrade.

**Lessons**:
1. Gemini's free chat tier is the operator's strategy brain — it picked
   the conservative niche for Sam. Tested 2026-05-07: works on this
   project for `gemini-2.5-flash` text. Use it the same way.
2. The conservative-women audience is **less AI-detection-savvy** than
   r/StableDiffusion would suggest. The bigger risk is platform bans,
   not realism (Sam got banned for content type, not for being AI).
3. Volume + free stack > polish + paid stack. Sam shipped daily.

---

## levelsio's pipeline disclosure

**Operator:** Pieter Levels (@levelsio), public builder.
**Threads:** [Apr 25 2025](https://x.com/levelsio/status/1915848425746088113), [Feb 11 2025](https://x.com/levelsio/status/1889062244626944423).

Stack:
1. Synthetic seed face (Photo AI — his SaaS)
2. **Nano Banana Pro** for edits (paid; replaceable with HF FLUX.1-Fill-dev free space + Pollinations)
3. **Wan 2.2 Animate** for video
4. **ElevenLabs** voice library

90% replicable on free tools per agent's analysis.

---

## The Clueless / Aitana López disclosure

**Operator:** Rubén Cruz (Spanish creative agency).
**Result:** ~$11,000 USD / month at peak. Profile: [netinfluencer](https://www.netinfluencer.com/the-clueless/).

**Stack:** GAN-style image gen (now Flux era) + **heavy manual
Photoshop compositing** + weekly editorial planning meetings.

**Lesson** (echoed in the prior `realism-stack.md`):
> AI is the base layer; **human Photoshop is the realism layer.**

Cruz's team ships Aitana looking like a real magazine shoot because
the Photoshop pass is heavy. Sierra needs an analogous "manual finish"
step until ComfyUI face/eye-detailer chains close the gap.

---

## The documented free 5-step pipeline (operator-validated)

```
1. Gemini (free)         → daily hook + script + comedy bit
2. ComfyUI Flux + LoRA   → 1 hero still per beat (local; Pollinations cloud-burst)
3. ElevenLabs Brielle    → 15–30s voice (already wired)
4. ComfyUI InfiniteTalk  → still + audio → lipsync mp4 (LOCAL, free)
5. CapCut / ffmpeg       → captions, trend audio, post
```

**Total recurring cost beyond existing ElevenLabs**: $0/month.
**One-time LoRA training**: $0 with any GPU ≥8GB; ~$0.50 on Vast.ai.

This is the pattern operators with hundreds of thousands of followers
are running. Sierra is already at steps 2 and 3; needs steps 1 and 4
locally + step 5 polish.

---

## InfiniteTalk — the lipsync workflow operators converged on

**Repo:** [MeiGen-AI/InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk)
**License:** check repo (tracked as Apache-style at time of survey).
**Hardware:** ~10GB VRAM, or **Wan2GP** ([deepbeepmeep/Wan2GP](https://github.com/deepbeepmeep/Wan2GP)) for sub-12GB GPUs.

**Why this beats LatentSync for Sierra specifically**: InfiniteTalk
takes a *single still* + audio and produces lipsync output without the
identity-drift LatentSync sometimes shows on close-ups. Operators
posting on r/comfyui call this combo "InfiniteTalk + Wan 2.2 Animate"
the canonical free alternative to HeyGen / D-ID / Synthesia.

YouTube tutorial walking through full setup:
[YouTube Mi0sonWTlbI](https://www.youtube.com/watch?v=Mi0sonWTlbI) —
"Unlimited AI Influencer videos (Full ComfyUI InfiniteTalk Tutorial)"

---

## Reddit / community canonical answers (consensus stack)

`r/StableDiffusion` (~500K members) and `r/comfyui` consensus 2025–2026
stack for AI influencers:

```
Base:        Flux.1-dev (or Flux.2 Klein)
Identity:    Custom LoRA (20–50 reference images) + InstantID/PuLID for hero touch-ups
Runtime:     ComfyUI local (or Vast.ai $0.50 one-time for training)
Lipsync:     InfiniteTalk + Wan 2.2 Animate
Voice:       Chatterbox (free, MIT) or ElevenLabs (paid)
Edit:        CapCut desktop (free)
```

This is the same stack Sierra is converging toward.

---

## YouTube full-stack tutorials worth bookmarking

(View counts unverified; pulled from agent search.)

- [QHw5UXLo74M](https://www.youtube.com/watch?v=QHw5UXLo74M) — "ComfyUI AI Influencer Starter Guide (2026)" — full free install
- [Cwyh3mQHxWM](https://www.youtube.com/watch?v=Cwyh3mQHxWM) — "Consistent AI Instagram Influencer in ComfyUI (Free)"
- [KJna9HSeGOQ](https://www.youtube.com/watch?v=KJna9HSeGOQ) — "Realistic AI Influencer locally (10+ ComfyUI workflows)"
- [Mi0sonWTlbI](https://www.youtube.com/watch?v=Mi0sonWTlbI) — "InfiniteTalk Full ComfyUI Tutorial & Setup"
- [n_mAPAjc4Fs](https://www.youtube.com/watch?v=n_mAPAjc4Fs) — "Pro AI Influencer. ComfyUI 30+ Workflows"

Channels worth following: **Next Diffusion** (operator-focused),
**Olivio Sarikas** (ComfyUI tutorials), **Apatero** (open-source bias).

---

## Discord communities (identified, not entered)

- [Civitai Discord](https://discord.com/invite/civitai) — 114K+ members, the LoRA / model exchange
- ComfyUI Discord (linked from [comfy.org](https://www.comfy.org)) — official, workflow troubleshooting
- Stability AI community Discord (quieter post-Flux dominance)
- Pollinations.ai Discord (Berlin-based; the free-API operator community)
- Apatero + Next Diffusion small operator-specific Discords linked from their tutorial sites

---

## What this means for Sierra (concrete next moves)

1. **Wire Gemini-text-as-planner** → unlocks free Sierra-script drafting,
   replaces the disabled Sonnet path. (Done this commit.)
2. **Set up local ComfyUI + InfiniteTalk + Wan 2.2** when a 12+GB GPU is
   available → kills Higgsfield video spend permanently.
3. **Train Sierra LoRA v2 locally** via the ComfyUI DATASET-maker
   workflow → kills Replicate Flux+LoRA spend.
4. **Self-host Postiz** on a $5 VPS → fills the missing posting layer.
5. **Adopt the daily 5-step operator sequence** (Gemini → ComfyUI →
   ElevenLabs → InfiniteTalk → CapCut) for every Sierra reel.

---

## Sources

- [@levelsio Apr 25 2025 thread](https://x.com/levelsio/status/1915848425746088113) — pipeline disclosure
- [@levelsio Feb 11 2025 thread](https://x.com/levelsio/status/1889062244626944423) — synthetic face gen
- [@OlivioSarikas Flux ControlNet thread](https://x.com/OlivioSarikas/status/1840921279756403016)
- [HN 38421157 — Spanish AI agency $11K/mo](https://news.ycombinator.com/item?id=38421157)
- [HN 46606633 — Instagram AI defamation thread](https://news.ycombinator.com/item?id=46606633)
- [netinfluencer.com — The Clueless / Aitana](https://www.netinfluencer.com/the-clueless/)
- [Rubén Cruz LinkedIn](https://www.linkedin.com/in/ruben-cruz-9a4638111/)
- [moneywise.com — Emily Hart MAGA operator](https://moneywise.com/news/top-stories/ai-maga-instagram-influencer-emily-hart-thirst-trap)
- [theprint.in — Emily Hart workflow detail](https://theprint.in/feature/how-an-indian-med-student-made-maga-dream-girl-emily-hart-democrats-know-its-ai-slop/2911376/)
- [Euronews — Jessica Foster MAGA AI](https://www.euronews.com/culture/2026/03/17/meet-jessica-foster-the-viral-onlyfans-ai-fooling-millions-of-maga-fans)
- [InfiniteTalk GitHub](https://github.com/MeiGen-AI/InfiniteTalk)
- [Wan2GP GitHub — GPU-poor video](https://github.com/deepbeepmeep/Wan2GP)
- [Pollinations.ai](https://pollinations.ai)
- [aitooldiscovery.com — Stable Diffusion Reddit roundup](https://www.aitooldiscovery.com/guides/stable-diffusion-reddit)
