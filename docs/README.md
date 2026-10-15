# Mühendislik Dokümantasyonu

Bu dizin motorun **nasıl** geliştirildiğini ve doğrulandığını tanımlar.
Ürün kapsamı için kök dizindeki `PRODUCT.md` / `ROADMAP.md`, kanıt kaydı için
`VERIFICATION.md`, iş durumu için `BACKLOG.md`.

| Belge | Ne zaman okunur |
|---|---|
| [process/DEVELOPMENT_PROCESS.md](process/DEVELOPMENT_PROCESS.md) | Her turun başında — fazlar, kapılar (G0–G4), DoR/DoD, devir notu |
| [process/TEST_STANDARD.md](process/TEST_STANDARD.md) | Test yazarken / yeni entegrasyon eklerken — oracle, tolerans, mutasyon |
| [specs/INDEX.md](specs/INDEX.md) | Sıradaki turu seçerken — spec kaydı, bağımlılık grafiği, DoR eksikleri |
| [specs/SPEC_TEMPLATE.md](specs/SPEC_TEMPLATE.md) | Yeni spec açarken |
| [adr/](adr/) | Mimari/sözleşme kararı alırken veya sorgularken |

## Bir turu başlatmak (özet)

1. `specs/INDEX.md`'den sıradaki `Planned` spec'i seç; DoR eksiklerini kapat.
2. Sorunu/hedefi yerelde ölç (G0), `SPEC_TEMPLATE.md`'yi kopyala, §1–§9'u doldur.
3. Sahip onayı → uygula → `python -m pytest -q` + mutasyon kanıtı.
4. `VERIFICATION.md`, `BACKLOG.md`, `specs/INDEX.md` güncelle; PR'ı şablonla aç; devir notunu yaz.

## Ajan için tur başlatma istemi (kopyala-yapıştır)

```
Repo: different35/ruhani_kesif. Önce docs/process/DEVELOPMENT_PROCESS.md ve
docs/process/TEST_STANDARD.md'yi oku. docs/specs/INDEX.md'deki SPEC-<NNN>'i
DoR'a göre yaz (docs/specs/SPEC_TEMPLATE.md), kök neden/tasarım iddialarını
canlı ölçümle kanıtla, uygulamayı yalnız spec kapsamıyla sınırla, DoD
listesini eksiksiz kapat, PR'ı main'e .github/pull_request_template.md ile aç
ve devir notunu yaz. Kanıtsız iddia yazma; ölçemediğini "doğrulanmadı" olarak işaretle.
```
