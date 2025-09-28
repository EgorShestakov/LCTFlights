import pandas as pd
# import drone_parser as dp
from .drone_parser import DroneDataParser


class BatchProcessor:
    def __init__(self, parser: DroneDataParser):
        self.parser = parser

    def process_directory(self, directory_path: str) -> pd.DataFrame:
        """Обрабатывает все Excel-файлы в директории"""
        import os
        import glob

        all_results = []

        excel_files = glob.glob(os.path.join(directory_path, "*.xlsx")) + \
                      glob.glob(os.path.join(directory_path, "*.xls"))

        for file_path in excel_files:
            print(f"Обработка файла: {file_path}")
            results = self.parser.parse_excel(file_path)

            for result in results:
                result['source_file'] = os.path.basename(file_path)
                all_results.append(result)

        return pd.DataFrame(all_results)