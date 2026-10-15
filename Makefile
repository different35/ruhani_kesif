# Standart komut yüzeyi — yerelde, devcontainer'da, ajan oturumunda ve CI'da AYNI hedefler.
# Ayrıntı: CONTRIBUTING.md · docs/process/TEST_STANDARD.md

VENV ?= .venv
PY   := $(VENV)/bin/python

.PHONY: help setup lint license test verify check gate mutation clean

help:            ## Hedefleri listele
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

setup:           ## .venv'i kur/güncelle (idempotent)
	@scripts/setup-dev.sh

lint: setup      ## ruff (yalnız hata sınıfları; ruff.toml)
	$(PY) -m ruff check engine tests

license: setup   ## Lisans bekçisi: üretim motoru swisseph import etmez (TEST_STANDARD §1)
	@if grep -nE '^\s*(import|from)\s+swisseph' engine/skyfield_adapter.py; then \
	  echo "HATA: engine/skyfield_adapter.py swisseph import ediyor"; exit 1; fi
	@echo "license guard OK"

test: setup      ## Hızlı birim/sözleşme testleri (oracle ızgarası hariç)
	$(PY) -m pytest -q --ignore=tests/verify

verify: setup    ## Oracle ızgarası (tests/verify)
	$(PY) -m pytest -q tests/verify

check: lint license  ## PR öncesi zorunlu: lint + lisans + TÜM testler (make gate bunu temiz kopyada koşar)
	$(PY) -m pytest -q

gate:            ## MERGE ÖNCESİ ZORUNLU (ADR-003): commit'i temiz kopyada doğrula + kanıt raporu. SHA=<commit>
	@scripts/ci-gate.sh $(or $(SHA),HEAD)

mutation: setup  ## SPEC-001 mutasyon örneği: kırmızı beklenir, dosya geri alınır
	@sed -i 's/return self._ts.ut1_jd(jd_ut)/return self._ts.tt_jd(jd_ut)/' engine/skyfield_adapter.py
	@$(PY) -m pytest -q | tail -1; git checkout -- engine/skyfield_adapter.py
	@echo "(geri alındı) — beklenen: 'N failed' satırı, N > 0"

clean:           ## Önbellekleri sil (venv kalır)
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache
