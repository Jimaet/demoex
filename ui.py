import sqlite3
import tkinter as tk
from tkinter import messagebox
import math
import csv

def show_suppliers():
    try:
        with open("suppliers.csv", newline='', encoding="windows-1251") as f:
            reader = csv.DictReader(f, delimiter=';')  # Точка с запятой!
  # Табуляция!
            suppliers = list(reader)

        if not suppliers:
            messagebox.showinfo("Поставщики", "Список поставщиков пуст.")
            return

        win = tk.Toplevel()
        win.title("Список поставщиков")
        win.geometry("1920x1080")
          
        tk.Label(win, text="Список поставщиков", font=("Arial", 14, "bold")).pack(pady=10)

        for s in suppliers:
            text = (f"Название: {s['Наименование поставщика']} | "
                    f"Тип: {s['Тип поставщика']} | "
                    f"ИНН: {s['ИНН']} | "
                    f"Рейтинг: {s['Рейтинг']} | "
                    f"С начала работы: {s['Дата начала работы с поставщиком']}")
            tk.Label(win, text=text, anchor="w", justify="left", wraplength=580).pack(fill="x", padx=10, pady=2)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить поставщиков:\n{e}")
        btn_suppliers = tk.Button(root, text="Показать поставщиков", command=show_suppliers, bg="lightblue")
        btn_suppliers.pack(pady=10)  
def calculate_min_purchase(row):
    try:
        qty = row["quantity"]
        min_qty = row["min_quantity"]
        pack_qty = row["pack_quantity"]
        price = row["unit_price"]

        if qty >= min_qty:
            return "0.00"

        need = min_qty - qty
        packs = math.ceil(need / pack_qty)
        total_cost = packs * pack_qty * price
        return f"{total_cost:.2f}"
    except Exception as e:
        messagebox.showerror("Ошибка расчета", f"Не удалось рассчитать стоимость партии:\n{e}")
        return "Ошибка"

def calculate_product_amount(product_type_id, material_type_id, material_amount, param1, param2):
    try:
        if material_amount <= 0 or param1 <= 0 or param2 <= 0:
            return -1

        conn = sqlite3.connect("materials.db")
        cursor = conn.cursor()

        cursor.execute("SELECT coefficient FROM product_types WHERE id = ?", (product_type_id,))
        product_data = cursor.fetchone()
        if not product_data:
            return -1

        cursor.execute("SELECT loss_percent FROM material_types WHERE id = ?", (material_type_id,))
        material_data = cursor.fetchone()
        if not material_data:
            return -1

        product_coefficient = product_data[0]
        loss_percent = material_data[0]

        required_material_per_unit = param1 * param2 * product_coefficient
        adjusted_required = required_material_per_unit * (1 + loss_percent / 100.0)

        result = int(material_amount // adjusted_required)
        return result
    except Exception as e:
        print(f"Ошибка в расчете: {e}")
        return -1

def show_all_suppliers():
    try:
        top_frame = tk.Frame(root)
        top_frame.pack(fill="x")

        supplier_btn = tk.Button(top_frame, text="Список поставщиков", command=show_all_suppliers)
        supplier_btn.pack(side="left", padx=10, pady=5)
        conn = sqlite3.connect("materials.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name, rating, start_date FROM suppliers")
        results = cursor.fetchall()
        if not results:
            messagebox.showinfo("Поставщики", "Список поставщиков пуст.")
            return

        win = tk.Toplevel()
        win.title("Список всех поставщиков")
        win.geometry("500x400")

        tk.Label(win, text="Поставщики", font=("Arial", 14, "bold")).pack(pady=10)

        for s in results:
            text = f"Поставщик: {s[0]} | Рейтинг: {s[1]} | Сотрудничество с: {s[2]}"
            tk.Label(win, text=text, anchor="w", justify="left").pack(fill="x", padx=10, pady=2)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при получении поставщиков:\n{e}")
    

def create_material_block(container, material, cost):
    block = tk.Frame(container, bd=2, relief="groove", padx=10, pady=5)
    block.pack(fill="x", padx=10, pady=5)

    header = tk.Label(block, text=f"{material['type']} | {material['name']}",
                      font=("Arial", 12, "bold"))
    header.pack(anchor="w")

    info_text = (
        f"Минимальное кол-во: {material['min_quantity']}\n"
        f"Кол-во на складе: {material['quantity']}\n"
        f"Цена: {material['unit_price']} {material['unit']}\n"
        f"Стоимость партии: {cost}"
    )
    info = tk.Label(block, text=info_text, justify="left", font=("Arial", 10))
    info.pack(anchor="w")


def load_data(container):
    try:
        conn = sqlite3.connect("materials.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT m.name, t.type_name, m.unit_price, m.quantity,
                   m.min_quantity, m.pack_quantity, m.unit
            FROM materials m
            JOIN material_types t ON m.type_id = t.id
        """)

        rows = cursor.fetchall()

        if not rows:
            messagebox.showinfo("Информация", "Материалы не найдены в базе данных.")
        
        for row in rows:
            try:
                material = {
                    "name": row[0],
                    "type": row[1],
                    "unit_price": row[2],
                    "quantity": row[3],
                    "min_quantity": row[4],
                    "pack_quantity": row[5],
                    "unit": row[6],
                }
                cost = calculate_min_purchase(material)
                create_material_block(container, material, cost)
            except Exception as e:
                messagebox.showwarning("Ошибка отображения", f"Ошибка отображения материала: {e}")

    except sqlite3.Error as e:
        messagebox.showerror("Ошибка базы данных", f"Не удалось подключиться к базе данных:\n{e}")
    finally:
        if 'conn' in locals():
            conn.close()

root = tk.Tk()
root.title("Учёт материалов")
canvas = tk.Canvas(root)
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
btn_suppliers = tk.Button(root, text="Показать поставщиков", command=show_suppliers, bg="lightblue")
btn_suppliers.pack(pady=10)  
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

load_data(scrollable_frame)

root.mainloop()
