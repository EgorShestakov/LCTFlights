"""
Парсер дат
"""

from .base_parser import BaseParser
from typing import Dict


class DateParser(BaseParser):
    """Парсер дат в формате ДДММГГ"""
    
    def parse(self, date_str: str) -> Dict[str, str]:
        """
        Парсит дату из строкового формата в структурированный вид
        
        Args:
            date_str: Строка с датой в формате ДДММГГ
            
        Returns:
            Словарь с распарсенной датой в различных форматах
        """
        try:
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = int("20" + date_str[4:6])  # Предполагаем 2000+ годы

            return {
                "original": date_str,
                "iso": f"{year:04d}-{month:02d}-{day:02d}",
                "readable": f"{day:02d}.{month:02d}.{year:04d}"
            }
        except Exception:
            return {"original": date_str, "iso": None, "readable": None}
