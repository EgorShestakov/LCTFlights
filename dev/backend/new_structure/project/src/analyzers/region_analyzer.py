import geopandas as gpd
from shapely.geometry import Point
from dev.backend.new_structure.project.config import SHAPEFILE_PATH
from typing import List, Dict

class RegionAnalyzer:
    def __init__(self):
        # Load shapefile
        self.gdf = gpd.read_file(f"{SHAPEFILE_PATH}.shp")
        if 'name' not in self.gdf.columns:
            raise ValueError("Shapefile missing 'name' column")

    def find_region(self, lat, lon) -> str:
        """Находит регион по координатам"""
        point = Point(lon, lat)
        for idx, row in self.gdf.iterrows():
            if row.geometry.contains(point):
                return row['name']
        return None

    def flights_percent(self, coords: List[tuple]) -> Dict:
        """
        Вычисляет проценты полетов по регионам
        
        Args:
            coordinates: Список (lon, lat)
            
        Returns:
            JSON-like dict with regions and percents
        """
        region_counts = {}
        total_flights = len(coords)
        if total_flights == 0:
            return {}

        for lon, lat in coords:
            region_name = self.find_region(lat, lon)
            if region_name:
                region_counts[region_name] = region_counts.get(region_name, 0) + 1

        result = {}
        for i, (name, count) in enumerate(region_counts.items(), 1):
            percent = (count / total_flights) * 100
            result[str(i)] = {"name": name, "percent": round(percent, 2)}

        return result
