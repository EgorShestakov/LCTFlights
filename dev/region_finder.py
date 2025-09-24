import geopandas as gpd
from shapely.geometry import Point
import os


class RegionFinder:
    def __init__(self, shapefile_path):
        """
        Инициализация поисковика регионов

        Args:
            shapefile_path: путь к shapefile (без расширения .shp)
        """
        # Проверяем существование файлов
        required_extensions = ['.shp', '.shx', '.dbf', '.prj']
        missing_files = []

        for ext in required_extensions:
            if not os.path.exists(f"{shapefile_path}{ext}"):
                missing_files.append(f"{shapefile_path}{ext}")

        if missing_files:
            raise FileNotFoundError(f"Отсутствуют файлы: {', '.join(missing_files)}")

        # Загружаем shapefile
        self.gdf = gpd.read_file(f"{shapefile_path}.shp")

        # Проверяем наличие нужных колонок
        if 'name' not in self.gdf.columns:
            raise ValueError("В shapefile отсутствует колонка 'name' с названиями регионов")

        print(f"Загружено {len(self.gdf)} регионов")

    def find_region(self, lon, lat):
        """
        Находит регион по координатам

        Args:
            lat: широта (градусы)
            lon: долгота (градусы)

        Returns:
            str: название региона или None, если не найден
        """
        # Создаем точку из координат
        point = Point(lon, lat)  # Обратите внимание: порядок (lon, lat)

        # Ищем регион, содержащий точку
        for idx, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                return row['name']

        return None

    def find_region_with_info(self, lon, lat):
        """
        Находит регион по координатам с дополнительной информацией

        Args:
            lat: широта (градусы)
            lon: долгота (градусы)

        Returns:
            dict: информация о регионе или None
        """
        point = Point(lon, lat)

        for idx, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                return {
                    'name': row['name'],
                    'geometry_type': row.geometry.geom_type,
                    'index': idx
                }

        return None

'''
def flights_percent(coordinates):

    Составляет словарь из всех регионов и количества полётов в них, а потом высчитывает процент для каждого.
    Чтобы составить json из всех регионов, нужно обратиться к файлу LCTFlights/Regions.json - файл с координатами границ всех регионов.

    :param coordinates: список координат вида: [(x1,y1), (x2, y2)]
    x -долгота; y - широта
    :return: словарь(json) вида:
    {
    "1":{
    "name": "Алтайская область",
    "drone_count": p
    },
    "2":{
     "name": "Московская область",
     "drone_count": 50
    }
    }
    где p = количество полётов в этой области/макс.число полётов*100(процент полётов)
    Проверить вхождение координаты в область можно с помощью функции RegionFinder.findregion
    (функция возвращает название области, которой принадлежит данная координата).
    pass
    '''

def flights_percent(coordinates):
    '''
    Составляет словарь из всех регионов и количества полётов в них.
    Процент = (полеты в регионе / общее число полетов по РФ) * 100
    Сумма всех процентов = 100%
    '''
    try:
        region_finder = RegionFinder('./regions_shapefile/regions_shapefile')
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Ошибка в flights_percent: {e}")
        return {}
    
    # Считаем полеты по регионам
    region_counts = {}
    total_flights = len(coordinates)
    
    if total_flights == 0:
        print("⚠️ Нет координат для анализа")
        return {}
    
    print(f"📊 Всего полетов для анализа: {total_flights}")
    
    for i, (lon, lat) in enumerate(coordinates, 1):
        region_name = region_finder.find_region(lat, lon)
        if region_name:
            region_counts[region_name] = region_counts.get(region_name, 0) + 1
            print(f"✅ {i}/{total_flights}: ({lat:.4f}, {lon:.4f}) → {region_name}")
        else:
            print(f"❌ {i}/{total_flights}: ({lat:.4f}, {lon:.4f}) → регион не найден")
    
    if not region_counts:
        print("⚠️ Не найдено ни одного региона для заданных координат")
        return {}
    
    # Формируем результат с правильными процентами
    result = {}
    total_percentage = 0
    
    print("\n📈 Статистика по регионам:")
    print("-" * 40)
    
    for i, (region_name, count) in enumerate(region_counts.items(), 1):
        percentage = (count / total_flights) * 100
        total_percentage += percentage
        
        result[str(i)] = {
            "name": region_name,
            "drone_count": round(percentage, 2),
            "absolute_count": count  # Добавляем абсолютное количество для информации
        }
        
        print(f"📍 {region_name}: {count} полетов ({percentage:.2f}%)")
    
    print(f"📊 Сумма процентов: {total_percentage:.2f}%")
    print(f"🔢 Обработано регионов: {len(region_counts)}")
    
    print(f"результат: {result}")
    
    return result

# Использование
# def main():
#     # Инициализируем поисковик
#     try:
#         region_finder = RegionFinder('./regions_shapefile/regions_shapefile')
#     except (FileNotFoundError, ValueError) as e:
#         print(f"Ошибка загрузки shapefile: {e}")
#         return

#     # Примеры координат для тестирования
#     test_coordinates = [
#         (85.0, 52.5),  # Пример координат в Алтайском крае
#         (37.6, 55.7),  # Москва
#         (30.3, 59.9),  # Санкт-Петербург
#         (84, 57)       # Томск
#     ]

#     for lon, lat in test_coordinates:
#         region = region_finder.find_region(lat, lon)
#         if region:
#             print(f"Координаты ({lat}, {lon}) принадлежат региону: {region}")
#         else:
#             print(f"Координаты ({lat}, {lon}) не принадлежат ни одному региону")

def main():
    # Инициализируем поисковик
    try:
        region_finder = RegionFinder('./regions_shapefile/regions_shapefile')
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
    
    result = flights_percent(flight_coords)
    
    if result:
        print("Результат в формате JSON:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Функция вернула пустой результат")



if __name__ == "__main__":
    main()