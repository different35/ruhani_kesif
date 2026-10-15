# GitHub Repo Ayarları — bir kerelik kurulum (Sahip)

Bu ayarlar dosyayla repo'ya yazılamaz; GitHub arayüzünden **repo sahibi** yapar.

## 1. GitHub Actions durumu (bilgi)

Hesap faturalama nedeniyle kilitli; Actions job'ları başlamıyor ve bu durum **kalıcı** kabul ediliyor
([ADR-003](../adr/ADR-003-local-ci-gate.md)). Merge kapısı yerel: `make gate`.
Bu yüzden:
- `tests.yml` yalnız elle tetiklenir; push/PR'larda kırmızı ✗ oluşmaz.
- Actions → `tests` → **Disable workflow** demek isteğe bağlıdır. Elle çalıştırma da kilitliyken başlamaz.

## 2. Pull Request ayarları

**Settings → General → Pull Requests**
- ✅ Allow merge commits (konsolidasyon PR'ları için)
- ✅ Allow squash merging → Default message: **Pull request title**
- ⬜ Allow rebase merging (kapalı)
- ✅ **Automatically delete head branches**: merge sonrası dal kendiliğinden silinir, dal birikmesi bir daha olmaz. Actions gerektirmez.

## 3. `main` koruma kuralı (ruleset)

**Settings → Rules → Rulesets → New ruleset → Import a ruleset** →
`.github/rulesets/main-protection.json` → **Create**.

| Kural | Etki |
|---|---|
| `deletion`, `non_fast_forward` | `main` silinemez, force-push yapılamaz |
| `pull_request` | `main`'e yalnız PR ile girilir; açık review thread'leri çözülmeden merge yok; yöntem: merge veya squash |
| bypass: Repository admin (yalnız PR üzerinden) | Acil durumda sahip PR'ı kurala takılmadan birleştirebilir; doğrudan push yine kapalı |

Zorunlu durum kontrolü (`pytest`) **bilerek yok**: Actions kilitliyken her PR'ı kalıcı olarak bloke ederdi.
Kapı PR akışında uygulanır ([CONTRIBUTING §3](../../CONTRIBUTING.md)).
Ruleset'lerin bu kilitli hesapta içe aktarılıp aktarılamadığı **doğrulanmadı**. Aktarılamazsa §2 tek başına yeterli asgari düzeni sağlar.

## 4. Eski dalların silinmesi (elle)

PR #12 merge edildi; aşağıdaki dalların **tamamı** `main` geçmişinde (doğrulandı: `git merge-base --is-ancestor`, 8/8).
Silmek veri kaybettirmez. `revert-10`'un commit'i (`005602e`) uygulanmadan geçmişte durur, gerekirse `git cherry-pick 005602e`.

github.com/different35/ruhani_kesif/branches → her birinin yanındaki çöp kutusu:
- `gist-roadmap-target-23a07`
- `roadmap-backlog-clarification-ce8a0`
- `main-branch-roadmap-status-report-157da`
- `vimshottari-dasha-bug-fix-af94a`
- `vedic-astrology-coding-scope-89b3a`
- `revert-10-vedic-astrology-coding-scope-89b3a`
- `claude/elegant-lovelace-hysdf5` (merge edilmiş PR'ların dalı)

Sonuç: Branches sayfasında yalnız `main` ve açık PR'ların dalları kalmalı.

## 5. Actions bir gün kullanılabilir olursa

1. `tests.yml` → `on:` altına `push: {branches: [main]}` ve `pull_request:` geri ekle.
2. Ruleset'e `required_status_checks` kuralını ekle (context: `pytest`, integration: GitHub Actions).
3. ADR-003'ü "Superseded" olarak işaretle; `make gate` yerel ön kontrol olarak kalır.

## 6. Kontrol listesi

- [ ] §2 PR ayarları, "Automatically delete head branches" açık
- [ ] §3 ruleset içe aktarıldı (veya aktarılamadığı not edildi)
- [ ] §4 eski dallar silindi
