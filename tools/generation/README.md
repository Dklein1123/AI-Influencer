# `tools.generation` — Higgsfield wrapper

Programmatic content generation for AI-Influencer personas. Wraps the
official `higgsfield-client` SDK and produces prompts from each persona's
locked spec (base block + wardrobe + setting + style suffix + negative).

**One command = one or many generations queued, polled, downloaded, and
logged.**

---

## Setup (one-time, on your local machine)

> Important: this tool can't run from the Claude Code on the web sandbox —
> the sandbox blocks outbound calls to `platform.higgsfield.ai`. Run it
> from your laptop or a server you control.

### 1. Clone the repo and create a venv
```bash
git clone https://github.com/Dklein1123/AI-Influencer.git
cd AI-Influencer
python3 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r tools/generation/requirements.txt
```

### 2. Set your API key
Create `~/.AI-Influencer.env` (outside the repo so it can't be committed):
```bash
umask 077
cat > ~/.AI-Influencer.env <<'EOF'
HF_KEY=your_key_id:your_key_secret
SIERRA_SOUL_ID=
EOF
chmod 600 ~/.AI-Influencer.env
```

The tool auto-loads this file on every run via `python-dotenv`.

### 3. Train Sierra's Soul ID (web UI for now)
Soul ID training is most reliable via Higgsfield's web app:

1. Go to https://higgsfield.ai → Soul / Character section
2. Upload 15–20 reference images (varied angles, consistent lighting)
3. Name it `sierra-frost-v1`
4. Wait ~5 minutes for training
5. Copy the resulting Soul ID
6. Paste into `~/.AI-Influencer.env` as the value of `SIERRA_SOUL_ID=...`

After this step every generation automatically locks Sierra's identity.
Without a Soul ID, generations still run but identity will drift.

---

## Daily use

### List all templates
```bash
python -m tools.generation --list
```

### Dry-run (no API call, no credits) — see the composed prompt
```bash
python -m tools.generation --dry-run P3
python -m tools.generation --dry-run P1 P3 P7 P12
```

### Generate one
```bash
python -m tools.generation P3
```

### Generate a batch (this is the typical workflow)
```bash
python -m tools.generation P1 P3 P7 P12 P19 P31
```

### Override aspect ratio or seed
```bash
python -m tools.generation --aspect 4:5 --seed 42 P47
```

### Different persona (when added to the portfolio)
```bash
python -m tools.generation --persona avery-cole P1
```

---

## What the tool does on each generation

1. Loads the persona module (e.g. `sierra_frost.py`)
2. Composes the full prompt: base block + wardrobe + setting + shot type +
   camera motion + pose + style suffix
3. Adds the locked negative prompt + safety tolerance
4. Looks up the persona's Soul ID from the env var; attaches if present
5. Submits to Higgsfield (default endpoint `/v1/text2image/soul` for
   stills; switch via `--application`)
6. Polls status until completion or failure
7. Downloads any returned media to `personas/<name>/content-queue/`
8. Appends a structured entry to `personas/<name>/generation-log.md`

Filenames follow `YYYY-MM-DD_<template>_v<n>.<ext>`.

---

## Output locations

| What | Where |
|---|---|
| Generated media | `personas/<name>/content-queue/` (gitignored) |
| Generation log | `personas/<name>/generation-log.md` (committed) |
| Persona prompt definitions | `tools/generation/<name>.py` |
| API key + Soul ID | `~/.AI-Influencer.env` (NEVER committed) |

---

## Cost reference (current Higgsfield pricing)

- Image (Soul text-to-image): ~0.25–5 credits per generation
- Video (DoP image-to-video): 15–25 credits
- Premium video (Sora 2 / Veo 3.1): 40–70 credits

Plans: Starter $15 (200 credits), Plus $39, Ultra $99–119 (3000 credits, 8
parallel jobs). Credits **expire 90 days, do not roll over**.

A typical 28-post batch (Sierra's 14-day sprint) is ~30–50 credits at the
Soul image tier — well within Plus or Ultra. Always verify with
`--dry-run` before committing real credits.

---

## Adding a new template

1. Open `tools/generation/<persona>.py`
2. Add an entry to `TEMPLATES`:
   ```python
   "P51": {
       "setting": "S1",
       "wardrobe": "A",
       "shot": "medium close-up",
       "motion": "static lock-off",
       "pose": "your pose description",
       "pillar": 1,
       "kind": "tiktok",
   },
   ```
3. Run `--dry-run P51` to verify it composes correctly
4. Generate live when satisfied

## Adding a new persona

1. Create `tools/generation/<persona_name>.py` (use `sierra_frost.py` as
   the template — copy and edit `BASE_BLOCK`, `NEGATIVE_PROMPT`,
   `STYLE_SUFFIX`, `WARDROBE`, `SETTINGS`, `TEMPLATES`)
2. Add the corresponding `<PERSONA>_SOUL_ID` env var to
   `~/.AI-Influencer.env`
3. Train the Soul ID via the Higgsfield web UI
4. Run `python -m tools.generation --persona <persona-name> --list` to
   verify

---

## Known limitations / TODO

- **No Soul ID training command.** The Python SDK's exact API surface for
  character creation is unstable in beta; web UI is more reliable.
  Revisit when SDK stabilizes.
- **Single-endpoint default.** Defaults to `/v1/text2image/soul`. To
  generate video, pass `--application /v1/image2video/dop` (you'll also
  need to wire an input image — not yet supported via CLI).
- **Motion presets aren't ID-mapped yet.** The motion text in templates is
  free-form; for DoP video we'd need to fetch motion preset IDs from the
  Higgsfield API and map names → IDs. Add when wiring video.
- **Re-hosting.** Higgsfield asset URLs aren't guaranteed permanent. We
  download immediately on success, but the original URL is the only
  re-fetch path in the log if the local file is lost.
