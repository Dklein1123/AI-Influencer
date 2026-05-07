# Sierra Realism Stack — kill the AI-pretty look

> Technical playbook for making Sierra's visuals indistinguishable from
> a real iPhone snap. Synthesis of community-tested 2026 Flux realism
> research. The TL;DR: don't describe a "photo" — describe a
> **snapshot**. Drop FluxGuidance to 2.5. Stack a realism LoRA. Add a
> face/eye detailer pass. Add film grain post.

---

## Why default Flux output looks AI

Flux Dev is **guidance-distilled toward "professional / pretty."** Out of
the box it produces:

- Perfect facial symmetry (real faces aren't symmetric)
- Airbrushed skin (no pores, no peach fuzz, no T-zone shine)
- Beauty-light bias (golden-hour soft, never harsh on-camera flash)
- Bokeh-soft backgrounds (real iPhone photos have motion-soft, not
  optical-soft)
- "Editorial polish" — what Annie Leibovitz would shoot, not what your
  friend texts you from a brunch table

The fix is to actively prompt **DOWN** toward casual snapshot, not UP
toward editorial. Every adjective stack like "shot on Sony A7IV / 50mm
prime / f/2.0 / golden hour" makes it worse, not better.

---

## The 5-move anti-slop fix (in priority order)

### 1. Drop FluxGuidance from 3.5 → 2.5 *(single biggest knob)*

**~50% of the AI-pretty look comes from over-guidance.** Flux's distilled
CFG controls how strongly the model "interprets" the prompt; the higher,
the more "polished." 2.5 is the realism-community sweet spot. Below 2.0
prompt adherence collapses; above 3.0 the beauty-mode kicks in.

In our code: `tools/lora/generate.py` now uses `guidance_scale=2.5` as
default. Earlier code shipped `guidance=3.5` which Replicate **silently
ignored** (param name was wrong) — the schema wants `guidance_scale`.
Free win: just rerun with the correct param.

### 2. Snapshot-language prompts, not editorial-language

Replace photographer/lens/aperture jargon with **what a real person would
write to label their phone photo**. Specific words that empirically
break beauty-mode:

```
✅ amateur snapshot photo
✅ taken on iPhone 15 Pro
✅ IMG_2222.HEIC          (the EXIF filename hack — Flux learned it)
✅ Reddit selfie, flickr 2007, posted to facebook 2014
✅ Polaroid 600, Kodak Portra 400, disposable camera
✅ harsh on-camera flash, mixed tungsten and daylight
✅ slightly underexposed, washed-out white balance, mild jpeg compression
✅ candid, unposed, looking slightly off-camera, mid-blink
```

Counter-intuitive: **"shot by Annie Leibovitz" makes it worse**. What works:
"shot by a friend at a party," "taken by mom," "selfie."

### 3. Skin-realism phrases (the descriptive ones, not the rendering jargon)

Flux ignores rendering vocabulary ("subsurface scattering," "PBR skin")
and responds to **descriptive photo language**:

```
✅ visible pores on the nose and cheeks
✅ peach fuzz catching the light
✅ faint under-eye circles
✅ mild T-zone shine
✅ slight asymmetry to face / nostril asymmetry
✅ fine baby hairs at hairline
✅ slight redness at the chin
```

These are now baked into `BASE_BLOCK` in `tools/generation/sierra_frost.py`.

### 4. Stack ONE realism LoRA on top of Sierra's

Replicate's `flux-dev-lora` schema accepts `extra_lora` + `extra_lora_scale`.
We can stack a single realism LoRA without leaving Replicate.

| LoRA | Trigger | Stack with Sierra @ |
|---|---|---|
| **Boreal-FD (Boring Reality)** — `kudzueye/Boreal` | `phone photo` | Sierra 0.95 + Boreal 0.5 |
| **Amateur Snapshot Photo** — Civitai #970862 | `early 2010s snapshot photo captured with a phone` | Sierra 0.9 + Amateur 0.6 |
| **iPhone Photo Realism Booster** — Civitai #738556 | `iphone photo` | Sierra 0.9 + iPhone 0.5 |
| **Photorealistic Skin (No Plastic)** — Civitai #1157318 | `aidmarealisticskin` | Sierra 0.85 + Skin 0.6 |

**Recommended default for Sierra: Boreal-FD @ 0.5.** It's the lowest-
collapse-risk option and produces phone-snap output. Set via env:

```bash
echo 'SIERRA_EXTRA_LORA=kudzueye/Boreal' >> ~/.AI-Influencer.env
```

Or per-run: `python -m tools.assembly.from_trend --extra-lora kudzueye/Boreal`.

For more grit on a specific shoot: `--extra-lora kudzueye/Boreal --extra-lora-scale 0.7`.

**Constraint:** Replicate `extra_lora` only stacks ONE additional LoRA.
For 2-3 LoRA stacks (Sierra + Boreal + Amateur Snapshot), we need local
ComfyUI. Roadmap below.

### 5. ffmpeg post-process: film grain + curves + vignette

Even a perfect Flux gen still reads AI because **it has zero sensor
noise.** Adding 5% grain is the single most-effective casual-viewer
fooler. Now baked into `tools/assembly/pipeline.py:_video_filter()`:

```
,curves=preset=vintage,vignette=PI/5,noise=alls=10:allf=t+u
```

- `curves=preset=vintage`: mild Portra/Cinestill warm-amber cast
- `vignette=PI/5`: barely-perceptible darken at edges
- `noise=alls=10:allf=t+u`: subtle moving grain, temporal+uniform

Toggle with `assemble(..., film_look=True)` (default ON).

---

## Beyond Replicate — the local ComfyUI roadmap

Replicate gets us 80% of the way. The remaining 20% requires a local
ComfyUI workstation (24GB VRAM minimum). When we move:

1. **Multi-LoRA stack** (Sierra @ 0.9 + Boreal @ 0.5 + Amateur Snapshot
   @ 0.6 + Photorealistic Skin @ 0.6).
2. **Face Detailer pass** (ImpactPack, denoise 0.30–0.35) +
   **eye detailer** with `eyes_v2.pt` Ultralytics model. Fixes
   symmetric AI-doll eyes specifically.
3. **Detail Daemon** — `Jonseed/ComfyUI-Detail-Daemon`. Settings:
   `detail_amount 0.4, start 0.2, end 0.8, bias 0.5`. Adds micro-detail
   without over-sharpening.
4. **Lying Sigma Sampler** — `dishonesty_factor -0.05`, `start 0.15`,
   `end 0.85`. Stronger negatives = more pores.
5. **SD1.5 Epic Realism img2img skin-only pass** at denoise 0.30. The
   "MyAIForce trick" — adds real pore noise SD1.5 has and Flux doesn't.
6. **Sampler:** `dpmpp_2m / sgm_uniform` or `deis / ddim`, **25–28
   steps full**. Lightning collapses skin texture.
7. **Post-process chain (final)**: ComfyUI-propost FilmGrain (0.04–0.06)
   → ComfyUI-Optical-Realism halation (0.15) → BilboX/Olm LUT (Portra
   400 or Cinestill 800T) → optional ComfyUI-Darkroom (161 physics-
   based film stocks).

---

## Identity safeguards (avoid LoRA collapse)

When stacking realism LoRAs on top of Sierra's character LoRA:

- **Keep Sierra ≥ 0.85.** Below that, identity drifts.
- **Any single style LoRA ≤ 0.7.** Above that, it overrides identity.
- **Stack of 2–3 max.** 4+ produces a face that could be "anyone."
- **Test on close-up frames first.** Sierra v1 already fails on 3/4-
  profile close-ups (`v1-decision.md` slot B4). Adding realism LoRAs
  amplifies the failure. Use medium and full-body shots until v2 retrains.

For B4-style problem shots (intimate close-ups, profile angles),
**InfiniteYou** (ByteDance) is the SOTA fallback — but it's CC-BY-NC,
academic-only, and not commercial-safe. Use as a research reference, not
production.

---

## Sierra v2 retrain plan (when reference dataset is ready)

The v1 training set was beauty-lit, frontal, and clean. v2 should
DELIBERATELY include imperfect inputs:

- **5+ off-axis angles** (3/4 profile, looking down, looking up) —
  fixes the v1 close-up failure
- **3+ harsh-light shots** (on-camera flash, mid-day window) — teaches
  the LoRA that Sierra exists in non-beauty light
- **2+ motion-blur shots** — candid energy, not posed
- **2+ "phone selfie" shots** — slight angles, awkward arms, the way a
  real influencer posts to story

Train cost ~$5 on Replicate H100, ~30 min. Bake-off rubric is in
`personas/sierra-frost/lora-bakeoff-rubric.md`; v2 needs Identity ≥ 8 in
**all** B-slots before it ships.

---

## Sources

- [Boreal-FD on HuggingFace](https://huggingface.co/kudzueye/Boreal)
- [Amateur Snapshot Photo (Civitai #970862)](https://civitai.com/models/970862)
- [Amateur Photography v6 (Civitai #652699)](https://civitai.com/models/652699)
- [iPhone Photo Realism Booster (Civitai #738556)](https://civitai.com/models/738556)
- [Photorealistic Skin No Plastic (Civitai #1157318)](https://civitai.com/models/1157318)
- [UltraReal Fine-Tune v4 (Civitai #978314)](https://civitai.com/models/978314)
- [Flux Realism Walkthrough (Civitai)](https://civitai.com/articles/8967/flux-realism-walkthrough)
- [Detail Daemon node](https://github.com/Jonseed/ComfyUI-Detail-Daemon)
- [ComfyUI-propost (post-process nodes)](https://github.com/digitaljohn/comfyui-propost)
- [ComfyUI-Optical-Realism (halation)](https://github.com/skatardude10/ComfyUI-Optical-Realism)
- [ComfyUI-Darkroom (161 film stocks)](https://github.com/jeremieLouvaert/ComfyUI-Darkroom)
- [k-mktr 20k photoreal portrait prompt dataset](https://huggingface.co/datasets/k-mktr/improved-flux-prompts-photoreal-portrait)
- [MyAIForce skin realism workflow](https://myaiforce.com/flux-skin-realism/)
- [InfiniteYou (ByteDance)](https://github.com/bytedance/InfiniteYou) — SOTA face-consistency, but CC-BY-NC; reference only
