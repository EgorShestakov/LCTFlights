import os

# Paths (relative to project root)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
SHAPEFILE_PATH = os.path.join(ROOT_DIR, 'regions_shapefile', 'regions_shapefile')
FRONTEND_JSON_PATH = os.path.join(ROOT_DIR, '..', 'frontend', 'data_from_back.json')

# Other configs
CHUNKSIZE = 10000  # For large Excel files
REQUIRED_FIELDS = ['takeoff_coords', 'landing_coords']  # Minimal for analysis
