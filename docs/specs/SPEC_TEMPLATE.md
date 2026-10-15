# SPEC-NNN — <Kısa başlık>

| Alan | Değer |
|---|---|
| Durum | Draft · Approved · In progress · Done · Superseded |
| Tür | Yeni modül · Hata düzeltmesi · Entegrasyon · Altyapı |
| Modül(ler) | `engine/<dosya>.py` |
| Bağımlılık | SPEC-xxx (Done olmalı) |
| Oracle | pyswisseph x.y / PyJHora x.y / kaynak kitap (bölüm, şloka) |
| Dal / PR | `<dal>` / <PR linki> |
| Tarih | YYYY-MM-DD |

## 1. Amaç (tek cümle, ölçülebilir)

> Örn: "`longitude()` 1901–2031 aralığında 7 cisimde swiss TRUEPOS oracle'ına ≤2″ (Ay ≤5″) uyar."

## 2. Bağlam

Neden şimdi? Hangi üst hedefe (BACKLOG/ROADMAP maddesi) hizmet ediyor? Önceki turun devir notundan alıntı.

## 3. Keşif / kök neden kanıtı (hata düzeltmelerinde zorunlu)

| Hipotez | Deney (yalnız bu değişken) | Komut | Ham sonuç | Karar |
|---|---|---|---|---|
| H1 | | | | Doğrulandı / Reddedildi |

## 4. Veri sözleşmesi

| Öğe | Tip | Birim | Zaman ölçeği / çerçeve | Aralık | Hata davranışı |
|---|---|---|---|---|---|
| Girdi … | | | | | |
| Çıktı … | | | | | |

Kural tabanlı modüllerde ek olarak: kural tablosu (koşul → sonuç), kaynak referansı her satırda.

## 5. Tasarım

- Fonksiyon imzaları (public API).
- Algoritma / formül (kaynaklı).
- Mevcut modüllerle etkileşim (port, facts ağacı).
- Değerlendirilen ve reddedilen alternatifler (kısa).

## 6. Kabul kriterleri

| AC | Kriter (sayısal) | Doğrulama yöntemi (test adı) | Durum |
|---|---|---|---|
| AC-1 | | | ⬜ |

## 7. Test planı

- **Sözleşme hizalama tablosu** (TEST_STANDARD §4).
- L1/L2/L3/L4/L6 testleri ve parametre ızgarası.
- Sınır vakaları.
- Mutasyon planı: hangi satır bozulacak, hangi testlerin kırılması beklenir.

## 8. Kapsam dışı

- Açıkça yapılmayacaklar ve nedeni.

## 9. Riskler / açık sorular

| Risk | Etki | Önlem / karar sahibi |
|---|---|---|

## 10. Kanıt kaydı (tur sonunda doldurulur)

```
$ python -m pytest -q
<özet satırı>
$ <mutasyon komutu>
<özet satırı>
```

## 11. Devir notu

```
DEVİR NOTU — SPEC-NNN
Kapanan:
Kanıt:
Açık bulgular:
Sonraki tur önerisi:
Doğrulanmamış iddialar:
```
