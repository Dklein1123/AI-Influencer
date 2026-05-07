# AI Influencer Community Brief — May 2026

> Map of the open-source / GitHub community building AI influencers in
> 2026. What to clone, what to study, what to skip. Synthesizes the
> field research from the May 2026 deep-dive plus the operator playbook
> intel from interviews / threads.

---

## How the field actually splits

There are five lanes building "AI influencer" tooling in 2026, and they
don't all want the same things:

| Lane | What they need | Best repos |
|---|---|---|
| **Identity-locked image gen** | Same face every time, any pose | InfiniteYou, PuLID-Flux, ostris/ai-toolkit |
| **Realism / anti-slop** | Output that doesn't read AI | Boreal-FD, Amateur Snapshot, propost, Detail Daemon |
| **Talking-head video** | Lipsync + expression on stills | LatentSync, MuseTalk, LivePortrait, Sonic |
| **Voice cloning** | One-shot clones, low cost | Chatterbox, XTTS v2.5, RVC for post-conversion |
| **Pipeline orchestration** | Chained gen → post → analyze | SamurAIGPT/AI-Influencer-Generator, custom |

Sierra's stack today: Replicate Flux + custom LoRA (image), ElevenLabs
Brielle (voice), Wan 2.7 (lipsync), ffmpeg (assembly), Lovable portal
(ops). All five lanes covered, but each at first-90% quality. The
upgrade path below moves us to the 95%+ tier.

---

## Tier 1 — install/study now

### Identity & face consistency

**[InfiniteYou (ByteDance)](https://github.com/bytedance/InfiniteYou)** — SOTA one-shot face
injection on Flux.1-dev. Uses InfuseNet residuals; beats PuLID on identity
+ text alignment. **CC-BY-NC license — academic only, NOT commercial.**
For Sierra: useful as a *reference* for what's possible, and for
research-only A/B tests. ~16GB VRAM with quantize_8bit + CPU offload.

**[PuLID-Flux Enhanced (sipie800)](https://github.com/sipie800/ComfyUI-PuLID-Flux-Enhanced)** —
Fork of balazik's PuLID-Flux adding `train_weight` fusion. Stack 5–10
Sierra references into one optimized embedding. Commercial-friendly.
~12GB VRAM. **Recommended for Sierra v2 as a fallback when LoRA misses.**

**[lldacing/ComfyUI_PuLID_Flux_ll](https://github.com/lldacing/ComfyUI_PuLID_Flux_ll)** —
Most actively-maintained PuLID-Flux fork. Use this rather than balazik's
original (stale).

**Skip:** PhotoMaker (worse identity than PuLID/InstantID on Flux),
InstantID (SDXL-era, weaker on Flux pipelines).

### Realism / anti-slop

(See [`realism-stack.md`](./realism-stack.md) for the full technical playbook.)

The community-blessed **Forge realism stack:**

```
sierra-frost-v1            0.9
amateur-snapshot-photo     0.6
boreal-fd                  0.5
guidance_scale             2.5
```

Plus a face/eye detailer pass (ImpactPack ADetailer eyes_v2) and
post-process (propost film grain 0.05 + halation 0.15 + Portra 400 LUT).

Key repos:
- [ComfyUI-Detail-Daemon (Jonseed)](https://github.com/Jonseed/ComfyUI-Detail-Daemon)
- [comfyui-propost (digitaljohn)](https://github.com/digitaljohn/comfyui-propost)
- [ComfyUI-Optical-Realism (skatardude10)](https://github.com/skatardude10/ComfyUI-Optical-Realism)
- [ComfyUI-Darkroom (jeremieLouvaert)](https://github.com/jeremieLouvaert/ComfyUI-Darkroom) — 161 physics-based film stocks

### Lipsync — replace Wan 2.7

**[LatentSync 1.6 (ByteDance)](https://github.com/bytedance/LatentSync)** —
Apache-2.0, 8–18GB VRAM, native 512×512, best LSE-C on HDTF (7.90).
Better lip-shape accuracy than Wan 2.7 on close-ups; preserves
identity better in latent space. **Drop-in replacement for Wan 2.7.**

**[MuseTalk 1.5 (TMElyralab)](https://github.com/TMElyralab/MuseTalk)** —
30fps real-time on V100. Best for live-streaming Sierra (eventually).

**[LivePortrait (Kuaishou)](https://github.com/KwaiVGI/LivePortrait)** —
Not lipsync per se — expression + head transfer from a driving video.
**Combine with LatentSync:** LivePortrait for head + eyes + expression,
LatentSync for mouth. Issue #400 documents the stack.

**[Sonic (smthemex ComfyUI nodes)](https://www.runcomfy.com/comfyui-workflows/sonic-advanced-lip-sync-portrait-animation-framework)** —
SVD-based, "global audio perception" — produces *expression* not just
lip shape. Use for emotional dating-commentary clips.

**Skip now:** Hallo3, EchoMimic, SadTalker — older, only worth it for
non-realistic/anime.

### Voice — Chatterbox is the move

**[Chatterbox (Resemble AI)](https://github.com/resemble-ai/chatterbox)** —
MIT license, beats ElevenLabs in **63.75% blind A/B (Podonos study)**,
<200ms latency, zero-shot from 10s reference. Multilingual variant
covers 23 languages. **Includes inaudible Perth watermark — disclosure
note.**

For Sierra: clone Brielle's voice into Chatterbox as a backup + cost
saver. ElevenLabs Creator at $22/mo is fine but 3x ElevenLabs's price.
Chatterbox is free at scale.

**[XTTS v2.5 (Coqui)](https://github.com/coqui-ai/TTS)** — Gold-standard
fallback. 6s reference, slower than Chatterbox.

**[RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)** —
Voice *conversion* not TTS. Useful as a post-pass: Chatterbox/ElevenLabs
output → RVC trained on Brielle for extra timbre lock.

### Pose / expression locking

**[Fannovel16/comfyui_controlnet_aux](https://github.com/Fannovel16/comfyui_controlnet_aux)** —
DWPose preprocessor (better than OpenPose on hands + face). Use
`DW_Openpose_full` → Flux-compatible ControlNet (Shakker Labs Union
Pro). **Lock Sierra's pose from a reference photo so each shot reads
as "shot in the same session."**

### Training

**[ostris/ai-toolkit](https://github.com/ostris/ai-toolkit)** — still
the standard for Flux LoRA training. Active Feb 2026 (FLUX2 Klein VRAM
fixes, MPS support). 24GB VRAM minimum for Flux.1-dev LoRA. Used to
train Sierra v1 already.

Recommendation for Sierra v2: include deliberately imperfect inputs in
the training set (motion blur, harsh flash, overexposure) — v1 likely
overfits to beauty-lit clean reference, which is why output reads AI.

---

## Tier 2 — operator playbooks (study, don't clone)

Real operators behind successful AI influencers. Lessons embedded.

### The Clueless / Aitana López (Rubén Cruz)

Stable Diffusion + Midjourney + ChatGPT + **heavy manual Photoshop
post.** They publicly downplay tooling, but it's confirmed GAN-era SD +
manual finish (Euronews, NetInfluencer profiles).

> **Lesson:** AI is the base layer; **human Photoshop is the realism
> layer.** The Clueless ships images that look like real magazine
> shoots because their Photoshop pass is heavy, not because their AI
> is uniquely good. Sierra needs an analogous "manual finish" step
> until tooling catches up.

### Lil Miquela / Brud

Completely different lane: **Unreal Engine + Maya/Blender + mocap**,
then AI for content scaling. Not Sierra's model — 3D pipeline cost is
prohibitive for solo ops. Skip unless you're funded.

### Milla Sofia

Stable Diffusion + ControlNet + Roop face-swap. **Single operator, low
budget**, proves SD+ControlNet+manual is viable solo. Closer to
Sierra's reality than Aitana.

### Emily Hart (MAGA AI influencer, India-based)

**Google Gemini Nano Banana Pro end-to-end. No ComfyUI.** Single 22-yr-
old operator. The most relevant case study for Sierra's lane.

> **Lesson:** for the conservative/political niche, the audience is
> *less AI-detection-savvy* than the r/StableDiffusion crowd — your
> bigger risk is **platform bans**, not realism. The candid-iPhone
> aesthetic actually builds *more* trust with this audience than
> editorial polish would.

This is why Sierra's anti-slop pivot (snapshot language, IMG_2222.HEIC,
mixed indoor lighting) is the right move — it builds trust with the
audience, not just defeats AI detectors.

---

## Tier 3 — "AI influencer in a box" repos

Pre-built pipelines worth studying for orchestration patterns. None are
production-ready for Sierra, but their architecture is instructive.

- [SamurAIGPT/AI-Influencer-Generator](https://github.com/SamurAIGPT/AI-Influencer-Generator) — closest to a turn-key open pipeline. Study the prompt-orchestration layer.
- [Anil-matcha/Open-Generative-AI](https://github.com/Anil-matcha/Open-Generative-AI) — uncensored Higgsfield/Krea clone, 200+ models. MIT. Study if you want to internalize Higgsfield Soul 2.
- [renefatuaki/influencer-ai](https://github.com/renefatuaki/influencer-ai) — Spring Boot + Mongo Twitter automation. Cherry-pick the scheduling layer.

---

## Recommended next 30-day install list

In priority order, with ETA + cost.

1. **Switch from `kudzueye/Boreal` realism LoRA via Replicate `extra_lora`** — *DONE this commit*, free, 5 min.
2. **Drop `guidance_scale` from 3.5 → 2.5** — *DONE this commit*, free, the single biggest realism unlock.
3. **Sierra v2 retrain** with deliberately imperfect refs (5 off-axis, 3 harsh-light, 2 motion-blur, 2 phone-selfie). $5 + 30min Replicate H100. Resolves v1's B4 close-up failure.
4. **LatentSync 1.6 trial** — render the same talking-head with Wan 2.7 + LatentSync, blind-A/B. Replace if LatentSync wins (it will). 4 hours setup, $0–5 inference.
5. **Chatterbox voice clone** — A/B vs ElevenLabs Brielle. 1 hour to set up, free at scale.
6. **Local ComfyUI workstation** ($0 if you have a 24GB GPU; ~$3K otherwise). Unlocks the multi-LoRA + ADetailer + propost + LUT chain that Replicate can't run. 1 day setup.
7. **PuLID-Flux Enhanced** as Sierra's fallback for shots where the LoRA drifts (close-ups, profiles). Local-only. 4 hours.
8. **DWPose ControlNet** for shoot-coherence (lock Sierra's pose across all 5 shots in a single "session"). Local-only. 2 hours.

---

## The honest assessment

Right now Sierra is **first-90%-quality** across the stack:

- Image: Replicate Flux + custom LoRA + (after this commit) anti-slop
  prompts + extra realism LoRA. Should produce convincingly real output
  on medium and full-body shots; close-ups still need v2 retrain.
- Voice: ElevenLabs Brielle, locked. Production-grade. Chatterbox
  backup recommended for cost.
- Lipsync: Wan 2.7. Functional but lifeless on >8s. **LatentSync swap
  is the single biggest video-quality upgrade left.**
- Assembly: ffmpeg with libass + (after this commit) film grain. Solid.
- Ops: Lovable portal + research + analytics tools. Strong.

The path to **95%+ tier** is:
- Sierra v2 retrain (close-ups)
- Local ComfyUI (multi-LoRA + face detailer + post-process)
- LatentSync (video lipsync)
- A "manual finish" Photoshop pass (the Aitana lesson) — this is the
  one that no automation replaces

**The 95%+ tier is what makes the difference between "looks AI"
and "indistinguishable."** We can get there in 30 days with the install
list above.

---

## Sources

- [InfiniteYou (ByteDance)](https://github.com/bytedance/InfiniteYou)
- [LatentSync (ByteDance)](https://github.com/bytedance/LatentSync)
- [Chatterbox (Resemble AI)](https://github.com/resemble-ai/chatterbox)
- [PuLID-Flux Enhanced](https://github.com/sipie800/ComfyUI-PuLID-Flux-Enhanced)
- [PuLID-Flux ll (lldacing)](https://github.com/lldacing/ComfyUI_PuLID_Flux_ll)
- [LivePortrait](https://github.com/KwaiVGI/LivePortrait)
- [MuseTalk](https://github.com/TMElyralab/MuseTalk)
- [ostris ai-toolkit](https://github.com/ostris/ai-toolkit)
- [Fannovel16 controlnet_aux](https://github.com/Fannovel16/comfyui_controlnet_aux)
- [The Clueless / Aitana profile (NetInfluencer)](https://www.netinfluencer.com/the-clueless/)
- [SamurAIGPT AI Influencer Generator](https://github.com/SamurAIGPT/AI-Influencer-Generator)
