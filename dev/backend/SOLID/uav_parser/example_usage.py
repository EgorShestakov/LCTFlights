"""
Пример использования UAV парсера
"""

from uav_parser import UAVFlightParser


def main():
    # Создаем экземпляр парсера
    parser = UAVFlightParser()
    
    # Пример сообщения о полете
    test_messages = [
        "-SID FLIGHT001 TYP/BLA DEP/5530N03730E DEST/5535N03735E ATD/0830 ATA/0930 ADD/151223 ADA/151223",
        "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E ATD/0900 ATA/1030 DOF/151223",
    ]
    
    print("Парсинг одиночного сообщения:")
    result1 = parser.parse_single_message(test_messages[0])
    print(f"Идентификатор полета: {result1.flight_identification}")
    print(f"Тип БПЛА: {result1.uav_type}")
    print(f"Координаты взлета: {result1.takeoff_coordinates}")
    print(f"Продолжительность полета: {result1.flight_duration}")
    print()
    
    print("Парсинг нескольких сообщений:")
    results = parser.parse_multiple_messages(test_messages)
    print(f"Распарсено сообщений: {parser.get_parsed_count()}")
    print()
    
    print("Результаты в JSON:")
    json_output = parser.to_json()
    print(json_output)


if __name__ == "__main__":
    main()
