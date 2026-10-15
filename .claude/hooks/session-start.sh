#!/bin/bash
# Claude Code bulut oturumu başlangıcı: standart ortamı kur ve oturuma .venv'i tanıt.
# Tek kaynak scripts/setup-dev.sh (yerel/devcontainer/CI ile aynı). Senkron çalışır:
# ajan test koşmadan önce bağımlılıkların hazır olması garanti edilir.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
scripts/setup-dev.sh

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export VIRTUAL_ENV=\"$CLAUDE_PROJECT_DIR/.venv\""
    echo "export PATH=\"$CLAUDE_PROJECT_DIR/.venv/bin:\$PATH\""
  } >> "$CLAUDE_ENV_FILE"
fi
