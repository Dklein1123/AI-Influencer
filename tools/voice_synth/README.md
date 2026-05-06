# `tools.voice_synth` — ElevenLabs synthesis for Sierra

Takes either inline prose or a chunked script (same `[start-end] TEXT`
format used by `tools.assembly`) and produces a `.wav` ready to feed
back into the assembly pipeline. Identity comes from the cloned voice
id stored in `~/.AI-Influencer.env`.

## Setup

1. Add to `~/.AI-Influencer.env`:

   ```
   ELEVEN_API_KEY=<your_api_key>            # from elevenlabs.io/app/settings/api-keys
   ELEVEN_SIERRA_VOICE_ID=<voice_id>         # from voice-clone-instructions.md
   ```

2. Install:

   ```bash
   .venv/bin/pip install -r tools/voice_synth/requirements.txt
   ```

## Daily use

### Inline text

```bash
python -m tools.voice_synth --text "Unpopular opinion: standards aren't asking too much." --output /tmp/vo.mp3
```

### Chunked script (drives the assembly pipeline)

```bash
python -m tools.voice_synth \
    --script personas/sierra-frost/content-units/2026-05-06_P7.script.txt \
    --output personas/sierra-frost/content-queue/2026-05-06_P7_vo.wav
```

The chunked-script flow synthesizes each `[start-end] TEXT` chunk
independently and stitches them together with precise timing so the
voiceover lines up perfectly with the burn-in subtitles produced by
`tools.assembly`.

### List the account's voices

```bash
python -m tools.voice_synth --list-voices
```

## Voice settings — defaults match `voice-profile.md §10`

| Flag | Default | Notes |
|---|---|---|
| `--model` | `eleven_multilingual_v2` | best naturalness for English |
| `--stability` | `0.55` | low for emotional posts, raise to 0.65 for monologue |
| `--similarity-boost` | `0.80` | identity preservation |
| `--style` | `0.20` | dry voice → low style transfer |

## Full pipeline (image → posted-ready TikTok)

```bash
# 1. Synthesize the voiceover
python -m tools.voice_synth \
    --script personas/sierra-frost/content-units/2026-05-06_P7.script.txt \
    --output personas/sierra-frost/content-queue/2026-05-06_P7_vo.wav

# 2. Assemble into the final mp4
python -m tools.assembly \
    --visual personas/sierra-frost/content-queue/2026-05-06_P7_kling_v1.mp4 \
    --vo personas/sierra-frost/content-queue/2026-05-06_P7_vo.wav \
    --music music/calm-piano.mp3 \
    --script personas/sierra-frost/content-units/2026-05-06_P7.script.txt \
    --output personas/sierra-frost/content-queue/2026-05-06_P7_final.mp4
```

That's the whole journey from "we have a Sierra image" to "ready to upload to TikTok," reproducible per-post.
