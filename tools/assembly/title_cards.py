"""Render branded title cards for Sierra's 3-bit rotation.

Each card: 1.5s, 1080x1920, distinct plate color per bit + identical
typography. Serves as the follower-first recognition asset per
voice-profile §5.6 + viral-playbook §0a.

Bits:
    sierra_reads        — cream plate, dating commentary
    calling_my_dad      — warm-amber plate, faith / trad-family
    brad_finance        — slate-blue plate, dating + culture absurdity

Animation: 0.25s fade-in, 1.0s hold, 0.25s fade-out — minimal, brand-
consistent. Tone sting per bit (different timbre so audience learns).

Usage:
    python -m tools.assembly.title_cards            # render all 3
    python -m tools.assembly.title_cards sierra_reads
    python -m tools.assembly.title_cards --no-sting
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT_DIR = pathlib.Path(__file__).resolve().parent / "title_cards"

FONT_PATH = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Black.ttf"
DUR = 1.5
W, H = 1080, 1920
FPS = 30


BITS = {
    "sierra_reads": {
        "plate":   "0xF5EFE3",   # warm cream
        "text":    "0x1A1A1A",   # near-black
        "accent":  "0xC8856A",   # terracotta accent rule
        "lines":   ("SIERRA READS", "HINGE BIOS"),
        "tag":     "EP. {ep}",
        "sting_hz": 760,         # bright bell tone
    },
    "calling_my_dad": {
        "plate":   "0xE8B97B",   # warm amber
        "text":    "0x2A1810",
        "accent":  "0x6B3E1A",
        "lines":   ("CALLING MY DAD", "ABOUT…"),
        "tag":     "EP. {ep}",
        "sting_hz": 450,         # phone-buzz adjacent
    },
    "brad_finance": {
        "plate":   "0x4A6B85",   # slate blue (newscaster)
        "text":    "0xF5F5F5",
        "accent":  "0xD4B95E",   # gold ticker
        "lines":   ("BRAD FROM FINANCE", "WEIGHS IN"),
        "tag":     "BREAKING",
        "sting_hz": 620,         # mock-news cue
    },
    "sierra_apologist": {
        "plate":   "0xD9C2A6",   # warm sandstone (between Sierra Reads cream + Dad amber)
        "text":    "0x2B1F12",   # deep umber
        "accent":  "0xA8513C",   # rust accent
        "lines":   ("SIERRA APOLOGIST", "DEFENDS THE INDEFENSIBLE"),
        "tag":     "EP. {ep}",
        "sting_hz": 540,         # mid-warm tone — between Sierra Reads bell + Dad buzz
    },
}


def build_card(bit_id: str, *, ep: int = 1, with_sting: bool = True) -> pathlib.Path:
    spec = BITS[bit_id]
    plate, text_c, accent = spec["plate"], spec["text"], spec["accent"]
    line1, line2 = spec["lines"]
    tag = spec["tag"].format(ep=ep)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{bit_id}.mp4"

    # Single-source video filter chain. Use unique labels (vbg, v1, v2, v3,
    # vfin) and chain via a single semicolon-separated graph. Fade-in/out is
    # applied at the end so the whole composed text fades together.
    fc_video = (
        f"color=c={plate}:s={W}x{H}:d={DUR}:r={FPS}[vbg];"
        f"[vbg]drawtext=fontfile={FONT_PATH}:text='{line1}':"
        f"fontcolor={text_c}:fontsize=96:x=(w-text_w)/2:y=820[v1];"
        f"[v1]drawtext=fontfile={FONT_PATH}:text='{line2}':"
        f"fontcolor={text_c}:fontsize=96:x=(w-text_w)/2:y=950[v2];"
        f"[v2]drawbox=x=(iw-100)/2:y=1075:w=100:h=4:color={accent}:t=fill[v3];"
        f"[v3]drawtext=fontfile={FONT_PATH}:text='{tag}':"
        f"fontcolor={text_c}:fontsize=36:x=(w-text_w)/2:y=1110[v4];"
        f"[v4]fade=t=in:st=0:d=0.25,fade=t=out:st=1.25:d=0.25,format=yuv420p[vout]"
    )

    if with_sting:
        sting_hz = spec["sting_hz"]
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "lavfi", "-i", f"sine=f={sting_hz}:d=0.25",
            "-filter_complex",
            f"{fc_video};[0:a]volume=0.10,apad=whole_dur={DUR},"
            f"aformat=channel_layouts=stereo[aout]",
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
            "-crf", "20", "-r", str(FPS), "-t", f"{DUR}",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            str(out),
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-filter_complex", fc_video,
            "-map", "[vout]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
            "-crf", "20", "-r", str(FPS), "-t", f"{DUR}",
            "-an", "-movflags", "+faststart",
            str(out),
        ]

    subprocess.run(cmd, check=True)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("bits", nargs="*", help="bit ids; default all")
    p.add_argument("--ep", type=int, default=1)
    p.add_argument("--no-sting", action="store_true")
    args = p.parse_args()

    bits = args.bits or list(BITS.keys())
    for bid in bits:
        if bid not in BITS:
            print(f"unknown bit '{bid}'. Valid: {list(BITS)}", file=sys.stderr)
            return 1
        out = build_card(bid, ep=args.ep, with_sting=not args.no_sting)
        print(f"[title-cards] wrote {out.relative_to(REPO_ROOT)} ({out.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
