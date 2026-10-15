# ADR-001 — Zaman ölçeği ve koordinat çerçevesi sözleşmesi

| Alan | Değer |
|---|---|
| Durum | **Accepted** |
| Tarih | 2026-10-15 |
| İlgili spec | [SPEC-001](../specs/SPEC-001-skyfield-time-scale.md) |
| Karar sahibi | proje sahibi (PR onayı ile) |

## Bağlam
`EphemerisPort` iki implementasyona sahip (Skyfield = üretim, swisseph = oracle).
Skyfield adapter float JD girdisini `ts.tt_jd` ile TT olarak yorumluyordu; bu,
ΔT (≈69 s) kaybına ve Ay'da −40″ sapmaya yol açtı. Önceki bir teşhis ayrıca
ekliptik çerçevenin J2000 olduğunu iddia etti; ölçüm bunun yanlış olduğunu gösterdi.

## Karar
1. Port'a verilen **float JD daima JD(UT1)**'dir (swiss `*_ut` fonksiyonlarıyla aynı).
2. **datetime** UTC'dir; naive datetime UTC kabul edilir. Yerel saat → UTC dönüşümü
   portun **dışında** (çağıran katmanda, tz veritabanıyla) yapılır.
3. UT1→TT dönüşümü yalnızca kütüphanenin ΔT tablosuyla yapılır; sabit ΔT yasaktır.
4. Tropik boylam: yer-merkezli, **geometrik** (ışık-zamanı/aberasyon yok),
   **true ecliptic & equinox of date** (nutasyon dahil). Sidereal = tropik − ayanamsa.
5. Skyfield'da `ts.tt_jd` yalnız gerçekten TT olan sayılarla çağrılır (ör. `time.tt ± δ`).

## Sonuçlar
- Olumlu: Oracle ile 41 epoch'ta ≤2″; sözleşme tek yerde yazılı.
- Maliyet: Görünür (apparent) pozisyon isteyen gelecekteki bir özellik (ör. gözlem
  amaçlı) ayrı bir ADR gerektirir.
- Kilitleyen testler: `tests/test_skyfield.py::test_time_scale_contract_*`,
  `tests/verify/test_foundation_grid.py::test_longitude_vs_swiss`.

## Değerlendirilen alternatifler
| Alternatif | Neden reddedildi |
|---|---|
| Sabit ΔT = 64 s | 1901'de 55 s hata (ΔT 9.3 s) |
| `ecliptic_J2000_frame` + elle presesyon/nutasyon matrisi | Gereksiz: `ecliptic_frame` zaten of-date; J2000 kullanımı −1318″ (2026) üretir |
| Görünür pozisyon (aberasyonlu) | Jyotish yazılımlarının (PyJHora/JHora) çoğu ile hizalama spec'te ayrıca karara bağlanmalı; şimdilik oracle sözleşmesi geometrik |
