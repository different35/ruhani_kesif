"""EphemerisPort — gist BÖLÜM 1.2'de zorunlu mimari karar olarak tanımlanan arayüz.

Amaç: Swiss Ephemeris (AGPL/ticari lisans riski) bağımlılığını tek noktaya hapsedmek.
Üst katmanlar yalnızca bu soyut arayüzü görür; implementasyon takılabilir.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    lat: float
    lon: float
    tz_offset_hours: float = 0.0


class EphemerisPort(ABC):
    """Hesaplama çekirdeğinin tek geçit noktası (gist §1.2)."""

    @abstractmethod
    def longitude(self, body: str, date, frame: str = "sidereal") -> float:
        """Gök cismi boylamı (derece). frame: 'sidereal' | 'tropical'."""

    @abstractmethod
    def houses(self, date, location: Location, system: str = "placidus") -> list[float]:
        """12 ev köşe noktası (cusp)."""

    @abstractmethod
    def ayanamsa(self, date, mode: str = "lahiri") -> float:
        """Seçilen ayanamsa moduna göre offset (derece)."""

    @abstractmethod
    def events(self, window, body: str) -> list[dict]:
        """Ingress / retrograd / station olayları."""
