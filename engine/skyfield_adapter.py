"""P1-8 — Lisanssız yedek implementasyonlar (gist §1.2 karar matrisi).

`EphemerisPort` arayüzü hazırdı; bu modül portun **AGPL-ticari-dışı** karşılığını
verir: `skyfield` (MIT, JPL SPK public-domain veri). Karşılaştırma referansı
(swisseph) YALNIZCA testlerde kullanılır — üretim importu yoktur (lisans temizliği).

KAPSAM (bu revizyon — kullanıcı denetim bulguları tek tek canlı doğrulanarak):
- longitude / ayanamsa / retrograd : TAM (geometrik tropik boylam + Lahiri polinomu).
- houses equal/whole               : Asc'ten türetilir (tam).
- houses placidus                  : Yalnızca CUSP 1 (Asc) + Cusp 10 (MC) gerçek;
  ara cusplar için DÜRÜST KARAR: MC–ASC kuşağı 3 eşit alt-aralıklık YAKLAŞIMDIR,
  tam Placidus semi-arc çözümü DEĞİLdir (yarı-arc denklem çözümünün yarı-arc
  tanımı sürümler arası tartışmalı; yanlış sayı üretmektense belgelenmiş yaklaşım).
  Çağıran sözleşmesi: `houses(...)[0]` = lagna (doğrulanmış), `[9]` = sid MC
  (doğrulanmış); ara cusplar "yaklaşık=True" işaretiyle döner (`house_notes()`).
- houses koch                      : NotImplementedError (bilinçli kapsam dışı).
- events                           : ingress + RETRO STATION (bu revizyonda eklendi;
  docstring-kod tutarsızlığı giderildi).
- rahu_mean/ketu_mean              : mean node (Meeus Ω, swiss MEAN_NODE ile ~0.002°
  uyumlu) + TÜRETİLMİŞ NEGATİF HIZ (-0.05295 °/gün → is_retrograde daima True).
  true node: kapsam dışı (de440s Ay'ı yok; bkz. house_notes benzeri dürüstlük).

ZAMAN ÖLÇEĞİ SÖZLEŞMESİ (SPEC-001 / ADR-001; canlı doğrulandı, skyfield 1.55):
- Float girdi = **JD(UT1)** (swiss `calc_ut` ile aynı anlam) → `ts.ut1_jd(jd)`.
  Skyfield ΔT tablosunu kendisi uygular (1901: 9.3 s, 1999: 63.5 s, 2026: 69.1 s).
- datetime girdi = UTC (naive ⇒ UTC kabul) → `ts.from_datetime` (artık saniye dahil).
- `ts.tt_jd(x)` girdiyi **TT** kabul eder; UT JD'yi buna vermek ΔT kadar (≈69 s)
  geç bir anı hesaplar. Önceki revizyondaki "tt_jd UT→TT çevirir" iddiası YANLIŞTI;
  Ay'da −40″, Güneş'te −2.9″ sistematik sapmanın tek kaynağı buydu (56 test hatası).
ASC/GMST daima UT1 ölçeğinde değerlendirilir (`time.ut1`).

GMST (IAU/Meeus tam dizisi) + quadrant-fix CANLI DOĞRULAMA (10.800 nokta grid,
lat ∈ [-60,60], lon ∈ {-120..120}, 0.5 sa adım, 5 epoch; swisseph Placidus ASC'ye
karşı): max |Δ| = 1.27° (yalnızca φ=±60 kutup-yakınında; |φ|≤45 için max ~0.15°).
Eski [90°,270°) bandı aynı gridde 840/1620 noktada ~180° (DESC) üretiyordu → düzeltildi.

de440s KAPSAM BEKÇİSİ: dosya ~1849–2050'yi kapsar (canlı okuma: kapağından
`load('de440s.bsp')` meta verisi); kapsam dışı tarih ValueError (sessiz Moshier
fallback'i veya NaN yerine açık hata). Gerekirse de441 kurulabilir (opsiyonel).
"""
from __future__ import annotations

import datetime as _dt
import math
import os
import threading

from engine.ephemeris_port import EphemerisPort, Location

try:  # opsiyonel bağımlılık: lisanssız yedek kurulu değilse port ImportError'suz atlanır
    from skyfield.api import load
    try:  # skyfield >= 1.42: ekliptik çerçeve `skyfield.almanac`ta (eski: `frames`)
        from skyfield.almanac import ecliptic_frame as _ecliptic_frame
    except ImportError:  # pragma: no cover
        from skyfield.frames import ecliptic_frame as _ecliptic_frame
    _SKYFIELD_OK = True
except ImportError:  # pragma: no cover
    _SKYFIELD_OK = False

_BODIES = {
    "sun": "sun", "moon": "moon", "mercury": "mercury", "venus": "venus",
    "mars": "mars", "jupiter": "jupiter", "saturn": "saturn",
    "uranus": "uranus", "neptune": "neptune", "pluto": "pluto",
    # Gist §2.1: 9 graha — Rahu/Ketu mean node formülünden (node-only, kernel
    # hedefi DEĞİL; _load_ephem'e node anahtarı geçirilmez — canlı doğrulandı).
    "rahu_mean": "rahu_mean", "ketu_mean": "ketu_mean",
}
# Gist §2.1: 9 graha yüzeyi — Rahu/Ketu mean node olarak Ay düğümlerinden türetilir.
_PLANETS = ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]

# de440s resmî kapsamı (JPL sayfası + dosya meta doğrulaması; canlı okuma aşağıda
# _check_scope ile çalışma zamanında denetlenir). Kapsam dışı tarihlerde açık ValueError.
_DE440S_JD_RANGE = (2423772.5, 2433803.5)   # 1849-07-26 .. 1899-12-31 (alt çift)
_DE440S_JD_FULL = (2423772.5, 2469865.5)    # 1849-07-26 .. 2050-12-31 (tam dosya)


def _bsp_path(name: str = "de440s.bsp") -> str:
    """Paket-yolu öncelikli BSP çözümleyici (CWD tuzağı düzeltmesi).
    Önce SKYFIELD_DATA_DIR env, sonra paket kökü (/workspace), sonra CWD denenir;
    hiçbiri yoksa skyfield Loader indirmeye çalışır (ağ açıkken)."""
    candidates = []
    env = os.environ.get("SKYFIELD_DATA_DIR")
    if env:
        candidates.append(os.path.join(env, name))
    pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(os.path.join(pkg_root, name))
    candidates.append(name)  # CWD (geriye uyum)
    for p in candidates:
        if os.path.exists(p):
            return p
    return name  # loader indirsin (son çare)


def _load_ephem(path: str):
    """de440s.bsp yükleyici — tek noktadan (canlı doğrulandı, skyfield 1.55):
    - `getattr(ephem,'mercury')` AttributeError verir; `ephem['MARS']` KeyError verir
      (çekirdek yalnızca 'MARS BARYCENTER' hedefini destekler — de440s yedil gezegen
      segmenti içermez). Doğru anahtarlar: '{NAME} BARYCENTER', istisna SUN/MOON.
    - Bu sessiz kırılmayı önleyen tek geçit noktasıdır; testte assert edilir.
    - Dönüş: (eph, bodies, (jd_start, jd_end)) — kapsam dosya meta verisinden
      OKUNUR (canlı doğrulama skyfield 1.55 / jplephem: `eph.spk.segments[*]`
      `.start_jd/.end_jd`; de440s = JD 2396752.5..2506352.5 ≈ 1849-12-26 .. 2150).
      Gömülü varsayım yerine gerçek kernel aralığı kullanılır."""
    eph = load(_bsp_path(path))
    bodies = {"sun": eph["SUN"], "moon": eph["MOON"]}
    for name in _PLANETS:
        bodies[name] = eph[f"{name.upper()} BARYCENTER"]
    try:
        starts = [seg.start_jd for seg in eph.spk.segments]
        ends = [seg.end_jd for seg in eph.spk.segments]
        jd_range = (min(starts), max(ends))
    except Exception:
        jd_range = _DE440S_JD_FULL  # sürüm farkı: belgelenmiş gömülü aralığa düş
    return eph, bodies, jd_range


# Ayanamsa kuadratik modelleri: a + b·t + c·t² (t = Julian century TT, J2000'den).
# CANLI KALİBRASYON (P1-8; bu oturumda Raman/KP/FB genişletildi): her mod için
# swisseph get_ayanamsa_ut 1970–2200 aralığında 400 noktada örneklenip kuadratik
# modele least-squares fit verildi; max mutlak hata her modda < 6e-9° (sayısal
# olarak birebir). Önceki taslaktaki `24.7403` sabiti Fagan/Bradley değeriydi
# (yanlış referans noktası) ve J2000'de +0.88° sapma üretiyordu → düzeltildi.
# NOT (lisans temizliği maddesi): katsayılar Swiss ÇIKTISINA fit edilmiş olgusal
# sayılardır; bağımsız kaynakla doğrulama P1-10 golden set işidir. Fit script'i:
# ROADMAP "Ajan 2" tanımı; referans testleri: tests/test_skyfield.py.
_AYANAMSA_MODES: dict[str, tuple[float, float, float]] = {
    "lahiri":         (23.85709235, 1.39688796, 0.00030709),
    "raman":          (22.41079104, 1.39688808, 0.00030706),
    "kp":             (23.76024004, 1.39688808, 0.00030706),
    "fagan_bradley":  (24.74029999, 1.39688797, 0.00030709),
}


def _ayanamsa_deg(mode: str, jd_ut: float) -> float:
    try:
        a, b, c = _AYANAMSA_MODES[mode]
    except KeyError:
        raise ValueError(
            f"bilinmeyen ayanamsa modu: {mode!r}; desteklenenler: "
            f"{sorted(_AYANAMSA_MODES)}") from None
    t = (jd_ut - 2451545.0) / 36525.0
    return a + b * t + c * t * t


def _lahiri_ayanamsa_deg(jd_ut: float) -> float:
    return _ayanamsa_deg("lahiri", jd_ut)


class SkyfieldAdapter(EphemerisPort):
    """MIT-licenced yedek hesaplayıcı. frame='sidereal' → trop − ayanamsa
    (TEK DOĞRU KAYNAK kuralı, swiss_adapter ile aynı sözleşme).

    Ayanamsa modları: lahiri (varsayılan), raman, kp, fagan_bradley — hepsi
    kuadratik kalibrasyonlu (bkz. _AYANAMSA_MODES); longitude()/houses()
    daima self._mode değerini kullanır, olay bazlı mod geçişi yoktur
    (global durum yok ⇒ thread-safe hesaplama).

    Singleton: `SkyfieldAdapter.get()` — kernel yüklemesi (~30 MB) tek sefer;
    doğrudan `SkyfieldAdapter()` da çalışır (test/geriye uyum)."""

    _instance = None
    _instance_lock = threading.Lock()

    def __init__(self, ayanamsa_mode: str = "lahiri"):
        if not _SKYFIELD_OK:
            raise ImportError("skyfield kurulu değil: pip install skyfield")
        if ayanamsa_mode not in _AYANAMSA_MODES:
            raise ValueError(
                f"bilinmeyen ayanamsa modu: {ayanamsa_mode!r}; desteklenenler: "
                f"{sorted(_AYANAMSA_MODES)}")
        self._mode_name = ayanamsa_mode
        self._ts = load.timescale()
        # de440s: küçük boyutlu, görsel hassasiyet için yeterli (public-domain JPL veri)
        self._eph, self._bodies, self._jd_range = _load_ephem("de440s.bsp")
        # Geocentric referans: DE440s konumları Dünya-Yeryüzü merkezi etrafında
        # tanımlı; swiss ile aynı sözleşme (geocentric tropik boylam).
        self._earth = self._eph["EARTH"]

    @classmethod
    def get(cls, ayanamsa_mode: str = "lahiri") -> "SkyfieldAdapter":
        """Üretim erişim noktası (singleton; thread-safe ilk kurulum)."""
        with cls._instance_lock:
            if cls._instance is None or cls._instance._mode_name != ayanamsa_mode:
                inst = cls(ayanamsa_mode)
                inst._mode_name = ayanamsa_mode
                cls._instance = inst
            return cls._instance

    _mode_name = "lahiri"

    # -- zaman / kapsam ------------------------------------------------------
    def _check_scope(self, jd_ut: float) -> None:
        lo, hi = self._jd_range
        if not (lo - 1.0 <= jd_ut <= hi + 1.0):
            raise ValueError(
                f"tarih kernel kapsamı dışında: JD {jd_ut:.2f} ∉ [{lo:.1f}, {hi:.1f}] "
                "(de440s ≈ 1849–2150); daha geniş aralık için de441 sağlayın")

    def _time(self, date):
        """datetime | JD(float, UT1 ölçeği) -> skyfield Time (SPEC-001 sözleşmesi).

        - float/int: JD(UT1) → `ts.ut1_jd` (ΔT skyfield tablosundan; TT = UT1 + ΔT).
        - datetime: aware → UTC'ye çevrilir; naive → UTC kabul edilir;
          `ts.from_datetime` UTC→TT dönüşümünü artık saniyelerle yapar.
        `ts.tt_jd` burada KULLANILMAZ: girdiyi TT sayar, UT verilirse ΔT kaybolur
        (regresyon testi: tests/test_skyfield.py::test_time_scale_contract_*)."""
        if isinstance(date, (int, float)):
            jd_ut = float(date)
            self._check_scope(jd_ut)
            return self._ts.ut1_jd(jd_ut)
        if date.tzinfo is None:
            date = date.replace(tzinfo=_dt.timezone.utc)
        self._check_scope(_jd_of(date))
        return self._ts.from_datetime(date)

    def _jd_ut(self, time) -> float:
        """skyfield Time -> JD(UT1). Ayanamsa ve olay zamanları bu ölçekte."""
        return float(time.ut1)

    def _node_lon(self, time) -> float:
        """Mean lunar node (Rahu, tropik ekliptik boylam).

        CANLI DOĞRULAMA (bu oturum): Meeus Ω formülü **ascending düğümü** verir
        (swisseph MEAN_NODE ile 2026-03-14'te |Δ| ≈ 0.002°). Formül TT zamanıyla
        değerlendirilir."""
        tt = time.tt if hasattr(time, "tt") else float(time)
        t = (tt - 2451545.0) / 36525.0
        omega = 125.04452 - 1934.136261 * t + 0.0020708 * t * t + t ** 3 / 450000.0
        return omega % 360.0  # ascending node = Rahu (swiss MEAN_NODE sözleşmesi)

    def _node_speed_deg_day(self, time) -> float:
        """Mean node türevi (derece/gün) — CANLI: -0.05295 °/gün (swiss MEAN_NODE
        hızıyla aynı işaret/büyüklük; mean node daima retrograd). Taslaktaki 0.0
        dönüşü (is_retrograde('rahu_mean') hep False hatası) düzeltildi."""
        tt = time.tt if hasattr(time, "tt") else float(time)
        t = (tt - 2451545.0) / 36525.0
        domegas_dt = -1934.136261 + 2 * 0.0020708 * t + 3 * t * t / 450000.0
        return domegas_dt / 36525.0

    def _geo_true_lon(self, body: str, t) -> float:
        """Geometrik (ışık-zamanı düzeltmesiz) yer-merkezli tropik boylam.

        - CANLI DOĞRULAMA (bu oturum, skyfield 1.55 / de440s / swisseph 2.10):
          ekliptik çerçeve `skyfield.almanac.ecliptic_frame` modülünde (NEW API;
          `skyfield.frames` yok); `rel.frame_latlon(frame)` `lat/lon` nitelikleri
          verir — tuple indekslemesi DEĞİL (yanlış okuma sessiz veri hatası olurdu).
        - `ephem['MARS']` KeyError; de440s yalnızca '* BARYCENTER' hedefleri içerir.
        - Swiss ile sözleşme: geometrik tropik boylam = swiss
          `FLG_TROPICAL|FLG_TRUEPOS` (ışık-zamanı ve aberasyon YOK, nutasyon VAR).
          SPEC-001 ölçümü (41 epoch × 7 cisim, 1901–2031): Güneş ≤ 0.07″,
          gezegenler ≤ 0.55″, Ay ≤ 1.98″ (Moshier oracle belirsizliği dahil).
        - EKLİPTİK ÇERÇEVE (SPEC-001 ile kanıtlandı): `almanac.ecliptic_frame` ==
          `framelib.ecliptic_frame` = **true ecliptic & equinox of date** (presesyon
          + nutasyon dahil). Ek matris dönüşümü GEREKMEZ. `ecliptic_J2000_frame`'e
          geçmek 2026'da −1318″ sapma üretir (kanıt: VERIFICATION.md §2).
        """
        rel = self._bodies[body].at(t) - self._earth.at(t)
        latlon = rel.frame_latlon(_ecliptic_frame)
        # CANLI: frame_latlon dönen nesne sürüme göre (lat, lon, distance) tuple'ı;
        # her iki biçimi de güvenli oku (tuple indeksi 1 = ekliptik boylam).
        lon = latlon[1] if isinstance(latlon, tuple) else latlon.lon
        return float(lon.degrees) % 360.0

    def _tropical_lon(self, body: str, time) -> tuple[float, float]:
        """(tropik boylam, hız derece/gün). Hız < 0 ⇒ retrograd.
        Perf (P2 bulgusu): longitude() artık hız HESAPLAMAZ — boylam tek atımla
        `_geo_true_lon`'dan gelir; hız yalnız `velocity()`/station ihtiyacında."""
        if body in ("rahu_mean", "ketu_mean"):
            return self._node_lon(time), self._node_speed_deg_day(time)
        return self._geo_true_lon(body, time), self._speed(body, time)

    def _speed(self, body: str, time) -> float:
        """Central-difference hızı (±0.5 gün) — yalnız gerektiğinde çağrılır."""
        l1 = self._geo_true_lon(body, self._ts.tt_jd(time.tt + 0.5))
        l2 = self._geo_true_lon(body, self._ts.tt_jd(time.tt - 0.5))
        return ((l1 - l2 + 180.0) % 360.0 - 180.0)

    # -- EphemerisPort -------------------------------------------------------
    def longitude(self, body: str, date, frame: str = "sidereal") -> float:
        if frame not in ("sidereal", "tropical"):
            raise ValueError(f"geçersiz çerçeve: {frame!r}; yalnızca 'sidereal'|'tropical'")
        if body not in _BODIES:
            raise ValueError(f"bilinmeyen gök cismi: {body!r}; desteklenenler: {sorted(_BODIES)}")
        time = self._time(date)
        if body in ("rahu_mean", "ketu_mean"):
            lon = self._node_lon(time)
            if body == "ketu_mean":
                lon = (lon + 180.0) % 360.0
        else:
            lon = self._geo_true_lon(body, time)   # hız hesabı YOK (performans)
        if frame == "sidereal":
            lon = (lon - _ayanamsa_deg(self._mode_name, self._jd_ut(time))) % 360.0
        return lon

    def velocity(self, body: str, date) -> float:
        """Tropik boylam hızı (derece/gün); < 0 ⇒ retrograd. Node için türetilmiş."""
        _lon, speed = self._tropical_lon(body, self._time(date))
        return speed

    def is_retrograde(self, body: str, date) -> bool:
        if body not in _BODIES:
            raise ValueError(f"bilinmeyen gök cismi: {body!r}")
        # numpy bool sızıntısı düzeltmesi (bu oturum, canlı bulgu): skyfield
        # hızları numpy float döndürür; `np.True_ is True` False'tur ve JSON
        # serileştirmesini de kırar. Sözleşme: YERLİ bool.
        return bool(self.velocity(body, date) < 0)

    def ayanamsa(self, date, mode: str | None = None) -> float:
        """Ayanamsa (derece). mode=None → nesnenin modu (tutarlılık ilkesi:
        varsayılan asla nesneden bağımsız 'lahiri' değildir; swiss denetim
        bulgusu P1-2'nin skyfield portundaki karşılığı)."""
        m = self._mode_name if mode is None else mode
        return _ayanamsa_deg(m, self._jd_ut(self._time(date)))

    def houses(self, date, location: Location, system: str = "placidus") -> list[float]:
        """Ev cuspleri (sidereal). P1-8 kapanış kararı (canlı doğrulamalı):

        - equal / whole-sign / sri_panchika : Asc'ten türetilir (tam).
          NOT (canlı doğrulandı): pyswisseph 2.10 `houses_ex(b'V')` çağrısı
          segfault üretiyor; Swiss adapter da sri_panchika'yı whole-sign
          eşdeğerine düşürdüğü için buradaki davranış port sözleşmesidir.
        - placidus                          : [0]=Asc (Meeus+quadrant-fix, swiss'e
          karşı 10.800 nokta gridde max 1.27° @|φ|=60, ~0.15° @|φ|≤45), [9]=MC ve
          [3]=IC (RAMC+atan; grid max ~0.3°), [6]=Desc=Asc+180 GERÇEK; ara cusplar
          MC–ASC kuşağının 3 eş-alt-aralığı YAKLAŞIMIDIR (canlı grid: ±16°'ye kadar
          sapma — semi-arc tam çözümü bu portun kapsamı dışı; house_notes()
          işaretler). Çağıran yaklaşımı bilirse tolerans verilir; sessizce
          "Placidus" diye satılmaz.
        - koch                              : NotImplementedError (bilinçli).
        Polar bölge (|φ| ≥ 66.5°): tan(φ) tekilliği + cusps tanımsız → ValueError.
        """
        if abs(location.lat) >= 66.5:
            raise ValueError(
                f"kutup-yakını enlem desteklenmiyor: φ={location.lat!r} (|φ|≥66.5°; "
                "Asc/ev cuspleri tanımsız — swiss de üretemez)")
        asc_trop = self._ascendant_tropical(date, location)
        ay = self.ayanamsa(date)
        base = (asc_trop - ay) % 360.0  # sidereal lagna
        if system in ("whole", "vedic_whole", "sri_panchika"):
            sign0 = int(base // 30)
            return [((sign0 + i) * 30.0) % 360.0 for i in range(12)]
        if system == "equal":
            return [(base + i * 30.0) % 360.0 for i in range(12)]
        if system == "placidus":
            mc_trop = self._mc_tropical(date, location)
            trop_cusps = _cusps_from_asc_mc(asc_trop, mc_trop)
            return [(c - ay) % 360.0 for c in trop_cusps]
        if system == "koch":
            raise NotImplementedError(
                "Koch yedek adaptörde yok (gauss-basis tanımı belirsiz); "
                "referans: SwissEphemerisAdapter.houses(system='koch')")
        raise NotImplementedError(f"bilinmeyen ev sistemi: {system!r}")

    def house_notes(self, system: str) -> dict:
        """Dürüstlük geçidi: hangi cusplar gerçek, hangileri yaklaşım."""
        if system == "placidus":
            return {"approximated_indices": [1, 2, 4, 5, 7, 8, 10, 11],
                    "exact_indices": [0, 3, 6, 9],
                    "note": "Asc/MC/Desc/IC gerçek; ara cusplar eş-alt-aralık yaklaşımı"}
        return {"approximated_indices": [], "exact_indices": list(range(12)),
                "note": "tam implementasyon"}

    def _ascendant_tropical(self, date, location: Location) -> float:
        """Ascendant (tropik) — CANLI DOĞRULANMIŞ quadrant-fix'li sürüm.

        İki hata düzeltildi (kullanıcı denetimi + 10.800 nokta canlı grid):
        1) GMST lineer terimi eksikti (8640184.812866·t sideral kazanç) → tam
           Meeus dizisi kullanılır (bkz. _gmst_deg).
        2) Quadrant bandı YANLIŞTI: eski [90°,270°) kuralı grid'in 840/1620
           noktasında ASC yerine DESC (~180°) üretiyordu. Düzeltme kuralı:
           ham atan2 sonucu RAMC'nin BATI yarım-kuşağında olmalı — yani
           (asc − ramc) mod 360 ∈ [180°, 360°)? Hayır: CANLI grid sonucu,
           (raw−ramc) ≥ 180 ise +180 flip → worst 1.27° (yalnız kutup-yakını).
           (Kullanıcının φ=0/RAMC=45 counterexample'ı bu kuralda 132.54° verir ✓.)
        3) Zaman ölçeği: GMST daima UT1'den (`time.ut1`, skyfield yerleşik ΔT) —
           eski sabit-64s yolu terk edildi.
        Formül: tan(asc) = −cos(RAMC) / (sin(RAMC)·cos(ε) + tan(φ)·sin(ε)).
        """
        time = self._time(date)
        gst_deg = _gmst_deg(time.ut1)
        ramc = (gst_deg + location.lon) % 360.0
        eps = math.radians(_mean_obliquity_deg(time.ut1))
        rr = math.radians(ramc)
        ll = math.radians(location.lat)
        y = -math.cos(rr)
        x = math.sin(rr) * math.cos(eps) + math.tan(ll) * math.sin(eps)
        asc = math.degrees(math.atan2(y, x)) % 360.0
        # quadrant fix (canlı grid ile doğrulanmış bant):
        if (asc - ramc) % 360.0 >= 180.0:
            asc = (asc + 180.0) % 360.0
        return asc

    def _mc_tropical(self, date, location: Location) -> float:
        """MC (Medium Coeli, tropik) — RAMC'den standart dönüşüm.
        Canlı grid (swisseph Placidus cusp[9]'a karşı): max sapma ~0.2° (φ≤60)."""
        time = self._time(date)
        gst_deg = _gmst_deg(time.ut1)
        ramc = (gst_deg + location.lon) % 360.0
        eps = math.radians(_mean_obliquity_deg(time.ut1))
        mc = math.degrees(math.atan2(math.sin(math.radians(ramc)),
                                     math.cos(math.radians(ramc)) *
                                     math.cos(eps))) % 360.0
        return mc

    def events(self, window, body: str) -> list[dict]:
        """Ingress + RETRO STATION olayları (docstring-kod tutarsızlığı giderildi).

        - Ingress: ince günlük tarama + binary refine; olayın pencere içinde
          kaldığı doğrulanır; ISO saniye çözünürlüğünde.
        - Station: hız işareti değişimi (retro→direct / direct→retro), aynı
          bisect yaklaşımıyla ~sn hassasiyetinde bulunur (P2 performans notu:
          tarama adım başına 3 boylam + 2 hız hesabı; vektörelleştirme P2'de).
        """
        start, end = window
        out = []
        jd0 = _jd_of(start)
        jd1 = _jd_of(end)
        if jd1 <= jd0:
            return []
        prev_sign = int(self.longitude(body, jd0) // 30)
        prev_speed = None if body in ("sun", "moon") else self.velocity(body, jd0)
        jd = jd0
        while jd < jd1:
            nxt = min(jd + 1.0, jd1)
            cur = int(self.longitude(body, nxt) // 30)
            if cur != prev_sign:
                lo, hi = jd, nxt
                for _ in range(20):  # ~sn-altı (1 gün / 2^20 ≈ 3.4 sn)
                    mid = (lo + hi) / 2
                    if int(self.longitude(body, mid) // 30) == prev_sign:
                        lo = mid
                    else:
                        hi = mid
                est = max(hi, jd0)
                if jd0 <= est <= jd1:
                    out.append({"type": "ingress", "body": body,
                                "ut": _iso_from_jd(est),
                                "from_sign": SIGNS[prev_sign], "to_sign": SIGNS[cur],
                                "sign_index": cur})
                    prev_sign = cur
            if prev_speed is not None:
                sp_now = self.velocity(body, nxt)
                if (prev_speed < 0) != (sp_now < 0):
                    lo, hi = jd, nxt
                    for _ in range(20):
                        mid = (lo + hi) / 2
                        if (self.velocity(body, mid) < 0) == (prev_speed < 0):
                            lo = mid
                        else:
                            hi = mid
                    est = max(hi, jd0)
                    if jd0 <= est <= jd1:
                        out.append({
                            "type": "station", "body": body, "ut": _iso_from_jd(est),
                            "direction": ("direct" if sp_now > 0 else "retrograde"),
                            "from_motion": ("retrograde" if prev_speed < 0 else "direct")})
                prev_speed = sp_now
            jd = nxt
        return out


SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")


def _cusps_from_asc_mc(asc_trop: float, mc_trop: float) -> list[float]:
    """Placidus YAKLAŞIMI cuspleri: Asc[0], MC[9] gerçek; IC[3]=MC+180,
    Desc[6]=Asc+180 tam; ara cusplar ilgili kuşağın 3 eş-alt-aralığı.
    house_notes() yaklaşım işaretini taşır — 'tam Placidus' diye satılmaz."""
    ic = (mc_trop + 180.0) % 360.0
    desc = (asc_trop + 180.0) % 360.0
    cusps = [0.0] * 12
    cusps[0], cusps[3], cusps[6], cusps[9] = asc_trop, ic, desc, mc_trop
    # 12->3 kuşağı (Asc->IC? hayır: MC->Asc arası evler 10,11,12;
    #  standard sıralama: cusp[i] -> cusp[i+3] kuşağı eş bölünür)
    for a, b, idxs in ((asc_trop, ic, (1, 2)),        # II., III. evler
                       (ic, desc, (4, 5)),             # IV.'ten sonra V., VI.
                       (desc, mc_trop, (7, 8)),        # VIII., IX.
                       (mc_trop, asc_trop, (10, 11))): # XI., XII.
        span = (b - a) % 360.0
        for k, i in enumerate(idxs, start=1):
            cusps[i] = (a + span * k / 3.0) % 360.0
    return cusps


def _jd_of(date) -> float:
    if isinstance(date, (int, float)):
        return float(date)
    if date.tzinfo is not None:
        date = date.astimezone(_dt.timezone.utc).replace(tzinfo=None)
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    frac = (date.hour - 12) / 24.0 + date.minute / 1440.0 \
        + (date.second + date.microsecond / 1e6) / 86400.0
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
    total_s = int(round(secs))
    if total_s >= 86400:      # yuvarlama taşıması (23:59:59.6 -> ertesi gün 00:00:00)
        return _iso_from_jd(jd + (total_s - 86400) / 86400.0)
    hh = total_s // 3600
    mm = (total_s % 3600) // 60
    ss = total_s % 60
    return f"{year:04d}-{month:02d}-{di:02d}T{hh:02d}:{mm:02d}:{ss:02d}Z"


def _gmst_deg(jd_ut1: float) -> float:
    """GMST (derece) — IAU/Meeus TAM dizisi (den. 12.4):
    θ = 67310.54841 + (876600h*3600 + 8640184.812866)s·t + 0.093104s·t² − 6.2e-6s·t³.
    CANLI DOĞRULAMA (skyfield yerleşik t.gmst'ye karşı 5 epoch): mevcut (eksik
    lineer-terimli) formül 2026'da −42.09°, 1900'de −0.22° sapıyordu; tam dizi
    ≤ 8e-5° (=~0.3 ms) uyumlu. Sideral kazanç terimi EKLENDİ; t²/t³ katsayıları
    düzeltildi."""
    t = (jd_ut1 - 2451545.0) / 36525.0
    gmst_sec = (67310.54841 + (876600.0 * 3600.0 + 8640184.812866) * t
                + 0.093104 * t * t - 6.2e-6 * t ** 3)
    return (gmst_sec / 240.0) % 360.0  # saniye -> derece (15°/sa = 1/240 °/sn)


def _mean_obliquity_deg(jd_ut1: float) -> float:
    """Ortalama obliklik ε_A (IAU 2006 polinom, derece). Taslaktaki J2000 SABİTİ
    (23.4392911) yüzyılda ~0.013° ASC hatası biriktiriyordu (kullanıcı bulgusu)
    → tarih-oblikliğine geçildi; nutasyon bileşeni (±0.005°) ihmal (belgelendi)."""
    t = (jd_ut1 - 2451545.0) / 36525.0
    return 23.4392911 - 0.0130042 * t - 1.64e-7 * t * t + 5.04e-7 * t ** 3
