import json
import os
from typing import Dict, List, Any


def json_to_postgis_regions(json_file_path: str, output_file_path: str = None) -> Dict[str, Any]:
    """
    Преобразует JSON с координатами регионов в PostGIS формат.

    Args:
        json_file_path (str): Путь к исходному JSON файлу
        output_file_path (str, optional): Путь для сохранения результата.

    Returns:
        Dict[str, Any]: Словарь в PostGIS формате
    """

    # Проверяем существование файла
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"Файл {json_file_path} не найден")

    # Проверяем размер файла
    file_size = os.path.getsize(json_file_path)
    if file_size == 0:
        raise ValueError(f"Файл {json_file_path} пустой")

    print(f"Размер файла: {file_size} байт")

    try:
        # Пробуем разные кодировки
        encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(json_file_path, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                    print(f"Попытка чтения с кодировкой {encoding}")
                    print(f"Первые 500 символов: {content[:500]}")

                    if not content:
                        raise ValueError("Файл пустой после чтения")

                    regions_data = json.loads(content)
                    print(f"Успешно прочитано с кодировкой {encoding}")
                    break

            except UnicodeDecodeError:
                print(f"Ошибка кодировки {encoding}, пробуем следующую...")
                continue
            except json.JSONDecodeError as e:
                print(f"Ошибка JSON с кодировкой {encoding}: {e}")
                # Если это последняя попытка, выбросим исключение
                if encoding == encodings[-1]:
                    raise e
                continue
        else:
            raise ValueError("Не удалось прочитать файл ни с одной кодировкой")

    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        # Дополнительная диагностика
        with open(json_file_path, 'rb') as f:
            raw_content = f.read()
            print(f"Сырые данные (первые 200 байт): {raw_content[:200]}")
        raise

    # Создаем структуру для PostGIS
    postgis_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Проверяем структуру данных
    if not isinstance(regions_data, dict):
        raise ValueError(f"Ожидался словарь, получен {type(regions_data)}")

    print(f"Найдено регионов: {len(regions_data)}")

    for region_name, region_data in regions_data.items():
        print(f"Обрабатываем регион: {region_name}")

        # Создаем feature для каждого региона
        feature = {
            "type": "Feature",
            "properties": {
                "name": region_name
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": []
            }
        }

        # Проверяем структуру данных региона
        if not isinstance(region_data, dict):
            print(f"Предупреждение: данные региона {region_name} не являются словарем, пропускаем")
            continue

        polygons = []
        valid_polygons_count = 0

        for polygon_key, polygon_coords in region_data.items():
            # Пропускаем пустые или некорректные данные
            if not polygon_coords or not isinstance(polygon_coords, list):
                continue

            # Проверяем, что координаты валидны
            valid_coords = []
            for coord in polygon_coords:
                if (isinstance(coord, list) and len(coord) == 2 and
                        all(isinstance(x, (int, float)) for x in coord)):
                    valid_coords.append(coord)

            if len(valid_coords) >= 3:  # Полигон должен иметь минимум 3 точки
                # Замыкаем полигон
                if valid_coords[0] != valid_coords[-1]:
                    valid_coords.append(valid_coords[0])

                polygons.append([valid_coords])  # MultiPolygon требует дополнительного уровня
                valid_polygons_count += 1

        print(f"Регион {region_name}: найдено {valid_polygons_count} валидных полигонов")

        if polygons:
            feature["geometry"]["coordinates"] = polygons
            postgis_data["features"].append(feature)
        else:
            print(f"Предупреждение: для региона {region_name} не найдено валидных полигонов")

    print(f"Успешно обработано регионов: {len(postgis_data['features'])}")

    # Сохраняем результат
    if output_file_path:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(postgis_data, f, ensure_ascii=False, indent=2)
            print(f"Результат сохранен в: {output_file_path}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    return postgis_data


# Упрощенная функция для диагностики
def diagnose_json_file(file_path: str):
    """Диагностика проблем с JSON файлом"""
    print(f"=== Диагностика файла {file_path} ===")

    if not os.path.exists(file_path):
        print("Файл не существует")
        return

    file_size = os.path.getsize(file_path)
    print(f"Размер файла: {file_size} байт")

    if file_size == 0:
        print("Файл пустой")
        return

    # Читаем сырые данные
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        print(f"Первые 200 байт: {raw_data[:200]}")
        print(f"Последние 200 байт: {raw_data[-200:]}")

    # Пробуем разные кодировки
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                print(f"\n=== Кодировка {encoding} ===")
                print(f"Длина содержимого: {len(content)} символов")
                print(f"Первые 500 символов: {repr(content[:500])}")

                # Пробуем распарсить JSON
                data = json.loads(content)
                print("✓ JSON валиден!")
                print(f"Тип корневого элемента: {type(data)}")
                if isinstance(data, dict):
                    print(f"Ключи: {list(data.keys())[:5]}...")  # Первые 5 ключей
                return data

        except UnicodeDecodeError as e:
            print(f"✗ Ошибка кодировки: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Ошибка JSON: {e}")
        except Exception as e:
            print(f"✗ Другая ошибка: {e}")

    return None


# Пример использования
if __name__ == "__main__":
    input_file = "../Regions.json"
    output_file = "Regions_postgis.json"

    # Сначала диагностируем файл
    print("Запускаем диагностику...")
    data = diagnose_json_file(input_file)

    if data is not None:
        print("\nФайл валиден, запускаем конвертацию...")
        result = json_to_postgis_regions(input_file, output_file)
        print("Конвертация завершена успешно!")
    else:
        print("\nФайл содержит ошибки, необходимо исправить перед конвертацией")