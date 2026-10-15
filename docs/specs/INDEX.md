# Spec Kayıt Defteri ve Tur Kuyruğu

Her tur bir spec'tir. Numara verildikten sonra değişmez; iptal edilen spec
`Superseded` olarak kalır. Şablon: [SPEC_TEMPLATE.md](SPEC_TEMPLATE.md).

## 1. Kayıt

| ID | Başlık | Tür | Durum | PR |
|---|---|---|---|---|
| [SPEC-001](SPEC-001-skyfield-time-scale.md) | Skyfield zaman ölçeği (UT1→TT) + temel ızgara onarımı | Düzeltme | **Done** | bu tur |
| SPEC-002 | Lagna / ev cuspleri hassasiyeti (GAST + true obliquity) | Düzeltme | Planned | — |
| SPEC-003 | Üretim doğuş/batış çözücüsü (`engine/` API) | Yeni modül | Planned | — |
| SPEC-004 | `panchanga.py` — tithi, vara, nakshatra, yoga, karana | Yeni modül | Planned | — |
| SPEC-005 | Graha durumu katmanı — dignity, maitri, combustion, drishti, yuddha | Yeni modül | Planned | — |
| SPEC-006 | `bhava_chalit.py` | Yeni modül | Planned | — |
| SPEC-007 | `ashtakavarga.py` — BAV + SAV + şodhana | Yeni modül | Planned | — |
| SPEC-008 | `yoga_rules.py` — kural şeması + ilk yoga seti | Yeni modül | Planned | — |
| SPEC-009 | `avasthas.py` | Yeni modül | Planned | — |
| SPEC-010 | `shadbala.py` — 6 bala bileşeni | Yeni modül | Planned | — |
| SPEC-011 | `ishta_kashta.py` | Yeni modül | Planned | — |

## 2. Bağımlılık grafiği

```
SPEC-001 (zaman ölçeği) ✅
   ├── SPEC-002 Lagna hassasiyeti ──┬── SPEC-006 bhava_chalit
   │                                └── (varga D1–D60, mevcut engine/varga.py)
   ├── SPEC-003 doğuş/batış ──────────── SPEC-004 panchanga
   └── SPEC-005 graha durumu ──┬── SPEC-007 ashtakavarga
                               ├── SPEC-008 yoga_rules
                               ├── SPEC-009 avasthas
                               └── SPEC-010 shadbala ◀── (SPEC-003, SPEC-004, SPEC-006)
                                        └── SPEC-011 ishta_kashta
```

## 3. Sıra kararı — Sahip onayı gerekiyor

Önceki turda önerilen sıra: `yoga_rules → ashtakavarga → avasthas → panchanga → bhava_chalit → ishta_kashta → shadbala`.

Bağımlılık analizine göre bu sıra **iki yerde kırılıyor**:

1. `ishta_kashta`, Shadbala'nın **Uchcha bala** ve **Cheshta bala** bileşenlerinden
   hesaplanır → `shadbala`'dan **önce** yazılamaz.
2. `yoga_rules`, `avasthas`, `ashtakavarga` ortak bir **graha durumu** katmanına
   (ev sahipliği, dignity, dostluk, aspekt, yanma) ihtiyaç duyar; bu katman
   şu an kodda yok (VERIFICATION: "state.py — kod yok"). Her modül bunu kendi
   içinde yeniden yazarsa üç ayrı hata kaynağı oluşur.
3. `panchanga` ve Shadbala'nın **Kala bala**sı doğuş zamanına bağlıdır; üretim
   kodunda doğuş çözücüsü yok (yalnız test helper'ında).

**Önerilen sıra:** §1 tablosundaki numara sırası (002 → 011). Önceki listedeki
yedi modülün tamamı korunur; yalnızca üç önkoşul (002, 003, 005) eklenir ve
`ishta_kashta` `shadbala`'nın arkasına alınır.

## 4. Her planlı spec için DoR eksikleri (spec yazılmadan önce kapanmalı)

| Spec | Oracle / kaynak | DoR eksiği |
|---|---|---|
| 002 | swiss `houses_ex` | Hedef eşik kararı (öneri ≤5″) |
| 003 | swiss `rise_trans` | Doğuş tanımı kararı: disk merkezi mi üst kenar mı, refraksiyon var mı (Hindu takvimi geleneği genelde **üst kenar + refraksiyonsuz** veya **merkez**; PyJHora varsayılanı spec'te sabitlenecek) |
| 004 | PyJHora `panchanga` | PyJHora sürümü sabitlenmeli; tithi/karana sınır vakaları listesi |
| 005 | BPHS + PyJHora | Dostluk tablosu (naisargika + tatkalika), yanma orbları kaynağı, yuddha tanımı seçimi |
| 006 | PyJHora / Sripati | Bhava tanımı seçimi (Sripati = dörtte-bölme; mevcut `_cusps_from_asc_mc` zaten bu geometri) |
| 007 | PyJHora `ashtakavarga` | Değişmez: SAV toplamı 337; BAV toplamları (Güneş 48 …) |
| 008 | BPHS bölüm/şloka + PyJHora | Kural şeması (koşul DSL'i) ve ilk yoga seti (öneri: Pancha Mahapurusha 5 yoga + Gaja Kesari) |
| 009 | Kitap + JHora GUI | **Kaynak golden gerekli** — PyJHora'da implementasyon yok (VERIFICATION kaydı) |
| 010 | PyJHora `strength` | 6 bileşen ayrı ayrı oracle'lanır; Rupa birimi |
| 011 | PyJHora | 010 Done |
