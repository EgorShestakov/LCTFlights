
import json
import geopandas as gpd
from typing import List, Dict, Tuple
from src.entities.flight import FlightData
from config import SHAPEFILE_PATH


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

    def compute_flight_statistics(self, flights: List[FlightData]) -> Dict:
        """Вычисляет статистику полетов и сохраняет в JSON"""
        coordinates = self.extract_coordinates(flights)
        region_percent = self.flights_percent(coordinates)
        return {
            "total_flights": len(flights),
            "unique_coordinates": len(coordinates),
            "region_distribution": region_percent
        }

