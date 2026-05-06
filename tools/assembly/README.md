# `tools.assembly` — TikTok / IG Reels final assembly

Combines a visual (image or video), an optional voiceover, an optional music
bed, and a timed script into a posted-ready 1080×1920 9:16 mp4 with
TikTok-optimized loudness and burn-in subtitles.

This is the bottom-of-funnel tool: ingredients in → posted asset out.
Replaces CapCut / Adobe Express for the standard Sierra format.

---

## Requirements

- `ffmpeg` and `ffprobe` on PATH (the repo's bootstrap script installs both)
- Roboto Black font (preinstalled on most Linux fontconfig setups, otherwise
  `apt-get install fonts-roboto`)
- Python 3.11+

No additional Python deps beyond stdlib.

---

## Quickstart

### Pure visual passthrough (no overlays, just normalize for upload)

```bash
python -m tools.assembly \
    --visual personas/sierra-frost/content-queue/2026-05-06_P7_v1.mp4 \
    --output /tmp/p7_clean.mp4
```

### Full TikTok assembly (visual + VO + music + burn-in script)

```bash
python -m tools.assembly \
    --visual personas/sierra-frost/content-queue/2026-05-06_P7_v1.mp4 \
    --vo voice/p7_take1.wav \
    --music music/calm-piano.mp3 \
    --script personas/sierra-frost/content-units/2026-05-06_P7.script.txt \
    --output personas/sierra-frost/content-queue/2026-05-06_P7_assembled.mp4
```

### Image-driven (slow ken-burns over a still + VO + script)

```bash
python -m tools.assembly \
    --visual personas/sierra-frost/content-queue/2026-05-06_P12_v1.png \
    --vo voice/p12_take1.wav \
    --script personas/sierra-frost/content-units/2026-05-06_P12.script.txt \
    --output personas/sierra-frost/content-queue/2026-05-06_P12_assembled.mp4
```

---

## Script format

The `--script` file (or `--script-text` flag) uses one chunk per line:

```
[00.0–02.0] UNPOPULAR OPINION:
[02.0–05.0] STANDARDS AREN'T
[05.0–07.0] ASKING TOO MUCH.
```

- Times are in **seconds**, decimal allowed.
- Both `-` and `–` (em-dash) work as range separators.
- A blank line ends the current chunk.
- Continuation lines (after a chunk header, before a blank line) are joined
  to the previous chunk with a line break.

These chunks become a **libass-styled .ass subtitle file** generated next
to the output mp4. ASS gives us per-chunk start/end timing, multi-line
support, and Roboto Black 96pt with thick black outline, centered, lower
third.

---

## Audio behavior

| Inputs | What happens |
|---|---|
| Just `--visual` (with audio) | Source audio preserved, normalized to -14 LUFS |
| `--vo` only | Voiceover replaces source audio |
| `--vo` + `--music` | Music bed sidechain-ducked under voiceover |
| `--vo` + `--music` + source-audio video | Source ducked to −22dB ambient, music to −12dB ducked, VO at +2.5dB |
| Just `--music` | Music at −9dB, source preserved at full |

All paths end with `loudnorm=I=-14:TP=-1:LRA=11` (TikTok's normalization
target). Final encode: H.264 medium preset CRF 20, AAC 192kbps stereo at
48kHz, 30fps, faststart enabled for instant playback on upload.

---

## Visual behavior

- **Video input:** scaled + center-cropped to 1080×1920 9:16 (preserves the
  motion, never letterboxes), forced to 30fps.
- **Image input:** scaled + cropped to 1080×1920, then a slow ken-burns
  zoom from 1.00× → 1.06× over the duration so the result reads as
  motion content, not a static frame.

---

## Subtitle styling

Defaults (mapped to `voice-profile.md §8`):

| Element | Value |
|---|---|
| Font | Roboto Black (close substitute for Anton) |
| Size | 96pt at 1080p output |
| Color | white fill |
| Outline | 8px black, +3px shadow |
| Position | centered horizontally, lower-third (30% from bottom) |
| Alignment | center |

Override font size with `--font-size`. To swap fonts entirely, install the
font system-wide via fontconfig and edit `pipeline.DEFAULT_FONT_*`.

---

## Dry run

Pass `--dry-run` to print the constructed ffmpeg command without executing
it. Useful for inspecting the filter graph or pasting the invocation into
a Makefile.

```bash
python -m tools.assembly --visual ... --output ... --dry-run
```

---

## Known limitations / TODO

- **No transitions / multi-clip support yet.** One visual per output.
  A v2 would accept a list of clips with cut points.
- **No end-card.** Want to slap "newsletter Sunday 🌴" on the last 1.5s as
  a separate frame? Use `--script-text` to put it on the final chunk for
  now; v2 will add `--end-card-text`.
- **No music auto-trim.** If your music bed is shorter than the duration,
  ffmpeg will end early on the audio side. Pad music with silence or pick
  a longer bed.
- **Single subtitle stream.** Word-for-word karaoke timing requires a
  per-word transcript (Whisper alignment); use chunked phrasing for now.
- **No automatic VO-to-script alignment.** You write the script chunks
  with the timings that match how you'd say them; the VO recorder must
  match. Future version: pass a Whisper transcript and snap chunks to it.
