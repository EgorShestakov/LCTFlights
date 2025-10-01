import json
import logging

from flask import Flask, request, jsonify, send_from_directory, abort
import os
from dev.backend.src.parsers.excel_parser import ExcelParser
from dev.backend.src.parsers.uav_flight_parser import UAVFlightParser
from dev.backend.src.analyzers.region_analyzer import RegionAnalyzer
from glob import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))
FRONTEND_STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'dev', 'frontend', 'public')
FRONTEND_STATS_PATH = os.path.join(FRONTEND_STATIC_FOLDER, 'flight_statistics.json')
FRONTEND_JSON_PATH = os.path.join(FRONTEND_STATIC_FOLDER, 'all_data_from_back.json')
DATA_DIR = os.path.join(PROJECT_ROOT, 'dev', 'backend', 'data')
# app = Flask(__name__, static_folder='dev/frontend/public')

@app.route('/')
def index():
    # app.logger.info(f"Looking for index.html in: {STATIC_FOLDER}")
    # app.logger.info(
    #     f"Files in static folder: {os.listdir(STATIC_FOLDER) if os.path.exists(STATIC_FOLDER) else 'FOLDER NOT EXISTS'}")
    #
    # if not os.path.exists(os.path.join(STATIC_FOLDER, 'index.html')):
    #     app.logger.error("index.html not found!")
    #     return "index.html not found", 500

    return send_from_directory(FRONTEND_STATIC_FOLDER, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route('/flights_percent', methods=['GET'])
def get_flights_percent():
    try:
        if not os.path.exists(FRONTEND_STATS_PATH):
            logging.error(f"File not found: {FRONTEND_STATS_PATH}")
            abort(404, description="Data file not found")

        with open(FRONTEND_STATS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in file: {e}")
        abort(500, description="Invalid data format")
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        abort(500, description="Cannot access data file")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        abort(500, description="Internal server error")


@app.route('/upload', methods=['POST'])
def upload():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for file in request.files.getlist('files'):
        file.save(os.path.join(DATA_DIR, file.filename))
    excel_parser = ExcelParser()
    uav_parser = UAVFlightParser()
    analyzer = RegionAnalyzer()
    excel_files = glob(os.path.join(DATA_DIR, "*.xlsx")) + glob(os.path.join(DATA_DIR, "*.xls"))
    all_flights = []
    for file_path in excel_files:
        flights = excel_parser.parse_excel(file_path, uav_parser)
        all_flights.extend(flights)
    with open(FRONTEND_JSON_PATH, 'w', encoding='utf-8') as f:
        import json
        json.dump([flight.to_dict() for flight in all_flights], f, ensure_ascii=False, indent=4)
    stats = analyzer.compute_flight_statistics(all_flights)
    with open(FRONTEND_STATS_PATH, 'w', encoding='utf-8') as f:
        import json
        json.dump(stats, f, ensure_ascii=False, indent=4)
    return jsonify(stats)

# Other endpoints (not implemented)
@app.route('/flights/filter', methods=['GET'])
def filter_flights():
    pass  # Filter by date/region/etc from all_data_from_back.json

@app.route('/flights/avg_duration', methods=['GET'])
def avg_duration():
    pass  # Compute average flight duration

@app.route('/flights/unique_uavs', methods=['GET'])
def unique_uavs():
    pass  # Count unique UAV types

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
