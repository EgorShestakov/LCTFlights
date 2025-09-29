import geopandas as gpd
from shapely.geometry import Point
import os
import json

from uav_parser import UAVFlightParser

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
        region_finder = RegionFinder('C:/Users/1\PycharmProjects\LCTFlights\dev/backend/regions_shapefile/regions_shapefile')
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка в flights_percent: {e}")
        return {}
    
    # Считаем полеты по регионам
    region_counts = {}
    total_flights = len(coordinates)
    
    if total_flights == 0:
        print("Нет координат для анализа")
        return {}
    
    print(f"Всего полетов для анализа: {total_flights}")
    
    for i, (lat, lon) in enumerate(coordinates, 1):
        region_name = region_finder.find_region(lat, lon)
        if region_name:
            region_counts[region_name] = region_counts.get(region_name, 0) + 1
            print(f"{i}/{total_flights}: ({lat:.4f}, {lon:.4f}) {region_name}")
        else:
            print(f"{i}/{total_flights}: ({lat:.4f}, {lon:.4f}) регион не найден")
    
    if not region_counts:
        print("Не найдено ни одного региона для заданных координат")
        return {}
    
    # Формируем результат с правильными процентами
    result = {}
    total_percentage = 0
    
    print("\nСтатистика по регионам:")
    print("-" * 40)
    
    for i, (region_name, count) in enumerate(region_counts.items(), 1):
        percentage = (count / total_flights) * 100
        total_percentage += percentage
        
        result[str(i)] = {
            "name": region_name,
            "percent": round(percentage, 2),
            # "absolute_count": count  # Добавляем абсолютное количество для информации
        }
        
        print(f"{region_name}: {count} полетов ({percentage:.2f}%)")

    # Загрузка jsonа в файл
    with open('../../frontend/data_from_back.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print(f"Сумма процентов: {total_percentage:.2f}%")
    print(f"Обработано регионов: {len(region_counts)}")
    
    print(f"результат: {result}")
    
    return result


def parse_coordinates_from_strings_list():
    parser = UAVFlightParser()

    # Тестовые сообщения
    test_messages = [
        "-SID FLIGHT001 TYP/BLA DEP/5530N03730E DEST/5535N03735E ATD/0830 ATA/0930 ADD/151223 ADA/151223",
        "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E ATD/0900 ATA/1030 DOF/151223",
        """ЗЦЗЦ ПАД000 0754
ФФ УНКУЗДЗЬ
290754 УНКУЗДЗИ
(SHR-ZZZZZ
-ZZZZ0400
-M0025/M0027 /ZONA 6837N08005E 6837N08007E 6834N08010E 6836N08022E
6843N08026E 6845N08032E 6841N08039E 6840N08036E 6842N08031E
6836N08027E 6830N08014E 6837N08005E/
-ZZZZ1800
-DEP/6836N08007E DEST/6836N08007E DOF/240102 EET/UNKU0001 UNKL0001
OPR/ООО ФИНКО REG/0267J81 02K6779 TYP/2BLA RMK/MR091162 MESSOIAHA GT
WZL/POS 683605N0800635E R 500 M H ABS 0-270 M MONITORING TRUBOPROVODA
POLET W ZONE H 250-270 M AMSL 220-250 AGL SHR RAZRABOTAL PRP
AWERXKOW TEL 89127614825 WZAIMODEJSTWIE S ORGANAMI OWD OSUQESTWLIAET
WNESHNIJ PILOT BWS САЛТЫКОВ 89174927358 89128709162 SID/7771444381)""",
        """(SHR-ZZZZZ
-ZZZZ0400
-M0025/M0027 /ZONA 6837N08005E 6849N07959E 6859N07957E 6859N08003E
6848N08026E 6859N08040E 6902N08057E 6858N08101E 6841N08039E
6833N08027E 6824N08030E 6824N08023E 6837N08005E/
-ZZZZ0600
-DEP/6836N08007E DEST/6836N08007E DOF/250103 EET/UNKL0001 OPR/ООО
ФИНКО REG/0R02080 055N126 TYP/2BLA RMK/MR091355 MESSOIAHA BWS
SUPERCAM S350 GT WZL POS 683605N0800635E H ABS 0 270 M R 500 M W ZONE
H POLETА 250 270 M AMSL 220 240 AGL CELX MONITORING TRUBOPROVODA SHR
RAZRABOTAL PRP ЕЛЫШЕВА TEL 89829906599 WZAIMODEJSTWIE S ORGANAMI OWD
OSUQESTWLIAET WNESHNIJ PILOT BWS АРСЕНЬЕВ 89962984808 89128709162
SID/7772271829)""",
        """
        ЗЦЗЦ ПАД592 0401
ФФ УНКУЗДЗЬ УНКЛЗРЗЬ
020401 УОООЗТЗЬ
(DEP-ZZZZZ-ZZZZ0400-ZZZZ1800
-DEP/6836N08007E DEST/6836N08007E DOF/240102
REG/0267J81 RMK/MR091162)
        """,
        """
        ЗЦЗЦ ПАТ993 0539
ФФ УНКЛЗТЗЬ УНКЛЗФЗЬ УНКЛЗРЗЬ
240538 УНКУЗДЗЬ
(ARR-RF37373-ZZZZ0530-ZZZZ0538
-DEP/5559N09245E DEST/5559N09245E DOF/240124 RMK/ SID/7771472929)
""",
        """
        -TITLE IDEP
-SID 7772271821
-ADD 250104
-ATD 0030
-ADEP ZZZZ
-ADEPZ 6049N06937E
-PAP 0
-REG 0J02194 00Q2171
        """

    ]
    parser.parse_multiple_messages(test_messages)
    takeoff_coords = parser.extract_unique_takeoff_coordinates()
    flights_percent(takeoff_coords)
# Использование
def main():
    pass


if __name__ == "__main__":
    parse_coordinates_from_strings_list()