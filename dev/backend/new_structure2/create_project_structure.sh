#!/bin/bash

# Expanded script to create the project structure and populate ALL files with full code content
# Run with: sh create_project_structure.sh
# This version includes complete heredocs for every file based on the provided code snippets.

BASE_DIR="project"

# Function to create directory if not exists
create_dir() {
    mkdir -p "$1" || { echo "Error creating directory $1"; return 1; }
    echo "Created directory: $1"
}

# Function to write file content using heredoc
write_file() {
    FILE_PATH="$1"
    CONTENT="$2"

    DIR=$(dirname "$FILE_PATH")
    create_dir "$DIR" || return 1

    # Создаем временный файл с содержимым
    echo "$CONTENT" > "$FILE_PATH"

    if [ $? -eq 0 ]; then
        echo "Created file: $FILE_PATH"
    else
        echo "Error creating file: $FILE_PATH"
    fi
}

# Create base directories
create_dir "$BASE_DIR/data"
create_dir "$BASE_DIR/src/parsers"
create_dir "$BASE_DIR/src/analyzers"
create_dir "$BASE_DIR/src/entities"
create_dir "$BASE_DIR/src/utils"
create_dir "$BASE_DIR/src/services"
create_dir "$BASE_DIR/frontend"
create_dir "$BASE_DIR/regions_shapefile"

# Populate files using heredocs

write_file "$BASE_DIR/config.py" $'
import os

# Paths (relative to project root)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, \'data\')
SHAPEFILE_PATH = os.path.join(ROOT_DIR, \'regions_shapefile\', \'regions_shapefile\')
FRONTEND_JSON_PATH = os.path.join(ROOT_DIR, \'frontend\', \'all_data_from_back.json\')
FRONTEND_STATS_PATH = os.path.join(ROOT_DIR, \'frontend\', \'flight_statistics.json\')

# Required fields for validation
REQUIRED_FIELDS = [\'takeoff_coordinates\', \'landing_coordinates\']
'

write_file "$BASE_DIR/main.py" $'
import os
import json
from config import DATA_DIR, FRONTEND_JSON_PATH, FRONTEND_STATS_PATH
from src.parsers.excel_parser import ExcelParser
from src.analyzers.region_analyzer import RegionAnalyzer
from src.parsers.uav_flight_parser import UAVFlightParser
import glob


def main():
    # Initialize parsers and analyzer
    excel_parser = ExcelParser()
    uav_parser = UAVFlightParser()
    analyzer = RegionAnalyzer()

    # Process Excel files
    excel_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx")) + glob.glob(os.path.join(DATA_DIR, "*.xls"))
    all_flights = []

    for file_path in excel_files:
        print(f"Processing file: {file_path}")
        flights = excel_parser.parse_excel(file_path, uav_parser)
        all_flights.extend(flights)

    # Save flight data to JSON
    os.makedirs(os.path.dirname(FRONTEND_JSON_PATH), exist_ok=True)
    with open(FRONTEND_JSON_PATH, \'w\', encoding=\'utf-8\') as f:
        json.dump([flight.to_dict() for flight in all_flights], f, ensure_ascii=False, indent=4)
    print(f"Output written to {FRONTEND_JSON_PATH}")

    # Compute and save flight statistics
    stats = analyzer.compute_flight_statistics(all_flights)
    os.makedirs(os.path.dirname(FRONTEND_STATS_PATH), exist_ok=True)
    with open(FRONTEND_STATS_PATH, \'w\', encoding=\'utf-8\') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    print(f"Statistics written to {FRONTEND_STATS_PATH}")


if __name__ == "__main__":
    main()
'

write_file "$BASE_DIR/src/parsers/excel_parser.py" $'
import pandas as pd
from typing import List, Dict
from config import REQUIRED_FIELDS
from src.utils.data_mapper import DataMapper
from src.parsers.uav_flight_parser import UAVFlightParser
from src.entities.flight import FlightData


class ExcelParser:
    """Парсер Excel-файлов для извлечения данных о полетах"""

    def __init__(self):
        self.mapper = DataMapper()
        self.required_fields = REQUIRED_FIELDS

    def parse_excel(self, file_path: str, uav_parser: UAVFlightParser) -> List[FlightData]:
        """Парсит Excel-файл, возвращая список объектов FlightData"""
        all_flights = []

        try:
            xl = pd.ExcelFile(file_path)
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if df.empty:
                    continue

                print(f"Processing sheet {sheet_name}")
                flights = self._process_sheet(df, sheet_name, uav_parser)
                all_flights.extend(flights)

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

        return all_flights

    def _process_sheet(self, df: pd.DataFrame, sheet_name: str, uav_parser: UAVFlightParser) -> List[FlightData]:
        """Обрабатывает лист Excel"""
        df = self._normalize_dataframe(df)
        column_mapping = self.mapper.identify_columns(df.columns)

        # Scenario 1: Raw messages (~3 columns, likely SHR/DEP/ARR)
        if len(column_mapping) <= 4:  # Allow some extra columns for safety
            return self._parse_raw_messages(df, sheet_name, uav_parser)

        # Scenario 2: Partially parsed data
        return self._parse_structured_data(df, sheet_name, column_mapping)

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Нормализует DataFrame, пропуская заголовочные строки"""
        for i, row in df.iterrows():
            first_cell = str(row.iloc[0]) if len(row) > 0 and pd.notna(row.iloc[0]) else ""
            if self.mapper.is_record_separator(first_cell) or not any(pd.notna(cell) for cell in row):
                continue
            df = df.iloc[i:].reset_index(drop=True)
            break

        df.columns = [str(col).strip().lower() for col in df.columns]
        df = df.dropna(how=\'all\')
        df = df.loc[:, ~df.isnull().all()]
        return df

    def _parse_raw_messages(self, df: pd.DataFrame, sheet_name: str, uav_parser: UAVFlightParser) -> List[FlightData]:
        """Парсит сырые сообщения SHR/DEP/ARR"""
        results = []
        for _, row in df.iterrows():
            messages = [str(cell) for cell in row if pd.notna(cell) and str(cell).strip()]
            if not messages:
                continue

            # Parse messages into FlightData objects
            flight_data_list = uav_parser.parse_multiple_messages(messages)
            if not flight_data_list:
                continue

            # Merge into a single FlightData object
            merged_flight = flight_data_list[0]  # Start with first (e.g., SHR)
            for flight in flight_data_list[1:]:
                if flight.flight_identification and not merged_flight.flight_identification:
                    merged_flight.flight_identification = flight.flight_identification
                if flight.uav_type and not merged_flight.uav_type:
                    merged_flight.uav_type = flight.uav_type
                if flight.takeoff_coordinates and not merged_flight.takeoff_coordinates:
                    merged_flight.takeoff_coordinates = flight.takeoff_coordinates
                if flight.landing_coordinates and not merged_flight.landing_coordinates:
                    merged_flight.landing_coordinates = flight.landing_coordinates
                if flight.takeoff_time and not merged_flight.takeoff_time:
                    merged_flight.takeoff_time = flight.takeoff_time
                if flight.landing_time and not merged_flight.landing_time:
                    merged_flight.landing_time = flight.landing_time
                if flight.takeoff_date and not merged_flight.takeoff_date:
                    merged_flight.takeoff_date = flight.takeoff_date
                if flight.landing_date and not merged_flight.landing_date:
                    merged_flight.landing_date = flight.landing_date

            if self._validate_row(merged_flight):
                merged_flight.source_sheet = sheet_name
                results.append(merged_flight)

        return results

    def _parse_structured_data(self, df: pd.DataFrame, sheet_name: str, column_mapping: Dict) -> List[FlightData]:
        """Парсит частично структурированные данные"""
        results = []
        for _, row in df.iterrows():
            flight = FlightData()
            for field in [\'flight_identification\', \'uav_type\', \'takeoff_coordinates\',
                          \'landing_coordinates\', \'takeoff_time\', \'landing_time\',
                          \'takeoff_date\', \'landing_date\']:
                if field in column_mapping:
                    value = row[column_mapping[field]]
                    parsed_value = self.mapper.parse_field_value(field, value)
                    if parsed_value:
                        setattr(flight, field, parsed_value)

            if self._validate_row(flight):
                flight.source_sheet = sheet_name
                results.append(flight)

        return results

    def _validate_row(self, flight: FlightData) -> bool:
        """Проверяет наличие обязательных полей"""
        return any(getattr(flight, field) is not None for field in self.required_fields)
'

write_file "$BASE_DIR/src/parsers/uav_flight_parser.py" $'
import json
from typing import List, Dict, Any
from src.services.flight_parser_service import FlightParserService
from src.entities.flight import FlightData


class UAVFlightParser:
    """Парсер сообщений о полетах БПЛА"""

    DEFAULT_CODE_DICTIONARIES = {
        "uav_type": {
            "BLA": "Беспилотный летательный аппарат",
            "1BLA": "Беспилотный летательный аппарат (с уточнением)",
            "2BLA": "Беспилотный летательный аппарат (мультироторный)",
            "AER": "Летательный аппарат аэростатного типа",
            "SHAR": "Аэростат (шар-зонд)"
        },
        "coordinate_prefix": {
            "DEP": "Координаты точки взлета",
            "DEST": "Координаты точки посадки",
            "ADEPZ": "Координаты аэродрома вылета",
            "ADARRZ": "Координаты аэродрома прибытия"
        }
    }

    def __init__(self, code_dictionaries: Dict[str, Any] = None):
        self.code_dictionaries = code_dictionaries or self.DEFAULT_CODE_DICTIONARIES
        self.parser_service = FlightParserService(self.code_dictionaries)
        self.parsed_data = []

    def parse_single_message(self, message: str) -> FlightData:
        result = self.parser_service.parse_single_message(message)
        self.parsed_data.append(result)
        return result

    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        results = self.parser_service.parse_multiple_messages(messages)
        self.parsed_data.extend(results)
        return results

    def to_json(self, indent: int = 2) -> str:
        data_dict = [item.to_dict() for item in self.parsed_data]
        return json.dumps(data_dict, ensure_ascii=False, indent=indent)

    def clear_data(self) -> None:
        self.parsed_data = []
'

write_file "$BASE_DIR/src/services/flight_parser_service.py" $'
from typing import List, Dict, Any
from src.entities.flight import FlightData
from src.utils.data_mapper import DataMapper
import re


class FlightParserService:
    """Сервис для парсинга сообщений о полетах"""

    def __init__(self, code_dictionaries: Dict[str, Any]):
        self.code_dictionaries = code_dictionaries
        self.mapper = DataMapper()

    def parse_single_message(self, message: str) -> FlightData:
        """Парсит одно сообщение"""
        flight = FlightData()
        if not message or not isinstance(message, str):
            return flight

        # Extract fields using DataMapper
        for field, keywords in self.mapper.column_mappings.items():
            for keyword in keywords:
                if keyword.lower() in message.lower():
                    value = self._extract_value(message, keyword)
                    parsed_value = self.mapper.parse_field_value(field, value)
                    if parsed_value:
                        setattr(flight, field, parsed_value)
                    break

        # Handle UAV type from code dictionary
        for code, description in self.code_dictionaries[\'uav_type\'].items():
            if code in message:
                flight.uav_type = description
                break

        # Handle coordinate prefixes
        for prefix in self.code_dictionaries[\'coordinate_prefix\']:
            if prefix in message:
                coords = self.mapper._extract_coordinates(message)
                if coords:
                    if prefix in [\'DEP\', \'ADEPZ\']:
                        flight.takeoff_coordinates = coords
                    elif prefix in [\'DEST\', \'ADARRZ\']:
                        flight.landing_coordinates = coords
                break

        return flight

    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        """Парсит несколько сообщений"""
        return [self.parse_single_message(msg) for msg in messages if msg]

    def _extract_value(self, message: str, keyword: str) -> str:
        """Извлекает значение после ключевого слова"""
        pattern = rf\'{keyword}\s*[:=]?\s*([^\s]+)\'
        match = re.search(pattern, message, re.IGNORECASE)
        return match.group(1) if match else ""
'

write_file "$BASE_DIR/src/utils/data_mapper.py" $'
from typing import Dict, List, Optional, Tuple
import pandas as pd
import re


class DataMapper:
    """Маппер для колонок и полей"""

    def __init__(self):
        self.column_mappings = {
            \'flight_identification\': [\'рейс\', \'flight\', \'sid\', \'pln\', \'п/п\', \'телеграмма pln\'],
            \'uav_type\': [\'тип\', \'type\', \'группа\', \'борт\', \'model\', \'typ\', \'shr\', \'тип вс\', \'борт. номер вс.\'],
            \'takeoff_coordinates\': [\'взлет\', \'takeoff\', \'dep\', \'место вылета\', \'а/в\', \'aftn ап вылета\', \'adepz\', \'вылет\'],
            \'landing_coordinates\': [\'посадка\', \'landing\', \'dest\', \'место посадки\', \'а/п\', \'aftn ап посадки\', \'adarrz\'],
            \'takeoff_time\': [\'время вылета\', \'takeoff time\', \'т выл\', \'atd\', \'вылета факт\', \'время вылета факт.\'],
            \'landing_time\': [\'время посадки\', \'landing time\', \'т пос\', \'ata\', \'посадки факт\', \'время посадки факт.\'],
            \'takeoff_date\': [\'дата\', \'date\', \'полёта\', \'дата вылета\', \'add\'],
            \'landing_date\': [\'дата\', \'date\', \'полёта\', \'дата посадки\', \'ada\']
        }
        self.coord_patterns = [
            r\'(\d+\.\d+)[,\s]+(\d+\.\d+)\',  # Decimal: 55.123,37.456
            r\'(\d{2,4})([NS])(\d{2,5})([EW])\'  # DMS: 5530N03730E
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
        if pd.isna(value):
            return None
        if \'coordinates\' in field_type:
            return self._extract_coordinates(value)
        elif field_type == \'uav_type\':
            return str(value).strip()
        elif \'time\' in field_type:
            return self._extract_time(value)
        elif \'date\' in field_type:
            return self._extract_date(value)
        return str(value).strip()

    def _extract_coordinates(self, value) -> Optional[Tuple[float, float]]:
        """Извлекает координаты из строки"""
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
                            if lat_dir.upper() == \'S\':
                                lat_decimal = -lat_decimal

                            if len(lon_deg_min) == 5:  # ДДДММ
                                lon_deg = int(lon_deg_min[:3])
                                lon_min = int(lon_deg_min[3:5])
                            else:  # ДДДДММ
                                lon_deg = int(lon_deg_min[:4])
                                lon_min = int(lon_deg_min[4:6])
                            lon_decimal = lon_deg + lon_min / 60.0
                            if lon_dir.upper() == \'W\':
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
        text = str(value).strip()
        match = re.match(r\'(\d{2}):?(\d{2})\', text)
        if match:
            return f"{match.group(1)}{match.group(2)}"
        return text

    def _extract_date(self, value) -> Optional[Dict[str, str]]:
        """Извлекает дату в формате ДДММГГ"""
        text = str(value).strip()
        match = re.match(r\'(\d{2})(\d{2})(\d{2})\', text)
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
        separators = [\'===\', \'---\', \'***\', \'январь\', \'февраль\', \'март\', \'апрель\', \'май\', \'июнь\',
                      \'июль\', \'август\', \'сентябрь\', \'октябрь\', \'ноябрь\', \'декабрь\']
        return any(sep.lower() in text.lower() for sep in separators) or text.strip() == ""
'

write_file "$BASE_DIR/src/entities/flight.py" $'
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
'

write_file "$BASE_DIR/src/entities/coordinates.py" $'
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
'

write_file "$BASE_DIR/src/analyzers/region_analyzer.py" $'
import json
import geopandas as gpd
from typing import List, Dict, Tuple
from src.entities.flight import FlightData
from config import SHAPEFILE_PATH


class RegionAnalyzer:
    """Анализатор регионов для полетов БПЛА"""

    def __init__(self):
        self.gdf = gpd.read_file(SHAPEFILE_PATH)

    def flights_percent(self, coordinates: List[Tuple[float, float]]) -> Dict:
        """Вычисляет процентное распределение координат по регионам"""
        # Placeholder: Implement actual logic based on your requirements
        points = gpd.GeoDataFrame(
            geometry=[gpd.points_from_xy([lon], [lat])[0] for lon, lat in coordinates],
            crs="EPSG:4326"
        )
        joined = gpd.sjoin(points, self.gdf, how="left", predicate="within")
        region_counts = joined[\'region_name\'].value_counts().to_dict()
        total = len(coordinates)
        return {region: (count / total * 100) if total > 0 else 0 for region, count in region_counts.items()}

    def extract_coordinates(self, flights: List[FlightData]) -> List[Tuple[float, float]]:
        """Извлекает уникальные координаты взлета (или посадки, если взлета нет)"""
        seen_ids = set()
        coordinates_list = []

        for flight in flights:
            if not flight.flight_identification or flight.flight_identification in seen_ids:
                continue

            coords = flight.get_takeoff_coordinates() or flight.get_landing_coordinates()
            if coords:
                # Convert to (lon, lat)
                lon, lat = coords[1], coords[0]
                coordinates_list.append((lon, lat))
                seen_ids.add(flight.flight_identification)

        return coordinates_list

    def compute_flight_statistics(self, flights: List[FlightData]) -> Dict:
        """Вычисляет статистику полетов и сохраняет в JSON"""
        coordinates = self.extract_coordinates(flights)
        region_percent = self.flights_percent(coordinates)
        return {
            "total_flights": len(flights),
            "unique_coordinates": len(coordinates),
            "region_distribution": region_percent
        }
'

write_file "$BASE_DIR/requirements.txt" $'
pandas
geopandas
shapely
openpyxl
'

echo "Project structure creation completed!"