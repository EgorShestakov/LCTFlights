
import pandas as pd
from typing import List, Dict
from dev.backend.config import REQUIRED_FIELDS
from dev.backend.src.utils.data_mapper import DataMapper
from dev.backend.src.parsers.uav_flight_parser import UAVFlightParser
from dev.backend.src.entities.flight import FlightData


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
        df = df.dropna(how='all')
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
            for field in ['flight_identification', 'uav_type', 'takeoff_coordinates',
                          'landing_coordinates', 'takeoff_time', 'landing_time',
                          'takeoff_date', 'landing_date']:
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

