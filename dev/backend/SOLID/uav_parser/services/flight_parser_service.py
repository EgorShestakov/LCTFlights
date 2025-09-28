"""
Сервис для парсинга сообщений о полетах UAV
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uav_entities.flight import FlightData
from parsers.coordinate_parser import CoordinateParser
from parsers.date_parser import DateParser
from parsers.field_parser import FieldParser


class FlightParserService:
    """Основной сервис для парсинга сообщений о полетах БПЛА"""
    
    def __init__(self, code_dictionaries: Dict[str, Any]):
        """
        Инициализация сервиса парсинга
        
        Args:
            code_dictionaries: Словари для расшифровки кодов
        """
        self.code_dictionaries = code_dictionaries
        self.field_parser = FieldParser(code_dictionaries)
        self.coordinate_parser = CoordinateParser()
        self.date_parser = DateParser()

    def _parse_time(self, time_str: str) -> Dict[str, str]:
        """
        Парсит время в формате ЧЧММ
        
        Args:
            time_str: Строка с временем
            
        Returns:
            Словарь с распарсенным временем
        """
        try:
            hours = int(time_str[:2])
            minutes = int(time_str[2:4])

            return {
                "original": time_str,
                "iso": f"{hours:02d}:{minutes:02d}",
                "readable": f"{hours:02d}:{minutes:02d} UTC"
            }
        except Exception:
            return {"original": time_str, "iso": None, "readable": None}

    def _calculate_duration(self, departure_time: str, arrival_time: str,
                          departure_date: str, arrival_date: str) -> Dict[str, Any]:
        """
        Вычисляет продолжительность полета
        
        Args:
            departure_time: Время вылета
            arrival_time: Время прибытия
            departure_date: Дата вылета
            arrival_date: Дата прибытия
            
        Returns:
            Словарь с информацией о продолжительности полета
        """
        try:
            dep_dt = datetime.strptime(f"{departure_date}{departure_time}", "%d%m%y%H%M")
            arr_dt = datetime.strptime(f"{arrival_date}{arrival_time}", "%d%m%y%H%M")

            # Если время прибытия меньше времени вылета, добавляем сутки
            if arr_dt < dep_dt:
                arr_dt += timedelta(days=1)

            duration = arr_dt - dep_dt
            total_minutes = int(duration.total_seconds() / 60)

            return {
                "minutes": total_minutes,
                "hours_minutes": f"{total_minutes // 60}:{total_minutes % 60:02d}",
                "readable": f"{total_minutes} минут ({total_minutes // 60} ч {total_minutes % 60} мин)"
            }
        except Exception:
            return {"minutes": None, "hours_minutes": None, "readable": "Не удалось вычислить"}

    def _transform_value(self, key: str, value: str) -> Any:
        """
        Применяет соответствующее преобразование к значению в зависимости от ключа
        
        Args:
            key: Ключ поля
            value: Значение для преобразования
            
        Returns:
            Преобразованное значение
        """
        if "coordinates" in key:
            return self.coordinate_parser.parse(value)
        elif key == "uav_type":
            return {
                "code": value,
                "description": self.code_dictionaries["uav_type"].get(value, "Неизвестный тип БПЛА")
            }
        elif "date" in key:
            return self.date_parser.parse(value)
        elif "time" in key:
            return self._parse_time(value)
        else:
            return value

    def _handle_dof_field(self, message: str, flight_data: FlightData) -> None:
        """
        Обрабатывает поле DOF (дата полета) если не найдены отдельные даты
        
        Args:
            message: Исходное сообщение
            flight_data: Объект с данными о полете
        """
        if (flight_data.takeoff_date is None and 
            flight_data.landing_date is None and 
            "DOF/" in message):

            dof_match = re.search(r'DOF/(\d{6})', message)
            if dof_match:
                date_obj = self.date_parser.parse(dof_match.group(1))
                flight_data.takeoff_date = date_obj
                flight_data.landing_date = date_obj

    def _calculate_flight_duration(self, flight_data: FlightData) -> None:
        """
        Вычисляет продолжительность полета если есть все необходимые данные
        
        Args:
            flight_data: Объект с данными о полете
        """
        if (flight_data.takeoff_time and flight_data.landing_time and
            flight_data.takeoff_date and flight_data.landing_date):

            duration = self._calculate_duration(
                flight_data.takeoff_time["original"],
                flight_data.landing_time["original"],
                flight_data.takeoff_date["original"],
                flight_data.landing_date["original"]
            )
            flight_data.flight_duration = duration

    def parse_single_message(self, message: str) -> FlightData:
        """
        Парсит одно сообщение о полете
        
        Args:
            message: Сообщение для парсинга
            
        Returns:
            Объект FlightData с распарсенными данными
        """
        # Нормализуем сообщение
        normalized_message = " ".join(message.strip().split())
        
        # Извлекаем поля
        extracted_fields = self.field_parser.extract_fields(normalized_message)
        
        # Создаем объект FlightData
        flight_data = FlightData()
        
        # Заполняем поля с преобразованием значений
        for key, value in extracted_fields.items():
            if value:
                setattr(flight_data, key, self._transform_value(key, value))
                
        # Дополнительная обработка
        self._handle_dof_field(normalized_message, flight_data)
        self._calculate_flight_duration(flight_data)
        
        return flight_data

    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        """
        Парсит несколько сообщений
        
        Args:
            messages: Список сообщений для парсинга
            
        Returns:
            Список объектов FlightData
        """
        return [self.parse_single_message(msg) for msg in messages]
