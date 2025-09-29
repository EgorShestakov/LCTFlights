"""
Модель координат
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Coordinates:
    """Класс для представления географических координат"""
    original: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    dms: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Конвертирует объект в словарь"""
        return {
            "original": self.original,
            "decimal": {
                "latitude": self.latitude,
                "longitude": self.longitude
            } if self.latitude and self.longitude else None,
            "dms": self.dms,
            "error": self.error
        }
