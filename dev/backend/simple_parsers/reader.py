import os
import json


def read_json_file(filename):
    """
    Читает JSON файл и возвращает его содержимое как словарь
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(filename):
            print(f"Ошибка: Файл '{filename}' не найден")
            return None

        # Открываем и читаем файл
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        print(f"Файл '{filename}' успешно прочитан")
        return data

    except json.JSONDecodeError as e:
        print(f"Ошибка: Файл '{filename}' содержит некорректный JSON")
        print(f"Детали ошибки: {e}")
        return None
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        return None