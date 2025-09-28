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

    def get_takeoff_coordinates(self) -> tuple:
        """
        Возвращает координаты взлета в виде кортежа (latitude, longitude)

        Returns:
            Кортеж с координатами или None если координаты отсутствуют
        """
        if (self.takeoff_coordinates and
                self.takeoff_coordinates.latitude is not None and
                self.takeoff_coordinates.longitude is not None):
            return (self.takeoff_coordinates.latitude, self.takeoff_coordinates.longitude)
        return None

    def get_landing_coordinates(self) -> tuple:
        """
        Возвращает координаты посадки в виде кортежа (latitude, longitude)

        Returns:
            Кортеж с координатами или None если координаты отсутствуют
        """
        if (self.landing_coordinates and
                self.landing_coordinates.latitude is not None and
                self.landing_coordinates.longitude is not None):
            return (self.landing_coordinates.latitude, self.landing_coordinates.longitude)
        return None

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
