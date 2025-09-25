import region_finder as rf


def test_find_region():
    # Инициализируем поисковик
    try:
        region_finder = rf.RegionFinder('./regions_shapefile/regions_shapefile')
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка загрузки shapefile: {e}")
        return

    # Примеры координат для тестирования
    test_coordinates = [
        (85.0, 52.5),  # Пример координат в Алтайском крае
        (37.6, 55.7),  # Москва
        (30.3, 59.9),  # Санкт-Петербург
        (84, 57)  # Томск
    ]

    for lon, lat in test_coordinates:
        region = region_finder.find_region(lat, lon)
        if region:
            print(f"Координаты ({lat}, {lon}) принадлежат региону: {region}")
        else:
            print(f"Координаты ({lat}, {lon}) не принадлежат ни одному региону")


def test_flights_percent():
    # Инициализируем поисковик
    try:
        region_finder = rf.RegionFinder('./regions_shapefile/regions_shapefile')
        print("✅ Shapefile загружен успешно!")
        print(f"Загружено регионов: {len(region_finder.gdf)}")
        print("Названия регионов:", region_finder.gdf['name'].head().tolist())  # Покажем первые 5
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Ошибка загрузки shapefile: {e}")
        return

    # Примеры координат для тестирования (более реальные)
    test_coordinates = [
        (37.6176, 55.7558),   # Москва (Кремль)
        (30.3351, 59.9343),   # Санкт-Петербург (Эрмитаж)
        (83.7696, 53.3551),   # Барнаул (Алтайский край)
        (135.0718, 48.4802),  # Хабаровск
        (61.4026, 55.1644),   # Челябинск
    ]

    print("\n🔍 Тестирование поиска регионов:")
    print("-" * 50)

    for i, (lon, lat) in enumerate(test_coordinates, 1):
        region = region_finder.find_region(lat, lon)
        if region:
            print(f"{i}. Координаты ({lat:.4f}, {lon:.4f}) → 📍 {region}")
        else:
            print(f"{i}. Координаты ({lat:.4f}, {lon:.4f}) → ❌ Регион не найден")

    # Тестирование функции flights_percent
    print("\n📊 Тестирование flights_percent:")
    print("-" * 50)

    # Создаем тестовые данные с повторениями для статистики
    flight_coords = [
        (37.6176, 55.7558),   # Москва
        (37.6176, 55.7558),   # Москва (еще раз)
        (30.3351, 59.9343),   # СПб
        (83.7696, 53.3551),   # Барнаул
        (83.7696, 53.3551),   # Барнаул
        (83.7696, 53.3551),   # Барнаул
    ]

    result = rf.flights_percent(flight_coords)

    if result:
        print("Результат в формате JSON:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Функция вернула пустой результат")