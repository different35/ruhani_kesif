"""Fact üretimi — gist BÖLÜM 2 "Fakt Kontratı" + §12.1 P1 çıkış ölçütü:
"7.380 düğüm üretiliyor" (9 MD + 81 AD + 729 PD + 6561 SD = Vimshottari düğüm sayısı).

Bu modül YORUM ÜRETMEZ (gist Kalc kutusu: "Yorum üretmek" yasak). Yalnızca
deterministik sayısal/semantik olgular üretir: doğum anı gezegen konumları,
nakshatra/pada, evler ve tam dasha ağacı (MD→AD→PD→SD).
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import swisseph as swe

from engine.dasha import ANTARDASHA_ORDER, LORDS, YEARS, balance_years
from engine.ephemeris_port import EphemerisPort, Location
from engine.nakshatra import nakshatra_pada

BODIES = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
          "rahu_mean", "ketu_mean")

# Gist §4 düğüm hedefi: 9 + 81 + 729 + 6561 = 7380
NODE_TARGET_MD = 9
NODE_TARGET_AD = 81
NODE_TARGET_PD = 729
NODE_TARGET_SD = 6561


def _sub_seq(lord: str) -> list[str]:
    return ANTARDASHA_ORDER[lord]


def dasha_tree(moon_sidereal_lon: float, birth_jd_ut: float) -> dict:
    """Vimshottari ağacı: MD → AD → PD → SD. Toplam düğüm = 7380 (tam döngüde).

    Formül (PyJHora `_vimsottari_bhukti/_vimsottari_antara` ile aynı ölçekleme):
      AD_yrs = MD_yrs * AD_years / 120
      PD_yrs = AD_yrs * PD_years / 120
      SD_yrs = PD_yrs * SD_years / 120
    Balanca: ilk MD kırpılır; onun altındaki tüm düğümler de oradan başlar.
    """
    YEAR = 365.2425
    bal, start_lord, _cur = balance_years(moon_sidereal_lon)
    lord_i = LORDS.index(start_lord)
    seq = [LORDS[(lord_i + k) % 9] for k in range(9)]
    durations = [bal] + [YEARS[s] for s in seq[1:]]
    full_durations = [YEARS[s] for s in seq]

    tree = {"mahadashas": [], "counts": {}}
    n_md = n_ad = n_pd = n_sd = 0
    cursor = birth_jd_ut
    for i_md, (md_lord, md_yrs) in enumerate(zip(seq, durations)):
        md_start, md_end = cursor, cursor + md_yrs * YEAR
        md_node = {"lord": md_lord, "start_jd_ut": md_start, "end_jd_ut": md_end,
                   "years": round(md_yrs, 4), "balanced": i_md == 0, "antardashas": []}
        # DÜĞÜM SAYISI KURALI (gist §4: 9+81+729+6561=7380): her MD tam 9 AD,
        # her AD tam 9 PD, her PD tam 9 SD ÜRETİR; doğum anında kesilen/tüketilen
        # parçalar yayınlanmaz ama takvimin iskeletini bozmaz.
        ad_cursor = md_start
        consumed_frac = (1.0 - md_yrs / full_durations[i_md]) if i_md == 0 else 0.0
        first_full_ad = full_durations[i_md] * YEARS[_sub_seq(md_lord)[0]] / 120.0
        if consumed_frac > 0.0:
            ad_cursor += consumed_frac * first_full_ad * YEAR
        for adi, ad_lord in enumerate(_sub_seq(md_lord)):
            ad_full_yrs = full_durations[i_md] * YEARS[ad_lord] / 120.0  # TAM ölçek
            ad_start = ad_cursor
            ad_end = min(ad_cursor + ad_full_yrs * YEAR, md_end)
            ad_node = {"lord": ad_lord, "start_jd_ut": ad_start, "end_jd_ut": ad_end,
                       "years": round((ad_end - ad_start) / YEAR, 5), "pdardashas": []}
            pd_cursor = ad_start
            for pd_lord in _sub_seq(ad_lord):
                pd_full_yrs = ad_full_yrs * YEARS[pd_lord] / 120.0
                pd_start = pd_cursor
                pd_end = min(pd_cursor + pd_full_yrs * YEAR, ad_end)
                pd_node = {"lord": pd_lord, "start_jd_ut": pd_start, "end_jd_ut": pd_end,
                           "years": round((pd_end - pd_start) / YEAR, 6), "sopandasdasas": []}
                sd_cursor = pd_start
                for sd_lord in _sub_seq(pd_lord):
                    sd_full_yrs = pd_full_yrs * YEARS[sd_lord] / 120.0
                    sd_start = sd_cursor
                    sd_end = min(sd_cursor + sd_full_yrs * YEAR, pd_end)
                    pd_node["sopandasdasas"].append(
                        {"lord": sd_lord, "start_jd_ut": sd_start, "end_jd_ut": sd_end})
                    n_sd += 1
                    sd_cursor = sd_end
                ad_node["pdardashas"].append(pd_node)
                n_pd += 1
                pd_cursor = pd_end
            md_node["antardashas"].append(ad_node)
            n_ad += 1
            ad_cursor = ad_end
        tree["mahadashas"].append(md_node)
        n_md += 1
        cursor = md_end
    tree["counts"] = {"md": n_md, "ad": n_ad, "pd": n_pd, "sd": n_sd,
                      "total": n_md + n_ad + n_pd + n_sd,
                      "target_total": NODE_TARGET_MD + NODE_TARGET_AD +
                                     NODE_TARGET_PD + NODE_TARGET_SD}
    return tree


def birth_facts(port: EphemerisPort, when: dt.datetime, loc: Location,
                frame: str = "sidereal") -> dict:
    """Gist §2 Fakt Kontratı: tek kaynaklı, çerçeve-etiketli olgu demeti."""
    ay = port.ayanamsa(when)
    out = {"frame": frame, "ayanamsa_deg": ay, "input": {"utc": when.isoformat(),
           "lat": loc.lat, "lon": loc.lon}, "planets": {}, "houses": [], "moon_nakshatra": None}
    for b in BODIES:
        trop = port.longitude(b, when, "tropical")
        sid = port.longitude(b, when, "sidereal")
        np_ = nakshatra_pada(sid)
        out["planets"][b] = {"tropical": trop, "sidereal": sid,
                             "nakshatra": np_["nakshatra"], "pada": np_["pada"]}
    out["moon_nakshatra"] = out["planets"]["moon"]["nakshatra"]
    out["houses"] = port.houses(when, loc)
    jd_ut = swe.julday(when.year, when.month, when.day,
                       when.hour + when.minute / 60 + when.second / 3600)
    moon_sid = out["planets"]["moon"]["sidereal"]
    out["dasha_tree"] = dasha_tree(moon_sid, jd_ut)
    return out
