"""Первое занятие: безопасно знакомимся с исходными продажами.

Скрипт НИЧЕГО не меняет в Excel. Он читает только первые строки одного листа
и отвечает на вопрос: какие проблемы есть в данных и сколько их.
"""

from pathlib import Path

import pandas as pd


# Path(__file__) — путь к этому скрипту. Так программа работает на любом
# компьютере и не зависит от буквы диска.
PROJECT_FOLDER = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_FOLDER / "data" / "input" / "online_retail_II.xlsx"

# Для первого запуска берём небольшой фрагмент. Позже заменим это значение
# на None и обработаем все строки обоих листов.
SHEET_NAME = "Year 2010-2011"
ROWS_TO_READ = 5_000


def show_examples(title: str, rows: pd.DataFrame, columns: list[str]) -> None:
    """Печатает заголовок и не более трёх строк, подходящих под условие."""
    print(f"\n{title}: {len(rows):,}")
    if rows.empty:
        print("  В этой выборке таких строк нет.")
    else:
        print(rows[columns].head(3).to_string(index=False))


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

    print(f"Лист: {SHEET_NAME}")
    print(f"Строк прочитано: {len(sales):,}")
    print("\nСтолбцы и типы данных:")
    print(sales.dtypes.to_string())

    print("\nПервые пять строк:")
    print(sales.head().to_string(index=False))

    # isna() означает "пустое значение". sum() складывает True как 1,
    # поэтому показывает число пустых ячеек в каждом столбце.
    print("\nПустые значения по столбцам:")
    print(sales.isna().sum().to_string())

    # duplicated() сравнивает все значения строки с другими строками.
    exact_duplicates = sales.duplicated().sum()
    print(f"\nПолностью одинаковые строки: {exact_duplicates:,}")

    # Возврат в этом наборе можно распознать двумя независимыми признаками.
    # Мы пока ничего не удаляем: возвраты понадобятся для отдельного отчёта.
    invoice_is_credit = sales["Invoice"].astype(str).str.startswith("C")
    quantity_is_negative = sales["Quantity"] < 0
    returns = sales[invoice_is_credit | quantity_is_negative]

    zero_price = sales["Price"] == 0
    missing_customer = sales["Customer ID"].isna()

    display_columns = [
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "Price",
        "Customer ID",
        "Country",
    ]
    show_examples("Возвраты", returns, display_columns)
    show_examples("Строки с нулевой ценой", sales[zero_price], display_columns)
    show_examples(
        "Строки без Customer ID", sales[missing_customer], display_columns
    )

    # Новая колонка пока существует только в памяти. Она показывает,
    # откуда берётся выручка в будущих отчётах.
    sales["LineRevenue"] = sales["Quantity"] * sales["Price"]
    print(
        "\nПример расчёта выручки строки "
        "(Quantity × Price = LineRevenue):"
    )
    print(
        sales[["Invoice", "Quantity", "Price", "LineRevenue"]]
        .head(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
