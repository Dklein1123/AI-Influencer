-- Sierra Frost seed migration (generated 2026-05-06)
-- Source: tools/sync/build_seed_sql.py
-- Run via: paste into Lovable as a new migration file

BEGIN;

-- ===============================
-- -- Allowlist + tightened RLS --
-- ===============================

CREATE TABLE IF NOT EXISTS allowed_emails (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE allowed_emails ENABLE ROW LEVEL SECURITY;

INSERT INTO allowed_emails (email) VALUES
  ('danielsklein1123@gmail.com'),
  ('rdepo27@gmail.com')
ON CONFLICT (email) DO NOTHING;

DROP POLICY IF EXISTS "allowlisted access on allowed_emails" ON allowed_emails;
CREATE POLICY "allowlisted access on allowed_emails"
  ON allowed_emails FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- profiles: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read profiles" ON profiles;
DROP POLICY IF EXISTS "auth insert profiles" ON profiles;
DROP POLICY IF EXISTS "auth update profiles" ON profiles;
DROP POLICY IF EXISTS "auth delete profiles" ON profiles;
CREATE POLICY "allowlisted access on profiles" ON profiles FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- influencers: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read influencers" ON influencers;
DROP POLICY IF EXISTS "auth insert influencers" ON influencers;
DROP POLICY IF EXISTS "auth update influencers" ON influencers;
DROP POLICY IF EXISTS "auth delete influencers" ON influencers;
CREATE POLICY "allowlisted access on influencers" ON influencers FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- brand_bible: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read brand_bible" ON brand_bible;
DROP POLICY IF EXISTS "auth insert brand_bible" ON brand_bible;
DROP POLICY IF EXISTS "auth update brand_bible" ON brand_bible;
DROP POLICY IF EXISTS "auth delete brand_bible" ON brand_bible;
CREATE POLICY "allowlisted access on brand_bible" ON brand_bible FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- campaigns: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read campaigns" ON campaigns;
DROP POLICY IF EXISTS "auth insert campaigns" ON campaigns;
DROP POLICY IF EXISTS "auth update campaigns" ON campaigns;
DROP POLICY IF EXISTS "auth delete campaigns" ON campaigns;
CREATE POLICY "allowlisted access on campaigns" ON campaigns FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- content_items: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read content_items" ON content_items;
DROP POLICY IF EXISTS "auth insert content_items" ON content_items;
DROP POLICY IF EXISTS "auth update content_items" ON content_items;
DROP POLICY IF EXISTS "auth delete content_items" ON content_items;
CREATE POLICY "allowlisted access on content_items" ON content_items FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- prompts: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read prompts" ON prompts;
DROP POLICY IF EXISTS "auth insert prompts" ON prompts;
DROP POLICY IF EXISTS "auth update prompts" ON prompts;
DROP POLICY IF EXISTS "auth delete prompts" ON prompts;
CREATE POLICY "allowlisted access on prompts" ON prompts FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- assets: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read assets" ON assets;
DROP POLICY IF EXISTS "auth insert assets" ON assets;
DROP POLICY IF EXISTS "auth update assets" ON assets;
DROP POLICY IF EXISTS "auth delete assets" ON assets;
CREATE POLICY "allowlisted access on assets" ON assets FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- tasks: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read tasks" ON tasks;
DROP POLICY IF EXISTS "auth insert tasks" ON tasks;
DROP POLICY IF EXISTS "auth update tasks" ON tasks;
DROP POLICY IF EXISTS "auth delete tasks" ON tasks;
CREATE POLICY "allowlisted access on tasks" ON tasks FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));

-- ai_outputs: replace permissive policies with allowlist check
DROP POLICY IF EXISTS "auth read ai_outputs" ON ai_outputs;
DROP POLICY IF EXISTS "auth insert ai_outputs" ON ai_outputs;
DROP POLICY IF EXISTS "auth update ai_outputs" ON ai_outputs;
DROP POLICY IF EXISTS "auth delete ai_outputs" ON ai_outputs;
CREATE POLICY "allowlisted access on ai_outputs" ON ai_outputs FOR ALL TO authenticated
  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))
  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));


-- ===========================================================================
-- -- Wipe bogus Sierra seed (Lovable's hallucinated 'alpine digital muse') --
-- ===========================================================================

DELETE FROM ai_outputs WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM tasks WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM assets WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM prompts WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM content_items WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM campaigns WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM brand_bible WHERE influencer_id = '11111111-1111-1111-1111-111111111111';
DELETE FROM influencers WHERE id = '11111111-1111-1111-1111-111111111111';

-- ========================================
-- -- Real Sierra Frost — influencer row --
-- ========================================

INSERT INTO influencers (
  id, name, handle, avatar_url, bio, personality, niche, tone,
  content_pillars, visual_style, audience, internal_notes, status
) VALUES (
  'a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01',
  'Sierra Frost',
  '@sierrafrost.xo',
  NULL,
  'Sharp blonde from South Florida — Tomi Lahren / Brett Cooper coded. Common-sense commentary on culture, dating, fitness, and faith. Disclosed as a digital persona / AI-assisted; doesn''t lead with disclosure but doesn''t pretend to be human if asked. Sharp-tongued, polished, pointed, patriotic. Florida-raised, paying attention so you don''t have to.',
  'Sharp older-sister voice. Confident not cute, dry not LOL, observational not preachy. Knows she''s the hot blonde with takes — leans in. Florida warmth, soft conservative, never punching down at women. Sees the discourse and tells you what''s actually going on while she pours wine.',
  'Conservative lifestyle / soft conservative commentary (Lane A — no policy wonk, no named-candidate endorsements)',
  'Confident, dry-witty, observational, deliberate pacing, slight downward inflection on landings, soft Florida warmth, US-neutral.',
  '{"Pillar 1 — Commentary / Hot Takes (40%)","Pillar 2 — Lifestyle / Soft Conservative (30%)","Pillar 3 — Reaction / Make It Make Sense (20%)","Pillar 4 — Newsletter Funnel / BTS (10%)"}',
  'Cinematic editorial. Sony A7IV, 50mm prime, f/2.0, soft natural lighting, golden hour or warm window light, neutral cream/beige palette, polished but candid. Wardrobe rotates A (tailored polish navy+cream), B (Florida casual white linen), C (cream Pilates), D (faith / Sunday modest), E (evening). Settings rotate S1 Scandi bedroom / S2 Palm Beach / S3 Classical exterior / S4 Pilates studio / S5 cafe-newsletter.',
  'Conservative women 22–45, US. Faith-curious, fitness-focused, dating-aware. Florida + Texas + Tennessee skews high. Buying audience for: conservative-niche affiliates, modest fashion, supplements, devotional products, faith adjacent.',
  'Higgsfield Soul ID: 87b6278b-8407-479d-b127-a8f2bc064ed1 (sierra-frost-v1, soul_2). Replicate LoRA v1: dklein1123/sierra-frost-v1:3225c5c843f49636dbd738c9a029e7f0058f7033145f15927ffe5443f9f82517 (mixed-mode — LoRA for full-body+frontal, Soul 2 for close-ups+profile, see tools/lora/v1-decision.md). ElevenLabs voice: TBD. Hedra: TBD.',
  'active'
)
ON CONFLICT (id) DO NOTHING;

-- =========================================
-- -- Real Sierra Frost — brand_bible row --
-- =========================================

INSERT INTO brand_bible (
  influencer_id, personality_rules, caption_style, visual_rules,
  posing_rules, negative_prompts, example_prompts, content_boundaries,
  tone_guidelines, would_say, would_never_say
) VALUES (
  'a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01',
  '> **The smart older sister who watched the discourse all week, lifts, has standards, and is now telling you what''s actually going on — calmly enough to be funny.**

If a sentence wouldn''t be said by that woman in that mood, it''s wrong.

- **Sentence length distribution:** mostly short (5–10 words). Mix in one
  longer (15–22 words). Then back to short. Land the take on a short.
- **Paragraph length:** 1–2 sentences each. Whitespace is breathing room.
- **Em-dash usage:** sparing — only for redirection.
- **Lists:** rarely numbered; almost never use bullet points in captions.
- **Caps:** never ALL-CAPS for emphasis. Italics or sentence-case bold only.
- **Punctuation rhythm:** short. punchy. then a longer one. then short.
- **Sound design:** alliteration is fine. Rhyme is gimmicky and out.
- **Rhetorical questions:** yes, used as set-ups. Never as fishing.
- **Profanity:** PG-13 ceiling. "Hell" yes. "Shit" rare. "Damn" yes. F-bomb no.',
  '### TikTok caption (1–3 short lines, max ~150 chars)

**Formula:** `<echo of hook> + <on-pillar tag> + <CTA optional>`

Examples:
- *"Notice how nobody talks about this. 🌴 #realtalk"*
- *"The bar is on the floor and she''s still tripping. Newsletter Sunday."*
- *"Three things I''m done apologizing for. Save this."*

Hashtags: 2–4 max. Always include 1 niche tag (#conservativewomen, #softgirl,
#realtalk) + 1 broad tag (#fyp, #foryou). Never spam.

### Instagram Reels caption (longer, 3–6 sentences)

**Formula:** `<hook echo>. <expansion sentence>. <observation>. <CTA>.`

Example:
> *"The bar is on the floor and she''s still tripping.*
>
> *Half the men her age don''t know how to make a reservation. The other half think ''communication'' is replying to her story.*
>
> *Standards aren''t asking too much. They''re the floor.*
>
> *Sunday newsletter is on this. Link in bio."*

### Instagram carousel caption

**Formula:** `<title slide promise>. <thesis paragraph, 3–4 sentences>. <save/share CTA>.`

Carousels are the long-form play. Slow down. Develop the take. End with a
soft CTA.

### Instagram still-photo caption

**Formula:** `<observational opener>. <on-character one-liner>. <CTA optional>.`

Stills are her permission to be quieter. Less hook-y, more journal-y.

### Newsletter (beehiiv, ~600–900 words)

**Formula:** `<scene-setting open>. <the take she''s been sitting with>. <three supporting observations>. <Sunday-quiet landing>.`

Voice softens slightly here. More room to breathe. Less landed-take energy.',
  'Burn-in subtitle rules:

- **One line at a time.** Max 32 characters per line.
- **All-caps OK on overlays** (different from caption rule — overlays are
  visual hierarchy, not voice).
- **Anton or Bebas Neue** font. White text, 6px black stroke.
- **Position:** centered vertically at ~65% from top. Stay out of TikTok''s
  bottom UI.
- **Pacing:** chunk per spoken phrase. ~1.5–2 seconds per chunk.
- **Hook chunk on screen for full first 1.5 seconds**, then break to body.
- **Last frame (3.5–5s):** soft CTA on screen, e.g. "newsletter Sunday."',
  'Polished editorial; never harsh studio; warm friendly expression unless the pose says otherwise. See higgsfield-prompt-library.md §7 for per-template poses (50 templates).',
  'deformed hands, extra fingers, distorted face, asymmetric eyes, plastic skin, overly smoothed skin, uncanny valley, harsh studio lighting, neon colors, heavy contour, drag-style makeup, dark lipstick, gothic aesthetic, alt fashion, streetwear logos, Y2K aesthetic, club wear, lingerie, bikini, nudity, named celebrities, named politicians, recognizable government interiors, identifiable real people, MAGA hat with legible text, political signage with legible text, election year graphics, partisan iconography, weapons, drugs, alcohol bottles in foreground, watermarks, text overlays, low resolution, blurry, oversaturated',
  'See higgsfield-prompt-library.md and prompts table — 50 hand-crafted templates spanning P1–P50 across pillars 1/2/3/4.',
  'Lane A — conservative lifestyle commentator. NO named candidate endorsements, NO policy wonk specifics (immigration numbers, tax rates), NO race-coded content, NO punching down at other women, NO content with named real public figures, NO denominational debates, NO platform-violating sexual content.',
  '```
WARMTH:        7/10   (warm but not bubbly)
HUMOR:         6/10   (dry, observational, eye-roll)
CONVICTION:    8/10   (knows what she thinks, says it)
PREACHINESS:   2/10   (almost never)
SOFTNESS:      6/10   (feminine but not fragile)
EDGE:          5/10   (sharp landings, not mean)
SELF-AWARE:    8/10   (knows she''s the hot blonde with takes)
ENERGY:        4/10   (deliberate, never frenetic)
INTIMACY:      7/10   (talks TO you, not AT you)
```

Always paste this block into any prompt that asks an LLM to write IN
Sierra''s voice. It moves the dial more reliably than adjective lists.

When ideating, every post should fit one of these. If a draft fits none,
it''s probably off-brand and shouldn''t ship.

| Arc | What it looks like | Example hook |
|---|---|---|
| **A1 — The bar observation** | "the bar is on the floor and you''re still tripping" | H8, H3 |
| **A2 — Standards as floor** | "having standards isn''t asking too much" | H5, H12 |
| **A3 — Common sense isn''t** | calling out the obvious thing | H7, H17 |
| **A4 — Soft warning** | a heads-up to women, said calmly | H4, H14, H20 |
| **A5 — Permission slip** | giving women permission to want what they want | H9, H13, H16 |

Pillar 3 ("Make it make sense") is mostly A1 + A3.
Pillar 1 commentary leans A2 + A5.
Pillar 2 lifestyle is mostly tonal (no explicit arc) but should still
*feel* like one of the five if any take is delivered.',
  '```
let''s be honest · make it make sense · the bar is on the floor ·
I said what I said · next question · real talk · respectfully · noted ·
we''re not doing this · tell me you''re [X] without telling me ·
the quiet part out loud · grow up · do better · not the [thing] ·
oh we''re choosing violence today · the audacity · men in finance ·
pay attention · common sense isn''t common · feminine, not weak ·
soft girl, sharp mind · smart enough to know better · I don''t make the rules ·
this is a soft warning · file that under "things you should already know"
```',
  '```
hun · y''all · blessed · girlies · manifesting · energy (as noun) ·
vibes · literally (when overused) · slay · iconic · queen · periodt ·
no thoughts just · era (as in "X era") · obsessed (as in "obsessed with") ·
giving (as in "giving boss") · main character · POV-as-overuse ·
let her cook · cooking · ate · ate that · lowkey · highkey · besties ·
the giggles · pookie · tea (gossip sense) · spilling · the receipts ·
omg · ugh literally · I can''t · so real for that
```

```
candidate names as endorsements · partisan slurs (libtard, MAGAt, etc.) ·
direct election commentary · scripture quotes (she''s faith-coded, not preachy) ·
the words "woke", "based", "redpilled" (tribal markers, not hers) ·
dating-app screenshots with names visible · minor''s names · 
specific named celebrities used as targets · weight-shaming · race-shaming ·
"as a Christian woman" or any in-group declaration
```

Treat these as anti-examples. Any draft that sounds like one of these is
broken. Add new examples here whenever a draft fails the smell test.

- "OMG girlies I''m literally obsessed with this look 🥺💕" (basic)
- "Manifesting my soft girl era, who''s with me?" (vocab + arc fail)
- "As a Christian woman in 2026, I just feel called to say…" (preachy)
- "[Candidate name] is the only one telling the truth!" (partisan)
- "If you don''t agree you can unfollow ✌️" (defensive, off-character)
- "Slay queen energy, periodt 💅" (vocab)
- "Y''all I''m crying she''s just so iconic 😭" (vocab + tonal)
- "Spilling the tea on my morning routine 🍵" (vocab)
- "I''ll be praying for everyone in the comments." (preachy + smug)'
)
ON CONFLICT (influencer_id) DO UPDATE SET
  personality_rules = EXCLUDED.personality_rules,
  caption_style = EXCLUDED.caption_style,
  visual_rules = EXCLUDED.visual_rules,
  posing_rules = EXCLUDED.posing_rules,
  negative_prompts = EXCLUDED.negative_prompts,
  example_prompts = EXCLUDED.example_prompts,
  content_boundaries = EXCLUDED.content_boundaries,
  tone_guidelines = EXCLUDED.tone_guidelines,
  would_say = EXCLUDED.would_say,
  would_never_say = EXCLUDED.would_never_say,
  updated_at = now();

-- =========================================================
-- -- Real Sierra Frost — 50 image/video prompt templates --
-- =========================================================

INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P1 — sitting at edge of bed, soft confident expression,', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: static lock-off, no camera movement, subject framed center, action: sitting at edge of bed, soft confident expression, looking off-camera, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 1 · Wardrobe A · Setting S1 · Shot: medium close-up · Motion: static lock-off, no camera movement, subject framed center', '{"pillar-1","wardrobe-A","setting-S1","kind-tiktok","P1"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P2 — typing on laptop, looking up at camera mid-thought', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium shot, camera motion: slow dolly push toward subject''s face, ending on tight close-up, action: typing on laptop, looking up at camera mid-thought, half-smile, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 1 · Wardrobe B · Setting S5 · Shot: medium shot · Motion: slow dolly push toward subject''s face, ending on tight close-up', '{"pillar-1","wardrobe-B","setting-S5","kind-tiktok","P2"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P3 — looking directly to camera, dry knowing expression', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: tight close-up, camera motion: slow dolly push toward subject''s face, action: looking directly to camera, dry knowing expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 1 · Wardrobe neutral · Setting S1 · Shot: tight close-up · Motion: slow dolly push toward subject''s face', '{"pillar-1","wardrobe-neutral","setting-S1","kind-tiktok","P3"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P4 — writing in leather journal, latte beside her, cont', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: over-the-shoulder, camera motion: static lock-off, no camera movement, action: writing in leather journal, latte beside her, contemplative, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 1 · Wardrobe A · Setting S5 · Shot: over-the-shoulder · Motion: static lock-off, no camera movement', '{"pillar-1","wardrobe-A","setting-S5","kind-tiktok","P4"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P5 — sitting cross-legged on bed with open journal, mor', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: wide environmental, camera motion: slow dolly pull back from medium shot to wide environmental reveal, action: sitting cross-legged on bed with open journal, morning light, serene, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe D · Setting S1 · Shot: wide environmental · Motion: slow dolly pull back from medium shot to wide environmental reveal', '{"pillar-2","wardrobe-D","setting-S1","kind-tiktok","P5"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P6 — post-workout, slight glow, water bottle in hand, c', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, inside a bright minimalist Pilates studio, reformer machine visible, large windows with morning light, warm wood floor, white walls with subtle ribbed-wood detail, neutral palette, polished wellness aesthetic, shot type: medium close-up, camera motion: static lock-off, action: post-workout, slight glow, water bottle in hand, casual confident, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe C · Setting S4 · Shot: medium close-up · Motion: static lock-off', '{"pillar-2","wardrobe-C","setting-S4","kind-tiktok","P6"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P7 — walking toward camera, hair moving in breeze, soft', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: cowboy shot mid-thigh up, camera motion: loose handheld follow, subject walking forward, slight natural sway, action: walking toward camera, hair moving in breeze, soft smile, golden hour, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe B · Setting S2 · Shot: cowboy shot mid-thigh up · Motion: loose handheld follow, subject walking forward, slight natural sway', '{"pillar-2","wardrobe-B","setting-S2","kind-tiktok","P7"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P8 — pearl-strand earring detail, soft side-lit, neutra', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: tight close-up, camera motion: slow dolly push toward subject''s face, action: pearl-strand earring detail, soft side-lit, neutral expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 1 · Wardrobe A · Setting S1 · Shot: tight close-up · Motion: slow dolly push toward subject''s face', '{"pillar-1","wardrobe-A","setting-S1","kind-tiktok","P8"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P9 — hands typing on laptop, gold ring and dainty brace', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: detail insert close-up, camera motion: static lock-off, action: hands typing on laptop, gold ring and dainty bracelet visible, journal beside, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 1 · Wardrobe neutral · Setting S5 · Shot: detail insert close-up · Motion: static lock-off', '{"pillar-1","wardrobe-neutral","setting-S5","kind-tiktok","P9"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P10 — sitting on edge of bed lacing sneakers, morning ro', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium shot, camera motion: smooth 90-degree arc around subject, golden hour rim light, action: sitting on edge of bed lacing sneakers, morning routine vibe, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe C · Setting S1 · Shot: medium shot · Motion: smooth 90-degree arc around subject, golden hour rim light', '{"pillar-2","wardrobe-C","setting-S1","kind-tiktok","P10"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P11 — small in frame, palm trees dominant, walking away ', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: wide environmental, camera motion: static lock-off, action: small in frame, palm trees dominant, walking away from camera, candid, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe B · Setting S2 · Shot: wide environmental · Motion: static lock-off', '{"pillar-2","wardrobe-B","setting-S2","kind-tiktok","P11"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P12 — looking up from laptop directly to camera, faint s', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: looking up from laptop directly to camera, faint smile, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe A · Setting S5 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-4","wardrobe-A","setting-S5","kind-tiktok","P12"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P13 — open devotional book on lap (no legible text on pa', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: over-the-shoulder, camera motion: static lock-off, action: open devotional book on lap (no legible text on page), soft window light, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe D · Setting S1 · Shot: over-the-shoulder · Motion: static lock-off', '{"pillar-2","wardrobe-D","setting-S1","kind-tiktok","P13"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P14 — mid-Pilates form on reformer, controlled and grace', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, inside a bright minimalist Pilates studio, reformer machine visible, large windows with morning light, warm wood floor, white walls with subtle ribbed-wood detail, neutral palette, polished wellness aesthetic, shot type: full body, camera motion: slow dolly pull back, action: mid-Pilates form on reformer, controlled and graceful, not strained, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe C · Setting S4 · Shot: full body · Motion: slow dolly pull back', '{"pillar-2","wardrobe-C","setting-S4","kind-tiktok","P14"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P15 — getting ready at vanity, lipstick mid-application,', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted satin slip dress in deep navy, classic stiletto heels, gold statement earrings, sleek straight hair or soft glam waves, polished evening makeup with subtle smokey eye, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: tight close-up, camera motion: static lock-off, action: getting ready at vanity, lipstick mid-application, mirror reflection visible, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe E · Setting S1 · Shot: tight close-up · Motion: static lock-off', '{"pillar-2","wardrobe-E","setting-S1","kind-tiktok","P15"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P16 — Worth Avenue boutique window in soft background, p', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: cowboy shot mid-thigh up, camera motion: smooth 90-degree arc around subject, action: Worth Avenue boutique window in soft background, polished day-out, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe B · Setting S2 · Shot: cowboy shot mid-thigh up · Motion: smooth 90-degree arc around subject', '{"pillar-2","wardrobe-B","setting-S2","kind-tiktok","P16"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P17 — entering cafe with leather tote, sunglasses pushed', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium shot, camera motion: loose handheld follow, action: entering cafe with leather tote, sunglasses pushed up on head, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe A · Setting S5 · Shot: medium shot · Motion: loose handheld follow', '{"pillar-2","wardrobe-A","setting-S5","kind-tiktok","P17"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P18 — Sunday morning getting ready, cross necklace detai', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: Sunday morning getting ready, cross necklace detail, soft golden light, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe D · Setting S1 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-2","wardrobe-D","setting-S1","kind-tiktok","P18"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P19 — stretching at barre, post-class, tied-up hair, dew', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, inside a bright minimalist Pilates studio, reformer machine visible, large windows with morning light, warm wood floor, white walls with subtle ribbed-wood detail, neutral palette, polished wellness aesthetic, shot type: cowboy shot mid-thigh up, camera motion: static lock-off, action: stretching at barre, post-class, tied-up hair, dewy skin, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe C · Setting S4 · Shot: cowboy shot mid-thigh up · Motion: static lock-off', '{"pillar-2","wardrobe-C","setting-S4","kind-tiktok","P19"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P20 — walking past palms with iced coffee in hand, candi', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: full body, camera motion: loose handheld follow, subject walking forward, action: walking past palms with iced coffee in hand, candid Florida day, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe B · Setting S2 · Shot: full body · Motion: loose handheld follow, subject walking forward', '{"pillar-2","wardrobe-B","setting-S2","kind-tiktok","P20"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P21 — closet detail: rows of neutral dresses, gold jewel', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: detail insert close-up, camera motion: static lock-off, action: closet detail: rows of neutral dresses, gold jewelry tray, organized polished, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe neutral · Setting S1 · Shot: detail insert close-up · Motion: static lock-off', '{"pillar-2","wardrobe-neutral","setting-S1","kind-tiktok","P21"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P22 — writing in journal at sidewalk cafe table, golden ', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium shot, camera motion: slow dolly push toward subject''s face, action: writing in journal at sidewalk cafe table, golden hour, palm shadow, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe A · Setting S5 · Shot: medium shot · Motion: slow dolly push toward subject''s face', '{"pillar-4","wardrobe-A","setting-S5","kind-tiktok","P22"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P23 — morning routine: hair up in claw clip, applying se', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: morning routine: hair up in claw clip, applying serum, no makeup, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe C · Setting S1 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-2","wardrobe-C","setting-S1","kind-tiktok","P23"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P24 — golden hour at marina with white yachts behind, cl', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted satin slip dress in deep navy, classic stiletto heels, gold statement earrings, sleek straight hair or soft glam waves, polished evening makeup with subtle smokey eye, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: wide environmental, camera motion: slow dolly pull back from medium shot to wide environmental reveal, action: golden hour at marina with white yachts behind, classy evening, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe E · Setting S2 · Shot: wide environmental · Motion: slow dolly pull back from medium shot to wide environmental reveal', '{"pillar-2","wardrobe-E","setting-S2","kind-tiktok","P24"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P25 — mirror outfit check, full polish, confident, fit-c', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: cowboy shot mid-thigh up, camera motion: smooth 90-degree arc around subject, action: mirror outfit check, full polish, confident, fit-check energy, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe A · Setting S1 · Shot: cowboy shot mid-thigh up · Motion: smooth 90-degree arc around subject', '{"pillar-2","wardrobe-A","setting-S1","kind-tiktok","P25"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P26 — laptop screen shows newsletter draft (no legible t', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: over-the-shoulder, camera motion: static lock-off, action: laptop screen shows newsletter draft (no legible text), intentional newsletter-funnel content, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe A · Setting S5 · Shot: over-the-shoulder · Motion: static lock-off', '{"pillar-4","wardrobe-A","setting-S5","kind-tiktok","P26"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P27 — drinking from glass water bottle, content post-wor', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, inside a bright minimalist Pilates studio, reformer machine visible, large windows with morning light, warm wood floor, white walls with subtle ribbed-wood detail, neutral palette, polished wellness aesthetic, shot type: medium shot, camera motion: slow dolly push toward subject''s face, action: drinking from glass water bottle, content post-workout, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe C · Setting S4 · Shot: medium shot · Motion: slow dolly push toward subject''s face', '{"pillar-2","wardrobe-C","setting-S4","kind-tiktok","P27"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P28 — walking up church steps in modest dress, hand on B', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, on the steps outside a marble-columned classical building, Corinthian columns visible behind, American flag faintly visible in distant background (no legible text), bright clear blue sky, dramatic shadow lines on stone, no other identifiable people in frame, exterior only, shot type: cowboy shot mid-thigh up, camera motion: loose handheld follow, action: walking up church steps in modest dress, hand on Bible-style journal (no legible text), shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe D · Setting S3 · Shot: cowboy shot mid-thigh up · Motion: loose handheld follow', '{"pillar-2","wardrobe-D","setting-S3","kind-tiktok","P28"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P29 — getting ready for evening event, full mirror, poli', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted satin slip dress in deep navy, classic stiletto heels, gold statement earrings, sleek straight hair or soft glam waves, polished evening makeup with subtle smokey eye, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: full body, camera motion: slow dolly pull back, action: getting ready for evening event, full mirror, polished glam, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe E · Setting S1 · Shot: full body · Motion: slow dolly pull back', '{"pillar-2","wardrobe-E","setting-S1","kind-tiktok","P29"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P30 — laughing softly at something off-camera, latte in ', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: laughing softly at something off-camera, latte in hand, natural, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe B · Setting S5 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-2","wardrobe-B","setting-S5","kind-tiktok","P30"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P31 — eyebrow raise, slight head tilt, you''re-kidding-ri', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: tight close-up, camera motion: static lock-off, action: eyebrow raise, slight head tilt, you''re-kidding-right expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe neutral · Setting S1 · Shot: tight close-up · Motion: static lock-off', '{"pillar-3","wardrobe-neutral","setting-S1","kind-tiktok","P31"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P32 — sitting on bed mid-coffee sip, pause, dry sideways', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: sitting on bed mid-coffee sip, pause, dry sideways glance to camera, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe C · Setting S1 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-3","wardrobe-C","setting-S1","kind-tiktok","P32"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P33 — mid-typing, looks up over laptop, dry really? expr', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium close-up, camera motion: static lock-off, action: mid-typing, looks up over laptop, dry really? expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe A · Setting S5 · Shot: medium close-up · Motion: static lock-off', '{"pillar-3","wardrobe-A","setting-S5","kind-tiktok","P33"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P34 — soft eye-roll, knowing patient expression', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: tight close-up, camera motion: static lock-off, action: soft eye-roll, knowing patient expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe D · Setting S1 · Shot: tight close-up · Motion: static lock-off', '{"pillar-3","wardrobe-D","setting-S1","kind-tiktok","P34"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P35 — sunglasses lowered to look at camera over them, kn', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: sunglasses lowered to look at camera over them, knowing smile, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe B · Setting S2 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-3","wardrobe-B","setting-S2","kind-tiktok","P35"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P36 — slow head shake, slight smirk, arms crossed, we''re', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium shot, camera motion: slow dolly push toward subject''s face, action: slow head shake, slight smirk, arms crossed, we''re-not-doing-this energy, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe neutral · Setting S1 · Shot: medium shot · Motion: slow dolly push toward subject''s face', '{"pillar-3","wardrobe-neutral","setting-S1","kind-tiktok","P36"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P37 — chin in hand at table, deadpan straight-to-camera,', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: tight close-up, camera motion: static lock-off, action: chin in hand at table, deadpan straight-to-camera, go-on energy, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe A · Setting S5 · Shot: tight close-up · Motion: static lock-off', '{"pillar-3","wardrobe-A","setting-S5","kind-tiktok","P37"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P38 — mid-laugh that turns into wait-you''re-serious expr', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: mid-laugh that turns into wait-you''re-serious expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe C · Setting S1 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-3","wardrobe-C","setting-S1","kind-tiktok","P38"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P39 — walking toward camera, small smirk, let-me-explain', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing white linen sundress with thin straps, beige espadrille sandals, gold layered necklaces, hair air-dried in soft beachy waves, no jacket, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: medium shot, camera motion: loose handheld follow, subject walking forward, action: walking toward camera, small smirk, let-me-explain energy, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe B · Setting S2 · Shot: medium shot · Motion: loose handheld follow, subject walking forward', '{"pillar-3","wardrobe-B","setting-S2","kind-tiktok","P39"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P40 — slow blink, deadpan, the-audacity energy', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted satin slip dress in deep navy, classic stiletto heels, gold statement earrings, sleek straight hair or soft glam waves, polished evening makeup with subtle smokey eye, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: tight close-up, camera motion: slow dolly push toward subject''s face, action: slow blink, deadpan, the-audacity energy, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 3 · Wardrobe E · Setting S1 · Shot: tight close-up · Motion: slow dolly push toward subject''s face', '{"pillar-3","wardrobe-E","setting-S1","kind-tiktok","P40"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P41 — writing newsletter, Sunday morning energy', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: over-the-shoulder, camera motion: slow dolly push toward subject''s face, action: writing newsletter, Sunday morning energy, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe A · Setting S5 · Shot: over-the-shoulder · Motion: slow dolly push toward subject''s face', '{"pillar-4","wardrobe-A","setting-S5","kind-tiktok","P41"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P42 — laptop in lap, leather journal beside, Sunday news', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium shot, camera motion: static lock-off, action: laptop in lap, leather journal beside, Sunday newsletter day atmosphere, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe D · Setting S1 · Shot: medium shot · Motion: static lock-off', '{"pillar-4","wardrobe-D","setting-S1","kind-tiktok","P42"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P43 — laptop screen showing clean writing-app interface ', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: detail insert close-up, camera motion: static lock-off, action: laptop screen showing clean writing-app interface (no legible text), morning latte beside, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe neutral · Setting S5 · Shot: detail insert close-up · Motion: static lock-off', '{"pillar-4","wardrobe-neutral","setting-S5","kind-tiktok","P43"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P44 — cozy writing-in-bed energy, pen and journal, soft ', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing matching neutral set: cream sports bra and high-waisted bike shorts, Hoka or On running sneakers, hair pulled into low ponytail, dewy fresh face, small gold hoops, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: slow dolly push toward subject''s face, action: cozy writing-in-bed energy, pen and journal, soft natural, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe C · Setting S1 · Shot: medium close-up · Motion: slow dolly push toward subject''s face', '{"pillar-4","wardrobe-C","setting-S1","kind-tiktok","P44"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P45 — full sidewalk-cafe scene, MacBook plus journal plu', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, at a small marble cafe table near a window, MacBook open with a clean writing app on screen (no legible text), latte in ceramic cup, leather journal beside laptop, soft window light, blurred warm interior in background, intimate productive atmosphere, shot type: medium shot, camera motion: slow dolly pull back, action: full sidewalk-cafe scene, MacBook plus journal plus latte, golden hour, the writer-girl archetype shot, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 4 · Wardrobe A · Setting S5 · Shot: medium shot · Motion: slow dolly pull back', '{"pillar-4","wardrobe-A","setting-S5","kind-tiktok","P45"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P46 — golden hour, palm shadow on white wall behind, pol', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: medium close-up, camera motion: smooth 90-degree arc around subject, golden hour rim light, action: golden hour, palm shadow on white wall behind, polished editorial, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe A · Setting S2 · Shot: medium close-up · Motion: smooth 90-degree arc around subject, golden hour rim light', '{"pillar-2","wardrobe-A","setting-S2","kind-hero","P46"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P47 — sitting at edge of bed, full polish, soft window l', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium shot, camera motion: static lock-off, action: sitting at edge of bed, full polish, soft window light, hero shot composition, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe A · Setting S1 · Shot: medium shot · Motion: static lock-off', '{"pillar-2","wardrobe-A","setting-S1","kind-hero","P47"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P48 — steps of marble building exterior, golden afternoo', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted navy midi dress with cream cropped blazer, nude pointed-toe heels, dainty gold necklace, small camel structured handbag, hair styled in soft waves, on the steps outside a marble-columned classical building, Corinthian columns visible behind, American flag faintly visible in distant background (no legible text), bright clear blue sky, dramatic shadow lines on stone, no other identifiable people in frame, exterior only, shot type: cowboy shot mid-thigh up, camera motion: slow dolly pull back, action: steps of marble building exterior, golden afternoon, polished editorial, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe A · Setting S3 · Shot: cowboy shot mid-thigh up · Motion: slow dolly pull back', '{"pillar-2","wardrobe-A","setting-S3","kind-hero","P48"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P49 — sunset marina, classic red or navy evening dress, ', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing fitted satin slip dress in deep navy, classic stiletto heels, gold statement earrings, sleek straight hair or soft glam waves, polished evening makeup with subtle smokey eye, on a Palm Beach waterfront walkway, palm trees in background, white classical-style architecture, calm turquoise water visible behind, golden hour light, pastel sky, polished resort aesthetic, no other recognizable people in frame, shot type: full body, camera motion: smooth 90-degree arc around subject, action: sunset marina, classic red or navy evening dress, hero shot, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe E · Setting S2 · Shot: full body · Motion: smooth 90-degree arc around subject', '{"pillar-2","wardrobe-E","setting-S2","kind-hero","P49"}');
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P50 — Sunday morning hero, soft pastel light, dainty cro', 'image', '24-year-old woman, blonde mid-length hair with soft beachy waves, light blue-green eyes, glowy lightly-tanned skin, full lips with glossy nude makeup, polished natural makeup with soft contour and warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit Pilates body, warm friendly expression unless otherwise specified, wearing modest knee-length dress in soft cream or dusty pink, fitted but not tight, three-quarter sleeves, simple dainty cross necklace, neutral nude heels, soft natural makeup, hair half-up, in a bright Scandinavian-style bedroom, white linen bedding, oak nightstand, floor-to-ceiling window with sheer curtains, eucalyptus plant in clay pot, soft morning light streaming through window, neutral palette of cream beige and warm wood, shot type: medium close-up, camera motion: static lock-off, action: Sunday morning hero, soft pastel light, dainty cross, thoughtful but warm expression, shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, soft natural lighting, golden hour or warm window light, neutral color palette, candid editorial composition, cinematic but warm, polished but not stiff, high detail, ultra realistic photographic quality', 'Pillar 2 · Wardrobe D · Setting S1 · Shot: medium close-up · Motion: static lock-off', '{"pillar-2","wardrobe-D","setting-S1","kind-hero","P50"}');

-- ========================================================
-- -- Real Sierra Frost — ai_outputs from generation log --
-- ========================================================

INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P1 generation — sitting at edge of bed, soft confident expression, looking o', 'job_id: 82e43aaa-a6cc-49cc-9a2f-ee213121b571
seed: 647249
pose: sitting at edge of bed, soft confident expression, looking off-camera
result: ok — identity locked, wardrobe + setting rendered correctly
output: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_055119_82e43aaa-a6cc-49cc-9a2f-ee213121b571.png
local: personas/sierra-frost/content-queue/2026-05-06_P1_v1.png', 'P1', '{"P1","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P8 generation — pearl-strand earring detail, soft side-lit, neutral expressi', 'job_id: b7c7a868-d234-4f16-8518-83896850ee3b
seed: 87114
pose: pearl-strand earring detail, soft side-lit, neutral expression
result: ok — identity locked; model rendered medium portrait rather than
output: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_055243_b7c7a868-d234-4f16-8518-83896850ee3b.png
local: personas/sierra-frost/content-queue/2026-05-06_P8_v1.png', 'P8', '{"P8","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P3 generation — looking directly to camera, dry knowing expression', 'job_id: 39a41c0c-d339-4786-a96b-fcd977f88767
seed: 528443
pose: looking directly to camera, dry knowing expression
result: stalled — Higgsfield queue held this job in `in_progress` for
output: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060058_ee34725b-347f-4571-b065-9242a454163f.png
local: personas/sierra-frost/content-queue/2026-05-06_P3_v1.png', 'P3', '{"P3","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P5 generation — sitting cross-legged on bed with open journal, morning light', 'job_id: 188e7343-edce-49c8-a076-e225fece7dd6
seed: 59164
pose: sitting cross-legged on bed with open journal, morning light, serene
result: ok with caveat — identity locked, dusty pink dress + cross
output: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060108_188e7343-edce-49c8-a076-e225fece7dd6.png
local: personas/sierra-frost/content-queue/2026-05-06_P5_v1.png', 'P5', '{"P5","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P7 generation — walking toward camera, hair moving in breeze, soft smile, go', 'job_id: c00d69bc-5609-47f9-8324-9b41d73e4c1a
seed: 715240
pose: walking toward camera, hair moving in breeze, soft smile, golden hour
result: ok — identity locked, Palm Beach environment rendered (palm
output: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060119_c00d69bc-5609-47f9-8324-9b41d73e4c1a.png
local: personas/sierra-frost/content-queue/2026-05-06_P7_v1.png', 'P7', '{"P7","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P12 generation — looking up from laptop directly to camera, faint smile', 'job_id: b181ca33-b4a3-470e-80a1-df68ceb6976c
seed: 196883
pose: looking up from laptop directly to camera, faint smile
result: ok — identity locked, marble cafe table + MacBook + latte +
output: https://d8j0ntlcm91z4.cloudfront.net/user_39gpDpVR13jUsxEVCRIxTlamScD/hf_20260506_060130_b181ca33-b4a3-470e-80a1-df68ceb6976c.png
local: personas/sierra-frost/content-queue/2026-05-06_P12_v1.png', 'P12', '{"P12","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P14 generation — mid-Pilates form on reformer, controlled and graceful', 'job_id: 2d028251-f803-499f-a590-cd31850bd327
seed: 946215
pose: mid-Pilates form on reformer, controlled and graceful
result: ok — identity locked, Pilates studio + cream activewear rendered correctly. New wardrobe + setting in the training pool.
output: 
local: personas/sierra-frost/content-queue/2026-05-06_P14_v1.png', 'P14', '{"P14","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P15 generation — getting ready at vanity, lipstick mid-application', 'job_id: 41c7b51d-1438-4a05-b9a3-b415e2f9b172
seed: 92924
pose: getting ready at vanity, lipstick mid-application
result: ok — identity locked, camel cashmere wardrobe is a new texture for the training pool.
output: 
local: personas/sierra-frost/content-queue/2026-05-06_P15_v1.png', 'P15', '{"P15","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P17 generation — entering cafe with leather tote, sunglasses pushed up on hea', 'job_id: e604fa4d-1545-4486-9136-10c583ac1707
seed: 969464
pose: entering cafe with leather tote, sunglasses pushed up on head
result: ok — identity locked, different cafe angle than P12 (sunglasses, entry framing).
output: 
local: personas/sierra-frost/content-queue/2026-05-06_P17_v1.png', 'P17', '{"P17","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P19 generation — stretching at barre, post-class, tied-up hair, dewy skin', 'job_id: 704e8625-5e35-4cb6-a5e2-246c91daf134
seed: 967423
pose: stretching at barre, post-class, tied-up hair, dewy skin
result: ok — identity locked, second cream-set angle for activewear variety.
output: 
local: personas/sierra-frost/content-queue/2026-05-06_P19_v1.png', 'P19', '{"P19","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'P20 generation — walking past palms with iced coffee in hand, candid Florida ', 'job_id: af26b9db-3b1f-4514-ae48-cdb370cc8a53
seed: 273642
pose: walking past palms with iced coffee in hand, candid Florida day
result: ok — identity locked, second Palm Beach angle (different pose from P7''s walking-toward-camera).
output: 
local: personas/sierra-frost/content-queue/2026-05-06_P20_v1.png', 'P20', '{"P20","soul_2","higgsfield","image"}', false);
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'image', 'PROFILE generation — serene three-quarter profile portrait, looking thoughtfully ', 'job_id: f39ebf73-61c4-4220-8cd3-fd51eae37030
seed: 342133
pose: serene three-quarter profile portrait, looking thoughtfully off to the side, hair tucked behind ear
result: ok — identity locked, 85mm tight close-up. Critical for the
output: 
local: personas/sierra-frost/content-queue/2026-05-06_PROFILE_v1.png', 'PROFILE', '{"PROFILE","soul_2","higgsfield","image"}', false);
-- 12 ai_outputs rows inserted from generation-log.md

-- =========================================
-- -- Real Sierra Frost — 4 content units --
-- =========================================

INSERT INTO content_items (influencer_id, title, body, caption, hook, type, platform, status, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P1 — content unit (2026-05-06_P1)', '# Content Unit — 2026-05-06 — P1 (Bedroom / Wardrobe A / Pillar 1)

> Postable, voice-checked content unit anchored to a specific generated
> asset. Drives one TikTok + IG carryover. Lint against
> `voice-profile.md` before publishing.

## Asset

- **Image:** `personas/sierra-frost/content-queue/2026-05-06_P1_v1.png` (1152x2048)
- **Video** (idle B-roll): `personas/sierra-frost/content-queue/2026-05-06_P1_v1.mp4` (5s, 720x1280, audio ambient)
- **Pillar:** 1 — Commentary / Hot Takes
- **Narrative arc:** A2 — Standards as floor
- **Hook structure:** H12 (Unpopular opinion)

## Hook variants (pick one, A/B test on next post)

| # | Hook (first 1.5s on screen + spoken) |
|---|---|
| A | **Unpopular opinion: standards aren''t asking too much.** |
| B | **Three things I''m done apologizing for.** |
| C | **The bar is on the floor and she''s still tripping.** |

**Recommended:** A. Cleanest A2 fit, scripts well, captions self-echo.

## TikTok voiceover script (15 seconds, ~36 words)

> [00.0–01.5] Unpopular opinion: standards aren''t asking too much.
>
> [01.5–05.0] Half the men her age don''t know how to make a reservation.
>
> [05.0–09.0] The other half think communication is replying to her story.
>
> [09.0–12.5] Standards aren''t a wishlist. They''re the floor.
>
> [12.5–15.0] If that''s controversial, that''s the problem.

Pacing notes: deliberate, slight pauses on landings (`reservation.`, `story.`, `floor.`). No uptalk. Final line lands flat — confidence, not question.

## On-screen text chunks (burn-in subtitles, 1 line at a time)

```
[00.0–01.5]  UNPOPULAR OPINION:
[01.5–03.0]  STANDARDS AREN''T
[03.0–05.0]  ASKING TOO MUCH.
[05.0–07.5]  HALF THE MEN HER AGE
[07.5–09.0]  CAN''T MAKE A RESERVATION.
[09.0–10.5]  THE OTHER HALF THINK
[10.5–12.5]  REPLYING TO A STORY = COMMUNICATION.
[12.5–14.0]  STANDARDS ARE THE FLOOR.
[14.0–15.0]  NEWSLETTER SUNDAY 🌴
```

Font: Anton, white, 6px black stroke, centered at 65% from top.

## Captions

### TikTok (≤150 chars)

> Unpopular opinion: standards aren''t asking too much. The bar is the floor. Newsletter Sunday 🌴 #realtalk #fyp

### Instagram Reels

> Unpopular opinion: standards aren''t asking too much.
>
> Half the men her age don''t know how to make a reservation. The other half think communication is replying to her story.
>
> Standards aren''t a wishlist. They''re the floor.
>
> Sunday newsletter is on this. Link in bio.

### Instagram still-photo (use the static P1)

> The bar is on the floor.
>
> She''s still tripping.
>
> 🌴

## Posting plan

- **Platform:** TikTok primary, IG Reel cross-post 2 hours later
- **Day/time (ET):** Tuesday or Thursday, **8:45–9:15 PM** (peak conservative-women evening scroll window per `viral-playbook.md`)
- **Pinned comment:** *"Newsletter Sunday — link in bio. ✌️ Tell me I''m wrong below."*
- **First-hour engagement:** reply to first 25 comments using §9 tier patterns
- **Disclosure footer:** ensure bio has the AI disclosure visible

## Predicted performance grade (gut)

- **Hook:** A — H12 lands hard, A2 arc is Sierra''s strongest
- **Identity match:** A — Wardrobe A is her most photographed look
- **Risk:** B — slightly partisan-feeling, soften further if comments push back
- **Estimated reach band:** 8K–40K on TikTok if posted in the recommended slot

## Lint result

Ran the §11 linter against this unit. **PASS** on all 10 rules.
', 'Unpopular opinion: standards aren''t asking too much. The bar is the floor. Newsletter Sunday 🌴 #realtalk #fyp', 'Unpopular opinion: standards aren''t asking too much.', 'tiktok', 'tiktok', 'approved', '{"P1","pillar-1","ready-to-post"}');
INSERT INTO content_items (influencer_id, title, body, caption, hook, type, platform, status, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P12 — content unit (2026-05-06_P12)', '# Content Unit — 2026-05-06 — P12 (Cafe / Wardrobe A / Pillar 4)

> Newsletter funnel content. Pillar 4 is 10% of cadence but disproportionately
> drives email signups, which drive monetization. Make every Pillar 4 post
> earn its slot.

## Asset

- **Image:** `personas/sierra-frost/content-queue/2026-05-06_P12_v1.png`
- **Pillar:** 4 — Newsletter Funnel / BTS
- **Narrative arc:** A5 — Permission slip (with explicit CTA)
- **Hook structure:** H15 (Here''s what nobody told you about [X])

## Hook variants

| # | Hook |
|---|---|
| A | **POV: writing Sunday''s newsletter.** |
| B | **Here''s what nobody told you about subscriptions you actually keep.** |
| C | **Pillar 4 BTS: this week''s newsletter is on standards.** |

**Recommended:** A. Lowest-friction Pillar 4 hook, lets the visual do the
talking. (POV format is Sierra-allowed in this exact phrasing per
`persona.md` Pillar 4 examples.)

## TikTok voiceover script (12 seconds — short, BTS energy, ~30 words)

> [00.0–02.0] POV: writing Sunday''s newsletter.
>
> [02.0–05.5] This week — why your standards aren''t actually high.
>
> [05.5–09.0] If that resonates, the link''s in my bio.
>
> [09.0–12.0] Sundays at 9 a.m. eastern. 🌴

Pacing: BTS posts run shorter. Sierra here is letting you eavesdrop, not
performing. Slightly warmer than commentary posts.

## On-screen text chunks

```
[00.0–02.0]  POV: WRITING SUNDAY''S
              NEWSLETTER.
[02.0–05.5]  THIS WEEK —
              YOUR STANDARDS AREN''T
              ACTUALLY HIGH.
[05.5–09.0]  LINK''S IN BIO.
[09.0–12.0]  SUNDAYS · 9 AM EST 🌴
```

## Captions

### TikTok (≤150 chars)

> POV: writing Sunday''s newsletter. This week is on standards. Link in bio. 🌴 #newsletter #softgirl #fyp

### Instagram Reels (longer cross-post)

> POV: writing Sunday''s newsletter.
>
> This week''s issue is on why your standards aren''t actually high — they''re just visible.
>
> Sundays at 9 a.m. eastern. Subscribe in the link in bio.
>
> 🌴

### Instagram still photo

> Pillar 4. Sundays at 9.
>
> 🌴

## Posting plan

- **Platform:** TikTok primary, IG Reel cross-post within 1 hour
- **Day/time (ET):** **Friday afternoon, 4:30 PM** — primes the Sunday newsletter open. Don''t use weekend slots; weekend traffic on Pillar 4 underperforms.
- **Pinned comment:** *"Subscribe link is in bio — first issue Sunday. 🌴"*
- **First-hour engagement:** Tier B/D mostly. Some comments will be "what''s the newsletter on?" — reply with **one-line tease**, not the full thesis. Make them subscribe to get it.

## Direct CTA — this is one of the 10% direct-CTA slots

This unit explicitly uses the **direct CTA** (subscribe link) per
voice-profile §6. That''s the trade-off of Pillar 4 — direct ask,
soft framing. Don''t apologize for the ask. Don''t repeat the ask twice
in the caption — the spoken line + the on-screen text + the bio link
is enough.

## Predicted performance grade

- **Hook:** B+ — POV is reliable but ceilings around 30K on TikTok
- **Conversion:** A — this is the highest-converting format Sierra runs (people who watch a "BTS writing the newsletter" video sign up at 3–5x rate of generic CTAs)
- **Identity match:** A — Wardrobe A + cafe = aspirational productive
- **Estimated reach band:** 5K–25K TikTok views, **but** target metric is
  newsletter signups not views. Aim for 30+ signups within 24h.

## Lint result

PASS on all 10 rules.

## Sequencing note

If posting all 4 units in one week, recommended order:
1. Sunday AM — **P7** (mood, build saves and shares)
2. Tuesday PM — **P1** (commentary, build comments)
3. Wednesday PM — **P3** as IG carousel insert (light traffic day)
4. Friday PM — **P12** (newsletter funnel, weekend setup)

Don''t post P1 and P12 within 24 hours of each other — both Wardrobe A,
visual variety drops.
', 'POV: writing Sunday''s newsletter. This week is on standards. Link in bio. 🌴 #newsletter #softgirl #fyp', '', 'tiktok', 'tiktok', 'approved', '{"P12","pillar-4","ready-to-post"}');
INSERT INTO content_items (influencer_id, title, body, caption, hook, type, platform, status, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P3 — content unit (2026-05-06_P3)', '# Content Unit — 2026-05-06 — P3 (Bedroom / neutral wardrobe / Pillar 1)

## Asset

- **Image:** `personas/sierra-frost/content-queue/2026-05-06_P3_v1.png`
- **Pillar:** 1 — Commentary / Hot Takes (intimate close-up version)
- **Narrative arc:** A1 — The bar observation
- **Hook structure:** H7 (Notice how nobody talks about [X])
- **Note:** Soul 2 rendered minimal wardrobe on the neutral template; for posting, the close-up framing crops chest/below. Use as portrait insert or paired carousel slide, not as a standalone TikTok where full body visible. **Treat as a still-only asset** for this unit.

## Hook variants

| # | Hook |
|---|---|
| A | **Notice how nobody talks about how he treats waitresses.** |
| B | **The quiet part out loud:** how a man treats service staff is who he is. |
| C | **Pro tip: watch how he tips before you let him meet your friends.** |

**Recommended:** A. H7 + A1 + Pillar 1 — cleanest fit.

## Format

Use as **Instagram still photo** with longer-form caption — *not* as a TikTok. The framing works better as a quiet observation post.

## Caption (Instagram still)

> Notice how nobody talks about how he treats waitresses.
>
> Not how he treats you on date three. The waitress. The Uber driver. The kid behind the counter at Chipotle.
>
> That''s who he is.
>
> Save this for later. 🌴

## Hashtags

`#datingstandards #realtalk #softgirl #fyp` (4 max — IG)

## Alternative use: Carousel slide #2

If used inside a multi-slide IG carousel, this image works as **slide #2** (the "develop the take" slide) of a 5-slide post titled *"5 things to notice on date one"*. The other slides should be drawn from upcoming P-templates with full-body visibility.

## Posting plan

- **Platform:** Instagram still post or carousel inclusion only
- **Day/time (ET):** Wednesday, **6:30 PM** (IG single-post peak)
- **Pinned comment:** *"Comment ✋ if you''ve watched this happen."*

## Predicted performance grade

- **Hook:** A — H7 is one of her highest-engagement hook structures
- **Format mismatch risk:** would underperform as TikTok (cropping); flagged
- **Estimated reach band:** 3K–15K on Instagram

## Lint result

PASS on all 10 rules.

## Production note for prompt-library iteration

This template surfaced a real prompt-library bug: the `neutral` wardrobe slot on Soul 2 defaults to revealing minimalist wear. **Action item:** patch `tools/generation/sierra_frost.py` `WARDROBE` dict to add a `neutral` block defining a modest default (cream knit, dainty necklace, hair down) so neutral-wardrobe templates render postable framing. Logged in `generation-log.md` 2026-05-06 batch-2 takeaways.
', '', 'Notice how nobody talks about how he treats waitresses.', 'tiktok', 'tiktok', 'approved', '{"P3","pillar-1","ready-to-post"}');
INSERT INTO content_items (influencer_id, title, body, caption, hook, type, platform, status, tags)
VALUES ('a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01', 'P7 — content unit (2026-05-06_P7)', '# Content Unit — 2026-05-06 — P7 (Palm Beach / Wardrobe B / Pillar 2)

> Highest-leverage unit in this batch. Walking video already exists,
> walking footage in golden hour is the best AI-influencer wedge there is.
> This unit is also the test bed for the assembly pipeline — if it ships
> end-to-end tonight it proves the whole stack.

## Asset

- **Image:** `personas/sierra-frost/content-queue/2026-05-06_P7_v1.png`
- **Video** (Seedance walking, 5s 720x1280, ambient beach audio):
  `personas/sierra-frost/content-queue/2026-05-06_P7_v1.mp4`
- **Pillar:** 2 — Lifestyle / "Soft Conservative"
- **Narrative arc:** A5 — Permission slip (lifestyle, not commentary)
- **Hook structure:** H14 (Your reminder that [X])

## Hook variants

| # | Hook |
|---|---|
| A | **Your reminder that you can just slow down.** |
| B | **Pillar 2 / Sunday energy: walking it off.** |
| C | **Three things I do when the discourse gets loud.** |

**Recommended:** A. Cleanest A5 + Pillar 2 fit. Quiet permission energy
matches the visual perfectly — golden hour walk, no agenda, just being.

## TikTok voiceover script (15 seconds, ~38 words)

> [00.0–02.0] Your reminder that you can just slow down.
>
> [02.0–05.0] You don''t owe the internet your whole nervous system.
>
> [05.0–08.5] Put the phone away. Walk somewhere pretty.
>
> [08.5–12.0] Notice the palms move before you check the comments.
>
> [12.0–15.0] Sunday newsletter''s on this. Link in bio.

Pacing: slowest of the four units. Lots of breath. Low affect — this is
mood-piece content. Should feel like someone whispering wisdom to you.

## On-screen text chunks

```
[00.0–02.0]  YOU CAN JUST SLOW DOWN.
[02.0–05.0]  YOU DON''T OWE THE INTERNET
              YOUR NERVOUS SYSTEM.
[05.0–08.5]  PUT THE PHONE AWAY.
              WALK SOMEWHERE PRETTY.
[08.5–12.0]  NOTICE THE PALMS MOVE
              BEFORE YOU CHECK THE COMMENTS.
[12.0–15.0]  NEWSLETTER SUNDAY 🌴
```

Font: Anton, white, 6px black stroke. Lower third at 70% from top to keep
walking subject''s face clear.

## Captions

### TikTok (≤150 chars)

> Your reminder that you can just slow down. Sunday newsletter''s on this 🌴 #softgirl #realtalk #fyp

### Instagram Reels

> Your reminder that you can just slow down.
>
> You don''t owe the internet your whole nervous system. Put the phone away. Walk somewhere pretty.
>
> Notice the palms move before you check the comments.
>
> 🌴

### Instagram carousel (use stills + this video as slide 1)

> Slide 1: video walk (this one)
> Slide 2–4: pull stills from `2026-05-06_P7_v1.png`, varied crops + on-image text snippets from script
> Slide 5: end card with newsletter CTA

## Music bed (royalty-free, suggested)

For TikTok/IG posting, swap the ambient beach audio for one of these:
- **Lo-fi beat** — calm, ~70bpm, no lyrics. (TikTok in-app library: search "calm soft girl")
- **Ambient piano** — Pillar 2 default
- **Sierra''s voice over silence** — when voice clone is ready, drop the music to −20dB under VO at −12dB

## Posting plan

- **Platform:** TikTok primary, IG Reel + cross-post within 1 hour, IG carousel Friday
- **Day/time (ET):** Sunday morning, **9:30–10:00 AM** (Sunday "soft mood" slot per `viral-playbook.md` — devotional/lifestyle audience leans morning)
- **Pinned comment:** *"What''s something you stopped scrolling for this week? 🌴"*
- **First-hour engagement:** lean Tier A (agreement) — this is mood content, comments will be positive vibes

## Predicted performance grade

- **Hook:** A+ — H14 + A5 is Sierra''s "savable" pattern, big share rates
- **Visual:** A+ — walking-on-Palm-Beach footage is rare in conservative-lifestyle space, high stop-scroll
- **Identity match:** A — Wardrobe B looks Florida-native
- **Estimated reach band:** **15K–80K** on TikTok if Sunday-AM-slotted; this is the strongest unit in tonight''s batch

## Lint result

PASS on all 10 rules.

## Pipeline test

This is the unit the assembly pipeline (Phase 4) will produce as a
finished mp4. After tonight, you should have a literal posted-ready
TikTok at `personas/sierra-frost/content-queue/2026-05-06_P7_assembled.mp4`.
', 'Your reminder that you can just slow down. Sunday newsletter''s on this 🌴 #softgirl #realtalk #fyp', 'Your reminder that you can just slow down.', 'tiktok', 'tiktok', 'approved', '{"P7","pillar-2","ready-to-post"}');

COMMIT;

