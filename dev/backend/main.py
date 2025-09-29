import pandas as pd
from parsers.universal_parser import UniversalDroneDataParser


def main():
    # Инициализация парсера
    parser = UniversalDroneDataParser()

    # Обработка файла
    try:
        results = parser.parse_excel("drone_data.xlsx")

        # Вывод результатов
        print(f"Обработано записей: {len(results)}")

        if results:
            df = pd.DataFrame(results)
            print("\nПервые 5 записей:")
            print(df.head())

            # Сохранение результатов
            df.to_excel("parsed_results.xlsx", index=False)
            print("\nРезультаты сохранены в parsed_results.xlsx")
        else:
            print("Данные не найдены")

    except Exception as e:
        print(f"Ошибка при обработке: {e}")


if __name__ == "__main__":
    main()