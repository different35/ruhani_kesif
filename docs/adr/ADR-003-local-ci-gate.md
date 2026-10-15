# ADR-003 — GitHub Actions'sız CI: yerel kapı (`make gate`)

| Alan | Değer |
|---|---|
| Durum | **Accepted** (Sahip kararı: 2026-10-15) |
| Tarih | 2026-10-15 |
| İlgili | ADR-002 (tek gövde), PR #12 |
| Karar sahibi | proje sahibi |

## Bağlam
- Repo sahibinin GitHub hesabı faturalama nedeniyle kilitli. Actions job'ları başlamıyor; GitHub'ın mesajı: *"The job was not started because your account is locked due to a billing issue."* (`runner_id: 0`, hiçbir adım çalışmıyor).
- Sahip faturayı haksız buluyor ve ödemeyecek. İtiraz reddedildi, ödeme yöntemi kaldırıldı. **Kilit kalıcı kabul edilir.**
- Kod, dal, PR ve merge işlemleri kilitten etkilenmiyor (PR #12 bu durumda merge edildi).
- Test suite GitHub'a bağımlı değil: `make check` her temiz ortamda aynı sonucu verir (sürümler sabit, ephemeris dosyası repoda).

## Karar
1. **Merge kapısı yereldir:** Hiçbir PR, son commit'i (head SHA) `make gate` ile **GEÇTİ** almadan `main`'e merge edilmez.
2. `make gate` (`scripts/ci-gate.sh`) şunları yapar:
   - commit'i geçici, temiz bir kopyaya çıkarır (commit'lenmemiş dosyalar ve mevcut `.venv` kullanılmaz);
   - sıfırdan venv kurup `make check` çalıştırır (lint + lisans bekçisi + tüm testler);
   - dalın `origin/main` ile güncel olduğunu doğrular;
   - SHA'yı ve sürüm bilgisini içeren bir kanıt raporu üretir. Kapı yalnız hepsi geçerse **GEÇTİ** der.
3. Rapor PR'a yorum olarak yapıştırılır. Merge eden kişi, raporun SHA'sının PR'ın **o anki** head SHA'sıyla aynı olduğunu kontrol eder. Raporda bir sonraki push eskir, kapı yeniden koşulur.
4. Ajan oturumları kapıyı her merge öncesinde kendi izole konteynerinde koşar. Geliştirici makinesine bağımlılık yoktur.
5. `tests.yml` yalnız elle tetiklenir (`workflow_dispatch`); her push'ta kırmızı ✗ üretmez. Ruleset'te zorunlu durum kontrolü **yoktur** (olsaydı hiçbir PR merge edilemezdi).

## Sonuçlar
- **Olumlu:** Geliştirme engellenmez; kontrol aynı komutla aynı titizlikte sürer; kanıt PR'da kalıcı durur.
- **Olumsuz:** Kontrolü bağımsız bir sunucu değil, merge eden taraf koşar. Bu bir güven ödünüdür. Telafisi: temiz kopya + sıfırdan ortam, SHA'ya bağlı rapor, dal güncelliği zorunluluğu, mutasyonla kanıtlanmış kapı (aşağıda).
- **Kapının boş olmadığının kanıtı (2026-10-15):** Kasıtlı bozulmuş commit (`ut1_jd`→`tt_jd`) → `KALDI ❌`, `39 failed`, çıkış kodu 1. `main` @ ab9fd35 → `GEÇTİ ✅`, `150 passed`.
- **Kilitleyen dosyalar:** `scripts/ci-gate.sh`, `Makefile` (`gate`), `.github/pull_request_template.md`, `CONTRIBUTING.md` §3.

## Geri dönüş koşulu
Actions bir gün kullanılabilir olursa: `tests.yml`'ye `push`/`pull_request` tetikleyicileri geri eklenir, ruleset'e `pytest` zorunlu kontrolü konur ve kapı tekrar GitHub'a taşınır (REPO_SETTINGS §5). `make gate` yerel ön kontrol olarak kalır.

## Değerlendirilen alternatifler
| Alternatif | Neden şimdilik seçilmedi |
|---|---|
| Faturayı ödemek | Sahip kararı: ödenmeyecek |
| Harici ücretsiz CI (CircleCI vb.) | Sahibin ayrı bir hesap açmasını gerektirir. İstenirse ileride eklenebilir; kapı komutu aynı kalır (`make check`) |
| Kapısız devam (testsiz merge) | Projenin kanıt ilkesiyle (DEVELOPMENT_PROCESS §4) çelişir |
| Self-hosted runner | Kilidin self-hosted runner'ları da durdurup durdurmadığı **doğrulanmadı**; sürekli açık bir makine gerektirir |
