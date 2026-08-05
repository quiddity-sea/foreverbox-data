#!/bin/bash
# Verify sidenav anchor IDs resolve to their target pages.
# Run from the stitch_project_repository_analyzer directory.
set -uo pipefail
BASE="${1:-.}"
SIDENAV="$BASE/components/sidenav.html"
failed=0; checked=0

while IFS='#' read -r page anchor; do
    if grep -q "id=\"$anchor\"" "$BASE/$page" 2>/dev/null; then
        checked=$((checked + 1))
    else
        echo "FAIL: $page#$anchor"; failed=1
    fi
done < <(grep -oP 'href="(part\d+\.html#part\d+[^"]*)"' "$SIDENAV" | sed 's/href="//;s/"//' | sort -u)

# Dupes check
for f in "$BASE"/part*.html; do
    dupes=$(grep -oP 'id="[^"]*"' "$f" | sort | uniq -d || true)
    [ -n "$dupes" ] && { echo "DUPLICATE in $(basename "$f"): $dupes"; failed=1; }
done

# Section balance
for f in "$BASE"/part*.html; do
    open=$(grep -c '<section' "$f" 2>/dev/null || echo 0)
    close=$(grep -c '</section>' "$f" 2>/dev/null || echo 0)
    [ "$open" != "$close" ] && { echo "UNBALANCED in $(basename "$f"): $open vs $close"; failed=1; }
done

echo "$checked anchors checked, $failed failures"
[ "$failed" -eq 0 ] && echo "PASS" || echo "FAIL"
exit "$failed"
