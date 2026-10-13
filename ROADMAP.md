# ROADMAP.md — Fazlar (P0–P6) ve Çıkış Ölçütleri

> Kaynak: gist BÖLÜM 12 (`data/gist_roadmap.md` §12.1). Kalem kalem uygulama
> durumu **BACKLOG.md**'dedir; bu dosya faz takvimi + çıkış ölçütlerini taşır.
> PRODUCT.md §5 (DoD) ile çapraz referanslıdır.

## Durum Özeti (canlı doğrulama: `python -m pytest -q`)

| Faz | Durum | Not |
|---|---|---|
| P0 | 🟠 %75 | Envanter+kurulum+SKU onayı ✅; **lisans kararı (P0-3) ve rakip saha (P0-4) İŞ** |
| P1 | 🟠 ~%85 | P1-1..P1-7 ✅ (swiss denetim bulguları kapatıldı, testler yeşil); **P1-8/P1-9/P1-10 açık** |
| P2–P6 | ⬜ | Kod yok; bağımlılık sırası aşağıda |

## P0 — İstihbarat + Karar (hedef: 2 hafta)
**Çıkış ölçütü:** ≥60 kanıt kaydı · imzalı lisans kararı · 40 SKU'dan 6 MVP seçimi.
- [x] P0-1 kaynak envanteri (`data/`), P0-2 kurulum/import, P0-5 MVP 6 SKU onayı (A1,A2,B2,C1,C3,G3 — PRODUCT.md §4)
- [ ] **P0-3 Swiss Ephemeris lisans kararı (AGPL vs ticari)** — 🔴 kritik yol; mimari önlem (EphemerisPort) alındı, hukuki karar bekliyor
- [ ] P0-4 rakip saha protokolü (≥60 kanıt) — manuel iş

## P1 — Hesaplama Çekirdeği (hedef: 4–6 hafta)
**Çıkış ölçütü:** 100 golden chart'ta %100 sayısal doğruluk · 7.380 düğüm timeline · çerçeve ayrımı test edilmiş.
- [x] P1-1 EphemerisPort · P1-2 SwissAdapter (denetim sonrası: TZ/julday cal parametresi, try/finally+lock ile global sidereal izolasyonu, ingress retrograd/pencere sınırı, ev sistemi/frame/mod doğrulamaları — hepsi düzeltildi ve regresyon testli)
- [x] P1-3 çerçeve testi · P1-4 Nakshatra+Pada · P1-5 Dasha timeline · P1-6 transit/ingress · P1-7 ev sistemleri
- [ ] **P1-8 Skyfield yedek adaptörü** — longitude/ayanamsa/events kalibre ✅; Ascendant formülü quadrant-fix bekliyor + `tests/test_skyfield.py` yazılacak
- [ ] **P1-9 Varga seti (D1–D60)** — `engine/varga.py` iskelet; JHora parity testi yazılacak
- [ ] **P1-10 Golden chart seti (100)** — danışman panelinden veri bekliyor; hedef %100 sayısal eşleşme
- **Kaldığımız nokta:** P1-8 kapanışı → P1-9 testi → P1-10 → P1 çıkış ölçütü ilanı.

## P2 — Kural Tabanı + Hüküm Motoru (6–10 hafta)
**Giriş koşulu:** P1 çıkış ölçütü karşılanmış (golden chart doğruluğu).
**Çıkış ölçütü:** 100 uzman-onaylı vaka · atıf kapsama ≥%95 · "bilmiyorum" yolu çalışıyor.
- Kural şeması (JSON: koşul→hüküm→atıf→güven), 300–500 kural kaydı, atıf grafı, Horary motoru (C3), Muhurta tarayıcı (C2), çakışma politikası (Vedik↔Batı — A5).

## P3 — Sima CV (8–12 hafta, P2 ile paralel)
**Çıkış:** IoU ≥0.75 · ten rengi stratifiye doğrulama · ham görüntü saklanmıyor · KVKK ayrı rıza akışı. E1/E2 ancak burada açılır.

## P4 — Agent + UX + Hafıza (4–6 hafta)
**Çıkış:** time-to-first-aha <15 sn · desteksiz iddia <%1 · çapraz rapor çelişkisi <%2. Orchestration, MEM, Judge/Synthesizer ayrımı, interaktif harita, rectification sihirbazı (A6).

## P5 — Monetizasyon + Dağıtım (4 hafta)
**Çıkış:** ölçülmüş conversion + D30 retention + kanal bazlı CAC. Ödeme, paywall, WhatsApp/ManyChat hunisi, takvim/widget (G3), MCP (H4), A/B.

## P6 — Sürekli Flywheel
Haftalık kalite eval'i, kullanıcı geri bildirimi → kural revizyonu, veri seti büyümesi, B2B genişleme.

## Bağımlılık Sırası (kritik yol)
```
P0-3 lisans kararı ─┐
P1-8 (Asc fix+test) ─┼→ P1-9 (varga testi) → P1-10 (golden charts) → P1 BİTTİ
                    └→ P2 kural şeması → (P3 paralel CV) → P4 agent/UX → P5 gelir → P6 flywheel
```

## Risk Matrisi (gist §12.4)
| Risk | Seviye | Önlem / sahip olduğu faz |
|---|---|---|
| Swiss Ephemeris lisansı (AGPL/ticari) | 🔴 | P0-3 kararı; EphemerisPort + Skyfield/JHora yedeği (P1-8); alternatif adaptör geçişi tek başına yükümlülük çözmez — dağıtım modeliyle birlikte değerlendirilir |
| KVKK biyometrik veri | 🔴 | P3: on-device-first, ham görüntü yok, DPIA |
| CV veri kıtlığı | 🔴 | P3'ü P2 ile paralel başlat |
| LLM halüsinasyonu | 🔴 | P2 atıf zorunluluğu + P4 deterministik Judge + golden set |

## Doğrulama
```bash
pip install -r requirements.txt && python -m pytest -q   # tümü yeşil olmalı
```
