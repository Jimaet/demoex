import sqlite3
import matplotlib.pyplot as plt

def extract_schema(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    schema = {}

    for (table,) in tables:
        cursor.execute(f"PRAGMA table_info('{table}');")
        columns = cursor.fetchall()
        schema[table] = [col[1] for col in columns]  # Только имена полей

    conn.close()
    return schema

def draw_diagram(schema, output_file='diagram.png'):
    num_tables = len(schema)
    max_fields = max((len(fields) for fields in schema.values()), default=1)

    height = num_tables * 2.5
    width = 8  # Ширина фиксированная, можно увеличить

    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis('off')

    spacing_y = 2.2
    y = 0

    for table, columns in schema.items():
        text = f"{table}\n" + "\n".join(f"  • {col}" for col in columns)
        ax.text(0, -y, text, fontsize=12, va='top', ha='left',
                bbox=dict(facecolor='lightblue', edgecolor='black', boxstyle='round,pad=0.5'))
        y += spacing_y

    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✅ Диаграмма сохранена как '{output_file}'")

if __name__ == "__main__":
    db_file = "materials.db"  # ← Укажи свой .db файл
    schema = extract_schema(db_file)
    draw_diagram(schema)