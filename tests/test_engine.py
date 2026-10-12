"""P1 çıkış ölçütü çekirdeği (gist §12.1): sayısal doğruluk + çerçeve ayrımı.

Golden değerler bağımsız referanslarla sabitlendi (bu oturumda canlı doğrulandı):
- Lahiri ayanamsa @ J2000 = 23.8571° (swisseph SIDM_LAHIRI)
- sid == (trop - ayanamsa) mod 360 — TEK DOĞRU KAYNAK kuralı
"""
import datetime as dt
import pytest
import swisseph as swe

from engine.swiss_adapter import SwissEphemerisAdapter
from engine.ephemeris_port import Location
from engine.nakshatra import nakshatra_pada, NAKSHATRAS
from engine.dasha import vimshottari, balance_years, YEARS

UTC = dt.timezone.utc
J2000 = dt.datetime(2000, 1, 1, 12, tzinfo=UTC)


@pytest.fixture(scope="module")
def adapter():
    return SwissEphemerisAdapter("lahiri")


def test_ayanamsa_lahiri_j2000(adapter):
    assert abs(adapter.ayanamsa(J2000) - 23.8571) < 1e-3


def test_single_source_of_truth(adapter):
    """Çerçeve ayrımı testi (P1 çıkış ölçütü): her gezegen için sid=trop-ay."""
    for body in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"):
        sid = adapter.longitude(body, J2000, "sidereal")
        trop = adapter.longitude(body, J2000, "tropical")
        ay = adapter.ayanamsa(J2000)
        assert abs((trop - ay) % 360 - sid) < 1e-9, body


def test_rahu_ketu_opposite(adapter):
    r = adapter.longitude("rahu_mean", J2000)
    k = adapter.longitude("ketu_mean", J2000)
    assert abs(((r - k) % 360) - 180.0) < 1e-9


def test_houses_count_and_range(adapter):
    cusps = adapter.houses(J2000, Location(41.0, 29.0))
    assert len(cusps) == 12
    assert all(0 <= c < 360 for c in cusps)


def test_nakshatra_boundaries():
    assert nakshatra_pada(0.0)["nakshatra"] == "Ashwini"
    assert nakshatra_pada(0.0)["pada"] == 1
    assert nakshatra_pada(360.0 / 27)["nakshatra_index"] == 1   # tam sınır -> sonraki
    assert nakshatra_pada(359.999)["nakshatra"] == "Revati"
    np_ = nakshatra_pada(199.4667)                               # J2000 Ay'ı
    assert (np_["nakshatra"], np_["pada"]) == ("Swati", 4)


def test_dasha_balance_swati():
    # Swati Rahu lordudur; Ay 19.4667 Libra = Swati span 186.667..200 -> kalan ~0.72 yıl
    rem, lord = balance_years(199.4667, None)
    assert lord == "Rahu" and 0.6 < rem < 0.8


def test_dasha_timeline_shape(adapter):
    moon = adapter.longitude("moon", J2000)
    tl = vimshottari(moon, swe.julday(2000, 1, 1, 12.0))
    assert len(tl) == 81                       # balance ile birleşen ilk MD + 9 tam MD
    assert tl[0]["mahadasha"] == "Rahu" and tl[0]["antardasha"] != "Rahu"
    # Rahu-Mercury AD'si doğumda zaten bitmiş -> timeline'a girmemeli
    assert not any(n["mahadasha"] == "Rahu" and n["antardasha"] == "Mercury" for n in tl)
    # süre tutarlılığı: AD yılları toplamı ≈ MD yılları
    rah_md = [n for n in tl if n["mahadasha"] == "Rahu"]
    assert abs(sum(n["years"] for n in rah_md) - YEARS["Rahu"]) < 0.05


def test_events_ingress_reference(adapter):
    """Canlı çıkarılan referans: Lahiri sid. Güneş 2026-03-14 Kumbha->Meena."""
    evs = adapter.events((dt.datetime(2026, 3, 1, tzinfo=UTC),
                          dt.datetime(2026, 4, 15, tzinfo=UTC)), "sun")
    assert len(evs) == 1
    assert evs[0]["from_sign"] == "Aquarius" and evs[0]["to_sign"] == "Pisces"
    assert evs[0]["ut"].startswith("2026-03-14")
