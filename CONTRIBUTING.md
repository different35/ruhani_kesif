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
| CI (GitHub Actions) | `.github/workflows/tests.yml` → `make check` |

Kurulumun tek kaynağı `scripts/setup-dev.sh`, bağımlılıkların tek kaynağı
`requirements-test.txt` (sürümler sabit). `requirements.txt` yalnızca araştırma
ortamı içindir (PyJHora, kerykeion); CI ve test suite onlara ihtiyaç duymaz.

```bash
make help      # tüm hedefler
make check     # PR açmadan önce ZORUNLU: lint + lisans bekçisi + tüm testler (CI ile birebir)
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
5. CI (`pytest` check'i) yeşil + DoD tamam → "Ready for review".
6. Sahip onayı → **Squash and merge** (başlık: `SPEC-NNN: ...`). Dal otomatik silinir.

Merge yöntemi: Spec PR'ları **squash** (bir spec = `main`'de bir commit). Geçmişi
korunması gereken konsolidasyon PR'ları (ör. PR #12) **merge commit** ile birleştirilir.

## 4. `main` koruması (repo ayarı — bir kerelik, Sahip yapar)

Ayrıntılı adımlar: [docs/process/REPO_SETTINGS.md](docs/process/REPO_SETTINGS.md).
Özet: ruleset `.github/rulesets/main-protection.json` içe aktarılır →
`main`'e doğrudan push, silme ve force-push kapanır; PR + `pytest` check'i zorunlu olur.

## 5. Yapılmayacaklar

- `main`'e doğrudan push · başka özellik dalına PR · force-push / rebase ile paylaşılmış geçmişi yeniden yazma
- Testi atlamak/devre dışı bırakmak/toleransı sonuç geçsin diye gevşetmek
- Kanıtsız iddia (DEVELOPMENT_PROCESS §4)
- Üretim motorunda `swisseph` import'u (CI bekçisi kırar)
