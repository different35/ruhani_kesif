# BACKLOG — Gist'teki A'dan Z'ye planın (BÖLÜM 12) kalem kalem uygulanma durumu

Kaynak: https://gist.github.com/different35/2e26066e6a025e3228568ef8648428e8
(depo kopyası: `data/gist_roadmap.md`)

Bu dosya **tek gerçeklik kaynağıdır**: her madde ya yapıldı (kod + test kanıtı),
ya yapılmadı. Plan/proza belgesi yoktur; yalnızca üretilen kod ve açık iş var.

## P0 — İstihbarat + karar

| # | Madde (gist §12.1) | Durum | Kanıt |
|---|---|---|---|
| P0-1 | Kaynak envanteri indirilsin (gist + PyJHora + pyhora2 features_per_book) | ✅ | `data/gist_roadmap.md` (1289 satır), `data/features_naturalstupid.txt` = `data/features_pyhora2.txt` (diff: özdeş, 35 satır) |
| P0-2 | PyJHora + pyswisseph kurulumu ve import doğrulaması | ✅ | `requirements.txt`; `import jhora` OK (swisseph 2.10.03) |
| P0-3 | Swiss Ephemeris lisans kararı (AGPL vs ticari) | ⬜ İŞ | Hukuki karar; mimari önlem alındı → P1-1 |
| P0-4 | Rakip saha protokolü (≥60 kanıt kaydı) | ⬜ | manuel saha işi |
| P0-5 | 40 SKU'dan MVP 6 seçimi (A1,A2,B2,C1,C3,G3) | ✅ onaylı kaynakta | gist BÖLÜM 4 sonu |

## P1 — Hesaplama çekirdeği

| # | Madde | Durum | Kanıt |
|---|---|---|---|
| P1-1 | **EphemerisPort** soyutlama katmanı (gist §1.2 "zorunlu mimari") | ✅ | `engine/ephemeris_port.py` — longitude/houses/ayanamsa/events |
| P1-2 | **SwissEphemerisAdapter** implementasyonu | ✅ | `engine/swiss_adapter.py` |
| P1-3 | Çerçeve ayrımı testi (sidereal/tropical, ayanamsa tutarlılığı) | ✅ | `tests/test_engine.py::test_single_source_of_truth` — 7 gezegende `sid == trop − ay` < 1e-9 |
| P1-4 | Nakshatra + Pada fakt üretimi | ✅ | `engine/nakshatra.py` + sınır testleri |
| P1-5 | **Dasha timeline** (Vimshottari MD+AD, balance dahil) | ✅ | `engine/dasha.py` — 90 düğüm, süre toplamı kontrolü testte |
| P1-6 | Transit tarayıcı (ingress olayları, binary refine ±~2sa) | ✅ | `events()` + `test_events_ingress_reference` (Güneş 2026-03-14 Kumbha→Meena) |
| P1-7 | Ev sistemi (Placidus/Koch/Whole/Equal/Sri-Panchika) | ✅ | `houses()` + `test_houses_count_and_range` |
| P1-8 | AstronomyEngine/Skyfield adaptörleri (lisanssız yedek) | 🟠 kısmi | `engine/skyfield_adapter.py`; boylam ≤2″ **doğrulandı** (SPEC-001); Lagna 14–66″ → SPEC-002; üretim doğuş çözücüsü yok → SPEC-003 |
| P1-9 | Varga seti (D1–D60) | ⬜ | JH adaptörü üzerinden |
| P1-10 | 100 golden chart'ta %100 sayısal doğruluk | 🟠 kısmi | 8 test geçti; golden chart seti oluşturulmadı |

## Uygulama sırasında KEŞFEDİLEN, gist'te olmayan kritik gerçekler
(bunlar sessiz veri hatalarıydı; canlı doğrulandı):

1. **pyswisseph 2.10 `get_ayanamsa_ut` float döner** (tuple değil) ve sabitler ham sayı olarak güvenilmez → `SIDM_*` sabitleriyle eşleme + J2000 Lahiri = 23.8571° referans testi.
2. **`calc_ut(FLG_SIDEREAL)` ile `get_ayanamsa_ut` arasında ~0.004° epoch düzeltme farkı var** → nakshatra sınırında yanlış pada üretir. Çözüm: tek doğru kaynak kuralı (`sid = trop − ayanamsa`).
3. **`jhora.const` importu global swisseph sid-mode'unu bozuyor** → adapter her hesapta modu yeniden kuruyor (regresyon testi `import jhora` ile çalışıyor).

## P2 — Kural tabanı + hüküm | P3 — Sima CV | P4 — Agent/UX | P5 — Monetizasyon | P6 — Flywheel
⬜ Henüz kod yok. Tur sırası ve bağımlılıklar: **[docs/specs/INDEX.md](docs/specs/INDEX.md)** (SPEC-002 → SPEC-011).
Süreç: [docs/process/DEVELOPMENT_PROCESS.md](docs/process/DEVELOPMENT_PROCESS.md).

## Doğrulama komutu
```
uv venv -p 3.12 .venv && uv pip install -p .venv/bin/python -r requirements-test.txt
.venv/bin/python -m pytest -q   # 150 passed (SPEC-001)
```
