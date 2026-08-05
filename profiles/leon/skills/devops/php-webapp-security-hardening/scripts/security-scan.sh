#!/usr/bin/env bash
# security-scan.sh — focused read-only security scan for an Apache PHP webapp.
# No ZAP required. Usage: ./security-scan.sh [https://site.example]
# Exit 0 = all checks pass. Read-only: only side effect is clearing rate-limit state.
set -u
BASE="${1:-https://plutus.invigor.com}"
SITE="${BASE#https://}"
SITE_DIR="/var/www/${SITE}"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "PASS: $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL: $1"; }

# 1. Security headers on index
H=$(curl -sk -D - -o /dev/null "$BASE/")
echo "$H" | grep -qi "x-content-type-options: nosniff" && ok "nosniff" || bad "nosniff"
echo "$H" | grep -qi "x-frame-options: sameorigin" && ok "X-Frame-Options" || bad "X-Frame-Options"
echo "$H" | grep -qi "referrer-policy" && ok "Referrer-Policy" || bad "Referrer-Policy"

# 2. CSRF guard on mutating endpoints (no token -> 403)
code=$(curl -sk -o /dev/null -w "%{http_code}" -X POST "$BASE/api.php?action=save_object" -d "entity_type=zone&name=x")
[ "$code" = "403" ] && ok "CSRF guard (403)" || bad "CSRF guard got $code"

# 3. SQL injection probes on GET endpoints (should NOT 500)
probe1=$(curl -sk -o /dev/null -w "%{http_code}" "$BASE/api.php?action=get_objects&entity_type=zone%27%20OR%201=1--")
probe2=$(curl -sk -o /dev/null -w "%{http_code}" "$BASE/api.php?action=get_dashboard&tab=overview%27")
[ "$probe1" != "500" ] && ok "SQLi probe 1 (no 500, got $probe1)" || bad "SQLi probe 1 -> 500"
[ "$probe2" != "500" ] && ok "SQLi probe 2 (no 500, got $probe2)" || bad "SQLi probe 2 -> 500"

# 4. Auth guard on exports
code=$(curl -sk -o /dev/null -w "%{http_code}" "$BASE/api.php?action=export_csv")
[ "$code" = "401" ] && ok "export unauth 401" || bad "export unauth got $code"

# 5. Auth guard on import (POST without session -> CSRF 403 first)
code=$(curl -sk -o /dev/null -w "%{http_code}" -X POST "$BASE/api.php?action=import_parse")
[ "$code" = "403" ] && ok "import CSRF guard 403" || bad "import guard got $code"

# 6. Rate limiting (6 rapid logins -> 429)
for i in 1 2 3 4 5 6; do curl -sk -o /dev/null -X POST "$BASE/api.php?action=login" -d "username=x&password=y" 2>/dev/null; done
code=$(curl -sk -o /dev/null -w "%{http_code}" -X POST "$BASE/api.php?action=login" -d "username=x&password=y")
[ "$code" = "429" ] && ok "rate limit 429" || bad "rate limit got $code"
sudo rm -rf "$SITE_DIR/runtime/rate_limit" 2>/dev/null  # clear so real logins are not blocked

# 7. Directory traversal / path probe
code=$(curl -sk -o /dev/null -w "%{http_code}" "$BASE/../../etc/passwd")
[ "$code" != "200" ] && ok "path traversal blocked ($code)" || bad "path traversal -> $code"

# 8. Sensitive files not exposed
for f in "db.php" ".env" ".git/config" "composer.lock"; do
    code=$(curl -sk -o /dev/null -w "%{http_code}" "$BASE/$f")
    [ "$code" != "200" ] && ok "$f not exposed ($code)" || bad "$f exposed -> 200"
done

echo ""
echo "SECURITY RESULT: $PASS passed, $FAIL failed"
[ "$FAIL" = "0" ] && exit 0 || exit 1
