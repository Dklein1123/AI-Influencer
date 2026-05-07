"""Build the Lovable migration SQL that seeds Sierra Frost from our markdown.

Run:
    .venv/bin/python -m tools.sync.build_seed_sql > tools/sync/seed_lovable_001_initial.sql

Generates a single migration file that:

1. Adds an `allowed_emails` table + tightens RLS on all 9 Lovable-created
   tables to check `auth.jwt()->>'email' IN (SELECT email FROM allowed_emails)`.
2. Wipes the bogus "alpine digital muse" Sierra Frost seed (UUID
   11111111-...).
3. Inserts the real Sierra: 1 influencers row, 1 brand_bible row, all 50
   prompts rows from the persona module, ~14 ai_outputs rows from the
   generation-log.md (one per generation), and 4 content_items rows from
   our content-units/.

Hand the resulting SQL to Lovable as a single prompt:
    "Create a new migration file in supabase/migrations/ named
    `20260506_seed_sierra_real.sql` with this exact contents:
    [PASTE]"

Lovable runs it; the portal goes from empty → real Sierra in one shot.
"""

from __future__ import annotations

import datetime as dt
import importlib
import pathlib
import re
import sys
from typing import Iterable

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PERSONA_DIR = REPO_ROOT / "personas" / "sierra-frost"


# ---- helpers ------------------------------------------------------------

def sql_str(value: str | None) -> str:
    """Escape a Python string for embedding in a SQL literal."""
    if value is None:
        return "NULL"
    return "'" + value.replace("'", "''") + "'"


def sql_array(values: Iterable[str]) -> str:
    """Build a Postgres TEXT[] literal from a Python iterable."""
    inside = ",".join(sql_str(v).strip("'") for v in values)
    inside_quoted = ",".join(f'"{v}"' for v in values)
    return "'{" + inside_quoted + "}'"


def section(name: str) -> str:
    bar = "=" * (len(name) + 6)
    return f"\n-- {bar}\n-- -- {name} --\n-- {bar}\n"


# ---- main builder -------------------------------------------------------

def build() -> str:
    out: list[str] = []
    add = out.append

    # Header
    add(f"-- Sierra Frost seed migration (generated {dt.date.today().isoformat()})")
    add("-- Source: tools/sync/build_seed_sql.py")
    add("-- Run via: paste into Lovable as a new migration file")
    add("")
    add("BEGIN;")

    # 1. allowed_emails table
    add(section("Allowlist + tightened RLS"))
    add("""
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
""".strip())

    # 2. Tighten RLS on all 9 existing tables
    tables = [
        "profiles", "influencers", "brand_bible", "campaigns",
        "content_items", "prompts", "assets", "tasks", "ai_outputs",
    ]
    add("")
    for t in tables:
        add(f'-- {t}: replace permissive policies with allowlist check')
        add(f'DROP POLICY IF EXISTS "auth read {t}" ON {t};')
        add(f'DROP POLICY IF EXISTS "auth insert {t}" ON {t};')
        add(f'DROP POLICY IF EXISTS "auth update {t}" ON {t};')
        add(f'DROP POLICY IF EXISTS "auth delete {t}" ON {t};')
        add(f'CREATE POLICY "allowlisted access on {t}" ON {t} FOR ALL TO authenticated')
        add(f"  USING (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails))")
        add(f"  WITH CHECK (auth.jwt() ->> 'email' IN (SELECT email FROM allowed_emails));")
        add("")

    # 3. Wipe bogus Sierra seed
    add(section("Wipe bogus Sierra seed (Lovable's hallucinated 'alpine digital muse')"))
    bogus_id = "'11111111-1111-1111-1111-111111111111'"
    for t in ["ai_outputs", "tasks", "assets", "prompts", "content_items",
              "campaigns", "brand_bible"]:
        add(f"DELETE FROM {t} WHERE influencer_id = {bogus_id};")
    add(f"DELETE FROM influencers WHERE id = {bogus_id};")

    # 4. Insert the real Sierra
    sierra_uuid = "'a1e7f0c1-5f00-4c2a-9db1-5f0e7c5e7e01'"  # canonical, generate-once

    add(section("Real Sierra Frost — influencer row"))
    add(f"""
INSERT INTO influencers (
  id, name, handle, avatar_url, bio, personality, niche, tone,
  content_pillars, visual_style, audience, internal_notes, status
) VALUES (
  {sierra_uuid},
  {sql_str("Sierra Frost")},
  {sql_str("@sierrafrost.xo")},
  NULL,
  {sql_str("Sharp blonde from South Florida — Tomi Lahren / Brett Cooper coded. Common-sense commentary on culture, dating, fitness, and faith. Disclosed as a digital persona / AI-assisted; doesn't lead with disclosure but doesn't pretend to be human if asked. Sharp-tongued, polished, pointed, patriotic. Florida-raised, paying attention so you don't have to.")},
  {sql_str("Sharp older-sister voice. Confident not cute, dry not LOL, observational not preachy. Knows she's the hot blonde with takes — leans in. Florida warmth, soft conservative, never punching down at women. Sees the discourse and tells you what's actually going on while she pours wine.")},
  {sql_str("Conservative lifestyle / soft conservative commentary (Lane A — no policy wonk, no named-candidate endorsements)")},
  {sql_str("Confident, dry-witty, observational, deliberate pacing, slight downward inflection on landings, soft Florida warmth, US-neutral.")},
  {sql_array([
    "Pillar 1 — Commentary / Hot Takes (40%)",
    "Pillar 2 — Lifestyle / Soft Conservative (30%)",
    "Pillar 3 — Reaction / Make It Make Sense (20%)",
    "Pillar 4 — Newsletter Funnel / BTS (10%)",
  ])},
  {sql_str("Cinematic editorial. Sony A7IV, 50mm prime, f/2.0, soft natural lighting, golden hour or warm window light, neutral cream/beige palette, polished but candid. Wardrobe rotates A (tailored polish navy+cream), B (Florida casual white linen), C (cream Pilates), D (faith / Sunday modest), E (evening). Settings rotate S1 Scandi bedroom / S2 Palm Beach / S3 Classical exterior / S4 Pilates studio / S5 cafe-newsletter.")},
  {sql_str("Conservative women 22–45, US. Faith-curious, fitness-focused, dating-aware. Florida + Texas + Tennessee skews high. Buying audience for: conservative-niche affiliates, modest fashion, supplements, devotional products, faith adjacent.")},
  {sql_str("Higgsfield Soul ID: 87b6278b-8407-479d-b127-a8f2bc064ed1 (sierra-frost-v1, soul_2). Replicate LoRA v1: dklein1123/sierra-frost-v1:3225c5c843f49636dbd738c9a029e7f0058f7033145f15927ffe5443f9f82517 (mixed-mode — LoRA for full-body+frontal, Soul 2 for close-ups+profile, see tools/lora/v1-decision.md). ElevenLabs voice: TBD. Hedra: TBD.")},
  'active'
)
ON CONFLICT (id) DO NOTHING;
""".strip())

    # 5. brand_bible row
    voice_profile = (PERSONA_DIR / "voice-profile.md").read_text()

    def _section(md: str, header_prefix: str, end_at_pattern: str = r"\n##\s") -> str:
        """Extract everything from a heading line up to the next `## ` heading.

        `header_prefix` is matched as the start of a line (with re.MULTILINE).
        We don't anchor `$` because DOTALL makes that brittle — instead we
        consume the rest of the heading line, then capture the body
        non-greedily until `end_at_pattern` (default = next `## ` heading).
        """
        pattern = rf"^{re.escape(header_prefix)}[^\n]*\n(?P<body>.*?)(?={end_at_pattern}|\Z)"
        m = re.search(pattern, md, re.MULTILINE | re.DOTALL)
        return m.group("body").strip() if m else ""

    def _subsection(md: str, header_prefix: str) -> str:
        """Like _section but stops at next `### ` (subsection) too."""
        return _section(md, header_prefix, end_at_pattern=r"\n###\s|\n##\s")

    personality_rules = (
        _section(voice_profile, "## 1. One-line voice fingerprint")
        + "\n\n"
        + _section(voice_profile, "## 3. Cadence rules")
    )
    caption_style = _section(voice_profile, "## 7. Caption structures by platform")
    visual_rules = _section(voice_profile, "## 8. On-screen text overlay (TikTok)")
    posing_rules = "Polished editorial; never harsh studio; warm friendly expression unless the pose says otherwise. See higgsfield-prompt-library.md §7 for per-template poses (50 templates)."
    negative_prompts = "deformed hands, extra fingers, distorted face, asymmetric eyes, plastic skin, overly smoothed skin, uncanny valley, harsh studio lighting, neon colors, heavy contour, drag-style makeup, dark lipstick, gothic aesthetic, alt fashion, streetwear logos, Y2K aesthetic, club wear, lingerie, bikini, nudity, named celebrities, named politicians, recognizable government interiors, identifiable real people, MAGA hat with legible text, political signage with legible text, election year graphics, partisan iconography, weapons, drugs, alcohol bottles in foreground, watermarks, text overlays, low resolution, blurry, oversaturated"
    example_prompts = "See higgsfield-prompt-library.md and prompts table — 50 hand-crafted templates spanning P1–P50 across pillars 1/2/3/4."
    content_boundaries = "Lane A — conservative lifestyle commentator. NO named candidate endorsements, NO policy wonk specifics (immigration numbers, tax rates), NO race-coded content, NO punching down at other women, NO content with named real public figures, NO denominational debates, NO platform-violating sexual content."
    tone_guidelines = (
        _section(voice_profile, "## 2. The voice as a vector")
        + "\n\n"
        + _section(voice_profile, "## 12. The five narrative arcs")
    )
    would_say = _subsection(voice_profile, "### Allow (use freely, in proportion)")
    would_never_say = (
        _subsection(voice_profile, "### Block (never appear in output)")
        + "\n\n"
        + _subsection(voice_profile, "### Block — content / political")
        + "\n\n"
        + _section(voice_profile, "## 13. Things Sierra would never say")
    )

    add(section("Real Sierra Frost — brand_bible row"))
    add(f"""
INSERT INTO brand_bible (
  influencer_id, personality_rules, caption_style, visual_rules,
  posing_rules, negative_prompts, example_prompts, content_boundaries,
  tone_guidelines, would_say, would_never_say
) VALUES (
  {sierra_uuid},
  {sql_str(personality_rules)},
  {sql_str(caption_style)},
  {sql_str(visual_rules)},
  {sql_str(posing_rules)},
  {sql_str(negative_prompts)},
  {sql_str(example_prompts)},
  {sql_str(content_boundaries)},
  {sql_str(tone_guidelines)},
  {sql_str(would_say)},
  {sql_str(would_never_say)}
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
""".strip())

    # 6. 50 prompts
    add(section("Real Sierra Frost — 50 image/video prompt templates"))
    sys.path.insert(0, str(REPO_ROOT))
    sierra = importlib.import_module("tools.generation.sierra_frost")
    for tid, t in sierra.TEMPLATES.items():
        full_prompt = sierra.build_prompt(tid)
        title = f"{tid} — {t['pose'][:50]}"
        category = "image" if t["kind"] in ("tiktok", "carousel", "hero") else "video"
        notes = (
            f"Pillar {t['pillar']} · Wardrobe {t['wardrobe']} · Setting {t['setting']} · "
            f"Shot: {t['shot']} · Motion: {t['motion']}"
        )
        tags = [
            f"pillar-{t['pillar']}",
            f"wardrobe-{t['wardrobe']}",
            f"setting-{t['setting']}",
            f"kind-{t['kind']}",
            tid,
        ]
        add(f"""
INSERT INTO prompts (influencer_id, title, category, body, notes, tags)
VALUES ({sierra_uuid}, {sql_str(title)}, {sql_str(category)}, {sql_str(full_prompt)}, {sql_str(notes)}, {sql_array(tags)});""".strip())

    # 7. ai_outputs from generation log (~14 entries)
    add(section("Real Sierra Frost — ai_outputs from generation log"))

    log_text = (PERSONA_DIR / "generation-log.md").read_text()
    # Parse entries shaped like:
    #   ### P1 — title
    #   - job_id: `xyz`
    #   - seed: `123`
    #   ...
    entry_re = re.compile(
        r"(?s)### (?P<tid>P\d+|PROFILE)[^\n]*\n\n"  # title
        r"(?:.*?- job_id:\s*`(?P<job>[a-f0-9-]+)`)?"
        r"(?:.*?- seed:\s*`(?P<seed>[^`]+)`)?"
        r"(?:.*?- pose:\s*(?P<pose>[^\n]+))?"
        r"(?:.*?- result:\s*(?P<result>[^\n]+))?"
        r"(?:.*?- saved:\s*`(?P<saved>[^`]+)`)?"
        r"(?:.*?- source:\s*(?P<src>https?://[^\s]+))?"
    )
    seen = set()
    count = 0
    for m in entry_re.finditer(log_text):
        tid = m.group("tid")
        job = m.group("job")
        if not job or job in seen:
            continue
        seen.add(job)
        seed = m.group("seed") or ""
        pose = (m.group("pose") or "").strip()
        result = (m.group("result") or "").strip()
        src = (m.group("src") or "").strip()
        saved = (m.group("saved") or "").strip()
        title = f"{tid} generation — {pose[:60] if pose else 'image'}"
        content = (
            f"job_id: {job}\nseed: {seed}\npose: {pose}\nresult: {result}\n"
            f"output: {src}\nlocal: {saved}"
        )
        tags = [tid, "soul_2", "higgsfield", "image"]
        add(f"""
INSERT INTO ai_outputs (influencer_id, kind, title, content, source_prompt, tags, starred)
VALUES ({sierra_uuid}, 'image', {sql_str(title)}, {sql_str(content)}, {sql_str(tid)}, {sql_array(tags)}, false);""".strip())
        count += 1
    add(f"-- {count} ai_outputs rows inserted from generation-log.md")

    # 8. content_items from our hand-written content units
    add(section("Real Sierra Frost — 4 content units"))
    units_dir = PERSONA_DIR / "content-units"
    if units_dir.is_dir():
        for unit_md in sorted(units_dir.glob("*.md")):
            text = unit_md.read_text()
            tid = re.search(r"P\d+", unit_md.name)
            tid = tid.group(0) if tid else "P?"
            # Extract pillar from the first table or "Pillar:" line
            pillar_m = re.search(r"\*\*Pillar:\*\*\s*(\d+)", text)
            pillar = pillar_m.group(1) if pillar_m else "1"
            # Take TikTok caption
            tt_m = re.search(r"### TikTok[^\n]*\n+>\s*(.+?)(?=\n\n|###|$)", text, re.DOTALL)
            caption = tt_m.group(1).strip() if tt_m else ""
            # Recommended hook (the one marked Recommended)
            hook_m = re.search(r"\*\*Recommended:\*\*\s*\w\.\s*(.+?)\.", text)
            hook = ""
            if hook_m:
                # Find the actual hook text from the table
                hooks_block = re.search(r"\| A \|\s*\*\*([^\*]+)\*\*", text)
                if hooks_block:
                    hook = hooks_block.group(1).strip()
            title = f"{tid} — content unit ({unit_md.stem})"
            tags = [tid, f"pillar-{pillar}", "ready-to-post"]
            add(f"""
INSERT INTO content_items (influencer_id, title, body, caption, hook, type, platform, status, tags)
VALUES ({sierra_uuid}, {sql_str(title)}, {sql_str(text[:8000])}, {sql_str(caption)}, {sql_str(hook)}, 'tiktok', 'tiktok', 'approved', {sql_array(tags)});""".strip())

    add("")
    add("COMMIT;")
    add("")
    return "\n".join(out)


def main() -> int:
    print(build())
    return 0


if __name__ == "__main__":
    sys.exit(main())
