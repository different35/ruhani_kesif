## Spec
SPEC-NNN — <başlık> (`docs/specs/SPEC-NNN-*.md`)

## Özet
<!-- Ne değişti, neden. Kök neden kanıtına link (spec §3). -->

## Kabul kriterleri
| AC | Kriter | Test | Durum |
|---|---|---|---|
| AC-1 | | | ✅ / ❌ |

## Kanıt
```
$ make check
<özet satırı>
```

### Merge kapısı (ADR-003) — merge'den hemen önce, PR'ın son commit'inde
<!-- `make gate SHA=<head>` çıktısındaki tabloyu buraya veya PR yorumuna yapıştırın.
     Rapordaki Commit = PR'ın şu anki head SHA'sı olmalı; sonradan push geldiyse yeniden koşun. -->

### Mutasyon
```
$ <kasıtlı bug komutu>
$ python -m pytest -q
<N failed …>
```

## DoD kontrol listesi
- [ ] Tüm AC'ler kanıtlı
- [ ] Suite tamamen yeşil
- [ ] `make gate` raporu GEÇTİ ✅ ve SHA = head SHA
- [ ] Mutasyon kanıtı eklendi
- [ ] `VERIFICATION.md` güncellendi (yanlış çıkan eski iddialar "DÜZELTİLDİ" notuyla)
- [ ] `BACKLOG.md` ve `docs/specs/INDEX.md` güncellendi
- [ ] Docstring'lerde spec ile çelişen iddia yok
- [ ] Kapsam dışı bulgular kuyruğa yazıldı

## Devir notu
```
DEVİR NOTU — SPEC-NNN
Kapanan:
Kanıt:
Açık bulgular:
Sonraki tur önerisi:
Doğrulanmamış iddialar:
```
