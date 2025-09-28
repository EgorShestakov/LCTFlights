"""
Модели данных (Entities) для парсера UAV сообщений
"""

from .coordinates import Coordinates
from .flight import FlightData

__all__ = ["Coordinates", "FlightData"]
