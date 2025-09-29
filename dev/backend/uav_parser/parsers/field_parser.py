"""
Парсер полей из сообщения
"""

import re
from typing import Dict, Any, Optional, List, Union


class FieldParser:
    """Парсер для извлечения полей из текстового сообщения"""
    
    def __init__(self, code_dictionaries: Dict[str, Any]):
        """
        Инициализация парсера полей
        
        Args:
            code_dictionaries: Словари для расшифровки кодов
        """
        self.code_dictionaries = code_dictionaries
        self.translate_map = {
            "flight_identification": "SID",
            "uav_type": ["TYP"],
            "takeoff_coordinates": ["DEP", "ADEPZ"],
            "landing_coordinates": ["DEST", "ADARRZ"],
            "takeoff_time": "ATD",
            "landing_time": "ATA",
            "takeoff_date": "ADD",
            "landing_date": "ADA"
        }

    def _find_value_by_code(self, message: str, code: str) -> Optional[str]:
        """
        Ищет значение по конкретному коду в сообщении
        
        Args:
            message: Нормализованное сообщение
            code: Код для поиска
            
        Returns:
            Найденное значение или None
        """
        # Пробуем найти с форматом CODE/VALUE
        pattern_slash = f"{code}/([A-Z0-9]+)"
        match = re.search(pattern_slash, message)
        if match:
            return match.group(1)

        # Пробуем найти с форматом -CODE VALUE
        pattern_space = f"-{code}\\s+([A-Z0-9]+)"
        match = re.search(pattern_space, message)
        if match:
            return match.group(1)

        return None

    def extract_fields(self, message: str) -> Dict[str, Any]:
        """
        Извлекает все поля из сообщения
        
        Args:
            message: Исходное сообщение
            
        Returns:
            Словарь с найденными значениями полей
        """
        result = {}
        
        for key, codes in self.translate_map.items():
            codes_list = codes if isinstance(codes, list) else [codes]
            value = None
            
            for code in codes_list:
                value = self._find_value_by_code(message, code)
                if value:
                    break
                    
            result[key] = value
            
        return result
