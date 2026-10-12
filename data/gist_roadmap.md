---

# BÖLÜM 0 — Stratejik teşhis: Moat nerede değil, nerede?

Ücretsiz `PyJHora` + ücretsiz `Swiss Ephemeris` + ücretsiz bir MCP sunucusu, **hesaplamayı zaten çözmüş**. Yarın bir rakip aynı repo'yu klonlayıp sizin "astroloji motorunuzu" birebir üretebilir.

Dolayısıyla hesaplama motoru moat **değildir**. Moat şu beş katmandadır:

| Katman | Neden kopyalanamaz / zor kopyalanır | Ürünsel karşılığı |
|---|---|---|
| **1. Yorum kural tabanı + atıf grafı** | Açık kaynakta *yok*. Hesap var, hüküm yok. | Tutarlı, kaynak gösteren, çelişmeyen yorum |
| **2. Longitudinal kullanıcı hafızası** | Rakipler her oturuma sıfırdan başlıyor. | "Beni hatırlayan" danışman |
| **3. Etiketli el çizgisi veri seti** | Açık kaynak setler araştırma ölçeğinde (aşağıda sayısını veriyorum) | Tek gerçek çoklu-modality ürün |
| **4. Aksiyon → zaman derleyicisi (Muhurta/Electional)** | Açık kaynakta hiç yok | "Ne zaman?" sorusuna ürün olarak cevap |
| **5. Dağıtım + insan köprüsü** | Teknoloji değil, operasyon | WhatsApp/Instagram/MCP/her yerden erişim |

**Bu raporun geri kalanı bu beş katmanı inşa eder.**

---

# BÖLÜM 1 — Açık kaynak envanteri: Ne var, ne kadarı var, lisansı ne

## 1.1 Doğrulanmış depo envanteri

| Proje | Kaynak | Gerçek yetenek | Üründe rolü | Kritik kısıt |
|---|---|---|---|---|
| **PyJHora** (`naturalstupid/PyJHora`) | github.com/naturalstupid/PyJHora | Kendi tanımına göre PVR Narasimha Rao, *Vedic Astrology – An Integrated Approach* kitabının neredeyse tüm özelliklerini içerir | Vedik hesaplama çekirdeği | Kitap telifli; **kod açık, metin değil** |
| **kerykeion** (PyPI 6.0.5) | pypi.org/project/kerykeion | Natal, evler, açıların, transit, synastry, return, SVG harita | Batı hesaplama + görsel üretim | `pyswisseph` bağımlılığı |
| **pyswisseph / Swiss Ephemeris** | Astrodienst | Endüstri standardı astronomik konum, ayanamsa, düğümler | Her iki geleneğin temeli | **AGPL-3.0 VEYA ticari lisans** |
| **astrology-mcp** (`DeadMeme5441/astrology-mcp`) | glama.ai/mcp/servers/DeadMeme5441/astrology-mcp | Yerel Swiss Ephemeris ile natal, dasha, transit, yoga hesaplayıp LLM'e tool olarak açıyor | MCP protokol referansı | Üretim kalitesi değil; referans mimari |
| **yeonsumia/palmistry** | github.com/yeonsumia/palmistry | "View-Invariant Machine Palmistry" — 4 adımlı ana çizgi tespiti | CV pipeline iskeleti | Araştırma kodu, üretim değeri düşük |
| **MuntahaShams/palm-line-detection** | github.com/MuntahaShams/palm-line-detection | Objeye dayalı ana palm çizgisi tespit+sınıflandırma | Baseline model | Etiket taksonomisi sığ |
| **GazanfarAnsari10/Cognisense-Palmistry-Analyzer** | github.com | Görüntüden desen çıkarımı | Feature extraction fikri | Doğrulama raporu yok |
| **lakshay102/Palm-Astro-Application** | github.com | Palm + astro sentezi denemesi | Rakip/mimari referansı | Derinlik yok |
| **Roboflow `palm-line-detection-9zzh0`** | universe.roboflow.com/palm-reading-test/… | **46 görüntü** + ön-eğitli model | Annotation bootstrap **ancak** | **46 görüntü üretim modeli için yok hükmünde** |
| **arXiv 2509.02248** | arxiv.org/html/2509.02248v1 | ML ile çizgi + mount tespiti | Literatür / yöntem | Akademik, veri seti sınırlı |
| **Benham, *The Laws of Scientific Hand Reading* (1900)** | archive.org/details/in.ernet.dli.2015.200302 | ~670 sayfalık, sistematik çizgi morfolojisi | **Kural tabanının omurgası** | Public domain — kullanılabilir |

**Pazar veri noktası (doğrulanmış basın):** Astopia için "300 bin dolar tohum öncesi yatırım" bildirilmiş (egirisim.com, Mart 2024). Bu bir **fonlama sinyalidir**, ciro değildir.

**Pazar veri değildir (ret çekiyorum):** R10'daki "Astroscope hazır uygulama — 20M+ potansiyel kullanıcı, kullanıcı başı 15–50₺/ay" ifadesi bir **hazır-uygulama satıcısının pazarlama iddiasıdır**. Pazar istihbaratı olarak kullanılmaz. Önceki yanıtlarda buna dayanılması hataydı.

**Ticari karşılaştırma noktası:** RoxyAPI, 18+ alan için $39/ay düz abonelik + Remote MCP sunuyor. Bu, **hesaplama API'sinin fiyat tabanını** gösterir. Yani "API satmak" stratejik olarak değersizdir; değeri üst katmanlarda yaratmalısınız.

## 1.2 Kritik lisans bulgusu — bunu bugün çözmezseniz ürününüz satılamaz

**Swiss Ephemeris çift lisanslıdır: AGPL-3.0 veya ticari lisans.**

Bunun anlamı:

- `pyswisseph`, `kerykeion`, `PyJHora` üzerinden Swiss Ephemeris'e bağlanan **her ticari SaaS**, AGPL'nin ağ etkileşimi maddesiyle karşı karşıyadır.
- AGPL altında ağ üzerinden servis veriyorsanız, servisin ilişkili kaynak kodunu kullanıcıya sunmak zorunda kalabilirsiniz.
- **"API arkasına gizleriz" çalışmaz.** AGPL tam da bunu kapatmak için yazılmıştır.

**Karar matrisi:**

| Seçenek | Maliyet | Risk | Öneri |
|---|---|---|---|
| Swiss Ephemeris ticari lisans | Astrodienst ile görüşülür; gelir/dağıtım modeline bağlı | Düşük | **Ticari ölçek için doğru yol** |
| AGPL'ye tam uyum | Tüm bağlı servisin kaynak açılımı | Yüksek (moat'ı açarsınız) | Sadece open-core hesap katmanı için |
| **Ephemeris soyutlama katmanı** | 3–4 hafta ek iş | Düşük | **Zorunlu mimari karar** |

**Zorunlu mimari:** Hesaplama katmanını tek bir `EphemerisPort` arayüzü arkasına koyun.

```
EphemerisPort
 ├─ longitude(body, date, frame) -> degrees
 ├─ houses(date, location, system) -> [12 cusps]
 ├─ ayanamsa(date, mode) -> degrees
 └─ events(window, body) -> [ingress, retro, station]

Implementations:
 ├─ SwissEphemerisAdapter   (lisanslı)
 ├─ AstronomyEngineAdapter (MIT — Don Cross / cosinekitty/astronomy)
 └─ SkyfieldAdapter        (MIT — JPL SPK, public domain veri)
```

Astronomy Engine ve Skyfield **astronomi** verir; **ev/açı/ayanamsa yorum katmanını siz yazarsınız.** Bu iş 3–4 haftadır ve karşılığında lisans bağımsızlığı kazanırsınız. Bu, rakiplerin çoğunun gözden kaçırdığı gerçek bir avantajdır.

---

# BÖLÜM 2 — "PyJHora kaç sayfa çıktı verir?" — Gerçek cevap ve bilgi mimarisi

Bu, sorduğunuz en kritik soru. Cevap: **PyJHora sayfa vermez. Sayılabilir bir veri yüzeyi verir.** Sayfa üretmek sizin ürün kararınızdır. Ve bu kararı yanlış verirseniz elinizde 250 sayfalık, kimsenin okumadığı bir PDF olur.

## 2.1 Veri yüzeyinin sayımı (sistem matematiğinden türetilmiş)

| Yüzey | Yapısal sayım | Açıklama |
|---|---|---|
| **Natal (D1)** | 9 graha × 8 özellik = **72 atomik olgu** | burç, derece, ev, nakshatra, pada, retro, avastha, hiz |
| **Divisional (Varga)** | Yaygın pratik set **16 harita** (D1, D2, D3, D4, D5, D7, D9, D10, D11, D12, D16, D20, D24, D27, D30, D60) | 16 × 9 = **144 yerleşim**. Tam desteklenen varga listesi repo denetiminde |
| **Shadbala** | 6 bala × 9 graha = **54 ham değer** + 9 oran | Sthana, Dig, Kala, Cheshta, Naisargika, Drik |
| **Ashtakavarga** | 8 graha × 12 rashi = **96 bindu** + 12 Sarvashtakavarga toplamı + **96 kakshya** | Kakshya, transit zamanlamasının gerçek anahtarıdır |
| **Vimshottari Dasha** | 9 MD + 81 AD + 729 PD + 6.561 SD = **7.380 düğüm** | Beşinci katman açılırsa +59.049 = **66.429** |
| **Transit × natal** | 9 graha × 12 ev = **108 hücre** | Ay'dan sayılan ev konumu |
| **Panchanga / gün** | 5 uzuv + günlük kala pencereleri + **24 planetary hour** | Tithi, Vara, Nakshatra, Yoga, Karana |
| **Choghadiya** | Gündüz 8 + gece 8 = **16 zaman dilimi/gün** | 7 isim döngüsü |
| **Yoga kuralları** | **Repo'da tanımlı kural sayısı** | "500 yoga var" demek ezbeciliktir. Sayılacak (aşağıdaki betik) |
| **Jaimini** | 12 Arudha pada + Upapada + Karakamsa + Chara Karaka + Argala | Ayrı bir yorum çerçevesi |
| **KP** | Sublord yüzeyi | **PyJHora'nın güçlü alanı değil.** Ayrı motor gerekir; "bedava geliyor" diye planlamayın |

## 2.2 "Kaç sayfa" hesabı — naif dökümün iflası

Varsayılan: sayfa = 400 kelime.

| Döküm parçası | Hesap | Kelime | Sayfa |
|---|---|---|---|
| 7.380 dasha düğümü × 12 kelime | 88.560 | ~221 |
| 16 varga × 9 yerleşim × 25 kelime | 3.600 | ~9 |
| 96 bindu × 10 kelime | 960 | ~2,4 |
| 54 bala değeri × 15 kelime | 810 | ~2 |
| 108 transit hücresi × 30 kelime | 3.240 | ~8 |
| 25 tetiklenen yoga × 60 kelime | 1.500 | ~3,8 |
| **Toplam** | **~98.670 kelime** | **~247 sayfa** |

**Bu, bir ürün değildir. Bu, bir veri dökümüdür.** Rakiplerin "detaylı rapor" diye sattığı şeyin sonu burasıdır ve ikinci kez açılmaz.

**Doğru ürün kararı:** Ham yüzeyi asla kullanıcıya göstermeyin. Kullanıcıya **projeksiyon** gösterin.

## 2.3 Projeksiyon mimarisi — aynı veri yüzeyinden 6 farklı ürün

| Ürün | Aktif fakt sayısı | Kelime | Tüketim süresi | Fiyat katmanı |
|---|---|---|---|---|
| **Günlük kart** | 1 aktif SD + 1 transit + 1 aksiyon | 80–120 | 20 saniye | Ücretsiz |
| **Haftalık kart** | 1 SD + 3 yakın eşik + 5 zaman penceresi | 400–600 | 2 dakika | Ücretsiz / düşük |
| **Aylık bülten** | 1 PD + 4 transit olayı + 3 aksiyon | 1.200–1.800 | 7 dakika | Abonelik |
| **Dönem geçiş raporu** | 1 AD eşiği + önceki/sonraki karşılaştırma | 3.000–4.000 | 20 dakika | Tek seferlik |
| **Yıl kitabı** | 12 ay × 3 tema + Solar Return | 10.000–14.000 | 60 dakika | Tek seferlik premium |
| **Ömür atlası** | 9 MD + 16 varga + Sima | 18.000–25.000 | 2–3 saat, 12 bölüm | Premium |

**Aynı motor. Altı ürün. 250 sayfa yerine 20 saniyelik bir alışkanlık.**

İsteyen kullanıcı için "tüm veriyi gör" drawer'ı açık kalsın — ama varsayılan asla döküm olmasın. Bu, şeffaflığı korurken kullanılabilirliği yaratır.

## 2.4 Repo denetim betiği — ezber değil, çıkarım

Aşağıdaki betik, depoyu klonlayıp **gerçek sembol yüzeyini ve kural tabanı adaylarını** statik olarak çıkarır. Import etmez, bağımlılık gerektirmez, çalışır.

```python
#!/usr/bin/env python3
# surface_audit.py
# Kullanım: python surface_audit.py ./PyJHora
import ast, json, sys, pathlib

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
symbols, tables = [], []

for path in sorted(ROOT.rglob("*.py")):
    if any(p in {".git", "venv", ".venv", "build", "dist"} for p in path.parts):
        continue
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        continue
    rel = str(path.relative_to(ROOT))

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = " ".join((ast.get_docstring(node) or "").split())[:400]
            args = []
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in node.args.args + node.args.kwonlyargs]
            symbols.append({
                "file": rel, "kind": type(node).__name__, "name": node.name,
                "line": node.lineno, "args": args, "doc": doc,
            })
        elif isinstance(node, ast.Assign):
            v = node.value
            if isinstance(v, ast.Dict):
                n = len(v.keys)
            elif isinstance(v, (ast.List, ast.Tuple, ast.Set)):
                n = len(v.elts)
            else:
                n = 0
            if n >= 5:
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                tables.append({"file": rel, "names": names,
                               "entries": n, "line": node.lineno})

summary = {
    "root": str(ROOT),
    "symbols": len(symbols),
    "classes": sum(1 for s in symbols if s["kind"] == "ClassDef"),
    "functions": sum(1 for s in symbols if s["kind"] != "ClassDef"),
    "documented": sum(1 for s in symbols if s["doc"]),
    "rule_table_candidates": sorted(tables, key=lambda t: -t["entries"]),
}

pathlib.Path("surface_inventory.json").write_text(
    json.dumps({"summary": summary, "symbols": symbols, "tables": tables},
               ensure_ascii=False, indent=2), encoding="utf-8")

print(json.dumps({k: v for k, v in summary.items()
                  if k != "rule_table_candidates"}, ensure_ascii=False, indent=2))
print("\nKURAL TABANISI ADAYLARI (ilk 25):")
for t in summary["rule_table_candidates"][:25]:
    print(f"{t['entries']:5d}  {t['file']}:{t['line']}  {t['names']}")
```

**Çıktıdan alınacak üç karar:**
1. `rule_table_candidates` → hangi modül kaç yorum kuralı içeriyor? Bu, **ürün yüzeyinin gerçek sınırıdır.**
2. `classes` + `functions` → hangi hesaplama SKU'ya dönüşebilir?
3. Docstring'i boş semboller → **dokümante edilmemiş = üretimde güvenilmez** ayrımı.

Sonrasında tek bir sabit doğum verisiyle runtime probe çalıştırıp her çıktının **gerçek JSON şemasını** kaydedin. Bu kayıt, aşağıdaki fakt kontratının temeli olur.

---

# BÖLÜM 3 — DASHA: Aboneliğin ve retention'ın gerçek omurgası

Bu bölüm, önceki yanıtların tamamen atladığı kısım.

## 3.1 Önce matematik: Dasha hangi sıklıkta değişir?

Vimshottari toplam **120 yıl**. Tam ağaç:

| Katman | Düğüm sayısı | 120 yıl / düğüm = ortalama süre | Gerçek ürün ritmi |
|---|---|---|---|
| **Maha Dasha (MD)** | 9 | ~13,3 yıl | Yaşam bölümü — ömür atlası |
| **Antara Dasha (AD)** | 81 | ~1,48 yıl (~18 ay) | **Dönem geçiş raporu** |
| **Pratyantara (PD)** | 729 | ~60 gün | **Aylık bültenin gerçek değişim birimi** |
| **Sookshma (SD)** | 6.561 | ~6,7 gün | **Haftalık kart** |
| Prana (5. katman) | 59.049 | ~18 saat | Geleneksel kullanımı sınırlı; repo desteği doğrulanmalı |

### Buradan çıkan kritik ürün dersı

**Günlük kartı Dasha'ya dayandıramazsınız.** SD bile ~6,7 günde bir değişir. "Her gün yeni dasha yorumu" üretmeye çalışırsanız **aynı metni 7 gün üst üste göndermiş olursunuz** — rakiplerin yaptığı tam olarak bu ve churn'un birinci nedeni.

Doğru katmanlama:

```
GÜNLÜK ritim  ← Transit + Panchanga + Planetary Hour + Choghadiya
HAFTALIK ritim ← Sookshma Dasha
AYLIK ritim   ← Pratyantara Dasha
YILLIK ritim  ← Antara Dasha eşiği
ÖMÜR ritmi    ← Maha Dasha eşiği
```

**Bu beş katmanlı saat, rakiplerde yok.** Çünkü Dasha hesaplamıyorlar; hesaplasalar bile ritim matematiğini çıkarmıyorlar.

## 3.2 Dasha-güdümlü gelir motoru

### A) Eşik tabanlı yeniden kazanım (reactivation)

Kullanıcının AD eşiği yaklaştığında (30–60 gün önce):

> "Şubat'ta ~18 aylık bir dönem kapanıyor. Önceki 18 ayda ne olduğunu ve sonrasını birlikte okumak ister misin?"

Bu, **kişiye özel, takvimsel olarak önceden bilinen, gerçekten yeni bilgi içeren** bir pazarlama tetikleyicisidir. Generic "seni özledik" kampanyası değildir.

### B) Dasha → SKU öneri motoru

Aktif Dasha temasına göre **ilgili dikeyi** öner:

| Aktif dönem işareti | Önerilecek SKU | Gerekçe |
|---|---|---|
| 10. ev / Satürn vurgulu AD | **F1 Kariyer (D10)** | Kullanıcının şu anki hayat sorusu büyük olasılıkla kariyer |
| 7. ev / Venüs vurgulu AD | **F3 Evlilik-Bağ (D9)** | Dönem teması ilişki |
| 2.–11. ev / Jüpiter AD | **F2 Para-Kaynak (D2/D11)** | Kaynak genişleme teması |
| 4. ev / Ay AD | **F5 Yerleşim (D4)** | Taşınma/yurt teması |
| AD eşiği < 45 gün | **B2 Dönem Geçiş Raporu** | Zaman hassas değer |

**Bu, jenerik upsell popup'ı değil, astrolojik olarak zamanlanmış bağlamsal tekliftir.** Dönüşüm farkı buradan gelir.

### C) Churn önleme

Zor bir AD/PD penceresi kapanırken kullanıcıya **kapanışı gösterin**:

> "Bu dönem zorlayıcıydı. Şu tarihli eşikle birlikte tema değişiyor. Aboneliğini bunun için kapatıyorsan, değişimi birlikte izlemeni öneririm."

Korkuyla tutundurma **değil**, görünürlükle tutundurma. Hem etik hem uzun vadeli LTV açısından doğru.

### D) Aboneliğin kaçınılmaz değeri

| Abonelik katmanı | Gerçek değişim kaynağı | Gönderim tavanı |
|---|---|---|
| Günlük Kart | Panchanga + Hora + transit | **Günde 1** |
| Haftalık | SD + 3 yakın eşik | Haftada 1 |
| Aylık | PD + aksiyon penceresi taraması | Ayda 1 + kullanıcı istediğinde |
| Dönem | AD eşiği | Yılda ~1 (olay bazlı) |

**Tavan koymak bir ürün kararıdır.** Rakipler bildirim spam'i yapıyor; sizin farkınız "sadece gerçekten bir şey değiştiğinde yazmak" olacak.

---

# BÖLÜM 4 — SKU KATALOGU: 40 kalem ürün/hizmet, 8 aile

Aşağıdaki katalog **türetilmiştir**, uydurulmamıştır. Kaynak kodları:
`JH` = PyJHora · `KER` = kerykeion · `SW` = Swiss · `RULE` = bizim kural motorumuz · `CV` = el çizgisi pipeline · `MEM` = kullanıcı hafızası · `CAL` = takvim entegrasyonu

## A — Kimlik ve Temel (6)

| ID | SKU | Kaynak | Format | Katman |
|---|---|---|---|---|
| A1 | Doğum İzi (Batı natal özet) | KER+SW | İnteraktif SVG + 12 ev kartı | Ücretsiz |
| A2 | Vedik Kök (Lagna + Nakshatra + Pada) | JH | 1 sayfa + audio | Ücretsiz |
| A3 | Güç Haritası (54 bala + 96 bindu) | JH+RULE | Isı haritası + 9 graha profili | Tek seferlik |
| A4 | 16 Hayat Alanı (16 varga) | JH+RULE | 16 bölümlü atlas | Tek seferlik premium |
| A5 | **Çift Gelenek Sentezi** | KER+JH+RULE | Çakışma matrisi + uzlaşı/gerilim raporu | Premium |
| A6 | **Doğum Saati Rectification** | JH+KER+MEM+RULE | 3–4 olası saat aralığı + olay doğrulama sihirbazı | Tek seferlik premium |

**A6 benzersiz bir üründür:** Kullanıcının doğum saati belirsizse → olası Lagna aralıklarını üret → her birinin D9/Dasha farkını göster → kullanıcıdan 5 yaşam olayı teyidi al → olasılığı güncelle. Rakipler "saat bilinmiyorsa öğle 12:00 yazar" yapıyor. Bu, güvenin öldüğü yerdir.

## B — Zaman ve Öngörü (6)

| ID | SKU | Kaynak | Format | Katman |
|---|---|---|---|---|
| B1 | Yaşam Çizgisi (7.380 düğüm → timeline) | JH | Kaydırılabilir interaktif zaman çizgisi | Premium |
| B2 | Aktif Dönem Raporu (MD+AD+PD) | JH+RULE | 4–6 sayfa + audio | Abonelik |
| B3 | Yıllık Transit Takvimi (108 hücre) | JH+KER+RULE | 12 aylık takvim + olay listesi | Tek seferlik |
| B4 | Sade Sati / Dhaiya Rehberi | JH+RULE | 3 fazlı rehber + aksiyon listesi | Tek seferlik |
| B5 | Yıl Kitabı (Solar Return, 12 bölüm) | KER+RULE | 60 sayfa + sesli özet | Tek seferlik premium |
| B6 | Ay Haritası (Lunar Return, 12 bölüm) | KER+RULE | 12 kısa bölüm | Abonelik |

## C — Aksiyon ve Zamanlama (5) — **en yüksek farklılaşma**

| ID | SKU | Kaynak | Format | Katman |
|---|---|---|---|---|
| C1 | **Aksiyon Zamanlayıcı** | JH+KER+RULE+CAL | Aksiyon seç → 7 günlük ranked pencere | Abonelik çekirdeği |
| C2 | Muhurta Taraması (7/30 gün) | JH+RULE | Takvime indirilebilir .ics | Tek seferlik |
| C3 | **Tek Soru (Horary)** | KER+RULE | Soru → hüküm + gerekçe + zamanlama | Tek seferlik, yüksek marj |
| C4 | Karar Paketi (3 Horary) | KER+RULE+MEM | 3 soru + karşılaştırmalı karar matrisi | Tek seferlik |
| C5 | Lansman / Girişim Muhurta Paketi | JH+KER+RULE | Aksiyon planı + 3 alternatif zaman | Premium |

## D — İlişki (4)

| ID | SKU | Kaynak | Not |
|---|---|---|---|
| D1 | Synastry | KER | 10×10 gezegen çifti, 5 açı türü potansiyeli |
| D2 | Composite / Davison | KER+RULE | İlişkinin kendi haritası |
| D3 | **Ashtakoota Guna Milan** | JH+RULE | 8 kategori / 36 guna — Vedik uyum, Batı'dan完全不同 |
| D4 | İlişki Zamanlaması | JH+RULE+CAL | İki kişinin Dasha eşiklerinin çakışması |

## E — Sima / Çoklu Kanallı (5)

| ID | SKU | Kaynak | Not |
|---|---|---|---|
| E1 | El Çizgisi Tarama Raporu | CV+RULE | Çizgiler işaretli, overlay'li görsel |
| E2 | **El–Harita Uyum Raporu** | CV+JH+RULE | **Mount ↔ Graha eşlemesi** (Bölüm 7) |
| E3 | El Şekli / Element Profili | CV+RULE | Çin/Hint + Batı element taksonomisi |
| E4 | Sima Yaşam Atlası | CV+JH+KER+RULE | Tam füzyon, premium |
| E5 | **Sima Değişim Takibi** | CV+MEM | Aylık tarama → normalize edilmiş fark analizi |

**E5 retention için altın bir özelliktir:** Kullanıcı kendi elinin değişimini izler. Bu, "bugün Yay burcuna şu olacak"tan çok daha güçlü bir alışkanlık döngüsüdür. **Ama:** CV gürültüsünü "değişim" diye satarsanız güveni anında öldürürsünüz. Ölçüm-güven eşiği zorunlu (Bölüm 7).

## F — Yaşam Alanı Dikeyleri (6)

| ID | SKU | Vedik referansı | Batı referansı |
|---|---|---|---|
| F1 | Kariyer / Meslek | D10 + 10. ev + Chara Karaka | 10. ev + Satürn + MC |
| F2 | Para / Kaynak Eğilimi | D2 + D11 + 2./11. ev | 2./8. ev + Jüpiter/Venüs |
| F3 | Evlilik / Bağ | D9 + 7. ev + Venüs | 7. ev + Venüs + Desc |
| F4 | Eğitim / Yetenek | D5 + 5. ev + Saraswati yoga | 3./9. ev + Merkür |
| F5 | Yerleşim / Taşınma | D4 + 4. ev | 4. ev + Ay + IC |
| F6 | Aile / Çocuk | D7 + 5. ev | 5. ev + Ay |

## G — Abonelik ve Erişim (4)

| ID | SKU | İçerik | Hedef fiyat hipotezi* |
|---|---|---|---|
| G1 | Günlük Kart | 1 transit + 1 hora + 1 aksiyon | Ücretsiz |
| G2 | Kişisel Bülten | PD + haftalık SD + aylık Lunar Return | 129–199₺/ay |
| G3 | **Kişisel Zaman Asistanı** | C1 + takvim + widget + sınırlı soru | 199–349₺/ay |
| G4 | Sınırsız Soru + İnsan Erişimi | G3 + aylık 1 canlı danışman seansı | 749–1.499₺/ay |

\* **Bunlar test edilecek hipotezlerdir, doğrulanmış pazar fiyatı değildir.**

## H — B2B ve Dağıtım (4)

| ID | SKU | Alıcı | Model |
|---|---|---|---|
| H1 | White-label Hesaplama API | Medya, wellness app, e-ticaret | Kotaya dayalı aylık |
| H2 | **Danışman Konsolu** | Bağımsız astrologlar/firasatçılar | SaaS + işlem komisyonu |
| H3 | Medya İçerik Beslemesi | Gazete, portal, podcast | Lisans |
| H4 | Geliştirici / MCP Erişimi | AI istemci kullanıcıları | Freemium + entitlement |

**Toplam: 40 kalem.**

**MVP kesiti (6 SKU):** A1, A2, B2, C1, C3, G3.
**Faz 2 (2 SKU ek):** E1, E2 — CV veri seti hazır olduğunda.
**Geri kalan 32 SKU:** veri ve kural tabanı olgunlaştıkça açılır.

Bu, "her şeyi aynı anda yapalım" tuzağından çıkmanın yoludur.

---

# BÖLÜM 5 — Transitleri "günümüze sokmak": Aksiyon Derleyicisi

Sorunuz doğru soruydu. Cevap: **Transiti kullanıcıya göstermeyiz. Transiti aksiyona derleriz.**

## 5.1 Aksiyon taksonomisi ve kural eşlemesi

| Aksiyon | Vedik parametre | Batı parametre | Çıktı |
|---|---|---|---|
| **Sözleşme / imza** | Merkür gücü, Tithi, Choghadiya = Amrit/Shukla/Labh, 2./11. ev | Merkür dignity, Ay uygulayıcı açı, 3. ev | Ranked 3 zaman penceresi |
| **Mülakat / iş başvurusu** | 10. ev lordu, Surya Hora, Vijaya yoga | MC, Güneş, Satürn açısızlık | Gün + saat aralığı |
| **Sunum / satış** | 5. ev, Budha Hora, Shukla | 5. ev, Merkür-Güneş, Ay | Saat penceresi |
| **İlk buluşma** | Venüs Hora, Rohini/Punarvasu nakshatra | Venüs dignity, 5. ev, Ay | Akşam saat önerisi |
| **Zor ilişki konuşması** | 7. ev, Ay artan ışık, Vishti kaçınma | 7. ev, Ay-Kronos açısızlık, Venüs | Gün önerisi + kaçınılacak gün |
| **Seyahat** | 3./9. ev, Ashwini/Revati, Rahu Kala dışı | 3./9. ev, Jüpiter, Ay | Tarih + çıkış saati |
| **Girişim / lansman** | Lagna gücü, Indra Yoga, Shukla Paksha | Electional ASC + Jüpiter + Merkür | Tam muhurta dosyası |
| **Taşınma** | D4, 4. ev, Dhruva nakshatra | 4. ev, IC, Satürn | Tarih aralığı |
| **Eğitim başlangıcı** | 5./9. ev, Brihaspati Hora, Saraswati yoga | 9. ev, Merkür-Jüpiter | Tarih |
| **Büyük alışveriş** | 2. ev, Venüs Hora, Amrit | 2. ev, Venüs-Jüpiter | Gün |

**Not:** Tıbbi ve hukuki kararlar için "en doğru zaman" iddiası üretilmez. Bu kategoriler yalnızca *randevu planlama tercihi* olarak ele alınır; teşhis/tedavi/hukuk tavsiyesi verilmez. Bu hem güvenilirlik hem ödeme/store riski açısından zorunludur.

## 5.2 Olay-farkındalıklı bildirim — gerçek killer feature

```
KULLANICI TAKVİMİ: "Perşembe 14:00 — Sözleşme görüşmesi"
                          ↓
Aksiyon sınıflandırıcı → category = contract
                          ↓
Transit taraması → Merkür, natal 2. evde; Satürn, natal Merkür'e kare
                          ↓
Dasha filtresi → aktif AD 6. ev temasında
                          ↓
Muhurta derleyici → Perşembe 14:00 yerine 11:20–12:40 daha uygun
                          ↓
BİLDİRİM:
"Perşembe öğleden sonraki sözleşme görüşmeni gördüm.
Sabah aralığı bu iş için daha temiz görünüyor.
İstersen 11:20'ye alman için gerekçeyi açayım."
```

**Bu, rakiplerin yapamadığı şeydir.** Çünkü:
1. Dasha hesaplamıyorlar.
2. Muhurta kural tabanı yok.
3. Takvim entegrasyonu yok.
4. Kullanıcı hafızası yok.

Dört eksik birden. Bunların kesişimi sizin konumlandırmanızdır.

## 5.3 Bildirim disiplini

- Günde **en fazla 1** proaktif mesaj.
- Kullanıcının sessiz saatlerine saygı.
- **Korku temelli bildirim yasak.** "Satürn geliyor, hazırlıklı ol" değil; "şu pencere daha uygun".
- Her bildirimin yanında "neden?" → kaynak + kural + hesap.
- Kullanıcı "bu konu beni ilgilendirmiyor" diyebilmeli → hafızaya yazılır, bir daha gelmez.

---

# BÖLÜM 6 — Horary (Soru) ve Muhurta: Açık kaynağın boşluğu = sizin surunuz

## 6.1 Kritik bulgu

**GitHub'da hesaplama var. Hüküm yok.**

`PyJHora` ve `kerykeion` size "Ay 14° Boğa'da" der. **"Bu sözleşme imzalanır mı?" sorusuna cevap vermez.** Bu ikisi arasındaki katman — yani *judgment layer* — açık kaynakta neredeyse tamamen boştur.

**Orayı siz yazacaksınız. Ve orası moat'ınız olacak.**

## 6.2 Horary motoru: uygulanabilir akış

```
1. SORU AL
   └─ Serbest metin → niyet sınıflandırıcı → konu + ev ataması

2. RADİCALLİK KONTROLÜ  (kritik — atlanırsa her cevap çöp)
   ├─ ASC gezegeni/karakteri kullanıcıya uyuyor mu?
   ├─ Ay boşlukta mı (Void of Course)?
   ├─ ASC'te Satürn / Acı Çekim dereceleri var mı?
   └─ Uyumsuzsa → "Bu soru için harita yeterli işaret taşımıyor"
       (UYDURMA. Bu dürüstlük rakiplerde yok.)

3. SİGNİFİKATÖR TAYİNİ
   ├─ 1. ev lordu = soran
   ├─ Konuya göre ev (aşağıdaki tablo)
   └─ Karşı tarafın significator'ı

4. AÇI ANALİZİ
   ├─ Uygulayıcı (applicative) mı, ayrılan (separating) mi?
   ├─ Reception (karşılıklı kabul) var mı?
   ├─ Translation of Light / Collection of Light var mı?
   └─ Açı türü + orb + derece

5. HÜKÜM
   └─ evet / hayır / şartlı / belirsiz
      + gerekçe zinciri
      + zamanlama (derece → gün/ay, burç türüne göre)

6. ÇAPRAZ KONTROL
   ├─ Aktif Dasha bu hükmü destekliyor mu?
   ├─ Transit destekliyor mu?
   └─ Çelişiyorsa → ÇELİŞKİYİ GÖSTER, sahte uzlaşı üretme
```

### Soru → ev eşleme tablosu

| Soru türü | Ev | Signifikatör |
|---|---|---|
| İş / kariyer değişimi | 10 | 10. ev lordu + Güneş |
| Borç / alacak | 2 / 8 | 2. ve 8. ev lordları |
| Kayıp eşya | 2 | 2. ev lordu + Ay |
| İlişki / evlilik | 7 | 1. ve 7. ev lordları |
| Sınav / eğitim | 9 | 9. ev lordu + Merkür |
| Seyahat / taşınma | 9 / 4 | 9. ve 4. ev lordları |
| Sağlık (genel) | 6 | 6. ev lordu + Ay — **teşhis yok** |
| Rakip / dava | 7 / 1 | 1. ve 7. ev lordları |
| Bekleme / sonuç | 11 | 11. ev lordu + Ay |

## 6.3 Muhurta motoru: tarama + puanlama

```
GİRDİ: aksiyon türü + coğrafya + ufuk tarihi + natal filtre
  ↓
ZAMAN IZGARASI: gelecek 7/30 gün × 24 saat × planetary hour
  ↓
HER ADAY İÇİN:
  ├─ Panchanga: Tithi / Nakshatra / Yoga / Karana / Vara
  ├─ Nitya Yoga: Priti, Ayushman, Saubhagya, Shobhana, Siddhi → olumlu
  │              Vishkambha, Atiganda, Hula, Vajra → olumsuz
  ├─ Karana: Vishti (Bhadra) → kaçınılacak
  ├─ Choghadiya: Amrit / Shukla / Labh → olumlu
  │              Roag / Kal / Udveg → kaçınılacak
  ├─ Kala pencereleri: Rahu Kala, Yamaganda, Gulika → dışarı
  ├─ Hora lordu: aksiyonla eşleşiyor mu?
  ├─ Batı overlay: ASC lordu, Ay, aksiyon gezegeni dignity
  └─ Natal filtre: aday an, natal hassas noktaya ne yapıyor?
  ↓
PUANLAMA + SIRALAMA
  ↓
ÇIKTI: Top 3 pencere + her biri için gerekçe + gelenek atfı
       + "bu yöntem belirgin bir işaret vermiyor" seçeneği
```

## 6.4 Tutarlılığın teknik şartı: ÇERÇEVE AYRIMI

**En sık yapılan ve en öldürücü hata:** Doğu ile Batı'yı aynı hesap çerçevesine sokmak.

| Parametre | Batı | Vedik |
|---|---|---|
| Zodyak | Tropikal | Sideral (Lahiri vb.) |
| Ayanamsa | Uygulanmaz | **Açıkça seçilmeli ve gösterilmeli** |
| Ev sistemi | Placidus / Whole Sign / Equal | Genelde Whole Sign / Equal |
| Düğüm | Ortalama veya gerçek — tutarlı seçilmeli | Genelde gerçek (true node) |
| Öngörü | Transit + progression + return | Dasha + transit |

**Mimari zorunluluk:**

```json
"frames": {
  "western": {"zodiac":"tropical","ayanamsa":null,"house_system":"placidus"},
  "vedic":   {"zodiac":"sidereal","ayanamsa":"lahiri","house_system":"whole_sign"}
}
```

İki çerçeve **ayrı hesaplanır**, ayrı yorumlanır, **sonra** çakışma analizi yapılır. "Lahiri zodyakta Plüton'un yorumu" gibi kategorik hatalar üreten rakiplerin karşısına bunu koyun.

### Çakışma çözme politikası

| Durum | Ürün davranışı |
|---|---|
| İki gelenek aynı şeyi söylüyor | "İki gelenek de bu temayı işaret ediyor" — yüksek örtüşme |
| İki gelenek farklı şeyi söylüyor | **İkisini de göster.** "Vedik dönem destekliyor, Batı transit gerilim söylüyor. Bu bir iç gerilim." |
| Bir gelenek susuyor | "Bu tema için Batı çerçevesinde belirgin işaret yok." |
| Hiçbiri desteklemiyor | **Söyleme.** Konu açma. |

Bu politika, "tutarlılık" kelimesinin ürün karşılığıdır.

## 6.5 Bağımsızlık ilkesi — halüsinasyonun gerçek çözümü

**D1, D9, D10 aynı doğum verisinden türer. Bağımsız kanıt değildir.**

Çakışma puanlarken kural sayısını değil, **bağımsız çerçeve sayısını** sayın:

```
Bağımsız çerçeveler (en fazla 6):
  1. Batı natal
  2. Vedik natal (ayrı ayanamsa/çerçeve)
  3. Dasha
  4. Transit
  5. Sima (görüntüden gelen, bağımsız ölçüm)
  6. Horary (sorunun anının haritası — bağımsız zaman)

Örtüşme skoru = destekleyen BAĞIMSIZ çerçeve sayısı
  ≥3 ve çelişki yok → "yüksek örtüşme"
  =2                → "örtüşme var"
  çelişki var       → "gerilim / iki eğilim"
  ≤1                → "belirgin işaret yok" — ÜRETME
```

**Bu tek başına, rakiplerin "her soruya 800 kelime uyduran" yaklaşımını teknik olarak yenar.**

---

# BÖLÜM 7 — Sima: Kadim kaynak + görüntü işleme + füzyon ontolojisi

## 7.1 Kaynak katmanı: neyi, nereden alacağız

| Gelenek | Kaynak | Üründe rolü | Telif durumu |
|---|---|---|---|
| **Batı Chiromancy** | **William G. Benham, *The Laws of Scientific Hand Reading* (1900)** | Çizgi morfolojisinin omurgası: zincir, adacık, çatal, kırılma, keskinlik | **Public domain** — archive.org'da mevcut |
| Batı Chiromancy | Cheiro, *Language of the Hand* | Çizgi uzunluğu / parmak oranı taksonomisi | Erken dönem baskılar PD; sürüm kontrolü gerekli |
| Batı Chiromancy | des Arpentigny (1830'lar), Desbarolles | El şekli sınıflandırması | Tarama + PD doğrulama gerekli |
| **Hint / Vedik** | *Brihat Parashara Hora Shastra*, *Phaladeepa*, *Prashna Marga*, *Jaimini Sutras*, *Saravali*, *Hora Sara* | Vedik yorum kural tabanı | Klasik metinler; **tercüme sürümleri telifli olabilir** |
| **Kod–literatür köprüsü** | **PVR Narasimha Rao, *Vedic Astrology: An Integrated Approach*** | **PyJHora'nın kendi tanımında referans verdiği kitap** | Telifli. **Metni kopyalama; terminolojiyi ve yapıyı hizala** |
| **Batı Horary/Election** | **William Lilly, *Christian Astrology* (1647)** | Horary hüküm kuralları + electional | **Public domain** — en değerli açık kaynak |
| Hellenistik | *Tetrabiblos* (Ptolemaios), *Carmen Astrologicum* (Dorotheus), Alcabitius | Temel dignity / ev doktrini | Klasik metin PD; çeviri kontrolü |
| **İlmi Sîma / Firaset** | Osmanlı/İslam firaset literatürü; Atkinson, *Practical Physiognomy* | Yerli kültürel çerçeve ve dil | Atkinson erken dönem PD |
| **Çin Xiangfa** | 《麻衣神相》, 《神相全編》, 《柳庄相法》 | El/yüz şekli–element sınıflandırması | Çeviri ve telif durumu teyit gerekli |
| Hint beden bilimi | **Samudrika Shastra** kümesi | Mount / beden işaretleri geleneği | Sanskrit kaynak + tercüme taraması gerekli |

**Kritik içgörü:** PyJHora'nın kodu, Rao'nun kitabının yapısını takip ediyor. **Kural tabanınızı aynı terminolojiyle hizalarsanız, hesap katmanı ile yorum katmanı arasında kategorik kayma olmaz.** Bu, "tutarlılık" için en pratik mühendislik kararıdır.

## 7.2 Füzyon ontolojisi: Mount ↔ Graha

**Bu, el çizgisi ile astroloji arasındaki gerçek, geleneğe dayalı köprüdür.**

Rastgele "kalp çizgin Ay'inle uyumlu" demek yerine, gelenekte zaten var olan mount–gezegen eşlemesini kullanın:

| El mountu | Konum | Gezegen | Natal karşılaştırma |
|---|---|---|---|
| Jupiter | Şah parmağı dibı | Guru / Jüpiter | Jüpiter dignity + Shadbala + D10 |
| Saturn | Orta parmak dibı | Shani / Satürn | Satürn dignity + 10. ev |
| Apollo / Sun | Yüzük parmağı dibı | Güneş | Güneş + 1. ev + MC |
| Mercury | Serçe parmak dibı | Budha / Merkür | Merkür dignity + 3./10. ev |
| Venus | Baş parmak yastığı | Shukra / Venüs | Venüs + 7. ev |
| Luna / Moon | Elin dış alt yüzeyi | Chandra / Ay | Ay + 4. ev + Nakshatra |
| Mars (iki düzlük) | Elin iç üst / merkez | Mangala / Mars | Mars + 6. ev |

**Sentez mantığı:**

| Mount durumu | Natal durum | Yorum |
|---|---|---|
| Gelişmiş mount | Güçlü graha | **Tutarlı ifade** — potansiyel ve kanal hizalı |
| Gelişmiş mount | Zayıf/zorlu graha | **Kanal var, zamanlama bekliyor** — Dasha eşiği göster |
| Zayıf mount | Güçlü graha | **Potansiyel var, ifade gelişiyor** — öğrenme alanı |
| Zayıf mount | Zayıf graha | **Bu tema baskın değil** — zorla yorum üretme |

**Bu tablo, rakiplerde yok.** Ve uydurma değil; iki geleneğin kendi eşlemesi.

### İkinci köprü: El şekli ↔ Element

Çin/Hint el şekli sınıflandırması ↔ Batı element trigonları (Ateş/Toprak/Hava/Su). Üçüncü bir bağımsız doğrulama ekseni.

### Üçüncü köprü: Çizgi işareti ↔ Zaman

Benham/Cheiro geleneğindeki çizgi üzerindeki işaretler ve dönem göstergeleri ↔ Dasha zaman çizgisi. **Ama:** bunu "kesin tarih" olarak değil, "geleneksel dönem okuması" olarak sunun. Epistemik durumu arayüzde açıkça belirtin.

## 7.3 CV pipeline — gerçek üretim mimarisi

**Önemli uyarı: MediaPipe Hands palm çizgisi tespit ETMEZ.** 21 parmak/eklem landmark'ı verir. Çizgi tespiti ayrı bir problemdir. Bunu karıştırmak, projenin en kolay öldüğü yerdir.

```
[1] KAMERA / YÜKLEME
      ↓
[2] KALITE KAPISI  ← kritik, atlanırsa her şey çöp
      ├─ bulanıklık ölçümü (Laplacian variance)
      ├─ parlama / gölge tespiti
      ├─ el açıklığı ve pozlama
      └─ başarısızsa: "Elini şu açıya getir" — yönlendirmeli UX
      ↓
[3] NORMALİZASYON
      ├─ MediaPipe Hands → landmark
      ├─ perspektif homografi → düzlem el
      └─ standart ROI + ölçek invariance
      ↓
[4] ÖN İŞLEME
      ├─ CLAHE (kontrast dengeleme)
      ├─ Gabor filtre bankı (yön duyarlı çizgi güçlendirme)
      └─ ridge orientation haritası
      ↓
[5] SEGMENTASYON
      ├─ U-Net / DeepLabV3+ (etiketli veri ile fine-tune)
      ├─ bootstrap: SAM 2 ile prompt-tabanlı annotation
      └─ çıktı: 4 ana çizgi + ikincil işaret maskeleri
      ↓
[6] İSKELET / EĞRİ
      ├─ OpenCV ximgproc.thinning
      ├─ eğri uydurma + spline
      └─ çizgi grafik gösterge (graph representation)
      ↓
[7] ÖZELLİK ÇIKARIMI  ← asıl değer burada
      ├─ uzunluk, başlangıç/bitiş konumu
      ├─ derinlik (intensity profile)
      ├─ kırılma / kesinti sayısı
      ├─ adacık (island) sayısı
      ├─ çatal / dal sayısı ve yönü
      ├─ kesişim ve hangi mounta doğru aktığı
      └─ HER ÖZELLİK İÇİN güven skoru
      ↓
[8] KURAL MOTORU
      └─ (özellik vektörü) × (Benham/Cheiro kural tabanı)
         → rule_id + atıf + kutup + karşı-gösterge
      ↓
[9] SENTEZ
      └─ astroloji faktörü ile bağımsız-çerçeve çakışma analizi
```

## 7.4 Veri seti: gerçek darboğaz

| Kaynak | Görüntü sayısı | Üretim için yeterli mi? |
|---|---|---|
| Roboflow `palm-line-detection-9zzh0` | **46** | **Hayır. Bootstrap only.** |
| `yeonsumia/palmistry` | Araştırma seti | Yöntem referansı |
| `MuntahaShams/palm-line-detection` | Objeye dayalı, sınırlı | Baseline only |

**Karanlık gerçek:** Üretim kalitesinde bir el çizgisi modeli için **binlerce, etiketli, çeşitlilik içeren görüntü** gerekir. Açık kaynak bu işi çözmüş değil.

**Önerilen veri iş kolu (3–6 ay):**

| Adım | Hedef | Not |
|---|---|---|
| Annotation şeması | 4 ana çizgi + 8 özellik türü + mount ROI | Versiyonlu, sürümlenmiş |
| Toplama | **5.000–10.000 görüntü** | Açık rıza, çeşitlilik (ten rengi, yaş, cinsiyet, ışık) |
| Annotation | SAM 2 bootstrap + insan doğrulama | Çift etiketçi + uyuşma ölçümü |
| Eğitim | U-Net / DeepLabV3 fine-tune | Ten rengi stratifiye doğrulama |
| Çıkış ölçütü | Ana çizgiler için **IoU ≥ 0.75**, özellik sınıflandırmasında ölçülebilir doğruluk | "Çalışıyor" değil, ölçülmüş |

**Bu veri seti moat'ın kendisidir.** Kimse klonlayamaz.

**Ayırt edin:** Palmprint biyometri veri setleri (IITD, PolyU, Ezd64k) **kimlik tanıma** içindir, çizgi semantiği için değildir. Bunları karıştırmayın.

## 7.5 E5 değişim takibi: gürültüyü anlam sanma

Aylık el taramasında fark raporlamak istiyorsanız:

1. **Aynı normalize koordinat sistemine** oturt.
2. **Ölçüm güven eşiği** tanımla (ışık, açı, çözünürlük farkını normalize et).
3. Farkı **istatistiksel belirsizlik aralığı** ile karşılaştır.
4. Eşik altındaki fark → **"ölçülebilir değişim yok"** de.
5. Eşik üstü fark → kural motoruna git.

**Bu dürüstlük, uzun vadeli güvenin ta kendisidir.**

## 7.6 KVKK: el görüntüsü özel nitelikli kişisel veridir

Türkiye'de biyometrik veri **KVKK m.6 kapsamında özel nitelikli kişisel veridir.** Bu bir uyumluluk maddesi değil, **mimari zorunluluk ve pazarlama avantajıdır.**

| Zorunluluk | Uygulama |
|---|---|
| Ayrı, açık rıza | Doğum verisinden **ayrı** rıza akışı |
| Veri minimizasyonu | **Ham görüntüyü varsayılan olarak saklama** |
| On-device tercih | Normalize + özellik vektörünü sunucuya gönder, görüntüyü cihazda tut |
| Şifreleme | Aktarım + saklama |
| Silme SLA | Tek tuşla silme, gerçek silme, 30 gün tavan |
| Kişiye özel değerlendirme | DPIA / veri envanteri |
| Şeffaflık | "Elin telefonundan çıkmıyor" — **ürün vaadi olarak** |

**Konumlandırma cümlesi:**
> "Elinizi bir sunucuya göndermiyoruz. Çizgilerinizin ölçüsünü çıkarıyoruz, görüntüsünü sizin telefonunuzda bırakıyoruz."

Bu, rakiplerin hiçbirinin söyleyemediği bir vaattir.

---

# BÖLÜM 8 — AI Agent mimarisi: Sorumluluk, yetki, yasak, metrik

## 8.1 Temel ilke

**LLM asla hesap yapmaz. LLM asla ham efemeris görmez.**

LLM sadece, **deterministik katmanın ürettiği, kuralla süzülmüş, atıf taşıyan bir fakt nesnesini** insan diline çevirir.

```
[Deterministik Katman]                 [Olasılıksal Katman]
                                      
Swiss / PyJHora / kerykeion            
        ↓                              
   Fakt nesnesi (JSON)                 
        ↓                              
   Kural motoru (RULE)                 
        ↓                              
   Kanıt paketi + atıf grafı    ───→   Sentez LLM
        ↓                              
   Hafıza (MEM)                ───→   Persona LLM
                                      
   ↑ Asla ters yönde veri yazmaz ↑
```

## 8.2 Fakt kontratı (Calculation ↔ LLM arayüzü)

```json
{
  "schema_version": "1.0.0",
  "subject_id": "opaque_id",
  "computed_at": "2026-10-12T10:00:00+03:00",
  "ephemeris": {
    "adapter": "swiss_licenced",
    "version": "x.y.z"
  },
  "frames": {
    "western": {"zodiac":"tropical","house_system":"placidus"},
    "vedic":   {"zodiac":"sidereal","ayanamsa":"lahiri","house_system":"whole_sign"}
  },
  "natal": {
    "vedic": {"lagna":"...","moon_nakshatra":"...","pada":3},
    "western": {"sun":"...","moon":"...","asc":"..."}
  },
  "strength": {
    "shadbala": {"jupiter": {"total": "...","ratio": "...","rank": 3}},
    "ashtakavarga": {"sarva": [1,2,3],"bhinna": {}}
  },
  "dasha": {
    "system": "vimshottari",
    "active": {"md":"...","ad":"...","pd":"...","sd":"..."},
    "active_until": "ISO",
    "next_thresholds": [
      {"level":"pd","at":"ISO","from":"...","to":"..."}
    ]
  },
  "transits": {
    "hits": [
      {
        "transiting":"saturn",
        "reference":"natal_moon",
        "house_from_moon": 1,
        "pattern":"sade_sati_phase_2",
        "orb_deg": 0.83,
        "window": {"from":"ISO","to":"ISO"}
      }
    ]
  },
  "rules_triggered": [
    {
      "rule_id":"VED.D9.VEN.7H.014",
      "tradition":"vedic",
      "frame":"vedic",
      "source":{"work":"Brihat Parashara Hora Shastra","locator":"..."},
      "polarity":"benefic",
      "strength":0.72,
      "evidence":["..."],
      "counter_indicators":["..."],
      "epistemic_status":"traditional_interpretation"
    }
  ],
  "sima": {
    "capture_quality": 0.91,
    "lines": [{"id":"heart","features":[...],"confidence":0.88}],
    "mounts": [{"id":"jupiter","development":0.7}],
    "delta_since_last": null
  },
  "concordance": {
    "theme":"...",
    "independent_frames_supporting": 3,
    "contradictions": [],
    "verdict":"high_overlap"
  },
  "memory_refs": ["..."],
  "provenance": {
    "rule_base_version":"1.3.0",
    "model_version":"...",
    "expert_review_status":"approved"
  }
}
```

**Bu JSON, ürünün gerçek fikri mülkiyetidir.** Repo'yu klonlayan biri bunu elde edemez.

## 8.3 Kural kaydı şeması (moat'ın atomu)

```json
{
  "rule_id": "SIM.BEN.HEART.FORK.001",
  "tradition": "western_chiromancy",
  "source": {
    "work": "The Laws of Scientific Hand Reading",
    "author": "William G. Benham",
    "year": 1900,
    "locator": "bölüm/sayfa/figür"
  },
  "input_predicate": {
    "line": "heart",
    "feature": "fork",
    "location": "toward_jupiter_mount"
  },
  "output_theme": "...",
  "polarity": "mixed",
  "counter_indicators": ["..."],
  "requires_context": ["mount_development", "hand_shape"],
  "expert_review": {"status":"approved","reviewer":"...","date":"..."},
  "epistemic_status": "traditional_interpretation",
  "version": "1.0.0"
}
```

**300–500 adet bu kayıt = rakibin kopyalayamayacağı bir yorum tabanı.** PDF'i RAG'e atıp "kadim bilgi kullandık" demek değildir.

## 8.4 Agent sorumluluk matrisi

| Agent | Tip | Girdi | Çıktı | Yetkili tool | **YASAK** | Başarı metriği |
|---|---|---|---|---|---|---|
| **Kalc** | Deterministik | doğum verisi, zaman, konum | Fakt JSON | EphemerisPort, JH, KER | Yorum üretmek | 100 golden chart'ta %100 sayısal doğruluk |
| **Vision** | CV model | el görüntüsü | Çizgi/mount özellik vektörü + güven | MediaPipe, segmentasyon, feature extractor | Anlam üretmek | IoU ≥ 0.75, kalite kapısı geçme oranı |
| **Judge** | Deterministik kural motoru | Fakt JSON | Tetiklenen kural + atıf + kutup | RuleDB | Kural olmayan çıkarım | Atıf kapsama ≥ %95 |
| **Concordance** | Deterministik | Çoklu çerçeve kuralları | Örtüşme / gerilim / sessizlik | Bağımsızlık grafi | Sahte uzlaşı üretmek | Çelişki yakalama oranı |
| **Memory** | Retrieval + embed | Kullanıcı geçmişi | İlgili geçmiş olgu + olay + tercih | VectorDB, olay defteri | Yeni olgu uydurmak | Çapraz rapor çelişki oranı |
| **Synthesizer** | LLM | Kanıt paketi | Yapılandırılmış yorum JSON | Sadece Judge çıktısı | **Yeni sayı/tarih/olay üretmek** | Desteksiz iddia oranı < %1 |
| **Persona** | LLM | Sentez JSON + hafıza | Sıcak, doğal Türkçe metin/ses | Synthesizer çıktısı | Korkutma, determinizm, teşhis | Tone skoru, kullanıcı "beni anladı" oranı |
| **Election** | Deterministik arama + LLM açıklama | Aksiyon + ufuk | Ranked zaman penceresi | Muhurta tarayıcı, takvim | Kesinlik vaadi | Pencere → kullanıcı kabul oranı |
| **Horary** | Deterministik + LLM | Soru + an haritası | Hüküm + gerekçe + zaman | Horary kural motoru | Radikalite yokken hüküm vermek | "Belirsiz" diyebilme oranı |
| **Guard** | Politika + sınıflandırıcı | Her çıktı | Geç / düzelt / engelle | Politika DB | — | Kaçak oranı, hukuki risk |
| **Concierge** | LLM, kısıtlı | Niyet + bağlam | Dönüşüm teklifi **veya sessizlik** | SKU kataloğu, MEM | Istem dışı spam, manipülasyon | Dönüşüm / şikayet oranı |
| **Eval** | LLM + deterministik test | Altın set + üretim örnekleri | Kalite raporu | Golden set, contradiction detector | — | Haftalık kalite trendi |

## 8.5 Persona: "sıcak kanlı" nasıl mühendislik olur?

Bu bir prompt süsü değil, **tasarlanmış davranış seti**:

| Davranış | Uygulama |
|---|---|
| **Jeneriklik yasağı** | Her yorum, kullanıcının kendi verisinden en az 1 somut olgu içermek zorunda |
| **Kullanıcının dilini yansıtm** | MEM'den kullanıcının kendi kelimelerini al; "tıkanma" dediyse "tıkanma" de |
| **Ajans vermek** | "Şöyle olacak" değil, "şöyle bir eğilim var; sen nasıl deneyimliyorsun?" |
| **Seçim sunmak** | "İstersen bu kısmı açalım" — zorla 10 sayfa okutmak yok |
| **Belirsizliği söylemek** | "Burada işaret zayıf" güven üretir; uydurmak üretmez |
| **Takip etmek** | Rapor sonrası 48 saat: "Okudun mu, hangi kısım sana dokundu?" |
| **İnsana devretmek** | Her ekranda görünür "Bir insana bağlan" |
| **Korku yasağı** | Ölüm, hastalık, boşanma "kesinlik" ile verilmez |
| **Ton tutarlılığı** | Danışman personası sürümlenir; her oturumda karakter değişmez |

**Hybrid gerçek:** En sıcak deneyim saf AI değildir. **AI'nin hazırladığı dosyayı eline alan insan danışman** en sıcak deneyimdir. Bu yüzden H2 (Danışman Konsolu) sadece bir B2B SKU değil, ** sizin C2C sıcaklık stratejinizdir.**

## 8.6 Uçtan uca senaryo: "Perşembe sözleşme imzalayayım mı?"

```
1. Niyet sınıflandırıcı → contract + horary + election
2. Memory → doğum verisi, aktif Dasha, geçmiş raporlar, el özellikleri
3. calc_horary_chart(soru_anı, kullanıcı_konumu)
4. judge_horary()
     ├─ radikalite kontrolü
     ├─ 1. ev / 7. ev significator
     ├─ Ay uygulayıcı açı / Void of Course
     └─ hüküm: şartlı + gerekçe
5. scan_muhurta(7 gün, action=contract, natal_filter)
     └─ top 3 pencere
6. get_active_dasha() → dönem teması
7. scan_transits() → Merkür / Satürn durumu
8. concordance() → bağımsız çerçeve sayımı
     └─ çelişki varsa açıkça işaretle
9. Synthesizer → yapılandırılmış cevap (yeni olgu YASAK)
10. Guard → kesinlik/teşhis/ticaret vaadi taraması
11. Persona → 150 kelime, sıcak Türkçe + 3 zaman penceresi
12. Memory write → soru, hüküm, kullanıcı geri bildirimi
13. Concierge → kullanıcı daha fazlasını isterse C3/C4 teklif et
                  istemezse SUS
```

**Bu senaryo, tek başına rakiplerin seluruh ürün gamından daha değerlidir.** Çünkü bir karar anında, somut, gerekçeli ve zamanlı yardım sunuyor.

---

# BÖLÜM 9 — Rakip istihbaratı: kanıt disiplini ve saha protokolü

## 9.1 Önce dürüstlük

Bu oturumda canlı tarama yapamadım. Bu nedenle:

- ❌ "Nebula şu kadar ciro yapıyor" → **yok**
- ❌ "X uygulamasının aboneliği Y TL" → **yok**
- ❌ "Türkiye pazarı Z milyar" → **yok**

Önceki yanıtlardaki bu tür sayılar **geri çekilmiştir.** Bunun yerine onları çıkaracak yöntemi veriyorum. Bir istihbarat raporunda doğrulanmamış sayı, doğrulanmış sayıdan daha tehlikelidir.

## 9.2 Sekiz katmanlı kanıt toplama

| Katman | Kaynak / yöntem | Ne çıkar? | Güven |
|---|---|---|---|
| **1. Store metadatası** | App Store / Google Play sayfası, abonelik grupları, IAP isimleri, fiyat, intro offer, **gizlilik besin etiketi**, izinler | Gelir mimarisi + veri toplama stratejisi | **Yüksek** |
| **2. Binary / SDK** | Kendi indirilen APK/IPA; `Info.plist`, gömülü framework'ler; RevenueCat, AppsFlyer, Adjust, OneSignal, Braze, Branch, ManyChat tespiti | Retention/CRM stack, dönüşüm altyapısı | **Yüksek** |
| **3. Ağ gözlemi** | **Kendi hesabınızla**, Mitmproxy/Charles ile API host + endpoint + şema | Hesaplama client mı server mı? LLM kullanıyor mu? Paywall tetikleyicisi ne? | **Yüksek** |
| **4. Reklam kütüphaneleri** | **Meta Ad Library**, TikTok Creative Center, Google Ads Transparency Center | Aktif reklam sayısı, ilk görünme tarihi, kreatif formatı, CTA, landing page, offer | **Yüksek** |
| **5. Huni yürüyüşü** | Instagram → DM → WhatsApp → ödeme → teslimat. **Her adım ekran görüntüsü + zaman damgası** | Gerçek dönüşüm akışı, insan/bot oranı, fiyat çapası, upsell sırası | **Yüksek** |
| **6. Ciro estimasyonu** | Sensor Tower / data.ai / Appfigures aralıkları; review velocity heuristikleri | Yalnızca **aralık + düşük güven etiketi** | **Düşük–Orta** |
| **7. Topluluk madeni** | App Store 1–3★ yorumları, Ekşi Sözlük, şikayetvar, Reddit, Instagram yorumları | **Rakibin zayıflık listesi = sizin roadmap'iniz** | **Yüksek (şikayet gerçekliği)** |
| **8. Teknik/yetenek sinyali** | LinkedIn iş ilanları, GitHub commit, kurucu röportajları, fonlama haberleri | Nereye yatırım yapıyorlar? | Orta |

**En yüksek ROI'li katman 7'dir.** Rakibin 1 yıldızlı yorumları, sizin ürün ihtiyaç listenizdir. Bunu para ödemeden toplarsınız.

### Yorum madenciliği taksonomisi

Her yorumu şu 8 koddan birine atayın:

```
ACC  → "hep aynı şeyi söylüyor", "bana uymadı"        → jeneriklik
WARM → "soğuk", "robot gibi", "kişiselsiz"            → sıcaklık eksikliği
TIME → "ne zaman?", "geç kaldı", "takip yok"          → zamanlama eksikliği
PRC  → "pahalı", "para tuzağı", "gizli abonelik"      → fiyat/şeffaflık
TRU  → "güvenemedim", "korkuttu", "kesin dedi"        → epistemik aşırılık
UX   → "kullanamıyorum", "yüklenmiyor", "kamera"      → teknik kalite
PRV  → "verilerim nerede?", "silemiyorum"             → gizlilik
DEP  → "ilk gün iyiydi, sonra aynı"                   → derinlik/retention
```

**Bu 8 kodun frekans dağılımı, reklam kreatifinizin brief'idir.**

## 9.3 Kanıt defteri şeması

```json
{
  "claim_id": "INT-0142",
  "competitor": "...",
  "surface": "meta_ad_library | store | funnel | review | network",
  "observation": "Somut, yorum içermeyen gözlem",
  "artifact_path": "evidence/2026-10-12/...",
  "captured_at": "2026-10-12T...",
  "method": "ekran görüntüsü / SDK analizi / huni yürüyüşü",
  "confidence": "high | medium | low",
  "weakness_code": ["ACC","WARM","TIME"],
  "implication": "Bu gözlem hangi ürün kararını etkiliyor",
  "sku_mapping": ["C1","G3"],
  "creative_hook": "Bu zayıflığa karşı hangi mesaj",
  "recheck_due": "2026-11-12"
}
```

**Kural:** `artifact_path` boşsa, kayıt istihbarat değildir. Not defteridir.

## 9.4 14 günlük saha protokolü

| Gün | İş | Çıktı |
|---|---|---|
| 1–2 | 8–12 rakip envanteri; store sayfaları + fiyat + abonelik grupları arşivi | `competitors.csv` |
| 3–4 | APK/IPA SDK analizi; gizlilik etiketleri | `tech_stack_matrix.xlsx` |
| 5–6 | Meta Ad Library + TikTok taraması; aktif kreatif arşivi | `creative_library/` |
| 7–9 | **Huni yürüyüşü**: 5 rakibi baştan sona satın alım dahil | `funnel_walks/` (her adım kanıtlı) |
| 10–11 | Yorum madenciliği: rakip başına ≥100 yorum, 8 koda etiketleme | `weakness_frequency.csv` |
| 12 | Ağ gözlemi: kendi hesabı ile API şeması | `api_surface.md` |
| 13 | Ciro aralıkları (duyurulmuş estimasyonlar), güven etiketiyle | `revenue_ranges.md` |
| 14 | **Sentez:** zayıflık → fırsat → SKU → kreatif matrisi | `positioning_brief.md` |

**Hedef:** ≥60 kanıt kaydı, ≥8 kodlu zayıflık matrisi, ≥20 kreatif arşivi.

Bu yapıldıktan sonra "rakibin zayıflığına dayalı reklam stratejisi" bir tahmin değil, **belgelenmiş bir çıkarım** olur.

---

# BÖLÜM 10 — Gelir, reklam ve müşteri kazanımı

## 10.1 Rakip zayıflığı → fırsat → kreatif → SKU

| Kanıtlanacak zayıflık | Fırsat | Kreatif hook | SKU |
|---|---|---|---|
| **Jenerik / Barnum yorum** | Kişisel, doğrulanabilir olgu | Ekranda canlı el tarama; çizgi işaretleniyor; "Bu ölçüm sizin. Genel burç yorumu değil." | A5, E2 |
| **Korku ve determinizm dili** | Güçlendirici dil | "Kaderin yazılmış bir senaryo değil. Elindeki bir harita." | G3, G4 |
| **PDF raporu bir daha açılmıyor** | Yaşayan zaman asistanı | Takvime düşen bir zaman penceresi; kullanıcı "tamam" diyor | C1, G3 |
| **İnsana ulaşmak pahalı/rastgele** | Her zaman erişim + insan köprüsü | "İstersen makine konuşsun, istersen bir insan. Sen seç." | G4, H2 |
| **Sadece Batı astrolojisi** | Çift gelenek + şeffaf çakışma | "İki gelenek aynı şeyi mi söylüyor? Bazen söylemiyor. Biz ikisini de gösteriyoruz." | A5 |
| **Soru soramıyorum** | Horary: tek soruya hüküm | "Bir sorunuz var mı? Tek soru. Gerekçesiyle." | C3, C4 |
| **Aboneliğe değer yok / aynı metin** | Dasha eşik + gerçek ritim matematiği | "Her gün aynı şeyi söylemiyoruz. Bir şey gerçekten değiştiğinde yazıyoruz." | G2, G3 |
| **Gizlilik belirsizliği** | On-device palm | "Elin telefonundan çıkmıyor." | E1, E2 |
| **Doğum saati bilinmiyorsa uydurma** | Rectification sihirbazı | "Saatini bilmiyor musun? Sorun değil. Birlikte daraltalım." | A6 |

## 10.2 Kreatif formülü

```
[SOMUT GÖZLEM]  + [KANIT]  + [GELENEK ATFI]  + [AJANS VEREN CTA]
```

**Örnek (30 sn Reels):**

> 0–3 sn: "Bu çizgi sizin. Herkeste yok."
> 3–10 sn: Ekranda el taranıyor, kalp çizgisi işaretleniyor, ölçüm çıkıyor.
> 10–18 sn: "Benham 1900'de bu çatalı böyle okudu. Biz aynı kuralı sizin haritanızla karşılaştırıyoruz."
> 18–25 sn: "Vedik ve Batı iki farklı şey söylüyor. Hangisi? İkisini de görüyorsunuz."
> 25–30 sn: "Tek sorunu sor. Cevabın gerekçesiyle gelsin."

**Yasak kreatifler:** "Kaderinde var", "3 gün içinde", "şansın açılacak", "bunu bilmezsen zarar görürsün". Hem etik hem reklam/platform riski hem de uzun vadeli güven açısından.

## 10.3 Kazanımın altın noktaları — sıralı

| # | Altın nokta | Uygulama | Metrik |
|---|---|---|---|
| 1 | **İlk 15 saniyede reddedilemez doğruluk** | El taraması veya doğum verisiyle %100 kişiye özel bir olgu | Time-to-first-aha < 15 sn |
| 2 | **Görsel kanıt** | Çizginin üstünü çizmek, "güvenilirim" demekten 10 kat güçlü |Capture success rate |
| 3 | **Tek soru, tek cevap** | Horary ile düşük sürtünmeli ilk paid deneyim | C3 conversion |
| 4 | **Takvime girmek** | `.ics` / Google Calendar → ürün kullanıcıdan çıkmıyor | Calendar connect rate |
| 5 | **Bildirim izni anı** | İzni kayıtta değil, **ilk değer anından sonra** iste | Push opt-in |
| 6 | **48 saat takip** | "Raporu okudun mu? Hangi kısım sana dokundu?" | 48h re-engagement |
| 7 | **Dasha eşiği reactivation** | Önceden bilinen, kişisel, zamanlı tetikleyici | Churn recovery |
| 8 | **İnsan köprüsü her zaman açık** | "Bir insana bağlan" her ekranda | Human attach rate |
| 9 | **Şeffaf belirsizlik** | "Bilmiyorum" diyebilen ürün = tekrar gelen ürün | Repeat session |
| 10 | **Kullanıcının kendi dili** | MEM üzerinden kelime yansıtma | "Beni anladı" skoru |

## 10.4 Fiyat mimarisi (test hipotezi)

| Katman | Ürün | Hipotez bant |
|---|---|---|
| Ücretsiz | A1, A2, G1 | 0 |
| Giriş tek seferlik | C3 Tek Soru / E2 El-Harita | 149–249₺ |
| Premium tek seferlik | B5 Yıl Kitabı, B1 Yaşam Çizgisi, E4 Atlas | 449–899₺ |
| Aylık abonelik | G2 / G3 | 129–349₺ |
| Yıllık abonelik | G3 + B5 dahil | 1.290–2.490₺ |
| İnsan seans köprüsü | G4 / marketplace | 750–2.500₺; platform %25–30 |
| B2B | H1 / H2 | Kotaya dayalı, sözleşmeli |

**Gelir karması hedefi:** %40 abonelik / %30 tek seferlik / %20 insan pazarı / %10 B2B.

**Birim ekonomi formülü** (tahmin değil, ölçülecek denklem):

```
Maksimum CAC ≤
    (aylık ARPU × brüt marj × beklenen ömür/ay)
  + (tek seferlik dönüşüm oranı × ortalama sepet × brüt marj)
  + (insan seans attach × komisyon × tekrar oranı)
```

Bu denklemi **kanaldan ölçmeden** reklam bütçesi artırmayın. Rakiplerin "cirosu" hakkında tahmin yürütmekten çok daha değerlidir.

## 10.5 Sosyal medya faaliyet modeli

| Kanal | İçerik tipi | Huni görevi |
|---|---|---|
| **Instagram Reels** | "Bu çizgi ne anlama gelir?" — eğitim, somut görsel | Keşif → DM |
| **Instagram DM (ManyChat)** | Anahtar kelime → mini okuma → uygulama | DM → aktivasyon |
| **TikTok** | 15 sn'lik "iki gelenek karşılaştırması" | Keşif → profil |
| **YouTube** | 15–25 dk derinlemesine gelenek/kaynak anlatımı | Güven → yıllık abonelik |
| **WhatsApp Business** | Rapor teslimi + günlük kart + insan köprüsü | Dönüşüm + retention |
| **Telegram bot** | Düşük sürtünmeli C3 (Tek Soru) | İlk paid |
| **Newsletter** | Haftalık kişisel + editoryal | Retention |
| **Podcast** | Kurucu + kadim literatür konukları | Otorite |
| **GitHub / MCP dizinleri** | Açık hesap katmanı + kapalı yorum katmanı | Geliştirici kazanımı |

**Kritik ayrım:** Sosyal medyada **eğitim** verin, **hüküm**ü ürün içinde satın. Her şeyi ücretsiz veren hesap, ürün satamaz.

---

# BÖLÜM 11 — Dağıtım: "Her yerden ulaşılabilir" mimarisi

## 11.1 Tek kimlik, tek fakt deposu, tek hafıza

```
                    ┌──────────────────────────┐
                    │   SUBJECT IDENTITY       │
                    │   FACT STORE             │
                    │   NARRATIVE MEMORY       │
                    └────────────┬─────────────┘
                                 │
        ┌────────┬───────┬───────┼────────┬────────┬────────┐
        │        │       │       │        │        │        │
      Web/PWA  iOS/And  WhatsApp Telegram Instagram Takvim  MCP
        │        │       │       │        │        │        │
        └────────┴───────┴───────┴────────┴────────┴────────┘
                                 │
                    ┌────────────┴─────────────┐
                    │  Widget / Watch / Ses     │
                    │  E-posta / SMS            │
                    └──────────────────────────┘
```

**Her kanalda aynı danışman, aynı hafıza.** Kullanıcı Instagram'da başladığı sohbeti WhatsApp'ta, oradan uygulamada devam ettirebilmeli. Rakiplerin çoğunda her kanal ayrı bir deneyim.

## 11.2 MCP bir ürün değil, **dağıtım kanaludur**

Bu, sorunuzun önemli bir parçası.

- `astrology-mcp` ve benzerleri zaten hesaplamayı LLM'e açıyor.
- Siz **kişisel MCP sunucusu** yayınlayın: kullanıcı Claude/Cursor/uyumlu istemcisinde "benim haritamda şu dönem ne?" diyebilsin.
- **Entitlement sınırı:** MCP hesap + fakt açsın; **Sentез + hafıza + Sima + Muhurta entitlement arkasında** olsun.

Böylece:
1. AI istemcileri sizin **kazanım kanalınız** olur.
2. Geliştiriciler sizin **istribütörünüz** olur.
3. Ücretsiz MCP ile rekabet etmek zorunda kalmazsınız — **üstüne katman olursunuz.**

## 11.3 İletişim köprüsü: gerçek huni

```
Instagram Reels
      ↓  (yorum/DM anahtar kelime)
ManyChat otomatik DM
      ↓  ("detayını istersen")
WhatsApp Business
      ↓  (ücretsiz 1 olgu + sesli kısa okuma)
Tek Soru / El-Harita raporu  ← ilk paid
      ↓  (48 saat takip)
Uygulama / PWA kaydı
      ↓  (takvim bağla, push aç)
G3 Aboneliği
      ↓  (Dasha eşiği / dikey öneri)
Yıl Kitabı / Ömür Atlası
      ↓  (ihtiyaç anında)
İnsan danışman seansı
      ↓  (danışman memnuniyeti)
H2 Konsolu / B2B
```

**Her ok bir veri noktasıdır.** Hangi okta kayıp olduğunu bilmeden kreatif bütçesi artırmayın.

---

# BÖLÜM 12 — A'dan Z'ye geliştirme planı

## 12.1 Fazlar ve çıkış ölçütleri

| Faz | Süre | İş | **Çıkış ölçütü (kanıtla)** |
|---|---|---|---|
| **P0 — İstihbarat + karar** | 2 hafta | Rakip saha protokolü; lisans kararı; fakt şeması; SKU onayı | ≥60 kanıt kaydı; imzalı lisans kararı; 40 SKU'dan 6 MVP seçimi |
| **P1 — Hesaplama çekirdeği** | 4–6 hafta | EphemerisPort; JH + KER adaptörü; Dasha timeline; transit tarayıcı; varga seti | **100 golden chart'ta %100 sayısal doğruluk**; 7.380 düğüm üretiliyor; çerçeve ayrımı test edilmiş |
| **P2 — Kural tabanı + hüküm** | 6–10 hafta | 300–500 kural kaydı; atıf grafı; Horary motoru; Muhurta tarayıcı; çakışma politikası | **100 uzman-onaylı vaka**; atıf kapsama ≥%95; "bilmiyorum" yolu çalışıyor |
| **P3 — Sima CV** *(P2 ile paralel)* | 8–12 hafta | Veri toplama + rıza; 5.000+ etiketli görüntü; segmentasyon; feature extraction; KVKK akışı | **IoU ≥0.75**; ten rengi stratifiye doğrulama; ham görüntü saklanmıyor |
| **P4 — Agent + UX + hafıza** | 4–6 hafta | Orchestration; MEM; Persona; interaktif harita; el overlay; rectification sihirbazı | Time-to-first-aha **<15 sn**; desteksiz iddia **<%1**; çapraz rapor çelişkisi **<%2** |
| **P5 — Monetizasyon + dağıtım** | 4 hafta | Ödeme; paywall; WhatsApp/ManyChat; takvim; widget; MCP; A/B | Ölçülmüş conversion + D30 retention + kanal bazlı CAC |
| **P6 — Sürekli flywheel** | sürekli | Eval; kullanıcı geri bildirimi → kural revizyonu; veri seti büyümesi; B2B | Haftalık kalite trendi; aylık yeni etiketli görüntü |

## 12.2 Ekip

| Rol | Sayı | Neden kritik |
|---|---|---|
| Ürün / tasarım | 1 | Projeksiyon mimarisi ve sıcaklık tasarımı |
| Backend (Python) | 2 | Hesaplama + kural motoru + orchestration |
| CV / ML | 1 | **Kritik yol; en zor iş** |
| Frontend / mobile | 1 | Overlay, interaktif harita, widget |
| **İçerik / literatür uzmanı** | 1 | **Bu işin en çok atlanan rolü.** Kadim metin → yapılandırılmış kural |
| Growth / operasyon | 1 | Huni, WhatsApp, danışman ağı |
| Hukuk (yarı zamanlı) | — | KVKK + lisans + reklam dili |
| Danışman astrolog/firasatçı (panel) | 3–5 | Golden set + kural onayı |

**7–8 çekirdek kişi.** "İçerik uzmanı"nı çıkarıp her şeyi LLM'e bırakırsanız, elinizde bir repo klonu olur.

## 12.3 Metrik ağacı

```
KAZANIM
 ├─ Kreatif CTR
 ├─ Profil → uygulama dönüşümü
 └─ CAC (kanal bazında)

AKTİVASYON
 ├─ Time-to-first-aha < 15 sn
 ├─ El yakalama başarı oranı
 ├─ Doğum verisi tamamlama oranı
 └─ İlk "bu bana uydu" onayı

DÖNÜŞÜM
 ├─ Ücretsiz → ilk paid (hedef: ölç, sonra hedef koy)
 ├─ C3 Tek Soru conversion
 ├─ Tek seferlik → abonelik yükseltme
 └─ Sepet / refund oranı

RETENTION
 ├─ D7 / D30 / D90
 ├─ Push opt-in + push → session
 ├─ **Aksiyon Zamanlayıcı haftalık aktif kullanım**  ← en önemli
 ├─ Takvim bağlı kullanıcı oranı
 └─ Dasha eşiği reactivation oranı

KALİTE
 ├─ Atıf kapsama ≥ %95
 ├─ Desteksiz iddia <%1
 ├─ Çapraz rapor çelişkisi <%2
 ├─ "Belirsiz" diyebilme oranı
 └─ "Beni anladı" skoru

EKONOMİ
 ├─ ARPU / LTV
 ├─ LTV:CAC
 ├─ Gelir karması (%40/%30/%20/%10)
 └─ Danışman attach + komisyon
```

**Tek metrik seçecekseniz:** *Aksiyon Zamanlayıcı haftalık aktif kullanım.* Çünkü bu, ürünün hayatın içine girdiğinin tek gerçek kanıtıdır. Açılan PDF değil, **gerçekleşen aksiyon**.

## 12.4 Risk matrisi

| Risk | Seviye | Önlem |
|---|---|---|
| **Swiss Ephemeris lisansı** | 🔴 Yüksek | P0'da karar; EphemerisPort soyutlaması; ticari lisans bütçesi |
| **KVKK biyometrik veri** | 🔴 Yüksek | On-device-first; ham görüntü saklamama; ayrı rıza; DPIA |
| **CV veri kıtlığı** | 🔴 Yüksek | P3'ü P2 ile paralel başlat; 46 görüntülük setlere aldanma |
| **LLM halüsinasyonu / tutarsızlık** | 🔴 Yüksek | Deterministik Judge + bağımsız çerçeve + atıf zorunluluğu + golden set |
| **Store / ödeme kategori riski** | 🟠 Orta | "Fal" değil "kadim bilgi + kişisel zamanlama / kültürel içerik" konumlandırması; hukuki teyit |
| **Öngörü iddiası / güven** | 🟠 Orta | Epistemik durumu arayüzde açıkça belirt: *geleneksel yorum*, doğrulanmış öngörü değil |
| **Özellik kopyalama** | 🟠 Orta | Moat'ı özelliğe değil; **veri seti + kural tabanı + hafıza + dağıtım**a kur |
| **İnsan danışmana bağımlılık** | 🟠 Orta | H2 Konsolu ile danışmanın iş akışını ürünleştir |
| **Bildirim yorgunluğu** | 🟡 Orta | Günde 1 tavan; sadece gerçek değişimde; sessiz saat |

---

# Son: Ürünün tek cümlelik tanımı

> **"Genel burç yorumu satmıyoruz. İki geleneğin, kadim bir el okuma kural tabanının ve kendi yaşam verinizin birlikte çalıştığı kişisel bir zamanlama asistanı yapıyoruz."**

Bu cümledeki her kelime bir teknik katmana karşılık geliyor:

| Cümle parçası | Teknik karşılık |
|---|---|
| "İki geleneğin" | Ayrı `frames`, ayrı ayanamsa, çakışma analizi |
| "Kadim el okuma kural tabanı" | 300–500 atıflı kural kaydı + Benham/Samudrika/Xiangfa |
| "Kendi yaşam verinizin" | MEM + rectification + longitudinal Sima |
| "Birlikte çalıştığı" | Bağımsız-çerçeve concordance + agent orchestration |
| "Kişisel zamanlama asistanı" | Dasha ritim matematiği + Muhurta derleyicisi + takvim |

**MVP'de inşa edilecek olan tam olarak budur.** Geri kalan 34 SKU, bu çekirdeğin üzerine biner.

---
