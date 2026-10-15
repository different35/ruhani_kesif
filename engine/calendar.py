"""Takvim yardımcıları — JD(UT) ↔ takvim dönüşümleri, `swisseph` İMPORT ETMEZ.

Lisans temizliği (gist §1.2 + kullanıcı kararı): üretim kodu yalnızca Skyfield
adaptörü ve yerel aritmetik kullanır; pyswisseph yalnızca test referansıdır.

Sözleşme:
- `julday(y, m, d, hour_ut=0.0)` → UT ölçeğinde Julian Day (float).
  Takvim alanları YIL/AY/GÜN olarak verilir; saat UT'dir (12.0 = öğlen UT).
- `revjul(jd_ut, mode=1)` → (year, month, day, hours) — `hours` günün ondalık
  SAATİDİR (ör. 12.5 = 12:30 UT); swisseph.revjul ile aynı sözleşme.
- Her iki yönde de tam tutarlılık ±1e-9 gün içinde korunur (test edilir).

Algoritma: Meeus "Astronomical Algorithms" Ch.7 (Julian Day Number), standart
proleptic Gregorian/Julian geçidi (JD ≥ 2299161 → Gregorian). Bu, skyfield
adapterındaki `_jd_of` / `_iso_from_jd` ile BİREBİR aynı matematiktir; tek fark
burada arayüz takvim tuple'ıdır, ISO string değildir (tek kaynak kuralı:
skyfield_adapter bu modülü kullanacak şekilde refaktör edilmiştir).
"""
from __future__ import annotations


def julday(year: int, month: int, day: int, hour_ut: float = 0.0) -> float:
    """Takvim (UT) -> Julian Day. hour_ut: günün UT saati (ondalık)."""
    if month <= 2:
        year -= 1
        month += 12
    a = year // 100
    b = 2 - a + a // 4
    if a < 0:  # Meeus notasyonu (-Y => Y+1)
        b = 0
    return (int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + b
            - 1524.5 + hour_ut / 24.0)


def revjul(jd: float, mode: int = 1) -> tuple:
    """Julian Day (UT) -> (yıl, ay, gün, saat). mode=1: ondalık saat (swiss sözleşmesi).

    mode=2: (yıl, ay, gün, saat, dakika, saniye) tam sayı demeti döner.
    """
    if int(jd) == jd:
        jd += 0.5
    z = int(jd)
    f = jd - z
    if z >= 2299161:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    else:
        a = z
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day_f = b - d - int(30.6001 * e) + f
    day = int(day_f)
    frac = day_f - day
    if mode == 2:
        hours = int(frac * 24.0)
        minutes = int((frac * 24.0 - hours) * 60.0)
        seconds = int(round(((frac * 24.0 - hours) * 60.0 - minutes) * 60.0))
        if seconds == 60:
            seconds = 0
            minutes += 1
        if minutes == 60:
            minutes = 0
            hours += 1
        return (c - 4716 if (e > 2) else c - 4715,  # yıl
                e - 1 if e < 14 else e - 13,        # ay
                day, hours, minutes, seconds)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    return (year, month, day, frac * 24.0)


def jd_to_datetime(jd_ut: float):
    """JD(UT) -> timezone-aware UTC datetime (hata ≤ ~ms; yuvarlama saniyeye)."""
    import datetime as _dt
    y, mo, d, hh, mm, ss = revjul(jd_ut, mode=2)
    micro = int(round((jd_ut - julday(y, mo, d, hh + mm / 60.0 + ss / 3600.0)) * 86400.0 * 1e6))
    micro = max(0, min(micro, 999999))
    try:
        return _dt.datetime(y, mo, d, hh, mm, ss, micro, tzinfo=_dt.timezone.utc)
    except ValueError:  # 23:59:59.9999995 yuvarlama taşıması
        base = _dt.datetime(y, mo, d, tzinfo=_dt.timezone.utc) + _dt.timedelta(days=1)
        return base.replace(hour=0, minute=0, second=0, microsecond=micro)
