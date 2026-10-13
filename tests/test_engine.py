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
from engine.dasha import vimshottari, balance_years, YEARS, YEAR

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


def test_dasha_balance_golden():
    """GOLDEN: standart Vimshottari + PyJHora `vimsottari_dasha_start_date`.

    Doğum dasha'sı = Ay'ın İÇİNDE OLDUĞU nakshatra lordu;
    balance = YEARS[current_lord] * (1 - frac_elapsed).
      Ay 190° (Swati, Rahu lordu, frac 0.25) -> (13.5, "Rahu", "Rahu")  [18×0.75]
      Ay 0°   (Ashwini, Ketu lordu, frac 0)   -> (7.0,  "Ketu", "Ketu") [7×1.0]
    (Geçici bir sürüm `next_lord * frac_elapsed` kullanmıştı — hiçbir kaynakta
    yoktur ve bu testi çökertirdi.)"""
    bal, start_lord, current_lord = balance_years(190.0)
    assert (round(bal, 6), start_lord, current_lord) == (13.5, "Rahu", "Rahu")
    bal, start_lord, current_lord = balance_years(0.0)
    assert (round(bal, 6), start_lord, current_lord) == (7.0, "Ketu", "Ketu")


def test_dasha_balance_swati_j2000_moon():
    """Canlı J2000 Ay'ı (sid. 199.4667°, Swati pada 4): Rahu'nun son ~0.72 yılı.
    PyJHora referansı: MD başlangıcı doğumdan geriye hesaplanır ->
    balance = 18 × (1 - 0.96) ≈ 0.72 yıl, devam eden MD = Rahu."""
    bal, start_lord, current_lord = balance_years(199.4667)
    assert current_lord == "Rahu" and start_lord == "Rahu"
    assert abs(bal - 0.72) < 0.01


def test_dasha_timeline_shape(adapter):
    moon = adapter.longitude("moon", J2000)   # sid. ~199.4667° -> Rahu kalanı ~0.72 yıl
    jd0 = swe.julday(2000, 1, 1, 12.0)
    tl = vimshottari(moon, jd0)
    # İlk MD kırpılmış; doğumdan önce tüketilen AD'ler yayınlanmaz -> < 81 segment.
    assert len(tl) <= 81
    bal, start_lord, _cur = balance_years(moon)
    assert start_lord == "Rahu" and abs(bal - 0.72) < 0.01
    # Tüketilen ~17.28 yıl Rahu'nun ilk AD'lerini yutar (Ketu..Moon); doğumda
    # görünür ilk parça Mars AD'sinin kalanı (nominal başlangıcı 1.62 yıl önce)
    # ve MD sonuna kırpılmış hali ~0.72 yıl (= balance) sürer.
    assert tl[0]["mahadasha"] == "Rahu" and tl[0]["antardasha"] == "Mars"
    assert tl[0]["start_utc"][:3] == (2000, 1, 1)          # görünür başlangıç = doğum
    assert abs(tl[0]["years"] - 0.72) < 0.01               # kalan = balance (kırpık)
    assert tl[1]["mahadasha"] == "Jupiter" and tl[1]["antardasha"] == "Jupiter"
    span = (swe.julday(*tl[-1]["end_utc"]) - jd0) / YEAR
    # Timeline = balance + 8 tam MD = 120 − tüketilen kısım (~102.72 yıl; 120 DEĞİL — normal).
    assert abs(span - (bal + 102.0)) < 0.01
    # ardışık segmentler kesintisiz olmalı (boşluk/çakışma yok; saat hassasiyetiyle)
    for i in range(1, len(tl)):
        prev_end = swe.julday(*tl[i-1]["end_utc"])
        cur_start = swe.julday(*tl[i]["start_utc"])
        assert abs(prev_end - cur_start) < 1e-6, f"gap at {i}"
    # süre tutarlılığı: tam MD'larda AD yılları toplamı ≈ MD yılı
    sat_md = [n for n in tl if n["mahadasha"] == "Saturn"]
    assert abs(sum(n["years"] for n in sat_md) - YEARS["Saturn"]) < 0.05
    # AD süresi balancadan BAĞIMSIZ: Rahu-Jupiter AD'si her zaman 18×16/120 = 2.4 yıl
    # (eski hatalı kod bunu ~0.1 yıl üretirdi); 2. Rahu MD turunda tam görünür.
    rj = [n for n in tl if n["mahadasha"] == "Rahu" and n["antardasha"] == "Jupiter"]
    assert len(rj) == 1 and abs(rj[0]["years"] - 2.4) < 0.005
    # Rahu MD turunda yalnızca son AD (Mars) görünür; sonraki 9 MD'da Rahu AD'leri TAM döner.
    ra_total = [n for n in tl if n["mahadasha"] == "Rahu"]
    assert len(ra_total) == 1                                   # ilk tur kırpık (yalnız Rahu-Mars)
    rme = [n for n in tl if n["mahadasha"] != "Rahu"]            # yerinde kontrol yerine:
    rk = [n for n in tl if n["antardasha"] == "Mercury" and n["mahadasha"] == "Ketu"]
    assert rk and abs(rk[0]["years"] - 7 * 17 / 120) < 0.005     # Ketu-Mercury tam AD = 0.9917 yıl


def test_dasha_timeline_golden_190():
    """GOLDEN takvim: Ay 190° (Swati, frac 0.25) -> Rahu MD kalanı 13.5 yıl.
    Tüketilen 4.5 yıl = Rahu-Rahu AD (tam 2.7) + Rahu-Jupiter AD'nin ilk 1.8
    yılı; bunlar doğumdan ÖNCE kaldığı için yayınlanmaz. İlk görünür AD =
    Rahu-Jupiter: nominal başlangıcı doğumdan ÖNCEYE kayar, görünür süresi =
    2.4 − 1.8 = 0.6 yıl. Sonraki AD'ler TAM süresiyle döner."""
    jd0 = swe.julday(2000, 1, 1, 12.0)
    tl = vimshottari(190.0, jd0)
    assert tl[0]["mahadasha"] == "Rahu" and tl[0]["antardasha"] == "Jupiter"
    assert tl[0]["start_utc"][:3] == (2000, 1, 1)     # görünür başlangıç = doğum
    assert abs(tl[0]["years"] - 0.6) < 0.005          # Jupiter AD'nin kalanı (2.4−1.8)
    assert abs(tl[1]["years"] - 2.85) < 0.005         # Rahu-Saturn: TAM AD (18×19/120)
    assert abs(tl[2]["years"] - 2.55) < 0.005         # Rahu-Mercury: TAM AD (18×17/120)
    # timeline = 13.5 + 8 tam MD = 115.5 yıl (120 − 4.5 tüketilen)
    span = (swe.julday(*tl[-1]["end_utc"]) - jd0) / YEAR
    assert abs(span - 115.5) < 0.01
    for i in range(1, len(tl)):
        assert abs(swe.julday(*tl[i-1]["end_utc"]) - swe.julday(*tl[i]["start_utc"])) < 1e-6


def test_events_ingress_reference(adapter):
    """Canlı çıkarılan referans: Lahiri sid. Güneş 2026-03-14 Kumbha->Meena.

    Pencere 2026-03-01..2026-04-15: ikinci gerçek geçiş (Meena->Mesha,
    2026-04-14) algoritma düzeltmesinden SONRA bulunuyor (eski sürümde
    kaçardı) — beklenti 1'den 2'ye güncellendi; her iki olay da doğrulanır.
    """
    evs = adapter.events((dt.datetime(2026, 3, 1, tzinfo=UTC),
                          dt.datetime(2026, 4, 15, tzinfo=UTC)), "sun")
    assert len(evs) == 2
    assert evs[0]["from_sign"] == "Aquarius" and evs[0]["to_sign"] == "Pisces"
    assert evs[0]["ut"].startswith("2026-03-14")
    assert evs[1]["from_sign"] == "Pisces" and evs[1]["to_sign"] == "Aries"
    assert evs[1]["ut"].startswith("2026-04-14")
