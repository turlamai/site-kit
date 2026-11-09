# Per-site migration playbook (agent-facing)

Migrate one family site to site-kit. Do this per repo, in order, with verification
gates after every step. Reference implementation: `~/Codes/fulcrum/site` (product
with installers) and `~/Codes/termpilot/site` (rebuilt page). Kit: `~/Codes/site-kit`
(read `dist/family.css` for available components, `template/index.html` for the
canonical skeleton, `docs/SITE-MIGRATION-PLAYBOOK.md` is this file).

## Steps per repo

1. **Clone & branch hygiene**
   - `gh repo clone turlamai/<repo> ~/Codes/<repo>` (skip if the dir exists).
   - `B=$(gh api repos/turlamai/<repo> --jq .default_branch)`; `git checkout $B`;
     `git pull --rebase`. Never commit on any other branch.

2. **Sync kit assets**: `~/Codes/site-kit/sync.sh ~/Codes/<repo>`
   (auto-detects `site/` or `docs/`; remember which one — that's `SITEDIR`).

3. **Inventory the old page** (read ALL of old `index.html` + any site JS):
   - every `data-i18n` key and its dictionaries (inline `var zh/en`, external
     `script.js` `const i18n`, or `data-en`/`data-zh` attributes);
   - every `reader-en`/`reader-zh` (or `vs-en`/`vs-zh`) span pair → becomes one
     element with a new `data-i18n` key, zh value canonical, en value translated;
   - section structure, nav links, footer links, download buttons, special sections
     (mockups, showcases, screenshots, tables, code blocks);
   - the theme/lang storage keys (e.g. `movebit-theme`, `movebit-lang-override-v2`)
     — the new page MUST keep the same keys so returning visitors keep their prefs.

4. **Release facts** (only if the repo ships installers):
   - `gh api "repos/turlamai/<repo>/releases?per_page=10"` — list asset names.
   - stable release exists → `kit-download` config with exact naming patterns;
     CTA/menu hrefs = `releases/latest`.
   - only prereleases or none → configure patterns anyway (harmless), point all
     hrefs at `/releases` (list page; `releases/latest` 404s without a stable
     release), and render the `kit-dl-note` WITHOUT the `kit-hidden` class.
   - linux-only products (e.g. syncpilot): only the `linux` pattern + menu row.
   - library/framework pages without binaries (rivet, glaze, permit, relaypilot,
     autarx): NO `kit-download` config, no `.kit-dl` split button; use a
     `raco pkg install <pkg>` `<pre>` block as the primary CTA instead.

5. **Rewrite `index.html` on the kit skeleton** — preserving ALL content:
   - `<html lang="zh-CN" data-kit-id="<repo>">`;
   - head: keep title/description/canonical/OG/twitter (og:lang-aware copy ok),
     theme-color `#D97757`, favicon (existing or recolored to #D97757),
     theme+lang pre-paint snippet keyed on the site's real storage keys,
     `family.css`, `site.css`, font preloads (Newsreader + Inter; the old page
     may preload only some fonts — preload what the page uses),
     `family.js` deferred;
   - nav: `kit-nav` with brand (existing logo SVG, recolor accent fills to
     `#D97757`), existing section links, `kit-lang` dropdown, `kit-theme-toggle`;
   - hero: `kit-hero` — eyebrow pill, h1 (split headline spans separated by a
     space text node, accent span gets `class="kit-accent-word"`), lead,
     `kit-btn-row` with `kit-dl` split button (+ per-platform menu) or install
     block, secondary CTA, `kit-hero-meta` with `kit-badge` availability line;
   - sections: `kit-section` (+ `kit-section--alt` for alternation), section
     headers as `kit-kicker` + `kit-h2` (+ `kit-lead`), cards as `kit-grid` +
     `kit-card` (+ `kit-card-icon`), platform chips as `kit-platform-chip`,
     numbered steps as `kit-steps`/`kit-step`;
   - keep unique showpieces (launcher/board/terminal mocks, screenshots) with
     their own classes styled in `site.css` using kit tokens (`--kit-*`);
   - footer: `kit-footer` 4-column grid (brand+tagline / product / family
     [全部产品→jrtx.site, family links] / legal [GitHub, license]);
     bottom bar `© 2026 TuringLambda AI` + `site-kit v1.0.1` mono stamp;
   - dictionaries: `<script type="application/json" id="kit-i18n">` with
     COMPLETE `zh` and `en` (every `data-i18n` key in BOTH dicts; zh canonical;
     en translated to product-grade English, not machine-literal);
   - download config (if applicable): `<script type="application/json"
     id="kit-download">` with `repo` + `assets` patterns (+ `archMap` when
     release names use x86_64/aarch64);
   - never hardcode versioned release URLs in markup;
   - `data-i18n` goes on LEAF elements only; sentences with inline links split
     into `-a`/`-b` keys around the `<a>`/`<code>`.

6. **`site.css`**: per-site sections only, on `--kit-*` tokens; end with the
   theme icon visibility rules (`html[data-theme="light"] .kit-icon-moon{display:none}`
   and the dark/sun counterpart). Delete the old homepage stylesheet ONLY if no
   other page references it (manual/guide pages usually do — keep those files
   and leave those pages untouched).

7. **Verify before commit** (all must pass):
   - `python3 ~/Codes/site-kit/check-site.py <SITEDIR> <repo>` → OK;
   - local serve `python3 -m http.server 87xx --bind 127.0.0.1` in SITEDIR;
   - headless checks with Edge:
     `"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --headless --disable-gpu --screenshot=/tmp/x.png --window-size=1280,900 --virtual-time-budget=4000 "http://127.0.0.1:87xx/index.html"`
     — then READ the PNG and confirm: fonts loaded, layout sane, no
     default-blue links, download CTA labeled, no missing text.
   - a second render with
     `--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"`
     must show the Windows label (do this by checking the primary label in the
     DOM via a `--dump-dom` run grepping for `kit-dl-label` content).
   - zh rendering: append `#` is not enough — for language checks rely on
     dictionary completeness + one screenshot with the browser set to zh via a
     temporary query-less check is NOT possible headless; instead verify all
     zh values exist in the dict (check-site does) and the markup defaults are zh.

8. **Commit & push** (never leave uncommitted work):
   ```
   git add <SITEDIR>
   git -c user.name=turlamai -c user.email=turlamai@users.noreply.github.com \
     commit -m "site: rebuild homepage on site-kit v1.0.1" \
     -m "- adopt the family design system (terracotta accent, Newsreader display)
   - language follows browser locale with persisted override; full zh/en dicts
   - unified download resolver / release-asset facts <adjust per repo>
   - <other pages> keep legacy assets until their own kit migration"
   git push
   ```

9. **Post-deploy verification**: wait for Pages deploy (workflow `Pages` or
   `pages-build-deployment`; legacy builds have no modern run — use the live
   URL with a cache-buster `?v=<date>`):
   - `<url>/family.js` and `<url>/family.css` → 200;
   - homepage HTML contains `data-kit-id`, `kit-i18n`, `kit-download` (when applicable);
   - one headless screenshot of the LIVE site, read it, confirm nothing broke.

## Hard rules

- Content preservation is absolute: no section, card, fact, link, caveat or
  legal line may disappear. When in doubt, keep.
- zh copy is canonical; en must be complete and idiomatic.
- Never reference CDNs, Google Fonts, or external hotlinks.
- Never edit files outside `<SITEDIR>` (no CI, no README, no app code) unless
  the task explicitly says so.
- If check-site.py fails, fix before commit — a failing lint never ships.
- If the repo turns out to lack a homepage entirely or has an exotic build,
  STOP and report instead of improvising.
