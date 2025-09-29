from typing import Dict, List, Optional
import re

class DataMapper:
    """Маппер для колонок и полей"""
    
    def __init__(self):
        self.column_mappings = {
            'coordinates': {
                'takeoff': ['dep', 'takeoff', 'взлет', 'adepz'],
                'landing': ['dest', 'landing', 'посадка', 'adarrz'],
                'drone_model': ['typ', 'model', 'тип', 'bort']
            }
        }
        self.coord_patterns = [r'(\d+\.\d+)[,\s]+(\d+\.\d+)', ...]  # Your patterns

    def identify_columns(self, columns: List[str]) -> Dict:
        mapping = {}
        for field, keywords in self.column_mappings['coordinates'].items():
            for col in columns:
                if any(kw.lower() in str(col).lower() for kw in keywords):
                    mapping[field] = col
                    break
        return mapping

    def classify_field(self, field_name: str) -> Optional[str]:
        field_lower = field_name.lower()
        field_mappings = {
            'takeoff_coords': ['взлет', 'takeoff', 'dep'],
            'landing_coords': ['посадка', 'landing', 'dest'],
            'drone_model': ['модель', 'model', 'typ']
        }
        for field_type, keywords in field_mappings.items():
            if any(kw in field_lower for kw in keywords):
                return field_type
        return None

    def parse_field_value(self, field_type: str, value) -> Optional[any]:
        if 'coords' in field_type:
            return self._extract_coordinates(value)
        elif field_type == 'drone_model':
            return str(value).strip()
        return None

    def _extract_coordinates(self, value):
        # Similar to your _extract_coordinates
        pass  # Implement

    def is_record_separator(self, text: str) -> bool:
        separators = ['===', '---', '***']
        return any(sep in text.lower() for sep in separators) or text.strip() == ""
