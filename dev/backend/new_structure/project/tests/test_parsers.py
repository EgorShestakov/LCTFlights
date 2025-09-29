import pytest
import sys
import os
from datetime import datetime

# Добавляем путь к родительской папке для импорта uav_parser.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

from uav_parser import UAVFlightParser

class TestUAVFlightParser:
    
    def setup_method(self):
        # """Инициализация парсера перед каждым тестом"""
        self.parser = UAVFlightParser()
    
    def test_parse_single_message_flight001(self):
        # """Тест парсинга первого сообщения с полными данными"""
        message = "-SID FLIGHT001 TYP/BLA DEP/5530N03730E DEST/5535N03735E ATD/0830 ATA/0930 ADD/151223 ADA/151223"
        
        result = self.parser.parse_single_message(message)
        
        assert result.flight_identification == "FLIGHT001"
        assert result.uav_type == {"type": "BLA"}
        assert result.takeoff_coordinates.latitude == pytest.approx(55.5, 0.001)
        assert result.takeoff_coordinates.longitude == pytest.approx(37.5, 0.001)
        assert result.landing_coordinates.latitude == pytest.approx(55.583333, 0.001)
        assert result.landing_coordinates.longitude == pytest.approx(37.583333, 0.001)
        assert result.takeoff_time == {"time": "0830"}
        assert result.landing_time == {"time": "0930"}
        assert result.takeoff_date == {"date": "151223"}
        assert result.landing_date == {"date": "151223"}
        assert result.flight_duration == {"duration": "0100"}

    # ... (add the rest of your test code here, as it's long, but in full script include all)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
