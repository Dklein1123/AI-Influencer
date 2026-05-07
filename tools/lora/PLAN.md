# Sierra LoRA training plan (Replicate / Flux)

> Goal: train a personal LoRA on Sierra's reference images so we can run
> identity-preserving generations at ~$0.003/image instead of Higgsfield
> Soul 2's ~$0.10–0.25/image. Saves real money the moment we cross
> ~100 images, which we will in week one.

## TL;DR

1. Pick 12–20 of our best Higgsfield-generated Sierra images, varied
   angle/lighting/wardrobe, **all identity-locked to the Soul ID**.
2. Caption them with a consistent trigger token (`SIERRA_FROST_V1`).
3. Zip and upload to Replicate. Train `ostris/flux-dev-lora-trainer`
   (the de-facto Flux LoRA trainer) with `trigger_word=SIERRA_FROST_V1`,
   1500–2000 steps, learning rate `1e-4`. Cost: ~$2–5, ~25 minutes.
4. Inference on `black-forest-labs/flux-dev` + our trained LoRA at
   ~$0.003/image. Drop-in replacement for the Higgsfield image-gen path
   in `tools/generation/higgsfield.py`.

## Why this is the right move

- **Cost.** Higgsfield Soul 2 charges per credit (~$0.10–0.25 effective
  per image at the Plus/Ultra tiers). 200 images/month = $20–50/mo.
  Flux LoRA on Replicate at $0.003/image for the same volume = $0.60/mo.
  Math is unambiguous past ~100 generations.
- **Identity portability.** Once the LoRA exists, Sierra is no longer
  trapped in Higgsfield. We can host the LoRA on Replicate, fal.ai,
  or even a self-hosted ComfyUI box. Vendor risk drops to ~zero.
- **Iteration speed.** Replicate generations are typically 4–8s vs.
  Higgsfield's 30–90s. 10x faster prompt iteration.
- **Style steerability.** Flux + LoRA + LoRA strength gives us a slider
  between "exactly Sierra" (1.0) and "Sierra-inspired" (0.5–0.7) for
  variation work.

## Why we don't kill Higgsfield entirely

- **Soul 2 is still better at hard cases.** Tight close-ups, complex
  poses, multi-person scenes — Soul 2 retains identity better than
  most Flux LoRAs do. Keep it for hero shots.
- **Video.** Higgsfield routes Seedance/Kling/Hailuo. Replicate also
  has video, but we're already proven on Higgsfield's video stack.
- **Marketing studio.** When we land an affiliate, Higgsfield's
  marketing-studio video is a real asset.

**Recommended posture:** Soul 2 for hero stills + all video. Flux LoRA
for high-volume daily content (carousels, multi-variant tests, B-roll
backgrounds, reel filler). 80/20 split toward LoRA at scale.

## Step 1 — Select training set

Selection criteria (in priority order):

1. **Identity must be intact.** Discard any frame where Soul 2 drifted.
   For Sierra's 6 current frames, P1, P5, P7, P8, P12 all qualify. P3
   has the wardrobe issue but identity is fine — include.
2. **Variety in framing.** 1–2 close-ups, 2–3 medium, 1–2 full body.
3. **Variety in lighting.** Indoor warm window light, golden hour
   outdoor, shadow-side, soft daylight.
4. **Variety in wardrobe.** Wardrobes A, B, D minimum.
5. **No two near-duplicates.** Soul 2 sometimes returns very similar
   crops; pick the best one and drop the rest.
6. **Aspect ratio normalized.** All training images get center-cropped
   to 1024×1024 by the trainer; pre-crop yourself if a key feature
   (face) would otherwise be off-center.
7. **Minimum 12, ideal 16–20.** Below 12, the LoRA over-fits to specific
   poses. Above 25 with our current variety, marginal returns drop.

Use `tools/lora/select_and_prepare.py` to interactively or programmatically
build the set into `tools/lora/training_set/`.

## Step 2 — Caption the training set

Each image needs a paired `.txt` file with the same basename containing
the caption. Caption format:

```
SIERRA_FROST_V1, <one-sentence factual description of the image>
```

Example:
```
training_set/img_001.png
training_set/img_001.txt   ->  "SIERRA_FROST_V1, blonde woman in navy midi dress with cream blazer sitting at edge of bed, scandinavian bedroom, soft morning light"
```

Critical rules:
- **Trigger token always first.** All-caps, underscored, version-suffixed.
  We'll bump to `SIERRA_FROST_V2` if we ever retrain.
- **Don't describe Sierra's face/body.** The LoRA should learn those
  passively from the consistent face across images. Describing them
  encourages the model to treat them as conditional on prompt — bad.
- **Do describe wardrobe + setting + lighting.** This is what we'll
  vary at inference time.
- **Keep captions short (8–20 words).** Long captions over-condition.

The runner script auto-generates baseline captions using Higgsfield's
generation log (the prompts we already wrote). We then hand-edit any
that need refinement.

## Step 3 — Train

Replicate training command via the `replicate` CLI or Python SDK:

```bash
replicate train ostris/flux-dev-lora-trainer \
  --destination YOUR_USERNAME/sierra-frost-v1 \
  --input "input_images=@training_set.zip" \
  --input "trigger_word=SIERRA_FROST_V1" \
  --input "steps=1750" \
  --input "lora_rank=32" \
  --input "learning_rate=1e-4" \
  --input "batch_size=1" \
  --input "resolution=1024" \
  --input "caption_dropout_rate=0.05"
```

Training cost: typically $2.50–$5 on Replicate's H100s, ~22–28 minutes.

After training, your destination model URL becomes
`replicate.com/YOUR_USERNAME/sierra-frost-v1`. The trained LoRA file
is also downloadable for self-hosted use.

## Step 4 — Inference

Two options:

### Option A — Replicate-hosted (zero ops, ~$0.003/image)

```bash
replicate run YOUR_USERNAME/sierra-frost-v1 \
  -i prompt="SIERRA_FROST_V1, blonde woman walking on Palm Beach waterfront, white linen sundress, golden hour, palm trees, polished editorial" \
  -i lora_scale=1.0 \
  -i aspect_ratio="9:16" \
  -i guidance=3.5 \
  -i num_inference_steps=28
```

### Option B — Self-hosted via ComfyUI / Diffusers

Download the trained `.safetensors` file from Replicate, drop it in
`models/loras/`, prompt with the trigger token. Cost = electricity.
Use this when daily volume exceeds ~3,000 generations and Replicate
hosting fees become meaningful.

## Step 5 — Wire into our existing wrapper

`tools/generation/higgsfield.py` becomes one backend among several. Add
`tools/generation/replicate_flux.py` with a parallel `generate()` that
takes the same template_id and calls Replicate. Add a `--backend` flag
to the CLI that defaults to `higgsfield` for now and switches to
`replicate` once the LoRA is trained.

The persona module's `build_prompt()` stays unchanged — only the
trigger token gets prepended for Replicate, and the negative prompt
+ soul_id are stripped (Flux LoRA has its own conditioning).

## Step 6 — Evaluate

After the first 50 LoRA generations, do an A/B blind test:
- Same template, same prompt, run via Higgsfield Soul 2 and via the LoRA
- Visual review: identity (1–10), prompt fidelity (1–10), aesthetic (1–10)
- If LoRA scores ≥ Soul 2 − 1 across the three, switch high-volume traffic to LoRA
- If LoRA scores worse, retrain with more data / different hyperparams
- Document scores in `personas/sierra-frost/lora-evaluation.md`

## Open questions / decisions you'll need to make

1. **Replicate account.** Sign up at replicate.com (free, Stripe-backed
   billing). Generate an API token, drop it in `~/.AI-Influencer.env`
   as `REPLICATE_API_TOKEN=r8_...`.
2. **Trainer choice.** `ostris/flux-dev-lora-trainer` is the de-facto
   pick. Alternatives are `lucataco/flux-dev-lora` (faster, lower
   quality) and `replicate/fast-flux-trainer` (newer, less-tested).
   Recommend ostris.
3. **fal.ai vs Replicate.** fal.ai is also strong — slightly cheaper
   inference, harder to use for training. Stick with Replicate end-to-end
   to start.

## Cost timeline (concrete)

| Phase | Cost | When |
|---|---|---|
| Train LoRA v1 | $3.50 (one-time) | Now-ish, after 12+ training references curated |
| First 100 inferences | $0.30 | Day 1 of LoRA |
| Steady state at 200 images/month | $0.60/mo | Ongoing |
| Re-train v2 every 6 months | $3.50 each | Twice a year |
| **First-year total** | **~$15 + Higgsfield premium for hero shots only** | vs. $200–600 if Higgsfield-only |

## What lives in `tools/lora/` after this is wired up

```
tools/lora/
├── PLAN.md                      ← this file
├── select_and_prepare.py        ← curate + caption training set
├── train.py                     ← submit Replicate training job
├── monitor.py                   ← watch training, capture model id
├── generate.py                  ← inference call, drop-in for higgsfield.py
└── training_set/                ← prepared images + captions (gitignored)
```

The first three scripts are the priority for the next session. Until we
have ~12 curated reference images, training is wasted.
