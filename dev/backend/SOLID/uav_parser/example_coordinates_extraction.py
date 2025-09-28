"""
Пример использования функциональности извлечения координат
"""

from uav_parser import UAVFlightParser


def main():
    # Создаем экземпляр парсера
    parser = UAVFlightParser()
    
    # Пример сообщений о полетах (включая дубликаты по flight_identification)
    test_messages = [
        "-SID 7772271067 TYP/BLA DEP/5706N06545E DEST/5706N06545E ADD/250101 ADA/250101",
        "-SID 7772271067 TYP/BLA DEP/5706N06545E DEST/5706N06545E ADD/250101 ADA/250101",  # Дубликат
        "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E ATD/0900 ATA/1030 DOF/151223",
        "-SID FLIGHT003 TYP/2BLA DEP/5530N03730E DEST/5535N03735E ATD/0830 ATA/0930 ADD/151223 ADA/151223",
        "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E ATD/0900 ATA/1030 DOF/151223",  # Дубликат
    ]
    
    print("Парсим сообщения...")
    results = parser.parse_multiple_messages(test_messages)
    print(f"Распарсено сообщений: {parser.get_parsed_count()}")
    
    print("\nСтатистика по координатам:")
    stats = parser.get_coordinates_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nУникальные координаты взлета (без дубликатов по flight_identification):")
    takeoff_coords = parser.extract_unique_takeoff_coordinates()
    for i, coords in enumerate(takeoff_coords, 1):
        print(f"  {i}. Широта: {coords[0]:.4f}, Долгота: {coords[1]:.4f}")
    
    print("\nУникальные координаты посадки (без дубликатов по flight_identification):")
    landing_coords = parser.extract_unique_landing_coordinates()
    for i, coords in enumerate(landing_coords, 1):
        print(f"  {i}. Широта: {coords[0]:.4f}, Долгота: {coords[1]:.4f}")
    
    print("\nВсе уникальные координаты (взлет + посадка):")
    all_coords = parser.extract_all_unique_coordinates()
    for i, coords in enumerate(all_coords, 1):
        print(f"  {i}. Широта: {coords[0]:.4f}, Долгота: {coords[1]:.4f}")
    
    print("\nФильтрация по координатам (только европейская часть России):")
    filtered = parser.filter_by_coordinates(min_lat=50.0, max_lat=60.0, min_lon=30.0, max_lon=60.0)
    print(f"Найдено полетов в указанном регионе: {len(filtered)}")
    for flight in filtered:
        coords = flight.get_takeoff_coordinates()
        if coords:
            print(f"  {flight.flight_identification}: {coords[0]:.4f}, {coords[1]:.4f}")


if __name__ == "__main__":
    main()
