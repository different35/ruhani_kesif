# Geliştirme Süreci — Spec-güdümlü, kanıt-kapılı turlar

> Durum: **Yürürlükte** · Sahip: proje sahibi · Son revizyon: SPEC-001 turu
> Bu belge, motora giren **her** değişikliğin (yeni modül, düzeltme, entegrasyon)
> nasıl tanımlandığını, uygulandığını, doğrulandığını ve kayda geçtiğini standartlaştırır.

## 1. Neden bu süreç var

Bu motorun çıktısı (gezegen boylamı, lagna, dasha, yoga hükmü…) kullanıcıya
**gerçek** bir yorum olarak sunulacak. Hesap hatası sessizdir: yanlış bir
pada veya bir dakika kaymış bir dasha başlangıcı hiçbir istisna fırlatmaz.
Bu yüzden:

1. **Kapsam yazılı ve dar olmalı** — bir tur tek bir hedefi kapatır.
2. **İddia = kanıt** — çalıştırılmış komut + ham çıktı yoksa durum "doğrulanmadı"dır.
3. **Teşhis de iddiadır** — kök neden ölçümle kanıtlanmadan düzeltme reçetesi yazılmaz.

### 1.1 Bu kuralları doğuran gerçek olaylar (SPEC-001 turundan)

| Olay | Sonuç | Kural |
|---|---|---|
| Docstring "`ts.tt_jd(jd_ut)` UT→TT çevirir" diyordu; yanlıştı | 38 test kırmızı, Ay'da −40″ | §4 G2: kütüphane davranışı iddiası canlı ölçümle kanıtlanır |
| Önceki turun teşhisi "J2000-mean yerine true ecliptic gerekir" idi | Uygulansaydı sapma −1318″'ye çıkacaktı; çerçeve zaten of-date idi | §4 G1: teşhis reçeteden önce ayrı ölçülür |
| Test helper'ı `TS.delta_t`, `Time.ut1_jd` (var olmayan API) ve ters `altaz()` açılımı kullanıyordu | 18 test hiç koşmamış halde commit'lenmişti | §4 G3: commit'lenen her test en az bir kez yerelde koşar |
| Sunrise penceresi oracle'ınkiyle farklı semantikteydi | 86400 s sahte fark | TEST_STANDARD §4: sözleşme hizalama tablosu zorunlu |
| PR'lar `main` yerine yan dallara zincirleme merge edildi | `main` 10 PR geride; gerçek kod tabanı belirsiz | §6 dal politikası (ADR-002) |

## 2. Roller

| Rol | Sorumluluk | Yapamaz |
|---|---|---|
| **Sahip** (proje sahibi) | Spec onayı, kapsam kararı, ADR kararı, merge | — |
| **Uygulayıcı** (insan veya ajan) | Spec taslağı, kod, birim test, kanıt toplama | Kendi spec'ini onaylamak; toleransı sonuç geçsin diye gevşetmek |
| **Doğrulayıcı** (ayrı oturum/ajan tercih edilir) | Oracle ızgarası, mutasyon testi, VERIFICATION kaydı | Üretim kodunu değiştirmek |

Aynı ajan iki rolü üstlenirse, doğrulama adımları **ayrı commit** olarak ve
mutasyon kanıtıyla yapılır (testin boş olmadığının kanıtı).

## 3. Tur yaşam döngüsü

```
 ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌────────────┐   ┌──────────┐   ┌────────┐
 │ 0.Keşif  │──▶│ 1.Spec    │──▶│ 2.Onay   │──▶│ 3.Uygulama │──▶│4.Doğrula │──▶│5.Kayıt │
 │ (ölçüm)  │   │ (taslak)  │   │ (Sahip)  │   │ (kod+test) │   │(oracle+  │   │(ledger,│
 └──────────┘   └───────────┘   └──────────┘   └────────────┘   │ mutasyon)│   │ PR)    │
                                                                 └──────────┘   └────────┘
```

| Faz | Girdi | Çıktı | Kapı (geçmeden ilerlenmez) |
|---|---|---|---|
| **0. Keşif** | Önceki turun "sonraki adım" notu, VERIFICATION açık maddeleri | Ham ölçüm, yeniden üretilmiş hata (komut + çıktı) | **G0**: Sorun yerelde yeniden üretildi (ör. "56 failed" kendimiz gördük) |
| **1. Spec** | Keşif çıktısı | `docs/specs/SPEC-NNN-*.md` ([şablon](../specs/SPEC_TEMPLATE.md)) | **G1**: Kök neden ölçümle kanıtlı; kabul kriterleri sayısal; kapsam-dışı listesi yazılı |
| **2. Onay** | Spec taslağı | Spec durumu `Approved` | Sahip onayı. *Hata düzeltmesi* turlarında, kök neden kanıtı tek-satır değişime indiriyorsa uygulayıcı ilerleyip PR'da onay ister |
| **3. Uygulama** | Onaylı spec | Kod + birim/regresyon testi | **G2**: Kütüphane davranış iddiaları canlı kanıtlı; docstring'ler spec'e atıf yapar |
| **4. Doğrulama** | Kod | Oracle ızgarası sonucu, mutasyon sonucu | **G3**: Tüm suite yeşil; her yeni test en az bir mutasyonla kırılıyor; toleranslar TEST_STANDARD §5'e uygun |
| **5. Kayıt** | Kanıtlar | VERIFICATION.md satırı, BACKLOG güncellemesi, PR | **G4**: PR şablonu eksiksiz; "sonraki tur" notu yazılı |

### 3.1 Definition of Ready (spec onaylanabilir mi?)

- [ ] Hedef tek cümle ve ölçülebilir ("Ay boylamı oracle'a ≤5″").
- [ ] Oracle seçili ve **sözleşme hizalama tablosu** dolu (TEST_STANDARD §4).
- [ ] Girdi/çıktı veri sözleşmesi (tipler, birimler, zaman ölçeği, çerçeve) yazılı.
- [ ] Bağımlı olduğu modüller `Done` durumunda (bkz. [specs/INDEX.md](../specs/INDEX.md)).
- [ ] Kapsam-dışı maddeler açıkça listeli.
- [ ] Kaynak (kitap/PyJHora fonksiyonu/makale) referansı var — kural tabanlı modüllerde zorunlu.

### 3.2 Definition of Done (tur kapanabilir mi?)

- [ ] Spec'teki tüm kabul kriterleri (AC) kanıt satırıyla işaretli.
- [ ] `python -m pytest -q` tamamı yeşil; çıktı PR'a yapıştırıldı.
- [ ] Mutasyon kanıtı: en az bir kasıtlı bug → hangi testlerin kırıldığı yazılı.
- [ ] VERIFICATION.md ilgili satır(lar) güncel; eski yanlış iddialar silinmedi, **düzeltildi olarak işaretlendi**.
- [ ] BACKLOG.md durum sütunu güncel.
- [ ] Docstring/yorumlarda spec ile çelişen iddia kalmadı.
- [ ] Kapsam dışı kalan bulgular `INDEX.md` kuyruğuna veya BACKLOG'a eklendi.

## 4. Kanıt kuralları (kapıların detayı)

- **G0 — Yeniden üretim:** "N test kırmızı" iddiası kendi ortamında koşturulmadan kabul edilmez.
- **G1 — Kök neden ölçümü:** Her hipotez için *ayrık* deney: yalnız o değişken
  değiştirilir, diğerleri sabit tutulur, sonuç tabloya yazılır. Birden fazla
  hipotez varsa her birinin katkısı ayrı ölçülür (SPEC-001 §3 örneği).
- **G2 — Kütüphane davranışı:** "X fonksiyonu Y yapar" cümlesi yalnızca
  çalıştırılmış bir snippet çıktısıyla yazılabilir. Snippet spec'e eklenir.
- **G3 — Test boş olmamalı:** Yeni/değişen her test, ilgili üretim satırı
  bozulduğunda kırılmalı. Kanıt: `sed` ile mutasyon → `pytest` çıktısı → geri al.
- **G4 — Kayıt değişmezliği:** VERIFICATION.md'de yanlış çıkan eski iddia
  silinmez; üstü çizilir/“DÜZELTİLDİ (SPEC-NNN)” notu düşülür. Geçmiş öğreticidir.

## 5. Kapsam disiplini

- Bir tur = bir spec = bir PR. Tur sırasında bulunan **başka** sorun düzeltilmez;
  spec'in "Bulgular / sonraki tur" bölümüne yazılır.
- İstisna: Spec'in kendi kabul kriterini doğrulamayı engelleyen test-altyapısı
  hatası (SPEC-001'deki sunrise helper hataları gibi) aynı turda düzeltilir ve
  spec'te ayrı satırda belirtilir.
- Tolerans değişikliği ayrı bir karardır: gerekçesi (oracle belirsizliği,
  fiziksel sınır) spec'te yazılmadan tolerans gevşetilemez.

## 6. Dal ve PR politikası (bkz. [ADR-002](../adr/ADR-002-trunk-branch-policy.md), uygulama: [CONTRIBUTING.md](../../CONTRIBUTING.md))

- Tek gövde (trunk): `main`. Her tur `main`'den açılan kısa ömürlü dalda yapılır.
- PR başlığı: `SPEC-NNN: <kısa hedef>`; gövde [PR şablonu](../../.github/pull_request_template.md) ile.
- PR `main` dışında bir dala **merge edilmez** (zincirleme merge geçmişi bozar).
- Merge koşulu: PR'ın son commit'inde `make gate` **GEÇTİ** (rapor PR'da; [ADR-003](../adr/ADR-003-local-ci-gate.md)) + DoD tamam + Sahip onayı.
- Spec PR'ları squash ile, konsolidasyon PR'ları merge commit ile birleşir; dal merge sonrası silinir.

## 7. Tur sonu "devir notu" formatı

Her turun son mesajı ve PR açıklaması şu bloğu içerir — bir sonraki turun
Keşif fazının tek girdisi budur:

```
DEVİR NOTU — SPEC-NNN
Kapanan: <AC listesi, geçti/kaldı>
Kanıt:   <pytest özet satırı>, <mutasyon sonucu>
Açık bulgular: <madde — önerilen spec numarası>
Sonraki tur önerisi: SPEC-MMM <başlık> (DoR eksikleri: ...)
Doğrulanmamış iddialar: <varsa açıkça>
```
