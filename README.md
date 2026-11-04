# spokesandlentils.com

Plain HTML + CSS. No build step, no dependencies.

**Publish:** Settings → Pages → Source: *Deploy from a branch* → branch `main`, folder `/ (root)` → Save.
The `CNAME` file points the site at spokesandlentils.com; `.nojekyll` stops GitHub from processing the files. Changes go live ~1 minute after a commit.

**Add a link:** open `index.html`, find the `<nav class="links">` block, uncomment the commented-out `<a class="link" ...>` block and edit its `href` and text.

**Logos:** each link carries an inline `<svg class="icon">` — no icon font, no extra requests. The `d="..."` path data came from [Simple Icons](https://simpleicons.org); the marks themselves remain the trademarks of their owners, used here to link to our own profiles. Logos take their colour from the button, so they follow `--accent` in light and dark mode. Drop the `<svg>` line for a text-only button.

**Header video:** the header is a short silent loop (`media/video/hero-v1.mp4`, 6 s, ~1.3 MB, in the repo) over a photo of its first frame. `hero.js` decides what to play:

- The photo always comes first, and only appears once it is fully decoded (a tiny blurred copy in `style.css` fills the box until then). Without JavaScript it simply shows.
- The loop is only downloaded for visitors who have not asked for reduced motion, have not turned on data saver and are not on 2G/3G (the last two can only be detected in Chrome/Edge/Android). It fades in once it is actually playing; if it cannot start within 8 s (slow link, iPhone low-power mode) it is dropped and the photo stays. There are no player controls.

**Change the header video:** you need [ffmpeg](https://ffmpeg.org) and the full-quality master (`Banner.mp4`, never commit it — GitHub refuses files over 100 MB). Run `tools/encode-hero-video.sh path/to/Banner.mp4`. It writes the short loop, `media/images/hero.jpeg` (its first frame). Then run `python3 tools/build-images.py` (see below) and paste the placeholder line it prints into `.hero` in `style.css`. The loop points (`START`/`END`, frame numbers) are at the top of the script; for a different master, pick two frames 6–8 s apart that look nearly the same (the script dissolves the last second so the wrap has no seam). Every time the video changes, bump `-v1` to `-v2` in the file name, in the script and in `index.html`, so no browser keeps the old one.

**Change the header photo:** the photo is the video's first frame, so normally the video script makes it. To use another picture, save it over `media/images/hero.jpeg` (at least 1200px wide, 16:9 to match the video) and run `python3 tools/build-images.py` (needs Python 3 and Pillow — `pip install Pillow`). It rewrites the nine small `hero-600/900/1200.avif/.webp/.jpg` files that the page actually serves, so a phone downloads roughly 35–200 KB instead of the multi-megabyte original, and prints the blurred placeholder for `style.css`. Commit everything. Then edit `index.html` by hand:

- **Every time:** rewrite *both* descriptions of the photo — the `alt="..."` on the `<img>`, and the `og:image:alt` line in the `<head>`. Until you do, they describe the old photo to screen-reader users and in every shared link preview.
- **If the new photo is a different shape:** copy the `width`/`height` the script prints onto the `<img>`, and the same two numbers onto `og:image:width` / `og:image:height` (and change `aspect-ratio` on `.hero` in `style.css`).

**Change the colours:** edit the `--accent` line at the top of `style.css`.

**Light / dark:** the site follows the visitor's browser or OS setting automatically — there is no toggle and nothing to configure. Dark mode reuses your `--accent`, lightening it so buttons stay readable on a dark page.

**Placeholders:** every value to replace is in ALL_CAPS or marked `EDIT:`.
