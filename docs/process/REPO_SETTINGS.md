# GitHub Repo Ayarları — bir kerelik kurulum (Sahip)

Bu ayarlar dosyayla repo'ya yazılamaz; GitHub arayüzünden **repo sahibi** yapar.
Sıra önemlidir: önce Actions çalışmalı, sonra `pytest` check'i zorunlu kılınmalı.

## 1. GitHub Actions'ın çalıştığını doğrula (ÖNCE BU)

Gözlem (2026-10-15, PR #12): `tests / pytest` job'ı **runner atanmadan** 2 sn'de
`failure` oldu (`runner_id: 0`, adım yok, log yok). Repo **public**, dolayısıyla
dakika kotası sebep değildir. Olası sebepler:

1. **Settings → Actions → General → Actions permissions**: "Allow all actions and reusable workflows" seçili olmalı.
2. **Hesap (github.com/settings/billing)**: Hesap faturalama nedeniyle kilitliyse
   Actions public repo'larda da çalışmaz — sayfada uyarı bandı görünür.
3. **Settings → Actions → General → Workflow permissions**: "Read and write permissions"
   (yalnız `branch-cleanup` workflow'u için gerekli; `tests` salt-okur çalışır).

Doğrulama: Actions → `tests` → **Run workflow** (`main` veya PR dalı) → job'da adımların göründüğünü ve yeşil bittiğini gör.

## 2. Pull Request ayarları

**Settings → General → Pull Requests**
- ✅ Allow merge commits (konsolidasyon PR'ları için)
- ✅ Allow squash merging → Default message: **Pull request title**
- ⬜ Allow rebase merging (kapalı)
- ✅ **Automatically delete head branches** — merge sonrası dal kendiliğinden silinir; dal birikmesi bir daha olmaz.

## 3. `main` koruma kuralı (ruleset)

**Settings → Rules → Rulesets → New ruleset → Import a ruleset** →
`.github/rulesets/main-protection.json` dosyasını seç → **Create**.

Getirdikleri:
| Kural | Etki |
|---|---|
| `deletion`, `non_fast_forward` | `main` silinemez, force-push yapılamaz |
| `pull_request` | `main`'e yalnız PR ile girilir; açık review thread'leri çözülmeden merge yok; yöntem: merge veya squash |
| `required_status_checks: pytest` (GitHub Actions) | CI yeşil değilse merge yok; dal `main`'e göre güncel olmalı |
| bypass: Repository admin (yalnız PR üzerinden) | Actions kesintisinde sahip, PR'ı kontrol olmadan birleştirebilir — doğrudan push yine kapalı |

Onay sayısı 0'dır: tek geliştiricili repo'da kendi PR'ını onaylayamazsın. İkinci
bir gözden geçiren eklendiğinde 1'e çıkarılmalı.

## 4. Eski dalların silinmesi

PR #12 (`main`'e merge commit ile) birleştikten sonra aşağıdaki dalların **tamamı**
`main` geçmişinde bulunur (konsolidasyon commit'i bunları ebeveyn olarak bağlar;
`revert-10`'un içeriği uygulanmadan geçmişte saklanır). Silmek veri kaybettirmez.

| Dal | Uç | Neden güvenli |
|---|---|---|
| `gist-roadmap-target-23a07` | cf89ac1 | main geçmişinde |
| `roadmap-backlog-clarification-ce8a0` | 841b51d | main geçmişinde |
| `main-branch-roadmap-status-report-157da` | 1fa7941 | main geçmişinde |
| `vimshottari-dasha-bug-fix-af94a` | 49cd9b7 | main geçmişinde |
| `vedic-astrology-coding-scope-89b3a` | 775fdd1 | main geçmişinde |
| `revert-10-vedic-astrology-coding-scope-89b3a` | 005602e | main geçmişinde (uygulanmamış; `git cherry-pick 005602e` ile geri getirilebilir) |
| `claude/elegant-lovelace-hysdf5` | PR #12 başı | merge sonrası |

İki yol:
- **Otomatik:** Actions → `branch-cleanup` → Run workflow (`dry_run: true` ile önce listele, sonra `false`). Workflow yalnız `main`'e tamamen dahil olan dalları siler.
- **Elle:** github.com/different35/ruhani_kesif/branches → her dalın yanındaki çöp kutusu.

## 5. Kontrol listesi

- [ ] Actions bir job'ı gerçekten çalıştırdı (adımlar görünür, yeşil)
- [ ] PR #12'de `pytest` yeşil → merge commit ile birleştirildi
- [ ] PR ayarları (§2) yapıldı, "Automatically delete head branches" açık
- [ ] Ruleset içe aktarıldı (§3)
- [ ] Eski dallar silindi (§4) → Branches sayfasında yalnız `main` kaldı
