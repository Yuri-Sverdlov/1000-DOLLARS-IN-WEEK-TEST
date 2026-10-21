"""Проверка: независимо считаем полностью одинаковые строки в выборке.

Скрипт читает ровно те же 5 000 строк листа "Year 2010-2011", что и
src/01-03, и считает точные копии всей строки ДВУМЯ независимыми способами:

1. pandas: sales.duplicated() — тот же метод, что в уроках 1-3;
2. чистый Python: строки превращаются в кортежи и считаются Counter.

Если оба способа дают одно число, результат надёжен. Исходный Excel
не меняется, никакой отчёт не создаётся.
"""

from collections import Counter
from pathlib import Path

import pandas as pd


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_FOLDER / "data" / "input" / "online_retail_II.xlsx"
SHEET_NAME = "Year 2010-2011"
ROWS_TO_READ = 5_000

# Пустую ячейку нельзя сравнивать обычным способом: в Python две пустые
# ячейки не равны друг другу. Заменяем её на понятный текст-маркер,
# чтобы пустые значения всё-таки участвовали в сравнении.
EMPTY_MARKER = "<пусто>"

SHOW_GROUPS = 3


def normalize(value: object) -> object:
    """Приводит значение ячейки к виду, пригодному для точного сравнения."""
    if pd.isna(value):
        return EMPTY_MARKER
    return value


def count_with_counter(sales: pd.DataFrame) -> tuple[int, int, int, Counter]:
    """Способ 2: считает копии через кортежи строк и collections.Counter."""
    row_tuples = [
        tuple(normalize(value) for value in row)
        for row in sales.itertuples(index=False, name=None)
    ]
    counter = Counter(row_tuples)

    group_sizes = [count for count in counter.values() if count > 1]
    extra_copies = sum(count - 1 for count in group_sizes)
    matching_rows = sum(group_sizes)
    return extra_copies, matching_rows, len(group_sizes), counter


def times_word(count: int) -> str:
    """Возвращает правильную форму слова «раз» для числа."""
    if count % 10 == 1 and count % 100 != 11:
        return "раз"
    if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return "раза"
    return "раз"


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Не найден исходный файл. Поместите online_retail_II.xlsx в data/input/."
        )

    sales = pd.read_excel(
        DATA_FILE,
        sheet_name=SHEET_NAME,
        nrows=ROWS_TO_READ,
    )

    columns = sales.columns.tolist()

    # Способ 1 — первым способом пользуемся как в уроках: сравниваем все поля.
    copies_by_pandas = int(sales.duplicated(subset=columns).sum())
    matching_by_pandas = int(
        sales.duplicated(subset=columns, keep=False).sum()
    )

    # Способ 2 — полностью независимая реализация на Counter.
    copies_by_counter, matching_by_counter, groups, counter = count_with_counter(
        sales
    )

    print(f"Файл: {DATA_FILE}")
    print(f"Лист: {SHEET_NAME}")
    print(f"Строк прочитано: {len(sales):,}")
    print(f"Столбцов: {len(columns)}")

    print(f"\nПолностью одинаковых строк: {matching_by_pandas:,}")
    print(f"Лишних точных копий: {copies_by_pandas:,}")
    print(f"Групп совпадений: {groups:,}")
    print(f"Останется строк после удаления копий: {len(sales) - copies_by_pandas:,}")

    print("\nПроверка двумя независимыми способами:")
    print(f"  pandas duplicated():   {copies_by_pandas:,}")
    print(f"  Counter по кортежам:   {copies_by_counter:,}")
    if copies_by_pandas != copies_by_counter:
        raise AssertionError(
            "Способы дали разный результат — доверять числу нельзя."
        )
    print("  результаты совпали: да")

    if not counter:
        print("\nПолностью одинаковых строк в выборке нет.")
        return

    print(f"\n{SHOW_GROUPS} самые крупные группы повторов:")
    for group_number, (row_tuple, count) in enumerate(
        counter.most_common(SHOW_GROUPS), start=1
    ):
        if count <= 1:
            break
        # Ищем номера строк Excel для этой группы.
        positions = [
            number + 2
            for number, other in enumerate(
                sales.itertuples(index=False, name=None)
            )
            if tuple(normalize(value) for value in other) == row_tuple
        ]
        shown_positions = ", ".join(str(p) for p in positions)
        print(
            f"\nГруппа {group_number} — {count} {times_word(count)} "
            f"(строки Excel: {shown_positions}):"
        )
        for name, value in zip(columns, row_tuple):
            print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
