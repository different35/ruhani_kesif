"""Canlı kalibrasyon: Placidus cusps (yarı-ark yöntemi) vs swisseph."""
import datetime as dt, math
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
EPH = 23.4392911
CE = math.cos(math.radians(EPH))
SE = math.sin(math.radians(EPH))


def asc_trop(tjd_ut, lat, lon):
    gst = swe.sidtime(tjd_ut) * 15.0
    ramc = (gst + lon) % 360
    rr = math.radians(ramc); ll = math.radians(lat); e = math.radians(EPH)
    y = -math.cos(rr)
    x = math.sin(rr) * math.cos(e) + math.tan(ll) * math.sin(e)
    a = math.degrees(math.atan2(y, x)) % 360
    if not (90 <= (a - ramc) % 360 < 270):
        a = (a + 180) % 360
    return a


def ra_of(lon):
    l = math.radians(lon)
    return math.degrees(math.atan2(math.sin(l) * CE, math.cos(l))) % 360


def lon_of(ra):
    r = math.radians(ra)
    return math.degrees(math.atan2(math.sin(r) / CE, math.cos(r))) % 360


def semi_arc(ra, lat):
    """Yukarı çıkış yarı-arkı (derece). cos(H) = -tan(dec)tan(lat); dec = atan(sin(ra)cos(eps))."""
    dec = math.atan(math.sin(math.radians(ra)) * CE)
    c = -math.tan(dec) * math.tan(math.radians(lat))
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def placidus(tjd_ut, lat, lon):
    asc = asc_trop(tjd_ut, lat, lon)
    gst = swe.sidtime(tjd_ut) * 15.0
    mc = (gst + lon) % 360  # tropik MC ekliptik boylamı = RAMC (aynı sayı, RA->lon dönüşümü ayrı; dikkat!)
    # DÜZELTME: MC ekliptikte: tan(lon_mc)=tan(ramc)/cos(eps) quadrant ramc ile aynı
    rr = math.radians(mc)
    mc_lon = math.degrees(math.atan2(math.sin(rr) / CE, math.cos(rr))) % 360
    ic = (mc_lon + 180) % 360
    desc = (asc + 180) % 360
    # MC/IC yarım arkı: meridyen üstü arcus: cos? MC noktasının declination'ı = dec(RA=ramc)
    ra_mc = ra_of(mc_lon)
    sa_mc = semi_arc(ra_mc, lat)   # MC'nin yarı-gündüz arkı
    ra_asc = ra_of(asc)
    sa_asc = semi_arc(ra_asc, lat)
    cusps = [0.0] * 13
    cusps[1], cusps[4], cusps[7], cusps[10] = asc, mc_lon, desc, ic
    for i in range(1, 4):
        f = i / 3.0
        cusps[i + 0] = None
    # alt'lar: C2..C3 (asc->mc arası), C11..C12 (ic->asc), C5..C6 (mc->desc), C8..C9 (desc->ic)
    def solve(arc_lo_ra, arc_hi_ra, lo_cusp_lon, hi_cusp_lon, frac, upper):
        # hedef RA çöz: RA = RA_lo + frac*(RA_hi - RA_lo) (dairesel değil, süreksizliği kontrol et)
        # basit doğrusal RA interpolasyonu (lo->hi yönünde)
        dra = (arc_hi_ra - arc_lo_ra) % 360
        ra = (arc_lo_ra + frac * dra) % 360
        dec = math.atan(math.sin(math.radians(ra)) * CE)
        t = math.tan(dec) * math.tan(math.radians(lat))
        if upper:
            ha = math.degrees(math.atan(t / math.tan(0.5 * math.radians(sa_mc))))
            # trHMC: H = arctan( tan(dec)tan(phi) / tan(0.5*SA_MC) )  (Meeus sf.173, tr semicircle)
        else:
            ha = math.degrees(math.atan(t / math.tan(0.5 * math.radians(180 - sa_mc))))
        lst = (ra - ha) % 360
        ramc_x = (lst - lon) % 360
        rr_ = math.radians(ramc_x)
        e = math.radians(EPH)
        y = -math.cos(rr_)
        x = math.sin(rr_) * math.cos(e) + math.tan(math.radians(lat)) * math.sin(e)
        a = math.degrees(math.atan2(y, x)) % 360
        if not (90 <= (a - ramc_x) % 360 < 270):
            a = (a + 180) % 360
        return lon_of(ra)
    # sırayla: C2,C3: asc->mc (üst kuşak, dilim 1/3,2/3); C5,C6: mc->desc; C8,C9: desc->ic; C11,C12: ic->asc
    pairs = [(2, asc, mc_lon, True), (5, mc_lon, desc, True), (8, desc, ic, False), (11, ic, asc, False)]
    out = {1: asc, 4: mc_lon, 7: desc, 10: ic}
    for base_i, lo_lon, hi_lon, upper0 in pairs:
        ra_lo, ra_hi = ra_of(lo_lon), ra_of(hi_lon)
        for k in (1, 2):
            frac = k / 3.0
            ra = (ra_lo + frac * ((ra_hi - ra_lo) % 360)) % 360
            dec = math.atan(math.sin(math.radians(ra)) * CE)
            upper = upper0
            denom_half = 0.5 * math.radians(sa_mc if upper else (180 - sa_mc))
            ha = math.degrees(math.atan(math.tan(dec) * math.tan(math.radians(lat)) / math.tan(denom_half)))
            lst = (ra - ha) % 360
            ramc_x = (lst - lon) % 360
            rr_ = math.radians(ramc_x); e = math.radians(EPH)
            y = -math.cos(rr_)
            x = math.sin(rr_) * math.cos(e) + math.tan(math.radians(lat)) * math.sin(e)
            a = math.degrees(math.atan2(y, x)) % 360
            if not (90 <= (a - ramc_x) % 360 < 270):
                a = (a + 180) % 360
            out[base_i + k - 1] = a
    res = [out.get(i) for i in range(1, 13)]
    return res


cases = [((2000, 1, 1, 12), 41.0, 29.0), ((2020, 6, 21, 3, 45), 12.9, 77.5),
         ((1987, 10, 13, 6, 20), -33.9, 151.2), ((1995, 5, 20, 10, 30), 52.5, -1.9),
         ((2011, 2, 3, 22, 15), 35.7, 139.7)]
for (y, mo, d, h, *rest), lat, lon in cases:
    hh = rest[0] if rest else 0
    tjd = swe.julday(y, mo, d, h + hh / 60)
    cusps_swe, _ = swe.houses_ex(tjd, lat, lon, b'P', swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    ay = swe.get_ayanamsa_ut(tjd)
    mine = placidus(tjd, lat, lon)
    diffs = []
    for i in range(12):
        m = mine[i]
        s = cusps_swe[i]
        dd = (m - s + 180) % 360 - 180
        diffs.append(dd)
    print(f"{y}-{mo:02d}-{d:02d} {h:02d}:{hh:02d} lat{lat}:")
    print("  swe:", " ".join(f"{c:7.3f}" for c in cusps_swe))
    print("  ben:", " ".join(f"{c:7.3f}" if c is not None else "   ---" for c in mine))
    print("  dfr:", " ".join(f"{c:+7.3f}" for c in diffs))
