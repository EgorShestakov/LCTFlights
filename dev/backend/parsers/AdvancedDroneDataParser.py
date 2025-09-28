from typing import List, Dict, Optional
import pandas as pd

import data_mapper as dp
import orientation_detector as od


class AdvancedDroneDataParser:
    def __init__(self):
        self.orientation_detector = od.TableOrientationDetector()
        self.mapper = dp.DataMapper()

    def parse_excel(self, file_path: str) -> List[Dict]:
        """Парсит Excel-файл с автоматическим определением ориентации"""
        all_data = []

        try:
            xl = pd.ExcelFile(file_path)

            for sheet_name in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Пропускаем полностью пустые листы
                if df.empty:
                    continue

                # Определяем ориентацию данных
                orientation = self.orientation_detector.detect_orientation(df)
                print(f"Лист '{sheet_name}': ориентация - {orientation}")

                if orientation == 'rows':
                    sheet_data = self._parse_rows_orientation(df, sheet_name)
                else:
                    sheet_data = self._parse_columns_orientation(df, sheet_name)

                all_data.extend(sheet_data)

        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

        return all_data

    def _parse_columns_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные в классической ориентации (заголовки в столбцах)"""
        # Используем предыдущую логику для столбцовой ориентации
        df_clean = self._normalize_dataframe(df)
        column_mapping = self._identify_columns(df_clean.columns)

        results = []
        for idx, row in df_clean.iterrows():
            if idx == 0:  # Пропускаем заголовок
                continue

            parsed_row = self._parse_data_row(row, column_mapping)
            if self._validate_row(parsed_row):
                parsed_row['source_sheet'] = sheet_name
                parsed_row['orientation'] = 'columns'
                results.append(parsed_row)

        return results

    def _parse_rows_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные в строчной ориентации (заголовки в строках)"""
        results = []

        # Транспонируем DataFrame для удобства обработки
        df_transposed = df.T
        df_transposed.columns = df_transposed.iloc[0]  # Первая строка становится заголовком
        df_transposed = df_transposed[1:]  # Убираем исходную строку заголовков

        # Обрабатываем как столбцовую ориентацию
        column_mapping = self._identify_columns(df_transposed.columns)

        for idx, row in df_transposed.iterrows():
            parsed_row = self._parse_data_row(row, column_mapping)
            if self._validate_row(parsed_row):
                parsed_row['source_sheet'] = sheet_name
                parsed_row['orientation'] = 'rows'
                results.append(parsed_row)

        return results

    def _parse_key_value_rows(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные в формате ключ-значение (каждая строка - поле)"""
        records = []
        current_record = {}

        for idx, row in df.iterrows():
            if len(row) < 2:
                continue

            key_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            value_cell = row.iloc[1] if len(row) > 1 else None

            # Определяем тип поля по ключу
            field_type = self._classify_field(key_cell)

            if field_type and pd.notna(value_cell):
                parsed_value = self._parse_field_value(field_type, value_cell)
                if parsed_value:
                    current_record[field_type] = parsed_value

            # Если встречаем разделитель или конец данных, сохраняем запись
            if self._is_record_separator(key_cell) or idx == len(df) - 1:
                if current_record and self._validate_row(current_record):
                    current_record['source_sheet'] = sheet_name
                    current_record['orientation'] = 'key_value'
                    records.append(current_record.copy())
                    current_record = {}

        return records

    def _classify_field(self, field_name: str) -> Optional[str]:
        """Классифицирует поле по его названию"""
        field_lower = field_name.lower()

        field_mappings = {
            'takeoff_coords': ['взлет', 'takeoff', 'старт', 'start', 'взлёт'],
            'landing_coords': ['посадка', 'landing', 'финиш', 'finish'],
            'drone_model': ['модель', 'model', 'тип', 'type', 'беспилотник', 'дрон'],
            'flight_date': ['дата', 'date', 'время', 'time'],
            'pilot': ['пилот', 'pilot', 'оператор', 'operator']
        }

        for field_type, keywords in field_mappings.items():
            for keyword in keywords:
                if keyword in field_lower:
                    return field_type

        return None

    def _parse_field_value(self, field_type: str, value) -> Optional[any]:
        """Парсит значение поля в зависимости от его типа"""
        if pd.isna(value):
            return None

        value_str = str(value)

        if 'coords' in field_type:
            return self._extract_coordinates(value_str)
        elif field_type == 'drone_model':
            return self._extract_drone_model(value_str)
        elif field_type == 'flight_date':
            return self._parse_date(value_str)
        else:
            return value_str.strip()

    def _is_record_separator(self, text: str) -> bool:
        """Определяет, является ли строка разделителем записей"""
        separators = ['===', '---', '***', 'запись', 'record', 'flight']
        text_lower = text.lower()

        return any(sep in text_lower for sep in separators) or text.strip() == ""
