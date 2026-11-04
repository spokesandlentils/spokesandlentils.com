#!/usr/bin/env python3
"""Make the header logo from the master logo file.

The master (media/images/logo.png) must have a transparent background.
This script trims the empty margin around it and shrinks it to web size,
writing logo-header.webp and logo-header.png next to the master.
Run it whenever logo.png changes (needs Pillow — pip install Pillow):

    python3 tools/build-logo.py

Commit everything it writes.
"""

from pathlib import Path

from PIL import Image

SOURCE = Path("media/images/logo.png")
STEM = "logo-header"

# The logo is shown at most ~220px wide; 600px covers retina screens.
WIDTH = 600


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
    height = round(out.height * WIDTH / out.width)
    out = out.resize((WIDTH, height), Image.LANCZOS)

    out.save(out_dir / f"{STEM}.png", optimize=True)
    out.save(out_dir / f"{STEM}.webp", quality=90, method=6)
    print(f"Wrote {STEM}.png / .webp — {WIDTH}x{height}.")
    print(f'Put width="{WIDTH}" height="{height}" on the logo <img> in index.html.')


if __name__ == "__main__":
    main()
