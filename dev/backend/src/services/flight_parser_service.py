
from typing import List, Dict, Any
from src.entities.flight import FlightData
from src.utils.data_mapper import DataMapper
import re


class FlightParserService:
    """Сервис для парсинга сообщений о полетах"""

    def __init__(self, code_dictionaries: Dict[str, Any]):
        self.code_dictionaries = code_dictionaries
        self.mapper = DataMapper()

    def parse_single_message(self, message: str) -> FlightData:
        """Парсит одно сообщение"""
        flight = FlightData()
        if not message or not isinstance(message, str):
            return flight

        # Extract fields using DataMapper
        for field, keywords in self.mapper.column_mappings.items():
            for keyword in keywords:
                if keyword.lower() in message.lower():
                    value = self._extract_value(message, keyword)
                    parsed_value = self.mapper.parse_field_value(field, value)
                    if parsed_value:
                        setattr(flight, field, parsed_value)
                    break

        # Handle UAV type from code dictionary
        for code, description in self.code_dictionaries['uav_type'].items():
            if code in message:
                flight.uav_type = description
                break

        # Handle coordinate prefixes
        for prefix in self.code_dictionaries['coordinate_prefix']:
            if prefix in message:
                coords = self.mapper._extract_coordinates(message)
                if coords:
                    if prefix in ['DEP', 'ADEPZ']:
                        flight.takeoff_coordinates = coords
                    elif prefix in ['DEST', 'ADARRZ']:
                        flight.landing_coordinates = coords
                break

        return flight

    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        """Парсит несколько сообщений"""
        return [self.parse_single_message(msg) for msg in messages if msg]

    def _extract_value(self, message: str, keyword: str) -> str:
        """Извлекает значение после ключевого слова"""
        pattern = rf'{keyword}\s*[:=]?\s*([^\s]+)'
        match = re.search(pattern, message, re.IGNORECASE)
        return match.group(1) if match else ""

