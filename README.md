# spokesandlentils.com

Plain HTML + CSS. No build step, no dependencies.

**Publish:** Settings → Pages → Source: *Deploy from a branch* → branch `main`, folder `/ (root)` → Save.
The `CNAME` file points the site at spokesandlentils.com; `.nojekyll` stops GitHub from processing the files. Changes go live ~1 minute after a commit.

**Add a link:** open `index.html`, find the `<nav class="links">` block, uncomment one `<a class="link" ...>` line and edit its `href` and text.

**Change the colours:** edit the `--accent` line at the top of `style.css`.

**Light / dark:** the site follows the visitor's browser or OS setting automatically — there is no toggle and nothing to configure. Dark mode reuses your `--accent`, lightening it so buttons stay readable on a dark page.

**Placeholders:** every value to replace is in ALL_CAPS or marked `EDIT:`.
