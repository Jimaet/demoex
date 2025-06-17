import csv
import sqlite3
import os
import sys

DB_NAME = "materials.db"
CSV_FILE = "materials.csv"
ENCODING = "windows-1251"
SUPPLIERS_CSV = "suppliers.csv"

def load_suppliers(cursor, conn):
    if not os.path.exists(SUPPLIERS_CSV):
        error(f"Файл {SUPPLIERS_CSV} не найден.")
        return

    try:
        with open(SUPPLIERS_CSV, encoding="windows-1251") as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                try:
                    name = row["Наименование поставщика"]
                    rating = int(row["Рейтинг"])
                    start_date = row["Дата начала работы с поставщиком"]

                    cursor.execute("""
                        INSERT INTO suppliers (name, rating, start_date)
                        VALUES (?, ?, ?)
                    """, (name, rating, start_date))
                except Exception as e:
                    error(f"Ошибка при добавлении поставщика '{row}': {e}")
            conn.commit()
            info("Поставщики успешно импортированы.")
    except Exception as e:
        error(f"Ошибка при чтении файла поставщиков: {e}")
def error(msg):
    print(f"❌ ОШИБКА: {msg}", file=sys.stderr)

def info(msg):
    print(f"ℹ️ {msg}")

def main():
    if not os.path.exists(CSV_FILE):
        error(f"Файл {CSV_FILE} не найден. Поместите его в ту же папку, что и скрипт.")
        return

    try:
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS material_suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id INTEGER,
        supplier_id INTEGER,
        FOREIGN KEY(material_id) REFERENCES materials(id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            start_date TEXT NOT NULL
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS product_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            coefficient REAL NOT NULL
        )""")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS material_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type_name TEXT UNIQUE,
            loss_percent REAL NOT NULL DEFAULT 0.0
        )
        """)


        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type_id INTEGER,
            unit_price REAL,
            quantity REAL,
            min_quantity REAL,
            pack_quantity INTEGER,
            unit TEXT,
            FOREIGN KEY (type_id) REFERENCES material_types(id)
        )
        """)
        conn.commit()
        info("Таблицы успешно созданы или уже существуют.")

        type_map = {}
        with open(CSV_FILE, encoding=ENCODING) as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                mat_type = row.get("Тип материала")
                if not mat_type:
                    error("В CSV отсутствует столбец 'Тип материала'.")
                    return
                if mat_type not in type_map:
                    try:
                        cursor.execute("INSERT INTO material_types (type_name) VALUES (?)", (mat_type,))
                        conn.commit()
                        type_map[mat_type] = cursor.lastrowid
                    except sqlite3.Error as e:
                        error(f"Ошибка при добавлении типа материала '{mat_type}': {e}")
                        return
        
        with open(CSV_FILE, encoding=ENCODING) as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                try:
                    name = row["Наименование материала"]
                    type_id = type_map[row["Тип материала"]]
                    price = float(row["Цена единицы материала"].replace(',', '.'))
                    qty = float(row["Количество на складе"].replace(',', '.'))
                    min_qty = float(row["Минимальное количество"].replace(',', '.'))
                    pack_qty = int(row["Количество в упаковке"])
                    unit = row["Единица измерения"]

                    if price < 0 or min_qty < 0:
                        error(f"Отрицательные значения у материала '{name}'. Импорт прерван.")
                        return

                    cursor.execute("""
                        INSERT INTO materials (
                            name, type_id, unit_price, quantity, min_quantity, pack_quantity, unit
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (name, type_id, price, qty, min_qty, pack_qty, unit))

                except KeyError as e:
                    error(f"Отсутствует обязательный столбец: {e}")
                    return
                except ValueError as e:
                    error(f"Ошибка преобразования чисел у материала '{row.get('Наименование материала', '???')}': {e}")
                    return
                except sqlite3.Error as e:
                    error(f"Ошибка SQLite при добавлении материала: {e}")
                    return

            conn.commit()
            info("Материалы успешно импортированы.")

    except Exception as e:
        error(f"Общая ошибка: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    load_suppliers(cursor, conn)
if __name__ == "__main__":
    main()