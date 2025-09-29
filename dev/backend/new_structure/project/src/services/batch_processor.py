import os
import glob
# import pandas as pd
from typing import List, Dict
from src.parsers.excel_parser import ExcelParser  # Dependency

class BatchProcessor:
    def __init__(self, parser: ExcelParser):
        self.parser = parser

    def process_directory(self, directory_path: str) -> List[Dict]:
        """Обрабатывает все Excel-файлы в директории, возвращая список сообщений"""
        all_results = []

        excel_files = glob.glob(os.path.join(directory_path, "*.xlsx")) + \
                      glob.glob(os.path.join(directory_path, "*.xls"))

        for file_path in excel_files:
            print(f"Обработка файла: {file_path}")
            results = self.parser.parse_excel(file_path)
            for result in results:
                result['source_file'] = os.path.basename(file_path)
                all_results.append(result)

        return all_results
