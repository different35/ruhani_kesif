# PRODUCT.md — Kapsam → Ürünleştirme → Planlama

> **Önce bu dosya okunur.** Kaynak strateji raporu: `data/gist_roadmap.md`
> (gist: https://gist.github.com/different35/2e26066e6a025e3228568ef8648428e8)
> Uygulama durumu tek gerçeklik kaynağı: **BACKLOG.md**. Faz takvimi: **ROADMAP.md**.

## 1. Vizyon ve Konumlanma

**Ürün:** "ruhani yolculuğunuza rehberlik" — Vedik (Jyotish) + Batı (natal/horary)
geleneklerini **tek doğruluk kaynaklı, deterministik bir hesaplama çekirdeği** ve
**atıf zorunlu bir kural/hüküm motoru** üzerine kuran kişisel zaman asistanı.

**Stratejik gerçek (gist §1):** Ham hesaplama API'si satmak değersizdir
(RoxyAPI emsali: 18+ alan, $39/ay). Değer üst katmanlarda: *hüküm, zamanlama,
kişiselleştirme, hafıza*. Farklılaşma ekseni: **"Aksiyon Zamanlayıcı"** —
kehanet değil, "ne zaman ne yapılır" ranked penceresi.

**Anti-hedefler:** Desteksiz iddia (halüsinasyon), sa-yı üretimi, kullanıcıyı
karanlık desenle aboneliğe itmek. Her hükmün kanıt paketi + atıf grafi vardır;
bilmiyorsak "belirsiz" deriz.

## 2. Kimlik ve Kullanıcı

- B2C çekirdek: 25–45, spiritüel merak, Türkçe konuşan pazar; fiyat hipotezleri ₺ bazlı (test edilecek hipotez, doğrulanmış pazar fiyatı değil).
- B2B faz 2: bağımsız astrolog/firasatçı (H2 Danışman Konsolu), medya/wellness app (H1/H3).
-Retention omurgası: Dasha eşiği + haftalık Aksiyon Zamanlayıcı kullanımı.

## 3. Mimari İlkeler (ürün kalitesini belirleyen teknik kararlar)

1. **EphemerisPort soyutlaması zorunludur** (`engine/ephemeris_port.py`): Swiss Ephemeris'in AGPL-3.0/ticari lisans riskine karşı JHora/Skyfield yedek adaptörleri aynı sözleşmeyi taşır. Lisans kararı dağıtım öncesi verilir; alternatif adaptöre geçiş tek başına lisans yükümlülüğünü çözmez — ayrı değerlendirilir.
2. **Tek doğruluk kaynağı:** `sidereal = tropical − ayanamsa`. Hesap yolları arasında ~0.004° epoch farkları nakshatra pada sınırını bozduğu için çok kaynaklı hesap yasaktır (canlı doğrulanmış sessiz veri hatası).
3. **Deterministik fakt katmanı:** LLM yalnızca sentez/yazım yapar; sayı, tarih, olay üretemez. Judge/synthesizer ayrımı ROADMAP P4'te.
4. **Global durum izolasyonu:** pyswisseph sidereal modu süreç-içi global'dir; adapter kilitle + try/finally ile korundu (swiss_adapter denetim bulguları kapatıldı, regresyon testleri `tests/test_engine.py`).

## 4. MVP — 6 SKU (gist §4 onaylı kesit)

| ID | SKU | Kaynak | Format | Katman / gelir |
|---|---|---|---|---|
| A1 | Doğum İzi (Batı natal özet) | KER+SW | İnteraktif SVG + 12 ev kartı | Ücretsiz (aktivasyon) |
| A2 | Vedik Kök (Lagna+Nakshatra+Pada) | JH | 1 sayfa + audio | Ücretsiz (first-aha <15 sn) |
| B2 | Aktif Dönem Raporu (MD+AD+PD) | JH+RULE | 4–6 sayfa + audio | Abonelik |
| C1 | **Aksiyon Zamanlayıcı** | JH+KER+RULE+CAL | Aksiyon seç → 7 günlük ranked pencere | **Abonelik çekirdeği** |
| C3 | Tek Soru (Horary) | KER+RULE | Soru → hüküm + gerekçe + zamanlama | Tek seferlik, yüksek marj |
| G3 | Kişisel Zaman Asistanı | C1 + takvim + widget + sınırlı soru | Uygulama kabuğu | 199–349₺/ay (hipotez) |

**Faz 2 ek:** E1, E2 (Sima CV) — veri seti hazır olduğunda. Kalan 32 SKU, kural tabanı olgunlaştıkça açılır.

## 5. Definition of Done (ürün düzeyi)

- Her rapor kalemi: golden-chart doğrulanmış sayı (P1-10) + kural-atıflı yorum (P2) + "belirsiz" çıkış yolu.
- Metrik eşikleri (gist §12.3): atıf kapsama ≥%95, desteksiz iddia <%1, çapraz rapor çelişkisi <%2, time-to-first-aha <15 sn.
- Ana metrik: **Aksiyon Zamanlayıcı haftalık aktif kullanım**.
- KVKK: biyometrik (CV) akışında on-device-first, ham görüntü saklanmaz, ayrı rıza.

## 6. Risk Notu (kısa)

Swiss lisansı 🔴 · KVKK biyometrik 🔴 · CV veri kıtlığı 🔴 · LLM halüsinasyonu 🔴 — önlemler sırasıyla P1 (port+yedek), P3 (KVKK akışı), P3 paralel veri, P2/P4 (deterministik judge+atıf). Detay: ROADMAP.md §risk.
