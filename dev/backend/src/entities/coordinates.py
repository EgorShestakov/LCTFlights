
from typing import Optional


class Coordinates:
    """Класс для представления координат"""

    def __init__(self, original: str = None, latitude: float = None, longitude: float = None, dms: str = None, error: str = None):
        self.original = original
        self.latitude = latitude
        self.longitude = longitude
        self.dms = dms
        self.error = error

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для JSON"""
        return {
            "original": self.original,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "dms": self.dms,
            "error": self.error
        }

