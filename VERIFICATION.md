# VERIFICATION.md — Doğrulayıcı kayıt defteri

Kural seti (kullanıcı prensipleri):
- Durum = kanıt: iddia / koşan komut / ham çıktı / geçti-kaldı. Komut çıktısı yoksa "doğrulanmadı".
- Oracle hiyerarşisi: pyswisseph (konum/ev), PyJHora (vedik mantık/panchanga/AV), JHora GUI/kitap (avasthala).
- Üretim motoru SADECE Skyfield; swiss/PyJHora yalnızca test-oracle'ı.
- Ayanamsa/ayar eşitlemesi zorunlu (Lahiri, mean node, NOABERR karşılığı).
- Mutasyon testi: doğrulayıcı kasıtlı bug sokar, test kırılmıyorsa test boş.

## Temel katman — canlı ölçümler (bu oturum)

### 1. Ayanamsa parity — GEÇTİ (kanıtlı)
Komut: `python - <<EOF` (swiss get_ayanamsa_ut vs `_ayanamsa_deg`, jd=2461329.0)
Çıktı: `ayanamsa swiss 24.231300609 skyfield 24.231300608 diff arcsec 0.000`
Durum: **doğrulandı** (<1e-5° kriteri karşılandı; 4 mod parametrikli test de koşuyor: `tests/test_skyfield.py::test_ayanamsa_modes_against_swiss` → passed).

### 2. Tropik boylam sapmaları — BULGU (tolerans gerçekçi değil)
Komut: çok-cisim × çok-epoch grid (jd ∈ {2448000, 2451545, 2461329}), swiss FLG_TROPICAL|FLG_NOABERR vs skyfield ecliptic_frame.
Ham çıktı (yay-saniyesi, ours−swiss):
```
jd 2451545: sun −2.72  moon −42.76  merc +21.07 venus +9.10 mars +13.66 jup +9.36 sat +6.99 ura +4.23 nep +3.73
jd 2461329: sun −2.83  moon −45.03  merc −5.02 venus −21.57 mars +10.33 jup +8.02 sat +6.96 ura +4.62 nep +4.23
jd 2448000: sun −2.30  moon −31.31  merc −12.88 venus +1.60 mars +12.96 jup +8.82 sat +6.07 ura +4.46 nep −0.85
```
Yorum (kanıta dayalı):
- Uranus/Neptune'da +4″ civarı **sabit sistematik offset** → J2000-mean vs of-date ekliptik çerçeve farkının imzası (presesyon düzeltmesi eksikliği).
- Ay'da −30…−45″ büyük sapma; Güneş'te −2.7″ küçük → ayar karışımı (no-aberration sözleşmesi + çerçeve).
- **Mevcut `≤0.02° (=72″)` toleransı bu yüzden GEÇİYOR ama 1–2″ hedefini geçemiyor.** Kullanıcının madde-tablosundaki "≤1–2 yay saniyesi" kriteri mevcut J2000-mean-ecliptic çerçevesiyle **karşılanmıyor — durum: KALDI (kısmen)**. Çözüm yolları (bir sonraki tur): ICRS→of-date ekliptik rotasyonu (precesyon+nutasyon matrisi) + gezegen ışık-zamanı gecikme düzeltmesinin netleştirilmesi; her adım ayrı grid ile ölçülerek.

### 3. Sidereal yeniden-türetme kontrolü — BULGU
Kanıt: `sid_recon_err` (swiss sid NOABERR − (ours_trop − ay_sw)): jd2451545 +56.7″, jd2461329 +37.0″, jd2448000 +19.7″.
Aynı epoch çiftlerinde tutarsız işaret/büyüklük → hata tek kaynağa indirgenemez (hem çerçeve hem aberrasyon sözleşmesi paylı). Raporda cisim bazında ayrıştırılacak.

### 4. Mevcut suite — GEÇTİ (referans, zayıf toleranslarla)
Komut: `python -m pytest tests/ -q` → `28 passed in 0.64s`.
Not: Bu suite kullanıcının istediği "bağımsız doğrulayıcı" DEĞİLDİR (uygulayanın kendi testi); temel katman kilidi için `tests/verify/` oracle-driven ızgara ayrıca yazılacak.

## Madde bazlı durum tablosu (yalnız kanıtlanmış satırlar dolu)

| Madde | İddia | Komut | Çıktı | Durum |
|---|---|---|---|---|
| Ayanamsa (4 mod) | <1e-5° | pytest + canlı diff | 0.000″ @jd2461329 | **GEÇTİ** |
| Boylam tropik | ≤1–2″ | 3×9 grid | max 45″ | **KALDI** (çerçeve+aberrasyon düzeltimi gerekli) |
| Boylam tropik | ≤0.02° (72″) | aynı grid | max 45″ | GEÇTİ (gevşek kriter) |
| Whole-sign bhava | birebir | pytest parity | passed | GEÇTİ (mevcut suite; bağımsız ızgara bekleniyor) |
| Asc/MC | ≤0.5° | pytest | passed | GEÇTİ (gevşek; 10.8k grid notu adapter docstring'inde) |
| Retro istasyon olayı | işaret değişimi | pytest | passed | GEÇTİ |
| Panchanga (tithi/karana/yoga/vara/sunrise) | PyJHora/swiss parity | — | — | **DOĞRULANMADI** (kod henüz yok) |
| Combustion/yuddha/dignity/maitri/avasthala/drishti | state.py | — | — | **DOĞRULANMADI** (kod yok) |
| Ashtakavarga bindu + toplamlar (Sun48…SAV337) | PyJHora parity | — | — | **DOĞRULANMADI** (kod yok) |
| Shadbala/Bhava bala/Ishta-Kashta | bileşen bazlı | — | — | **DOĞRULANMADI** (kod yok) |
| Avasthalar golden | kitap/GUI | — | — | **KAYNAK GOLDEN GEREKLİ** (PyJHora 4.8.7'de implementasyon yok — önceki oturum grep kanıtı) |

## Mutasyon testi durumu
Henüz koşulmadı → tüm maddeler için **DOĞRULANMADI**. Plan: doğrulayıcı suite yazıldıktan sonra `skyfield_adapter._ayanamsa_deg` ve dignity tablosuna kasıtlı ±bug sokulup hangi testlerin kırıldığı listelenecek.

## Sonraki adım sırası (temel katman kilitlenecek — kullanıcı talimatı)
1. ICRS→of-date ekliptik dönüşümü + aberrasyon sözleşmesi kararı → boylam ≤2″ hedefi (grid ile ölçülü).
2. Sunrise/sunset solver (swiss rise_trans'a ≤60 sn) + kutup kenar vakası.
3. Bağımsız `tests/verify/` oracle ızgarası (200+ chart) — 1–2'nin kilidi üzerinde.
4. Panchanga → State → Ashtakavarga → Shadbala fazları, madde-tablosu kriterleriyle.
