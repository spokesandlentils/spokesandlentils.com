# spokesandlentils.com

Plain HTML + CSS. No build step, no dependencies.

**Publish:** Settings → Pages → Source: *Deploy from a branch* → branch `main`, folder `/ (root)` → Save.
The `CNAME` file points the site at spokesandlentils.com; `.nojekyll` stops GitHub from processing the files. Changes go live ~1 minute after a commit.

**Add a link:** open `index.html`, find the `<nav class="links">` block, uncomment the commented-out `<a class="link" ...>` block and edit its `href` and text.

**Logos:** each link carries an inline `<svg class="icon">` logo — no icon font, no extra requests. The brand marks come from [Simple Icons](https://simpleicons.org) (CC0); grab the `d="..."` out of any icon there and paste it into the `<path>` for a new link. Logos take their colour from the button, so they follow `--accent` in light and dark mode automatically. Drop the `<svg>` line for a text-only button.

**Change the colours:** edit the `--accent` line at the top of `style.css`.

**Light / dark:** the site follows the visitor's browser or OS setting automatically — there is no toggle and nothing to configure. Dark mode reuses your `--accent`, lightening it so buttons stay readable on a dark page.

**Placeholders:** every value to replace is in ALL_CAPS or marked `EDIT:`.
