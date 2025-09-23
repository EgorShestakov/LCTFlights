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


# Использование
def main():
    # Инициализируем поисковик
    try:
        region_finder = RegionFinder('./regions_shapefile/regions_shapefile')
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка загрузки shapefile: {e}")
        return

    # Примеры координат для тестирования
    test_coordinates = [
        (85.0, 52.5),  # Пример координат в Алтайском крае
        (37.6, 55.7),  # Москва
        (30.3, 59.9),  # Санкт-Петербург
        (84, 57)
    ]

    for lon, lat in test_coordinates:
        region = region_finder.find_region(lat, lon)
        if region:
            print(f"Координаты ({lat}, {lon}) принадлежат региону: {region}")
        else:
            print(f"Координаты ({lat}, {lon}) не принадлежат ни одному региону")


if __name__ == "__main__":
    main()