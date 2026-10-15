# SPEC-001 — Skyfield adapter zaman ölçeği (UT1→TT) düzeltmesi ve temel ızgaranın onarımı

| Alan | Değer |
|---|---|
| Durum | **Done** |
| Tür | Hata düzeltmesi + test altyapısı onarımı |
| Modül(ler) | `engine/skyfield_adapter.py`, `tests/verify/test_foundation_grid.py`, `tests/test_skyfield.py` |
| Bağımlılık | — (temel katman) |
| Oracle | pyswisseph 2.10.3.2 (Moshier), skyfield 1.55, de440s |
| Dal | `claude/elegant-lovelace-hysdf5` (taban: `vimshottari-dasha-bug-fix-af94a` @ 49cd9b7) |
| Tarih | 2026-10-15 |

## 1. Amaç

`SkyfieldAdapter.longitude()` 1901–2031 aralığında 7 cisimde swiss
`FLG_TROPICAL|FLG_TRUEPOS` oracle'ına gezegenlerde ≤2″, Ay'da ≤5″ uysun; temel
doğrulama ızgarası (`tests/verify/`) tamamen koşar ve yeşil olsun.

## 2. Bağlam

Önceki turun devir notu: *"56 test hatasının kök nedeni `_geo_true_lon`'da
J2000-mean ekliptik yerine true ecliptic kullanılmaması ve UT→TT dönüşümündeki
ΔT eksikliğidir. Reçete: UT+ΔT ile TT + ICRS→true ecliptic of-date matris dönüşümü."*

Bu spec o teşhisi **yeniden ölçtü**; teşhisin yarısı doğru, yarısı yanlış çıktı (§3).

## 3. Keşif / kök neden kanıtı

**G0 — Yeniden üretim:** `python -m pytest -q` → `56 failed, 92 passed`
(38 × `test_longitude_vs_swiss`, 18 × `test_sunrise_vs_swiss`).

| # | Hipotez | Deney (yalnız bu değişken) | Ham sonuç | Karar |
|---|---|---|---|---|
| H1 | `ts.tt_jd(jd_ut)` UT'yi TT'ye çevirmiyor (ΔT kaybı) | `tt_jd(jd).ut1 − jd` ölç | 1901: −9.34 s · 1999: −63.47 s · 2026: −69.11 s (= −ΔT) | **Doğrulandı** |
| H1b | `tt_jd`→`ut1_jd` sapmayı giderir | aynı çerçeve, zaman ölçeği değişti | jd 2451182.5 Ay: −36.12″ → +0.21″; Güneş: −2.71″ → −0.02″ | **Doğrulandı** |
| H2 | Çerçeve J2000-mean; true-of-date'e geçmek gerekir | `almanac.ecliptic_frame is framelib.ecliptic_frame` | `True` → zaten **true ecliptic & equinox of date** | **Reddedildi** |
| H2b | (karşı-kanıt) J2000 çerçevesine geçilirse | `ecliptic_J2000_frame` ile aynı ölçüm | 1999: +59.3″ · 2026: −1318.4″ · 1901: +4614.7″ | J2000'e geçmek felaket olurdu |
| H3 | 18 sunrise hatası adapter kaynaklı | Hata mesajı | `AttributeError: 'Timescale' object has no attribute 'delta_t'` | **Reddedildi** — test helper hatası |
| H3b | Helper başka gizli hatalar taşıyor | Sırayla düzelt-koş | (a) `altaz()` → `(alt, az, d)`; test `_az, al, _d` açıyordu (azimut = irtifa sanılıyor) · (b) `Time.ut1_jd` yok, doğrusu `Time.ut1` · (c) pencere `[jd−½, jd+½]` önceki doğuşu yakalıyor, swiss `rise_trans` jd sonrası ilk doğuşu döndürür → ≈86400 s fark | **Doğrulandı** (3 ek hata) |

Ham ölçüm tablosu (yay-saniyesi, motor − oracle; `cur` = düzeltme öncesi):

```
jd=2451182.5  ΔT=63.47s
   sun      cur= -2.712  ut1+date= -0.017  ut1+J2000= +59.285
   moon     cur=-36.119  ut1+date= +0.212  ut1+J2000= +59.507
   mercury  cur= -3.806  ut1+date= -0.009  ut1+J2000= +59.292
jd=2461070.0  ΔT=69.11s
   sun      cur= -2.918  ut1+date= +0.006  ut1+J2000=-1318.394
   moon     cur=-40.693  ut1+date= +1.272  ut1+J2000=-1317.096
```

## 4. Veri sözleşmesi (bu spec ile sabitlenen)

| Öğe | Sözleşme |
|---|---|
| `date: float/int` | **JD(UT1)** — swiss `calc_ut` ile aynı anlam → `ts.ut1_jd(jd)` |
| `date: datetime` (aware) | UTC'ye çevrilir → `ts.from_datetime` (artık saniye dahil) |
| `date: datetime` (naive) | **UTC kabul edilir** |
| TT | skyfield ΔT tablosu (sabit 64 s **yok**; `_UT_TO_TT_DAYS` kaldırıldı) |
| Çerçeve | `ecliptic_frame` = true ecliptic & equinox of date (değişmedi) |
| Pozisyon tipi | geometrik (ışık-zamanı ve aberasyon yok) |

Karar kaydı: [ADR-001](../adr/ADR-001-time-scale-contract.md).

## 5. Tasarım / değişiklik

- `SkyfieldAdapter._time`: `ts.tt_jd(jd)` → `ts.ut1_jd(jd)` (float); datetime yolu `ts.from_datetime`.
- `_jd_ut` değişmedi (`time.ut1`) — artık girdiyle birebir aynı JD'yi döndürür.
- Yanlış docstring iddiaları (tt_jd UT→TT çevirir; çerçeve J2000-mean'dir) düzeltildi.
- Test helper: `TS.delta_t` → `TS.ut1_jd(jd).tt`; `altaz()` açılımı; `.ut1_jd` → `.ut1`; pencere `[jd, jd+1]`.
- **Yapılmayan:** Önceki reçetedeki "ICRS→true ecliptic matris dönüşümü" — H2 reddedildi.

## 6. Kabul kriterleri

| AC | Kriter | Doğrulama | Durum |
|---|---|---|---|
| AC-1 | 41 epoch × 7 cisim: gezegen ≤2″, Ay ≤5″ | `test_longitude_vs_swiss` (41 param) | ✅ max: Sun 0.061″, Moon 1.978″, Mer 0.103″, Ven 0.265″, Mar 0.542″, Jup 0.485″, Sat 0.397″ |
| AC-2 | float girdi UT1; 2026 ΔT 68–71 s | `test_time_scale_contract_float_is_ut1` | ✅ |
| AC-3 | aware/naive/+03:00 datetime aynı TT; |UT1−UTC| < 0.9 s | `test_time_scale_contract_datetime_is_utc` | ✅ |
| AC-4 | Sunrise ızgarası (6 konum × 3 epoch) ≤60 s | `test_sunrise_vs_swiss` | ✅ max |Δ| 2.4 s |
| AC-5 | Tüm suite yeşil | `python -m pytest -q` | ✅ `150 passed` |
| AC-6 | Mutasyon: düzeltme geri alınınca testler kırılır | §10 | ✅ 38 (grid) + 1 (birim) kırıldı |

## 7. Test planı

Sözleşme hizalama tablosu: [TEST_STANDARD §4](../process/TEST_STANDARD.md#4-sözleşme-hizalama-tablosu-her-oracle-testinin-başına-zorunlu).
Yeni L2 regresyon testleri: `tests/test_skyfield.py::test_time_scale_contract_*`.

## 8. Kapsam dışı (bulgular → kuyruk)

| Bulgu | Ölçüm | Önerilen |
|---|---|---|
| Lagna (Asc) hassasiyeti swiss'e karşı 14″ (φ=0) … 66″ (φ=60) | 7 enlem × 3 epoch × 12 saat × 5 boylam | SPEC-002: GAST (nutasyon RA) + true obliquity |
| Asc test eşiği 0.5° (≈1800″) — ölçülenin 27 katı gevşek | `test_houses_asc_mc_within_tolerance` | SPEC-002 ile ≤5″'e daralt |
| Sunrise yalnız **test helper'ında** var; üretim API'sinde doğuş/batış yok | grep | SPEC-003 (panchanga önkoşulu) |
| `tests/test_skyfield.py` boylam/node testleri 0.02°/0.01° gevşek | — | SPEC-002'de ızgara eşiklerine çek |
| Olay zamanları (ingress/station) yalnız gün düzeyinde test ediliyor | — | Kuyruk |
| `requirements.txt` PyJHora+kerykeion çekiyor ama suite onlara ihtiyaç duymuyor; sistem Python'unda pyswisseph derlenmiyor | — | `requirements-test.txt` + CI eklendi (bu tur) |

## 9. Riskler

| Risk | Etki | Önlem |
|---|---|---|
| Naive datetime artık UTC kabul ediliyor (önce de `_jd_of` UTC kabul ediyordu) | Davranış değişikliği yok | AC-3 testi |
| Skyfield ΔT tablosu ileri tarihlerde (2030+) tahmin | ±1 s düzeyi | Belgelendi; kernel kapsamı 2150 |

## 10. Kanıt kaydı

```
$ python -m pytest -q                        # düzeltme öncesi
56 failed, 92 passed in 2.46s
$ python -m pytest -q                        # düzeltme sonrası
150 passed in 5.46s
$ sed -i 's/return self._ts.ut1_jd(jd_ut)/return self._ts.tt_jd(jd_ut)/' engine/skyfield_adapter.py
$ python -m pytest -q                        # mutasyon (tüm suite)
39 failed, 111 passed                         # 38 grid + 1 birim regresyon testi
$ git checkout -- engine/skyfield_adapter.py && python -m pytest -q
150 passed
```

## 11. Devir notu

```
DEVİR NOTU — SPEC-001
Kapanan: AC-1..AC-6 hepsi geçti.
Kanıt:   150 passed; mutasyon 38+1 kırmızı.
Açık bulgular: Lagna 14–66″ (SPEC-002), üretim sunrise yok (SPEC-003),
               gevşek eşikler (SPEC-002), olay zamanı hassasiyeti (kuyruk).
Sonraki tur önerisi: SPEC-002 Lagna/ev hassasiyeti — varga (D60 = 0.5° dilim)
               ve bhava_chalit bunun üzerine kurulur.
Düzeltilen yanlış iddia: "J2000-mean ekliptik → true ecliptic matrisi gerekir" (H2 reddedildi).
Doğrulanmamış iddialar: yok (bu spec kapsamında).
```
