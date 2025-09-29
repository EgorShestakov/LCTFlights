import os

import pandas as pd
import re
from typing import Dict, List, Optional, Tuple
from .orientation_detector import TableOrientationDetector


class ExelParcer:
    def __init__(self):
        self.keywords = {
            'drone_model': ['модель', 'model', 'тип', 'type', 'беспилотник', 'дрон'],
            'takeoff': ['взлет', 'takeoff', 'старт', 'start', 'взлёт'],
            'landing': ['посадка', 'landing', 'финиш', 'finish'],
            'coordinates': ['координат', 'coord', 'lat', 'lon', 'широт', 'долгот']
        }

    def parse_excel(self, file_path: str) -> List[Dict]:
        """Парсит Excel файл и возвращает данные"""
        all_results = []

        try:
            # Читаем Excel файл
            xl = pd.ExcelFile(file_path)
            print(f"Найдены листы: {xl.sheet_names}")

            for sheet_name in xl.sheet_names:
                print(f"Обработка листа: {sheet_name}")
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Пропускаем пустые листы
                if df.empty:
                    print("Лист пустой, пропускаем")
                    continue

                # Определяем ориентацию данных
                detector = TableOrientationDetector()
                orientation = detector.detect_orientation(df)
                print(f"Ориентация данных: {orientation}")

                if orientation == 'rows':
                    results = self._parse_rows_orientation(df, sheet_name)
                else:
                    results = self._parse_columns_orientation(df, sheet_name)

                print(f"Найдено записей на листе {sheet_name}: {len(results)}")
                all_results.extend(results)

        except Exception as e:
            print(f"Ошибка при обработке файла: {e}")

        return all_results

    def _detect_orientation(self, df: pd.DataFrame) -> str:
        """Определяет ориентацию данных"""
        if df.empty:
            return 'columns'

        # Проверяем первую строку на наличие ключевых слов
        first_row_score = 0
        for cell in df.iloc[0] if len(df) > 0 else []:
            if pd.notna(cell):
                first_row_score += self._count_keywords(str(cell))

        # Проверяем первый столбец на наличие ключевых слов
        first_col_score = 0
        first_col = df.iloc[:, 0] if len(df.columns) > 0 else pd.Series()
        for cell in first_col:
            if pd.notna(cell):
                first_col_score += self._count_keywords(str(cell))

        print(f"Счетчик ориентации: строки={first_col_score}, столбцы={first_row_score}")

        return 'rows' if first_col_score > first_row_score else 'columns'

    def _count_keywords(self, text: str) -> int:
        """Считает количество ключевых слов в тексте"""
        text_lower = text.lower()
        count = 0

        for key_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    count += 1

        return count

    def _parse_columns_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные с заголовками в столбцах"""
        results = []

        # Очищаем названия столбцов
        df.columns = [str(col).strip().lower() for col in df.columns]
        print(f"Столбцы: {list(df.columns)}")

        # Ищем нужные столбцы
        column_mapping = {}
        for col in df.columns:
            col_lower = str(col).lower()

            if any(keyword in col_lower for keyword in self.keywords['drone_model']):
                column_mapping['drone_model'] = col
            elif any(keyword in col_lower for keyword in self.keywords['takeoff']):
                column_mapping['takeoff'] = col
            elif any(keyword in col_lower for keyword in self.keywords['landing']):
                column_mapping['landing'] = col

        print(f"Найдены столбцы: {column_mapping}")

        # Обрабатываем строки с данными (начиная со второй строки, если первая - заголовок)
        start_row = 1 if len(df) > 1 else 0

        for i in range(start_row, len(df)):
            row_data = {'source_sheet': sheet_name, 'orientation': 'columns'}
            row = df.iloc[i]

            # Извлекаем модель дрона
            if 'drone_model' in column_mapping:
                model = self._extract_drone_model(row[column_mapping['drone_model']])
                if model:
                    row_data['drone_model'] = model

            # Извлекаем координаты взлета
            if 'takeoff' in column_mapping:
                coords = self._extract_coordinates(row[column_mapping['takeoff']])
                if coords:
                    row_data['takeoff_coords'] = coords

            # Извлекаем координаты посадки
            if 'landing' in column_mapping:
                coords = self._extract_coordinates(row[column_mapping['landing']])
                if coords:
                    row_data['landing_coords'] = coords

            # Проверяем, что есть хотя бы одно поле
            if len(row_data) > 2:  # Больше чем source_sheet и orientation
                results.append(row_data)

        return results

    def _parse_rows_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        """Парсит данные с заголовками в строках"""
        results = []
        current_record = {}

        for i in range(len(df)):
            row = df.iloc[i]

            # Пропускаем пустые строки
            if row.isnull().all():
                if current_record:  # Сохраняем текущую запись
                    current_record.update({
                        'source_sheet': sheet_name,
                        'orientation': 'rows'
                    })
                    results.append(current_record)
                    current_record = {}
                continue

            # Ищем ключ и значение в строке
            key, value = self._extract_key_value_from_row(row)

            if key and value is not None:
                if key == 'drone_model':
                    current_record['drone_model'] = value
                elif key == 'takeoff':
                    coords = self._extract_coordinates(value)
                    if coords:
                        current_record['takeoff_coords'] = coords
                elif key == 'landing':
                    coords = self._extract_coordinates(value)
                    if coords:
                        current_record['landing_coords'] = coords

        # Добавляем последнюю запись
        if current_record:
            current_record.update({
                'source_sheet': sheet_name,
                'orientation': 'rows'
            })
            results.append(current_record)

        return results

    def _extract_key_value_from_row(self, row) -> Tuple[Optional[str], Optional[str]]:
        """Извлекает ключ и значение из строки"""
        if len(row) < 2:
            return None, None

        key_cell = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
        value_cell = row.iloc[1] if len(row) > 1 and pd.notna(row.iloc[1]) else None

        if not key_cell or value_cell is None:
            return None, None

        # Определяем тип ключа
        key_lower = key_cell.lower()
        for key_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in key_lower:
                    return key_type, str(value_cell)

        return None, None

    def _extract_drone_model(self, value) -> Optional[str]:
        """Извлекает модель дрона"""
        if pd.isna(value):
            return None

        text = str(value).strip().upper()

        # Проверяем известные модели
        models = ['DJI', 'MAVIC', 'PHANTOM', 'INSPIRE', 'MATRICE', 'AIR']
        for model in models:
            if model in text:
                return text

        return text if text and text != 'NAN' else None

    def _extract_coordinates(self, value) -> Optional[Tuple[float, float]]:
        """Извлекает координаты из значения"""
        if pd.isna(value):
            return None

        text = str(value)

        # Паттерны для координат
        patterns = [
            r'(\d+\.\d+)[,\s]+(\d+\.\d+)',  # 55.7558, 37.6173
            r'(\d+)[°\s]+(\d+\.\d+)[\'″]?[NS][,\s]+(\d+)[°\s]+(\d+\.\d+)[\'″]?[EW]',  # Градусы, минуты
            r'lat[:\s]*([\d.]+)[,\s]*lon[:\s]*([\d.]+)',  # lat:55.7558, lon:37.6173
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) >= 2:
                        lat = float(match.group(1))
                        lon = float(match.group(2))
                        # Проверяем корректность координат
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            return (lat, lon)
                except ValueError:
                    continue

        return None


# Тестирование
def test_with_real_data():
    """Тест с реальными данными"""
    parser = ExelParcer()

    # Создаем реалистичный тестовый файл
    test_data_columns = {
        'Модель БПЛА': ['DJI Mavic 3', 'Autel Evo II', 'Skydio 2'],
        'Точка взлета': ['55.7558, 37.6173', '59.9343, 30.3351', '54.9833, 73.3667'],
        'Точка посадки': ['55.7558, 37.6173', '59.9343, 30.3351', '54.9833, 73.3667'],
        'Оператор': ['Иванов', 'Петров', 'Сидоров']
    }

    test_data_rows = [
        ['Модель дрона', 'DJI Phantom 4', '', ''],
        ['Координаты взлета', '55.7558, 37.6173', '', ''],
        ['Координаты посадки', '55.7560, 37.6175', '', ''],
        ['', '', '', ''],
        ['Модель', 'Autel Evo Lite', '', ''],
        ['Взлет', '59.9343, 30.3351', '', ''],
        ['Посадка', '59.9345, 30.3353', '', '']
    ]

    # Сохраняем тестовые данные
    with pd.ExcelWriter('test_drones.xlsx') as writer:
        pd.DataFrame(test_data_columns).to_excel(writer, sheet_name='Столбцы', index=False)
    with pd.ExcelWriter('test_drones2.xlsx') as writer2:
        pd.DataFrame(test_data_rows).to_excel(writer2, sheet_name='Строки', index=False, header=False)

    # Тестируем парсер
    results1 = parser.parse_excel('test_drones.xlsx')
    results2 = parser.parse_excel('test_drones2.xlsx')

    print(f"\n=== РЕЗУЛЬТАТЫ ===")
    print(f"Всего найдено записей: {len(results1)}")
    print(f"Всего найдено записей: {len(results2)}")

    for i, result in enumerate(results1, 1):
        print(f"\nЗапись {i}:")
        for key, value in result.items():
            print(f"  {key}: {value}")

    for i, result in enumerate(results2, 1):
        print(f"\nЗапись {i}:")
        for key, value in result.items():
            print(f"  {key}: {value}")

    # Очистка
    import time
    time.sleep(1)  # Даем время на закрытие файла
    try:
        os.remove('test_drones.xlsx')
        os.remove('test_drones2.xlsx')
        print("\nТестовый файл удален")
    except:
        print("\nНе удалось удалить тестовый файл")


if __name__ == "__main__":
    test_with_real_data()