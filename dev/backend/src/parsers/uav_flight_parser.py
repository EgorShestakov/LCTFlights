
import json
from typing import List, Dict, Any
from src.services.flight_parser_service import FlightParserService
from src.entities.flight import FlightData


class UAVFlightParser:
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
        self.code_dictionaries = code_dictionaries or self.DEFAULT_CODE_DICTIONARIES
        self.parser_service = FlightParserService(self.code_dictionaries)
        self.parsed_data = []

    def parse_single_message(self, message: str) -> FlightData:
        result = self.parser_service.parse_single_message(message)
        self.parsed_data.append(result)
        return result

    def parse_multiple_messages(self, messages: List[str]) -> List[FlightData]:
        results = self.parser_service.parse_multiple_messages(messages)
        self.parsed_data.extend(results)
        return results

    def to_json(self, indent: int = 2) -> str:
        data_dict = [item.to_dict() for item in self.parsed_data]
        return json.dumps(data_dict, ensure_ascii=False, indent=indent)

    def clear_data(self) -> None:
        self.parsed_data = []

