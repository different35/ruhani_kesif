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
$ python -m pytest -q
<özet satırı>
```

### Mutasyon
```
$ <kasıtlı bug komutu>
$ python -m pytest -q
<N failed …>
```

## DoD kontrol listesi
- [ ] Tüm AC'ler kanıtlı
- [ ] Suite tamamen yeşil
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
