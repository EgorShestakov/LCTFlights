
import os

# Paths (relative to project root)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
SHAPEFILE_PATH = os.path.join(ROOT_DIR, 'regions_shapefile', 'regions_shapefile')
FRONTEND_JSON_PATH = os.path.join(ROOT_DIR, 'frontend', 'all_data_from_back.json')
FRONTEND_STATS_PATH = os.path.join(ROOT_DIR, 'frontend', 'flight_statistics.json')

# Required fields for validation
REQUIRED_FIELDS = ['takeoff_coordinates', 'landing_coordinates']

