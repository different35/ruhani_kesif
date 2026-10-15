"""Nakshatra + Pada — kural katmanının en temel birimi (gist BÖLÜM 2: fakt -> hüküm).

27 nakshatra x 4 pada = 108; her pada 3°20' = 1/9 burç.
Bu modül SAF ARİTMETİK yapar; LLM hiçbir sayı üretmez (gist §8 yasakları).

Sayısal kararlar (bu revizyon):
- 108'lik TEK İNDEKS: nakshatra ve pada, bölmeden önce çarparak üretilir
  (`lon * 108 // 360`). Böylece `360/27`'nin float'ta tam temsil edilememesi
  (13.333333333333334) sınır noktalarında (ör. 40.0°, 53.333…°) bir alta
  kayma yaratamaz; `min(...)` clamp hilesi de gerekmez.
- 360'a eşdeğer girdi normalize edilir: Python'da `(-1e-17) % 360.0 == 360.0`
  olduğundan çok küçük negatif boylamlar (ayanamsa çıkarımından gelebilir)
  idx=27/12 üretip NAKSHATRAS[27] / SIGNS[12] ile patlatırdı.
- Ham değer döner; yuvarlama YALNIZCA gösterim alanlarındadır (*_display).
  `round(29.99996, 4) -> 30.0` tuzağına karşı display'de `% 30` / `% 360`
  tekrar uygulanır (30.0 → 0.0, 360.0 → 0.0).
- `frac_elapsed` iki ALANLA tek kaynak olarak döner; dasha katmanı kendi
  başına yeniden hesaplamaz:
    * frac_exact  : pada SINIRI bazında {0, .25, .5, .75} — klasik Jyotish
                    "ay içindeki nakshatra" sayımı ve PyJHora'nın kullandığı
                    değer. Golden balanca testleri bunu kullanır.
    * frac_smooth : derecesel (lon - idx*span)/span — süre hesabı için daha
                    doğru olan sürekli değer.
  Dasha BALANCASI klasik kural olduğundan `frac_exact` ile hesaplanır;
  takvim kayması istenmiyorsa tüketici `frac_smooth`'u okuyabilir.
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
SPAN_DEG = 360.0 / (len(NAKSHATRAS) * PADAS_PER_NAK)  # 3.333... (bir pada)


def _normalize_deg(lon: float) -> float:
    """Herhangi boylamı [0, 360) aralığına indirger.

    Python `%` negatif girdide pozitif sonuç verir ama sonucu 360.0 yapabilir
    (ör. `-1e-17 % 360.0 == 360.0`); bu da `int(lon/span) == 27` ve
    `int(lon//30) == 12` IndexError'larına yol açar. Tam tur atılır.
    """
    out = lon % 360.0
    if out >= 360.0:      # float kenar durumu (çok küçük negatif girdi)
        out = 0.0
    return out


def nakshatra_pada(sidereal_lon: float) -> dict:
    """Boylam (sidereal derece) -> nakshatra, pada, sign, frac_elapsed.

    Dönen anahtarlar:
      ham (sözleşme taşıyıcıları): sidereal_lon yok; deg_in_sign, frac_elapsed
      gösterim (yuvarlanmış, yalnızca insan/LLM çıktısı için): *_display
    """
    lon = _normalize_deg(sidereal_lon)
    n_nak = len(NAKSHATRAS)
    total_padas = n_nak * PADAS_PER_NAK        # 108
    # BÖLMEDEN ÖNCE ÇARP: tek 0..107 indeksi hem nakshatra hem pada türetir.
    # Eski yol `int(lon / (360/27))` idi; 360/27 float'ta 13.333333333333334
    # olduğundan tam sınır girdileri (ör. 53.333333333333336 = 4*360/27'nin
    # float komşusu) bir ALT nakshatra'ya düşebiliyordu. Burada pay önce
    # ölçeklenir, sonra TAM BÖLME ile dilimlenir; `% 108` yalnızca savunma.
    pada_index = int(lon * total_padas) // 360 % total_padas
    idx = pada_index // PADAS_PER_NAK
    pada = pada_index % PADAS_PER_NAK
    # frac_exact TAM SAYI ARİTMETİĞİNDEN türetilir: dilim içi sıra / 4.
    # (Saf `(lon - idx*span)/span` biçimi float biriktirme hatası üretir;
    # balanca klasik pada-sınırı kuralı olduğunda burada kesinlik korunur.)
    frac_exact = pada / PADAS_PER_NAK          # {0, .25, .5, .75} — kesin
    span_nak = 360.0 / n_nak                   # nakshatra yayı (13.333°)
    frac_smooth = (lon - idx * span_nak) / span_nak  # derecesel, 0..1 sürekli
    deg_in_sign = lon % 30.0                   # HAM değer; yuvarlama gösterimde
    sign_index = int(lon // 30.0) % 12
    return {
        "nakshatra": NAKSHATRAS[idx],
        "nakshatra_index": idx,
        "pada": pada + 1,
        "sign": SIGNS[sign_index],
        "sign_index": sign_index,
        "deg_in_sign": deg_in_sign,            # HAM
        "frac_elapsed": frac_smooth,           # HAM derecesel oran (geriye dönük ad)
        "frac_exact": frac_exact,              # pada-sınırı kesini (balanca kaynağı)
        "frac_smooth": frac_smooth,            # açık adlı eşdeğer
        # --- yalnızca gösterim alanları (yuvarlama burada, sözleşme ham'da) ---
        "deg_in_sign_display": round(deg_in_sign % 30.0, 4),   # 30.0 gelirse -> 0.0
        "longitude_display": round(lon % 360.0, 4),            # 360.0 gelirse -> 0.0
    }
