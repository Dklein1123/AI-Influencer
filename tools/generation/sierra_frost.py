"""Sierra Frost — persona-specific constants and prompt templates.

Single source of truth for Sierra's generation parameters. Mirrors the
spec in personas/sierra-frost/higgsfield-prompt-library.md. When you
update one, update both — or refactor to load from the markdown.
"""

NAME = "sierra-frost"
DISPLAY_NAME = "Sierra Frost"
SOUL_ID_ENV_VAR = "SIERRA_SOUL_ID"

# Universal blocks paste into every prompt.
#
# DESIGN NOTE (2026-05-07 anti-slop refactor):
# Flux Dev is guidance-distilled toward "professional / pretty." Default
# prompts produce AI-slop: airbrushed skin, perfect symmetry, beauty light.
# We actively prompt DOWN toward "snapshot" not "photo." Specific anti-slop
# moves embedded below: filename-hack ("IMG_2222.HEIC"), explicit asymmetry
# + skin-texture language, indoor/mixed-light over golden-hour, "amateur
# snapshot photo" trigger from the Spectrum0001 Civitai community LoRA, and
# critically — NO photographer/lens/aperture jargon (those produce
# editorial polish). See docs/research/realism-stack.md for the full
# rationale and source list.

BASE_BLOCK = (
    "25 year old woman, blonde mid-length hair with soft beachy waves and "
    "a few flyaway strands at the hairline, light blue-green eyes with "
    "slight asymmetry between left and right, lightly-tanned skin with "
    "visible pores on the nose and cheeks, peach fuzz catching the light, "
    "faint under-eye circles, mild T-zone shine, slight nostril asymmetry, "
    "small natural lip line, dainty gold jewelry, fit Pilates body but not "
    "overly defined, unposed expression unless otherwise specified, "
    "looking slightly off-camera, candid not posed"
)

# Flux Dev largely ignores negative prompts at distilled CFG=1 (which is
# what we use). The functional way to "subtract" is via positive-prompt
# language ("amateur, not editorial"). This negative is here for backends
# that DO use it (Higgsfield Soul 2) and for documentation; Replicate
# Flux runs without applying it unless we wire DynamicThresholding + true
# CFG, which costs 2x for marginal gain.
NEGATIVE_PROMPT = (
    "airbrushed, plastic skin, smooth skin, glossy, wax figure, "
    "beauty filter, instagram filter, perfect symmetry, perfectly symmetric "
    "eyes, retouched, professional studio lighting, softbox lighting, "
    "ring light, ad campaign, magazine cover, 3d render, cgi, illustration, "
    "drawn, painted, AI-generated look, deformed hands, extra fingers, "
    "neon colors, drag-style makeup, dark lipstick, gothic, alt fashion, "
    "streetwear logos, Y2K aesthetic, club wear, lingerie, bikini, nudity, "
    "named celebrities, named politicians, recognizable government interiors, "
    "MAGA hat with legible text, partisan iconography, weapons, drugs, "
    "alcohol bottles in foreground, watermarks, text overlays, low resolution, "
    "blurry, oversaturated"
)

# STYLE_SUFFIX is now the SNAPSHOT scaffold, not editorial scaffold.
# Every line here is calibrated to break Flux's beauty-mode default.
STYLE_SUFFIX = (
    "amateur snapshot photo, taken on iPhone 15 Pro, casual candid framing, "
    "slightly underexposed, mixed indoor lighting (warm tungsten with cool "
    "window daylight), motion-soft not bokeh-soft, IMG_2231.HEIC, "
    "washed-out neutral white balance, mild jpeg compression, faint sensor "
    "noise, posted to a friend's instagram story, no professional retouching, "
    "not a model shoot, no studio lighting"
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
    "S6": (  # Car Interior — Driver's Seat (Range Rover / SUV style)
        "inside the driver's seat of a clean modern SUV interior (Range "
        "Rover / Tahoe coded, cream leather, no badge visible), parked "
        "or about to drive, hands resting on steering wheel or in lap, "
        "soft afternoon daylight through windshield, faint reflection "
        "on glass, blurred parking lot or driveway visible behind, no "
        "other people in frame"
    ),
    "S7": (  # Bed — Casual / Phone-in-hand
        "lying or sitting up on a made bed, white linen bedding, "
        "phone in hand or face-down on duvet, soft afternoon window "
        "light, hair down loose, casual at-home vibe, no shoes, "
        "neutral palette of cream and warm beige"
    ),
    "S8": (  # Bathroom — Skincare / Getting Ready
        "at a clean modern bathroom vanity, marble counter, large "
        "framed mirror with warm bulbs, skincare bottles arranged "
        "neatly (no legible labels), soft warm overhead light, neutral "
        "stone palette, towel folded nearby, getting-ready energy"
    ),
    "S9": (  # Kitchen — Morning Coffee / Casual Counter
        "at a bright modern kitchen counter, marble or quartz island, "
        "ceramic mug of coffee in hand, oat milk carton or french press "
        "visible in soft focus, morning light through tall window, "
        "muted greige cabinetry behind, no other people in frame, "
        "candid morning-routine atmosphere"
    ),
    "S10": (  # Outdoor Walking — Phone-Selfie POV
        "walking on a tree-lined sidewalk or quiet street, holding "
        "phone in selfie position, slight motion blur on hand, golden "
        "afternoon light filtering through trees, neutral residential "
        "background, no traffic visible, candid handheld feel"
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
    # Block 6 — Natural settings (P51-P57) — added when lipsync went live so
    # Sierra has talking-head templates beyond bedroom/cafe. These are the
    # canonical "in car / in bed / getting ready / walking" Sierra-talks-to-
    # camera setups.
    "P51": {"setting": "S6", "wardrobe": "A", "shot": "medium close-up centered driver-seat angle", "motion": "static lock-off, shot mounted on dash or passenger seat", "pose": "in driver's seat, looking sideways toward camera mid-thought, hand on steering wheel, slight half-smile, Tesla / Range Rover interior", "pillar": 1, "kind": "tiktok"},
    "P52": {"setting": "S7", "wardrobe": "C", "shot": "medium close-up", "motion": "static lock-off, propped phone selfie angle", "pose": "lying on bed propped on elbow, phone in opposite hand, hair spread on pillow, deadpan dry expression, no shoes, casual at-home", "pillar": 1, "kind": "tiktok"},
    "P53": {"setting": "S8", "wardrobe": "neutral", "shot": "medium close-up bathroom mirror angle", "motion": "static lock-off, slight handheld sway", "pose": "applying serum or doing skincare at vanity mirror, hair clipped back, mid-routine pause to look at camera with knowing dry expression", "pillar": 2, "kind": "tiktok"},
    "P54": {"setting": "S9", "wardrobe": "C", "shot": "medium close-up kitchen counter angle", "motion": "static lock-off", "pose": "leaning on kitchen island holding ceramic mug, mid-sip pause, dry sideways glance, morning-routine vibe, hair loose", "pillar": 2, "kind": "tiktok"},
    "P55": {"setting": "S10", "wardrobe": "B", "shot": "selfie phone-cam medium close-up", "motion": "loose handheld, slight walking motion in frame", "pose": "walking and holding phone in selfie pose, mid-thought facial expression, hair moving slightly with motion, golden hour", "pillar": 2, "kind": "tiktok"},
    "P56": {"setting": "S6", "wardrobe": "C", "shot": "medium close-up driver-seat angle", "motion": "static lock-off, parked car", "pose": "parked in driveway / parking lot, phone propped on dash, post-Pilates / post-errand look, talking to camera with dry confessional energy", "pillar": 1, "kind": "tiktok"},
    "P57": {"setting": "S7", "wardrobe": "neutral", "shot": "medium close-up handheld phone-cam angle", "motion": "static lock-off, propped phone", "pose": "sitting cross-legged in bed at night, hair down, soft warm bedside lamp light, talking to camera with confessional / vulnerable register-shift energy", "pillar": 1, "kind": "tiktok"},
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
