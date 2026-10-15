# ruhani_kesif
ruhani yolculuğunuza rehberlik.

## Dokümanlar
- **[PRODUCT.md](PRODUCT.md)** — Kapsam → Ürünleştirme → Planlama: ürün kalemlerinin izahı, MVP'nin 6 SKU tanımı, paketleme/fiyat, Definition of Done. **Önce bu okunur.**
- **[ROADMAP.md](ROADMAP.md)** — Fazlar (P0–P6) ve çıkış ölçütleri; PRODUCT.md §5 ile çapraz referanslı.
- **[docs/](docs/README.md)** — Mühendislik süreci: tur yaşam döngüsü, test standardı, spec kaydı ve kuyruğu, ADR'ler.
- **[VERIFICATION.md](VERIFICATION.md)** — Kanıt kaydı (komut + ham çıktı). **[BACKLOG.md](BACKLOG.md)** — iş durumu.

## Geliştirme
```
make setup   # ortam (Python 3.12 .venv)
make check   # lint + lisans bekçisi + tüm testler
make gate    # merge kapısı: commit'i temiz kopyada doğrula + kanıt raporu (ADR-003)
```
Akış ve dal modeli: **[CONTRIBUTING.md](CONTRIBUTING.md)**.

Kaynak strateji raporu: https://gist.github.com/different35/2e26066e6a025e3228568ef8648428e8
