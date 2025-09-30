import pandas as pd
from typing import List, Dict, Optional, Tuple
from dev.backend.new_structure.project.config import CHUNKSIZE, REQUIRED_FIELDS
from ..utils.orientation_detector import TableOrientationDetector
from ..utils.data_mapper import DataMapper
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
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if df.empty:
                    continue

                orientation = self.orientation_detector.detect_orientation(df)
                print(f"Processing sheet {sheet_name} with orientation: {orientation}")
                if orientation == 'rows':
                    sheet_data = self._parse_rows_orientation(df, sheet_name)
                elif orientation == 'key_value':
                    sheet_data = self._parse_key_value_rows(df, sheet_name)
                else:
                    sheet_data = self._parse_columns_orientation(df, sheet_name)
                all_data.extend(sheet_data)

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

        return all_data

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
                results.append(self._group_to_messages(parsed_row))

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
        for field in ['flight_identification', 'uav_type', 'takeoff_coordinates',
                      'landing_coordinates', 'takeoff_time', 'landing_time',
                      'takeoff_date', 'landing_date']:
            if field in column_mapping:
                value = row[column_mapping[field]]
                parsed_value = self.mapper.parse_field_value(field, value)
                if parsed_value:
                    result[field] = parsed_value
        return result

    def _group_to_messages(self, parsed_row: Dict) -> Dict:
        """Группирует parsed_row в dict с SHR/DEP/ARR"""
        return {
            'SHR': parsed_row.get('uav_type', ''),
            'DEP': f"DEP/{parsed_row.get('takeoff_coordinates', ('', ''))[0]}" if parsed_row.get(
                'takeoff_coordinates') else '',
            'ARR': f"ARR/{parsed_row.get('landing_coordinates', ('', ''))[0]}" if parsed_row.get(
                'landing_coordinates') else ''
        }

    def _validate_row(self, parsed_row: Dict) -> bool:
        """Проверяет наличие обязательных полей"""
        return any(field in parsed_row for field in self.required_fields)
