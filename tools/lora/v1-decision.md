# Sierra LoRA v1 — decision record

**Date:** 2026-05-06
**Trained model:** `dklein1123/sierra-frost-v1:3225c5c843f49636…`
**Training cost:** ~$3.50 on Replicate H100 (~30 min)
**Bake-off cost:** ~$0.025 (8 inferences)

## Verdict

**Mixed-mode deployment.** v1 is production-grade for **frontal full-body
and medium-shot framings**. v1 **fails catastrophically on 3/4-profile and
intimate close-up framings** — it renders a recognizably different person.
Retrain v2 with profile-heavy refs before relying on the LoRA for hero
close-ups.

## Detailed evaluation

See `personas/sierra-frost/lora-bakeoff-rubric.md` §Results for the
12-row scoring matrix and `lora-bakeoff-contact.png` for the 4×3 visual
review.

### What works

- **B1 bedroom (full-body, frontal sitting):** Identity 8/10. Wardrobe A
  (navy + cream blazer) renders cleanly. Setting S1 (Scandinavian
  bedroom) preserved. Editorial polish at parity with Soul 2.
- **B2 Palm Beach (medium full, walking forward):** Identity 8/10. White
  linen sundress rendered correctly. Palm trees, golden hour, classical
  architecture all present. Slight motion-blur tells but acceptable.
- **B3 cafe (medium close, looking up from laptop):** Identity 8/10.
  Wardrobe A + marble cafe table + MacBook all present. Pillar-4
  productive vibe intact.

Both LoRA scales (1.0 and 0.85) produce roughly identical results in
these three slots — no advantage to lowering the scale.

### What fails

- **B4 three-quarter profile (intimate close-up):** Identity **2/10**.
  The LoRA renders a brunette with markedly different facial structure
  — clearly NOT Sierra. Both LoRA scales fail identically.

This isn't a small drift. It's a hard failure mode.

## Root-cause analysis

The training set had:
- **0 true 3/4-profile shots from outside the bedroom** — only PROFILE
  (1 ref) at this angle
- **2 close-up portraits** total (P3 close-up, PROFILE) — the rest are
  medium / full body
- **All 11 final refs were front-facing or 3/4-front facing** (PROFILE
  was the only one looking off-axis)

Result: the LoRA learned "Sierra = blonde-woman-facing-camera" but
didn't learn what her face looks like from a 3/4 angle. When prompted
for that angle, the model defaults to a generic "young woman in profile"
template — losing identity entirely.

This is a **training-set composition bug**, not a hyperparameter bug.

## Operating posture going forward

Until v2 ships:

| Use case | Backend | Cost / image |
|---|---|---|
| **Full-body anywhere (Sierra walking, sitting, standing)** | LoRA v1 (scale=1.0) | ~$0.003 |
| **Medium shots from the front** | LoRA v1 | ~$0.003 |
| **Outdoor scenes (Palm Beach, walking, cafe entry)** | LoRA v1 | ~$0.003 |
| **Frontal close-ups with eye contact** | Soul 2 | ~$0.10–0.25 |
| **3/4 profile / off-axis / dramatic close-up** | Soul 2 | ~$0.10–0.25 |
| **Hero shots that will be the post** | Soul 2 | ~$0.10–0.25 |

Practically: **most B-roll, carousel filler, and Reel backgrounds** go
through LoRA v1 (cheap). **Hero TikToks, brand collab assets, and
intimate close-ups** stay on Soul 2.

Effective cost-per-image at expected mix (~70% LoRA / 30% Soul 2):
- ~$0.05/image vs. $0.10–0.25 Soul-2-only
- 2–5× cheaper without giving up the angles where LoRA fails

## v2 retrain plan

Schedule the retrain after one more batch of varied-angle Soul 2
generations to fill the gap.

### Refs to add for v2 (5 new, all generated via Soul 2)

- **PROFILE-2:** 3/4 left profile, soft window light, looking directly off-camera
- **PROFILE-3:** 3/4 right profile, golden hour, looking off-camera with slight smile
- **CLOSEUP-1:** intimate close-up, looking down (reading or thinking)
- **CLOSEUP-2:** intimate close-up, eyes-to-camera, neutral expression
- **OUTDOOR-PROFILE:** Sierra in profile walking in golden hour, half-turned away from camera

This adds **5 close-up / off-axis refs** to the existing 11, bringing v2
training set to **16 refs** with much stronger angle coverage. Should
close the B4 failure mode.

### v2 hyperparameters (changes from v1)

| Param | v1 | v2 | Reason |
|---|---|---|---|
| `steps` | 1750 | **2200** | More refs → more steps |
| `lora_rank` | 32 | 32 | Keep |
| `learning_rate` | 1e-4 | 1e-4 | Keep |
| `caption_dropout_rate` | 0.05 | **0.10** | Reduce caption over-conditioning |
| `resolution` | 1024 | 1024 | Keep |

Cost: ~$4.00 training + ~$0.10 bake-off + ~$1 (5 new Soul 2 refs).
**Total v2 budget: ~$5–6.**

### v2 success criteria (re-running the same 4-slot bake-off)

- Identity ≥ 7/10 in **all 4 slots**, including B4
- LoRA wins or ties Soul 2 in B1+B2+B3
- B4 LoRA identity within 1 point of Soul 2

If v2 hits those, posture switches to: **LoRA-default for all daily
generation, Soul 2 reserved for highest-stakes brand-collab hero shots
only**. Effective cost-per-image drops to ~$0.005.

## What changed in the env

- `~/.AI-Influencer.env` now contains `SIERRA_LORA_VERSION=dklein1123/sierra-frost-v1:3225c5c843f4…`
- `tools.lora.generate <template_id>` works for the 70% of use cases
  where v1 is good enough
- `tools.generation <template_id>` (Soul 2) remains the default for
  hero shots and the cases v1 fails

The CLI surface is unchanged — same template IDs, same flags, just two
different commands depending on which backend you want. Eventually
this becomes a single CLI with a `--backend` flag that picks
intelligently.
