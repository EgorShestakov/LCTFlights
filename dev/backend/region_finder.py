import geopandas as gpd
from shapely.geometry import Point
import os
import json

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
    "percent": p
    },
    "2":{
     "name": "Московская область",
     "percent": 50
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
        region_finder = RegionFinder('regions_shapefile/regions_shapefile')
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
            "percent": round(percentage, 2),
            # "absolute_count": count  # Добавляем абсолютное количество для информации
        }
        
        print(f"📍 {region_name}: {count} полетов ({percentage:.2f}%)")

    # Загрузка jsonа в файл
    with open('../frontend/data_from_back.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"📊 Сумма процентов: {total_percentage:.2f}%")
    print(f"🔢 Обработано регионов: {len(region_counts)}")
    
    print(f"результат: {result}")
    
    return result


# Использование
def main():
    pass


if __name__ == "__main__":
    main()