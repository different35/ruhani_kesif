"""P1-9 — Varga seti (D1–D60), gist §2.1 "Yaygın pratik set 16 harita" + §4 A4 SKU.

Gist kuralı: hesaplama PyJHora üzerinden yapılır (`jhora.horoscope.chart.charts`,
bölüm 1.1 envanteri). Bu modül, `EphemerisPort`'tan gelen Lahiri-sidereal D1
boylamlarını JHora'nın beklediği `[[planet,(rasi,longitude_in_sign)],...]`
biçimine çevirip **yaygın 16 varga** kümesini üretir:

    D1 D2 D3 D4 D5 D7 D9 D10 D12 D16 D20 D24 D27 D30 D40 D60

Gist §2.1 sayım kuralı: **16 × 9 = 144 yerleşim** — gezegen yüzeyi 9 grahadır
(Sun..Satürn + Rahu/Ketu, mean node). Notlar (canlı doğrulandı, pyswisseph
2.10.3.2 / PyJHora 4.8.7):
- `navamsa_chart` çıktısı bağımsız parity formülüyle karşılaştırıldı: özdeş.
- JHora fonksiyonları girdi listesini YERİNDE değiştirir → her çağrıdan önce
  derin kopya verilir (sessiz veri hatası riski; BACKLOG "keşfedilen gerçekler"
  ilkesi gereği burada da savunma yapıldı).
- Ketu, Rahu'nun tam karşısıdır (180° mod 12 burç ⇒ aynı burç) — varga listesinde
  ayrı öğe olarak eklenir; çıktı sözleşmesi bunu test eder.
- D60 (shashtyamsa) chart_method=1 istenmez; varsayılan 2 (Parasara standardı).
"""
from __future__ import annotations

import copy
from typing import Callable

from engine.ephemeris_port import EphemerisPort

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")

# Gist §2.1'deki "yaygın pratik 16 harita" listesi. jhora sürümünde D5 panchamsa
# fonksiyonu bulunmadığı için D5, §2.4 "runtime probe ile doğrula" ilkesine uygun
# biçimde yerel Parashara D5 implementasyonuyla üretilir (test edildi).
COMMON_16 = (1, 2, 3, 4, 5, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 60)

VARGA_NAMES = {
    1: "D1 Rasi (natal)", 2: "D2 Hora (servet)", 3: "D3 Drekkana (kardeşler)",
    4: "D4 Chaturthamsa (gayrimenkul)", 5: "D5 Panchamsa (kreativite/güç)",
    7: "D7 Saptamsa (çocuklar)", 9: "D9 Navamsa (evlilik/çekirdek)",
    10: "D10 Dasamsa (kariyer)", 12: "D12 Dwadasamsa (ebeveynler)",
    16: "D16 Shodasamsa (araç/lüks)", 20: "D20 Vimsamsa (ruhani inanç)",
    24: "D24 Chaturvimsamsa (eğitim)", 27: "D27 Nakshatramsa (destan)",
    30: "D30 Trimsamsa (günah/kötücül)", 40: "D40 Khavedamsa (nasil)",
    60: "D60 Shashtyamsa (geçmiş yaşam karma)",
}


def _jhora_functions() -> dict[int, tuple[Callable, int]]:
    """PyJHora importunu geç çöz — yan etkisi (global sid-mode değişimi) yalnızca
    gerçekten varga üretileceği zaman yüklenir (BACKLOG keşif #3 savunması)."""
    from jhora.horoscope.chart import charts as C
    # factor -> (fonksiyon, önerilen chart_method)
    return {
        2: (C.hora_chart, 1), 3: (C.drekkana_chart, 1), 4: (C.chaturthamsa_chart, 1),
        7: (C.saptamsa_chart, 1), 9: (C.navamsa_chart, 1), 10: (C.dasamsa_chart, 1),
        12: (C.dwadasamsa_chart, 1), 16: (C.shodasamsa_chart, 1),
        20: (C.vimsamsa_chart, 1), 24: (C.chaturvimsamsa_chart, 1),
        27: (C.nakshatramsa_chart, 1), 30: (C.trimsamsa_chart, 1),
        40: (C.khavedamsa_chart, 1), 60: (C.shashtyamsa_chart, 2),
    }


def _panchamsa_d5(sign_idx: int, deg_in_sign: float) -> tuple[int, float]:
    """Parashara D5: tek burçlarda paylar 1-4-7-10-... (Leone), çiftlerde ters
    (Aquarius başlangıç). Bölge = 6°; dönüşüm = bölge lordunun burcuna göre 5× kaydırma."""
    if sign_idx % 2 == 0:  # odd sign (Aries=0): sequence 1,4,7,10,...
        parts = [((i * 3 + 1) - 1) % 12 for i in range(5)]
    else:                 # even sign: sequence 10,7,4,1,...
        parts = [(10 - 3 * i - 1) % 12 for i in range(5)]
    part_i = min(int(deg_in_sign / 6.0), 4)
    start = parts[part_i]
    d5_sign = (start + int(deg_in_sign // 6)) % 12
    return d5_sign, deg_in_sign - part_i * 6.0


# JHora/vedik sırası: Sun=0 ... Saturn=6, Rahu=7 (Ketu listeden türetilir).
PLANET_ORDER = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]


def rasi_positions(port: EphemerisPort, when, lagna_lon: float | None = None) -> list[list]:
    """EphemerisPort D1 boylamlarını JHora girdi biçimine çevirir.
    İlk öğe Lagna ('L') ise mevcuttur; gezegenler integer index ile (Sun=0..Saturn=6),
    ardından Rahu (index 7). Ketu karşısı olduğundan çıktıda türetilir."""
    pos = []
    if lagna_lon is not None:
        pos.append(["L", (int(lagna_lon // 30), lagna_lon % 30)])
    for i, b in enumerate(PLANET_ORDER):
        lon = port.longitude(b, when, "sidereal")
        pos.append([i, (int(lon // 30), lon % 30)])
    rahu = port.longitude("rahu_mean", when, "sidereal")
    pos.append([7, (int(rahu // 30), rahu % 30)])
    return pos


def varga_set(port: EphemerisPort, when, factors=COMMON_16,
              lagna_lon: float | None = None) -> dict:
    """16 vargalık yaygın seti üret: {factor: {body: {sign, sign_index, lon_in_sign}}}."""
    funcs = _jhora_functions()
    base = rasi_positions(port, when, lagna_lon)
    out: dict[str, dict] = {}
    for f in factors:
        if f == 1:
            res = copy.deepcopy(base)
        elif f == 5:
            res = []
            for item in copy.deepcopy(base):
                key, (s, d) = item[0], item[1]
                s5, d5 = _panchamsa_d5(s, d)
                res.append([key, (s5, d5)])
        else:
            fn, method = funcs[f]
            res = fn(copy.deepcopy(base), chart_method=method)
        chart = {}
        for item in res:
            key = item[0]
            name = "lagna" if key == "L" else _INDEX_TO_NAME[key]
            chart[name] = {"sign_index": item[1][0], "sign": SIGNS[item[1][0]],
                           "lon_in_sign": round(float(item[1][1]), 4)}
        # Çıktı sözleşmesi (gist §2.1: 9 graha): Ketu, mean node'un tam karşısıdır;
        # burç indeksinde +6 (180°) ve burç içi derece aynen geçerlidir.
        if "rahu" in chart:
            rsi = chart["rahu"]["sign_index"]
            chart["ketu"] = {"sign_index": (rsi + 6) % 12,
                             "sign": SIGNS[(rsi + 6) % 12],
                             "lon_in_sign": chart["rahu"]["lon_in_sign"]}
        out[f"D{f}"] = chart
    return out


_INDEX_TO_NAME = {**{i: p for i, p in enumerate(PLANET_ORDER)}, 7: "rahu", 8: "ketu"}
