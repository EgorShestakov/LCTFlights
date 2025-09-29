# import pytest
# import sys
# import os
# from datetime import datetime
#
# # Добавляем путь к родительской папке для импорта uav_parser.py
# # sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#
# from ..uav_parser import UAVFlightParser
#
#
# class TestUAVFlightParser:
#
#     def setup_method(self):
#         """Инициализация парсера перед каждым тестом"""
#         self.parser = UAVFlightParser()
#
#     def test_parse_single_message_flight001(self):
#         """Тест парсинга первого сообщения с полными данными"""
#         message = "-SID FLIGHT001 TYP/BLA DEP/5530N03730E DEST/5535N03735E ATD/0830 ATA/0930 ADD/151223 ADA/151223"
#
#         result = self.parser.parse_single_message(message)
#
#         assert result.flight_identification == "FLIGHT001"
#         assert result.uav_type == {"type": "BLA"}
#         assert result.takeoff_coordinates.latitude == pytest.approx(55.5, 0.001)
#         assert result.takeoff_coordinates.longitude == pytest.approx(37.5, 0.001)
#         assert result.landing_coordinates.latitude == pytest.approx(55.583333, 0.001)
#         assert result.landing_coordinates.longitude == pytest.approx(37.583333, 0.001)
#         assert result.takeoff_time == {"time": "0830"}
#         assert result.landing_time == {"time": "0930"}
#         assert result.takeoff_date == {"date": "151223"}
#         assert result.landing_date == {"date": "151223"}
#         assert result.flight_duration == {"duration": "0100"}
#
#     def test_parse_single_message_flight002(self):
#         """Тест парсинга второго сообщения с DOF вместо ADD/ADA"""
#         message = "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E ATD/0900 ATA/1030 DOF/151223"
#
#         result = self.parser.parse_single_message(message)
#
#         assert result.flight_identification == "FLIGHT002"
#         assert result.uav_type == {"type": "1BLA"}
#         assert result.takeoff_date == {"date": "151223"}
#         assert result.landing_date == {"date": "151223"}
#         assert result.flight_duration == {"duration": "0130"}
#
#     def test_parse_single_complex_message(self):
#         """Тест парсинга сложного сообщения с зоной полета"""
#         message = """ЗЦЗЦ ПАД000 0754
# ФФ УНКУЗДЗЬ
# 290754 УНКУЗДЗИ
# (SHR-ZZZZZ
# -ZZZZ0400
# -M0025/M0027 /ZONA 6837N08005E 6837N08007E 6834N08010E 6836N08022E
# 6843N08026E 6845N08032E 6841N08039E 6840N08036E 6842N08031E
# 6836N08027E 6830N08014E 6837N08005E/
# -ZZZZ1800
# -DEP/6836N08007E DEST/6836N08007E DOF/240102 EET/UNKU0001 UNKL0001
# OPR/ООО ФИНКО REG/0267J81 02K6779 TYP/2BLA RMK/MR091162 MESSOIAHA GT
# WZL/POS 683605N0800635E R 500 M H ABS 0-270 M MONITORING TRUBOPROVODA
# POLET W ZONE H 250-270 M AMSL 220-250 AGL SHR RAZRABOTAL PRP
# AWERXKOW TEL 89127614825 WZAIMODEJSTWIE S ORGANAMI OWD OSUQESTWLIAET
# WNESHNIJ PILOT BWS САЛТЫКОВ 89174927358 89128709162 SID/7771444381)"""
#
#         result = self.parser.parse_single_message(message)
#
#         assert result.flight_identification == "7771444381"
#         assert result.uav_type == {"type": "2BLA"}
#         assert result.takeoff_coordinates.latitude == pytest.approx(68.6, 0.001)
#         assert result.takeoff_coordinates.longitude == pytest.approx(80.116667, 0.001)
#         assert result.landing_coordinates.latitude == pytest.approx(68.6, 0.001)
#         assert result.landing_coordinates.longitude == pytest.approx(80.116667, 0.001)
#         assert result.takeoff_date == {"date": "240102"}
#         assert result.landing_date == {"date": "240102"}
#
#     def test_parse_single_minimal_message(self):
#         """Тест парсинга сообщения с минимальным набором данных"""
#         message = """
#         ЗЦЗЦ ПАД592 0401
#         ФФ УНКУЗДЗЬ УНКЛЗРЗЬ
#         020401 УОООЗТЗЬ
#         (DEP-ZZZZZ-ZZZZ0400-ZZZZ1800
#         -DEP/6836N08007E DEST/6836N08007E DOF/240102
#         REG/0267J81 RMK/MR091162)
#         """
#
#         result = self.parser.parse_single_message(message)
#
#         assert result.takeoff_coordinates.latitude == pytest.approx(68.6, 0.001)
#         assert result.takeoff_coordinates.longitude == pytest.approx(80.116667, 0.001)
#         assert result.takeoff_date == {"date": "240102"}
#
#     def test_parse_single_arrival_message(self):
#         """Тест парсинга сообщения о прибытии"""
#         message = """
#         ЗЦЗЦ ПАТ993 0539
#         ФФ УНКЛЗТЗЬ УНКЛЗФЗЬ УНКЛЗРЗЬ
#         240538 УНКУЗДЗЬ
#         (ARR-RF37373-ZZZZ0530-ZZZZ0538
#         -DEP/5559N09245E DEST/5559N09245E DOF/240124 RMK/ SID/7771472929)
#         """
#
#         result = self.parser.parse_single_message(message)
#
#         assert result.flight_identification == "7771472929"
#         assert result.takeoff_coordinates.latitude == pytest.approx(55.983333, 0.001)
#         assert result.takeoff_coordinates.longitude == pytest.approx(92.75, 0.001)
#         assert result.takeoff_date == {"date": "240124"}
#
#     def test_parse_single_idep_format(self):
#         """Тест парсинга формата IDEP"""
#         message = """
#         -TITLE IDEP
#         -SID 7772271821
#         -ADD 250104
#         -ATD 0030
#         -ADEP ZZZZ
#         -ADEPZ 6049N06937E
#         -PAP 0
#         -REG 0J02194 00Q2171
#         """
#
#         result = self.parser.parse_single_message(message)
#
#         assert result.flight_identification == "7772271821"
#         assert result.takeoff_date == {"date": "250104"}
#         assert result.takeoff_time == {"time": "0030"}
#         assert result.takeoff_coordinates.latitude == pytest.approx(60.816667, 0.001)
#         assert result.takeoff_coordinates.longitude == pytest.approx(69.616667, 0.001)
#
#     def test_parse_multiple_messages(self):
#         """Тест парсинга нескольких сообщений"""
#         messages = [
#             "-SID FLIGHT001 TYP/BLA DEP/5530N03730E DEST/5535N03735E ATD/0830 ATA/0930 ADD/151223 ADA/151223",
#             "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E ATD/0900 ATA/1030 DOF/151223"
#         ]
#
#         results = self.parser.parse_multiple_messages(messages)
#
#         assert len(results) == 2
#         assert results[0].flight_identification == "FLIGHT001"
#         assert results[1].flight_identification == "FLIGHT002"
#         assert results[0].uav_type == {"type": "BLA"}
#         assert results[1].uav_type == {"type": "1BLA"}
#
#     def test_parse_single_invalid_message(self):
#         """Тест парсинга некорректного сообщения"""
#         message = "INVALID MESSAGE FORMAT"
#
#         result = self.parser.parse_single_message(message)
#
#         assert result is not None
#
#     def test_parse_single_empty_message(self):
#         """Тест парсинга пустого сообщения"""
#         message = ""
#
#         result = self.parser.parse_single_message(message)
#
#         assert result is not None
#
#     def test_parse_multiple_with_invalid_messages(self):
#         """Тест парсинга списка сообщений с некорректными"""
#         messages = [
#             "-SID FLIGHT001 TYP/BLA DEP/5530N03730E DEST/5535N03735E",
#             "INVALID MESSAGE",
#             "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E DEST/5235N03725E"
#         ]
#
#         results = self.parser.parse_multiple_messages(messages)
#
#         assert len(results) == 3
#         assert results[0].flight_identification == "FLIGHT001"
#         assert results[2].flight_identification == "FLIGHT002"
#
#     def test_coordinates_parsing(self):
#         """Тест правильности парсинга координат"""
#         test_cases = [
#             ("5530N03730E", (55.5, 37.5)),
#             ("5530S03730W", (-55.5, -37.5)),
#             ("0000N00000E", (0.0, 0.0)),
#         ]
#
#         for coord_str, expected in test_cases:
#             message = f"-SID TEST DEP/{coord_str} DEST/{coord_str}"
#             result = self.parser.parse_single_message(message)
#
#             assert result.takeoff_coordinates.latitude == pytest.approx(expected[0], 0.001)
#             assert result.takeoff_coordinates.longitude == pytest.approx(expected[1], 0.001)
#
#     def test_parser_reusability(self):
#         """Тест что парсер можно использовать многократно"""
#         message1 = "-SID FLIGHT001 TYP/BLA DEP/5530N03730E"
#         message2 = "-SID FLIGHT002 TYP/1BLA DEP/5230N03720E"
#
#         result1 = self.parser.parse_single_message(message1)
#         result2 = self.parser.parse_single_message(message2)
#
#         assert result1.flight_identification == "FLIGHT001"
#         assert result2.flight_identification == "FLIGHT002"
#
#     def test_flight_duration_calculation(self):
#         """Тест расчета продолжительности полета"""
#         messages = [
#             "-SID TEST1 ATD/0800 ATA/0900",  # 1 час
#             "-SID TEST2 ATD/0830 ATA/0930",  # 1 час
#             "-SID TEST3 ATD/0900 ATA/1030",  # 1.5 часа
#         ]
#
#         for message in messages:
#             result = self.parser.parse_single_message(message)
#             assert result.flight_duration is not None
#
#     def test_message_with_special_characters(self):
#         """Тест сообщения со специальными символами"""
#         message = "-SID FLIGHT@123 TYP/BLA-L DEP/5530N03730E DEST/5535N03735E"
#         result = self.parser.parse_single_message(message)
#         assert result.flight_identification == "FLIGHT@123"
#         assert result.uav_type == {"type": "BLA-L"}
#
#
# if __name__ == "__main__":
#     pytest.main([__file__, "-v"])