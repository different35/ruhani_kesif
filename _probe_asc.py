import datetime as dt, math
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)
dates = [dt.datetime(2000,1,1,12), dt.datetime(2020,6,21,3,45), dt.datetime(1987,10,13,6,20)]
locs = [(41.0,29.0), (12.9,77.5), (-33.9,151.2)]
for d in dates:
    tjd = swe.julday(d.year,d.month,d.day,d.hour+d.minute/60)
    for lat,lon in locs:
        cusps,dom = swe.houses_ex(tjd, lat, lon, b'P', swe.FLG_SIDEREAL|swe.FLG_SWIEPH)
        asc_swe = cusps[0]
        # Meeus formülü (mevcut kodun mantığı): gst via swe
        gst = swe.sidtime(tjd) * 15.0  # degrees
        ramc = (gst + lon) % 360.0
        eps = math.radians(23.4392911)
        rr = math.radians(ramc); ll = math.radians(lat)
        ar = math.atan2(-math.cos(rr), math.sin(rr)*math.cos(eps)+math.tan(ll)*math.sin(eps))
        asc_meeus = math.degrees(ar)%360
        diff = (asc_meeus-asc_swe+180)%360-180
        print(f"{d} lat{lat} lon{lon}: swe_asc_sid={asc_swe:.4f} meeus_trop->sid={(asc_meeus-swe.get_ayanamsa_ut(tjd))%360:.4f} diff={diff:.4f} ramc={ramc:.3f}")
