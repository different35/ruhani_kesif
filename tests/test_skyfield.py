"""P1-8: SkyfieldAdapter doğrulama testleri (Swiss referanslı, canlı ölçümlü).

Strateji — TEK DOĞRU KAYNAK sözleşmesi her iki adaptörde de
sid = trop − ayanamsa olduğundan, referans "derived source" ile alınır:
    swiss_ref_sid = (swe.calc_ut(...)[0] − swe.get_ayanamsa_ut(jd)) % 360
Bu, FLG_SIDEREAL epoch düzeltmesi tuzağını (swiss longitude() da türetilmiş
kullanıyor — bkz. swiss_adapter yorumu) elemine eder; ölçülen fark gerçek
model farkıdır.

swisseph YALNIZCA test/dev bağımlılığıdır (lisans temizliği maddesi):
ticari build'de bu testler çalışmaz; engine/skyfield_adapter runtime'ı
swisseph İMPORT ETMEZ (grep CI kontrolü: ROADMAP P1-8 kapanış kriteri).
"""
import datetime as dt

import pytest

swe = pytest.importorskip("swisseph")

from engine.ephemeris_port import Location
from engine.skyfield_adapter import SkyfieldAdapter

UTC = dt.timezone.utc
J2000 = dt.datetime(2026, 1, 1, 12, tzinfo=UTC)
# J2026: takvim etiketi — modülde tüm "J2000" adlı datetime'ler aslında
# 2026-01-01 12:00 UTC'dir (JD2026 ile aynı an). Eksik tanımdan doğan
# NameError düzeltildi (canlı test bulgusu, bu oturum).
J2026 = J2000
JD2026 = swe.julday(2026, 1, 1, 12.0)

PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
SWE_FL = {"sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
          "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
          "saturn": swe.SATURN}


@pytest.fixture(scope="module")
def sk():
    return SkyfieldAdapter("lahiri")


def _circ_diff(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


# ---------------------------------------------------------------- ayanamsa --
@pytest.mark.parametrize("mode,sidm", [
    ("lahiri", swe.SIDM_LAHIRI),
    ("raman", swe.SIDM_RAMAN),
    ("kp", swe.SIDM_KRISHNAMURTI),
    ("fagan_bradley", swe.SIDM_FAGAN_BRADLEY),
])
def test_ayanamsa_modes_against_swiss(mode, sidm):
    """Kuadratik fit'ler swiss çıktısına birebir oturmalı (<1e-5°)."""
    swe.set_sid_mode(sidm)
    ref = swe.get_ayanamsa_ut(JD2026)
    got = SkyfieldAdapter(mode).ayanamsa(J2026)
    assert abs(ref - got) < 1e-5, f"{mode}: swiss={ref} skyfield={got}"


def test_ayanamsa_default_uses_object_mode(sk):
    """Denetim bulgusu P1-2 port karşılığı: mode=None nesnenin modunu döner;
    nesne 'raman' ise varsayılan Lahiri DEĞİL Raman olmalı."""
    r = SkyfieldAdapter("raman")
    swe.set_sid_mode(swe.SIDM_RAMAN)
    assert abs(r.ayanamsa(J2000) - swe.get_ayanamsa_ut(JD2026)) < 1e-5
    # açık mod geçişi nesneden bağımsız çalışır
    assert abs(sk.ayanamsa(J2000, mode="kp") - r.ayanamsa(J2000, mode="kp")) < 1e-9


def test_ayanamsa_unknown_mode_raises(sk):
    with pytest.raises(ValueError):
        sk.ayanamsa(J2000, mode="yulek")
    with pytest.raises(ValueError):
        SkyfieldAdapter("bogus")


def test_ayanamsa_stateless_no_global_mutation(sk):
    """Skyfield tarafında global sid-mode yoktur; ardışık farklı-mod çağrıları
    birbirini etkilemez (swiss'teki yarış koşulu burada yapısal olarak yok)."""
    a1 = sk.ayanamsa(J2000)
    _ = SkyfieldAdapter("raman").ayanamsa(J2000)
    assert sk.ayanamsa(J2000) == a1


# --------------------------------------------------------------- longitude --
def test_longitude_sidereal_derived_source_parity(sk):
    """7 gezegen: |Δ| ≤ 0.02° (canlı ölçüm max ~0.012°; tolerans paylı)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ay = swe.get_ayanamsa_ut(JD2026)
    for b in PLANETS:
        ref = (swe.calc_ut(JD2026, SWE_FL[b])[0][0] - ay) % 360.0
        got = sk.longitude(b, J2000)
        assert _circ_diff(got, ref) <= 0.02, f"{b}: {got} vs {ref}"


def test_longitude_tropical_frame(sk):
    """Tropik çerçeve: ayanamsa düşülmez; swiss tropikle ≤0.02° (güneş/ay hızlı
    olduğundan zamanlama hassasiyeti aynı JD'de test edilir)."""
    for b in PLANETS:
        ref = swe.calc_ut(JD2026, SWE_FL[b])[0][0]
        got = sk.longitude(b, JD2026, frame="tropical")  # JD girdisi UT
        assert _circ_diff(got, ref) <= 0.02, b


def test_longitude_rejects_bad_frame_body(sk):
    with pytest.raises(ValueError):
        sk.longitude("sun", J2000, frame="sidereal ")   # sessiz tropik kaçağı yok
    with pytest.raises(ValueError):
        sk.longitude("vulcan", J2000)


def test_rahu_mean_node_parity_and_retrograde(sk):
    """Mean node: Meeus Ω swiss MEAN_NODE ile ≤0.01° (TT sözleşmesi); daima
    retrograd (hız ≈ −0.05295°/gün) — taslakta hız 0.0 → is_retrograde False'ydu."""
    res_n = swe.calc_ut(JD2026, swe.MEAN_NODE)[0][0]
    got = sk.longitude("rahu_mean", J2000, frame="tropical")
    assert _circ_diff(got, res_n) <= 0.01
    assert sk.is_retrograde("rahu_mean", J2000) is True
    assert sk.velocity("rahu_mean", J2000) < 0
    # ketu = rahu + 180
    k = sk.longitude("ketu_mean", J2000, frame="tropical")
    assert _circ_diff(k, (res_n + 180.0) % 360.0) <= 0.01


# ------------------------------------------------------------------ scope --
def test_scope_guard_out_of_range_raises(sk):
    old = dt.datetime(1800, 1, 1, tzinfo=UTC)     # de440s ~1849-2150 dışında
    with pytest.raises(ValueError):
        sk.longitude("sun", old)
    future = dt.datetime(2199, 1, 1, tzinfo=UTC)
    with pytest.raises(ValueError):
        sk.ayanamsa(future)


# ------------------------------------------------------------------ houses --
IST = Location(lat=41.0082, lon=28.9784, tz_offset_hours=0.0)


def test_houses_whole_sign_exact_parity(sk):
    from engine.swiss_adapter import SwissEphemerisAdapter
    sw = SwissEphemerisAdapter("lahiri")
    w_sw = sw.houses(J2000, IST, "whole")
    w_sk = sk.houses(J2000, IST, "whole")
    for i, (a, b) in enumerate(zip(w_sw, w_sk)):
        assert _circ_diff(a, b) <= 0.02, f"cusp{i+1}: {a} vs {b}"


def test_houses_asc_mc_within_tolerance(sk):
    """Asc/MC: quadrant-fix'li Meeus formülü swiss Placidus'a karşı canlı
    ölçümde İstanbul'da ≤0.4° (grid taraması worst ~1.3° @|φ|=60)."""
    from engine.swiss_adapter import SwissEphemerisAdapter
    sw = SwissEphemerisAdapter("lahiri")
    h_sw = sw.houses(J2000, IST, "placidus")
    h_sk = sk.houses(J2000, IST, "placidus")
    assert _circ_diff(h_sw[0], h_sk[0]) <= 0.5      # Asc
    assert _circ_diff(h_sw[9], h_sk[9]) <= 0.5      # MC
    assert _circ_diff(h_sw[3], h_sk[3]) <= 0.5      # IC
    assert _circ_diff(h_sw[6], h_sk[6]) <= 0.5      # Desc
    # ara cusplar YAKLAŞIM — house_notes bunu itiraf etmeli (dürüstlük geçidi)
    notes = sk.house_notes("placidus")
    assert set(notes["exact_indices"]) == {0, 3, 6, 9}
    assert 4 in notes["approximated_indices"]       # cusp5 ±10° civarı sapabilir


def test_houses_koch_not_implemented_and_polar_valueerror(sk):
    with pytest.raises(NotImplementedError):
        sk.houses(J2000, IST, "koch")
    with pytest.raises(NotImplementedError):
        sk.houses(J2000, IST, "regiomontanus")
    polar = Location(lat=69.0, lon=25.0)
    with pytest.raises(ValueError):
        sk.houses(J2000, polar, "placidus")


# ------------------------------------------------------------------ events --
def test_events_ingress_reference(sk):
    """Canlı çıkarılan referans: Lahiri sid. Güneş 2026-03-14 Kumbha→Meena ve
    2026-04-14 Meena→Mesha (pencerede 2 gerçek geçiş)."""
    evs = sk.events((dt.datetime(2026, 3, 1, tzinfo=UTC),
                     dt.datetime(2026, 4, 15, tzinfo=UTC)), "sun")
    assert len(evs) == 2
    assert evs[0]["ut"].startswith("2026-03-14")
    assert (evs[0]["from_sign"], evs[0]["to_sign"]) == ("Aquarius", "Pisces")
    assert evs[1]["ut"].startswith("2026-04-14")
    assert (evs[1]["from_sign"], evs[1]["to_sign"]) == ("Pisces", "Aries")


def test_events_station_detected(sk):
    """Retro station docstring-kod tutarsızlığı giderildi: Merkür 2026-02-26
    civarı durağanlık (retro→direct) penceresinde olay üretilmeli."""
    evs = sk.events((dt.datetime(2026, 2, 20, tzinfo=UTC),
                     dt.datetime(2026, 3, 6, tzinfo=UTC)), "mercury")
    stations = [e for e in evs if e["type"] == "station"]
    assert len(stations) >= 1
    # swiss referansı: hız işareti değişimi aynı gün içinde.
    # DÜZELTME (canlı bulgu): pyswisseph 2.10 `calc_ut` tek cisimde düz liste
    # döndürür — `[1][0]` TypeError üretiyordu; doğru indeksleme `[0][3]`.
    jd = swe.julday(2026, 2, 26, 0.0)
    sp_before = swe.calc_ut(jd - 1.0, swe.MERCURY)[0][3]
    sp_after = swe.calc_ut(jd + 1.0, swe.MERCURY)[0][3]
    assert (sp_before < 0) != (sp_after < 0), "swiss referansında işaret değişimi yok"
    # gerçek iddia: istasyon olayının tarihi swiss hız işareti değişimiyle uyumlu
    st = stations[0]["ut"][:10]
    jd_st = swe.julday(*map(int, st.split("-")), 0.0)
    assert (swe.calc_ut(jd_st - 1.0, swe.MERCURY)[0][3] < 0) \
        != (swe.calc_ut(jd_st + 1.0, swe.MERCURY)[0][3] < 0)
