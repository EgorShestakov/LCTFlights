```python
import os
import errno

# Define the project structure and file contents
FILE_CONTENTS = {
    "project/config.py": """import os

# Paths (relative to project root)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
SHAPEFILE_PATH = os.path.join(ROOT_DIR, 'regions_shapefile', 'regions_shapefile')
FRONTEND_JSON_PATH = os.path.join(ROOT_DIR, '..', 'frontend', 'data_from_back.json')

# Other configs
CHUNKSIZE = 10000  # For large Excel files
REQUIRED_FIELDS = ['takeoff_coords', 'landing_coords']  # Minimal for analysis
""",
    "project/main.py": """import os
import json
from config import DATA_DIR, FRONTEND_JSON_PATH
from src.services.batch_processor import BatchProcessor
from src.parsers.excel_parser import ExcelParser
from src.parsers.message_parser import MessageParser
from src.analyzers.region_analyzer import RegionAnalyzer

def main():
    # Step 1: Batch process Excel files from data/
    excel_parser = ExcelParser()
    batch_processor = BatchProcessor(excel_parser)
    all_messages = batch_processor.process_directory(DATA_DIR)  # List of dicts: [{'SHR': '...', 'DEP': '...', 'ARR': '...'}, ...]

    # Step 2: Parse messages to FlightData JSONs
    message_parser = MessageParser()
    flight_jsons = []  # List of JSON dicts
    for msg_group in all_messages:
        # Parse each group (SHR/DEP/ARR) into one JSON if possible
        combined_msg = f"{msg_group.get('SHR', '')} {msg_group.get('DEP', '')} {msg_group.get('ARR', '')}".strip()
        if combined_msg:
            flight_data = message_parser.parse_single_message(combined_msg)
            flight_jsons.append(flight_data.to_dict())
        else:
            # Fallback: Parse individually
            for key in ['SHR', 'DEP', 'ARR']:
                msg = msg_group.get(key)
                if msg:
                    flight_data = message_parser.parse_single_message(msg)
                    flight_jsons.append(flight_data.to_dict())

    # Step 3: Extract unique coordinates for analysis
    coordinates = message_parser.extract_all_unique_coordinates()  # From your UAVFlightParser

    # Step 4: Analyze and get region percentages
    analyzer = RegionAnalyzer()
    region_percent_json = analyzer.flights_percent(coordinates)

    # Step 5: Write to frontend JSON (combined results)
    output = {
        'flights': flight_jsons,
        'region_analysis': region_percent_json
    }
    os.makedirs(os.path.dirname(FRONTEND_JSON_PATH), exist_ok=True)
    with open(FRONTEND_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Output written to {FRONTEND_JSON_PATH}")

if __name__ == "__main__":
    main()
""",
    "project/src/__init__.py": "",
    "project/src/parsers/__init__.py": """from .excel_parser import ExcelParser
from .message_parser import MessageParser
""",
    "project/src/parsers/base_parser.py": """"""""
Базовый класс для всех парсеров
""""""

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров"""
    
    @abstractmethod
    def parse(self, value: str) -> Any:
        """
        Парсит строковое значение в структурированный формат
        
        Args:
            value: Строка для парсинга
            
        Returns:
            Распарсенное значение
        """
        pass
""",
    "project/src/parsers/coordinate_parser.py": """"""""
Парсер географических координат
""""""

import re
from typing import Dict
from .base_parser import BaseParser
from src.entities.coordinates import Coordinates


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
""",
    "project/src/parsers/date_parser.py": """"""""
Парсер дат
""""""

from .base_parser import BaseParser
from typing import Dict


class DateParser(BaseParser):
    """Парсер дат в формате ДДММГГ"""
    
    def parse(self, date_str: str) -> Dict[str, str]:
        """
        Парсит дату из строкового формата в структурированный вид
        
        Args:
            date_str: Строка с датой в формате ДДММГГ
            
        Returns:
            Словарь с распарсенной датой в различных форматах
        """
        try:
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = int("20" + date_str[4:6])  # Предполагаем 2000+ годы

            return {
                "original": date_str,
                "iso": f"{year:04d}-{month:02d}-{day:02d}",
                "readable": f"{day:02d}.{month:02d}.{year:04d}"
            }
        except Exception:
            return {"original": date_str, "iso": None, "readable": None}
""",
    "project/src/parsers/field_parser.py": """"""""
Парсер полей из сообщения
""""""

import re
from typing import Dict, Any, Optional, List, Union
from config import REQUIRED_FIELDS


class FieldParser:
    """Парсер для извлечения полей из текстового сообщения"""
    
    def __init__(self, code_dictionaries: Dict[str, Any]):
        """
        Инициализация парсера полей
        
        Args:
            code_dictionaries: Словари для расшифровки кодов
        """
        self.code_dictionaries = code_dictionaries
        self.translate_map = {
            "flight_identification": "SID",
            "uav_type": ["TYP"],
            "takeoff_coordinates": ["DEP", "ADEPZ"],
            "landing_coordinates": ["DEST", "ADARRZ"],
            "takeoff_time": "ATD",
            "landing_time": "ATA",
            "takeoff_date": "ADD",
            "landing_date": "ADA"
        }

    def _find_value_by_code(self, message: str, code: str) -> Optional[str]:
        """
        Ищет значение по конкретному коду в сообщении
        
        Args:
            message: Нормализованное сообщение
            code: Код для поиска
            
        Returns:
            Найденное значение или None
        """
        # Пробуем найти с форматом CODE/VALUE
        pattern_slash = f"{code}/([A-Z0-9]+)"
        match = re.search(pattern_slash, message)
        if match:
            return match.group(1)

        # Пробуем найти с форматом -CODE VALUE
        pattern_space = f"-{code}\\s+([A-Z0-9]+)"
        match = re.search(pattern_space, message)
        if match:
            return match.group(1)

        return None

    def extract_fields(self, message: str) -> Dict[str, Any]:
        """
        Извлекает все поля из сообщения
        
        Args:
            message: Исходное сообщение
            
        Returns:
            Словарь с найденными значениями полей
        """
        result = {}
        
        for key, codes in self.translate_map.items():
            codes_list = codes if isinstance(codes, list) else [codes]
            value = None
            
            for code in codes_list:
                value = self._find_value_by_code(message, code)
                if value:
                    break
                    
            result[key] = value
            
        return result
""",
    "project/src/parsers/excel_parser.py": """import pandas as pd
from typing import List, Dict, Optional, Tuple
from config import CHUNKSIZE
from src.utils.orientation_detector import TableOrientationDetector
from src.utils.data_mapper import DataMapper
import re


class ExcelParser:
    """Универсальный парсер Excel-файлов с поддержкой разных форматов и ориентаций"""
    
    def __init__(self):
        self.orientation_detector = TableOrientationDetector()
        self.mapper = DataMapper()
        self.required_fields = REQUIRED_FIELDS

    def parse_excel(self, file_path: str) -> List[Dict]:
        """Парсит Excel-файл, возвращая список dicts с сообщениями (SHR/DEP/ARR группами)"""
        all_data = []

        try:
            xl = pd.ExcelFile(file_path)

            for sheet_name in xl.sheet_names:
                # Read in chunks for large files
                reader = pd.read_excel(file_path, sheet_name=sheet_name, chunksize=CHUNKSIZE)
                for chunk in reader:
                    if chunk.empty:
                        continue

                    orientation = self.orientation_detector.detect_orientation(chunk)
                    if orientation == 'rows':
                        sheet_data = self._parse_rows_orientation(chunk, sheet_name)
                    elif orientation == 'key_value':
                        sheet_data = self._parse_key_value_rows(chunk, sheet_name)
                    else:
                        sheet_data = self._parse_columns_orientation(chunk, sheet_name)
                    all_data.extend(sheet_data)

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

        return all_data  # [{'SHR': '...', 'DEP': '...', 'ARR': '...'}, ...]

    def _parse_columns_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные с заголовками в столбцах"""
        df = self._normalize_dataframe(df)
        column_mapping = self.mapper.identify_columns(df.columns)

        results = []
        for _, row in df.iterrows():
            parsed_row = self._parse_row(row, column_mapping)
            if self._validate_row(parsed_row):
                parsed_row['source_sheet'] = sheet_name
                parsed_row['orientation'] = 'columns'
                results.append(self._group_to_messages(parsed_row))  # Convert to SHR/DEP/ARR dict

        return results

    def _parse_rows_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные с заголовками в строках"""
        df_transposed = df.T
        df_transposed.columns = df_transposed.iloc[0]
        df_transposed = df_transposed[1:]

        column_mapping = self.mapper.identify_columns(df_transposed.columns)

        results = []
        for _, row in df_transposed.iterrows():
            parsed_row = self._parse_row(row, column_mapping)
            if self._validate_row(parsed_row):
                parsed_row['source_sheet'] = sheet_name
                parsed_row['orientation'] = 'rows'
                results.append(self._group_to_messages(parsed_row))

        return results

    def _parse_key_value_rows(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит ключ-значение формат"""
        records = []
        current_record = {}

        for _, row in df.iterrows():
            if len(row) < 2:
                continue

            key_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            value_cell = row.iloc[1] if len(row) > 1 else None

            field_type = self.mapper.classify_field(key_cell)
            if field_type and pd.notna(value_cell):
                parsed_value = self.mapper.parse_field_value(field_type, value_cell)
                if parsed_value:
                    current_record[field_type] = parsed_value

            if self.mapper.is_record_separator(key_cell) or _ == len(df) - 1:
                if current_record and self._validate_row(current_record):
                    current_record['source_sheet'] = sheet_name
                    current_record['orientation'] = 'key_value'
                    records.append(self._group_to_messages(current_record))
                    current_record = {}

        return records

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Нормализует DataFrame"""
        df.columns = [str(col).strip().lower() for col in df.columns]
        df = df.dropna(how='all')
        df = df.loc[:, ~df.isnull().all()]
        return df

    def _parse_row(self, row: pd.Series, column_mapping: Dict) -> Dict:
        """Парсит строку"""
        result = {}
        if 'takeoff' in column_mapping:
            coords = self._extract_coordinates(row[column_mapping['takeoff']])
            if coords:
                result['takeoff_coords'] = coords
        if 'landing' in column_mapping:
            coords = self._extract_coordinates(row[column_mapping['landing']])
            if coords:
                result['landing_coords'] = coords
        if 'drone_model' in column_mapping:
            model = self._extract_drone_model(row[column_mapping['drone_model']])
            if model:
                result['drone_model'] = model
        return result

    def _group_to_messages(self, parsed_row: Dict) -> Dict:
        """Группирует parsed_row в dict с SHR/DEP/ARR (placeholder; adjust based on actual messages)"""
        # Here, extract messages from parsed_row if available; for now, dummy
        return {
            'SHR': parsed_row.get('drone_model', ''),  # Example
            'DEP': f"DEP/{parsed_row.get('takeoff_coords', ('', ''))[0]}",  # Example
            'ARR': f"ARR/{parsed_row.get('landing_coords', ('', ''))[0]}"   # Example
        }

    def _extract_coordinates(self, value) -> Optional[Tuple[float, float]]:
        if pd.isna(value):
            return None
        text = str(value)
        patterns = [r'(\d+\.\d+)[,\s]+(\d+\.\d+)', ...]  # Your patterns
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    lat = float(match.group(1))
                    lon = float(match.group(2))
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        return (lat, lon)
                except ValueError:
                    continue
        return None

    def _extract_drone_model(self, value) -> Optional[str]:
        if pd.isna(value):
            return None
        text = str(value).strip().upper()
        models = ['DJI', 'MAVIC', 'PHANTOM', 'INSPIRE', 'MATRICE', 'AIR']
        for model in models:
            if model in text:
                return text
        return text if text and text != 'NAN' else None

    def _validate_row(self, parsed_row: Dict) -> bool:
        return any(field in parsed_row for field in self.required_fields)
""",
    "project/src/analyzers/__init__.py": """from .region_analyzer import RegionAnalyzer
""",
    "project/src/analyzers/region_analyzer.py": """import geopandas as gpd
from shapely.geometry import Point
import os
import json
from config import SHAPEFILE_PATH
from typing import List, Dict

class RegionAnalyzer:
    def __init__(self):
        # Load shapefile
        self.gdf = gpd.read_file(f"{SHAPEFILE_PATH}.shp")
        if 'name' not in self.gdf.columns:
            raise ValueError("Shapefile missing 'name' column")

    def find_region(self, lat, lon) -> str:
        """Находит регион по координатам"""
        point = Point(lon, lat)
        for idx, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                return row['name']
        return None

    def flights_percent(self, coordinates: List[tuple]) -> Dict:
        """
        Вычисляет проценты полетов по регионам
        
        Args:
            coordinates: Список (lon, lat)
            
        Returns:
            JSON-like dict with regions and percents
        """
        region_counts = {}
        total_flights = len(coordinates)
        if total_flights == 0:
            return {}

        for lon, lat in coordinates:
            region_name = self.find_region(lat, lon)
            if region_name:
                region_counts[region_name] = region_counts.get(region_name, 0) + 1

        result = {}
        for i, (name, count) in enumerate(region_counts.items(), 1):
            percent = (count / total_flights) * 100
            result[str(i)] = {"name": name, "percent": round(percent, 2)}

        return result
""",
    "project/src/entities/__init__.py": "",
    "project/src/entities/coordinates.py": """from typing import Optional


class Coordinates:
    """Класс для хранения данных о координатах"""
    
    def __init__(
        self,
        original: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        dms: Optional[str] = None,
        error: Optional[str] = None
    ):
        self.original = original
        self.latitude = latitude
        self.longitude = longitude
        self.dms = dms
        self.error = error
        
    def to_dict(self):
        """Преобразует объект в словарь"""
        return {
            "original": self.original,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "dms": self.dms,
            "error": self.error
        }
""",
    "project/src/entities/flight.py": """from typing import Optional, Dict, Any
from .coordinates import Coordinates


class FlightData:
    """Класс для хранения данных о полете"""
    
    def __init__(
        self,
        flight_identification: Optional[str] = None,
        uav_type: Optional[str] = None,
        takeoff_coordinates: Optional[Coordinates] = None,
        landing_coordinates: Optional[Coordinates] = None,
        takeoff_time: Optional[str] = None,
        landing_time: Optional[str] = None,
        takeoff_date: Optional[Dict[str, str]] = None,
        landing_date: Optional[Dict[str, str]] = None
    ):
        self.flight_identification = flight_identification
        self.uav_type = uav_type
        self.takeoff_coordinates = takeoff_coordinates
        self.landing_coordinates = landing_coordinates
        self.takeoff_time = takeoff_time
        self.landing_time = landing_time
        self.takeoff_date = takeoff_date
        self.landing_date = landing_date
        
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует объект в словарь"""
        return {
            "flight_identification": self.flight_identification,
            "uav_type": self.uav_type,
            "takeoff_coordinates": self.takeoff_coordinates.to_dict() if self.takeoff_coordinates else None,
            "landing_coordinates": self.landing_coordinates.to_dict() if self.landing_coordinates else None,
            "takeoff_time": self.takeoff_time,
            "landing_time": self.landing_time,
            "takeoff_date": self.takeoff_date,
            "landing_date": self.landing_date
        }
    
    def get_takeoff_coordinates(self) -> tuple:
        """Возвращает кортеж координат взлета"""
        if self.takeoff_coordinates and self.takeoff_coordinates.latitude is not None and self.takeoff_coordinates.longitude is not None:
            return (self.takeoff_coordinates.latitude, self.takeoff_coordinates.longitude)
        return None
""",
    "project/src/utils/__init__.py": """from .orientation_detector import TableOrientationDetector
from .data_mapper import DataMapper
""",
    "project/src/utils/orientation_detector.py": """import pandas as pd
from typing import Optional


class TableOrientationDetector:
    """Класс для определения ориентации таблицы в DataFrame"""
    
    def detect_orientation(self, df: pd.DataFrame) -> str:
        """
        Определяет ориентацию таблицы
        
        Args:
            df: DataFrame для анализа
            
        Returns:
            'rows' - заголовки в строках
            'columns' - заголовки в столбцах
            'key_value' - формат ключ-значение
        """
        if df.empty:
            return 'columns'
            
        first_row = df.iloc[0]
        first_column = df.iloc[:, 0]
        
        # Проверяем формат ключ-значение
        key_value_indicators = ['key', 'field', 'параметр', 'значение']
        if any(any(ind.lower() in str(val).lower() for ind in key_value_indicators) for val in first_column):
            return 'key_value'
            
        # Проверяем заголовки в строках или столбцах
        header_indicators = ['координаты', 'взлет', 'посадка', 'тип', 'model', 'dep', 'dest']
        first_row_has_headers = any(any(ind.lower() in str(val).lower() for ind in header_indicators) for val in first_row)
        first_col_has_headers = any(any(ind.lower() in str(val).lower() for ind in header_indicators) for val in first_column)
        
        if first_row_has_headers and not first_col_has_headers:
            return 'columns'
        elif first_col_has_headers and not first_row_has_headers:
            return 'rows'
        else:
            # По умолчанию считаем заголовки в столбцах
            return 'columns'
""",
    "project/src/utils/data_mapper.py": """from typing import Dict, List, Optional
import re

class DataMapper:
    """Маппер для колонок и полей"""
    
    def __init__(self):
        self.column_mappings = {
            'coordinates': {
                'takeoff': ['dep', 'takeoff', 'взлет', 'adepz'],
                'landing': ['dest', 'landing', 'посадка', 'adarrz'],
                'drone_model': ['typ', 'model', 'тип', 'bort']
            }
        }
        self.coord_patterns = [r'(\d+\.\d+)[,\s]+(\d+\.\d+)', ...]  # Your patterns

    def identify_columns(self, columns: List[str]) -> Dict:
        mapping = {}
        for field, keywords in self.column_mappings['coordinates'].items():
            for col in columns:
                if any(kw.lower() in str(col).lower() for kw in keywords):
                    mapping[field] = col
                    break
        return mapping

    def classify_field(self, field_name: str) -> Optional[str]:
        field_lower = field_name.lower()
        field_mappings = {
            'takeoff_coords': ['взлет', 'takeoff', 'dep'],
            'landing_coords': ['посадка', 'landing', 'dest'],
            'drone_model': ['модель', 'model', 'typ']
        }
        for field_type, keywords in field_mappings.items():
            if any(kw in field_lower for kw in keywords):
                return field_type
        return None

    def parse_field_value(self, field_type: str, value) -> Optional[any]:
        if 'coords' in field_type:
            return self._extract_coordinates(value)
        elif field_type == 'drone_model':
            return str(value).strip()
        return None

    def _extract_coordinates(self, value):
        # Similar to your _extract_coordinates
        pass  # Implement

    def is_record_separator(self, text: str) -> bool:
        separators = ['===', '---', '***']
        return any(sep in text.lower() for sep in separators) or text.strip() == ""
""",
    "project/src/services/__init__.py": """from .batch_processor import BatchProcessor
from .flight_parser_service import FlightParserService
""",
    "project/src/services/batch_processor.py": """import os
import glob
import pandas as pd
from typing import List, Dict
from src.parsers.excel_parser import ExcelParser  # Dependency

class BatchProcessor:
    def __init__(self, parser: ExcelParser):
        self.parser = parser

    def process_directory(self, directory_path: str) -> List[Dict]:
        """Обрабатывает все Excel-файлы в директории, возвращая список сообщений"""
        all_results = []

        excel_files = glob.glob(os.path.join(directory_path, "*.xlsx")) + \
                      glob.glob(os.path.join(directory_path, "*.xls"))

        for file_path in excel_files:
            print(f"Обработка файла: {file_path}")
            results = self.parser.parse_excel(file_path)
            for result in results:
                result['source_file'] = os.path.basename(file_path)
                all_results.append(result)

        return all_results
""",
    "project/src/services/flight_parser_service.py": """from typing import List, Dict, Any, Optional
from src.parsers.field_parser import FieldParser
from src.parsers.coordinate_parser import CoordinateParser
from src.parsers.date_parser import DateParser
from src.entities.flight import FlightData
from src.entities.coordinates import Coordinates


class FlightParserService:
    """Сервис для парсинга сообщений о полетах"""
    
    def __init__(self, code_dictionaries: Dict[str, Any]):
        self.field_parser = FieldParser(code_dictionaries)
        self.coord_parser = CoordinateParser()
        self.date_parser = DateParser()
        
    def parse_single_message(self, message: str) -> FlightData:
        """
        Парсит одно сообщение
        
        Args:
            message: Сообщение для парсинга
            
        Returns:
            Объект FlightData
        """
        fields = self.field_parser.extract_fields(message)
        
        takeoff_coords = None
        landing_coords = None
        takeoff_date = None
        landing_date = None
        
        if fields.get("takeoff_coordinates"):
            takeoff_coords = self.coord_parser.parse(fields["takeoff_coordinates"])
        if fields.get("landing_coordinates"):
            landing_coords = self.coord_parser.parse(fields["landing_coordinates"])
        if fields.get("takeoff_date"):
            takeoff_date = self.date_parser.parse(fields["takeoff_date"])
        if fields.get("landing_date"):
            landing_date = self.date_parser.parse(fields["landing_date"])
            
        return FlightData(
            flight_identification=fields.get("flight_identification"),
            uav_type=fields.get("uav_type"),
            takeoff_coordinates=takeoff_coords,
            landing_coordinates=landing_coords,
            takeoff_time=fields.get("takeoff_time"),
            landing_time=fields.get("landing_time"),
            takeoff_date=takeoff_date,
            landing_date=landing_date
        )
    
    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        """
        Парсит несколько сообщений
        
        Args:
            messages: Список сообщений
            
        Returns:
            Список объектов FlightData
        """
        return [self.parse_single_message(msg) for msg in messages]
""",
    "project/tests/__init__.py": "",
    "project/tests/test_parsers.py": """import pytest
from src.parsers.message_parser import MessageParser
from src.entities.flight import FlightData


def test_message_parser():
    parser = MessageParser()
    message = "SID/FL123 TYP/BLA DEP/5540N03722E DEST/5545N03730E ATD/1430 ADD/150923"
    
    result = parser.parse_single_message(message)
    
    assert isinstance(result, FlightData)
    assert result.flight_identification == "FL123"
    assert result.uav_type == "BLA"
    assert result.takeoff_coordinates.latitude is not None
    assert result.landing_coordinates.latitude is not None
    assert result.takeoff_time == "1430"
    assert result.takeoff_date["iso"] == "2023-09-15"
""",
    "project/tests/tests_functions.py": """import pytest
from src.parsers.excel_parser import ExcelParser


def test_excel_parser():
    parser = ExcelParser()
    # Placeholder test; add your actual test data
    pass
""",
    "project/requirements.txt": """pandas
geopandas
shapely
openpyxl
pytest
""",
    "project/convert.py": """import geopandas as gpd
import json

# Placeholder for your GeoJSON/PostGIS conversion
def convert_to_geojson(shapefile_path, output_path):
    gdf = gpd.read_file(shapefile_path)
    gdf.to_file(output_path, driver='GeoJSON')
"""
}

def create_project_structure():
    """Создает структуру проекта и заполняет файлы содержимым."""
    base_dir = os.path.abspath("project")
    
    for file_path, content in FILE_CONTENTS.items():
        full_path = os.path.join(base_dir, file_path)
        directory = os.path.dirname(full_path)
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Создан файл: {full_path}")
            
        except OSError as e:
            if e.errno == errno.EACCES:
                print(f"Ошибка: Нет прав для записи файла {full_path}")
            elif e.errno == errno.ENOSPC:
                print(f"Ошибка: Недостаточно места на диске для {full_path}")
            else:
                print(f"Ошибка при создании файла {full_path}: {e}")
                
        except Exception as e:
            print(f"Неизвестная ошибка при обработке файла {full_path}: {e}")

    # Create empty directories
    empty_dirs = [
        "project/data",
        "project/regions_shapefile"
    ]
    for dir_path in empty_dirs:
        full_dir_path = os.path.join(base_dir, dir_path)
        try:
            os.makedirs(full_dir_path, exist_ok=True)
            print(f"Создана директория: {full_dir_path}")
        except OSError as e:
            print(f"Ошибка при создании директории {full_dir_path}: {e}")

if __name__ == "__main__":
    print("Создание структуры проекта...")
    create_project_structure()
    print("Создание завершено!")
```