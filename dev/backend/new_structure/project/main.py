import os
import json
from config import DATA_DIR, FRONTEND_JSON_PATH
from src.services.batch_processor import BatchProcessor
from src.parsers.excel_parser import ExcelParser
from src.parsers.message_parser import MessageParser
from src.analyzers.region_analyzer import RegionAnalyzer

def main():
    # Step 1: Batch process Excel files from data/
    excel_parser = ExcelParser()
    batch_processor = BatchProcessor(excel_parser)
    all_messages = batch_processor.process_directory(DATA_DIR)  # List of dicts: [{'SHR': '...', 'DEP': '...', 'ARR': '...'}, ...]

    # Step 2: Parse messages to FlightData JSONs
    message_parser = MessageParser()
    flight_jsons = []  # List of JSON dicts
    for msg_group in all_messages:
        # Parse each group (SHR/DEP/ARR) into one JSON if possible
        combined_msg = f"{msg_group.get('SHR', '')} {msg_group.get('DEP', '')} {msg_group.get('ARR', '')}".strip()
        if combined_msg:
            flight_data = message_parser.parse_single_message(combined_msg)
            flight_jsons.append(flight_data.to_dict())
        else:
            # Fallback: Parse individually
            for key in ['SHR', 'DEP', 'ARR']:
                msg = msg_group.get(key)
                if msg:
                    flight_data = message_parser.parse_single_message(msg)
                    flight_jsons.append(flight_data.to_dict())

    # Step 3: Extract unique coordinates for analysis
    coordinates = message_parser.extract_all_unique_coordinates()  # From your UAVFlightParser

    # Step 4: Analyze and get region percentages
    analyzer = RegionAnalyzer()
    region_percent_json = analyzer.flights_percent(coordinates)

    # Step 5: Write to frontend JSON (combined results)
    output = {
        'flights': flight_jsons,
        'region_analysis': region_percent_json
    }
    os.makedirs(os.path.dirname(FRONTEND_JSON_PATH), exist_ok=True)
    with open(FRONTEND_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Output written to {FRONTEND_JSON_PATH}")

if __name__ == "__main__":
    main()
