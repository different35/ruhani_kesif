#!/usr/bin/env bash
# Yerel CI kapısı (ADR-003) — GitHub Actions yerine merge öncesi ZORUNLU kontrol.
#
#   scripts/ci-gate.sh            # HEAD'i doğrula
#   scripts/ci-gate.sh <sha|ref>  # belirli commit'i doğrula (PR'ın son commit'i)
#
# Ne yapar:
#   1. Hedef commit'i GEÇİCİ, temiz bir çalışma kopyasına çıkarır (git worktree) —
#      çalışma dizinindeki commit'lenmemiş değişiklikler ve mevcut .venv KULLANILMAZ.
#   2. Orada sıfırdan .venv kurar (scripts/setup-dev.sh) ve `make check` koşar.
#   3. origin/main'in bu commit'in atası olup olmadığını denetler (dal güncel mi?).
#   4. PR'a yapıştırılacak kanıt raporunu basar; çıkış kodu = kapı sonucu.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="${1:-HEAD}"
cd "$ROOT"

SHA="$(git rev-parse --verify "$REF^{commit}" 2>/dev/null)" || { echo "[gate] commit bulunamadı: $REF" >&2; exit 2; }
WORK="$(mktemp -d "${TMPDIR:-/tmp}/ci-gate.XXXXXX")"
LOG="$WORK/check.log"
cleanup() { git -C "$ROOT" worktree remove --force "$WORK/src" >/dev/null 2>&1; rm -rf "$WORK"; }
trap cleanup EXIT

echo "[gate] commit $SHA → temiz kopya: $WORK/src" >&2
git worktree add --detach -q "$WORK/src" "$SHA"

# Dal güncelliği: merge sonrası main'in ağacı ile test edilen ağaç aynı olsun diye.
git fetch -q origin main 2>/dev/null || true
if git merge-base --is-ancestor origin/main "$SHA" 2>/dev/null; then
  UP_TO_DATE="evet (origin/main @ $(git rev-parse --short origin/main) atası)"
else
  UP_TO_DATE="HAYIR — önce: git merge origin/main"
fi

start=$(date +%s)
( cd "$WORK/src" && VENV="$WORK/venv" scripts/setup-dev.sh && make check VENV="$WORK/venv" ) >"$LOG" 2>&1
rc=$?
dur=$(( $(date +%s) - start ))

PY_VER="$("$WORK/venv/bin/python" --version 2>/dev/null || echo '?')"
REQ_HASH="$(sha256sum "$WORK/src/requirements-test.txt" | cut -c1-12)"
SUMMARY="$(grep -E '^[0-9]+ (passed|failed)|passed|failed|error' "$LOG" | tail -1)"
LINT="$(grep -E 'All checks passed|Found [0-9]+ error' "$LOG" | tail -1)"
LIC="$(grep -E 'license guard OK|HATA:' "$LOG" | tail -1)"

if [[ $rc -eq 0 && "$UP_TO_DATE" == evet* ]]; then RESULT="GEÇTİ ✅"; else RESULT="KALDI ❌"; fi

cat <<EOF
### Yerel CI kapısı — $RESULT
| Alan | Değer |
|---|---|
| Commit | \`$SHA\` |
| main ile güncel | $UP_TO_DATE |
| Ortam | sıfırdan venv · $PY_VER · requirements-test.txt sha256:$REQ_HASH |
| ruff | ${LINT:-?} |
| Lisans bekçisi | ${LIC:-?} |
| pytest | ${SUMMARY:-?} |
| Süre | ${dur} sn · \`scripts/ci-gate.sh $SHA\` |
EOF

if [[ $rc -ne 0 ]]; then
  echo; echo "--- make check çıktısının sonu ---"; tail -40 "$LOG"
fi
[[ "$RESULT" == GEÇTİ* ]]
