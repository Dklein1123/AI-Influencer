# Sierra LoRA v1 — bake-off evaluation rubric

> Run this immediately after `dklein1123/sierra-frost-v1` training completes.
> Outputs an objective decision: which backend handles which use case.
> Bake-off is run once per LoRA version; results live in §Results below.

## Test setup

Generate the same 4 prompts on both backends and grade side-by-side.

| Slot | Test prompt template | Why |
|---|---|---|
| **B1 — bedroom hero** | "SIERRA_FROST_V1, sitting at edge of bed, navy midi dress with cream blazer, scandinavian bedroom, soft morning light" | Hardest setting — most reference data, must hold ID |
| **B2 — Palm Beach walking** | "SIERRA_FROST_V1, walking forward at golden hour, white linen sundress, Palm Beach waterfront, palm trees" | Out-of-bedroom — tests setting transfer |
| **B3 — cafe productive** | "SIERRA_FROST_V1, looking up from MacBook directly to camera, navy dress and cream blazer, marble cafe table" | Tests Pillar 4 wardrobe + S5 setting |
| **B4 — close-up profile** | "SIERRA_FROST_V1, three-quarter profile portrait looking thoughtfully off to the side, soft window light, intimate" | Hardest framing — tests face fidelity |

For each slot, generate both:
- **Soul 2 baseline** (existing `tools.generation`, with the trained Higgsfield Soul ID)
- **LoRA v1** (`tools.lora.generate`) at `lora_scale=1.0` and at `lora_scale=0.85`

Two LoRA scales because rank-32 LoRAs sometimes over-condition at 1.0 and
look better at 0.80–0.90.

## Grading — three axes, 1–10 each

| Axis | What you're judging | 10 = | 5 = | 1 = |
|---|---|---|---|---|
| **Identity** | Is it Sierra? | indistinguishable from Soul 2 reference | recognizable but slightly off | different person |
| **Prompt fidelity** | Did it follow the prompt? | every detail rendered | most details, one slip | half the details missed |
| **Aesthetic** | Editorial polish | Vogue-ready | average AI-image quality | uncanny / over-baked |

A backend "wins" a slot if it scores **higher across the sum** of the
three axes for that slot.

## Decision rule

After grading 4 slots × 2 backends = 8 generations:

| Outcome | Recommended posture |
|---|---|
| LoRA wins ≥3 slots, Identity ≥7 in all slots | **Switch high-volume traffic to LoRA.** Soul 2 reserved for hero shots only. |
| LoRA wins 2 slots, Identity ≥7 in all slots | **Mixed mode.** LoRA for bedroom + cafe; Soul 2 for outdoor + close-ups. |
| LoRA wins 0–1 slots OR Identity <7 in any slot | **Retrain LoRA v2.** Reasons usually: too few refs in a setting, lr too aggressive, steps too low. |

## Cost-per-image after the decision

| Backend | Cost / 1024x1024 | Time / image | Daily cost @ 10 images |
|---|---|---|---|
| Higgsfield Soul 2 | ~$0.10–0.25 | 30–90s | $1.00–2.50 |
| Replicate Flux + LoRA v1 | ~$0.003 | 4–8s | $0.03 |

**At anything beyond ~5 images/day, LoRA pays for itself the first week.**

## Results — fill in after bake-off

```
2026-XX-XX  LoRA v1  bake-off

| Slot | Backend           | Identity | Prompt | Aesthetic | Total |
|------|-------------------|----------|--------|-----------|-------|
| B1   | Soul 2            |          |        |           |       |
| B1   | LoRA v1 (s=1.0)   |          |        |           |       |
| B1   | LoRA v1 (s=0.85)  |          |        |           |       |
| B2   | Soul 2            |          |        |           |       |
| B2   | LoRA v1 (s=1.0)   |          |        |           |       |
| B2   | LoRA v1 (s=0.85)  |          |        |           |       |
| B3   | Soul 2            |          |        |           |       |
| B3   | LoRA v1 (s=1.0)   |          |        |           |       |
| B3   | LoRA v1 (s=0.85)  |          |        |           |       |
| B4   | Soul 2            |          |        |           |       |
| B4   | LoRA v1 (s=1.0)   |          |        |           |       |
| B4   | LoRA v1 (s=0.85)  |          |        |           |       |

Decision: <to be filled>
```

## What gets committed after the bake-off

- All 12 generated bake-off images saved to `personas/sierra-frost/lora-bakeoff/`
  (gitignored)
- A 2×6 contact sheet for visual review at
  `personas/sierra-frost/lora-bakeoff-contact.png` (committed)
- This file with the Results section filled in
- A short ADR (architectural decision record) in
  `tools/lora/v1-decision.md` capturing the chosen posture
