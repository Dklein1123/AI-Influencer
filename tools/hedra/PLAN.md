# Sierra talking-head plan (Hedra Character-3)

> Once Sierra's voice is cloned in ElevenLabs and we have a usable
> portrait of her face (P3 close-up, P15 vanity, or PROFILE all qualify),
> Hedra unlocks a format conservative-lifestyle creators are crushing
> right now: warm direct-to-camera takes with controllable speech.
> Voice + face → 30s talking-head reel.

## Why Hedra over alternatives

- **Hedra Character-3** is the current gold standard for portrait-driven
  lip-sync (better than D-ID, HeyGen, Synthesia for editorial-realism
  takes). Listed in your `COMPANY.md §8` as part of the buy stack.
- It accepts (still image + audio) → produces (talking-head video). Eyes
  blink, head shifts subtly, lip-sync respects the audio's prosody.
- No retraining needed per generation — Sierra's identity comes from the
  source portrait. We can swap portraits between settings (bedroom for
  morning takes, cafe for productive Pillar 4 takes) and use the same
  Hedra account.
- Output: 1080p (paid tier) up to ~60s, 9:16 native.

## Prerequisites (in order)

1. **Voice clone done.** See `personas/sierra-frost/voice-clone-instructions.md`.
   Until you give me an `ELEVEN_SIERRA_VOICE_ID`, no Hedra value.
2. **Hedra account.** Sign up at hedra.com. Their Creator plan is ~$10/mo
   for ~30 generations of 1080p Character-3. Higher tiers for volume.
3. **Source portrait curated.** Hedra works best with: head-and-shoulders
   framing, direct gaze (or 3/4 looking just off-camera), neutral facial
   expression, soft even lighting. From the current set:
   - **P3** (bedroom close-up, looking to camera) — A grade. Eyes engaged.
   - **P15** (vanity, lipstick mid-application) — B+ grade. Composition
     too active for talking-head; better as B-roll.
   - **PROFILE** (3/4 profile portrait) — A grade. Calm, intimate, eyes
     thoughtful. Best for monologue takes.
   - **P12** (cafe, looking up from laptop) — B grade. Composition strong
     but face partially hidden behind laptop angle.
   - Generate one new portrait specifically for Hedra: full bust crop,
     direct gaze, neutral expression, perfectly even lighting. Worth
     burning ~5 credits to get a "Hedra-ideal" still.

## Pipeline once unblocked

```
ElevenLabs voice clone (Sierra v1)
       │
       ▼
tools/voice_synth/synthesize.py  ← read content-units/*.script.txt
       │       (produces .wav)
       ▼
tools/hedra/animate.py           ← (still + .wav) → talking-head .mp4
       │       (downloads result)
       ▼
tools/assembly/                  ← burn-in subs, music bed, end-card
       │
       ▼
personas/sierra-frost/content-queue/2026-XX-XX_PXX_hedra.mp4
```

The assembly pipeline already handles the burn-in subtitle pass; Hedra's
output is just a "visual" input from `tools/assembly/`'s perspective.

## Hedra script-library — 10 starter takes (write once, generate forever)

These are pre-written 30-second monologues in Sierra's voice, designed
for talking-head Hedra animation. Lint each against `voice-profile.md`,
then generate audio from ElevenLabs once, then animate with Hedra.

### H1 — "The bar observation" (Pillar 1, A1)

> Hot take incoming and I don't care.
>
> The bar is on the floor and women are still tripping over it. Half the
> men her age can't make a reservation. The other half think replying
> to a story is communication.
>
> Standards aren't a wishlist. They're the floor.
>
> If that's controversial, that's the problem.

### H2 — "Permission slip" (Pillar 2, A5)

> Your reminder that you can just slow down.
>
> You don't owe the internet your whole nervous system. Put the phone
> away. Walk somewhere pretty. Read on a Saturday night. Take three
> hours getting ready and call it Sunday.
>
> Soft girl, sharp mind. The two are not in tension.

### H3 — "The waitress test" (Pillar 1, A3)

> Notice how nobody talks about how he treats waitresses.
>
> Not how he treats you on date three. The waitress. The Uber driver.
> The kid behind the counter at Chipotle.
>
> That's who he is. That's the data.
>
> Save this for the group chat.

### H4 — "Sunday newsletter intro" (Pillar 4)

> POV: writing Sunday's newsletter.
>
> This week — why your standards aren't actually high. They're just
> visible. There's a difference.
>
> Sundays at nine a.m. eastern. Link is in my bio.

### H5 — "Soft warning" (Pillar 1, A4)

> Three things conservative women don't say out loud, but should.
>
> One: you're allowed to want a husband. It's not a regression.
> Two: not every man is your project. Some are just messy.
> Three: choosing a slower life on purpose is not the same as settling.
>
> Pay attention.

### H6 — "Quiet judgment" (Pillar 3, A1)

> Quietly judging anyone who calls a Wednesday night drink a little
> outing.
>
> Respectfully. That's just dinner.

(short — ~15 seconds, good for a Tuesday algorithm test)

### H7 — "Done apologizing" (Pillar 1, A5)

> Three things I'm done apologizing for.
>
> Knowing what I want. Taking my time getting ready. Reading on a
> Saturday night.
>
> The audacity, I know.

### H8 — "Pro tip" (Pillar 1, A2)

> Pro tip.
>
> If he won't pay for dinner, he won't pay for anything.
>
> The data on this is unambiguous. Next.

### H9 — "Newsletter funnel direct" (Pillar 4, direct CTA)

> Sunday's newsletter is on standards.
>
> Specifically: why high standards aren't high. They're visible. There's
> a difference.
>
> Subscribe in the bio. Sundays at nine.

### H10 — "Lifestyle close" (Pillar 2, A5)

> Your reminder that the algorithm doesn't care about you.
>
> Your group chat does. Your standards do. The book on your nightstand
> does. The walk you almost didn't take does.
>
> Choose those instead.

All ten lint clean against `voice-profile.md §11`. They become the first
batch of Hedra-animated content the moment we have audio + Hedra account.

## Cost reckoning

- ElevenLabs synthesis (10 × 30s scripts): ~3,000 chars ≈ free under Starter
- Hedra Character-3 1080p (~30s each): ~$1–2 per video on Creator plan
- 10 hero talking-head reels: ~$15–20 one-time
- Replaces ~2 hours of recording + editing per piece if Sierra were
  filmed in person. Not a comparison; this only exists at all because
  she's AI.

## What I'd build when unblocked

```
tools/hedra/
├── PLAN.md           ← this file
├── __init__.py
├── __main__.py       ← CLI: python -m tools.hedra --portrait P3.png --audio H1.wav --output H1.mp4
├── client.py         ← Hedra API wrapper (auth, submit, poll, download)
└── README.md
```

Plus:

```
tools/voice_synth/
├── __init__.py
├── __main__.py       ← CLI: python -m tools.voice_synth --script H1.txt --output H1.wav
├── client.py         ← ElevenLabs API wrapper
└── README.md
```

These are ~2 hours each to build well. Both are parked behind the voice
clone — once you complete that step, they're the next 4 hours of work
and Sierra has a full talking-head studio in her bag.

## Decision still open

- **Hedra account billing.** Add ~$10/mo on top of ElevenLabs Starter $5
  + Higgsfield Ultimate. Total stack at this scale: ~$50/mo for
  generation. Trivial vs. revenue once Sierra is monetizing.
- **When to introduce Hedra format.** Recommend NOT shipping a
  talking-head Hedra video until Sierra has 7–14 days of B-roll content
  out and an audience that's seen her face animated lightly via
  Seedance/Kling. The talking-head format is more aggressive
  parasocial-wise; ease in.
