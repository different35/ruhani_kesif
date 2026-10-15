#!/usr/bin/env bash
# Standart geliştirme ortamı kurulumu — TEK KAYNAK.
# Yerel makine, devcontainer, Claude Code bulut oturumu (SessionStart hook) ve CI
# aynı betiği kullanır; ortam farkı bu yüzden oluşmaz.
#
#   scripts/setup-dev.sh            # .venv yoksa kurar, requirements değiştiyse günceller
#   FORCE=1 scripts/setup-dev.sh    # sıfırdan kur
#
# Notlar:
# - Python 3.12 hedeflenir (.python-version). Debian/Ubuntu sistem Python'unda
#   pyswisseph derlemesi setuptools 'install_layout' hatası verir → her zaman izole venv.
# - uv varsa kullanılır (hızlı); yoksa python -m venv + pip.
# - İdempotent: requirements-test.txt'nin hash'i .venv/.req-hash ile karşılaştırılır.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${VENV:-$ROOT/.venv}"
REQ="$ROOT/requirements-test.txt"
PY_VERSION="$(cat "$ROOT/.python-version" 2>/dev/null || echo 3.12)"
HASH_FILE="$VENV/.req-hash"
req_hash="$(sha256sum "$REQ" | cut -d' ' -f1)"

log() { echo "[setup-dev] $*" >&2; }

if [[ "${FORCE:-0}" == "1" ]]; then
  log "FORCE=1 → $VENV siliniyor"
  rm -rf "$VENV"
fi

if [[ -x "$VENV/bin/python" && -f "$HASH_FILE" && "$(cat "$HASH_FILE")" == "$req_hash" ]]; then
  log "ortam güncel ($VENV)"
  exit 0
fi

if command -v uv >/dev/null 2>&1; then
  if [[ ! -x "$VENV/bin/python" ]]; then
    log "uv ile venv oluşturuluyor (python $PY_VERSION)"
    uv venv -q -p "$PY_VERSION" "$VENV"
  fi
  log "bağımlılıklar kuruluyor (uv)"
  uv pip install -q -p "$VENV/bin/python" -r "$REQ"
else
  if [[ ! -x "$VENV/bin/python" ]]; then
    PY_BIN="$(command -v "python$PY_VERSION" || command -v python3)"
    log "venv oluşturuluyor ($PY_BIN)"
    "$PY_BIN" -m venv "$VENV"
  fi
  log "bağımlılıklar kuruluyor (pip)"
  "$VENV/bin/python" -m pip install -q --upgrade pip
  "$VENV/bin/python" -m pip install -q -r "$REQ"
fi

echo "$req_hash" > "$HASH_FILE"
log "hazır: $("$VENV/bin/python" --version), $("$VENV/bin/python" -c 'import skyfield, swisseph; print("skyfield", skyfield.__version__, "| pyswisseph", swisseph.version)')"
