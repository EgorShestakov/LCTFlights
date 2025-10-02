
import json
import geopandas as gpd
from typing import List, Dict, Tuple
from dev.backend.src.entities.flight import FlightData
from dev.backend.config import SHAPEFILE_PATH


class RegionAnalyzer:
    """Анализатор регионов для полетов БПЛА"""

    def __init__(self):
        self.gdf = gpd.read_file(SHAPEFILE_PATH + ".shp")

    def flights_percent(self, coordinates: List[Tuple[float, float]]) -> Dict:
        """Вычисляет процентное распределение координат по регионам"""
        # Placeholder: Implement actual logic based on your requirements
        points = gpd.GeoDataFrame(
            geometry=[gpd.points_from_xy([lon], [lat])[0] for lat, lon in coordinates],
            crs="EPSG:4326"
        )
        joined = gpd.sjoin(points, self.gdf, how="left", predicate="within")
        region_counts = joined['name'].value_counts().to_dict()
        total = len(coordinates)
        return {region: (count / total * 100) if total > 0 else 0 for region, count in region_counts.items()}

    def extract_coordinates(self, flights: List[FlightData]) -> List[Tuple[float, float]]:
        """Извлекает уникальные координаты взлета (или посадки, если взлета нет)"""
        seen_ids = set()
        coordinates_list = []

        for flight in flights:
            if not flight.flight_identification or flight.flight_identification in seen_ids:
                continue

            coords = flight.get_takeoff_coordinates() or flight.get_landing_coordinates()
            if coords:
                # Convert to (lon, lat)
                lon, lat = coords[1], coords[0]
                coordinates_list.append((lon, lat))
                seen_ids.add(flight.flight_identification)

        return coordinates_list

    # def compute_flight_statistics(self, flights: List[FlightData]) -> Dict:
    #     """Вычисляет статистику полетов и сохраняет в JSON"""
    #     """Нумерует регионы в соответствии с data.json"""
    #     coordinates = self.extract_coordinates(flights)
    #     region_percent = self.flights_percent(coordinates)
    #     return {
    #         # "total_flights": len(flights),
    #         # "unique_coordinates": len(coordinates),
    #         "region_distribution": region_percent
    #     }
    def compute_flight_statistics(self, flights: List[FlightData]) -> Dict:
        """Вычисляет статистику полетов и возвращает JSON в формате data.json с нумерацией регионов из data.json"""
        coordinates = self.extract_coordinates(flights)
        region_percent = self.flights_percent(coordinates)
        result = {}
        region_id_map = {
            "Республика Адыгея": "1",
            "Республика Башкортостан": "2",
            "Республика Бурятия": "3",
            "Республика Алтай": "4",
            "Республика Дагестан": "5",
            "Республика Ингушетия": "6",
            "Карачаево-Черкесская Республика": "7",
            "Республика Калмыкия": "8",
            "Кабардино-Балкарская Республика": "9",
            "Республика Карелия": "10",
            "Республика Коми": "11",
            "Республика Марий Эл": "12",
            "Республика Мордовия": "13",
            "Республика Саха (Якутия)": "14",
            "Республика Татарстан": "16",
            "Республика Северная Осетия-Алания": "17",
            "Удмуртская Республика": "18",
            "Республика Хакасия": "19",
            "Чеченская Республика": "20",
            "Чувашская Республика": "21",
            "Алтайский край": "22",
            "Краснодарский край": "23",
            "Красноярский край": "24",
            "Приморский край": "25",
            "Ставропольский край": "26",
            "Хабаровский край": "27",
            "Амурская область": "28",
            "Архангельская область": "29",
            "Астраханская область": "30",
            "Белгородская область": "31",
            "Брянская область": "32",
            "Владимирская область": "33",
            "Волгоградская область": "34",
            "Вологодская область": "35",
            "Воронежская область": "36",
            "Ивановская область": "37",
            "Иркутская область": "38",
            "Калининградская область": "39",
            "Калужская область": "40",
            "Камчатский край": "41",
            "Кемеровская область": "42",
            "Кировская область": "43",
            "Костромская область": "44",
            "Курганская область": "45",
            "Курская область": "46",
            "Ленинградская область": "47",
            "Липецкая область": "48",
            "Магаданская область": "49",
            "Московская область": "50",
            "Мурманская область": "51",
            "Нижегородская область": "52",
            "Новгородская область": "53",
            "Новосибирская область": "54",
            "Омская область": "55",
            "Оренбургская область": "56",
            "Орловская область": "57",
            "Пензенская область": "58",
            "Пермский край": "59",
            "Псковская область": "60",
            "Ростовская область": "61",
            "Рязанская область": "62",
            "Самарская область": "63",
            "Саратовская область": "64",
            "Сахалинская область": "65",
            "Свердловская область": "66",
            "Смоленская область": "67",
            "Тамбовская область": "68",
            "Тверская область": "69",
            "Томская область": "70",
            "Тульская область": "71",
            "Тюменская область": "72",
            "Ульяновская область": "73",
            "Челябинская область": "74",
            "Забайкальский край": "75",
            "Ярославская область": "76",
            "г. Москва": "77",
            "г. Санкт-Петербург": "78",
            "Еврейская автономная область": "79",
            "Ненецкий автономный округ": "83",
            "Ханты-Мансийский автономный округ": "86",
            "Чукотский АО": "87",
            "Ямало-Ненецкий автономный округ": "89",
            "Республика Крым": "90",
            "Донецкая Народная Республика": "91",
            "Луганская Народная Республика": "92",
            "Севастополь": "93"
        }
        for region_name, percent in region_percent.items():
            region_id = region_id_map.get(region_name)
            if region_id:
                result[region_id] = {
                    "name": region_name,
                    "drone_count": percent
                }
        return result

