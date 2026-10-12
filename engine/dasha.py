"""Vimshottari Dasha — gist BÖLÜM 3: 'aboneliğin ve retention'ın gerçek omurgası'.

Yönerge (PyJHora davranışıyla birebir): başlangıç noktası Ay'ın nakshatra padası.
MD sırası: Ketu->Venus->Sun->Moon->Mars->Rahu->Jupiter->Saturn->Mercury
Yıllar:     7,7,6,10,7,12,16,19,20  (toplam 120)
Balanca: doğum anında geçmiş dasha süresi düşülür (pada oranına göre).
"""
from __future__ import annotations

from engine.nakshatra import NAKSHATRAS, PADAS_PER_NAK, SPAN_DEG

LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
         "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
# düzeltme: standart Vimshottari: Ketu7 Venus20 Sun6 Moon10 Mars7 Rahu18 Jup16 Sat19 Merc17 = 120
assert sum(YEARS.values()) == 120

ANTARDASHA_ORDER = {
    "Ketu":   ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"],
    "Venus":  ["Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury","Ketu"],
    "Sun":    ["Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury","Ketu","Venus"],
    "Moon":   ["Moon","Mars","Rahu","Jupiter","Saturn","Mercury","Ketu","Venus","Sun"],
    "Mars":   ["Mars","Rahu","Jupiter","Saturn","Mercury","Ketu","Venus","Sun","Moon"],
    "Rahu":   ["Rahu","Jupiter","Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars"],
    "Jupiter":["Jupiter","Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu"],
    "Saturn": ["Saturn","Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter"],
    "Mercury":["Mercury","Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn"],
}


def balance_years(moon_sidereal_lon: float, years_per_dasha: float) -> float:
    """Ay'ın içinde bulunduğu nakshatranın tamamlanmamış fraction'ı kalan süreyi verir."""
    span = 360.0 / len(NAKSHATRAS)
    idx = int((moon_sidereal_lon % 360.0) / span)
    within = (moon_sidereal_lon % 360.0) - idx * span
    frac_elapsed = within / span            # 0..1 geçilen kısım
    lord_start = idx % 9                    # nakshatra lordu (Ashwini=Ketu ...)
    full = YEARS[LORDS[lord_start]]
    return full * (1.0 - frac_elapsed), LORDS[lord_start]


def vimshottari(moon_sidereal_lon: float, birth_jd_ut: float) -> list[dict]:
    """Doğumdan 120 yıl sonrasına MD+AD takvimi (julian day UT cinsinden)."""
    import swisseph as swe
    rem_years, start_lord = balance_years(moon_sidereal_lon, None)
    lord_i = LORDS.index(start_lord)
    md_list = []
    # Tam döngü: balancalı ilk MD'dan sonra 120 yılı tamamlamak için 10 MD gerekir
    # (son MD'ın balance'a kadar olan kısmı kesilir).
    seq = [LORDS[(lord_i + k) % 9] for k in range(10)]
    durations = [rem_years] + [YEARS[s] for s in seq[1:]]
    cursor = birth_jd_ut
    for lord, yrs in zip(seq, durations):
        start, end = cursor, cursor + yrs * 365.2425
        sub_seq = ANTARDASHA_ORDER[lord]
        sub_cursor = start
        for sub in sub_seq:
            sub_yrs = yrs * YEARS[sub] / 120.0
            md_list.append({"mahadasha": lord, "antardasha": sub,
                            "start_utc": swe.revjul(sub_cursor, 1)[:3],
                            "end_utc": swe.revjul(min(sub_cursor + sub_yrs*365.2425, end), 1)[:3],
                            "years": round(sub_yrs, 3)})
            sub_cursor += sub_yrs * 365.2425
        cursor = end
    return md_list
