#!/usr/bin/env python3
"""check-site.py — lint one family site directory against the kit contract.

Usage: check-site.py <site-dir> [repo-name]

Fails (exit 1) on contract violations; warns on softer issues.
"""
import json
import pathlib
import re
import sys

KIT_ROOT = pathlib.Path(__file__).resolve().parent
KIT_VERSION = (KIT_ROOT / "VERSION").read_text().strip()

FAILS = []
WARNS = []


def fail(msg):
    FAILS.append(msg)


def warn(msg):
    WARNS.append(msg)


def main():
    if len(sys.argv) < 2:
        print("usage: check-site.py <site-dir> [repo-name]", file=sys.stderr)
        return 2
    site = pathlib.Path(sys.argv[1]).resolve()
    repo_name = sys.argv[2] if len(sys.argv) > 2 else site.parent.name
    index = site / "index.html"
    if not index.is_file():
        fail(f"{site}: index.html missing")
        report()
        return 1
    html = index.read_text(encoding="utf-8")

    # 1. kit wiring
    m = re.search(r'<html[^>]*data-kit-id="([^"]+)"', html)
    if not m:
        fail("index.html: missing data-kit-id on <html>")
    else:
        if m.group(1) != repo_name:
            warn(f'data-kit-id="{m.group(1)}" != repo name "{repo_name}"')
        theme_key = re.search(r'data-kit-theme-key="([^"]+)"', html)
        theme_key = theme_key.group(1) if theme_key else f"{m.group(1)}-theme"
        if theme_key not in html:
            warn(f"theme pre-paint snippet does not reference '{theme_key}'")
    if not re.search(r'<html[^>]*lang="', html):
        fail("index.html: missing lang attribute on <html>")
    if "dataset.theme" not in html and "localStorage.getItem" not in html:
        warn("index.html: no theme pre-paint script found (flash risk)")

    # 2. kit assets present, linked, version current
    for asset in ("family.css", "family.js"):
        p = site / asset
        if not p.is_file():
            fail(f"{asset} missing from site dir")
            continue
        head = p.read_text(encoding="utf-8", errors="ignore")[:220]
        if f"site-kit v{KIT_VERSION}" not in head:
            fail(f"{asset}: stale or unstamped (expected site-kit v{KIT_VERSION}); re-run sync.sh")
        if asset not in html:
            fail(f"index.html does not reference {asset}")
    fonts = site / "fonts"
    for font in ("newsreader-latin-var.woff2", "inter-latin-var.woff2"):
        if not (fonts / font).is_file():
            fail(f"fonts/{font} missing (family sites self-host fonts)")

    # 3. i18n completeness: every data-i18n key resolves in zh AND en
    m = re.search(
        r'<script type="application/json" id="kit-i18n">(.*?)</script>',
        html, re.S)
    if not m:
        fail("index.html: missing <script id=\"kit-i18n\"> dictionary")
    else:
        try:
            dicts = json.loads(m.group(1))
        except json.JSONDecodeError as e:
            fail(f"kit-i18n JSON invalid: {e}")
            dicts = None
        if dicts:
            for lang in ("zh", "en"):
                if lang not in dicts:
                    fail(f"kit-i18n: '{lang}' dictionary missing")
            keys = set(re.findall(r'data-i18n(?:-key)?="([^"]+)"', html))
            # multi-page sites (generated digests, manuals) carry keys on
            # their other pages — scan every html file that runs on the kit
            # engine. Pages with their own legacy engines (manual.html,
            # guide.html) own their dictionaries and are skipped.
            for extra_page in site.rglob("*.html"):
                if extra_page != index:
                    ph = extra_page.read_text(encoding="utf-8", errors="ignore")
                    if "family.js" in ph:
                        keys |= set(re.findall(
                            r'data-i18n(?:-key)?="([^"]+)"', ph))
            for key in sorted(keys):
                for lang in ("zh", "en"):
                    d = dicts.get(lang) or {}
                    if key not in d:
                        fail(f"i18n[{lang}] missing key: {key}")
            for lang in ("zh", "en"):
                d = dicts.get(lang) or {}
                for key in d:
                    if key not in keys:
                        warn(f"i18n[{lang}] key unused in markup: {key}")

    # 4. download contract
    if re.search(r'id="kit-download"', html):
        m = re.search(
            r'<script type="application/json" id="kit-download">(.*?)</script>',
            html, re.S)
        try:
            cfg = json.loads(m.group(1)) if m else None
        except json.JSONDecodeError as e:
            cfg = None
            fail(f"kit-download JSON invalid: {e}")
        if cfg:
            want = f"turlamai/{repo_name}"
            if cfg.get("repo") != want:
                fail(f'kit-download repo "{cfg.get("repo")}" != "{want}"')
            assets = cfg.get("assets") or {}
            if not any(("{" in p and "}" in p) or p for p in assets.values()):
                fail("kit-download: asset patterns empty")
        if re.search(r'releases/download/v?\d+\.\d+', html):
            fail("index.html hardcodes a versioned release URL; the resolver owns links")
    if "data-kit-dl-primary" in html and not re.search(r'id="kit-download"', html):
        fail("primary download CTA present but kit-download config missing")

    # 5. CNAME
    if not (site / "CNAME").is_file():
        warn("CNAME missing (custom-domain sites need it)")

    # 6. No third-party CDNs or web fonts — mainland-safe self-hosting only.
    blob = html
    for extra in site.glob("*.css"):
        blob += extra.read_text(encoding="utf-8", errors="ignore")
    for extra in site.glob("*.js"):
        blob += extra.read_text(encoding="utf-8", errors="ignore")
    for marker in ("fonts.googleapis", "fonts.gstatic", "cdn.jsdelivr",
                   "unpkg.com", "cdnjs.cloudflare", "google-analytics",
                   "googletagmanager"):
        if marker in blob:
            fail(f"external dependency found: {marker} (self-host instead)")

    # 7. site.css presence (per-site sections)
    if not (site / "site.css").is_file():
        warn("site.css missing (per-site sections should live there)")

    report()
    return 1 if FAILS else 0


def report():
    for w in WARNS:
        print(f"WARN: {w}")
    for f in FAILS:
        print(f"FAIL: {f}")
    if not FAILS:
        print("OK")


if __name__ == "__main__":
    sys.exit(main())
