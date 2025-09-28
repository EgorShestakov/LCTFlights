import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import reader as rd


class UAVFlightParser:
    """Парсер сообщений о полетах БПЛА"""

    # Словари для расшифровки кодов
    CODE_DICTIONARIES = rd.read_json_file("codes.json")
    #  = {
    #     "uav_type": {
    #         "BLA": "Беспилотный летательный аппарат",
    #         "1BLA": "Беспилотный летательный аппарат (с уточнением)",
    #         "2BLA": "Беспилотный летательный аппарат (мультироторный)",
    #         "AER": "Летательный аппарат аэростатного типа",
    #         "SHAR": "Аэростат (шар-зонд)"
    #     },
    #     "coordinate_prefix": {
    #         "DEP": "Координаты точки взлета",
    #         "DEST": "Координаты точки посадки",
    #         "ADEPZ": "Координаты аэродрома вылета",
    #         "ADARRZ": "Координаты аэродрома прибытия"
    #     }
    # }

    def __init__(self):
        self.parsed_data = []

    def parse_coordinates(self, coord_str: str) -> Dict[str, float]:
        """Конвертирует координаты из формата ГГГГNДДДДЕ в десятичные градусы"""
        try:
            # Ищем шаблон координат: цифры+N/S+цифры+E/W
            match = re.search(r'(\d{2,4})([NS])(\d{2,5})([EW])', coord_str.upper())
            if not match:
                return {"original": coord_str, "decimal": None, "dms": None}

            lat_deg_min, lat_dir, lon_deg_min, lon_dir = match.groups()

            # Обрабатываем широту
            if len(lat_deg_min) == 4:  # ГГММ
                lat_deg = int(lat_deg_min[:2])
                lat_min = int(lat_deg_min[2:4])
            else:  # ГГГММ
                lat_deg = int(lat_deg_min[:3])
                lat_min = int(lat_deg_min[3:5])

            lat_decimal = lat_deg + lat_min / 60.0
            if lat_dir == 'S':
                lat_decimal = -lat_decimal

            # Обрабатываем долготу
            if len(lon_deg_min) == 5:  # ДДДММ
                lon_deg = int(lon_deg_min[:3])
                lon_min = int(lon_deg_min[3:5])
            else:  # ДДДДММ
                lon_deg = int(lon_deg_min[:4])
                lon_min = int(lon_deg_min[4:6])

            lon_decimal = lon_deg + lon_min / 60.0
            if lon_dir == 'W':
                lon_decimal = -lon_decimal

            return {
                "original": coord_str,
                "decimal": {
                    "latitude": round(lat_decimal, 6),
                    "longitude": round(lon_decimal, 6)
                },
                "dms": f"{lat_deg}°{lat_min}'{lat_dir} {lon_deg}°{lon_min}'{lon_dir}"
            }
        except Exception as e:
            return {"original": coord_str, "decimal": None, "dms": None, "error": str(e)}

    def parse_date(self, date_str: str) -> Dict[str, Any]:
        """Парсит дату в формате ДДММГГ"""
        try:
            day = int(date_str[:2])
            month = int(date_str[2:4])
            year = int("20" + date_str[4:6])  # Предполагаем 2000+ годы

            return {
                "original": date_str,
                "iso": f"{year:04d}-{month:02d}-{day:02d}",
                "readable": f"{day:02d}.{month:02d}.{year:04d}"
            }
        except:
            return {"original": date_str, "iso": None, "readable": None}

    def parse_time(self, time_str: str) -> Dict[str, Any]:
        """Парсит время в формате ЧЧММ"""
        try:
            hours = int(time_str[:2])
            minutes = int(time_str[2:4])

            return {
                "original": time_str,
                "iso": f"{hours:02d}:{minutes:02d}",
                "readable": f"{hours:02d}:{minutes:02d} UTC"
            }
        except:
            return {"original": time_str, "iso": None, "readable": None}

    def calculate_duration(self, departure_time: str, arrival_time: str,
                           departure_date: str, arrival_date: str) -> Dict[str, Any]:
        """Вычисляет продолжительность полета"""
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
        except:
            return {"minutes": None, "hours_minutes": None, "readable": "Не удалось вычислить"}

    def parse_single_message(self, message: str) -> Dict[str, Any]:
        """Парсит одно сообщение простым поиском подстрок"""

        # Ваш JSON-шаблон для сопоставления
        translate_map = {
            "flight_identification": "SID",
            "uav_type": ["TYP"],
            "takeoff_coordinates": ["DEP", "ADEPZ"],
            "landing_coordinates": ["DEST", "ADARRZ"],
            "takeoff_time": "ATD",
            "landing_time": "ATA",
            "takeoff_date": "ADD",
            "landing_date": "ADA"
        }

        result = {}

        # Преобразуем сообщение в одну строку для поиска
        message_single_line = " ".join(message.strip().split())

        # Обрабатываем каждый ключ и его коды
        for key, codes in translate_map.items():
            value_found = None

            # Если codes - список (несколько вариантов кодов)
            if isinstance(codes, list):
                for code in codes:
                    # Ищем код с / (например "TYP/", "DEP/")
                    pattern = f"{code}/([A-Z0-9]+)"
                    match = re.search(pattern, message_single_line)
                    if match:
                        value_found = match.group(1)
                        break

                    # Ищем код с пробелом (например "-SID ", "-ATD ")
                    pattern = f"-{code}\\s+([A-Z0-9]+)"
                    match = re.search(pattern, message_single_line)
                    if match:
                        value_found = match.group(1)
                        break
            else:
                # Если codes - одиночный код
                code = codes
                # Ищем код с /
                pattern = f"{code}/([A-Z0-9]+)"
                match = re.search(pattern, message_single_line)
                if match:
                    value_found = match.group(1)
                else:
                    # Ищем код с пробелом
                    pattern = f"-{code}\\s+([A-Z0-9]+)"
                    match = re.search(pattern, message_single_line)
                    if match:
                        value_found = match.group(1)

            # Применяем соответствующее преобразование к найденному значению
            if value_found:
                if "coordinates" in key:
                    result[key] = self.parse_coordinates(value_found)
                elif key == "uav_type":
                    result[key] = {
                        "code": value_found,
                        "description": self.CODE_DICTIONARIES["uav_type"].get(value_found, "Неизвестный тип БПЛА")
                    }
                elif "date" in key:
                    result[key] = self.parse_date(value_found)
                elif "time" in key:
                    result[key] = self.parse_time(value_found)
                else:
                    result[key] = value_found
            else:
                result[key] = None

        # Дополнительная обработка для DOF (если не найдены отдельные даты)
        if (result.get("takeoff_date") is None and
                result.get("landing_date") is None and
                "DOF/" in message_single_line):

            dof_match = re.search(r'DOF/(\d{6})', message_single_line)
            if dof_match:
                date_obj = self.parse_date(dof_match.group(1))
                result["takeoff_date"] = date_obj
                result["landing_date"] = date_obj

        # Расчет продолжительности полета
        if (result.get("takeoff_time") and result.get("landing_time") and
                result.get("takeoff_date") and result.get("landing_date")):
            duration = self.calculate_duration(
                result["takeoff_time"]["original"],
                result["landing_time"]["original"],
                result["takeoff_date"]["original"],
                result["landing_date"]["original"]
            )
            result["flight_duration"] = duration

        return result


    def parse_multiple_messages(self, messages: List[str]) -> List[Dict[str, Any]]:
        """Парсит несколько сообщений"""
        results = []
        for message in messages:
            try:
                parsed = self.parse_single_message(message)
                results.append(parsed)
            except Exception as e:
                results.append({"error": f"Ошибка парсинга: {str(e)}", "original_message": message})
        self.parsed_data.append(results)
        return results

    def to_json(self, indent: int = 2) -> str:
        """Возвращает результаты в формате JSON"""
        return json.dumps(self.parsed_data, ensure_ascii=False, indent=indent)


# Пример использования
if __name__ == "__main__":
    parser = UAVFlightParser()

    # Тестовые сообщения
    test_messages = [
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