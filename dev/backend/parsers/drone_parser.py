import re
import numpy as np
from typing import Dict, List, Optional
import pandas as pd
# from .data_mapper import DataMapper


class DroneDataParser:
    def __init__(self):
        # self.mapper = DataMapper()
        self.required_fields = ['takeoff_coords', 'landing_coords', 'drone_model']

    def parse_excel(self, file_path: str) -> List[Dict]:
        """Основной метод парсинга Excel-файла"""
        all_data = []

        try:
            xl = pd.ExcelFile(file_path)

            for sheet_name in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_data = self._parse_sheet(df, sheet_name)
                all_data.extend(sheet_data)

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

        return all_data

    def _parse_sheet(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит отдельный лист Excel"""
        results = []

        # Нормализация данных
        df = self._normalize_dataframe(df)

        # Поиск ключевых столбцов
        column_mapping = self._identify_columns(df.columns)

        # Обработка каждой строки
        for idx, row in df.iterrows():
            parsed_row = self._parse_row(row, column_mapping)
            if self._validate_row(parsed_row):
                parsed_row['source_sheet'] = sheet_name
                results.append(parsed_row)

        return results

    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Нормализует DataFrame: очищает заголовки, удаляет пустые строки/столбцы"""
        # Очистка названий столбцов
        df.columns = [str(col).strip().lower() for col in df.columns]

        # Удаление полностью пустых строк и столбцов
        df = df.dropna(how='all')
        df = df.loc[:, ~df.isnull().all()]

        return df

    def _identify_columns(self, columns: List[str]) -> Dict:
        """Идентифицирует назначение каждого столбца"""
        mapping = {}

        # Поиск столбцов с координатами взлета
        takeoff_col = self.mapper.find_matching_column(
            columns, self.mapper.column_mappings['coordinates']['takeoff']
        )
        if takeoff_col:
            mapping['takeoff'] = takeoff_col

        # Поиск столбцов с координатами посадки
        landing_col = self.mapper.find_matching_column(
            columns, self.mapper.column_mappings['coordinates']['landing']
        )
        if landing_col:
            mapping['landing'] = landing_col

        # Поиск модели дрона
        model_col = self.mapper.find_matching_column(
            columns, self.mapper.column_mappings['coordinates']['drone_model']
        )
        if model_col:
            mapping['drone_model'] = model_col

        return mapping

    def _parse_row(self, row: pd.Series, column_mapping: Dict) -> Dict:
        """Парсит отдельную строку данных"""
        result = {}

        # Извлечение координат взлета
        if 'takeoff' in column_mapping:
            coords = self._extract_coordinates(row[column_mapping['takeoff']])
            if coords:
                result['takeoff_coords'] = coords

        # Извлечение координат посадки
        if 'landing' in column_mapping:
            coords = self._extract_coordinates(row[column_mapping['landing']])
            if coords:
                result['landing_coords'] = coords

        # Извлечение модели дрона
        if 'drone_model' in column_mapping:
            model = self._extract_drone_model(row[column_mapping['drone_model']])
            if model:
                result['drone_model'] = model

        return result

    def _extract_coordinates(self, value) -> Optional[tuple]:
        """Извлекает координаты из различных форматов"""
        if pd.isna(value):
            return None

        value_str = str(value)

        for pattern in self.mapper.coord_patterns:
            match = re.search(pattern, value_str)
            if match:
                try:
                    lat = float(match.group(1))
                    lon = float(match.group(2))
                    return (lat, lon)
                except ValueError:
                    continue

        return None

    def _extract_drone_model(self, value) -> Optional[str]:
        """Извлекает модель дрона"""
        if pd.isna(value):
            return None

        # Нормализация названия модели
        model = str(value).strip().upper()

        # Список известных моделей для проверки
        known_models = ['DJI MAVIC', 'PHANTOM', 'INSPIRE', 'MATRICE']
        for known_model in known_models:
            if known_model in model:
                return known_model

        return model

    def _validate_row(self, parsed_row: Dict) -> bool:
        """Проверяет, содержит ли строка минимально необходимые данные"""
        return any(field in parsed_row for field in self.required_fields)