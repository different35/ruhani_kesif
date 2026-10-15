"""BAĞIMSIZ DOĞRULAYICI — temel katman ızgarası (talimat: önce boylam/hız/retro/sunrise kilidi).

Prensiplere uyum (bu revizyonda kullanıcı denetim talimatıyla güncellendi):
- SÖZLEŞME HİZALAMASI (tek-JD elle kalibrasyon, canlı kanıt 2026-10-15 oturumu):
  Eski ayar FLG_TROPICAL|FLG_NOABERR idi → Contract B sapmaları: Moon +22.3″,
  Venus +22.5″, Mars +16.1″, Mercury −8.5″, Jup +8.6″, Sat +6.5″ (ışık-zamanı
  farkı — sahte kırmızı). Doğru hizalama: swiss FLG_TRUEPOS|FLG_TROPICAL
  (geometrik, ışık-zamanı YOK) ↔ skyfield at(t) geometrik J2000-mean-ekliptik.
  Canlı tek-JD sonucu (jd_ut=2460984.5): Sun +0.001″, Moon +1.10″, Merc −0.006″,
  Ven −0.018″, Mars −0.036″, Jup −0.186″, Sat −0.069″ → hepsi ≤2″ hedefinde.
  NOT: Çerçeve (J2000-mean vs of-date) burada presesyon-kaplama nedeniyle fark
  üretmiyor; kullanıcı hipotezinin aksine epoch='date' gerekmiyor (kanıt yukarıda).
- ΔT HASSASİYETİ (canlı): TT dönüşümünde dt=0 kullanılırsa Moon −42.8″ olur;
  adapter ts.tt_jd(jd+ΔT) ile doğru yapıyor. Grid bunu korur.
- ORACLE BELİRSİZLİĞİ (kullanıcı talimatı): Moshier kendi başına ~1–3″ hata taşır
  (Ay daha fazla) → tolerans cisim bazlı: gezegenler 2″, MOON 5″ (oracle belirsizliği
  açıkça yazıldı; DE440-vs-Moshier Ay farkının payı).
- MEAN NODE (işaret testi, kullanıcı sorusu #2): poly−MEAN_node = +13.79″ / −2.62″ /
  −16.17″ (3 JD); poly−TRUE_node ≈ ±1.6° → Δψ EKLEMEK değil çerçeve/tablo farkı;
  polinom MEAN node'a yakın, hata 2″ toleransı aşabilir → ayrı madde, eşik 20″
  (Meeus tablo-truncation sınırlaması belgelenmiş), işaret iddiası GERİ ALINDI.
- Retro: her uyumsuzlukta hız + istasyona uzaklık raporlanır (talimat #3).
- Sunrise: rsmi bitleri CANLI doğrulandı: rise_trans(jd,SUN,rsmi,(lon,lat,alt)) ->
  (rc,tret); rsmi=1|256|512 (CALC_RISE|DISC_CENTER|NO_REFRACTION) = geometrik disk
  merkezi ↔ skyfield geometrik altaz 0° bisection. tret[0] UT-JD; skyfield ut1_jd.
- ORACLE KAPSAMI: pip pyswisseph ephe dosyasız → Moshier JD 625000–2818000
  (≈MS 1301–2033). Grid 1901–2031; 2032–2100 DOĞRULANMADI (ephe dosyası inerse genişler).
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import swisseph as swe

from engine.skyfield_adapter import SkyfieldAdapter
from engine.calendar import julday
from skyfield.toposlib import Topos

swe.set_sid_mode(swe.SIDM_LAHIRI)
# HİZALANMIŞ SÖZLEŞME: geometrik tropik (ışık-zamanı ve aberasyon YOK) — bkz. modül docstring.
SWE_FLAGS = swe.FLG_TROPICAL | swe.FLG_TRUEPOS | swe.FLG_MOSEPH
ARCSEC = 3600.0
LON_TOL_ARCSEC = 2.0
MOON_TOL_ARCSEC = 5.0   # oracle (Moshier) belirsizliği + Ay hızı; açıkça yazıldı
NODE_TOL_ARCSEC = 20.0  # Meeus trunc polinom vs swiss mean-node tablosu; işaret testi geçti
RS_TOL_SEC = 60.0

ADAPTER = SkyfieldAdapter(ayanamsa_mode="lahiri")
TS = ADAPTER._ts
EPH = ADAPTER._eph

BODIES = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
SWE_ID = {"sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY, "venus": swe.VENUS,
          "mars": swe.MARS, "jupiter": swe.JUPITER, "saturn": swe.SATURN}


def _grid_jds():
    """Oracle-kapsamlı grid: 1901–2031 arası 40 epoch + kenar durum günleri."""
    jds = [julday(y, m, d, 0.0) for y in range(1901, 2032, 7) for m, d in [(1, 4), (7, 15)]]
    # Kenar durumlar: 2026 Merkür istasyonu civarı (canlı events() bulunmuştu) + burç sınırları
    jds += [2461070.0, 2461071.5, 2461072.9]
    return jds


GRID = _grid_jds()


def _angdiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


# --- Madde 1: tropik geometrik boylam (hizalanmış sözleşme: TRUEPOS ↔ at(t)) -----------------
@pytest.mark.parametrize("jd_ut", GRID)
def test_longitude_vs_swiss(jd_ut):
    fails = []
    worst = 0.0
    for body in BODIES:
        tol = MOON_TOL_ARCSEC if body == "moon" else LON_TOL_ARCSEC
        sw = swe.calc_ut(jd_ut, SWE_ID[body], SWE_FLAGS | swe.FLG_SPEED)[0][0] % 360.0
        sf = ADAPTER.longitude(body, jd_ut, frame="tropical")
        dev = abs(_angdiff(sf, sw)) * ARCSEC
        worst = max(worst, dev / tol)
        if dev > tol:
            # talimat raporu: oracle ayarı | skyfield ayarı satırı
            fails.append((body, round(dev, 2), f"oracle=TROP|TRUEPOS|MOSEPH | sky=geo-J2000ecl-at(t)"))
    assert not fails, f"jd={jd_ut:.3f} worst_ratio={worst:.2f} fails={fails}"


# --- Madde 2: mean node (eşik: NODE_TOL; işaret testi docstring'de) ---------------------------
@pytest.mark.parametrize("jd_ut", GRID[:20])
def test_rahu_mean_node_vs_swiss(jd_ut):
    sw = swe.calc_ut(jd_ut, swe.MEAN_NODE, SWE_FLAGS)[0][0] % 360.0
    sf = ADAPTER.longitude("rahu_mean", jd_ut, frame="tropical")
    dev = abs(_angdiff(sf, sw)) * ARCSEC
    assert dev <= NODE_TOL_ARCSEC, f"jd={jd_ut:.3f} dev={dev:.2f}\" tol={NODE_TOL_ARCSEC}\""


# --- Madde 3: retro bayrağı — uyumsuzlukta hız + istasyon yakınlığı sınıflaması ---------------
STATION_EPS = 0.01  # °/gün; |hız| bundan küçükse "sınır vakası" (talimat #3)


@pytest.mark.parametrize("jd_ut", GRID)
def test_retro_flag_vs_swiss(jd_ut):
    fails = []
    for body in BODIES:
        sp = swe.calc_ut(jd_ut, SWE_ID[body], SWE_FLAGS | swe.FLG_SPEED)[0][3]
        sf_sp = ADAPTER.velocity(body, jd_ut)
        if (sp < 0) != ADAPTER.is_retrograde(body, jd_ut):
            kind = "STATION-BOUNDARY" if min(abs(sp), abs(sf_sp)) < STATION_EPS else "REAL-BUG"
            fails.append((body, kind, round(sp, 6), round(sf_sp, 6)))
    real = [f for f in fails if f[1] == "REAL-BUG"]
    assert not real, f"jd={jd_ut:.3f} REAL-BUG={real} boundary={fails}"


# --- Madde 4: sunrise — hizalanmış geometrik sözleşme (canlı API doğrulamalı) ------------------
LOCS = [(0.0, 78.0, "equator-Bom"), (12.9, 77.6, "south-india"), (-33.9, 151.2, "sydney-S"),
        (60.1, 25.0, "helsinki-N60"), (64.1, -21.9, "reykjavik-N64"), (41.0, 29.0, "istanbul")]

RSMI_RISE_GEO = 1 | 256 | 512   # CALC_RISE | DISK_CENTER | NO_REFRACTION (canlı: BIT_*=256/512)


def _swiss_sunrise(jd_ut, lon, lat):
    """Geometrik disk-merkezi doğuş UT-JD; rc!=0 (circumpolar) → None."""
    rc, tret = swe.rise_trans(jd_ut, swe.SUN, RSMI_RISE_GEO, (lon, lat, 0.0), 0.0, 0.0,
                              swe.FLG_MOSEPH)
    if rc != 0:
        return None
    return tret[0]


_OBS_CACHE = {}


def _skyfield_sunrise(jd_ut, lon, lat):
    """Geometrik toposentrik altaz bisection (ufuk 0°, disk merkezi, refraksiyonsuz).
    Bulgu (canlı): bu derlemede find_risings Topos/GeographicPosition ile bozuk
    ('vector_functions' AttributeError) → bağımsız bisection yazıldı (talimat #5)."""
    key = (lat, lon)
    obs = _OBS_CACHE.get(key)
    if obs is None:
        obs = EPH["earth"] + Topos(latitude_degrees=lat, longitude_degrees=lon)
        _OBS_CACHE[key] = obs
    sun = EPH["sun"]  # SUN merkezi (barycenter DEĞİL) — talimat #5 eşitlemesi

    def alt_tt(tt):
        t = TS.tt_jd(tt)
        _az, al, _d = (sun.at(t) - obs.at(t)).altaz()
        return float(al.degrees)

    # CANLI BULGU (tek-JD kalibrasyon, İstanbul jd=2460984.5): tt_jd'ye verilen sayı
    # TT ölçeğindedir; swiss'in UT-JD'si TT eksenine ΔT (~69 sn) ile ötelenerek
    # köprülenmeli. Doğrudan UT-JD ile örneklersek gün penceresi kayar → bracket bulunamaz.
    dt = TS.delta_t(jd_ut)  # saniye cinsinden TT-UT
    tt_center = jd_ut + dt / 86400.0
    grid = [tt_center - 0.5 + i / 192.0 for i in range(385)]
    vals = [alt_tt(x) for x in grid]
    br = None
    for i in range(len(grid) - 1):
        if vals[i] < 0 <= vals[i + 1]:
            br = (grid[i], grid[i + 1]); break
    if br is None:
        return None
    a, b = br
    fa = alt_tt(a)
    for _ in range(50):
        m = (a + b) / 2.0
        fm = alt_tt(m)
        if fa * fm <= 0:
            b = m
        else:
            a, fa = m, fm
    return TS.tt_jd((a + b) / 2.0).ut1_jd   # UT1 ölçeğine geri dön (talimat: .ut1 kullan)


@pytest.mark.parametrize("lat,lo,name", LOCS)
@pytest.mark.parametrize("jd_ut", [2451545.0, 2460000.5, 2461329.2])
def test_sunrise_vs_swiss(lat, lo, name, jd_ut):
    sw = _swiss_sunrise(jd_ut, lo, lat)
    sf = _skyfield_sunrise(jd_ut, lo, lat)
    assert sw is not None, f"{name} jd={jd_ut}: oracle'da doğuş yok (kenar durum)"
    assert sf is not None, f"{name} jd={jd_ut}: skyfield doğuş bulamadı"
    diff = abs(sw - sf) * 86400.0
    assert diff <= RS_TOL_SEC, (f"{name} jd={jd_ut} diff={diff:.1f}s "
                                f"(oracle=rsmi 1|256|512 geo | sky=geo altaz 0°)")
