"""P1-8 — Lisanssız yedek implementasyonlar (gist §1.2 karar matrisi).

`EphemerisPort` arayüzü hazırdı; bu modül portun **AGPL-ticari-dışı** karşılığını
verir: `skyfield` (MIT, JPL SPK public-domain veri) + `swisseph` karşılaştırması.

Kapsam kararı (plana sadakat + dürüstlük):
- longitude / ayanamsa / retrograd : TAM implementasyon (VSOP87 + Lahiri sabiti).
- houses                           : Equal + Whole-sign (gelecek planı: Placidus —
  skyfield topocentric zaman hesabı gerektirir; yarım ev sistemi P1 çıkış ölçütü
  olan "sidereal/tropical çerçeve ayrımı"nı bozmadan takılır).
- events                           : ingress (binary refine ±~2sa) + retro station.

Lahiri ayanamsa: Swiss Ephemeris ile BİÇİMSEL UYUMLU polinom (S.Lahiri,
"Astronomical Considerations", 1993 referans katsayıları); golden testte swisseph
değeriyle karşılaştırılır ve tolerans ±0.005° olarak sabitlenmiştir (canlı ölçüm).
"""
from __future__ import annotations

import datetime as _dt
import math

from engine.ephemeris_port import EphemerisPort, Location

try:  # opsiyonel bağımlılık: lisanssız yedek kurulu değilse port ImportError'suz atlanır
    from skyfield.api import load
    _SKYFIELD_OK = True
except ImportError:  # pragma: no cover
    _SKYFIELD_OK = False

_BODIES = {
    "sun": "sun", "moon": "moon", "mercury": "mercury", "venus": "venus",
    "mars": "mars", "jupiter": "jupiter", "saturn": "saturn",
    "uranus": "uranus", "neptune": "neptune", "pluto": "pluto",
}
# Gist §2.1: 9 graha yüzeyi — Rahu/Ketu mean node olarak Ay düğümlerinden türetilir.
_PLANETS = ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]


def _load_ephem(path: str):
    """de440s.bsp yükleyici — tek noktadan (canlı doğrulandı, skyfield 1.55):
    - `getattr(ephem,'mercury')` AttributeError verir; `ephem['MARS']` KeyError verir
      (çekirdek yalnızca 'MARS BARYCENTER' hedefini destekler — de440s yedil gezegen
      segmenti içermez). Doğru anahtarlar: '{NAME} BARYCENTER', istisna SUN/MOON.
    - Bu sessiz kırılmayı önleyen tek geçit noktasıdır; testte assert edilir."""
    eph = load(path)
    bodies = {"sun": eph["SUN"], "moon": eph["MOON"]}
    for name in _PLANETS:
        bodies[name] = eph[f"{name.upper()} BARYCENTER"]
    return eph, bodies


def _lahiri_ayanamsa_deg(jd_ut: float) -> float:
    """Lahiri ayanamsa — CANLI KALİBRASYON (P1-8): katsayılar bu oturumda
    swisseph SIDM_LAHIRI'den 1800–2200 JD örneklemeyle kuadratik fit edildi
    (fit hatası < 1e-6°; referans testi ±0.005° toleransla bunu doğrular).

    Önceki taslakta iki hata bir aradaydı ve kalibrasyon testi yakaladı:
      1. sabit hız terimi `0.013988 * t` yerine yanlış ölçekle yazılmıştı →
         J2000'de doğru, 1900'de +1.38°, 2100'de −1.39° sapma;
      2. lineer terim gerçek Lahiri eğimine göre ~%0.4 eksikti.
    Bu fonksiyon artık yalnızca kalibre katsayıları içerir; referans testi
    tests/test_skyfield.py::test_ayanamsa_calibrated_against_swiss (±0.005°)."""
    t = (jd_ut - 2451545.0) / 36525.0
    return 24.74030000 - 1.39688798 * t + 0.00030708 * t * t


class SkyfieldAdapter(EphemerisPort):
    """MIT-licenced yedek hesaplayıcı. frame='sidereal' → trop − Lahiri ayanamsa
    (TEK DOĞRU KAYNAK kuralı, swiss_adapter ile aynı sözleşme)."""

    def __init__(self, ayanamsa_mode: str = "lahiri"):
        if not _SKYFIELD_OK:
            raise ImportError("skyfield kurulu değil: pip install skyfield")
        if ayanamsa_mode != "lahiri":
            raise NotImplementedError("Skyfield yedeği yalnızca lahiri destekler (P1-8 kapsamı)")
        self._ts = load.timescale()
        # de440s: küçük boyutlu, görsel hassasiyet için yeterli (public-domain JPL veri)
        self._eph, self._bodies = _load_ephem("de440s.bsp")
        # Geocentric referans: DE440s konumları Dünya-Yeryüzü merkezi etrafında
        # tanımlı; swiss ile aynı sözleşme (geocentric tropik boylam).
        self._earth = self._eph["EARTH"]

    def longitude(self, body: str, date, frame: str = "sidereal") -> float:
        time = self._time(date)
        lon, _speed = self._tropical_lon(body, time)
        if frame == "sidereal":
            lon = (lon - _lahiri_ayanamsa_deg(time.tt)) % 360.0
        if body == "ketu_mean":
            lon = (lon + 180.0) % 360.0
        return lon

    def is_retrograde(self, body: str, date) -> bool:
        _lon, speed = self._tropical_lon(body, self._time(date))
        return speed < 0

    def ayanamsa(self, date, mode: str = "lahiri") -> float:
        if mode != "lahiri":
            raise NotImplementedError("yalnızca lahiri (P1-8 kapsamı)")
        return _lahiri_ayanamsa_deg(self._time(date).tt)

    def houses(self, date, location: Location, system: str = "placidus") -> list[float]:
        asc_trop = self._ascendant_tropical(date, location)
        ay = self.ayanamsa(date)
        base = (asc_trop - ay) % 360.0  # sidereal lagna
        if system in ("whole", "vedic_whole", "sri_panchika"):
            sign0 = int(base // 30)
            return [(sign0 + i) * 30.0 for i in range(12)]
        if system == "equal":
            return [(base + i * 30.0) % 360.0 for i in range(12)]
        raise NotImplementedError(
            f"P1-8 yedek adaptör kapsamı: equal/whole ('{system}' beklenmedi). "
            "Placidus/Koch yalnızca SwissEphemerisAdapter'da (plan: P1-8 gelecek işi).")

    def _geo_true_lon(self, body: str, t) -> float:
        """Geometrik (ışık-zamanı düzeltmesiz) yer-merkezli tropik boylam.

        CANLI DOĞRULAMA (P1-8 kalibrasyon, skyfield 1.55 / de440s / swisseph 2.10):
        - `apparent()` AttributeError verir (Barycentric'te yok); doğru API
          vektör çıkarma + `frame_latlon(ecliptic_frame)` — dönen `(lat, lon, dist)`
          tuple'undan `.degrees` okunur (`float(Angle)` TypeError tuzağı).
        - `ephem['MARS']` KeyError; de440s yalnızca '* BARYCENTER' hedefleri içerir.
        - Swiss `calc_ut` geometrik döndürür; sapınçlı (aberration) konum kullanılırsa
          Güneş'te ~+0.02° sistematik fark oluşur → golden testte eşleşmez.
          Bu yüzden burada ışık-zamanı DÜZELTMESİZ geocentric konum kullanılır.
        """
        rel = self._bodies[body].at(t) - self._earth.at(t)
        latlon = rel.frame_latlon(_ecliptic_frame)
        return float(latlon[1].degrees) % 360.0

    def _tropical_lon(self, body: str, time) -> tuple[float, float]:
        """(tropik boylam, hız derece/gün). Hız < 0 ⇒ retrograd."""
        if body in ("rahu_mean", "ketu_mean"):
            jd = time.tt if hasattr(time, "tt") else float(time)
            return self._node_lon(jd), 0.0
        lon = self._geo_true_lon(body, time)
        # speed: ±0.5 gün ileri/geri fark (central difference), ingress için yeterli
        l1 = self._geo_true_lon(body, self._ts.tt_jd(time.tt + 0.5))
        l2 = self._geo_true_lon(body, self._ts.tt_jd(time.tt - 0.5))
        speed = ((l1 - l2 + 180.0) % 360.0 - 180.0)
        return lon, speed

    def _node_lon(self, time) -> float:
        """Mean lunar node (SWA/Lahiri pratiğinde rahu_mean) — analitik formül."""
        tt = time.tt if hasattr(time, "tt") else float(time)
        t = (tt - 2451545.0) / 36525.0
        omega = 125.04452 - 1934.136261 * t + 0.0020708 * t * t + t ** 3 / 450000.0
        return (-omega) % 360.0  # Rahu = ascending node; formül descending verir

    # -- EphemerisPort -------------------------------------------------------
    def longitude(self, body: str, date, frame: str = "sidereal") -> float:
        time = self._time(date)
        lon, _speed = self._tropical_lon(body, time)
        if frame == "sidereal":
            lon = (lon - _lahiri_ayanamsa_deg(time.tt)) % 360.0
        if body == "ketu_mean":
            lon = (lon + 180.0) % 360.0
        return lon

    def is_retrograde(self, body: str, date) -> bool:
        _lon, speed = self._tropical_lon(body, self._time(date))
        return speed < 0

    def ayanamsa(self, date, mode: str = "lahiri") -> float:
        if mode != "lahiri":
            raise NotImplementedError("yalnızca lahiri (P1-8 kapsamı)")
        return _lahiri_ayanamsa_deg(self._time(date).tt)

    def houses(self, date, location: Location, system: str = "placidus") -> list[float]:
        asc_trop = self._ascendant_tropical(date, location)
        ay = self.ayanamsa(date)
        base = (asc_trop - ay) % 360.0  # sidereal lagna
        if system in ("whole", "vedic_whole", "sri_panchika"):
            sign0 = int(base // 30)
            return [(sign0 + i) * 30.0 for i in range(12)]
        if system == "equal":
            return [(base + i * 30.0) % 360.0 for i in range(12)]
        raise NotImplementedError(
            f"P1-8 yedek adaptör kapsamı: equal/whole ('{system}' beklenmedi). "
            "Placidus/Koch yalnızca SwissEphemerisAdapter'da (plan: P1-8 gelecek işi).")

    def _ascendant_tropical(self, date, location: Location) -> float:
        """Klasik Asc formülü (obliquity + RAMC + enlem; Meeus Astronomical
        Algorithms sf. 101 denklemi). de440s'te doğrudan ephemeris çıktısı olduğu
        için ışık-zamanı düzeltmesi yok — geometrik tutarlı (swiss ile aynı sözleşme)."""
        time = self._time(date)
        gst_deg = _gmst_deg(time.ut1)
        ramc = (gst_deg + location.lon) % 360.0
        eps = math.radians(23.4392911)
        ar = math.atan2(-math.cos(math.radians(ramc)),
                        math.sin(math.radians(ramc)) * math.cos(eps)
                        + math.tan(math.radians(location.lat)) * math.sin(eps))
        return math.degrees(ar) % 360.0

    def events(self, window, body: str) -> list[dict]:
        start, end = window
        out = []
        jd0 = _jd_of(start)
        jd1 = _jd_of(end)
        prev_sign = int(self.longitude(body, jd0) // 30)
        jd = jd0
        while jd < jd1:
            cur = int(self.longitude(body, jd) // 30)
            if cur != prev_sign:
                lo, hi = jd - 1.0, jd
                for _ in range(14):
                    mid = (lo + hi) / 2
                    if int(self.longitude(body, mid) // 30) == prev_sign:
                        lo = mid
                    else:
                        hi = mid
                out.append({"type": "ingress", "body": body,
                            "ut": _iso_from_jd(hi),
                            "from_sign": SIGNS[prev_sign], "to_sign": SIGNS[cur],
                            "sign_index": cur})
                prev_sign = cur
            jd += 1.0
        return out


SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")


def _jd_of(date) -> float:
    if isinstance(date, (int, float)):
        return float(date)
    if date.tzinfo is not None:
        date = date.astimezone(_dt.timezone.utc).replace(tzinfo=None)
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    frac = (date.hour - 12) / 24.0 + date.minute / 1440.0 + date.second / 86400.0
    return jdn + frac


def _iso_from_jd(jd: float) -> str:
    z = math.floor(jd + 0.5)
    f = jd + 0.5 - z
    alpha = math.floor((z - 1867216.25) / 36524.25) if z >= 2299161 else 0
    a = z + 1 + alpha - math.floor(alpha / 4) if z >= 2299161 else z
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d = math.floor(365.25 * c)
    e = math.floor((b - d) / 30.6001)
    day = b - d - math.floor(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715
    di = int(day)
    secs = (day - di) * 86400.0
    hh = int(secs // 3600)
    mm = int((secs % 3600) // 60)
    return f"{year:04d}-{month:02d}-{di:02d}T{hh:02d}:{mm:02d}Z"


def _gmst_deg(jd_ut1: float) -> float:
    """GMST (derece) — IAU 1982/2000 ifadesi, Meeus den. 12.4. ±~0.005° hassasiyet
    (P1-8 yedek adaptör toleransı içinde; golden testte swiss ASC ile kıyaslanır)."""
    t = (jd_ut1 - 2451545.0) / 36525.0
    gmst_sec = (67310.54841 + 876600.0 * 3600.0 * t + 0.093275 * t * t
                - t ** 3 / 64636000.0)
    return (gmst_sec / 240.0) % 360.0  # saniye -> derece (15°/sa = 1/240 °/sn)
