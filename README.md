# site-kit

The single source of truth for every `jrtx.site` family product site: one design system, one i18n engine, one download resolver — so the family reads as one commercial product instead of twenty hand-rolled pages.

[中文说明](README.zh-CN.md)

## Why

Every family site used to hand-copy its own CSS, i18n dictionaries and download logic. That produced three visual dialects, broken language toggles, and downloads that gave a macOS package to Windows visitors. This kit removes the copies: sites sync the kit assets in, and a CI job audits the whole family weekly.

## Layout

```
dist/
  family.css   design tokens + shared components (nav, hero, cards, footer, themes)
  family.js    theme + i18n + download resolver engines (zero dependencies)
  fonts/       self-hosted Newsreader + Inter (no CDN, no Google Fonts)
template/
  index.html   the canonical page skeleton, documented by example
sync.sh        copy dist assets into a target repo's site directory
check-site.py  lint one site directory against the kit contract
family.json    every family site: repo, URL, kind, installer flag
.github/workflows/drift-check.yml  weekly family audit, opens an issue on drift
```

## Use

```sh
# bring a site repo up to the current kit version
./sync.sh ~/Codes/fulcrum

# lint a site directory
./check-site.py ~/Codes/fulcrum/site fulcrum
```

Then rework the site's `index.html` onto the template skeleton (nav / hero / features / platforms / getting started / footer) and move per-site sections into `site.css`.

## Page contract

- `<html data-kit-id="<site-id>">` — drives the per-site storage keys (`<site-id>-theme`, `<site-id>-lang-override-v2`).
- Dictionaries: `<script type="application/json" id="kit-i18n">` with complete `zh` and `en` objects. `data-i18n` goes on leaf elements only.
- Downloads: `<script type="application/json" id="kit-download">` with the repo and asset naming patterns. The resolver never defaults an unknown platform to macOS; unresolvable CTAs fall back to the Releases page.
- Language: stored override wins, otherwise the browser locale; `languagechange` is honored live.
- Fonts and all assets are self-hosted. Never reference Google Fonts or any CDN.

## Versioning

`VERSION` tracks the kit. `sync.sh` stamps synced files; `check-site.py` fails on stale stamps; `drift-check.yml` opens an issue when a deployed site diverges.

## License

[MIT](LICENSE)
