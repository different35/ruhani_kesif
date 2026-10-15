# Ajanlar için çalışma kuralları (ruhani_kesif)

Bu repo'da çalışan her ajan oturumu için bağlayıcıdır. Ayrıntılar bağlantılı belgelerde.

## Her oturumun başında
1. `docs/process/DEVELOPMENT_PROCESS.md` ve `docs/process/TEST_STANDARD.md`'yi oku.
2. Sıradaki işi `docs/specs/INDEX.md`'den al (onaylı sıra: SPEC-002 → SPEC-011).
3. Ortam hazır değilse: `make setup` (bulut oturumunda SessionStart hook bunu yapar).

## Dal / PR
- Taban ve hedef **daima `main`** (ADR-002). Başka bir özellik dalına PR açma veya merge etme.
- Bir tur = bir spec = bir PR. Kapsam dışı bulgu → spec'in "kapsam dışı" bölümüne / INDEX kuyruğuna.
- PR açmadan önce `make check` yeşil olmalı; PR gövdesi `.github/pull_request_template.md`.

## Kanıt
- "X şöyle çalışır" diyen her cümle (kütüphane davranışı, kök neden) çalıştırılmış komut çıktısıyla desteklenir.
- Önceki turun teşhisini kabul etmeden önce yeniden ölç (G0/G1). SPEC-001'de önceki teşhisin yarısı yanlıştı.
- Commit'lenen her test en az bir kez koşmuş olmalı; uydurma API kullanma.
- Her yeni/değişen test için mutasyon kanıtı (TEST_STANDARD §7).

## Teknik sözleşmeler (ADR-001)
- Port'a verilen float JD = **JD(UT1)** → Skyfield'da `ts.ut1_jd`. `ts.tt_jd` yalnız gerçek TT sayılarıyla.
- datetime = UTC (naive → UTC). Tropik boylam: geometrik, true ecliptic & equinox of date.
- Üretim motoru yalnız Skyfield; `swisseph`/`PyJHora` yalnız test oracle'ı.

## Komutlar
`make check` (CI ile birebir) · `make test` · `make verify` · `make mutation` · `make help`
