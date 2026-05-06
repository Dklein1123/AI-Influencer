# Persona Launch Checklist

> The 30-day playbook codified as a runbook. Use this for every new persona
> after Sierra Frost. Print it, work top-to-bottom, check boxes. The whole
> point is that persona #2 takes 1/3 the time persona #1 took.

**How to use:** copy this file to `personas/[new-persona]/launch-checklist.md`
and check items off in that copy. The original stays clean for the next
launch.

**Total elapsed:** ~30 days from concept to "monetization on, audience
forming."

---

## Phase 0 — Concept (Days -14 to 0)

Don't post anything until every box in this phase is checked. Pre-launch
discipline is what separates a portfolio from a graveyard.

### Strategic decisions

- [ ] **Lane locked.** Define lane × audience × monetization in one
      sentence. Confirm no overlap with existing portfolio personas.
- [ ] **Lane gap-checked.** Search TikTok + IG for top 20 accounts in this
      lane. Confirm: (a) audience exists, (b) no existing AI persona
      dominates, (c) brands actively spend in the niche.
- [ ] **Risk tier assigned.** Low / Medium / High per `COMPANY.md` §12.
      Disclosure approach matched to risk tier.
- [ ] **Disclosure stance decided.** Soft (Sierra-style) or explicit ("AI
      model"). Document in persona bible.

### Identity

- [ ] **Name picked.** Check availability on TikTok, IG, X, Threads,
      beehiiv, Stan.store, the matching domain. All available before
      committing.
- [ ] **Handle picked.** Same handle across all platforms — ideally
      `firstname.lastname` or `firstname.last.xo` style. Lock everywhere
      before announcing.
- [ ] **Bio copy drafted.** Short version (TikTok), longer version (IG),
      newsletter "about" page. Disclosure baked in.
- [ ] **One-line positioning written.** "Persona is X for Y." If you can't
      write this in one sentence, the lane isn't sharp enough.

### Visual identity

- [ ] **Reference images sourced.** 6–10 mood-board images defining the
      look (hair, skin, makeup, body, age range). Use real photos for
      reference; we generate from there.
- [ ] **Soul ID v1 trained** on the cleanest reference set. Save with name
      `[persona-slug]-v1`.
- [ ] **Test generations.** Generate 20 images across multiple prompts;
      confirm identity locks. If drift > 20%, retrain before proceeding.
- [ ] **Wardrobe palette locked.** Hero colors, accents, "never" list. Keep
      tight — too much variety reads as inconsistent.
- [ ] **5 hero settings defined.** The reusable environments she shows up
      in repeatedly.

### Voice identity

- [ ] **Voice archetype picked.** Reference 2–3 real creators whose
      delivery feels right (e.g., for Sierra: Brett Cooper, Tomi Lahren,
      Allie Beth Stuckey).
- [ ] **ElevenLabs voice locked** as `[persona-slug]-voice-v1`. Or, if
      using your own voice over the persona's face, confirm the voice
      doesn't break the illusion.
- [ ] **Voice rules documented** in the persona bible (pace, pitch, tone).

### Documentation

- [ ] **Persona bible written** at `personas/[name]/persona.md`. Use
      Sierra's as the template. Include all 12 sections.
- [ ] **Viral playbook drafted** at `personas/[name]/viral-playbook.md`.
      Tier rules (🟢 only), 8 structures applied to the lane, 50-take
      backlog, hook library, conversion-test discipline.
- [ ] **Higgsfield prompt library drafted** at
      `personas/[name]/higgsfield-prompt-library.md`. 50 templates minimum
      across the 5 settings × wardrobe blocks × shot types.
- [ ] **Brand pitch templates customized** at
      `personas/[name]/brand-pitch-templates.md`. Rate sheet adjusted for
      the niche, affiliate program list customized, DM/email templates
      reworded for the audience.

### Infrastructure

- [ ] **Email created** — `[persona]@[company-domain]` via Google
      Workspace.
- [ ] **TikTok account created.** Personal → Business (free) for
      analytics. Bio + link in bio set.
- [ ] **Instagram account created.** Personal → Creator account. Bio +
      linktr.ee placeholder set.
- [ ] **Threads account created** (linked to IG by default).
- [ ] **Newsletter set up on beehiiv.** Welcome email + first send draft
      ready. Sign-up form embedded on landing page or Stan.store.
- [ ] **Stan.store / Beacons set up.** Replaces linktr.ee. Affiliate links
      seeded (placeholders OK on day 0; fill in once approved).
- [ ] **Domain registered** via Cloudflare. Point at Stan.store or simple
      landing page.
- [ ] **Posting scheduler connected** (Metricool or Buffer) to TikTok +
      IG.
- [ ] **Analytics tracking confirmed** working on each platform.

### Initial content batch

- [ ] **First 14 days of content planned.** Use the sprint matrix from the
      viral playbook — every post mapped to a structure × backlog item.
- [ ] **First 30 generations completed** in Higgsfield. Quality-gate each
      against the checklist. Selected assets in `content-queue/`.
- [ ] **First 14 captions drafted.** Drive every one to bio. Include base
      hashtag set + 1–2 trend tags.
- [ ] **First 7 days scheduled** in the posting tool. Day 8–14 generation
      done but not yet scheduled (we'll adjust based on Day 1–7 learning).

### Legal / ops

- [ ] **LLC owns this persona** (assumed already incorporated per
      `COMPANY.md` §10).
- [ ] **Operational isolation confirmed.** Different email, different
      Stan.store, no cross-promotion with existing personas. No following
      each other from internal accounts.
- [ ] **Disclosure language reviewed against current platform policies**
      (TikTok AI labeling, IG branded content, FTC). Confirm bio + caption
      defaults comply.
- [ ] **Brand contract template** at `shared/legal/contract-template.md`
      ready (or note that no brand deals yet — fine for day 0).

---

## Phase 1 — Soft Launch (Days 1–14)

The goal here is **identity-lock and audience-discovery, not monetization**.
Don't push affiliate links or newsletter signups in the first 7 days. Let
the algorithm warm up.

### Daily cadence (every day)

- [ ] **Post 2 TikToks/day** per the sprint matrix
- [ ] **Post 1 IG Reel** (re-shot caption, NOT cross-post with TikTok
      watermark)
- [ ] **3 IG Stories** with link sticker pointed at landing page
- [ ] **Reply to every comment in the first 60 minutes** after each post
- [ ] **Monitor for hostile comments** — block + ignore per protocol; don't
      argue
- [ ] **Pin spiciest pro-persona comment** as top comment on each post

### Every 2 days

- [ ] **Carousel post on IG** (8-slide opinion essay format for commentary
      personas; 8-slide aesthetic edit for lifestyle personas)
- [ ] **Track post performance** — log views, likes, follower delta in
      `analytics/daily.csv` (or whatever your tracking format is)

### End of week 1 (Day 7)

- [ ] **Mini post-mortem on first 14 posts.** Which structures hit? Which
      flopped? Which hooks performed?
- [ ] **Adjust days 8–14 plan** based on what's working. Lean into hits;
      cut formats that scored F/1K-views <2.
- [ ] **Confirm Soul ID identity-lock holding** across the week's content.
      Any drift? Retrain or tighten prompts.
- [ ] **Newsletter list count check.** Should be >50 from organic discovery
      already if any post hit. If 0, the bio isn't driving — fix.

### End of week 2 (Day 14)

- [ ] **Full post-mortem on 28 posts.** Rank by F/1K-views. Identify the
      top 3 hooks, top 3 structures, top 3 visual formats.
- [ ] **Update viral playbook v0.2** with what's working. Promote winning
      hooks into the primary library.
- [ ] **Generate next 28 days of content** using the proven formats.
- [ ] **Review platform policies** for any AI-labeling violations. Adjust
      if needed.

---

## Phase 2 — Validation + Monetization (Days 15–30)

Now we layer revenue surfaces in. Do NOT do all of this at once — sequence
matters.

### Day 15 — affiliate applications

- [ ] **Apply to 5 affiliate programs** in the niche. Use template from
      `brand-pitch-templates.md`.
- [ ] **Track applications** in `pitch-log.md`. Follow up after 7 days if
      no response.

### Day 18 — newsletter monetization layer

- [ ] **Newsletter live with 4-section template** (hook + 3 quick takes +
      lifestyle + CTA).
- [ ] **First send goes out.** Welcome subscribers, declare the persona's
      mission in 200 words, link to top 3 posts so far.
- [ ] **Affiliate links seeded** in the newsletter footer (whatever's
      approved by day 18).

### Day 21 — Stan.store + first product

- [ ] **First digital product live** ($15–25 PDF or guide). Built in Canva
      in <1 day.
- [ ] **Stan.store linked from bio** with: newsletter signup (top),
      digital product (middle), affiliate links (bottom).
- [ ] **Mention the product** in 1 TikTok and 1 IG Story per week — not
      more (audience hates a constant pitch).

### Day 24 — first brand outreach wave

- [ ] **Pitch 10 small brands in niche** via DM/email per
      `brand-pitch-templates.md`. Smaller brands first — they say yes
      faster, build the case study for bigger pitches.
- [ ] **Track every outreach** in `pitch-log.md` with date, brand, channel,
      outcome.

### Day 30 — gate decision

Run the gate analysis. Score the persona honestly:

| Metric | Green threshold | Yellow | Red |
|---|---|---|---|
| Combined followers | >5K | 2–5K | <2K |
| Newsletter subs | >300 | 100–300 | <100 |
| F/1K-views ratio | >5 | 2–5 | <2 |
| Affiliate sales (any) | ≥1 | 0 | 0 |
| Comment sentiment | >3/5 | 2–3 | <2 |
| Brand response rate | >5% | 2–5% | <2% |

### Decision

- **Mostly green** → Continue to Phase 3 (ramp). Increase posting cadence
  if sustainable, push monetization harder, scale brand outreach to 10+/wk.
- **Mostly yellow** → Run another 30-day cycle. Diagnose top 1–2 weak
  signals. Adjust playbook v0.3.
- **Mostly red** → Hard conversation. Diagnose:
  - Is the lane actually empty for a reason?
  - Is the persona look right but voice wrong, or vice versa?
  - Is engagement low because hooks are weak, or because audience doesn't
    exist?
  - Decide by Day 60 max: pivot or sunset. Don't drag a dying persona
    past 90 days.

---

## Common pitfalls (don't repeat Sierra's mistakes)

These are the failure modes most likely to bite. Pre-emptively avoid:

1. **Posting before identity is locked.** Generated 5 posts where she looks
   slightly different in each → audience subconsciously notices, follows
   don't compound. Always do the 20-image identity test before posting.
2. **Pretending to be human in the bio.** Massive legal risk + brand-deal
   killer. Disclose from post #1 — never retroactively.
3. **Politician composites or named real-public-figure content.** Hard
   stop. Different state laws, GitHub-search-discoverable, account-killer.
4. **Stapling adult monetization (Fanvue/OF) to a non-adult persona.** It's
   a strategic landmine — pick one lane.
5. **"Pay-for-access" or fake-credibility framing** ("I'm a journalist!" /
   "BTS with [politician]!") — wire fraud territory the moment money
   crosses state lines.
6. **Cross-promoting personas at launch.** The connection becomes the
   story. Independent traction first, cross-promotion only at scale and
   only if there's audience overlap.
7. **Building tooling before validating the persona.** Phase 2 tooling
   only kicks in after persona #1 hits Day 90 in green. Premature tooling
   has killed every small media operation in history.
8. **Reading the algorithm too early.** Day 7 metrics aren't predictive.
   Day 30 is the earliest gate. Don't pivot at day 10 because one post
   flopped.

---

## Templates / artifacts referenced

These should exist in `shared/` or `personas/sierra-frost/` and be reused
or adapted:

| Doc | Source |
|---|---|
| Persona bible template | `personas/sierra-frost/persona.md` |
| Viral playbook template | `personas/sierra-frost/viral-playbook.md` |
| Higgsfield prompt library template | `personas/sierra-frost/higgsfield-prompt-library.md` |
| Brand pitch templates | `personas/sierra-frost/brand-pitch-templates.md` |
| Contract template | `shared/legal/contract-template.md` (TODO) |
| Disclosure language | `shared/legal/disclosure-language.md` (TODO) |
| Brand-relationship CRM | `shared/brand-relationships.md` (TODO) |

When a template is missing (TODO above), persona #2's launch is the right
forcing function to write the first version. By persona #3, all templates
exist and launch is a matter of customization, not authoring.

---

## Versioning

Update this checklist after every persona launch. Each launch teaches
something — capture it as a checklist item, a new pitfall, or a refined
phase boundary. By persona #5, this doc is the most valuable IP in the
company.

**v0.1** — initial checklist. Codifies the Sierra-launch playbook for
reuse. Phase 0–2 + gate decision. Common-pitfall list seeded from Sierra's
near-misses.
