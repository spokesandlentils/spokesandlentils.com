#!/usr/bin/env python3
"""Make the small web-sized copies of the header photo.

The header photo is the first frame of the header video (the "poster");
tools/encode-hero-video.sh writes it to media/images/hero.jpeg. You need this
script whenever that photo changes. Then run:

    pip install Pillow          # one-off, needs Python 3
    python3 tools/build-images.py

It writes hero-600 / hero-900 / hero-1200 next to it, in three formats each
(.avif, .webp, .jpg), and leaves your original hero.jpeg untouched as the
master copy. Commit everything it writes — the website has no build step, so
the files in the repo are exactly the files the browser downloads.

If the new photo has a different shape (taller/wider) than the old one, the
script prints the width/height numbers to put on the <img> tag in index.html.
"""

import base64
import io
from pathlib import Path

from PIL import Image, features

# The header never covers more than 1920 screen pixels (see .hero in
# style.css), the width of the video master. The master photo must be
# at least as wide as the largest of these.
WIDTHS = (600, 900, 1200, 1600, 1920)

# The copy used for link previews (og:image in index.html).
OG_WIDTH = 1200

SOURCE = Path("media/images/hero.jpeg")
STEM = "hero"

# Quality settings. Higher = better looking but bigger download.
JPEG_QUALITY = 80
WEBP_QUALITY = 78
AVIF_QUALITY = 60


def main() -> None:
    for fmt in ("avif", "webp"):
        if not features.check(fmt):
            raise SystemExit(
                f"This copy of Pillow was built without {fmt.upper()} support. "
                "Try: pip install --upgrade Pillow"
            )

    src_path = Path(__file__).resolve().parent.parent / SOURCE
    out_dir = src_path.parent

    if not src_path.is_file():
        raise SystemExit(
            f"There is no {SOURCE} to work from. The photo has to sit at that "
            "exact path, with that exact name — if your camera or phone called "
            "it something else (hero.jpg, HERO.JPEG, IMG_4021.jpeg), rename it "
            "to hero.jpeg and run this again."
        )

    with Image.open(src_path) as src:
        orientation = src.getexif().get(274, 1)
        if orientation != 1:
            raise SystemExit(
                f"hero.jpeg says it needs rotating (EXIF orientation {orientation}). "
                "Rotate and re-save it upright first, then run this again."
            )
        master = src.convert("RGB")
        full_w, full_h = master.size

    print(f"source: {full_w}x{full_h}, {src_path.stat().st_size / 1024:.0f} KiB")

    # Never blow a small photo up. Stretching a 800px photo to 1200px makes a
    # file that is both blurrier AND bigger than the original, and it is the
    # one a modern phone would choose — so stop and say so instead.
    if full_w < max(WIDTHS):
        raise SystemExit(
            f"\nhero.jpeg is only {full_w}px wide. The page needs one at least "
            f"{max(WIDTHS)}px wide to stay sharp on a modern phone, so nothing "
            "was written and the old files are untouched.\n\n"
            "Export or re-scan the photo at a bigger size and run this again. "
            "Enlarging this one would make the page blurrier and slower at the "
            "same time.\n\n"
            "If this really is the largest copy that exists, edit the WIDTHS "
            "line near the top of this script — but then the srcset lines in "
            "index.html have to be changed to match, or the page will point at "
            "files that are not there and show no photo at all. Ask someone "
            "comfortable with HTML to do that bit."
        )

    for width in WIDTHS:
        height = round(width * full_h / full_w)
        resized = master.resize((width, height), Image.LANCZOS)

        # No exif=/xmp= argument is passed anywhere below, so the camera and
        # editing metadata in the original is left out of these copies.

        # JPEG is the fallback every browser understands. It is BASELINE (not
        # progressive) on purpose: the page only shows the photo once it is
        # fully decoded (img.decode() in index.html), and then fades it in
        # over a tiny blurred placeholder, so there is no half-loaded stage to
        # improve and baseline is a little smaller and quicker to decode.
        jpg = out_dir / f"{STEM}-{width}.jpg"
        resized.save(jpg, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=False)

        webp = out_dir / f"{STEM}-{width}.webp"
        resized.save(webp, "WEBP", quality=WEBP_QUALITY, method=6)

        avif = out_dir / f"{STEM}-{width}.avif"
        resized.save(avif, "AVIF", quality=AVIF_QUALITY)

        sizes = "  ".join(
            f"{p.suffix.lstrip('.'):>4} {p.stat().st_size / 1024:5.0f} KiB"
            for p in (avif, webp, jpg)
        )
        print(f"{width:>5}px ({width}x{height}) {sizes}")

    # The placeholder that fills the box until the real photo is ready:
    # a 16px-wide copy, inlined in style.css as a data: URI (well under 1 KB),
    # which the browser stretches into a soft blur. Plus its average colour.
    tiny = master.resize((16, round(16 * full_h / full_w)), Image.LANCZOS)
    buf = io.BytesIO()
    tiny.save(buf, "JPEG", quality=60, optimize=True)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    avg = "#%02x%02x%02x" % tuple(round(c) for c in master.resize((1, 1), Image.BOX).getpixel((0, 0)))
    print(f"\nplaceholder ({len(uri)} bytes) - paste into .hero in style.css:"
          f"\n    background: {avg} url({uri}) center / cover;")

    widest = OG_WIDTH
    tallest = round(widest * full_h / full_w)
    print(
        "\nNow open index.html and, EVERY time the photo changes, rewrite BOTH"
        "\ndescriptions of it — they still describe the old photo until you do,"
        "\nand screen readers and link previews are what read them:"
        '\n    the alt="..." on the <img> inside <picture>'
        '\n    the <meta property="og:image:alt"> line in the <head>'
        "\n\nIf the new photo is a DIFFERENT SHAPE from the old one, these three"
        "\nnumbers have to change too, or the page will leave the wrong-sized gap"
        "\nfor it and link previews will crop it oddly:"
        f'\n    the <img> inside <picture>:  width="{widest}" height="{tallest}"'
        f'\n    <meta property="og:image:width" content="{widest}">'
        f'\n    <meta property="og:image:height" content="{tallest}">'
    )


if __name__ == "__main__":
    main()
