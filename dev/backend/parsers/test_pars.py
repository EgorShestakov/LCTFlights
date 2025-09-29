from .batch_processor import BatchProcessor
from .drone_parser import DroneDataParser
import os

data_path = "../data"
file_names = ['2024.xlsx', '2025.xlsx']
# Инициализация парсера
parser = DroneDataParser()
processor = BatchProcessor(parser)


# Обработка директории с файлами
results_df = processor.process_directory(data_path)

# Экспорт результатов
results_df.to_excel("parsed_drone_data.xlsx", index=False)
results_df.to_csv("parsed_drone_data.csv", index=False)

# Анализ результатов
print(f"Обработано записей: {len(results_df)}")
print(f"Уникальных моделей дронов: {results_df['drone_model'].nunique()}")