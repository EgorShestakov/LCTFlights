"""
Парсер географических координат
"""

import re
from typing import Dict
from .base_parser import BaseParser
from uav_entities.coordinates import Coordinates


class CoordinateParser(BaseParser):
    """Парсер координат из формата ГГГГNДДДДЕ в десятичные градусы"""
    
    def parse(self, coord_str: str) -> Coordinates:
        """
        Конвертирует координаты из строкового формата в объект Coordinates
        
        Args:
            coord_str: Строка с координатами в формате ГГГГNДДДДЕ
            
        Returns:
            Объект Coordinates с распарсенными данными
        """
        try:
            # Ищем шаблон координат: цифры+N/S+цифры+E/W
            match = re.search(r'(\d{2,4})([NS])(\d{2,5})([EW])', coord_str.upper())
            if not match:
                return Coordinates(original=coord_str)

            lat_deg_min, lat_dir, lon_deg_min, lon_dir = match.groups()

            # Обрабатываем широту
            if len(lat_deg_min) == 4:  # ГГММ
                lat_deg = int(lat_deg_min[:2])
                lat_min = int(lat_deg_min[2:4])
            else:  # ГГГММ
                lat_deg = int(lat_deg_min[:3])
                lat_min = int(lat_deg_min[3:5])

            lat_decimal = lat_deg + lat_min / 60.0
            if lat_dir == 'S':
                lat_decimal = -lat_decimal

            # Обрабатываем долготу
            if len(lon_deg_min) == 5:  # ДДДММ
                lon_deg = int(lon_deg_min[:3])
                lon_min = int(lon_deg_min[3:5])
            else:  # ДДДДММ
                lon_deg = int(lon_deg_min[:4])
                lon_min = int(lon_deg_min[4:6])

            lon_decimal = lon_deg + lon_min / 60.0
            if lon_dir == 'W':
                lon_decimal = -lon_decimal

            return Coordinates(
                original=coord_str,
                latitude=round(lat_decimal, 6),
                longitude=round(lon_decimal, 6),
                dms=f"{lat_deg}°{lat_min}'{lat_dir} {lon_deg}°{lon_min}'{lon_dir}"
            )
        except Exception as e:
            return Coordinates(original=coord_str, error=str(e))
