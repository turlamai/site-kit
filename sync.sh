#!/usr/bin/env bash
# sync.sh — copy site-kit dist assets into a family site repo.
# Usage: ./sync.sh <path-to-target-repo>
# Resolves the target site directory automatically:
#   1. .github/workflows/pages.yml "path:" (workflow-deployed sites)
#   2. docs/index.html                     (legacy Pages from /docs)
#   3. site/index.html                     (Pages from /site)
# Never touches index.html or CNAME — those stay per-site.
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(cat "$KIT_ROOT/VERSION")"

if [[ $# -ne 1 ]]; then
    echo "usage: $0 <path-to-target-repo>" >&2
    exit 2
fi

REPO="$(cd "$1" && pwd)"
TARGET=""

# 1. Workflow-deployed: read the artifact path out of the pages workflow.
PAGES_WF="$REPO/.github/workflows/pages.yml"
if [[ -f "$PAGES_WF" ]]; then
    WF_PATH="$(grep -E '^\s*path:' "$PAGES_WF" | head -1 | sed -E 's/^\s*path:\s*//; s/^["'"'"']|["'"'"']$//g') || true"
    if [[ -n "${WF_PATH:-}" && "$WF_PATH" != "/" && -d "$REPO/$WF_PATH" ]]; then
        TARGET="$REPO/$WF_PATH"
    fi
fi

# 2/3. Conventional locations.
if [[ -z "$TARGET" && -f "$REPO/docs/index.html" ]]; then TARGET="$REPO/docs"; fi
if [[ -z "$TARGET" && -f "$REPO/site/index.html" ]]; then TARGET="$REPO/site"; fi

if [[ -z "$TARGET" ]]; then
    echo "error: no site directory found in $REPO (expected docs/ or site/ with index.html)" >&2
    exit 1
fi

echo "site-kit v$VERSION -> $TARGET"

# Copy engine + styles, prepending the version stamp.
for f in family.css family.js; do
    {
        echo "/* site-kit v$VERSION — generated from github.com/turlamai/site-kit; do not edit per-site. */"
        cat "$KIT_ROOT/dist/$f"
    } > "$TARGET/$f"
done

# Fonts.
mkdir -p "$TARGET/fonts"
cp "$KIT_ROOT/dist/fonts/"*.woff2 "$TARGET/fonts/"

# Version marker for drift checks.
printf '%s\n' "$VERSION" > "$TARGET/site-kit.version"

echo "done: $(ls "$TARGET" | tr '\n' ' ')"