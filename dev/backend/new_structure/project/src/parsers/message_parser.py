"""
Главный класс парсера сообщений
"""

import json
from typing import List, Dict, Any
from src.services.flight_parser_service import FlightParserService
from src.entities.flight import FlightData


class MessageParser:
    """Парсер сообщений о полетах БПЛА"""
    
    DEFAULT_CODE_DICTIONARIES = {
        "uav_type": {
            "BLA": "Беспилотный летательный аппарат",
            "1BLA": "Беспилотный летательный аппарат (с уточнением)",
            "2BLA": "Беспилотный летательный аппарат (мультироторный)",
            "AER": "Летательный аппарат аэростатного типа",
            "SHAR": "Аэростат (шар-зонд)"
        },
        "coordinate_prefix": {
            "DEP": "Координаты точки взлета",
            "DEST": "Координаты точки посадки",
            "ADEPZ": "Координаты аэродрома вылета",
            "ADARRZ": "Координаты аэродрома прибытия"
        }
    }

    def __init__(self, code_dictionaries: Dict[str, Any] = None):
        """
        Инициализация парсера
        
        Args:
            code_dictionaries: Словари для расшифровки кодов (опционально)
        """
        self.code_dictionaries = code_dictionaries or self.DEFAULT_CODE_DICTIONARIES
        self.parser_service = FlightParserService(self.code_dictionaries)
        self.parsed_data = []

    def parse_single_message(self, message: str) -> FlightData:
        """
        Парсит одно сообщение
        
        Args:
            message: Сообщение для парсинга
            
        Returns:
            Объект FlightData с распарсенными данными
        """
        result = self.parser_service.parse_single_message(message)
        self.parsed_data.append(result)
        return result

    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        """
        Парсит несколько сообщений
        
        Args:
            messages: Список сообщений для парсинга
            
        Returns:
            Список объектов FlightData
        """
        results = self.parser_service.parse_multiple_messages(messages)
        self.parsed_data.extend(results)
        return results

    def to_json(self, indent: int = 2) -> str:
        """
        Возвращает результаты в формате JSON
        
        Args:
            indent: Отступ для форматирования JSON
            
        Returns:
            Строка в формате JSON
        """
        data_dict = [item.to_dict() for item in self.parsed_data]
        return json.dumps(data_dict, ensure_ascii=False, indent=indent)

    def clear_data(self) -> None:
        """Очищает сохраненные данные"""
        self.parsed_data = []

    def get_parsed_count(self) -> int:
        """Возвращает количество распарсенных сообщений"""
        return len(self.parsed_data)

    def extract_unique_takeoff_coordinates(self) -> list:
        """
        Извлекает уникальные координаты взлета

        Returns:
            Список кортежей координат (latitude, longitude) без дубликатов по flight_identification
        """
        seen_ids = set()
        coordinates_list = []

        for flight_data in self.parsed_data:
            if not flight_data.flight_identification:
                continue
            if flight_data.flight_identification in seen_ids:
                continue
            coords = flight_data.get_takeoff_coordinates()
            if coords:
                coordinates_list.append(coords)
                seen_ids.add(flight_data.flight_identification)

        return coordinates_list

    def extract_unique_landing_coordinates(self) -> list:
        """
                Извлекает уникальные координаты посадки из всех распарсенных сообщений

                Returns:
                    Список кортежей координат (latitude, longitude) без дубликатов по flight_identification
                """
        seen_ids = set()
        coordinates_list = []

        for flight_data in self.parsed_data:
            # Пропускаем записи без идентификатора
            if not flight_data.flight_identification:
                continue

            # Если уже видели этот идентификатор, пропускаем
            if flight_data.flight_identification in seen_ids:
                continue

            # Получаем координаты посадки
            coords = flight_data.get_landing_coordinates()
            if coords:
                coordinates_list.append(coords)
                seen_ids.add(flight_data.flight_identification)

        return coordinates_list

    def extract_all_unique_coordinates(self) -> list:
        """
                Извлекает все уникальные координаты (и взлета и посадки) из всех распарсенных сообщений

                Returns:
                    Список кортежей координат (latitude, longitude) без дубликатов по flight_identification
                """
        seen_ids = set()
        coordinates_list = []

        for flight_data in self.parsed_data:
            # Пропускаем записи без идентификатора
            if not flight_data.flight_identification:
                continue

            # Если уже видели этот идентификатор, пропускаем
            if flight_data.flight_identification in seen_ids:
                continue

            # Сначала пробуем взлет, потом посадку
            coords = (flight_data.get_takeoff_coordinates() or
                      flight_data.get_landing_coordinates())

            if coords:
                coordinates_list.append(coords)
                seen_ids.add(flight_data.flight_identification)

        return coordinates_list

    def filter_by_coordinates(self, min_lat: float = None, max_lat: float = None,
                              min_lon: float = None, max_lon: float = None) -> list:
        """
                Фильтрует распарсенные данные по географическим координатам

                Args:
                    min_lat: Минимальная широта
                    max_lat: Максимальная широта
                    min_lon: Минимальная долгота
                    max_lon: Максимальная долгота

                Returns:
                    Список FlightData, отфильтрованный по координатам
                """
        filtered_data = []

        for flight_data in self.parsed_data:
            coords = flight_data.get_takeoff_coordinates()
            if not coords:
                continue

            lat, lon = coords

            # Проверяем границы широты
            if min_lat is not None and lat < min_lat:
                continue
            if max_lat is not None and lat > max_lat:
                continue

            # Проверяем границы долготы
            if min_lon is not None and lon < min_lon:
                continue
            if max_lon is not None and lon > max_lon:
                continue

            filtered_data.append(flight_data)

        return filtered_data

    def get_coordinates_statistics(self) -> dict:
        """
                Возвращает статистику по координатам

                Returns:
                    Словарь со статистикой
                """
        takeoff_coords = []
        landing_coords = []

        for flight_data in self.parsed_data:
            takeoff = flight_data.get_takeoff_coordinates()
            landing = flight_data.get_landing_coordinates()

            if takeoff:
                takeoff_coords.append(takeoff)
            if landing:
                landing_coords.append(landing)

        return {
            "total_flights": len(self.parsed_data),
            "flights_with_takeoff_coords": len(takeoff_coords),
            "flights_with_landing_coords": len(landing_coords),
            "unique_takeoff_locations": len(set(takeoff_coords)),
            "unique_landing_locations": len(set(landing_coords))
        }
