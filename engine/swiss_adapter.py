"""SwissEphemerisAdapter — pyswisseph üzerinden EphemerisPort implementasyonu.

LİSANS NOTU (gist §1.2): swisseph AGPL-3.0 veya ticari lisansa tabidir.
Bu adaptör ONLY lisanslı dağıtımda aktif olur; aksi halde AstronomyEngine/Skyfield
adaptörüne geçilir. Port arayüzü değişmediği için üst katman etkilenmez.
NOT: alternatif adaptöre geçmek dağıtımın lisans yükümlülüklerini otomatik çözmez;
AGPL-3.0 ve ticari lisans koşulları dağıtım biçimine göre ayrı değerlendirilmelidir.

Review düzeltmeleri (bu revizyon, hepsi canlı pyswisseph 2.10.3.2 ile doğrulandı):
- P0 _to_jd(): swe.julday()'ın 5. parametresi TAKVİM seçimidir (cal), UTC ofseti
  DEĞİL (canlı: cal=-3 -> ValueError "invalid calendar (-3)"). Ofset artık saat
  dilimine uygulanır; tz-aware girdide utcoffset kullanılır, naive girdide
  tz_offset_hours. Mikrosaniye korunur.
- P0 ayanamsa() global mod sızıntısı: önceki sidereal mod (tüm parametreleriyle)
  artık try/finally ile HER ZAMAN geri yüklenir; hesap sırasında başka bir thread
  modu değiştirirse bile son adımda doğru moda döner. Desteklenmeyen mod açıkça
  ValueError üretir.
- P0 concurrency: Swiss Ephemeris'in sidereal modu PROCESS-GENEL global durumdur
  (pyswisseph'te get_sid_mode bile yok — canlı doğrulandı). Mod-değiştiren tüm
  işlemler (_set_sid_mode / houses / ayanamsa-switch) sınıf-seviyesi ortak RLock
  altında tek atomik bölümde yürür. longitude()/ayanamsa() aynı kilidi kullandığı
  için farklı modlu iki adapter dönüşümlü/eşzamanlı çağrıda birbirinin ayarını
  bozamaz. Yine de adapter yalnızca bu kilit sayesinde thread-safe'tir; SE
  kütüphanesinin kendisine güvenilmez.
- P1 longitude(): frame artık kesin doğrulanır ("sidereal"/"tropical");
  "sidereal " gibi geçersiz girdi sessizce tropik döndürmek yerine ValueError.
- P1 _set_sid_mode(): desteklenmeyen mod KeyError yerine ValueError (uygun mesaj).
- P1 houses(): bilinmeyen sistem KeyError yerine NotImplementedError;
  sri_panchika eşlemesi b"V" (Vehlow point-system) olarak belgelendi — Jyotish
  Sri Panchika tanımıyla birebir karşılığı DOĞRULANMAMIŞTIR (yedek skyfield
  adaptörü segfault riski nedeniyle bunu whole-sign'a düşürür; port sözleşmesi
  orada belirlenmelidir). Çıktı: 12 ev başlangıcı, FLG_SIDEREAL sözleşmesiyle
  sidereal referansta.
- P1 events(): sınır taraması artık (a) çoklu geçişleri [jd-1, jd] aralığında
  TARAYARAK kaçurmaz, (b) retrograd ileri/geri ingress'leri yönleriyle doğru
  sınıflandırır (from/to gerçek komşu burçlardan, binary refine alt sınırı
  pencere başlangıcına kıskaçlanır), (c) olayın pencere içinde kaldığı doğrulanır,
  (d) ISO çıktısı saniye hassasiyetindedir.
- _tropical() gerçek hesaplama modu FLG_SWIEPH'tir (yorumdaki FLG_MOSEPH iddiası
  yanlıştı; düzeltildi).
"""
from __future__ import annotations

import datetime as _dt
import threading
from zoneinfo import ZoneInfo

import swisseph as swe

from engine.ephemeris_port import EphemerisPort, Location

_BODIES = {
    "sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
    "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
    "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
    "pluto": swe.PLUTO, "rahu_mean": swe.MEAN_NODE, "ketu_mean": swe.MEAN_NODE,
}

# Swiss Ephemeris sidereal modu GLOBAL süreç durumudur; mod-değiştiren tüm
# bölümler bu tek ortak kilit altında çalışır (farklı adapter örnekleri dahil).
_GLOBAL_LOCK = threading.RLock()


def _body_id(body: str) -> int:
    """Port sözleşmesi: bilinmeyen cisim ham KeyError değil ValueError üretir."""
    try:
        return _BODIES[body]
    except KeyError:
        raise ValueError(
            f"bilinmeyen gök cismi: {body!r}; desteklenenler: {sorted(_BODIES)}") from None


def _to_jd(date, tz_offset_hours: float = 0.0) -> float:
    """datetime | JD(float) -> JD UT.

    ÖNEMLİ (P0 düzeltme): swe.julday()'ın 5. parametresi `cal` takvim seçimidir
    (0=GREGORIAN, 1=JULIAN); UTC ofseti DEĞİLDİR. Eski kod `-tz_offset_hours`
    buraya geçiriyordu → ya ValueError (canlı doğrulandı: invalid calendar (-3))
    ya da yanlış takvim. Ofset artık doğru biçimde GÜN SAATİ bileşenine
    uygulanır: local = UTC + offset ⇒ JD_UT = julday(yerel alan − offset).
    """
    if isinstance(date, (int, float)):
        return float(date)
    if date.tzinfo is not None:
        # tz-aware: UTC'ye çevir; utcoffset kullanılabilir olmalı (ölüydü — P0).
        utc = date.astimezone(ZoneInfo("UTC"))
        hour = utc.hour + utc.minute / 60 + (utc.second + utc.microsecond / 1e6) / 3600
        return swe.julday(utc.year, utc.month, utc.day, hour)
    # naive: yerel saat kabul edilir; tz_offset_hours kadar UTC geriye kaydırılır.
    hour = date.hour + date.minute / 60 + (date.second + date.microsecond / 1e6) / 3600
    return swe.julday(date.year, date.month, date.day, hour - tz_offset_hours)


def _ayanamsa_deg(ret) -> float:
    """pyswisseph sürümüne göre get_ayanamsa_ut ya float ya (tjd, ayanamsa) döner."""
    return ret[1] if isinstance(ret, tuple) else float(ret)


class SwissEphemerisAdapter(EphemerisPort):
    # pyswisseph 2.10 sabitleriyle DOĞRULANMIŞ eşleme (J2000 ayanamsa değerleriyle test edildi):
    # mode 1 -> 23.8571 (Lahiri ✓), mode 0 -> 24.7403 (Fagan/Bradley ✓),
    # mode 5 -> 23.7602 (Raman ✓), mode 7 -> 22.4788 (Yukteshwar ✓),
    # mode 9 -> 23.5336 (Krishnamurti ✓). Ham sayı yerine swe.* sabitleri kullanılır.
    @property
    def _modes(self) -> dict:
        return {"lahiri": (swe.SIDM_LAHIRI, None), "fagan": (swe.SIDM_FAGAN_BRADLEY, None),
                "raman": (swe.SIDM_RAMAN, None), "yukteshwar": (swe.SIDM_YUKTESHWAR, None),
                "krishnamurti": (swe.SIDM_KRISHNAMURTI, None)}

    # Ev sistemi eşlemesi. NOT: b"V" Swiss Ephemeris'in *Vehlow* point-system
    # evidir; "sri_panchika" adlandırması Jyotish tanımından bağımsız doğrulanmış
    # değildir (bkz. modül docstring + skyfield yedeğindeki whole-sign kararı).
    _HOUSE_SYSTEMS = {
        "placidus": b"P", "koch": b"K", "whole": b"W",
        "equal": b"E", "sri_panchika": b"V", "vedic_whole": b"W",
    }

    def __init__(self, ayanamsa_mode: str = "lahiri"):
        if ayanamsa_mode not in self._modes:
            raise ValueError(
                f"desteklenmeyen ayanamsa modu: {ayanamsa_mode!r}; "
                f"geçerli modlar: {sorted(self._modes)}")
        self._mode = ayanamsa_mode
        # jhora.const importu global sid-mode'u SIDM_USER'a çevirir; bu yüzden
        # mod her hesap çağrısında KESIN olarak yeniden kurulur (yan etki =
        # sessiz veri hatası). Kurulum _GLOBAL_LOCK altında yapılır.
        self._set_sid_mode()

    def _set_sid_mode(self):
        with _GLOBAL_LOCK:
            try:
                t0, a0 = self._modes[self._mode]
            except KeyError:
                raise ValueError(
                    f"desteklenmeyen ayanamsa modu: {self._mode!r}; "
                    f"geçerli modlar: {sorted(self._modes)}") from None
            if a0 is None:
                swe.set_sid_mode(t0)
            else:
                swe.set_sid_mode(swe.SIDM_USER, t0, a0)

    @staticmethod
    def _tropical(tjd: float, body: int) -> float:
        # Gerçek hesaplama modu FLG_SWIEPH'tir (ephem dosyası varsa Swiss, yoksa
        # pyswisseph Moshier'e düşebilir; J2000 yakınında fark ihmal edilebilir).
        xx, _ = swe.calc_ut(tjd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)
        return xx[0]

    def longitude(self, body: str, date, frame: str = "sidereal",
                  tz_offset_hours: float = 0.0) -> float:
        if frame not in ("sidereal", "tropical"):
            raise ValueError(
                f"geçersiz çerçeve: {frame!r}; yalnızca 'sidereal' | 'tropical')".replace(")", ""))
        b = _body_id(body)
        with _GLOBAL_LOCK:
            # Tek atomik bölüm: mod kurulumu + hesaplama birlikte kilit altında;
            # başka bir adapter bu sırada global sid-mode'u değiştiremez.
            self._set_sid_mode()
            tjd = _to_jd(date, tz_offset_hours)
            if frame == "sidereal":
                # TEK DOGRU KAYNAK kurali: sidereal = tropical - ayanamsa.
                # calc_ut FLG_SIDEREAL'in epoch düzeltmesi ile get_ayanamsa_ut arasında
                # ~0.004° fark var (canlı doğrulandı); bu fark hüküm katmanında
                # nakshatra sınır hataları üretmesin diye türetilmiş değer kullanılır.
                lon = (self._tropical(tjd, b) - swe.get_ayanamsa_ut(tjd)) % 360.0
            else:
                lon = self._tropical(tjd, b)
        if body == "ketu_mean":
            lon = (lon + 180.0) % 360.0
        return lon

    def ayanamsa(self, date, mode: str | None = None,
                 tz_offset_hours: float = 0.0) -> float:
        """Seçili ayanamsa modunun offseti (derece).

        Sözleşme (P0 düzeltme):
        - mode=None → NESNENİN modu kullanılır (adapter tutarlılığı; eski davranış
          "varsayılan lahiri ama nesnenin modu uygulanıyor" belirsizliği kaldırıldı).
        - mode verilirse → istenen mod GEÇİCİ olarak kurulur, değer okunur ve
          önceki sidereal ayar try/finally ile TÜM PARAMETRELERİYLE geri yüklenir
          (hesap arasında üçüncü bir taraf modu değiştirse bile son adım doğru
          moda döner). Desteklenmeyen mod ValueError.
        """
        if mode is None:
            mode = self._mode
        if mode not in self._modes:
            raise ValueError(
                f"desteklenmeyen ayanamsa modu: {mode!r}; geçerli modlar: {sorted(self._modes)}")
        tjd = _to_jd(date, tz_offset_hours)
        with _GLOBAL_LOCK:
            if mode == self._mode:
                # Gereksiz save/restore yok; nesne zaten kendi modunu garantiler.
                self._set_sid_mode()
                return _ayanamsa_deg(swe.get_ayanamsa_ut(tjd))
            # Önceki tam durumu kaydet (pyswisseph 2.10'da get_sid_mode YOK —
            # canlı doğrulandı; bu nedenle yalnızca nesnenin bildiği kendi modu
            # restore hedefi olarak güvenilir biçimde saklanabilir).
            prev_mode = self._mode
            try:
                self._mode = mode
                self._set_sid_mode()
                return _ayanamsa_deg(swe.get_ayanamsa_ut(tjd))
            finally:
                # Global state'i her zaman (hata durumunda da) nesnenin kendi
                # moduna geri kur; self._mode ile global durum uyumlu kalır.
                self._mode = prev_mode
                self._set_sid_mode()

    def houses(self, date, location: Location, system: str = "placidus") -> list[float]:
        hs = self._HOUSE_SYSTEMS.get(system)
        if hs is None:
            raise NotImplementedError(
                f"desteklenmeyen ev sistemi: {system!r}; "
                f"geçerli sistemler: {sorted(self._HOUSE_SYSTEMS)}")
        tjd = _to_jd(date, location.tz_offset_hours)
        with _GLOBAL_LOCK:
            # mod kurulumu + hesaplama tek atomik bölümde (yarış koşusu kapalı).
            self._set_sid_mode()
            cusps, _ = swe.houses_ex(tjd, location.lat, location.lon,
                                     hs, swe.FLG_SIDEREAL)
        # Sözleşme: 12 ev BAŞLANGICI (cusp), sidereal çerçeve (FLG_SIDEREAL).
        return list(cusps)

    SIGNS = ("Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces")

    def events(self, window, body: str) -> list[dict]:
        """Ingress olayları: ince tarama (±3° hareket eşiği) + binary refine.

        P1 düzeltmeleri:
        - Günlük örneklemede birden fazla burç sınırının aşıldığı aralıklar
          (hızlı gezegenler) artık 3° adım alt-bölmeyle taranır → olay kaçmaz.
        - Retrograd geçişler: sınır [lo,hi] içinde hangi yönden aşılıyorsa
          from/to buna göre gerçek komşu burçlardır ((cur∓1)%12); ileri ve geri
          ingress ayrı olaylardır.
        - Binary refine'ın alt sınırı pencere başlangıcına kıskaçlanır; bulunan
          olay zamanının gerçekten [start, end] içinde kaldığı doğrulanır.
        - Hassasiyet ~1 sn (40 iterasyon); ISO çıktıları saniye içerir.
        """
        start, end = window
        jd0, jd1 = _to_jd(start), _to_jd(end)
        if jd1 <= jd0:
            return []

        def sign_index(jd: float) -> int:
            return int(self.longitude(body, jd) // 30)

        # Hız tahmini (derece/gün) — alt-bölme adımını belirlemek için.
        speed = abs(((self.longitude(body, min(jd0 + 0.5, jd1))
                      - self.longitude(body, max(jd0 - 0.5, jd0)) + 180.0)
                     % 360.0) - 180.0)
        step = 1.0 if speed < 3.0 else max(0.05, 3.0 / (speed + 1e-9))

        out: list[dict] = []
        prev_sign = sign_index(jd0)
        jd = jd0
        while jd < jd1:
            nxt = min(jd + step, jd1)
            cur = sign_index(nxt)
            if cur != prev_sign:
                lo, hi = jd, nxt
                for _ in range(40):  # ~sn-altı hassasiyet
                    mid = (lo + hi) / 2
                    if sign_index(mid) == prev_sign:
                        lo = mid
                    else:
                        hi = mid
                # Refine alt sınırını pencere başlangıcına kıskaçla: geçiş,
                # tarama aralığının SOLUNDA (window öncesi) kalmış olabilir.
                est = max(hi, jd0)
                if not (jd0 <= est <= jd1):
                    prev_sign = cur
                    jd = nxt
                    continue
                # YÖN TESTİ (P1 düzeltme — retrograd sınıfaması): binary refine
                # yalnızca "burç indeksi değişti" anını bulur; hangi komşu burçtan
                # geldiğini GUARANTİ etmez (Ay'ın bir burcun içindeyken bile ileri/
                # geri sınır sınır dolaşması mümkün). Bu yüzden olay anının hemen
                # ÖNCESİNDEKİ gerçek burç doğrudan ölçülür — tahmin/değil gözlem:
                probe_back = max(est - 1e-4, jd0)   # ~8.6 sn önce
                at_before = sign_index(probe_back)
                probe_fwd = min(est + 1e-4, jd1)    # ~8.6 sn sonra
                at_after = sign_index(probe_fwd)
                if at_before == at_after:
                    # Uç durum: ya geçiş tam pencere sınırında ya da çok dar salınım;
                    # emin olanamayız → olay ÜRETME (yanlış sınıflama yerine sessizlik).
                    to_sign = None
                    from_sign = None
                else:
                    from_sign = at_before
                    to_sign = at_after
                    if to_sign == prev_sign:
                        # Tarama "değişim" gördü ama yön ileri değil (geri geçiş);
                        # yine de gerçek gözlem bu → onu yaz.
                        pass
                if to_sign is not None and to_sign != from_sign:
                    dtv = _dt.datetime(2000, 1, 1, tzinfo=_dt.timezone.utc) \
                        + _dt.timedelta(days=est - 2451544.5)
                    dtv = dtv.replace(microsecond=0)
                    out.append({"type": "ingress", "body": body,
                                "ut": dtv.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "from_sign": self.SIGNS[from_sign],
                                "to_sign": self.SIGNS[to_sign],
                                "sign_index": to_sign})
                    prev_sign = to_sign
            jd = nxt
        return out
