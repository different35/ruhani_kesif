"""Fact üretimi — gist BÖLÜM 2 "Fakt Kontratı" + §12.1 P1 çıkış ölçütü:
"7.380 düğüm üretiliyor" (9 MD + 81 AD + 729 PD + 6561 SD = Vimshottari düğüm sayısı).

Bu modül YORUM ÜRETMEZ (gist Kalc kutusu: "Yorum üretmek" yasak). Yalnızca
deterministik sayısal/semantik olgular üretir: doğum anı gezegen konumları,
nakshatra/pada, evler ve tam dasha ağacı (MD→AD→PD→SD).

Dasha ağacı revizyonu (bu turda canlı PyJHora ile doğrulanan kararlar):
- SANAL BAŞLANGIK: doğum, devam eden ilk MD'ın içindedir. Takvim, tüketilen
  süre kadar gerideki sanal MD başlangıcından yürütülür (PyJHora
  `vimsottari_dasha_start_date` de MD başlangıcını doğumdan geriye hesaplar).
  Böylece alt seviyeler DOĞUMDAN YENİDEN BAŞLAMAZ; tam döngünün kaldığı yerden
  devam eder. Orantılı küçültme ve `min(..., md_end)` clamp'leri kaldırıldı —
  sanal başlangıçtan yürüyünce gerekmiyor.
- Doğumdan önce biten düğümler ağıktan ATILMAZ; ağaçta durur ve `pre_birth`
  bayrağı ile işaretlenir. Tüketici isterse `end_jd_ut <= birth_jd_ut` ile
  filtreleyebilir.
- Her seviyede tam 9 çocuk üretilir: 9 + 81 + 729 + 6561 = 7380 düğüm. Bu
  sayı yapısal bir değişmezdir; asıl doğrulama golden testlerledir (ilk MD
  balancası + ilk AD/PD tarihlerinin PyJHora `_vimsottari_bhukti` /
  `_vimsottari_antara` çıktısıyla birebir eşleşmesi).
- Anahtar adları sözleşmesi: antardashas / pratyantardashas / sookshmadashas
  (eski hatalı "pdardashas"/"sopandasdasas" adları düzeltildi; düzeltme bu
  revizyonda yapıldı, tüketiciler artık bu adları kullanacak).
- years alanı HER seviyede TAM nominal yıldır (kırpılmaz); segment süresi
  end-start farkından türetilebilir.
"""
from __future__ import annotations

import datetime as dt

from engine.calendar import julday
from engine.dasha import ANTARDASHA_ORDER, LORDS, YEARS, SIDEREAL_YEAR, balance_years
from engine.ephemeris_port import EphemerisPort, Location
from engine.nakshatra import nakshatra_pada

BODIES = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn",
          "rahu_mean", "ketu_mean")

# Gist §4 düğüm hedefi: 9 + 81 + 729 + 6561 = 7380
NODE_TARGET_MD = 9
NODE_TARGET_AD = 81
NODE_TARGET_PD = 729
NODE_TARGET_SD = 6561


def _build_level(lord: str, start: float, full_yrs: float, birth_jd_ut: float,
                 depth: int, counts: list[int]) -> dict:
    """Tek dasha düzeyini ÖZYİNELEMELİ kurar (MD derinlik 0 → SD derinlik 3).

    Çocukların süresi her zaman TAM formülle (PyJHora `_vimsottari_bhukti` /
    `_vimsottari_antara` ile birebir):
        child_full_yrs = YEARS[child] / 120 * full_yrs(ebeveyn)
    `full_yrs` ebeveynin BALANCADAN BAĞIMSIZ tam yılıdır. Ne orantılı
    küçültme ne de clamp gerekir: cursor SANAL döngü başlangıcından yürür.
    Doğumdan önce biten düğümler `pre_birth=True` ile işaretlenir ama ağaçta
    kalır; kısmen tüketilmiş doğum-üstü düğümün başlangıcı doğumda kesilir.
    years = TAM nominal yıl (her seviyede aynı basamak: 4).
    """
    node = {"lord": lord, "start_jd_ut": max(start, birth_jd_ut),
            "end_jd_ut": start + full_yrs * SIDEREAL_YEAR,
            "years": round(full_yrs, 4),
            "pre_birth": start + full_yrs * SIDEREAL_YEAR <= birth_jd_ut}
    if depth == 3:                      # SD yaprak düzeyi: çocuk yok (anahtar yok)
        counts[3] += 1
        return node
    key = ("antardashas", "pratyantardashas", "sookshmadashas")[depth]
    node[key] = []
    children = ANTARDASHA_ORDER[lord]
    cursor = start
    for ch in children:
        c_full = YEARS[ch] / 120.0 * full_yrs
        node[key].append(_build_level(ch, cursor, c_full, birth_jd_ut,
                                      depth + 1, counts))
        cursor += c_full * SIDEREAL_YEAR
    counts[depth + 1] += len(children)
    return node


def dasha_tree(moon_sidereal_lon: float, birth_jd_ut: float,
               smooth: bool = False) -> dict:
    """Vimshottari ağacı: MD → AD → PD → SD. Toplam düğüm = 7380 (yapısal).

    İlk MD balanca ile açılır; takvim SANAL MD başlangıcından (doğumdan
    tüketilen yıl kadar önce) yürür — PyJHora da MD başlangıcını doğumdan
    geriye hesaplar. Alt düğümler doğumdan DEĞİL, tam döngünün kaldığı yerden
    devam eder. Sonraki MD'lar kendi gerçek başlangıçlarından açılır.
    Doğumdan önce biten düğümler `pre_birth=True` ile işaretlidir ama ağaçta
    kalır (sayıyı bozmaz); tüketici isterse end_jd_ut <= birth_jd_ut filtreler.
    """
    bal, start_lord, _cur = balance_years(moon_sidereal_lon, smooth)
    lord_i = LORDS.index(start_lord)
    seq = [LORDS[(lord_i + k) % 9] for k in range(9)]

    tree = {"mahadashas": [], "counts": {}}
    counts = [0, 0, 0, 0]               # md, ad, pd, sd
    # Sanal MD başlangıcı: doğum − tüketilen kısım (balance = tam − tüketilen).
    virtual_start = birth_jd_ut - (YEARS[seq[0]] - bal) * SIDEREAL_YEAR
    cursor = virtual_start
    for i_md, md_lord in enumerate(seq):
        md_end = cursor + YEARS[md_lord] * SIDEREAL_YEAR   # TAM md_end (clamp yok)
        node = _build_level(md_lord, cursor, YEARS[md_lord], birth_jd_ut, 0, counts)
        node["balanced"] = i_md == 0
        tree["mahadashas"].append(node)
        counts[0] += 1
        cursor = md_end
    tree["counts"] = {"md": counts[0], "ad": counts[1], "pd": counts[2],
                      "sd": counts[3], "total": sum(counts),
                      "target_total": NODE_TARGET_MD + NODE_TARGET_AD +
                                     NODE_TARGET_PD + NODE_TARGET_SD}
    return tree


def birth_facts(port: EphemerisPort, when: dt.datetime, loc: Location,
                frame: str = "sidereal") -> dict:
    """Gist §2 Fakt Kontratı: tek kaynaklı, çerçeve-etiketli olgu demeti.

    `frame` YALNIZCA etikettir (çıktının baskın referansını bildirir);
    hesaplamayı değiştirmez — hem tropical hem sidereal zaten üretilir.
    """
    # ZAMAN DİLİMİ NORMALİZASYONU: swe.julday girdiyi UT varsayar. tz-aware
    # ama UTC olmayan bir datetime gelirse önce UTC'ye çevrilir; naive girdi
    # belgelenmiş sözleşmeyle UT kabul edilir. Sessiz yanlış JD üretilemez.
    if when.tzinfo is not None:
        when_utc = when.astimezone(dt.timezone.utc)
    else:
        when_utc = when.replace(tzinfo=dt.timezone.utc)
    ay = port.ayanamsa(when_utc)
    out = {"frame": frame, "ayanamsa_deg": ay,
           "input": {"utc": when_utc.isoformat(), "lat": loc.lat, "lon": loc.lon},
           "planets": {}, "houses": [], "moon_nakshatra": None}
    for b in BODIES:
        trop = port.longitude(b, when_utc, "tropical")
        sid = port.longitude(b, when_utc, "sidereal")
        np_ = nakshatra_pada(sid)
        out["planets"][b] = {"tropical": trop, "sidereal": sid,
                             "nakshatra": np_["nakshatra"], "pada": np_["pada"]}
    out["moon_nakshatra"] = out["planets"]["moon"]["nakshatra"]
    out["houses"] = port.houses(when_utc, loc)
    # GÜN + SAAT hassasiyeti korunur (eskisi [:3] ile saati atıyordu).
    # LİSANS TEMİZLİĞİ: swe.julday yerine yerel engine.calendar.julday (aynı
    # sözleşme: takvim alanları + UT saat -> JD(UT)).
    jd_ut = julday(when_utc.year, when_utc.month, when_utc.day,
                   when_utc.hour + when_utc.minute / 60
                   + (when_utc.second + when_utc.microsecond / 1e6) / 3600)
    moon_sid = out["planets"]["moon"]["sidereal"]
    out["dasha_tree"] = dasha_tree(moon_sid, jd_ut)
    return out
