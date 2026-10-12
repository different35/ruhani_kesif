"""Nakshatra + Pada — kural katmanının en temel birimi (gist BÖLÜM 2: fakt -> hüküm).

27 nakshatra x 4 pada = 108; her pada 3°20' = 1/9 burç.
Bu modül SAF ARİTMETİK yapar; LLM hiçbir sayı üretmez (gist §8 yasakları).
"""
from __future__ import annotations

NAKSHATRAS = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
)
SIGNS = ("Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")
PADAS_PER_NAK = 4
SPAN_DEG = 360.0 / (len(NAKSHATRAS) * PADAS_PER_NAK)  # 3.333...


def nakshatra_pada(sidereal_lon: float) -> dict:
    """Boylam (sidereal derece) -> nakshatra, pada, sign, dev degree."""
    lon = sidereal_lon % 360.0
    idx = int(lon / (360.0 / len(NAKSHATRAS)))
    within = lon - idx * (360.0 / len(NAKSHATRAS))
    pada = min(int(within / SPAN_DEG), PADAS_PER_NAK - 1)
    return {
        "nakshatra": NAKSHATRAS[idx],
        "nakshatra_index": idx,
        "pada": pada + 1,
        "sign": SIGNS[int(lon // 30)],
        "sign_index": int(lon // 30),
        "deg_in_sign": round(lon % 30, 4),
        "dev_degree": round(lon, 4),
    }
