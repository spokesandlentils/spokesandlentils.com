#!/usr/bin/env python3
"""Make the header logo from the master logo file.

The master (media/images/logo.png) must have a transparent background.
This script trims the empty margin around it and shrinks it to web size,
writing logo-header.webp, logo-header-1400.webp and logo-header.png next
to the master.
Run it whenever logo.png changes (needs Pillow — pip install Pillow):

    python3 tools/build-logo.py

Commit everything it writes.
"""

from pathlib import Path

from PIL import Image

SOURCE = Path("media/images/logo.png")
STEM = "logo-header"

# The logo is 36% of the header (at most 960px wide), so it is shown from
# ~140px (phone) to ~346px wide. 600px covers phones on retina screens; the
# 1400px copy is only fetched by wide retina screens.
WIDTH = 600
LARGE_WIDTH = 1400


def main() -> None:
    src_path = Path(__file__).resolve().parent.parent / SOURCE
    out_dir = src_path.parent

    with Image.open(src_path) as src:
        src = src.convert("RGBA")

    out = src
    alpha = src.getchannel("A")

    # Trim the empty margin (ignore faint specks).
    box = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
    out = out.crop(box)
    trimmed = out

    large_h = round(trimmed.height * LARGE_WIDTH / trimmed.width)
    large = trimmed.resize((LARGE_WIDTH, large_h), Image.LANCZOS)
    large.save(out_dir / f"{STEM}-{LARGE_WIDTH}.webp", quality=90, method=6)
    print(f"Wrote {STEM}-{LARGE_WIDTH}.webp — {LARGE_WIDTH}x{large_h}.")

    height = round(trimmed.height * WIDTH / trimmed.width)
    out = trimmed.resize((WIDTH, height), Image.LANCZOS)

    out.save(out_dir / f"{STEM}.png", optimize=True)
    out.save(out_dir / f"{STEM}.webp", quality=90, method=6)
    print(f"Wrote {STEM}.png / .webp — {WIDTH}x{height}.")
    print(f'Put width="{WIDTH}" height="{height}" on the logo <img> in index.html.')


if __name__ == "__main__":
    main()
