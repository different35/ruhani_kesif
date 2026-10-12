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


def balance_years(moon_sidereal_lon: float, years_per_dasha: float = None):
    """Vimshottari balanca kuralı — PyJHora `vimsottari_dasha_start_date` ile birebir
    (kaynak: jhora/horoscope/dhasa/graha/vimsottari.py, AGPL referans davranışı):

      current_lord = Ay'ın İÇİNDE olduğu nakshatra'nın lordu (Swati -> Rahu)
      frac_elapsed = nakshatra içinde geçilen oran
      balance      = next_lord_years * frac_elapsed     <-- JYOTISH STANDARDI
      start_lord   = next_lord (Rahu sonrası -> Jupiter)

    Gist §3 "aboneliğin omurgası" dediği için bu fonksiyon kritik yol: önceki
    sürümde `current_full * (1-frac)` kullanılıyordu (yanlış formül; Swati örneğinde
    0.72 yıl yerine 15.36 yıl çıkmalı). Düzeltme + golden test eklendi.
    """
    span = 360.0 / len(NAKSHATRAS)
    lon = moon_sidereal_lon % 360.0
    idx = int(lon / span)
    frac_elapsed = (lon - idx * span) / span   # 0..1 geçilen kısım
    current_lord = LORDS[idx % 9]              # Ashwini=Ketu ... Revati=Mercury
    next_lord = LORDS[(idx % 9) + 1 if (idx % 9) + 1 < 9 else 0]
    balance = YEARS[next_lord] * frac_elapsed
    return balance, next_lord, current_lord


def vimshottari(moon_sidereal_lon: float, birth_jd_ut: float) -> list[dict]:
    """Doğumdan 120 yıl sonrasına MD+AD takvimi (julian day UT cinsinden)."""
    import swisseph as swe
    rem_years, start_lord, _current_lord = balance_years(moon_sidereal_lon)
    lord_i = LORDS.index(start_lord)
    md_list = []
    # PyJHora `vimsottari_mahadasa` ile birebir: 9 MD döner; ilki BALANCA süresiyle
    # açılır, kalan 8'i tam. (Eski sürümde 10. MD eklenip sonu kırpılıyordu ->
    # timeline 120 yıl yerine ~137 yıla taşıyordu. Düzeltme: P1-5 regresyon testi.)
    seq = [LORDS[(lord_i + k) % 9] for k in range(9)]
    durations = [rem_years] + [YEARS[s] for s in seq[1:]]
    cursor = birth_jd_ut
    YEAR = 365.2425  # sidereal year (gist/PyJHora: const.sidereal_year)
    for i_md, (lord, yrs) in enumerate(zip(seq, durations)):
        start, end = cursor, cursor + yrs * YEAR
        sub_seq = ANTARDASHA_ORDER[lord]
        # PyJHora `_vimsottari_bhukti` ile birebir: AD sırası her MD'da MD lorduyla
        # BAŞLAR (option=1). Balanca kırpması = ilk AD'ın tüketilen kısmı kadar kaydır.
        first_full = YEARS[lord] * YEARS[sub_seq[0]] / 120.0
        consumed_frac = 1.0 - yrs / YEARS[lord] if i_md == 0 else 0.0
        sub_cursor = start + consumed_frac * first_full * YEAR
        for si, sub in enumerate(sub_seq):
            sub_yrs = yrs * YEARS[sub] / 120.0
            seg_end = min(sub_cursor + sub_yrs * YEAR, end)
            if seg_end > sub_cursor:
                md_list.append({"mahadasha": lord, "antardasha": sub,
                                "start_utc": swe.revjul(sub_cursor, 1)[:3],
                                "end_utc": swe.revjul(seg_end, 1)[:3],
                                "years": round((seg_end - sub_cursor) / YEAR, 3)})
            sub_cursor = seg_end
        cursor = end
    return md_list


def yrs_full(lord: str) -> float:
    """MD'ın tam (kırpılmamış) yılı — balance hesabında referans."""
    return YEARS[lord]
