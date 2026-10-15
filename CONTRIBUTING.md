# Katkı Rehberi — Standart Geliştirme Akışı

Bu belge "bir değişiklik `main`'e nasıl girer" sorusunun **tek** cevabıdır.
Ne yapılacağının kuralları: [docs/process/DEVELOPMENT_PROCESS.md](docs/process/DEVELOPMENT_PROCESS.md).
Nasıl test edileceği: [docs/process/TEST_STANDARD.md](docs/process/TEST_STANDARD.md).

## 1. Ortam (her yerde aynı)

| Nerede | Nasıl |
|---|---|
| Yerel makine | `make setup` (Python 3.12; `uv` varsa onu, yoksa `venv+pip` kullanır) |
| VS Code / Codespaces | `.devcontainer/` ile aç → `make setup` otomatik çalışır |
| Claude Code bulut oturumu | `.claude/hooks/session-start.sh` oturum açılırken `make setup` eşdeğerini çalıştırır ve `.venv`'i PATH'e ekler |
| **Merge kapısı** (ADR-003) | `make gate` — commit'i temiz kopyada, sıfırdan ortamla `make check`'ten geçirir ve kanıt raporu üretir. GitHub Actions bu hesapta kullanılamıyor; `tests.yml` yalnız elle tetiklenir |

Kurulumun tek kaynağı `scripts/setup-dev.sh`, bağımlılıkların tek kaynağı
`requirements-test.txt` (sürümler sabit). `requirements.txt` yalnızca araştırma
ortamı içindir (PyJHora, kerykeion); CI ve test suite onlara ihtiyaç duymaz.

```bash
make help      # tüm hedefler
make check     # PR açmadan önce ZORUNLU: lint + lisans bekçisi + tüm testler
make gate      # MERGE öncesi ZORUNLU: PR head commit'ini temiz kopyada doğrula + rapor (SHA=<commit>)
make test      # hızlı döngü (oracle ızgarası hariç)
make verify    # yalnız oracle ızgarası
make mutation  # mutasyon kanıtı örneği
```

## 2. Dal modeli — tek gövde (ADR-002)

```
main ──●──────────●──────────●──────▶   (korumalı; yalnız PR ile, CI yeşilken)
        \        /  \        /
         spec/002-lagna     spec/003-sunrise      (kısa ömürlü, main'den açılır, merge sonrası silinir)
```

- **Tek kalıcı dal: `main`.** Başka uzun ömürlü dal yoktur.
- Dal adı: `spec/NNN-kisa-ad` (ör. `spec/002-lagna-precision`). Spec'e bağlı olmayan
  küçük işler: `chore/<ad>`, `docs/<ad>`, `fix/<ad>`. Ajan oturumlarının otomatik
  dal adları (ör. `claude/...`) da kabul edilir; kural **tabanın ve hedefin `main` olması**dır.
- **Her dal `main`'den açılır, PR'ı `main`'e açılır.** Başka bir özellik dalına
  PR açmak/merge etmek yasaktır (bu repo'da PR #3–#11 böyle dağıldı).
- Uzun süren dal `main`'in gerisinde kalırsa: `git merge origin/main` (rebase/force-push yok).

## 3. Bir turun PR akışı

1. `git switch main && git pull && git switch -c spec/NNN-ad`
2. Spec'i yaz: `docs/specs/SPEC-NNN-*.md` (şablon), `docs/specs/INDEX.md` durumunu güncelle.
3. Uygula + test et. Commit mesajı: `SPEC-NNN: <emir kipinde özet>` (gövdede kanıt satırları).
4. `make check` yeşil → push → **Draft PR** (`main`'e). Gövde `.github/pull_request_template.md` ile dolar.
5. DoD tamam → dal `main` ile güncel değilse `git merge origin/main` → push.
6. **Kapı:** `make gate SHA=<PR'ın son commit'i>` → rapor **GEÇTİ ✅** olmalı → raporu PR'a yorum olarak yapıştır → "Ready for review".
7. Sahip onayı → merge öncesi raporun SHA'sı PR'ın **şu anki** head SHA'sıyla aynı mı bak (sonradan push geldiyse kapıyı yeniden koş) → **Squash and merge** (başlık: `SPEC-NNN: ...`). Dal otomatik silinir.

Merge yöntemi: Spec PR'ları **squash** (bir spec = `main`'de bir commit). Geçmişi
korunması gereken konsolidasyon PR'ları (ör. PR #12) **merge commit** ile birleştirilir.

## 4. `main` koruması (repo ayarı — bir kerelik, Sahip yapar)

Ayrıntılı adımlar: [docs/process/REPO_SETTINGS.md](docs/process/REPO_SETTINGS.md).
Özet: ruleset `.github/rulesets/main-protection.json` içe aktarılır →
`main`'e doğrudan push, silme ve force-push kapanır; `main`'e yalnız PR ile girilir.
Test kapısı GitHub'da değil, §3 adım 6'da (`make gate`) uygulanır (ADR-003).

## 5. Yapılmayacaklar

- `main`'e doğrudan push · başka özellik dalına PR · force-push / rebase ile paylaşılmış geçmişi yeniden yazma
- `make gate` raporu GEÇTİ olmadan veya raporun SHA'sı head SHA'dan farklıyken merge etmek
- Testi atlamak/devre dışı bırakmak/toleransı sonuç geçsin diye gevşetmek
- Kanıtsız iddia (DEVELOPMENT_PROCESS §4)
- Üretim motorunda `swisseph` import'u (`make check` lisans bekçisi kırar)
