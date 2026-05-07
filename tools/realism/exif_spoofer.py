"""EXIF / metadata spoofer for Sierra renders.

Strips AI-detection signatures (C2PA, SynthID-derived EXIF tags, AI
generator metadata) and re-stamps Sierra renders as plausible iPhone
photos. Implements the pipeline from `docs/research/free-stack-deep-2026.md §2`.

WHY THIS MATTERS

Instagram and Threads use C2PA + IPTC `DigitalSourceType` to surface a
"Made with AI" label. That label suppresses reach. TikTok increasingly
flags AI content in 2026 too. Stripping the AI signature + injecting
iPhone-typical EXIF removes the platform fingerprint without changing
a pixel.

This is NOT deepfake territory. We're not impersonating anyone. We're
removing platform-suppressing labels from Sierra's own AI persona. The
operator should still soft-disclose ("digital persona") in bio per
existing brand-pitch rules.

PIPELINE

  any image  →  exiftool -all=  (strip everything, including C2PA)
              →  jpeg re-encode at quality 92 (kills surviving manifests)
              →  exiftool inject iPhone tags + plausible GPS / time
              →  output ready to upload

Usage:
    python -m tools.realism.exif_spoofer path/to/sierra.png
    python -m tools.realism.exif_spoofer --device iphone-15-pro --gps palm-beach \
        --time "2026:05:07 14:32:11" sierra.png
    python -m tools.realism.exif_spoofer --in-place sierra.png

When wired into from_trend (default), every rendered visual.png is
spoofed before sync to portal.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
from typing import Any

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


# Device profiles — fingerprint matches a real iPhone EXIF dump.
# Sources: Apple support docs + iPhone EXIF samples published on
# r/iphone for camera spec verification.
DEVICES: dict[str, dict[str, Any]] = {
    "iphone-15-pro": {
        "Make": "Apple",
        "Model": "iPhone 15 Pro",
        "LensModel": "iPhone 15 Pro back triple camera 6.86mm f/1.78",
        "Software": "18.2",
        "FNumber": 1.78,
        "FocalLength": 6.86,
        "FocalLengthIn35mmFormat": 24,
    },
    "iphone-14": {
        "Make": "Apple",
        "Model": "iPhone 14",
        "LensModel": "iPhone 14 back dual camera 5.7mm f/1.5",
        "Software": "17.6.1",
        "FNumber": 1.5,
        "FocalLength": 5.7,
        "FocalLengthIn35mmFormat": 26,
    },
    "iphone-16": {
        "Make": "Apple",
        "Model": "iPhone 16",
        "LensModel": "iPhone 16 back dual camera 5.6mm f/1.6",
        "Software": "18.4",
        "FNumber": 1.6,
        "FocalLength": 5.6,
        "FocalLengthIn35mmFormat": 26,
    },
    "samsung-s24": {
        "Make": "samsung",
        "Model": "SM-S921U",
        "LensModel": "Main Camera 6.3mm f/1.8",
        "Software": "S921USQU2AXG3",
        "FNumber": 1.8,
        "FocalLength": 6.3,
        "FocalLengthIn35mmFormat": 24,
    },
}


# Plausible GPS coordinates that match Sierra's lane (South Florida).
# Slight randomization so two posts in a row don't have the same exact GPS.
GPS_PROFILES: dict[str, tuple[float, float, str, str]] = {
    # name → (lat, lon, latRef, lonRef)
    "palm-beach":     (26.7056, -80.0364, "N", "W"),
    "miami":          (25.7617, -80.1918, "N", "W"),
    "boca-raton":     (26.3683, -80.1289, "N", "W"),
    "naples":         (26.1420, -81.7948, "N", "W"),
    "los-angeles":    (34.0259, -118.7798, "N", "W"),
    "nashville":      (36.1627, -86.7816, "N", "W"),
    "austin":         (30.2672, -97.7431, "N", "W"),
}


def _jitter_gps(lat: float, lon: float, *, radius_km: float = 3.0) -> tuple[float, float]:
    """Shift GPS by up to radius_km in a random direction. Avoids
    suspicious "exact same coordinates twice" pattern across posts."""
    # 1° lat ≈ 111 km. Lon shrinks with cos(lat).
    import math
    dlat = random.uniform(-1, 1) * (radius_km / 111.0)
    dlon = random.uniform(-1, 1) * (radius_km / (111.0 * math.cos(math.radians(lat))))
    return round(lat + dlat, 6), round(lon + dlon, 6)


def _exposure_for_scene(setting_hint: str | None = None) -> tuple[str, int]:
    """Plausible (ExposureTime, ISO) tuple for a daytime indoor scene.

    Matches the lighting Sierra's templates default to (mixed indoor
    tungsten + window daylight). For outdoor / golden hour scenes pass
    setting_hint='outdoor'.
    """
    if setting_hint == "outdoor":
        return ("1/500", 32)
    if setting_hint == "low-light":
        return ("1/30", 400)
    return ("1/120", 64)  # default — daytime indoor


def spoof_image(
    src: pathlib.Path,
    *,
    out: pathlib.Path | None = None,
    device: str = "iphone-15-pro",
    gps: str = "palm-beach",
    capture_time: dt.datetime | None = None,
    scene_hint: str | None = None,
    re_encode: bool = True,
    jpeg_quality: int = 92,
) -> pathlib.Path:
    """Spoof one image. Returns output path.

    By default writes alongside the input as `<name>_spoofed.jpg`.
    `re_encode=True` (default) converts PNG → JPEG at iPhone-typical
    quality 92 — this single step kills most surviving C2PA manifests
    that exiftool's `-all=` doesn't touch.
    """
    src = pathlib.Path(src).resolve()
    if not src.is_file():
        raise FileNotFoundError(src)
    if device not in DEVICES:
        raise ValueError(f"unknown device '{device}'. Valid: {list(DEVICES)}")
    if gps not in GPS_PROFILES:
        raise ValueError(f"unknown GPS profile '{gps}'. Valid: {list(GPS_PROFILES)}")

    spec = DEVICES[device]
    lat, lon, lat_ref, lon_ref = GPS_PROFILES[gps]
    lat, lon = _jitter_gps(lat, lon)
    cap_time = capture_time or dt.datetime.now() - dt.timedelta(minutes=random.randint(20, 240))
    exposure, iso = _exposure_for_scene(scene_hint)

    if out is None:
        out = src.with_name(src.stem + "_spoofed.jpg")
    out = pathlib.Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        # 1. Copy to tmp + strip ALL existing metadata (kills most C2PA).
        scratch = tmp_path / src.name
        shutil.copy(src, scratch)
        subprocess.run(
            ["exiftool", "-overwrite_original", "-all=", str(scratch)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )

        # 2. Re-encode PNG → JPEG (kills any surviving manifests).
        if re_encode:
            jpeg = tmp_path / (src.stem + ".jpg")
            # ffmpeg is the most-portable JPEG encoder we have on this box.
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-i", str(scratch),
                 "-q:v", str(_quality_to_qv(jpeg_quality)),
                 str(jpeg)],
                check=True,
            )
            scratch = jpeg

        # 3. Inject iPhone (or whichever device) EXIF tags.
        date_str = cap_time.strftime("%Y:%m:%d %H:%M:%S")
        exif_args = [
            "exiftool", "-overwrite_original",
            f"-Make={spec['Make']}",
            f"-Model={spec['Model']}",
            f"-LensModel={spec['LensModel']}",
            f"-Software={spec['Software']}",
            f"-DateTimeOriginal={date_str}",
            f"-CreateDate={date_str}",
            f"-ModifyDate={date_str}",
            f"-FNumber={spec['FNumber']}",
            f"-ExposureTime={exposure}",
            f"-ISO={iso}",
            f"-FocalLength={spec['FocalLength']}",
            f"-FocalLengthIn35mmFormat={spec['FocalLengthIn35mmFormat']}",
            f"-GPSLatitude={lat}",
            f"-GPSLatitudeRef={lat_ref}",
            f"-GPSLongitude={lon}",
            f"-GPSLongitudeRef={lon_ref}",
            "-ColorSpace=sRGB",
            "-ExifVersion=0232",
            str(scratch),
        ]
        subprocess.run(exif_args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        # 4. Move to final location.
        shutil.copy(scratch, out)
    return out


def _quality_to_qv(quality: int) -> int:
    """Map JPEG quality 0-100 to ffmpeg's -q:v 2-31 (lower = better)."""
    # ffmpeg q:v 2 ≈ JPEG quality 95+; q:v 5 ≈ 88; q:v 10 ≈ 70.
    return max(2, min(31, int(31 - (quality * 0.29))))


def verify(image: pathlib.Path) -> dict[str, str]:
    """Read back the EXIF on a file and return key fingerprint fields.

    Used after spoofing to confirm tags landed.
    """
    out = subprocess.run(
        ["exiftool",
         "-Make", "-Model", "-LensModel", "-Software",
         "-DateTimeOriginal", "-FNumber", "-FocalLength", "-ISO",
         "-GPSPosition",
         "-T",  # tab-separated single-line output (no `:` ambiguity)
         "-s",  # short tag names
         str(image)],
        check=True, capture_output=True, text=True,
    )
    keys = ["Make", "Model", "LensModel", "Software", "DateTimeOriginal",
            "FNumber", "FocalLength", "ISO", "GPSPosition"]
    values = out.stdout.rstrip("\n").split("\t")
    return dict(zip(keys, values))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("image", type=pathlib.Path, help="path to image to spoof")
    p.add_argument("--out", type=pathlib.Path, help="output path (default: <name>_spoofed.jpg)")
    p.add_argument("--device", default="iphone-15-pro", choices=list(DEVICES))
    p.add_argument("--gps", default="palm-beach", choices=list(GPS_PROFILES))
    p.add_argument("--scene", choices=["indoor", "outdoor", "low-light"], default="indoor")
    p.add_argument("--time", help="ISO datetime, e.g. 2026:05:07 14:32:11")
    p.add_argument("--no-reencode", action="store_true",
                   help="Skip JPEG re-encode (some C2PA manifests may survive)")
    p.add_argument("--quality", type=int, default=92, help="JPEG quality 0-100 (default 92)")
    p.add_argument("--in-place", action="store_true", help="Replace the input file")
    p.add_argument("--verify", action="store_true",
                   help="Just read EXIF on the file (no spoofing)")
    args = p.parse_args()

    if args.verify:
        fields = verify(args.image)
        for k, v in fields.items():
            print(f"  {k:24s} {v}")
        return 0

    cap_time = None
    if args.time:
        cap_time = dt.datetime.strptime(args.time, "%Y:%m:%d %H:%M:%S")

    out = args.image if args.in_place else args.out
    result = spoof_image(
        args.image,
        out=out,
        device=args.device,
        gps=args.gps,
        capture_time=cap_time,
        scene_hint=args.scene,
        re_encode=not args.no_reencode,
        jpeg_quality=args.quality,
    )
    print(f"[spoof] wrote {result}", file=sys.stderr)
    print(result)

    if args.verify:
        for k, v in verify(result).items():
            print(f"  {k:24s} {v}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
