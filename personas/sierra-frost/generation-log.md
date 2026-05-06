# Sierra Frost — Generation Log

Append-only log of every generation. Do not edit history.

## 2026-05-06 — first live batch (P1, P3, P8)

First end-to-end test of the generation pipeline against Higgsfield Soul 2.0
with the trained Soul ID `87b6278b-8407-479d-b127-a8f2bc064ed1`
(`sierra-frost-v1`). Submitted via the Higgsfield MCP connector while the
Python wrapper was being patched for the Soul 2 API shape (params wrapper +
`width_and_height` literals + `soul_id` instead of `custom_reference_id`).

- model: `soul_2` (internal: `text2image_soul_v2`)
- aspect: 9:16 → 1152x2048
- style: General (default), strength 1.0
- quality: 1080p
- soul_reference: sierra-frost-v1

### P1 — Pillar 1 / Wardrobe A / Setting S1

- job_id: `82e43aaa-a6cc-49cc-9a2f-ee213121b571`
- seed: `647249`
- pose: sitting at edge of bed, soft confident expression, looking off-camera
- result: ok — identity locked, wardrobe + setting rendered correctly
- saved: `personas/sierra-frost/content-queue/2026-05-06_P1_v1.png`
- source: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_055119_82e43aaa-a6cc-49cc-9a2f-ee213121b571.png

### P8 — Pillar 1 / Wardrobe A / Setting S1

- job_id: `b7c7a868-d234-4f16-8518-83896850ee3b`
- seed: `87114`
- pose: pearl-strand earring detail, soft side-lit, neutral expression
- result: ok — identity locked; model rendered medium portrait rather than
  the requested tight close-up (note for prompt iteration on Soul 2)
- saved: `personas/sierra-frost/content-queue/2026-05-06_P8_v1.png`
- source: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_055243_b7c7a868-d234-4f16-8518-83896850ee3b.png

### P3 — Pillar 1 / neutral wardrobe / Setting S1

- job_id: `39a41c0c-d339-4786-a96b-fcd977f88767`
- seed: `528443`
- pose: looking directly to camera, dry knowing expression
- result: stalled — Higgsfield queue held this job in `in_progress` for
  10+ minutes while siblings finished in <90s. Treated as transient
  service hiccup; re-submitted as a fresh job (see batch 2).

---

## 2026-05-06 — batch 2 (P3 re-do, P5, P7, P12)

Expansion across pillars + settings + wardrobes to validate Sierra's
identity holds beyond the bedroom. Submitted via the MCP connector.
Same model/style/aspect as batch 1.

### P3 (re-submission) — Pillar 1 / neutral wardrobe / Setting S1

- job_id: `ee34725b-347f-4571-b065-9242a454163f`
- seed: `75931`
- pose: looking directly to camera, dry knowing expression
- result: ok — identity locked. Wardrobe rendered as minimal white tube
  top (Soul 2's interpretation when no wardrobe block is supplied);
  acceptable for neutral-wardrobe template, worth flagging if neutral
  templates need a "modest default" added.
- saved: `personas/sierra-frost/content-queue/2026-05-06_P3_v1.png`
- source: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060058_ee34725b-347f-4571-b065-9242a454163f.png

### P5 — Pillar 2 / Wardrobe D (modest cream/dusty pink) / Setting S1

- job_id: `188e7343-edce-49c8-a076-e225fece7dd6`
- seed: `59164`
- pose: sitting cross-legged on bed with open journal, morning light, serene
- result: ok with caveat — identity locked, dusty pink dress + cross
  necklace + bedroom rendered, BUT Soul 2 returned a 2-panel storyboard
  in one frame (likely from "slow dolly pull back" prompting it to
  imagine multiple frames). Crop to taste, or revise camera-motion phrasing
  for stills (motion phrases are designed for video templates, not
  text2image).
- saved: `personas/sierra-frost/content-queue/2026-05-06_P5_v1.png`
- source: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060108_188e7343-edce-49c8-a076-e225fece7dd6.png

### P7 — Pillar 2 / Wardrobe B (Florida casual) / Setting S2 (Palm Beach)

- job_id: `c00d69bc-5609-47f9-8324-9b41d73e4c1a`
- seed: `715240`
- pose: walking toward camera, hair moving in breeze, soft smile, golden hour
- result: ok — identity locked, Palm Beach environment rendered (palm
  trees, white classical architecture, waterfront, golden hour). Soul 2
  rendered the linen sundress as a fitted mini rather than thin-strap
  midi; close to spec. Strong polished resort look.
- saved: `personas/sierra-frost/content-queue/2026-05-06_P7_v1.png`
- source: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060119_c00d69bc-5609-47f9-8324-9b41d73e4c1a.png

### P12 — Pillar 4 / Wardrobe A (Tailored Polish) / Setting S5 (Cafe)

- job_id: `b181ca33-b4a3-470e-80a1-df68ceb6976c`
- seed: `196883`
- pose: looking up from laptop directly to camera, faint smile
- result: ok — identity locked, marble cafe table + MacBook + latte +
  navy midi + cream blazer + camel handbag all rendered, productive
  intimate cafe atmosphere. Strong on-pillar Pillar-4 (entrepreneurial)
  output.
- saved: `personas/sierra-frost/content-queue/2026-05-06_P12_v1.png`
- source: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060130_b181ca33-b4a3-470e-80a1-df68ceb6976c.png

### Batch 2 takeaways

- Identity (Soul ID 87b6278b…) holds across 4 distinct settings,
  wardrobes, and pillars without drift. Soul 2 + this Soul ID is
  production-ready for Sierra.
- "Camera motion" wording in templates is video-oriented and confuses
  Soul 2 stills (see P5). For text2image, prefer phrases like
  "framing: medium close-up" over "camera motion: slow dolly".
- "Neutral wardrobe" (P3) lets Soul 2 default to revealing minimalism;
  if the brand voice requires modest defaults, add a "modest neutral
  default" wardrobe block in `sierra_frost.WARDROBE`.
- Soul 2's "tight close-up" framing direction is loosely respected; if
  a true close-up is needed, simplify the prompt and lean on framing
  language earlier in the sentence.

---

## Pipeline notes (2026-05-06)

Discoveries from the first batch, captured here so future runs don't
re-learn them:

1. **`/v1/text2image/soul` is the only Soul-family path.** Soul 2 is
   selected via `params.model = "soul_2"`, not via a different URL.
2. **API expects `{"params": {...}}` wrapping.** Flat-keyed bodies return
   `body.params: missing`.
3. **`width_and_height` is a literal whitelist**, not free-form. The Soul 2
   set is `1152x2048, 2048x1152, 2048x1536, 1536x2048, 1344x2016, 2016x1344,
   960x1696, 1536x1536, 1536x1152, 1696x960, 1152x1536, 1088x1632, 1632x1088,
   1120x1680`. **There is no exact 4:5** — closest portrait is 3:4
   (`1536x2048`). The wrapper now maps `4:5 → 1536x2048` automatically.
4. **Soul 2 ignores `negative_prompt` and `safety_tolerance`.** They were
   removed from the wrapper's request body; `persona.NEGATIVE_PROMPT` is
   retained as documentation and for future Soul 1 / other-model fallback.
5. **Soul reference field is `soul_id`** (not `custom_reference_id` —
   though internally the platform stores it as `custom_reference_id`).
6. **Platform API key billing is separate from web/MCP plan.** The
   Ultimate plan's 719 credits do not apply to API-key generations; a
   `403 "Not enough credits"` was returned even though the same generation
   ran successfully via the MCP connector. Top up API credits in the
   Higgsfield dashboard before using the CLI wrapper for live batches.
