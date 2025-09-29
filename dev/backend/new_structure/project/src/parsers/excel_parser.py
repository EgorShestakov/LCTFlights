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
