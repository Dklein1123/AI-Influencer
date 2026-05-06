# Sierra Frost — Higgsfield Prompt Library

> Companion to `persona.md` and `viral-playbook.md`. The bible defines who she
> is; the playbook defines what she posts; this doc defines exactly how to
> generate the visual content for those posts in Higgsfield. Pull this up
> before any generation session.

**Goal:** batch-generate 2 weeks of content (28+ posts of visual content) in a
single 2–3 hour generation session. Consistency, lane-fit, and lead time are
the priorities.

---

## 1. The character lock — most important section

The single biggest failure mode for AI personas is **identity drift** — she
looks like a slightly different girl across posts, the audience subconsciously
notices, follows don't compound. We solve this in three layers:

### Layer 1 — Soul ID / Character (Higgsfield's consistency tool)
Use Higgsfield's character/Soul ID feature to lock Sierra's face. Train it on
6–10 of the cleanest existing reference images (front, ¾ left, ¾ right,
profile, smiling, neutral). **This is the foundation — don't generate without
it.** Save the trained character with the name `sierra-frost-v1`. If the look
ever drifts, retrain v2 — never silently change v1.

### Layer 2 — The Sierra base block (paste into every prompt)
Every prompt starts with this exact block. Don't paraphrase, don't shorten —
identical text every time:

```
{{sierra-frost-v1}}, 24-year-old woman, blonde mid-length hair with soft
beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips
with glossy nude makeup, polished natural makeup with soft contour and warm
neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body,
warm friendly expression unless otherwise specified
```

### Layer 3 — Seed lock when possible
If Higgsfield exposes a seed parameter, use the same seed for content within
the same shoot/scene to keep micro-features consistent (jewelry placement,
hair part, etc.). Document working seeds in `seeds.md` as we find them.

---

## 2. The negative prompt (paste into every generation)

Forbidden visual elements. Paste this in the negative prompt field every
single time:

```
deformed hands, extra fingers, distorted face, asymmetric eyes, plastic skin,
overly smoothed skin, uncanny valley, harsh studio lighting, neon colors,
heavy contour, drag-style makeup, dark lipstick, gothic aesthetic, alt
fashion, streetwear logos, Y2K aesthetic, club wear, lingerie, bikini,
nudity, named celebrities, named politicians, recognizable government
interiors, identifiable real people, MAGA hat with legible text, political
signage with legible text, election year graphics, partisan iconography,
weapons, drugs, alcohol bottles in foreground, watermarks, text overlays,
low resolution, blurry, oversaturated
```

---

## 3. Universal style suffix (paste at the END of every prompt)

After the scene-specific content, every prompt ends with this:

```
shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft
natural lighting, golden hour or warm window light, neutral color palette,
candid editorial composition, cinematic but warm, polished but not stiff,
high detail, ultra realistic photographic quality, 9:16 vertical aspect
ratio
```

For static IG carousels, swap `9:16 vertical` → `4:5 portrait`.
For wide hero shots, swap → `16:9 horizontal`.

---

## 4. Camera motion vocabulary (Higgsfield's specialty — use it)

Higgsfield's edge over competitors is cinematic camera motion. Generic
prompts get generic results. Use this vocabulary:

| Motion | When to use | Sample phrase |
|---|---|---|
| **Slow push-in** | Reveal moments, intimate confessionals | "slow dolly push toward subject's face, ending on tight close-up" |
| **Slow pull-out** | Establishing scenes, lifestyle reveal | "slow dolly pull back from medium shot to wide environmental reveal" |
| **Handheld follow** | Lifestyle / day-in-the-life | "loose handheld follow, subject walking forward, slight natural sway" |
| **Static lock-off** | Talking head, list-format videos | "locked-off tripod, no camera movement, subject framed center" |
| **Orbit / arc** | Hero showcase shots | "smooth 90-degree arc around subject, golden hour rim light" |
| **Whip pan** | Transitions between B-roll | "whip pan motion blur transition into next scene" |
| **Tilt up / down** | Dramatic reveals | "tilt up from feet to face, full body reveal" |
| **POV** | "POV: you're..." structure | "first-person POV, handheld, gentle natural movement" |

**Rule:** every video prompt explicitly names a camera motion. "Static" is a
choice, not a default — naming it is part of the prompt.

---

## 5. Wardrobe blocks (reusable)

Drop the relevant block into the prompt body. Don't reinvent wardrobe each
time — these match the persona-bible spec and stay on-brand.

### A. Tailored Polish
```
wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe
heels, dainty gold necklace, small camel structured handbag, hair styled in
soft waves
```
Variation: forest green fitted dress with thin tan leather belt. Variation:
camel midi dress, ivory cardigan over shoulders.

### B. Florida Casual
```
wearing white linen sundress with thin straps, beige espadrille sandals,
gold layered necklaces, hair air-dried in soft beachy waves, no jacket
```
Variation: pale pink slip dress + denim jacket + sneakers. Variation: white
button-down knotted at waist + tan linen shorts.

### C. Athleisure
```
wearing matching neutral set: cream sports bra and high-waisted bike shorts,
Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face,
small gold hoops
```
Variation: dusty pink bodysuit + black bike shorts + sneakers. Variation:
sage green seamless leggings + sports bra + cropped quarter-zip.

### D. Faith / Sunday
```
wearing modest knee-length dress in soft cream or dusty pink, fitted but not
tight, three-quarter sleeves, simple dainty cross necklace, neutral nude
heels, soft natural makeup, hair half-up
```
Variation: navy A-line midi dress + camel cardigan. Variation: forest green
fitted dress with belt + nude pumps.

### E. Evening
```
wearing fitted satin slip dress in deep navy, classic stiletto heels, gold
statement earrings, sleek straight hair or soft glam waves, polished evening
makeup with subtle smokey eye
```
Variation: classic red bodycon midi + nude heels. Variation: black tailored
jumpsuit with gold belt.

---

## 6. Setting blocks (reusable)

### S1. Sunlit Scandi-Neutral Bedroom
```
in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand,
floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot,
soft morning light streaming through window, neutral palette of cream
beige and warm wood
```

### S2. South Florida Exterior
```
on a Palm Beach waterfront walkway, palm trees in background, white
classical-style architecture, calm turquoise water visible behind, golden
hour light, pastel sky, polished resort aesthetic, no other recognizable
people in frame
```

### S3. Classical American Architecture (NO real people, NO interior)
```
on the steps outside a marble-columned classical building, Corinthian
columns visible behind, American flag faintly visible in distant background
(no legible text), bright clear blue sky, dramatic shadow lines on stone,
no other identifiable people in frame, exterior only
```
**Reminder:** never generate her INSIDE the White House or Capitol. Exterior
only. Never with named figures. Never with rally signage.

### S4. Boutique Pilates Studio / Gym
```
inside a bright minimalist Pilates studio, reformer machine visible, large
windows with morning light, warm wood floor, white walls with subtle
ribbed-wood detail, neutral palette, polished wellness aesthetic
```

### S5. Coffee Shop / Newsletter Workspace
```
at a small marble cafe table near a window, MacBook open with a clean
writing app on screen (no legible text), latte in ceramic cup, leather
journal beside laptop, soft window light, blurred warm interior in
background, intimate productive atmosphere
```

---

## 7. Shot-type vocabulary

| Type | Description | When to use |
|---|---|---|
| **Tight close-up** | Face fills frame, eyes dominant | Cold-open commentary, reveal moments |
| **Medium close-up** | Head + shoulders | Standard talking head |
| **Medium shot** | Waist up | Reaction stitches, lifestyle commentary |
| **Cowboy / 3-quarter** | Mid-thigh up | Wardrobe showcase, GRWM |
| **Full body** | Head to toe | Outfit reveal, "fit check," establishing |
| **Wide / environmental** | Subject small, context dominant | Lifestyle reveal, opening shot, "POV" |
| **Detail / insert** | Hands, jewelry, journal, latte | B-roll cutaways |
| **Over-the-shoulder** | Past her shoulder into laptop/journal | Newsletter writing content |

---

## 8. The 50-prompt template library

Plug-and-play prompts. Each combines [base block] + [scene] + [motion] +
[style suffix] + [negative prompt]. The shorthand below shows the unique
content; assemble with the universals from §1–§3 and §4.

### Block 1 — Talking head / commentary B-roll (15 templates)

These are companion shots for Pillars 1 + 3 (commentary, reaction). The
talking-head audio is recorded separately or generated via Hedra/HeyGen with
Sierra's image; these prompts produce the visual environment + lifestyle
context shots that get cut between her speaking.

```
P1.  [Bedroom S1] + medium close-up + static lock-off + Tailored Polish A
     (sitting at edge of bed, soft confident expression, looking off-camera)

P2.  [Coffee shop S5] + medium shot + slow push-in + Florida Casual B
     (typing on laptop, looking up at camera mid-thought, half-smile)

P3.  [Bedroom S1] + tight close-up + slow push-in + neutral
     (looking directly to camera, dry knowing expression — for Cold Open
     and "I said what I said" structures)

P4.  [Coffee shop S5] + over-the-shoulder + static + Tailored Polish A
     (writing in leather journal, latte beside her, contemplative)

P5.  [Bedroom S1] + wide environmental + slow pull-out + Faith/Sunday D
     (sitting cross-legged on bed with open journal, morning light, serene)

P6.  [Pilates studio S4] + medium close-up + static + Athleisure C
     (post-workout, slight glow, water bottle in hand, casual confident)

P7.  [Florida exterior S2] + cowboy shot + handheld follow + Florida Casual B
     (walking toward camera, hair moving in breeze, soft smile, golden hour)

P8.  [Bedroom S1] + tight close-up + slow push-in + Tailored Polish A
     (pearl-strand earring detail, soft side-lit, neutral expression — for
     "Confession" structure intros)

P9.  [Coffee shop S5] + detail insert + static + (no wardrobe focus)
     (hands typing on laptop, gold ring + dainty bracelet visible, journal
     beside — pure B-roll cutaway)

P10. [Bedroom S1] + medium shot + slow orbit + Athleisure C
     (sitting on edge of bed lacing sneakers, morning routine vibe)

P11. [Florida exterior S2] + wide environmental + static + Florida Casual B
     (small in frame, palm trees dominant, walking away from camera, candid)

P12. [Coffee shop S5] + medium close-up + slow push-in + Tailored Polish A
     (looking up from laptop directly to camera, faint smile, "caught you
     watching" energy)

P13. [Bedroom S1] + over-the-shoulder + static + Faith/Sunday D
     (open Bible or devotional book on lap — generic book, no legible text,
     soft window light)

P14. [Pilates studio S4] + full body + slow pull-out + Athleisure C
     (mid-Pilates form on reformer, controlled and graceful, not strained)

P15. [Bedroom S1] + tight close-up + static + Evening E
     (getting ready at vanity, lipstick mid-application, mirror reflection
     visible)
```

### Block 2 — Lifestyle / Pillar 2 (15 templates)

Standalone lifestyle content — full posts, not B-roll. Each tells a tiny
story.

```
P16. [Florida exterior S2] + cowboy shot + slow orbit + Florida Casual B
     (Worth Avenue boutique window in soft background, polished day-out)

P17. [Coffee shop S5] + medium shot + handheld follow + Tailored Polish A
     (entering cafe with leather tote, sunglasses pushed up on head)

P18. [Bedroom S1] + medium close-up + slow push-in + Faith/Sunday D
     (Sunday morning getting ready, cross necklace detail, soft golden light)

P19. [Pilates studio S4] + cowboy shot + static + Athleisure C
     (stretching at barre, post-class, tied-up hair, dewy skin)

P20. [Florida exterior S2] + full body + handheld follow + Florida Casual B
     (walking past palms with iced coffee in hand, candid Florida day)

P21. [Bedroom S1] + detail insert + static + (any outfit)
     (closet detail: rows of neutral dresses, gold jewelry tray, organized
     polished)

P22. [Coffee shop S5] + medium shot + slow push-in + Tailored Polish A
     (writing in journal at sidewalk cafe table, golden hour, palm shadow)

P23. [Bedroom S1] + medium close-up + slow push-in + Athleisure C
     (morning routine: hair up in claw clip, applying serum, no makeup)

P24. [Florida exterior S2] + wide environmental + slow pull-out + Evening E
     (golden hour at marina with white yachts behind, classy evening)

P25. [Bedroom S1] + cowboy shot + slow orbit + Tailored Polish A
     (mirror outfit check, full polish, confident, "fit check" energy)

P26. [Coffee shop S5] + over-the-shoulder + static + Tailored Polish A
     (laptop screen shows Sunday newsletter draft — no legible text —
     intentional newsletter-funnel content)

P27. [Pilates studio S4] + medium shot + slow push-in + Athleisure C
     (drinking from glass water bottle, content post-workout)

P28. [Florida exterior S2] + cowboy shot + handheld follow + Faith/Sunday D
     (walking up church steps in modest dress, hand on Bible/journal)

P29. [Bedroom S1] + full body + slow pull-out + Evening E
     (getting ready for evening event, full mirror, polished glam)

P30. [Coffee shop S5] + medium close-up + slow push-in + Florida Casual B
     (laughing softly at something off-camera, latte in hand, natural)
```

### Block 3 — Reaction / "Looking at camera" content (10 templates)

For reaction stitches and POV structures. These shots emphasize the *look* —
the dry, knowing, eyebrow-raised expression that does the work.

```
P31. [Bedroom S1] + tight close-up + static + neutral wardrobe
     (eyebrow raise, slight head tilt, "you're kidding right" expression)

P32. [Bedroom S1] + medium close-up + slow push-in + Athleisure C
     (sitting on bed mid-coffee sip, pause, dry sideways glance to camera)

P33. [Coffee shop S5] + medium close-up + static + Tailored Polish A
     (mid-typing, looks up over laptop, dry "really?" expression)

P34. [Bedroom S1] + tight close-up + static + Faith/Sunday D
     ("forgive them, they know not what they do" expression — soft eye-roll)

P35. [Florida exterior S2] + medium close-up + slight zoom + Florida Casual B
     (sunglasses lowered to look at camera over them, knowing smile)

P36. [Bedroom S1] + medium shot + slow push-in + neutral
     (slow head shake, slight smirk, arms crossed, "we're not doing this")

P37. [Coffee shop S5] + tight close-up + static + Tailored Polish A
     (chin in hand at table, deadpan straight-to-camera, "go on")

P38. [Bedroom S1] + medium close-up + slow push-in + Athleisure C
     (mid-laugh that turns into "wait, you're serious?" expression)

P39. [Florida exterior S2] + medium shot + handheld + Florida Casual B
     (walking toward camera, small smirk, "let me explain" energy)

P40. [Bedroom S1] + tight close-up + slow push-in + Evening E
     (slow blink, deadpan, "the audacity" energy)
```

### Block 4 — Newsletter funnel / Pillar 4 (5 templates)

```
P41. [Coffee shop S5] + over-the-shoulder + slow push-in + Tailored Polish A
     (writing newsletter, Sunday morning energy, "POV: I'm writing this
     week's letter" framing)

P42. [Bedroom S1] + medium shot + static + Faith/Sunday D
     (laptop in lap, leather journal beside, "Sunday newsletter day"
     atmosphere)

P43. [Coffee shop S5] + detail insert + static
     (laptop screen showing clean writing-app interface, no legible text,
     morning latte beside)

P44. [Bedroom S1] + medium close-up + slow push-in + Athleisure C
     (cozy "writing in bed" energy, pen and journal, soft natural)

P45. [Coffee shop S5] + medium shot + slow pull-out + Tailored Polish A
     (full sidewalk-cafe scene, MacBook + journal + latte, golden hour, the
     "writer girl" archetype shot)
```

### Block 5 — Hero shots (5 templates)

Reusable across pillars. These are the "wow" shots — for IG hero post,
linktr.ee thumbnail, profile pic refresh, brand-deal pitch deck.

```
P46. [Florida exterior S2] + medium close-up + slow orbit + Tailored Polish A
     (golden hour, palm shadow on white wall behind, polished editorial)

P47. [Bedroom S1] + medium shot + static + Tailored Polish A
     (current existing hero shot vibe — sitting at edge of bed, full polish,
     soft window light — match the locked aesthetic)

P48. [Classical architecture S3] + cowboy shot + slow pull-out
     + Tailored Polish A (steps of marble building, exterior only, no
     interior, golden afternoon, polished editorial)

P49. [Florida exterior S2] + full body + slow orbit + Evening E
     (sunset marina, classic red or navy evening dress, hero shot)

P50. [Bedroom S1] + medium close-up + static + Faith/Sunday D
     (Sunday morning hero — soft pastel light, dainty cross, thoughtful but
     warm expression — for faith content)
```

---

## 9. Batch generation workflow

### Pre-session prep (15 min)
1. Pull next 14 days of posts from `viral-playbook.md` → assign each a
   prompt template number (P1–P50)
2. Identify which need video (TikTok/Reels) vs. static (IG carousel)
3. Note any custom variants needed (specific take requires specific outfit?)
4. Open `seeds.md` for proven seeds

### Generation session (2 hours)
1. **Generate in batches of 4** per prompt — keep best 1, archive others
2. **Quality gate** each generation against the checklist (§10) before
   accepting
3. **Name files consistently:** `YYYY-MM-DD_pillar1_P03_v2.mp4`
4. **Log to `generation-log.md`:** prompt template, seed, what worked, what
   didn't

### Post-session organization
1. Selected clips → `content-queue/` ordered by intended post date
2. B-roll → `content-queue/b-roll/` for talking-head cutaways
3. Backup originals → cloud (don't lose seeds + raw files)

### Cadence
**Once every 14 days**, batch-generate the next 28 posts. This is one of the
two recurring time investments (the other is daily posting + comment reply).

---

## 10. Quality gate checklist

Reject the generation if any of these fail. It's faster to regenerate than
to ship mid-quality content.

### Identity (most important)
- [ ] Looks like Sierra v1, not "a girl who looks like Sierra"
- [ ] Eye color matches (light blue/green, not brown/dark)
- [ ] Hair color matches (warm blonde with soft waves, not platinum or
      darker)
- [ ] Face shape matches reference (no AI drift toward generic prettiness)
- [ ] Skin tone matches (lightly tanned, glowy, not pale or over-tanned)

### Hands & body
- [ ] Hands have 5 fingers, normal proportions, no extras
- [ ] No distorted limbs, melted body parts, weird joints
- [ ] Body proportions consistent across shots in same scene

### Brand-fit
- [ ] Wardrobe matches the locked palette (no neon, no streetwear, no Y2K)
- [ ] Setting is on-brand (not nightclub, not gritty, not edgy)
- [ ] Expression matches the post's intent (dry for commentary, warm for
      lifestyle, contemplative for newsletter)

### Hard fails (instant reject)
- [ ] No legible text in scene that wasn't intended
- [ ] No identifiable real people in background
- [ ] No partisan signage / political iconography
- [ ] No nudity or sexual content
- [ ] No watermarks or artifacts

---

## 11. Talking-head video — what Higgsfield is and isn't for

**Higgsfield is best at:** cinematic visual content, lifestyle scenes,
B-roll, mood pieces, hero shots, motion-driven sequences.

**Higgsfield is NOT optimized for:** lip-synced talking head where Sierra
"says" specific commentary on camera with synced audio.

**Recommended stack:**
- **Higgsfield:** all visual content per templates above
- **Hedra Character-3 or HeyGen:** lip-sync Sierra's image to a recorded or
  AI voiceover when she needs to actually "speak" on camera
- **CapCut or Descript:** post-production assembly — combine her talking
  head + Higgsfield B-roll + captions

For commentary posts (Pillars 1 + 3), the typical stack is:
1. Write the take (from playbook backlog)
2. Record voiceover (your real voice, or 11Labs / generated voice — pick one
   voice and stick with it forever, voice consistency matters as much as
   face consistency)
3. Hedra/HeyGen produces talking-head with synced audio
4. Higgsfield prompts P1–P15 produce environmental B-roll
5. CapCut assembles with cuts every 2–4s, captions, music

---

## 12. Voice consistency

If using AI voice for Sierra, lock the voice in 11Labs (or equivalent) the
same way we locked her face. Save as `sierra-voice-v1`. The voice should
match her persona:

- **Pitch:** mid-range, slightly lower than typical "girly" range
- **Pace:** confident, slightly slower than baseline (gives weight to takes)
- **Tone:** dry, knowing, occasional smirk in the delivery
- **Accent:** neutral American, very slight South Florida polish (not
  Southern drawl)

**Reference voices to model after:** Brett Cooper, Allie Beth Stuckey at her
sharper moments, Tomi Lahren on her dry days. Avoid: anything bubbly,
podcast-vocal-fry-heavy, or overly bright.

---

## 13. Files to maintain alongside this doc

| File | Purpose |
|---|---|
| `seeds.md` | Working seeds that produced great results, by template number |
| `generation-log.md` | Every batch session: what prompts hit, what flopped |
| `prompt-variants.md` | Variants we've discovered that beat the originals |
| `content-queue/` | Generated assets ordered by intended post date |
| `archive/` | Rejected generations (keep for retraining / debugging drift) |

---

## 14. Versioning

This doc evolves with what generates well. Update wardrobe blocks, settings,
or templates as we learn. Retrain Sierra v1 → v2 only if absolutely
necessary; document the diff if so.

**v0.1** — initial library. 50 templates. 5 wardrobe blocks. 5 settings. 8
camera motions. Soul ID strategy locked. Stack note: Higgsfield + Hedra +
11Labs + CapCut.
