# import re
# import pandas as pd
# from typing import Optional, Tuple
#
#
# class DataMapper:
#     def __init__(self):
#         self.column_mappings = {
#             'coordinates': {
#                 'takeoff': ['взлет', 'takeoff', 'старт', 'start', 'координаты взлета'],
#                 'landing': ['посадка', 'landing', 'финиш', 'finish', 'координаты посадки'],
#                 'drone_model': ['модель', 'model', 'тип', 'type', 'беспилотник']
#             }
#         }
#
#         self.coord_patterns = [
#             r'(\d+\.\d+)[,\s]+(\d+\.\d+)',
#             r'lat[:\s]*([\d.]+)[,\s]*lon[:\s]*([\d.]+)',
#             r'x[:\s]*([\d.]+)[,\s]*y[:\s]*([\d.]+)'
#         ]
#
#         self.row_patterns = {
#             'drone_model': r'(?:модель|model|тип)[\s:]*([^\n]+)',
#             'takeoff_coords': r'(?:взлет|takeoff|старт)[\s:]*([\d.,\s]+)',
#             'landing_coords': r'(?:посадка|landing|финиш)[\s:]*([\d.,\s]+)'
#         }
#
#     def find_matching_column(self, available_columns, target_keys):
#         for col in available_columns:
#             col_lower = str(col).lower()
#             for key in target_keys:
#                 if key in col_lower:
#                     return col
#         return None
#
#     def extract_coordinates(self, value) -> Optional[Tuple[float, float]]:
#         if pd.isna(value):
#             return None
#
#         value_str = str(value)
#
#         for pattern in self.coord_patterns:
#             match = re.search(pattern, value_str)
#             if match:
#                 try:
#                     lat = float(match.group(1))
#                     lon = float(match.group(2))
#                     return (lat, lon)
#                 except ValueError:
#                     continue
#         return None
#
#     def extract_from_text(self, text: str) -> dict:
#         results = {}
#
#         for field_type, pattern in self.row_patterns.items():
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 value = match.group(1).strip()
#                 if 'coords' in field_type:
#                     coords = self.extract_coordinates(value)
#                     if coords:
#                         results[field_type] = coords
#                 else:
#                     results[field_type] = value
#         return results
#
#
# if __name__ == "__main__":
#     # Тестирование
#     mapper = DataMapper()
#     test_text = "модель: DJI Mavic, взлет: 55.7558, 37.6173"
#     print(mapper.extract_from_text(test_text))