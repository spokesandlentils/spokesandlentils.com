#!/usr/bin/env python3
"""Make the small web-sized copies of the oval photo at the bottom of the page.

Save the new photo over media/images/us.jpeg (4:3, at least 1200px wide,
upright), then run:

    pip install Pillow          # one-off, needs Python 3
    python3 tools/build-us-photo.py

It writes us-400 / us-600 / us-800 / us-1200 in .avif, .webp and .jpg next to
it and prints the blurred placeholder to paste into .us in style.css.
The oval is an ellipse touching all four edges of the photo, so anything near
the corners is cut off — keep faces away from them.
"""

import base64
import io
from pathlib import Path

from PIL import Image, features

# The photo is shown at most 36rem (576px) wide, so 1200 covers 2x screens.
WIDTHS = (400, 600, 800, 1200)
SOURCE = Path("media/images/us.jpeg")
STEM = "us"

JPEG_QUALITY = 78
WEBP_QUALITY = 76
AVIF_QUALITY = 58


def main() -> None:
    for fmt in ("avif", "webp"):
        if not features.check(fmt):
            raise SystemExit(f"Pillow lacks {fmt.upper()} support. Try: pip install --upgrade Pillow")

    src_path = Path(__file__).resolve().parent.parent / SOURCE
    out_dir = src_path.parent
    if not src_path.is_file():
        raise SystemExit(f"There is no {SOURCE}. Save the photo there under exactly that name.")

    with Image.open(src_path) as src:
        if src.getexif().get(274, 1) != 1:
            raise SystemExit("us.jpeg needs rotating (EXIF orientation). Re-save it upright first.")
        master = src.convert("RGB")
    full_w, full_h = master.size
    if full_w < max(WIDTHS):
        raise SystemExit(f"us.jpeg is only {full_w}px wide; it needs at least {max(WIDTHS)}px.")

    for width in WIDTHS:
        height = round(width * full_h / full_w)
        resized = master.resize((width, height), Image.LANCZOS)
        # No exif= anywhere: location and camera data stay out of the copies.
        # Baseline JPEG on purpose: the page shows the photo only once fully
        # decoded, over a blurred placeholder, so it never paints in stripes.
        resized.save(out_dir / f"{STEM}-{width}.jpg", "JPEG",
                     quality=JPEG_QUALITY, optimize=True, progressive=False)
        resized.save(out_dir / f"{STEM}-{width}.webp", "WEBP", quality=WEBP_QUALITY, method=6)
        resized.save(out_dir / f"{STEM}-{width}.avif", "AVIF", quality=AVIF_QUALITY)
        sizes = "  ".join(
            f"{ext:>4} {(out_dir / f'{STEM}-{width}.{ext}').stat().st_size / 1024:4.0f} KiB"
            for ext in ("avif", "webp", "jpg")
        )
        print(f"{width:>5}px ({width}x{height}) {sizes}")

    tiny = master.resize((16, round(16 * full_h / full_w)), Image.LANCZOS)
    buf = io.BytesIO()
    tiny.save(buf, "JPEG", quality=60, optimize=True)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    avg = "#%02x%02x%02x" % master.resize((1, 1), Image.BOX).getpixel((0, 0))
    print(f"\nplaceholder - paste into .us in style.css:\n  background: {avg} url({uri}) center / cover;")
    print(f'\nIf the shape changed, set width/height on the <img> to 1200 / {round(1200 * full_h / full_w)}'
          "\nand aspect-ratio on .us in style.css. Rewrite the alt text in index.html too.")


if __name__ == "__main__":
    main()
