
from typing import Optional, Tuple
from src.entities.coordinates import Coordinates


class FlightData:
    """Класс для хранения данных о полете"""

    def __init__(self):
        self.flight_identification: Optional[str] = None
        self.uav_type: Optional[str] = None
        self.takeoff_coordinates: Optional[Tuple[float, float]] = None
        self.landing_coordinates: Optional[Tuple[float, float]] = None
        self.takeoff_time: Optional[str] = None
        self.landing_time: Optional[str] = None
        self.takeoff_date: Optional[dict] = None
        self.landing_date: Optional[dict] = None
        self.source_sheet: Optional[str] = None

    def to_dict(self) -> dict:
        """Преобразует объект в словарь для JSON"""
        return {
            "flight_identification": self.flight_identification,
            "uav_type": self.uav_type,
            "takeoff_coordinates": self.takeoff_coordinates,
            "landing_coordinates": self.landing_coordinates,
            "takeoff_time": self.takeoff_time,
            "landing_time": self.landing_time,
            "takeoff_date": self.takeoff_date,
            "landing_date": self.landing_date,
            "source_sheet": self.source_sheet
        }

    def get_takeoff_coordinates(self) -> Optional[Tuple[float, float]]:
        """Возвращает координаты взлета"""
        return self.takeoff_coordinates

    def get_landing_coordinates(self) -> Optional[Tuple[float, float]]:
        """Возвращает координаты посадки"""
        return self.landing_coordinates

