# Test ve Doğrulama Standardı

> Durum: **Yürürlükte** · Kapsam: `engine/` altındaki her modül ve her yeni entegrasyon
> İlişkili: [DEVELOPMENT_PROCESS.md](DEVELOPMENT_PROCESS.md) · [VERIFICATION.md](../../VERIFICATION.md)

## 1. Temel ilkeler

1. **Üretim motoru yalnızca Skyfield.** `swisseph` ve `PyJHora` yalnızca test
   oracle'ıdır; `engine/` altındaki üretim yolu bunları import etmez (lisans: AGPL).
2. **Oracle'a karşı test, kendine karşı değil.** Uygulayıcının kendi beklenen
   değerlerini yazdığı test "doğrulayıcı" sayılmaz; oracle ya da yayımlanmış kaynak gerekir.
3. **Her test bir şey kanıtlar.** Mutasyonla kırılmayan test silinir veya düzeltilir.
4. **Sözleşme önce hizalanır, sonra karşılaştırılır.** Zaman ölçeği, çerçeve,
   ışık-zamanı, aberasyon, nutasyon, ayanamsa, pencere semantiği eşitlenmeden
   alınan sapma ölçümü geçersizdir.

## 2. Test katmanları

| Katman | Dizin / işaret | Amaç | Ne zaman zorunlu |
|---|---|---|---|
| **L1 Birim / sözleşme** | `tests/test_*.py` | Fonksiyonun tip, birim, sınır, hata davranışı | Her yeni public fonksiyon |
| **L2 Regresyon** | `tests/test_*.py` (`test_<konu>_contract_*`) | Düzeltilmiş bir hatanın geri dönmemesi | Her hata düzeltmesi (SPEC-001: `test_time_scale_contract_*`) |
| **L3 Oracle ızgarası** | `tests/verify/` | Çok-epoch × çok-konum × çok-cisim oracle karşılaştırması | Her sayısal hesap modülü |
| **L4 Golden chart** | `tests/golden/` (P1-10) | Bilinen haritalarda uçtan uca kural çıktısı | Kural tabanlı modüller (yoga, avastha, shadbala) |
| **L5 Mutasyon** | elle / PR kanıtı | Testin boş olmadığının kanıtı | Her tur, DoD maddesi |
| **L6 Özellik (property)** | `tests/test_*.py` | Değişmezler (ör. `sid == trop − ay`, toplam 337 bindu) | Değişmezi olan her modül |

## 3. Oracle hiyerarşisi

| Alan | Birincil oracle | İkincil | Not |
|---|---|---|---|
| Gezegen boylamı, hız, retro | `pyswisseph` (Moshier, `FLG_MOSEPH`) | — | Ephe dosyası yoksa kapsam ≈ 1301–2033 |
| Lagna / ev cuspleri | `pyswisseph houses_ex` | — | |
| Doğuş/batış | `pyswisseph rise_trans` | — | |
| Ayanamsa | `pyswisseph get_ayanamsa_ut` | — | |
| Panchanga, Ashtakavarga, Shadbala, Varga | `PyJHora` | Kaynak kitap tablosu | PyJHora sürümü spec'te sabitlenir |
| Yoga, Avastha | Kaynak kitap (BPHS vb.) + `PyJHora` varsa | JHora GUI ekran görüntüsü | Kitap bölüm/şloka numarası spec'te yazılır |

Oracle'ın kendi belirsizliği tolerans bütçesine **açıkça** yazılır (ör. Moshier Ay ≈ 1–3″).

## 4. Sözleşme hizalama tablosu (her oracle testinin başına zorunlu)

Her `tests/verify/` modülünün docstring'i bu tabloyu içerir. Örnek (SPEC-001 sonrası boylam ızgarası):

| Boyut | Motor (Skyfield) | Oracle (swisseph) | Eşit mi |
|---|---|---|---|
| Girdi zaman ölçeği | JD(UT1) → `ts.ut1_jd` | `calc_ut` JD(UT) | ✅ |
| TT dönüşümü | skyfield ΔT tablosu | swiss ΔT | ✅ (fark < 0.1 s) |
| Merkez | yer-merkezli | yer-merkezli | ✅ |
| Işık-zamanı | yok (`at(t)` geometrik) | yok (`FLG_TRUEPOS`) | ✅ |
| Aberasyon | yok | yok (`FLG_TRUEPOS`) | ✅ |
| Çerçeve | `ecliptic_frame` = true ecliptic & equinox of date | tropik, nutasyon dahil | ✅ |
| Arama penceresi (olaylar) | `[jd, jd+1]` sonraki ilk olay | `rise_trans`: jd sonrası ilk | ✅ |

Bir satır ❌ ise test yazılmaz; önce hizalama yapılır veya fark tolerans bütçesine gerekçesiyle eklenir.

## 5. Tolerans politikası

| Büyüklük | Hedef (üretim) | Mevcut test eşiği | Gerekçe |
|---|---|---|---|
| Güneş/gezegen boylamı | ≤ 1″ | 2″ | Moshier ≈ 0.1–1″ |
| Ay boylamı | ≤ 2″ | 5″ | Moshier Ay belirsizliği; Ay 0.55″/s |
| Mean node | ≤ 20″ | 20″ | Meeus polinom kesmesi |
| Ayanamsa | ≤ 0.04″ (1e-5°) | 1e-5° | Kuadratik fit |
| Lagna (Asc) | ≤ 5″ (D60 için) | 0.5° (geçici) | **Açık iş** — bkz. INDEX SPEC-002 |
| Doğuş/batış | ≤ 5 s | 60 s | SPEC-001 ölçümü max 2.4 s |
| Olay zamanı (ingress/station) | ≤ 60 s | gün çözünürlüğü | Açık iş |
| Kural çıktısı (yoga var/yok, bindu sayısı) | **birebir** | birebir | Ayrık değer — tolerans yok |

Kurallar:
- Eşik, ölçülen en kötü değerin **altına** çekilemez; **üstüne** ancak gerekçeyle konur.
- "Hedef" ile "mevcut eşik" farklıysa spec'te bir kapanış turu planlanır.
- Ayrık çıktılar (rasi, nakshatra, pada, yoga) sınır yakınında test edilir:
  sınıra `< tolerans` uzaklıktaki vakalar ayrıca raporlanır ("boundary" sınıfı).

## 6. Test yazım kuralları

- **Adlandırma:** `test_<modül>_<davranış>[_<koşul>]`; regresyonlar `_contract_` içerir.
- **Parametrizasyon:** Izgaralar `@pytest.mark.parametrize` ile; id'ler okunur (`istanbul`, `jd=2451545`).
- **Hata mesajı:** Başarısızlıkta girdi + motor değeri + oracle değeri + sapma + tolerans yazılır.
- **Oracle yoksa atla, kırma:** `swe = pytest.importorskip("swisseph")`.
- **Docstring:** hangi AC'yi (SPEC-NNN AC-k) kanıtladığını yazar.
- **Uydurma API yasağı:** Test helper'ında kullanılan her kütüphane çağrısı commit öncesi en az bir kez koşmuş olmalıdır (SPEC-001'de `TS.delta_t`, `Time.ut1_jd` vakası).
- **Determinizm:** Rastgele grid gerekiyorsa `random.Random(seed)` ile sabitlenir.

## 7. Mutasyon protokolü (DoD maddesi)

```bash
# 1) Kasıtlı bug
sed -i 's/return self._ts.ut1_jd(jd_ut)/return self._ts.tt_jd(jd_ut)/' engine/skyfield_adapter.py
python -m pytest -q | tail -1          # beklenen: N failed
# 2) Geri al
git checkout -- engine/skyfield_adapter.py
python -m pytest -q | tail -1          # beklenen: all passed
```
PR'a iki satır da yapıştırılır. Mutasyonda kırılan test sayısı 0 ise test boştur.

## 8. Ortam

Tek kaynak `scripts/setup-dev.sh` + sabit sürümlü `requirements-test.txt`; her yerde aynı komut:

```bash
make setup     # .venv (Python 3.12; uv varsa uv, yoksa venv+pip) — idempotent
make check     # lint (ruff, yalnız hata sınıfları) + lisans bekçisi + tüm testler = CI
```
Debian/Ubuntu sistem Python'unda pyswisseph doğrudan pip ile derlenmez
(setuptools `install_layout` hatası) — bu yüzden daima izole venv.
Merge kapısı: `make gate` (ADR-003). Commit'i temiz bir kopyada sıfırdan ortamla `make check`'ten geçirir; GitHub Actions bu hesapta kullanılamıyor.
Ortam tablosu: [CONTRIBUTING.md §1](../../CONTRIBUTING.md).

## 9. Yeni entegrasyon kontrol listesi (modül eklerken)

- [ ] Spec onaylı (DoR tamam).
- [ ] Oracle seçili, sürümü `requirements-test.txt`'te sabit.
- [ ] Sözleşme hizalama tablosu dolu (§4).
- [ ] L1 + L3 (sayısal) veya L1 + L4 (kural) testleri var.
- [ ] L6 değişmezleri tanımlı (varsa).
- [ ] Sınır vakaları (burç/nakshatra sınırı, kutup enlemi, kernel kapsam kenarı) test edildi.
- [ ] Mutasyon kanıtı PR'da.
- [ ] VERIFICATION.md satırı eklendi.
