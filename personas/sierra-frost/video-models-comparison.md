# Video models — head-to-head on Sierra (2026-05-06)

> A/B/C test: same Sierra reference image (P7 Palm Beach walking),
> same prompt, three vendor backends. Goal — pick the right model per
> use case.

## Test setup

- **Reference image:** `2026-05-06_P7_v1.png` (1152×2048, Sierra walking,
  Wardrobe B, Setting S2 Palm Beach)
- **Prompt (identical across all runs):** *"Sierra walks slowly forward
  toward the camera along a Palm Beach waterfront walkway in soft
  golden-hour light. Hair gently moves in the breeze. Subtle natural
  sway. Gentle relaxed smile. Palm trees softly sway in background.
  Polished editorial pace, slow handheld follow. Identity locked."*
- **Aspect:** 9:16 across all
- **Duration:** 5–6s

## Results

| Model | Vendor | Resolution | Duration | File size | Result |
|---|---|---|---|---|---|
| **Seedance 2.0** | ByteDance | 720×1280 | 5s | 1.8 MB | ✅ |
| **Kling 3.0 Pro** | Kling | 1080×1920 | 5s | 11 MB | ✅ |
| **Hailuo (minimax-2.3)** | MiniMax | — | — | — | ❌ failed twice — image reference not propagated by MCP bridge |

## Side-by-side observations

### Seedance 2.0
- **Identity preservation:** A. Sierra's face fully consistent across all 150 frames.
- **Wardrobe rendering:** B+. Wardrobe interpreted as fitted white mini rather than the linen sundress in the reference, but consistent across frames.
- **Motion quality:** B. Walking gait is believable; some hair-physics weirdness on close inspection.
- **Background:** A−. Palm trees do sway gently, walkway architecture stable.
- **Audio (auto):** Beach ambient + soft footsteps. Listenable as B-roll, replaceable.
- **Cost / time:** Faster generation (~60s); cheaper credit cost.
- **Artifacts:** Slight motion blur at frame edges; resolution is the limiter.

### Kling 3.0 Pro
- **Identity preservation:** A. Equally tight; arguably slightly more natural eye-line than Seedance.
- **Wardrobe rendering:** B+. Same fitted-mini interpretation as Seedance.
- **Motion quality:** A. Cleaner gait, more believable subtle sway, less hair artifact.
- **Background:** A. Palms move with believable wind physics; lighting holds golden hour through entire 5s.
- **Resolution:** 1080×1920 native — **6× the pixel count of Seedance**. Visibly sharper.
- **Audio (auto):** Beach ambient. Comparable to Seedance.
- **Cost / time:** Slower (~3–4 min). Higher credit cost.
- **Artifacts:** None visible at 1080p.

### Hailuo (failed)
- Two submissions returned `status=failed` with `input_image: null` in
  the dispatched params, indicating Higgsfield's MCP-to-Hailuo bridge
  is not propagating image references (the model defaults to text-only
  square 1024×1024 generation when no image attaches).
- Tried passing `medias[].value` as both a prior-generation `job_id`
  and as a freshly-uploaded `media_input` UUID. Both ignored.
- Likely a vendor-side integration bug. Re-test in a few weeks; in the
  meantime use Seedance or Kling for image-driven Sierra video.

## Verdict — pick by job

| Use case | Recommended model | Why |
|---|---|---|
| **Hero TikTok / reel** (will be the post) | **Kling 3.0 Pro** | 1080p resolution + cleanest motion. The +2 min generation time and higher credit cost are worth it for posts that ship. |
| **Daily B-roll / variant testing** | **Seedance 2.0** | Faster, cheaper. Quality penalty is real but tolerable for content you're A/B testing or mass-producing for carousels. |
| **Talking-head / direct-to-camera** | **(deferred — Hedra)** | Once Sierra has a voice clone, Hedra (Character-3, in COMPANY.md stack) is the right tool — purpose-built for lip-sync. Image-to-video via Seedance/Kling produces motion but no controllable speech. |
| **Multi-shot scenes** | **Kling 3.0 Pro multi-shot** | Kling's `multi_shots` flag (we didn't use it here) supports 2–3 shot sequences in one generation — the right tool when we want a 10s post that cuts. |
| **Cinematic premium** | **Sora / Veo (when available via MCP)** | Currently inaccessible from this stack. Seedance and Kling are the ceiling for now. |

## Default for the assembly pipeline

Update `tools/assembly/` documentation to recommend **Kling 3.0 Pro** as
the default video source for production posts. Seedance is the rapid-
iteration backstop. (No code change needed — the assembly pipeline is
backend-agnostic; it consumes whatever video file you point it at.)

## Cost-per-post (rough)

Based on Higgsfield's credit pricing:
- Seedance 5s 720p std: ~15–18 credits ≈ $0.50–0.60
- Kling 3.0 Pro 5s 1080p: ~30–40 credits ≈ $1.00–1.40
- (Hailuo unavailable here)

For a 4-video-per-week posting cadence:
- All Kling: ~$22/mo
- All Seedance: ~$10/mo
- 80/20 Kling/Seedance: ~$15/mo

Trivial vs. the value of one good post landing.

## Files generated

- `personas/sierra-frost/content-queue/2026-05-06_P7_v1.mp4` — Seedance walk
- `personas/sierra-frost/content-queue/2026-05-06_P1_v1.mp4` — Seedance idle (P1, deviated to standing)
- `personas/sierra-frost/content-queue/2026-05-06_P7_kling_v1.mp4` — **Kling 3.0 Pro walk (production-grade)**
- `personas/sierra-frost/content-queue/2026-05-06_P7_assembled_demo.mp4` — pipeline E2E proof from static P7 PNG

## Next experiments (parked for later)

1. **Kling multi-shot** — same prompt with 2 shot beats, see if we get a cut.
2. **Hailuo direct API** (bypass Higgsfield MCP) — if integration is the
   issue not the model, hitting MiniMax's API directly may unlock it.
3. **Runway Gen-3** — not in current stack but worth a $15 trial if we
   want a fourth comparison point.
4. **Sora when API drops** — likely the long-term winner for premium
   shots once accessible.
