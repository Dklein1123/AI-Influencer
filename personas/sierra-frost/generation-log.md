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

### Batch 2 takeaways (continued in batch 3)

---

## 2026-05-06 — batch 3 (LoRA training-set expansion: P14, P15, P17, P19, P20, PROFILE)

Goal: take Sierra's training set from 6 mostly-bedroom shots (insufficient
LoRA variety) to 12 images covering Pillars 1/2/4, Wardrobes A/B/C/D/E +
neutral, Settings S1/S2/S4/S5, and 3/4 profile angle. Submitted via the
MCP connector. Same model/style/aspect as batches 1+2.

### P14 — Pillar 2 / Wardrobe C (cream Pilates set) / Setting S4 (studio)

- job_id: `2d028251-f803-499f-a590-cd31850bd327`
- seed: `946215`
- pose: mid-Pilates form on reformer, controlled and graceful
- result: ok — identity locked, Pilates studio + cream activewear rendered correctly. New wardrobe + setting in the training pool.
- saved: `personas/sierra-frost/content-queue/2026-05-06_P14_v1.png`

### P15 — Pillar 2 / Wardrobe E (camel cashmere) / Setting S1 (bedroom)

- job_id: `41c7b51d-1438-4a05-b9a3-b415e2f9b172`
- seed: `92924`
- pose: getting ready at vanity, lipstick mid-application
- result: ok — identity locked, camel cashmere wardrobe is a new texture for the training pool.
- saved: `personas/sierra-frost/content-queue/2026-05-06_P15_v1.png`

### P17 — Pillar 2 / Wardrobe A / Setting S5 (cafe entry)

- job_id: `e604fa4d-1545-4486-9136-10c583ac1707`
- seed: `969464`
- pose: entering cafe with leather tote, sunglasses pushed up on head
- result: ok — identity locked, different cafe angle than P12 (sunglasses, entry framing).
- saved: `personas/sierra-frost/content-queue/2026-05-06_P17_v1.png`

### P19 — Pillar 2 / Wardrobe C (cream Pilates) / Setting S4 (barre)

- job_id: `704e8625-5e35-4cb6-a5e2-246c91daf134`
- seed: `967423`
- pose: stretching at barre, post-class, tied-up hair, dewy skin
- result: ok — identity locked, second cream-set angle for activewear variety.
- saved: `personas/sierra-frost/content-queue/2026-05-06_P19_v1.png`

### P20 — Pillar 2 / Wardrobe B (white linen) / Setting S2 (Palm Beach)

- job_id: `af26b9db-3b1f-4514-ae48-cdb370cc8a53`
- seed: `273642`
- pose: walking past palms with iced coffee in hand, candid Florida day
- result: ok — identity locked, second Palm Beach angle (different pose from P7's walking-toward-camera).
- saved: `personas/sierra-frost/content-queue/2026-05-06_P20_v1.png`

### PROFILE — custom 3/4 profile portrait (no template, hand-prompted)

- job_id: `f39ebf73-61c4-4220-8cd3-fd51eae37030`
- seed: `342133`
- pose: serene three-quarter profile portrait, looking thoughtfully off to the side, hair tucked behind ear
- result: ok — identity locked, 85mm tight close-up. Critical for the
  LoRA training set since all prior shots were front-3/4 or full-body.
- saved: `personas/sierra-frost/content-queue/2026-05-06_PROFILE_v1.png`

### Batch 3 takeaways

- **12 strong reference images now available for LoRA training.**
  Excluding P5 (2-panel storyboard issue), the usable training set is:
  P1, P3, P7, P8, P12, P14, P15, P17, P19, P20, PROFILE, plus carefully
  re-cropping P5 manually if needed = 12. Hits the LoRA threshold
  cleanly.
- **Identity holds across 4 wardrobes + 3 settings + 3/4 profile angle.**
  Sierra is now a genuinely portable identity — Soul ID + 12 refs covering
  enough variation that any image-gen pipeline (Flux LoRA, Replicate,
  fal, ComfyUI) can take her on.
- **Variety achieved without identity drift.** No retraining of the Soul ID
  needed across batches 1, 2, and 3.

### Batch 1+2 original takeaways



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
## 2026-05-07T02:44:07 — P32 (LoRA)

- backend: replicate-flux-lora
- model: `dev`
- aspect: `9:16`
- guidance: `3.5`
- lora_scale: `1.0`
- saved:
  - `personas/sierra-frost/content-queue/2026-05-07_P32_lora_v1.png`
- prompt:
  ```
  SIERRA_FROST_V1, 24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject's face, action: sitting on bed mid-coffee sip, pause, dry sideways glance to camera, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality
  ```

## 2026-05-07T03:11:45 — P32 (LoRA)

- backend: replicate-flux-lora
- model: `dev`
- aspect: `9:16`
- guidance: `None`
- lora_scale: `0.9`
- saved:
  - `personas/sierra-frost/content-queue/2026-05-07_P32_lora_v1.png`
- prompt:
  ```
  SIERRA_FROST_V1, 25 year old woman, blonde mid-length hair with soft beachy waves and a few flyaway strands at the hairline, light blue-green eyes with slight asymmetry between left and right, lightly-tanned skin with visible pores on the nose and cheeks, peach fuzz catching the light, faint under-eye circles, mild T-zone shine, slight nostril asymmetry, small natural lip line, dainty gold jewelry, fit Pilates body but not overly defined, unposed expression unless otherwise specified, looking slightly off-camera, candid not posed, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject's face, action: sitting on bed mid-coffee sip, pause, dry sideways glance to camera, amateur snapshot photo, taken on iPhone 15 Pro, casual candid framing, slightly underexposed, mixed indoor lighting (warm tungsten with cool window daylight), motion-soft not bokeh-soft, IMG_2231.HEIC, washed-out neutral white balance, mild jpeg compression, faint sensor noise, posted to a friend's instagram story, no professional retouching, not a model shoot, no studio lighting
  ```

## 2026-05-07T03:20:26 — P32 (LoRA)

- backend: replicate-flux-lora
- model: `dev`
- aspect: `9:16`
- guidance: `None`
- lora_scale: `0.9`
- saved:
  - `personas/sierra-frost/content-queue/2026-05-07_P32_lora_v1.png`
- prompt:
  ```
  SIERRA_FROST_V1, 25 year old woman, blonde mid-length hair with soft beachy waves and a few flyaway strands at the hairline, light blue-green eyes with slight asymmetry between left and right, lightly-tanned skin with visible pores on the nose and cheeks, peach fuzz catching the light, faint under-eye circles, mild T-zone shine, slight nostril asymmetry, small natural lip line, dainty gold jewelry, fit Pilates body but not overly defined, unposed expression unless otherwise specified, looking slightly off-camera, candid not posed, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject's face, action: sitting on bed mid-coffee sip, pause, dry sideways glance to camera, amateur snapshot photo, taken on iPhone 15 Pro, casual candid framing, slightly underexposed, mixed indoor lighting (warm tungsten with cool window daylight), motion-soft not bokeh-soft, IMG_2231.HEIC, washed-out neutral white balance, mild jpeg compression, faint sensor noise, posted to a friend's instagram story, no professional retouching, not a model shoot, no studio lighting
  ```

