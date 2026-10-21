"""Занятие 3: создаём очищенную копию данных без точных дубликатов.

Исходный Excel никогда не перезаписывается. Результат сохраняется отдельно.
"""

from pathlib import Path

import pandas as pd


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_FOLDER / "data" / "input" / "online_retail_II.xlsx"
OUTPUT_FILE = PROJECT_FOLDER / "output" / "01_without_exact_duplicates.xlsx"
SHEET_NAME = "Year 2010-2011"
ROWS_TO_READ = 5_000


def main() -> None:
    # raw_sales — неизменяемая исходная выборка в памяти.
    raw_sales = pd.read_excel(
        DATA_FILE,
        sheet_name=SHEET_NAME,
        nrows=ROWS_TO_READ,
    )

    # drop_duplicates() по умолчанию сохраняет первую запись каждой группы
    # и удаляет только её точные последующие копии.
    clean_sales = raw_sales.drop_duplicates().copy()

    removed_rows = len(raw_sales) - len(clean_sales)
    expected_removed_rows = raw_sales.duplicated().sum()

    # Проверка защищает от незаметной ошибки в логике очистки.
    assert removed_rows == expected_removed_rows, (
        "Количество удалённых строк не совпадает с числом точных копий."
    )

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    clean_sales.to_excel(OUTPUT_FILE, index=False, sheet_name="Cleaned sales")

    # Повторно открываем созданный файл: так проверяем не только расчёт
    # в памяти, но и то, что Excel-файл сохранился корректно.
    saved_sales = pd.read_excel(OUTPUT_FILE, sheet_name="Cleaned sales")
    assert len(saved_sales) == len(clean_sales), (
        "В сохранённом Excel изменилось число строк."
    )

    print(f"Исходных строк: {len(raw_sales):,}")
    print(f"Удалено точных копий: {removed_rows:,}")
    print(f"Осталось строк: {len(clean_sales):,}")
    print(f"Очищенная копия: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
