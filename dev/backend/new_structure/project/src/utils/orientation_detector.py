import pandas as pd


class TableOrientationDetector:
    def __init__(self):
        self.keywords = {
            'drone_model': ['модель', 'model', 'тип', 'type', 'беспилотник', 'дрон'],
            'takeoff': ['взлет', 'takeoff', 'старт', 'start', 'взлёт'],
            'landing': ['посадка', 'landing', 'финиш', 'finish'],
            'coordinates': ['координат', 'coord', 'lat', 'lon', 'широт', 'долгот'],
            'date': ['дата', 'date', 'время', 'time']
        }

    def detect_orientation(self, df: pd.DataFrame) -> str:
        """Определяет ориентацию данных: 'columns' или 'rows'"""
        if df.empty:
            return 'columns'  # по умолчанию

        # Проверяем первые 5 строк и столбцов на наличие ключевых слов
        column_score = self._score_columns(df)
        row_score = self._score_rows(df)

        print(f"Column score: {column_score}, Row score: {row_score}")

        # return 'rows'

        # Почему такое условие?
        if row_score > column_score * 1.2:  # Пороговое значение
            return 'rows'
        else:
            return 'columns'

    def _score_columns(self, df: pd.DataFrame) -> int:
        """Оценивает вероятность того, что заголовки в столбцах"""
        score = 0
        header_row = df.iloc[0] if len(df) > 0 else pd.Series()

        for cell in header_row:
            if pd.notna(cell):
                score += self._contains_keywords(str(cell))

        return score

    def _score_rows(self, df: pd.DataFrame) -> int:
        """Оценивает вероятность того, что заголовки в строках"""
        score = 0

        # Проверяем первый столбец на наличие ключевых слов
        first_column = df.iloc[:, 0] if len(df.columns) > 0 else pd.Series()

        for cell in first_column:
            if pd.notna(cell):
                score += self._contains_keywords(str(cell))

        return score

    def _contains_keywords(self, text: str) -> int:
        """Проверяет наличие ключевых слов в тексте"""
        text_lower = text.lower()
        score = 0

        for key_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    score += 3  # Больший вес для точных совпадений

        # Дополнительные эвристики
        if any(sep in text for sep in [':', '=', '-']):
            score += 1

        return score
