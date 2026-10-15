# ADR-002 — Tek gövde (trunk) dal politikası

| Alan | Değer |
|---|---|
| Durum | **Accepted** (Sahip onayı: 2026-10-15) |
| Tarih | 2026-10-15 |
| İlgili spec | — (süreç) |
| Karar sahibi | proje sahibi |

## Bağlam (2026-10-15 itibarıyla ölçülen durum)

- `main` @ `5b531a7` — PR #2'den sonra hiç ilerlememiş.
- PR #3–#11 `main`'e değil, birbirine zincirleme merge edilmiş:
  `gist-roadmap-target-23a07` ← `roadmap-backlog-clarification-ce8a0` ←
  `main-branch-roadmap-status-report-157da` / `vimshottari-dasha-bug-fix-af94a` ←
  `vedic-astrology-coding-scope-89b3a`.
- En güncel kod `vimshottari-dasha-bug-fix-af94a` @ `49cd9b7` (=
  `vedic-astrology-coding-scope-89b3a` ağacıyla özdeş). `main` ile farkı 14 dosya,
  ~2000 satır (skyfield adapter, varga, calendar, VERIFICATION, 32 MB `de440s.bsp`).
- Ayrıca merge edilmemiş `revert-10-vedic-astrology-coding-scope-89b3a` dalı var
  (PR #10'u geri alır: "swisseph bağımlılığını üretimden çıkar" değişikliği).
- Sonuç: "Projenin güncel hali nedir?" sorusunun cevabı hangi dala bakıldığına göre değişiyor.

## Karar

1. **`main` tek gövdedir.** Tüm tur PR'ları `main`'i hedefler.
2. Konsolidasyon: SPEC-001 PR'ı (`vimshottari-dasha-bug-fix-af94a` tabanlı)
   onaylandıktan sonra `main`'e merge edilir → `main` en güncel kodu içerir.
3. `revert-10-…` dalının commit'i (PR #10'un geri alınması) ADR-001 ve TEST_STANDARD §1
   ile çeliştiği için **uygulanmaz**; ancak veri kaybı olmasın diye konsolidasyon
   commit'ine `-s ours` ebeveyni olarak bağlanır (geçmişte durur, ağaca girmez).
4. Konsolidasyon yöntemi: tüm yan dal uçları tek bir `git merge -s ours` commit'iyle
   gövde geçmişine bağlanır (ağaç değişmez — doğrulandı). Böylece 8 dalın her biri
   `main`'in atası olur ve silinmeleri hiçbir commit'i kaybettirmez. (Arşiv etiketi
   denendi; oturum proxy'si etiket push'una izin vermedi.)
5. `main` koruması `.github/rulesets/main-protection.json` ile; merge sonrası dal
   otomatik silme açık; eski dallar elle silinir (`branch-cleanup` workflow'u Actions
   kilidi nedeniyle kaldırıldı — ADR-003).
   Kurulum adımları: [REPO_SETTINGS.md](../process/REPO_SETTINGS.md). Akış: [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Sonuçlar
- Olumlu: Tek gerçeklik kaynağı; CI'ın anlamlı olması.
- Maliyet: Tek seferlik konsolidasyon merge'ü (çakışma beklenmiyor — `main`
  zincirin atasıdır, fast-forward'a yakın).

## Değerlendirilen alternatifler
| Alternatif | Neden reddedildi |
|---|---|
| Zincirleme yan dallarla devam | Her turda "taban hangisi" belirsizliği; ajanlar yanlış dalda çalışıyor |
| `develop` + `main` (git-flow) | Tek geliştirici/ajan akışı için gereksiz tören |
