# ROADMAP — ruhani_kesif

> **Kaynak (hedef doküman):** https://gist.github.com/different35/2e26066e6a025e3228568ef8648428e8
> Bu yol haritası, söz konusu strateji/mühendislik raporundaki **BÖLÜM 12 (A'dan Z'ye geliştirme planı)** fazlarını ve rapordaki mimari zorunlulukları doğrudan hedef olarak alır.
>
> ⚠️ **Kapsam ve ürünleştirme bu dosyada DEĞİLDİR.** Ürün kalemlerinin izahı (girdi→hesap→kural→çıktı→fiyat), MVP'nin 6 SKU'sunun detaylı tanımı, paketleme ve Definition of Done → **[PRODUCT.md](PRODUCT.md)**. Bu dosya yalnızca **faz sırası ve çıkış ölçütlerini** içerir; PRODUCT.md §5'te çapraz referanslıdır.

## Ürünün tek cümlelik tanımı (kuzey yıldızı)

> "Genel burç yorumu satmıyoruz. İki geleneğin, kadim bir el okuma kural tabanının ve kendi yaşam verinizin birlikte çalıştığı **kişisel bir zamanlama asistanı** yapıyoruz."

Cümledeki her kelime bir teknik katmana karşılık gelir:

| Cümle parçası | Teknik karşılık |
|---|---|
| "İki geleneğin" | Ayrı `frames`, ayrı ayanamsa, çakışma analizi |
| "Kadim el okuma kural tabanı" | 300–500 atıflı kural kaydı (Benham / Samudrika / Xiangfa) |
| "Kendi yaşam verinizin" | MEM (longitudinal hafıza) + rectification + değişim takipli Sima |
| "Birlikte çalıştığı" | Bağımsız-çerçeve concordance + agent orchestration |
| "Kişisel zamanlama asistanı" | Dasha ritim matematiği + Muhurta derleyicisi + takvim entegrasyonu |

## Moat nerede? (hesaplama motoru değil)

Hesaplama açık kaynakta zaten var; moat beş katmandadır ve tüm fazlar bu beşini inşa edecek şekilde sıralanmıştır:

1. **Yorum kural tabanı + atıf grafı** (300–500 yapılandırılmış, kaynaklı kural kaydı)
2. **Longitudinal kullanıcı hafızası** (MEM — "beni hatırlayan" danışman)
3. **Etiketli el çizgisi veri seti** (5.000+ görüntü, üretim ölçeğinde)
4. **Aksiyon → zaman derleyicisi** (Muhurta / Electional — "ne zaman?" sorusunun ürünsel cevabı)
5. **Dağıtım + insan köprüsü** (WhatsApp / Instagram / MCP / danışman ağı)

---

## Fazlar ve çıkış ölçütleri

### P0 — İstihbarat + karar (2 hafta)
- [ ] Rakip saha protokolünün yürütülmesi (BÖLÜM 9.4, 14 günlük protokol) → **≥60 kanıt kaydı** (kanıt defteri şemasına uygun)
- [ ] **Swiss Ephemeris lisans kararı** (ticari lisans / AGPL uyum / soyutlama üzerinden MIT alternatifler) → imzalı karar belgesi
- [ ] Fact Contract şemasının dondurulması (bkz. aşağıdaki JSON sözleşmesi, `schema_version: 1.0.0`)
- [ ] 40 SKU katalogundan **6 MVP SKU'sunun seçimi** (aday havuz: A1 Doğum İzi, A2 Vedik Kök, A5 Çift Gelenek Sentezi, A6 Rectification, B-ailesi dasha/transit ürünleri, C-ailesi Muhurta/aksiyon ürünleri)
- **Çıkış ölçütü:** ≥60 kanıt kaydı; imzalı lisans kararı; 40 SKU'dan 6 MVP seçimi.

### P1 — Hesaplama çekirdeği (4–6 hafta)
- [ ] `EphemerisPort` arayüzü (zorunlu mimari karar):
  ```
  EphemerisPort
   ├─ longitude(body, date, frame) -> degrees
   ├─ houses(date, location, system) -> [12 cusps]
   ├─ ayanamsa(date, mode) -> degrees
   └─ events(window, body) -> [ingress, retro, station]

  Implementations:
   ├─ SwissEphemerisAdapter   (lisanslı)
   ├─ AstronomyEngineAdapter  (MIT — Don Cross/astronomy)
   └─ SkyfieldAdapter         (MIT — JPL SPK)
  ```
- [ ] PyJHora (JH) adaptörü — Vedik hesap: Lagna, nakshatra/pada, vimshottari dasha, shadbala, ashtakavarga, varga seti
- [ ] kerykeion (KER) adaptörü — Batı hesap: natal, evler, açılar, transit, synastry, return
- [ ] Dasha timeline üretimi + eşik hesabı (reactivation tetikleri için `next_thresholds`)
- [ ] Transit tarayıcı (günümüze "aksıyan" olay pencereleri; sadhe sati vb. pattern eşlemesi)
- [ ] **Çerçeve ayrımı (frame separation):** western=tropical / vedic=sidereal+ayanamsa; hiçbir hesap iki çerçeveyi karıştırmaz
- [ ] Golden chart test seti kurulumu
- **Çıkış ölçütü:** **100 golden chart'ta %100 sayısal doğruluk**; ~7.380 düğüm üretiliyor (veri yüzeyi tam döküm); çerçeve ayrımı test edilmiş.

### P2 — Kural tabanı + hüküm (6–10 hafta)
- [ ] **300–500 kural kaydı**, şema:
  ```json
  {
    "rule_id": "SIM.BEN.HEART.FORK.001",
    "tradition": "western_chiromancy",
    "source": {"work": "...", "author": "...", "year": 1900, "locator": "bölüm/sayfa/figür"},
    "input_predicate": {...},
    "output_theme": "...",
    "polarity": "mixed",
    "counter_indicators": [...],
    "requires_context": [...],
    "expert_review": {"status": "approved", "reviewer": "...", "date": "..."},
    "epistemic_status": "traditional_interpretation",
    "version": "1.0.0"
  }
  ```
- [ ] Atıf grafı (her hükmün kaynağa bağlanması) → **atıf kapsama ≥%95**
- [ ] Horary (soru) motoru: soru → ev eşleme tablosu + uygulanabilir akış (BÖLÜM 6.2)
- [ ] Muhurta tarayıcısı + puanlama (BÖLÜM 6.3)
- [ ] Çakışma çözme politikası (BÖLÜM 6.4) ve **"bilmiyorum" / "belirsiz" yolu** (bağımsızlık ilkesi, BÖLÜM 6.5)
- [ ] Uzman paneli onay akışı (3–5 astrolog/firasatçı)
- **Çıkış ölçütü:** 100 uzman-onaylı vaka; atıf kapsama ≥%95; "bilmiyorum" yolu çalışıyor.

### P3 — Sima CV (8–12 hafta, P2 ile paralel başlar)
- [ ] Veri toplama + **ayrı rıza akışı** (KVKK: el görüntüsü özel nitelikli kişisel veridir; BÖLÜM 7.6)
- [ ] **5.000+ etiketli görüntü** hedefi (araştırma ölçeğindeki 46 görüntülük setlere aldanma)
- [ ] Segmentasyon + feature extraction pipeline'ı (BÖLÜM 7.3 üretim mimarisi)
- [ ] Füzyon ontolojisi: Mount ↔ Graha, el şekli ↔ element, çizgi işareti ↔ zaman (BÖLÜM 7.2)
- [ ] E5 değişim takibi: gürültü/anlam ayrımı (delta_since_last)
- [ ] Ten rengi stratifiye doğrulama; **ham görüntü saklanmaz** (on-device-first)
- **Çıkış ölçütü:** IoU ≥0.75; stratifiye doğrulama; ham görüntü saklanmıyor.

### P4 — Agent + UX + hafıza (4–6 hafta)
- [ ] Orchestration: Calculation → Fact Contract → LLM; **LLM yalnızca fakt kontratı üzerinde yorumlar, hesap yapmaz** (BÖLÜM 8.1 sorumluluk/yetki/yasak matrisi)
- [ ] Fact Contract v1.0.0 uygulaması (tam şema: frames, natal, strength, dasha, transits, rules_triggered, sima, concordance, memory_refs, provenance)
- [ ] MEM — longitudinal kullanıcı hafızası
- [ ] Persona: "sıcak kanlı" anlatım mühendisliği (BÖLÜM 8.5)
- [ ] İnteraktif harita + el overlay UI
- [ ] Doğum saati rectification sihirbazı (olay doğrulamalı, A6)
- [ ] Deterministik Judge + eval harness (desteksiz iddia avı)
- **Çıkış ölçütü:** Time-to-first-aha <15 sn; desteksiz iddia <%1; çapraz rapor çelişkisi <%2.

### P5 — Monetizasyon + dağıtım (4 hafta)
- [ ] Ödeme + paywall (fiyat mimarisi hipotezleri, BÖLÜM 10.4)
- [ ] WhatsApp / ManyChat iletişim köprüsü (BÖLÜM 11.3)
- [ ] Takvim entegrasyonu (aksiyon zamanlayıcı → gerçek takvime yazma)
- [ ] Widget + **MCP dağıtım kanalı** (MCP bir ürün değil, kanaldır — BÖLÜM 11.2)
- [ ] A/B altyapısı; konumlandırma: "fal" değil "kadim bilgi + kişisel zamanlama / kültürel içerik"
- **Çıkış ölçütü:** Ölçülmüş conversion + D30 retention + kanal bazlı CAC.

### P6 — Sürekli flywheel (sürekli)
- [ ] Eval + kullanıcı geri bildirimi → kural revizyonu döngüsü
- [ ] Etiketli görüntü veri setinin aylık büyümesi
- [ ] B2B / danışman konsolu (H-ailesi SKU'lar; danışmanın iş akışını ürünleştirme)
- **Çıkış ölçütü:** Haftalık kalite trendi; aylık yeni etiketli görüntü.

---

## MVP kapsamı (P0'da kesinleşecek 6 SKU — ön aday listesi)

| ID | SKU | Kaynak katmanı |
|---|---|---|
| A1 | Doğum İzi (Batı natal özet) | KER+SW |
| A2 | Vedik Kök (Lagna+Nakshatra+Pada) | JH |
| A5 | Çift Gelenek Sentezi (çakışma matrisi) | KER+JH+RULE |
| A6 | Doğum Saati Rectification | JH+KER+MEM+RULE |
| B* | Dasha-güdümlü öngörü/ritim ürünü | JH+RULE |
| C* | Aksiyon Zamanlayıcı (Muhurta derleyicisi) | RULE+CAL |

Geri kalan 34 SKU bu çekirdeğin üzerine biner.

## Metrik ağacı (özet)

```
KAZANIM     : Kreatif CTR · Profil→uygulama · CAC (kanal bazlı)
AKTİVASYON  : Time-to-first-aha <15sn · El yakalama başarı · Doğum verisi tamamlama · İlk "bu bana uydu"
DÖNÜŞÜM     : Free→ilk paid · Tek soru conversion · Tek seferlik→abonelik · Sepet/refund
RETENTION   : D7/D30/D90 · Push opt-in→session · Aksiyon Zamanlayıcı haftalık aktif · Takvim bağlılık · Dasha eşiği reactivation
KALİTE      : Atıf kapsama ≥%95 · Desteksiz iddia <%1 · Çapraz çelişki <%2 · "Belirsiz" diyebilme · "Beni anladı" skoru
EKONOMİ     : ARPU/LTV · LTV:CAC · Gelir karması (%40/%30/%20/%10) · Danışman attach+komisyon
```

**North-star metric:** *Aksiyon Zamanlayıcı haftalık aktif kullanım* — açılan PDF değil, gerçekleşen aksiyon.

## Risk matrisi (özet)

| Risk | Seviye | Önlem (hangi fazda) |
|---|---|---|
| Swiss Ephemeris lisansı | 🔴 Yüksek | P0 karar + `EphemerisPort` soyutlaması (P1) + ticari lisans bütçesi |
| KVKK biyometrik veri | 🔴 Yüksek | P3: on-device-first, ham görüntü saklamama, ayrı rıza, DPIA |
| CV veri kıtlığı | 🔴 Yüksek | P3'ü P2 ile paralel başlatmak; büyük etiketli set hedefi |
| LLM halüsinasyonu/tutarsızlık | 🔴 Yüksek | P2/P4: deterministik Judge, bağımsız çerçeve, atıf zorunluluğu, golden set |
| Store/ödeme kategori riski | 🟠 Orta | P5: konumlandırma + hukuki teyit |
| Öngörü iddiası/güven | 🟠 Orta | Arayüzde epistemik durum açık: *geleneksel yorum*, doğrulanmış öngörü değil |
| Özellik kopyalama | 🟠 Orta | Moat = veri seti + kural tabanı + hafıza + dağıtım (özellik değil) |
| Danışmana bağımlılık | 🟠 Orta | P6: danışman konsolu ile iş akışını ürünleştirme |
| Bildirim yorgunluğu | 🟡 Orta | Günde 1 tavan; sadece gerçek değişimde; sessiz saat |

## Ekip hedefi (7–8 çekirdek kişi)

Ürün/tasarım ×1 · Backend (Python) ×2 · CV/ML ×1 (kritik yol) · Frontend/mobile ×1 · **İçerik/literatür uzmanı ×1** (en çok atlanan rol) · Growth/operasyon ×1 · Hukuk (yarı zamanlı) · Danışman paneli 3–5 kişi.

---

## Depo yapılanma hedefi (fazların kod karşılığı)

```
core/            # EphemerisPort + JH/KER adaptörleri, dasha/transit/varga (P1)
rules/           # Kural kayıtları + atıf grafı + çakışma politikası (P2)
sima/            # CV pipeline + rıza/KVKK akışı (P3)
agent/           # Orchestration, fact contract, persona, judge (P4)
memory/          # MEM longitudinal hafıza (P4)
channels/        # MCP sunucusu, WhatsApp köprüsü, widget, takvim (P5)
sku/             # Ürün projeksiyonları (A–H aileleri)
tests/golden/    # 100 golden chart + 100 uzman-onaylı vaka
```

> Not: Bu dosya gist'teki raporun **uygulanabilir hedef versiyonudur**. Detaylı gerekçeler, tam 40 SKU kataloğu, tam fact-contract şeması ve saha protokolleri için kaynak gist referans alınmalıdır.
