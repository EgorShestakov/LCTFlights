"""
Модель данных о полете UAV
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .coordinates import Coordinates


@dataclass
class FlightData:
    """Класс для представления данных о полете БПЛА"""
    flight_identification: Optional[str] = None
    uav_type: Optional[Dict[str, str]] = None
    takeoff_coordinates: Optional[Coordinates] = None
    landing_coordinates: Optional[Coordinates] = None
    takeoff_time: Optional[Dict[str, str]] = None
    landing_time: Optional[Dict[str, str]] = None
    takeoff_date: Optional[Dict[str, str]] = None
    landing_date: Optional[Dict[str, str]] = None
    flight_duration: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        """Конвертирует объект в словарь для сериализации в JSON"""
        result = {}
        for field, value in self.__dict__.items():
            if value is None:
                result[field] = None
            elif hasattr(value, 'to_dict'):
                result[field] = value.to_dict()
            else:
                result[field] = value
        return result
