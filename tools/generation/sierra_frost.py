"""Sierra Frost — persona-specific constants and prompt templates.

Single source of truth for Sierra's generation parameters. Mirrors the
spec in personas/sierra-frost/higgsfield-prompt-library.md. When you
update one, update both — or refactor to load from the markdown.
"""

NAME = "sierra-frost"
DISPLAY_NAME = "Sierra Frost"
SOUL_ID_ENV_VAR = "SIERRA_SOUL_ID"

# Universal blocks paste into every prompt.

BASE_BLOCK = (
    "24-year-old woman, blonde mid-length hair with soft beachy waves, "
    "light blue-green eyes, glowy lightly-tanned skin, full lips with "
    "glossy nude makeup, polished natural makeup with soft contour and "
    "warm neutral eyeshadow, dainty gold jewelry, hourglass figure, fit "
    "Pilates body, warm friendly expression unless otherwise specified"
)

NEGATIVE_PROMPT = (
    "deformed hands, extra fingers, distorted face, asymmetric eyes, "
    "plastic skin, overly smoothed skin, uncanny valley, harsh studio "
    "lighting, neon colors, heavy contour, drag-style makeup, dark "
    "lipstick, gothic aesthetic, alt fashion, streetwear logos, Y2K "
    "aesthetic, club wear, lingerie, bikini, nudity, named celebrities, "
    "named politicians, recognizable government interiors, identifiable "
    "real people, MAGA hat with legible text, political signage with "
    "legible text, election year graphics, partisan iconography, weapons, "
    "drugs, alcohol bottles in foreground, watermarks, text overlays, "
    "low resolution, blurry, oversaturated"
)

STYLE_SUFFIX = (
    "shot on Sony A7IV, 50mm prime lens, shallow depth of field f/2.0, "
    "soft natural lighting, golden hour or warm window light, neutral "
    "color palette, candid editorial composition, cinematic but warm, "
    "polished but not stiff, high detail, ultra realistic photographic "
    "quality"
)

# Aspect ratio per output type.
ASPECT = {
    "tiktok": "9:16",
    "reel": "9:16",
    "carousel": "4:5",
    "hero": "16:9",
}

# ---- Wardrobe blocks (A-E) ----

WARDROBE = {
    "A": (  # Tailored Polish
        "wearing fitted navy midi dress with cream cropped blazer, nude "
        "pointed-toe heels, dainty gold necklace, small camel structured "
        "handbag, hair styled in soft waves"
    ),
    "B": (  # Florida Casual
        "wearing white linen sundress with thin straps, beige espadrille "
        "sandals, gold layered necklaces, hair air-dried in soft beachy "
        "waves, no jacket"
    ),
    "C": (  # Athleisure
        "wearing matching neutral set: cream sports bra and high-waisted "
        "bike shorts, Hoka or On running sneakers, hair pulled into low "
        "ponytail, dewy fresh face, small gold hoops"
    ),
    "D": (  # Faith / Sunday
        "wearing modest knee-length dress in soft cream or dusty pink, "
        "fitted but not tight, three-quarter sleeves, simple dainty "
        "cross necklace, neutral nude heels, soft natural makeup, hair "
        "half-up"
    ),
    "E": (  # Evening
        "wearing fitted satin slip dress in deep navy, classic stiletto "
        "heels, gold statement earrings, sleek straight hair or soft glam "
        "waves, polished evening makeup with subtle smokey eye"
    ),
    "neutral": "",  # No wardrobe focus — for tight close-ups and inserts.
}

# ---- Setting blocks (S1-S5) ----

SETTINGS = {
    "S1": (  # Sunlit Scandi-Neutral Bedroom
        "in a bright Scandinavian-style bedroom, white linen bedding, "
        "oak nightstand, floor-to-ceiling window with sheer curtains, "
        "eucalyptus plant in clay pot, soft morning light streaming "
        "through window, neutral palette of cream beige and warm wood"
    ),
    "S2": (  # South Florida Exterior
        "on a Palm Beach waterfront walkway, palm trees in background, "
        "white classical-style architecture, calm turquoise water visible "
        "behind, golden hour light, pastel sky, polished resort "
        "aesthetic, no other recognizable people in frame"
    ),
    "S3": (  # Classical American Architecture (exterior only, no real people)
        "on the steps outside a marble-columned classical building, "
        "Corinthian columns visible behind, American flag faintly visible "
        "in distant background (no legible text), bright clear blue sky, "
        "dramatic shadow lines on stone, no other identifiable people in "
        "frame, exterior only"
    ),
    "S4": (  # Boutique Pilates Studio / Gym
        "inside a bright minimalist Pilates studio, reformer machine "
        "visible, large windows with morning light, warm wood floor, "
        "white walls with subtle ribbed-wood detail, neutral palette, "
        "polished wellness aesthetic"
    ),
    "S5": (  # Coffee Shop / Newsletter Workspace
        "at a small marble cafe table near a window, MacBook open with a "
        "clean writing app on screen (no legible text), latte in ceramic "
        "cup, leather journal beside laptop, soft window light, blurred "
        "warm interior in background, intimate productive atmosphere"
    ),
}

# ---- Templates P1-P50 (mirrors viral-playbook organization) ----
# Each template: setting, wardrobe, shot, motion, pose, pillar, output_kind

TEMPLATES = {
    # Block 1 — Talking head / commentary B-roll (P1-P15)
    "P1":  {"setting": "S1", "wardrobe": "A", "shot": "medium close-up", "motion": "static lock-off, no camera movement, subject framed center", "pose": "sitting at edge of bed, soft confident expression, looking off-camera", "pillar": 1, "kind": "tiktok"},
    "P2":  {"setting": "S5", "wardrobe": "B", "shot": "medium shot", "motion": "slow dolly push toward subject's face, ending on tight close-up", "pose": "typing on laptop, looking up at camera mid-thought, half-smile", "pillar": 1, "kind": "tiktok"},
    "P3":  {"setting": "S1", "wardrobe": "neutral", "shot": "tight close-up", "motion": "slow dolly push toward subject's face", "pose": "looking directly to camera, dry knowing expression", "pillar": 1, "kind": "tiktok"},
    "P4":  {"setting": "S5", "wardrobe": "A", "shot": "over-the-shoulder", "motion": "static lock-off, no camera movement", "pose": "writing in leather journal, latte beside her, contemplative", "pillar": 1, "kind": "tiktok"},
    "P5":  {"setting": "S1", "wardrobe": "D", "shot": "wide environmental", "motion": "slow dolly pull back from medium shot to wide environmental reveal", "pose": "sitting cross-legged on bed with open journal, morning light, serene", "pillar": 2, "kind": "tiktok"},
    "P6":  {"setting": "S4", "wardrobe": "C", "shot": "medium close-up", "motion": "static lock-off", "pose": "post-workout, slight glow, water bottle in hand, casual confident", "pillar": 2, "kind": "tiktok"},
    "P7":  {"setting": "S2", "wardrobe": "B", "shot": "cowboy shot mid-thigh up", "motion": "loose handheld follow, subject walking forward, slight natural sway", "pose": "walking toward camera, hair moving in breeze, soft smile, golden hour", "pillar": 2, "kind": "tiktok"},
    "P8":  {"setting": "S1", "wardrobe": "A", "shot": "tight close-up", "motion": "slow dolly push toward subject's face", "pose": "pearl-strand earring detail, soft side-lit, neutral expression", "pillar": 1, "kind": "tiktok"},
    "P9":  {"setting": "S5", "wardrobe": "neutral", "shot": "detail insert close-up", "motion": "static lock-off", "pose": "hands typing on laptop, gold ring and dainty bracelet visible, journal beside", "pillar": 1, "kind": "tiktok"},
    "P10": {"setting": "S1", "wardrobe": "C", "shot": "medium shot", "motion": "smooth 90-degree arc around subject, golden hour rim light", "pose": "sitting on edge of bed lacing sneakers, morning routine vibe", "pillar": 2, "kind": "tiktok"},
    "P11": {"setting": "S2", "wardrobe": "B", "shot": "wide environmental", "motion": "static lock-off", "pose": "small in frame, palm trees dominant, walking away from camera, candid", "pillar": 2, "kind": "tiktok"},
    "P12": {"setting": "S5", "wardrobe": "A", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "looking up from laptop directly to camera, faint smile", "pillar": 4, "kind": "tiktok"},
    "P13": {"setting": "S1", "wardrobe": "D", "shot": "over-the-shoulder", "motion": "static lock-off", "pose": "open devotional book on lap (no legible text on page), soft window light", "pillar": 2, "kind": "tiktok"},
    "P14": {"setting": "S4", "wardrobe": "C", "shot": "full body", "motion": "slow dolly pull back", "pose": "mid-Pilates form on reformer, controlled and graceful, not strained", "pillar": 2, "kind": "tiktok"},
    "P15": {"setting": "S1", "wardrobe": "E", "shot": "tight close-up", "motion": "static lock-off", "pose": "getting ready at vanity, lipstick mid-application, mirror reflection visible", "pillar": 2, "kind": "tiktok"},
    # Block 2 — Lifestyle / Pillar 2 (P16-P30)
    "P16": {"setting": "S2", "wardrobe": "B", "shot": "cowboy shot mid-thigh up", "motion": "smooth 90-degree arc around subject", "pose": "Worth Avenue boutique window in soft background, polished day-out", "pillar": 2, "kind": "tiktok"},
    "P17": {"setting": "S5", "wardrobe": "A", "shot": "medium shot", "motion": "loose handheld follow", "pose": "entering cafe with leather tote, sunglasses pushed up on head", "pillar": 2, "kind": "tiktok"},
    "P18": {"setting": "S1", "wardrobe": "D", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "Sunday morning getting ready, cross necklace detail, soft golden light", "pillar": 2, "kind": "tiktok"},
    "P19": {"setting": "S4", "wardrobe": "C", "shot": "cowboy shot mid-thigh up", "motion": "static lock-off", "pose": "stretching at barre, post-class, tied-up hair, dewy skin", "pillar": 2, "kind": "tiktok"},
    "P20": {"setting": "S2", "wardrobe": "B", "shot": "full body", "motion": "loose handheld follow, subject walking forward", "pose": "walking past palms with iced coffee in hand, candid Florida day", "pillar": 2, "kind": "tiktok"},
    "P21": {"setting": "S1", "wardrobe": "neutral", "shot": "detail insert close-up", "motion": "static lock-off", "pose": "closet detail: rows of neutral dresses, gold jewelry tray, organized polished", "pillar": 2, "kind": "tiktok"},
    "P22": {"setting": "S5", "wardrobe": "A", "shot": "medium shot", "motion": "slow dolly push toward subject's face", "pose": "writing in journal at sidewalk cafe table, golden hour, palm shadow", "pillar": 4, "kind": "tiktok"},
    "P23": {"setting": "S1", "wardrobe": "C", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "morning routine: hair up in claw clip, applying serum, no makeup", "pillar": 2, "kind": "tiktok"},
    "P24": {"setting": "S2", "wardrobe": "E", "shot": "wide environmental", "motion": "slow dolly pull back from medium shot to wide environmental reveal", "pose": "golden hour at marina with white yachts behind, classy evening", "pillar": 2, "kind": "tiktok"},
    "P25": {"setting": "S1", "wardrobe": "A", "shot": "cowboy shot mid-thigh up", "motion": "smooth 90-degree arc around subject", "pose": "mirror outfit check, full polish, confident, fit-check energy", "pillar": 2, "kind": "tiktok"},
    "P26": {"setting": "S5", "wardrobe": "A", "shot": "over-the-shoulder", "motion": "static lock-off", "pose": "laptop screen shows newsletter draft (no legible text), intentional newsletter-funnel content", "pillar": 4, "kind": "tiktok"},
    "P27": {"setting": "S4", "wardrobe": "C", "shot": "medium shot", "motion": "slow dolly push toward subject's face", "pose": "drinking from glass water bottle, content post-workout", "pillar": 2, "kind": "tiktok"},
    "P28": {"setting": "S3", "wardrobe": "D", "shot": "cowboy shot mid-thigh up", "motion": "loose handheld follow", "pose": "walking up church steps in modest dress, hand on Bible-style journal (no legible text)", "pillar": 2, "kind": "tiktok"},
    "P29": {"setting": "S1", "wardrobe": "E", "shot": "full body", "motion": "slow dolly pull back", "pose": "getting ready for evening event, full mirror, polished glam", "pillar": 2, "kind": "tiktok"},
    "P30": {"setting": "S5", "wardrobe": "B", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "laughing softly at something off-camera, latte in hand, natural", "pillar": 2, "kind": "tiktok"},
    # Block 3 — Reaction / "Looking at camera" (P31-P40)
    "P31": {"setting": "S1", "wardrobe": "neutral", "shot": "tight close-up", "motion": "static lock-off", "pose": "eyebrow raise, slight head tilt, you're-kidding-right expression", "pillar": 3, "kind": "tiktok"},
    "P32": {"setting": "S1", "wardrobe": "C", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "sitting on bed mid-coffee sip, pause, dry sideways glance to camera", "pillar": 3, "kind": "tiktok"},
    "P33": {"setting": "S5", "wardrobe": "A", "shot": "medium close-up", "motion": "static lock-off", "pose": "mid-typing, looks up over laptop, dry really? expression", "pillar": 3, "kind": "tiktok"},
    "P34": {"setting": "S1", "wardrobe": "D", "shot": "tight close-up", "motion": "static lock-off", "pose": "soft eye-roll, knowing patient expression", "pillar": 3, "kind": "tiktok"},
    "P35": {"setting": "S2", "wardrobe": "B", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "sunglasses lowered to look at camera over them, knowing smile", "pillar": 3, "kind": "tiktok"},
    "P36": {"setting": "S1", "wardrobe": "neutral", "shot": "medium shot", "motion": "slow dolly push toward subject's face", "pose": "slow head shake, slight smirk, arms crossed, we're-not-doing-this energy", "pillar": 3, "kind": "tiktok"},
    "P37": {"setting": "S5", "wardrobe": "A", "shot": "tight close-up", "motion": "static lock-off", "pose": "chin in hand at table, deadpan straight-to-camera, go-on energy", "pillar": 3, "kind": "tiktok"},
    "P38": {"setting": "S1", "wardrobe": "C", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "mid-laugh that turns into wait-you're-serious expression", "pillar": 3, "kind": "tiktok"},
    "P39": {"setting": "S2", "wardrobe": "B", "shot": "medium shot", "motion": "loose handheld follow, subject walking forward", "pose": "walking toward camera, small smirk, let-me-explain energy", "pillar": 3, "kind": "tiktok"},
    "P40": {"setting": "S1", "wardrobe": "E", "shot": "tight close-up", "motion": "slow dolly push toward subject's face", "pose": "slow blink, deadpan, the-audacity energy", "pillar": 3, "kind": "tiktok"},
    # Block 4 — Newsletter funnel (P41-P45)
    "P41": {"setting": "S5", "wardrobe": "A", "shot": "over-the-shoulder", "motion": "slow dolly push toward subject's face", "pose": "writing newsletter, Sunday morning energy", "pillar": 4, "kind": "tiktok"},
    "P42": {"setting": "S1", "wardrobe": "D", "shot": "medium shot", "motion": "static lock-off", "pose": "laptop in lap, leather journal beside, Sunday newsletter day atmosphere", "pillar": 4, "kind": "tiktok"},
    "P43": {"setting": "S5", "wardrobe": "neutral", "shot": "detail insert close-up", "motion": "static lock-off", "pose": "laptop screen showing clean writing-app interface (no legible text), morning latte beside", "pillar": 4, "kind": "tiktok"},
    "P44": {"setting": "S1", "wardrobe": "C", "shot": "medium close-up", "motion": "slow dolly push toward subject's face", "pose": "cozy writing-in-bed energy, pen and journal, soft natural", "pillar": 4, "kind": "tiktok"},
    "P45": {"setting": "S5", "wardrobe": "A", "shot": "medium shot", "motion": "slow dolly pull back", "pose": "full sidewalk-cafe scene, MacBook plus journal plus latte, golden hour, the writer-girl archetype shot", "pillar": 4, "kind": "tiktok"},
    # Block 5 — Hero shots (P46-P50)
    "P46": {"setting": "S2", "wardrobe": "A", "shot": "medium close-up", "motion": "smooth 90-degree arc around subject, golden hour rim light", "pose": "golden hour, palm shadow on white wall behind, polished editorial", "pillar": 2, "kind": "hero"},
    "P47": {"setting": "S1", "wardrobe": "A", "shot": "medium shot", "motion": "static lock-off", "pose": "sitting at edge of bed, full polish, soft window light, hero shot composition", "pillar": 2, "kind": "hero"},
    "P48": {"setting": "S3", "wardrobe": "A", "shot": "cowboy shot mid-thigh up", "motion": "slow dolly pull back", "pose": "steps of marble building exterior, golden afternoon, polished editorial", "pillar": 2, "kind": "hero"},
    "P49": {"setting": "S2", "wardrobe": "E", "shot": "full body", "motion": "smooth 90-degree arc around subject", "pose": "sunset marina, classic red or navy evening dress, hero shot", "pillar": 2, "kind": "hero"},
    "P50": {"setting": "S1", "wardrobe": "D", "shot": "medium close-up", "motion": "static lock-off", "pose": "Sunday morning hero, soft pastel light, dainty cross, thoughtful but warm expression", "pillar": 2, "kind": "hero"},
}


def build_prompt(template_id: str) -> str:
    """Compose the full text prompt for a template."""
    if template_id not in TEMPLATES:
        raise KeyError(
            f"Unknown template '{template_id}'. Valid: P1..P50."
        )
    t = TEMPLATES[template_id]
    parts = [
        BASE_BLOCK,
        WARDROBE[t["wardrobe"]],
        SETTINGS[t["setting"]],
        f"shot type: {t['shot']}",
        f"camera motion: {t['motion']}",
        f"action: {t['pose']}",
        STYLE_SUFFIX,
    ]
    return ", ".join(p for p in parts if p)


def aspect_for(template_id: str) -> str:
    """Aspect ratio derived from template's output kind."""
    return ASPECT[TEMPLATES[template_id]["kind"]]
