import pandas as pd
from typing import Dict, List
from .drone_parser import DroneDataParser


class UniversalDroneDataParser:
    def __init__(self):
        self.advanced_parser = DroneDataParser()

    def parse_excel(self, file_path: str) -> List[Dict]:
        all_results = []

        try:
            xl = pd.ExcelFile(file_path)

            for sheet_name in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                if df.empty:
                    continue

                methods = [
                    self._try_columns_orientation,
                    self._try_rows_orientation,
                ]

                sheet_results = []
                for method in methods:
                    try:
                        results = method(df, sheet_name)
                        if results and len(results) > len(sheet_results):
                            sheet_results = results
                    except Exception as e:
                        continue

                all_results.extend(sheet_results)

        except Exception as e:
            print(f"Ошибка: {e}")

        return all_results

    def _try_columns_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        return self.advanced_parser._parse_columns_orientation(df, sheet_name)

    def _try_rows_orientation(self, df: pd.DataFrame, sheet_name: str) -> List[Dict]:
        return self.advanced_parser._parse_rows_orientation(df, sheet_name)


if __name__ == "__main__":
    # Тестирование
    parser = UniversalDroneDataParser()