"""Занятие 2: отличаем строки одного заказа от полных дубликатов.

Этот скрипт только показывает кандидаты на удаление. Исходный Excel не меняется.
"""

from pathlib import Path

import pandas as pd


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_FOLDER / "data" / "input" / "online_retail_II.xlsx"
SHEET_NAME = "Year 2010-2011"
ROWS_TO_READ = 5_000


def main() -> None:
    sales = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME, nrows=ROWS_TO_READ)

    # Важный момент: проверяем не только Invoice.
    # Сравниваем все исходные столбцы. Тогда две строки считаются одинаковыми,
    # только если у них совпали счёт, товар, количество, цена, клиент, дата и страна.
    source_columns = sales.columns.tolist()

    # По умолчанию duplicated() помечает только вторую и последующие копии.
    # keep=False помечает и первую строку, и её копию — это удобно для проверки.
    later_copies = sales.duplicated(subset=source_columns).sum()
    all_matching_rows = sales[
        sales.duplicated(subset=source_columns, keep=False)
    ].copy()

    # Номера DataFrame начинаются с 0. В Excel первая строка — заголовки,
    # поэтому +2 превращает их в видимые номера строк Excel.
    all_matching_rows.insert(0, "ExcelRow", all_matching_rows.index + 2)

    print(f"Проверено строк: {len(sales):,}")
    print(f"Лишних точных копий: {later_copies:,}")
    print(
        "Строк, участвующих в совпадениях "
        f"(оригиналы и копии вместе): {len(all_matching_rows):,}"
    )

    if all_matching_rows.empty:
        print("\nВ этой выборке точных совпадений нет.")
        return

    print("\nПервые две группы полностью одинаковых строк:")

    # groupby собирает одинаковые строки в группы. dropna=False важно:
    # пустое значение тоже должно участвовать в сравнении.
    groups = all_matching_rows.groupby(
        source_columns,
        dropna=False,
        sort=False,
    )

    for group_number, (_, group) in enumerate(groups, start=1):
        print(f"\nГруппа {group_number}:")
        print(group.to_string(index=False))
        if group_number == 2:
            break

    print(
        "\nВывод: совпадение только номера Invoice — нормально. "
        "Кандидатом на удаление является лишь точная копия всей строки."
    )


if __name__ == "__main__":
    main()
