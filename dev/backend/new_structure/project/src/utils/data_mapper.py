from typing import Dict, List, Optional, Tuple
import re
import pandas as pd


class DataMapper:
    """Маппер для колонок и полей"""

    def __init__(self):
        self.column_mappings = {
            'flight_identification': ['рейс', 'flight', 'sid', 'pln', 'п/п', 'телеграмма pln'],
            'uav_type': ['тип', 'type', 'группа', 'борт', 'model', 'typ', 'shr', 'тип вс', 'борт. номер вс.'],
            'takeoff_coordinates': ['взлет', 'takeoff', 'dep', 'место вылета', 'а/в', 'aftn ап вылета', 'adepz',
                                    'вылет'],
            'landing_coordinates': ['посадка', 'landing', 'dest', 'место посадки', 'а/п', 'aftn ап посадки', 'adarrz'],
            'takeoff_time': ['время вылета', 'takeoff time', 'т выл', 'atd', 'вылета факт', 'время вылета факт.'],
            'landing_time': ['время посадки', 'landing time', 'т пос', 'ata', 'посадки факт', 'время посадки факт.'],
            'takeoff_date': ['дата', 'date', 'полёта', 'дата вылета', 'add'],
            'landing_date': ['дата', 'date', 'полёта', 'дата посадки', 'ada']
        }
        self.coord_patterns = [
            r'(\d+\.\d+)[,\s]+(\d+\.\d+)',  # Decimal: 55.123,37.456
            r'(\d{2,4})([NS])(\d{2,5})([EW])'  # DMS: 5530N03730E
        ]

    def identify_columns(self, columns: List[str]) -> Dict:
        """Идентифицирует столбцы, сопоставляя их с полями JSON"""
        mapping = {}
        for field, keywords in self.column_mappings.items():
            for col in columns:
                col_lower = str(col).lower()
                if any(kw.lower() in col_lower for kw in keywords):
                    mapping[field] = col
                    break
        return mapping

    def classify_field(self, field_name: str) -> Optional[str]:
        """Классифицирует поле для формата ключ-значение"""
        field_lower = field_name.lower()
        for field, keywords in self.column_mappings.items():
            if any(kw.lower() in field_lower for kw in keywords):
                return field
        return None

    def parse_field_value(self, field_type: str, value) -> Optional[any]:
        """Парсит значение в зависимости от типа поля"""
        if 'coordinates' in field_type:
            return self._extract_coordinates(value)
        elif field_type == 'uav_type':
            return str(value).strip()
        elif 'time' in field_type:
            return self._extract_time(value)
        elif 'date' in field_type:
            return self._extract_date(value)
        return str(value).strip()

    def _extract_coordinates(self, value) -> Optional[Tuple[float, float]]:
        """Извлекает координаты из строки"""
        if pd.isna(value):
            return None
        text = str(value)
        for pattern in self.coord_patterns:
            try:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        if pattern == self.coord_patterns[0]:  # Decimal format
                            lat = float(match.group(1))
                            lon = float(match.group(2))
                            if -90 <= lat <= 90 and -180 <= lon <= 180:
                                return (lat, lon)
                        else:  # DMS format
                            lat_deg_min, lat_dir, lon_deg_min, lon_dir = match.groups()
                            if len(lat_deg_min) == 4:  # ГГММ
                                lat_deg = int(lat_deg_min[:2])
                                lat_min = int(lat_deg_min[2:4])
                            else:  # ГГГММ
                                lat_deg = int(lat_deg_min[:3])
                                lat_min = int(lat_deg_min[3:5])
                            lat_decimal = lat_deg + lat_min / 60.0
                            if lat_dir.upper() == 'S':
                                lat_decimal = -lat_decimal

                            if len(lon_deg_min) == 5:  # ДДДММ
                                lon_deg = int(lon_deg_min[:3])
                                lon_min = int(lon_deg_min[3:5])
                            else:  # ДДДДММ
                                lon_deg = int(lon_deg_min[:4])
                                lon_min = int(lon_deg_min[4:6])
                            lon_decimal = lon_deg + lon_min / 60.0
                            if lon_dir.upper() == 'W':
                                lon_decimal = -lon_decimal

                            return (lat_decimal, lon_decimal)
                    except (ValueError, IndexError):
                        continue
            except TypeError as e:
                print(f"Invalid regex pattern {pattern}: {e}")
                continue
        return None

    def _extract_time(self, value) -> Optional[str]:
        """Извлекает время в формате ЧЧММ или ЧЧ:ММ"""
        if pd.isna(value):
            return None
        text = str(value).strip()
        match = re.match(r'(\d{2}):?(\d{2})', text)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return text

    def _extract_date(self, value) -> Optional[Dict[str, str]]:
        """Извлекает дату в формате ДДММГГ"""
        if pd.isna(value):
            return None
        text = str(value).strip()
        match = re.match(r'(\d{2})(\d{2})(\d{2})', text)
        if match:
            day, month, year = match.groups()
            year = f"20{year}"
            return {
                "original": text,
                "iso": f"{year}-{month}-{day}",
                "readable": f"{day}.{month}.{year}"
            }
        return {"original": text, "iso": None, "readable": None}

    def is_record_separator(self, text: str) -> bool:
        """Проверяет, является ли строка разделителем записей"""
        separators = ['===', '---', '***', 'январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                      'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']
        return any(sep.lower() in text.lower() for sep in separators) or text.strip() == ""
