"""
Базовый класс для всех парсеров
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров"""
    
    @abstractmethod
    def parse(self, value: str) -> Any:
        """
        Парсит строковое значение в структурированный формат
        
        Args:
            value: Строка для парсинга
            
        Returns:
            Распарсенное значение
        """
        pass
