# Sierra voice clone — instant setup (~10 minutes, you-only step)

> The single highest-leverage thing you can do tonight that I literally
> cannot do for you. Once Sierra has a voice, every TikTok, every reel,
> every Hedra talking-head, every newsletter audio version is unblocked.
> 10 minutes of recording = weeks of voiceovers.

## Pick the voice path

ElevenLabs has three options. We want **Instant Voice Clone (IVC)**.

| Option | Time | Quality | Cost | When to use |
|---|---|---|---|---|
| Voice Library (premade) | 0 min | Good | Free tier | Drafts only |
| **Instant Voice Clone** | **10 min** | **Very good** | **Included in Starter $5/mo** | **Sierra v1 — start here** |
| Professional Voice Clone | 1–4 hours of audio + 7-day train | Best | Creator $22/mo | Sierra v2, in 30 days, after this voice has proven |

**Decision: IVC tonight. Upgrade to Professional once Sierra has 30+ days of posting and a confirmed voice character.**

## What the cloned voice should sound like

From `voice-profile.md §10`:

- **Warm alto, mid-register**, light slightly-Florida warmth (no country twang)
- Speed 0.95–1.0× — deliberate, never rushed
- Slight **downward inflection on landings** — confidence, not uptalk
- Dry, observational tone — not bubbly, not preachy
- 24-year-old read, but with read-books-and-knows-things energy

Closest celebrity voice references for the recording vibe (don't try to imitate, just channel the energy): Brittany Broski's stillness, Alex Cooper without the volume, Reese Witherspoon's *Big Little Lies* deposition scenes. **Confident woman who doesn't need to raise her voice.**

## Step 1 — Pick the speaker

You have two real choices for *whose voice* gets cloned:

### Option A — Your own voice (or your partner's), once
**Recommended.** Quick, free of legal/consent issues, you control re-recording forever. The voice doesn't need to match Sierra's persona's gender of the recorder — ElevenLabs IVC clones the timbre, not the identity. **A clear, well-recorded female alto in any room is fine.** If neither of you have a voice that fits, go to Option B.

### Option B — Hire a voice actor on Fiverr/Voices.com (~$50–150)
Brief: *"I need a 5-minute voice sample for an internal AI brand. Female, age 25–35, warm alto, dry observational delivery (think Reese Witherspoon depositions), no country accent, US-neutral. You retain no rights — please confirm a buyout license."* Pick someone whose demo sounds like the persona. Have them record the script below.

### Option C — License an existing actress voice
**Skip this.** Right-of-publicity exposure is real, and ElevenLabs will refuse to clone a recognizable voice. Don't.

## Step 2 — Record the source audio (~3 minutes of speech)

ElevenLabs IVC needs **at least 1 minute, ideally 3–5 minutes** of clean audio. More than 10 minutes hurts (over-fits to specific cadence).

### Recording specs (non-negotiable)

- **Quiet room.** No HVAC, no traffic outside, no other people.
- **Phone at arm's length** (10–14 inches from mouth) is fine. Built-in
  Voice Memos (iPhone) or Voice Recorder (Android) works.
- **Single take per script** — don't stitch.
- **Save as .m4a or .wav.** No MP3 if avoidable.
- **No music**, no background noise, no second voice.
- **Monotone reading is bad.** Read like you're explaining something
  interesting to a friend over coffee. Sierra's voice has shape.

### Read this aloud (the source script)

Read it once through to warm up, then record take 2 or 3. Aim for ~3 minutes total elapsed when you read it deliberately. **Don't rush.**

---

> Hot take incoming and I don't care.
>
> Half the men her age don't know how to make a reservation. The other half think communication is replying to her story. Standards aren't asking too much — they're the floor.
>
> Let me explain this slowly. Notice how nobody talks about how he treats waitresses. Not how he treats you on date three. The waitress. The Uber driver. The kid behind the counter. That's who he is.
>
> Pro tip: if he won't pay for dinner, he won't pay for anything.
>
> Your reminder that you can just slow down. You don't owe the internet your whole nervous system. Put the phone away. Walk somewhere pretty. Notice the palms move before you check the comments.
>
> Three things I'm done apologizing for: knowing what I want, taking my time getting ready, and reading on a Saturday night. The bar is on the floor and she's still tripping.
>
> Unpopular opinion: standards aren't a wishlist. Common sense isn't common. Soft girl, sharp mind. Make it make sense.
>
> Quietly judging anyone who calls a Wednesday night drink "a little outing." Respectfully — that's just dinner.
>
> Newsletter Sundays at nine a.m. eastern. Link in bio. Save this for the group chat.

---

## Step 3 — Upload to ElevenLabs

1. Sign up at https://elevenlabs.io if you haven't (Starter plan $5/mo or use the free 10-minute trial).
2. **Voices** → **Add Voice** → **Instant Voice Clone**.
3. Name: `Sierra Frost v1`.
4. Drop in the .m4a/.wav file (or all 2–3 takes if you recorded multiples).
5. Description (paste verbatim — it tunes the embedding):

   > Warm alto in mid-register, US-neutral. Dry observational delivery, deliberate pacing, slight downward inflection on landings, confident without raising voice. 24-year-old conservative-lifestyle commentator energy.

6. Labels (suggested): `accent: american`, `age: young`, `gender: female`, `use case: social-media`.
7. Click **Add Voice**. Takes ~30 seconds.

## Step 4 — Get the voice ID + first test

1. Click into the new voice. URL will be `https://elevenlabs.io/app/voice-lab/<voice_id>`.
2. **Copy the voice_id.** Send it to me — I'll add it to `~/.AI-Influencer.env` as `ELEVEN_SIERRA_VOICE_ID=...`.
3. In ElevenLabs's Speech tab, paste this test text:

   > "Hot take incoming and I don't care. Standards aren't asking too much. They're the floor."

   Settings (per `voice-profile.md §10`):
   - Stability: **0.55**
   - Similarity Boost: **0.80**
   - Style Exaggeration: **0.20**
   - Speaker Boost: **on**
   - Model: **eleven_multilingual_v2** (or `eleven_turbo_v2_5` for cheaper batch jobs)

4. Generate. **Listen.** Does it sound like the woman in §1 of the voice profile? If yes, ship it. If no, see troubleshooting below.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Sounds robotic / uneven | Stability ↑ to 0.65, Style ↓ to 0.15 |
| Sounds drifty / unstable | Stability ↑ to 0.70 |
| Sounds flat / no shape | Stability ↓ to 0.45, Style ↑ to 0.30 |
| Wrong accent (slight British, weird vowels) | Re-record source — was probably <2 min, IVC needs more |
| Sounds different from take to take | Normal at low stability; lock stability ≥0.55 for finals |

## Step 5 — Send me the voice_id

Reply with:
- The `voice_id` (UUID-shaped string from the URL)
- A short ElevenLabs-generated test mp3 if you can drop a link

I will:
1. Add `ELEVEN_SIERRA_VOICE_ID=<id>` to `~/.AI-Influencer.env`
2. Build `tools/voice_synth/` — a Python wrapper that takes a script
   from `content-units/*.script.txt` and produces a `.wav` file ready
   for the assembly pipeline
3. Generate the first **real** voiceover for the **P7 Sunday post**
4. Run it through `tools/assembly/` → finished posted-ready TikTok
5. Move on to Hedra wiring (talking-head, lip-sync to your voice)

## Cost reckoning

- ElevenLabs Starter $5/mo = 30,000 characters of generation = roughly
  500 minutes of voiceover. We won't come close in month one.
- Upgrade to Creator $22/mo only when we cross 100,000 characters/month
  or when we move to Professional Voice Clone for v2.
- Sierra's monthly voice usage at 4 TikToks/week × 15s × 30 days ≈
  ~3,500 characters. Trivial.

## When to retrain (v2)

Train a Professional Voice Clone (~30–60 min of clean audio) when:
- Sierra has 30+ days of posts and the voice has settled
- You want to own a higher-quality master version for premium content
- You're tired of small inconsistencies between IVC generations

The current IVC stays as a fallback for fast turnaround.
