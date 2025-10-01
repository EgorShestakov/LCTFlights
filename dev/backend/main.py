
import os
import json
from config import DATA_DIR, FRONTEND_JSON_PATH, FRONTEND_STATS_PATH
from dev.backend.src.parsers.excel_parser import ExcelParser
from dev.backend.src.analyzers.region_analyzer import RegionAnalyzer
from dev.backend.src.parsers.uav_flight_parser import UAVFlightParser
import glob


def main():
    # Initialize parsers and analyzer
    excel_parser = ExcelParser()
    uav_parser = UAVFlightParser()
    analyzer = RegionAnalyzer()

    # Process Excel files
    excel_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx")) + glob.glob(os.path.join(DATA_DIR, "*.xls"))
    all_flights = []

    for file_path in excel_files:
        print(f"Processing file: {file_path}")
        flights = excel_parser.parse_excel(file_path, uav_parser)
        all_flights.extend(flights)

    # Save flight data to JSON
    os.makedirs(os.path.dirname(FRONTEND_JSON_PATH), exist_ok=True)
    with open(FRONTEND_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump([flight.to_dict() for flight in all_flights], f, ensure_ascii=False, indent=4)
    print(f"Output written to {FRONTEND_JSON_PATH}")

    # Compute and save flight statistics
    stats = analyzer.compute_flight_statistics(all_flights)
    os.makedirs(os.path.dirname(FRONTEND_STATS_PATH), exist_ok=True)
    with open(FRONTEND_STATS_PATH, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    print(f"Statistics written to {FRONTEND_STATS_PATH}")


if __name__ == "__main__":
    main()

