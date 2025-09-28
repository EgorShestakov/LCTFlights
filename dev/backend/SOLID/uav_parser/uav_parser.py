"""
Главный класс UAV парсера
"""

import json
from typing import List, Dict, Any
from services.flight_parser_service import FlightParserService
from entities.flight import FlightData


class UAVFlightParser:
    """Парсер сообщений о полетах БПЛА"""
    
    # Словари для расшифровки кодов
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


if __name__ == "__main__":
    parser = UAVFlightParser()

    # Тестовые сообщения
    test_messages = [
        """(SHR-ZZZZZ
-ZZZZ0000
-M0010/M0090 /ZONA USP223/
-ZZZZ2359
-DEP/5706N06545E DEST/5706N06545E DOF/250101 EET/USTR0001 OPR/MUSANOV
ANTON VIKTOROVI4 REG/072D217 TYP/BLA RMK/РАЗРЕШЕНИЕ АДМИНИСТРАЦИИ Г
ТЮМЕНЬ ИСХ 19-08-000652-24 ОТ 25 03 2024 ПОЛЕТЫ В ЗОНАХ USP223 USR913
СОГЛАСОВАНЫ РАЗРЕШЕНИЯ ПРИКАЗ 345 ОТ 22 09 2023 ПИСЬМО ИСХ 1-2944 ОТ
03 10 2023 ЦЕЛЬ ПОЛЕТА ОХРАНА И МОНИТОРИНГ ОБЬЕКТОВ ТЮМЕНСКОГО НПЗ
ТЕЛЕФОН ОТВЕТСТВЕННОГО 8-932-470-8396 SID/7772271067)""",
        """-TITLE IDEP
        -SID 7772270512
        -ADD 250101
        -ATD 0030
        -ADEP ZZZZ
        -ADEPZ 6130N07022E
        -PAP 0
        -REG 0J02194 00Q2171""",

        """-TITLE IARR
                       -SID 7772271232
                       -ADA 250103
                       -ATA 1545
                       -ADARR ZZZZ
                       -ADARRZ 6047N06449E
                       -PAP 0
                       -REG 079J011"""

    ]



    results = parser.parse_multiple_messages(test_messages)
    print(parser.to_json())