# PRODUCT.md — Kapsam → Ürünleştirme → Planlama

> Bu belge **ürünleştirmenin ana kaynağıdır**. ROADMAP.md yalnızca faz/çıkış ölçütlerini içerir; ürün kalemlerinin tanımı, kullanıcıya nasıl göründüğü ve hangi fazda üretildiği burada izah edilir.
> Kaynak: https://gist.github.com/different35/2e26066e6a025e3228568ef8648428e8 (BÖLÜM 9–12)

---

## 1. Kapsam: Ne yapıyoruz, ne yapmıyoruz

### YAPTIĞIMIZ (kapsam içi)
| # | Kapsam kalemi | Açıklama |
|---|---|---|
| K1 | İki gelenek, ayrı çerçeve | Batı (tropical) + Vedik (sidereal+ayanamsa); hiçbir hesap iki çerçeveyi karıştırmaz; sentez ayrı "çakışma matrisi" katmanında yapılır |
| K2 | Kadim kural tabanı | 300–500 atıflı, şemalanmış yorum hükmü (Benham/Samudrika/Xiangfa + horary/muhurta literatürü) |
| K3 | Sima (el okuma) CV | Etiketli çizgi/mount verisiyle segmentasyon; on-device-first, ham görüntü saklanmaz |
| K4 | Kişisel zamanlama | Dasha/transit ritmi + Muhurta/Electional → "bu işi ne zaman yapayım?" sorusunun ürünsel cevabı |
| K5 | Longitudinal hafıza (MEM) | Kullanıcının geçmiş oturumlarını, gerçekleşen/gerçekleşmeyen olayları hatırlayan danışman; rectification buna besler |
| K6 | Doğum saati rectification | Olay doğrulamalı saat düzeltme sihirbazı |
| K7 | Dağıtım köprüleri | WhatsApp/Instagram botu, takvim entegrasyonu, MCP kanalı, danışman konsolu (B2B) |

### YAPMADIĞIMIZ (kapsam dışı — kalıcı yasaklar)
- ❌ **Genel burç yorumu / günlük fal içeriği** (kuzey yıldızı cümlesinin reddettiği şey)
- ❌ **LLM'e hesaplama yaptırmak** — LLM yalnızca Fact Contract üzerinde yorumlar; sayıyı üreten her zaman deterministik çekirdektir
- ❌ **Doğrulanmış öngörü iddiası** — tüm çıktılarda epistemik durum açıkça "geleneksel yorum" olarak etiketlenir
- ❌ **Ham biyometrik görüntü saklama** (KVKK; P3 rıza akışı hariç hiçbir yerde el verisi tutulmaz)
- ❌ Tek seferlik "PDF rapor dükkanı" olmamak — PDF bir teslim biçimidir, ürün değil (north-star: aksiyonun gerçekleşmesi)

---

## 2. Ürünleştirme: 40 SKU aile haritası + MVP'nin 6 kalemi

Her ürün kalemi şu alanlarla tanımlanır: **Girdi → Hesap katmanı → Kural katmanı → Çıktı deneyimi → Fiyatlama sınıfı → Faz.**

### 2.1 A-ailesi — Kimlik & Kök raporları (tek seferlik, giriş ürünü)

#### A1 — "Doğum İzi" (Batı natal özeti) ✅ MVP
- **Kullanıcıya vaadi:** "Haritanın sabit iskeleti: karakter çekirdeğin ve hayat temaların."
- **Girdi:** doğum tarihi/saati/yeri (saat yoksa "saatsiz modu" + A6'ya yönlendirme)
- **Hesap:** KER/SW — evler, gezegen boylamları, açılar
- **Kural:** RULE — natal tema eşleme (atıflı)
- **Çıktı:** interaktif harita + 7 bloklu kişisel anlatı; tek soru hakkı
- **Fiyat:** tek seferlik düşük bilet (~₺/€ giriş) · **Faz:** P1→P4
- **Neden MVP'de:** en düşük üretim maliyeti, veri toplama (doğum bilgisi) hunisinin ön ucu.

#### A2 — "Vedik Kök" (Lagna + Nakshatra + Pada) ✅ MVP
- **Vaad:** "Ruhani kök haritan: Lagna'n, yıldız grubun, yaşam yolunun Vedik adı."
- **Girdi:** aynı doğum verisi (sidereal yeniden hesap)
- **Hesap:** JH — Lagna, nakshatra/pada, chandra-lagna, temel varga'lar
- **Kural:** RULE — Vedik tema kayıtları (Chapters on the Koondalini vb. atıflar)
- **Çıktı:** nakshatra kartı + varga paneli + "Batı versiyonundan farkı" notu (çerçeve ayrımı vurgusu)
- **Fiyat:** tek seferlik · **Faz:** P1→P4
- **Neden MVP'de:** çift-gelenek konumlandırmanın ikinci ayağı; A1 ile bundle adayı.

#### A5 — "Çift Gelenek Sentezi" (çakışma matrisi) ✅ MVP
- **Vaad:** "İki gelenek aynı sana bakıyor: nerelerde hemfikir, nerelerde ayrılıyor — ve neden."
- **Girdi:** A1+A2 çıktıları (bağımsız hesaplanmış iki frame)
- **Hesap:** CAL yok; **Concordance motoru** — tema bazlı uzlaşma/çelişki sınıflandırması
- **Kural:** RULE — çakışma çözme politikası (BÖLÜM 6.4): uzlaşma→güçlendirilmiş hüküm, çelişki→iki ses de gösterilir, çözüm yoksa **"belirsiz" yolu**
- **Çıktı:** yeşil/haki/kırmızı çakışma matrisi + her satırda kaynak atfı
- **Fiyat:** premium tek seferlik · **Faz:** P2→P4
- **Neden MVP'de:** moat'in 1 ve 3 numaralı katmanlarını (kural tabanı + çerçeve bağımsızlığı) ilk kez *görünür* kılan ürün. Ayırt edici kanıt.

#### A6 — "Doğum Saati Rectification" ✅ MVP
- **Vaad:** "Doğum saatin belirsiz mi? Yaşam olaylarınla saatini geri hesaplıyoruz."
- **Girdi:** ±hata aralığı + kullanıcıdan 5–8 yaşam olayı (tarih + tür)
- **Hesap:** JH+KER — aday saat taraması, dasha/transit olay eşlemesi
- **Kural:** RULE — olay→yöneticilik eşleme kuralları
- **Çıktı:** olasılıklı saat + "bu olaylar bu saati destekliyor" kanıt listesi; MEM'e yazılır
- **Fiyat:** tek seferlik orta bilet · **Faz:** P1→P4
- **Neden MVP'de:** veri kalitesi çarpanı (yanlış saat = tüm downstream ürünler yanlış) ve re-aktive tetikleyici.

*(A-ailesi devamı — post-MVP: A3 Synastry/İliki Haritası, A4 Annual Return, A7 Güney-Hint Nadi seçmesi…)*

### 2.2 B-ailesi — Zaman & Ritim (abonelik çekirdeği)

#### B1 — "Dasha Ritmi" (öngörü takvimi) ✅ MVP (`B*` slotu)
- **Vaad:** "Hayatının içinde bulunduğun dönem: bu mahadasha/antardasha ne getiriyor, eşik tarihlerin neler?"
- **Girdi:** doğrulanmış doğum verisi (A6 çıkışı tercih edilir)
- **Hesap:** JH — vimshottari dasha timeline + `next_thresholds` (gezgin eşikleri), Shani sadhe-sati durumu
- **Kural:** RULE — dasha Lord tema kayıtları + transit pattern eşlemesi
- **Çıktı:** akışkan zaman çizelgesi + eşik günlerinde push ("ritim değişimi") bildirimi
- **Fiyat:** abonelik (B-ailesi = retention motoru) · **Faz:** P1→P4→P5(push)
- **Neden MVP'de:** north-star metriği (haftalık aktif kullanım) doğrudan besleyen tek ürün ailesi; reactivation döngüsünün kaynağı.

*(B2 Transit Gözü, B3 Yıllık Panjika kişiselleştirmesi…)*

### 2.3 C-ailesi — Aksiyon Zamanlayıcı (Muhurta / Electional) ⭐ farklılaştırıcı

#### C1 — "Aksiyon Zamanlayıcı" ✅ MVP (`C*` slotu)
- **Vaad:** "Şu işi ne zaman yapayım? — Takvimine yazılabilir, kişisel uygun pencerelerin."
- **Girdi:** eylem türü (imza, taşınma, görüşme, başlangıç…) + hedef aralık + kullanıcının natal/dasha bağlamı
- **Hesap:** CAL — muhurta tarayıcı (choghadiya, hora, lagna puanları; BÖLÜM 6.3)
- **Kural:** RULE — eylem→yönetici gezegen/ev eşlemesi (horary tablosunun electional hali)
- **Çıktı:** skorlu pencere listesi + **takvime tek tıkla yazma** (P5) + gerçekleşme takibi (MEM)
- **Fiyat:** abonelik üstü ek değer / kredi bazlı · **Faz:** P2→P4→P5(takvim)
- **Neden MVP'de:** "fal" kategorisinden çıkaran, raporu aksiyona bağlayan ürün; moat'in 4 numaralı katmanı. North-star metrik bu kalemin kendisidir.

*(C2 Horary "Tek Soru" — soru→ev eşleme motoru, kredi bazlı; P2 çıkış ölçütünün ürünsel yüzü.)*

### 2.4 D/E-ailesi — Sima (el okuma)

#### E1–E5 — El İzleri / Mount & Graha Füzyonu / Çizgi-Zaman / Ten Stratifikasyonu / **Değişim Takibi**
- MVP'de **YOK** (P3 paralel yürür ama kullanıcıya ilk sürüm P4 sonunda; ayrı KVKK rızası şart).
- E5 (delta_since_last) MEM'e bağlandığında abonelik için ikinci retention sebebi üretir.

### 2.5 F/G/H-ailesi — Platform & B2B (post-MVP)
- F: uygulama içi soru/odaklanma ürünleri; G: eğitim/kültürel içerik (konumlandırma riski azaltıcı); **H: Danışman Konsolu** (danışmanın iş akışını ürünleştirme — P6, komisyon modeli, danışmana bağımlılık riskinin panzehiri).

### 2.6 Kalan 34 SKU hakkında ilke
Post-MVP SKU'lar bu 6'sının **aynı çekirdek bileşenlerinin yeniden projeksiyonudur** (yeni girdi × yeni kural alt kümesi × yeni teslim kanalı). Katalog genişletmesi, çekirdeğe yeni kod yazarak değil, `sku/` altında proje dosyası ekleyerek yapılır. Bu, 40 SKU kataloğunun gerçekçi maliyet hesabıdır.

---

## 3. Ortak ürün altyapısı (ürün olmayan ama her ürünü taşıyan kalemler)

| Altyapı kalemi | Ne sağlar | Hangi ürünler tüketir | Faz |
|---|---|---|---|
| `EphemerisPort` + SW/JH/KER adaptörleri | Tüm gök hesapları; lisans riskinden yalıtım | hepsi | P1 |
| **Fact Contract v1.0.0** | Hesap↔yorum arasındaki tek sözleşme; LLM'e giden tek kapı | hepsi | P0 dondurulur, P4 uygulanır |
| RULE tabanı + atıf grafı | Her hükmün kaynağa bağlı olması; desteksiz iddia avı | A5, A6, B1, C1 öncelikle | P2 |
| MEM | Kişisel hafıza; "beni hatırlayan" danışman | A6, B1, C1, E5 | P4 |
| Deterministic Judge + eval harness | Desteksiz iddia <%1, çapraz çelişki <%2 SLA'sı | hepsi | P4 |
| Kanallar (WhatsApp/takvim/MCP) | Dağıtım; ürün değil boru hattı | B1 push, C1 takvim | P5 |

---

## 4. Paketleme & fiyat mimarisi (hipotez — P0/P5'te A/B ile doğrulanacak)

| Paket | İçerik | Sınıf |
|---|---|---|
| Serbest keşif | A1 önizleme (3 blok) + tek "bu bana uydu" mikro anı | funnel |
| Başlangıç | A1 + A2 bundle | tek seferlik |
| Derin Kimlik | A5 + A6 | tek seferlik premium |
| **Ritim Aboneliği** | B1 + C1 (aylık X kredi) + MEM kişiselleştirme | aylık ← LTV merkezi |
| Uzman teması | Danışmana yönlendirme (H ailesi üzerinden komisyon) | servis |

Gelir karması hedefi: %40 abonelik / %30 tek-seferlik premium / %20 kredi-bazlı soru / %10 B2B (rapor BÖLÜM 10).

---

## 5. Ürünleştirme → Faz planlaması (ROADMAP.md ile çapraz referans)

| Faz | Ürünleştirme çıktısı | ROADMAP çıkış ölçütü |
|---|---|---|
| **P0** (2 hf) | 6 MVP SKU'sunun kesin seçimi + fiyat hipotezleri + lisans kararı | ≥60 kanıt kaydı; imzalı karar; 6/40 seçim |
| **P1** (4–6 hf) | A1,A2,B1,C1'in **hesap** yarısı hazır (yorum yok, ham fact contract) | 100 golden chart %100 doğruluk; çerçeve ayrımı testli |
| **P2** (6–10 hf) | A5,C1(,C2)'nin **kural/hüküm** yarısı; "bilmiyorum" yolu | 100 uzman-onaylı vaka; atıf ≥%95 |
| **P3** (8–12 hf, ∥P2) | E-ailesi veri hattı (henüz kullanıcıya kapalı) | IoU ≥0.75; KVKK akışı |
| **P4** (4–6 hf) | **6 MVP SKU'sunun kullanıcıya görünür hale gelişi** + MEM + persona + judge | TTFA <15 sn; desteksiz iddia <%1 |
| **P5** (4 hf) | Paketleme, ödeme, WhatsApp, takvim(C1), MCP | ölçülmüş conversion + D30 + kanal CAC'i |
| **P6** (sürekli) | E-ailesi lansmanı, H konsolu, kalan 34 SKU proje dosyaları | haftalık kalite trendi |

**Sıra mantığı:** önce veri-hunisi ucunu üreten ucuz ürünler (A1/A2) → ayırt edici kanıt (A5) → retention motoru (B1/C1). Sima bilinçli olarak geç: en pahalı, en riskli (KVKK), en çok veri isteyen kalem; moat'in 3 numaralı katmanı ama MVP'nin hayatta kalma koşulu değil.

---

## 6. Kabul kriteri kontrol listesi (her SKU için ortak Definition of Done)
Bir ürün kalemi ancak şu yedisi tamamsa "bitti" sayılır:
1. Girdi eksikse düşüş modu tanımlı (saatsiz doğum, belirsiz olay tarihi…)
2. Tüm sayılar Fact Contract üzerinden geldi (LLM hesap yapmadı)
3. Her hükmün atfı var; atıfsız cümle UI'da gösterilmiyor
4. Epistemik durum ibareti mevcut ("geleneksel yorum", doğrulanmış öngörü değildir)
5. Çerçeve karışımı testi geçti (western/vedic alanları ayrı)
6. Judge eval setinde desteksiz iddia çıkmadı
7. Ölçüm noktaları gömülü (TTFA, "bu bana uydu" klik, dönüşüm)
