"""Vimshottari Dasha — gist BÖLÜM 3: 'aboneliğin ve retention'ın gerçek omurgası'.

Standart Vimshottari kuralı (PyJHora `vimsottari_dasha_start_date` ile aynı):
MD sırası: Ketu->Venus->Sun->Moon->Mars->Rahu->Jupiter->Saturn->Mercury
Yıllar:    7,20,6,10,7,18,16,19,17  (toplam 120; tek doğru kaynak YEARS dict'i)
Balanca:   doğum anında Ay'ın İÇİNDE OLDUĞU nakshatra lordunun dasha'sı akar;
           kalan süre = YEARS[current_lord] * (1 - frac_elapsed).
Doğumdan önceki (tüketilen) kısım takvime girmez; timeline bu yüzden tam
döngüde 120 yıl DEĞİL, 120 − tüketilen kısım yıldır (9 MD: balance + 8 tam MD).
"""
from __future__ import annotations

import swisseph as swe

from engine.nakshatra import NAKSHATRAS, nakshatra_pada

# TEK KAYNAK: tüm katmanlar (facts.py dahil) yılı buradan import eder.
# PyJHora `const.sidereal_year` = 365.256364 (canlı doğrulandı) — birebir uyum.
# Fallback Gregoryen ortalaması 365.2425'tir; o değer SIDEREAL DEĞİLDİR ve
# yalnızca PyJHora kurulmadığında kullanılır.
try:
    from jhora import const as _jhora_const
    SIDEREAL_YEAR = float(_jhora_const.sidereal_year)  # 365.256364
except Exception:
    SIDEREAL_YEAR = 365.2425  # Gregoryen ortalama yıl (sidereal DEĞİL — fallback)
YEAR = SIDEREAL_YEAR  # geriye dönük takma ad (eski import'lar kırılmasın)

LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
         "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
# Standart Vimshottari: Ketu7 Venus20 Sun6 Moon10 Mars7 Rahu18 Jup16 Sat19 Merc17 = 120
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


def balance_years(moon_sidereal_lon: float, smooth: bool = False):
    """Vimshottari balanca kuralı — standart Jyotish + PyJHora referansı.

      current_lord = Ay'ın İÇİNDE olduğu nakshatra'nın lordu (Swati -> Rahu)
      frac_elapsed = nakshatra içinde geçilen oran (0..1)
      balance      = YEARS[current_lord] * (1 - frac_elapsed)   <-- STANDART KURAL
      start_lord   = current_lord (doğum, devam eden MD'ın ortasında açılır)

    PyJHora `vimsottari_dasha_start_date` (canlı okundu) tam olarak bunu yapar:
        nak = int(lon / (360/27));  rem = lon - nak*(360/27)
        elapsed_yrs = (rem / one_star) * period          # DERECESEL (smooth)
        start_date  = jd - elapsed_yrs * sidereal_year   # MD doğumdan GERİYE
    Dolayısıyla PyJHora ile BİREBİR uyum = derecesel oran (smooth=True).
    Klasik pada-sınırı sayımı (frac_exact ∈ {0,.25,.5,.75}) "temiz" golden
    değerler üretir ve varsayılandır; iki mod arasındaki fark en fazla bir
    pada süresidir (~1.7 yıl). Kaynak: engine.nakshatra (TEK KAYNAK).

    Geçici bir sürümde `next_lord * frac_elapsed` kullanılmıştı — hiçbir
    Jyotish kaynağında yoktur, geri alındı. Docstring'deki eski "0.72 vs
    15.36" sayısı da hatalıydı (0.72 = 18×0.04 derecesel, 15.36 = 16×0.96 —
    iki FARKLI lord karıştırılmıştı); aynı olayın doğru ifadeleri:
      derecesel: 18 × (1 − 0.95999) ≈ 0.72 yıl   (PyJHora ile birebir)
      pada-sınırı: 18 × (1 − 0.75) = 4.5 yıl     (Swati pada 4)

    Golden testler (varsayılan pada-sınırı modu):
      Ay 190° (Swati, frac 0.25) -> (13.5, "Rahu", "Rahu")   [18 × 0.75]
      Ay 0°   (Ashwini, frac 0)   -> (7.0,  "Ketu", "Ketu")  [7 × 1.0]

    Dönüş: (balance_years, start_lord, current_lord).
    """
    np_ = nakshatra_pada(moon_sidereal_lon)
    idx = np_["nakshatra_index"]
    # TEK KAYNAK: oran engine.nakshatra'dan gelir; burada yeniden hesaplanmaz.
    frac = np_["frac_smooth"] if smooth else np_["frac_exact"]
    current_lord = LORDS[idx % 9]              # Ashwini=Ketu ... Revati=Mercury
    balance = YEARS[current_lord] * (1.0 - frac)
    return balance, current_lord, current_lord


def vimshottari(moon_sidereal_lon: float, birth_jd_ut: float,
                smooth: bool = False) -> list[dict]:
    """Doğumdan itibaren MD+AD takvimi (julian day UT cinsinden).

    Timeline toplamı = 120 − (nakshatrada doğumdan önce tüketilen yıl); ilk MD
    balanca ile açıldığı için 9 MD'lık döngü tam 120 yıl DEĞİLDİR — normal olan
    budur. `smooth=True` PyJHora ile birebir derecesel balanca verir.
    """
    rem_years, start_lord, _current_lord = balance_years(moon_sidereal_lon, smooth)
    lord_i = LORDS.index(start_lord)
    # PyJHora `vimsottari_mahadasa` ile birebir: 9 MD döner; ilki BALANCA
    # süresiyle açılır (devam eden MD), kalan 8'i tam.
    seq = [LORDS[(lord_i + k) % 9] for k in range(9)]
    durations = [rem_years] + [YEARS[s] for s in seq[1:]]
    md_list = []
    cursor = birth_jd_ut
    for i_md, (lord, yrs) in enumerate(zip(seq, durations)):
        start, end = cursor, cursor + yrs * YEAR
        sub_seq = ANTARDASHA_ORDER[lord]
        # AD süreleri her zaman MD'ın TAM yılıyla ölçeklenir:
        #   AD_yrs = YEARS[lord] * YEARS[sub] / 120
        # İlk MD kırpılmış (balanca) olsa da AD'ler küçülmez. Doğum, devam
        # eden MD'ın İÇİNDE bir noktadır: tüketilen süre kadar GERİDEKİ sanal
        # başlangıçtan yürürüz; böylece ne orantılı küçültme ne de clamp
        # gerekir. Sanal başlangıçta ilk AD tam süresiyle başlar; doğuma
        # ulaşan ilk AD kısmen tüketilmiş olabilir ve segmenti doğumda kesilir.
        consumed_days = (YEARS[lord] - yrs) * YEAR if i_md == 0 else 0.0
        sub_cursor = start - consumed_days     # SANAL başlangıç (doğumdan ÖNCE)
        for si, sub in enumerate(sub_seq):
            sub_full_days = YEARS[lord] * YEARS[sub] / 120.0 * YEAR  # balancadan bağımsız
            seg_start = max(sub_cursor, start)   # doğumdan önceki kısak görünmez
            seg_end = sub_cursor + sub_full_days
            if seg_end > seg_start:
                md_list.append({"mahadasha": lord, "antardasha": sub,
                                "start_utc": swe.revjul(seg_start, 1),
                                "end_utc": swe.revjul(seg_end, 1),
                                "years": round((seg_end - seg_start) / YEAR, 3)})
            sub_cursor = seg_end
        cursor = end
    return md_list
