-- Таблица типов материалов
CREATE TABLE material_types (
    type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL UNIQUE
);

-- Таблица материалов
CREATE TABLE materials (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type_id INTEGER NOT NULL,
    unit_price REAL CHECK(unit_price >= 0),
    quantity REAL,
    min_quantity REAL CHECK(min_quantity >= 0),
    pack_quantity INTEGER,
    unit TEXT,
    FOREIGN KEY (type_id) REFERENCES material_types(type_id)
);
