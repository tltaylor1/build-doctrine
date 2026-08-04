#!/usr/bin/env bash
# Run the real gates against a project directory and report what each found.
#
# Usage: scripts/verify.sh /path/to/project
#
# This runs tools, not questions. Every check names the tool, the finding, and
# whether it blocks. Exits non-zero if any blocking check fails, so it can be
# used as a checkpoint gate rather than as advice.
set -uo pipefail

PROJECT="${1:-.}"
cd "$PROJECT" || { echo "No such directory: $PROJECT"; exit 2; }

FAILED=0
say()  { printf '\n== %s ==\n' "$1"; }
pass() { printf '  PASS  %s\n' "$1"; }
fail() { printf '  FAIL  %s\n' "$1"; FAILED=1; }
skip() { printf '  SKIP  %s\n' "$1"; }

PY=""
for candidate in venv/bin/python .venv/bin/python python3; do
  command -v "$candidate" >/dev/null 2>&1 && { PY="$candidate"; break; }
  [ -x "$candidate" ] && { PY="$candidate"; break; }
done

say "Secrets in the full history (gitleaks)"
if command -v gitleaks >/dev/null 2>&1; then
  if gitleaks git --redact --no-banner . >/dev/null 2>&1; then
    pass "no findings in any commit"
  else
    fail "gitleaks reported findings; run: gitleaks git --redact ."
  fi
else
  skip "gitleaks not installed"
fi

say "Credential-shaped strings in tracked files"
# Deliberately broader than a secret scanner: catches demo and sample passwords
# that a scanner correctly ignores but that still read as credentials (see D-002).
HITS=$(git ls-files -z 2>/dev/null | xargs -0 grep -nEI \
  "(password|passwd|secret|token|apikey|api_key)[[:space:]]*[:=][[:space:]]*[\"'][^\"'{}\$]{6,}[\"']" 2>/dev/null \
  | grep -viE "example|placeholder|replace-with|gitleaks:allow|os\.environ|getenv|Field\(|secrets\.token" || true)
if [ -z "$HITS" ]; then
  pass "none found"
else
  fail "review these lines:"; printf '%s\n' "$HITS" | sed 's/^/        /'
fi

say "Tests"
if [ -n "$PY" ] && [ -d tests ]; then
  if OUT=$("$PY" -m pytest -q 2>&1); then
    pass "$(printf '%s' "$OUT" | tail -1)"
  else
    fail "$(printf '%s' "$OUT" | tail -3)"
  fi
else
  skip "no tests directory or no interpreter found"
fi

say "Static analysis (bandit)"
if [ -n "$PY" ] && [ -d app ]; then
  if "$PY" -m bandit -r app -q >/dev/null 2>&1; then
    pass "no findings"
  else
    fail "bandit reported findings; run: $PY -m bandit -r app"
  fi
else
  skip "no app directory or bandit unavailable"
fi

say "Dependency audit (pip-audit)"
if [ -n "$PY" ] && [ -f requirements.txt ]; then
  if "$PY" -m pip_audit -r requirements.txt --disable-pip >/dev/null 2>&1; then
    pass "no known vulnerabilities in the pinned tree"
  else
    fail "pip-audit reported findings"
  fi
else
  skip "no requirements.txt or pip-audit unavailable"
fi

say "Dependency pins carry hashes"
if [ -f requirements.txt ]; then
  if grep -q -- "--hash=" requirements.txt; then
    pass "hashes present"
  else
    fail "requirements.txt has no hashes; compile with --generate-hashes"
  fi
else
  skip "no requirements.txt"
fi

say "Software bill of materials present and newer than the pins"
if [ -f sbom.json ] && [ -f requirements.txt ]; then
  if [ sbom.json -nt requirements.txt ]; then
    pass "sbom.json is current"
  else
    fail "sbom.json is older than requirements.txt; regenerate it"
  fi
else
  skip "no sbom.json"
fi

say "Workflow actions pinned to commit hashes"
WF=$(ls .github/workflows/*.yml 2>/dev/null || true)
if [ -n "$WF" ]; then
  LOOSE=$(grep -hE "^\s*uses:" $WF | grep -vE "@[0-9a-f]{40}" || true)
  if [ -z "$LOOSE" ]; then
    pass "every action pinned by hash"
  else
    fail "these actions are pinned by tag:"; printf '%s\n' "$LOOSE" | sed 's/^/        /'
  fi
else
  skip "no workflow files"
fi

say "Container base images pinned by digest"
if [ -f Dockerfile ]; then
  LOOSE=$(grep -E "^FROM " Dockerfile | grep -v "@sha256:" || true)
  if [ -z "$LOOSE" ]; then
    pass "every base image pinned by digest"
  else
    fail "these base images are pinned by tag:"; printf '%s\n' "$LOOSE" | sed 's/^/        /'
  fi
else
  skip "no Dockerfile"
fi

say "Image vulnerabilities with an available fix (trivy)"
if command -v trivy >/dev/null 2>&1 && [ -f Dockerfile ]; then
  IMG="verify-$$"
  if docker build -q -t "$IMG" . >/dev/null 2>&1; then
    if trivy image --quiet --ignore-unfixed --severity HIGH,CRITICAL --exit-code 1 "$IMG" >/dev/null 2>&1; then
      pass "no fixable high or critical findings"
    else
      fail "fixable findings; run: trivy image --ignore-unfixed --severity HIGH,CRITICAL $IMG"
    fi
    docker rmi -f "$IMG" >/dev/null 2>&1
  else
    skip "image build failed"
  fi
else
  skip "trivy or Dockerfile unavailable"
fi

say "Committed environment file"
if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  fail ".env is tracked and must never be"
else
  pass ".env is not tracked"
fi

printf '\n'
if [ "$FAILED" -eq 0 ]; then
  echo "All executed checks passed. Skipped checks are not passes; install the tool or run them by hand."
else
  echo "One or more checks failed. Fix or formally accept each finding before release."
fi
exit "$FAILED"
