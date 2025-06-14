-- Создание базы данных
CREATE DATABASE IF NOT EXISTS furniture_company_db;
USE furniture_company_db;

-- Таблица типов материалов
CREATE TABLE material_types (
    material_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Таблица единиц измерения
CREATE TABLE units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL
);

-- Таблица материалов
CREATE TABLE materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    material_type_id INT NOT NULL,
    unit_id INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity DECIMAL(10,2) NOT NULL,
    min_quantity DECIMAL(10,2) NOT NULL CHECK (min_quantity >= 0),
    package_quantity INT NOT NULL,
    FOREIGN KEY (material_type_id) REFERENCES material_types(material_type_id),
    FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);

-- Таблица типов продукции
CREATE TABLE product_types (
    product_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    coefficient DECIMAL(5,2) NOT NULL
);

-- Таблица продукции
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    product_type_id INT NOT NULL,
    FOREIGN KEY (product_type_id) REFERENCES product_types(product_type_id)
);

-- Таблица использования материалов в продукции
CREATE TABLE product_materials (
    product_material_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    material_id INT NOT NULL,
    required_quantity DECIMAL(10,2) NOT NULL,
    loss_percentage DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE,
    UNIQUE KEY (product_id, material_id)
);

-- Заполнение тестовыми данными
INSERT INTO material_types (name) VALUES 
('Дерево'), ('Металл'), ('Ткань'), ('Пластик'), ('Стекло');

INSERT INTO units (name, abbreviation) VALUES 
('килограмм', 'кг'), ('метр', 'м'), ('штука', 'шт'), ('литр', 'л'), ('квадратный метр', 'м²');

INSERT INTO product_types (name, coefficient) VALUES 
('Стол', 1.2), ('Стул', 0.8), ('Шкаф', 1.5), ('Полка', 0.5), ('Диван', 1.8);

-- Добавление материалов
INSERT INTO materials (name, material_type_id, unit_id, unit_price, stock_quantity, min_quantity, package_quantity) VALUES 
('Дубовая доска', 1, 2, 1500.50, 100.5, 20.0, 10),
('Стальной уголок', 2, 1, 200.75, 500.25, 100.0, 20),
('Хлопковая ткань', 3, 2, 300.00, 200.0, 50.0, 5),
('Пластик ABS', 4, 1, 450.25, 300.75, 75.0, 15),
('Стекло закаленное', 5, 2, 800.00, 50.0, 10.0, 5);

-- Добавление продукции
INSERT INTO products (name, description, product_type_id) VALUES 
('Офисный стол', 'Большой стол для офиса', 1),
('Офисный стул', 'Удобный стул для офиса', 2),
('Книжный шкаф', 'Шкаф для книг', 3),
('Настенная полка', 'Полка для книг и декора', 4),
('Угловой диван', 'Комфортный диван для офиса', 5);

-- Связи материалов и продукции
INSERT INTO product_materials (product_id, material_id, required_quantity, loss_percentage) VALUES 
(1, 1, 2.5, 5.0), (1, 2, 1.0, 3.0),
(2, 1, 1.0, 5.0), (2, 3, 0.5, 2.0),
(3, 1, 5.0, 8.0), (3, 2, 2.0, 5.0),
(4, 1, 1.5, 5.0), (4, 4, 0.8, 3.0),
(5, 3, 3.0, 10.0), (5, 4, 2.5, 5.0);