# Система учета материалов мебельного производства

## О проекте

Профессиональное решение для автоматизации учета материалов и продукции на мебельном производстве. Система предоставляет полный цикл управления ресурсами предприятия.

## Основные функции

### Управление материалами
- Добавление новых материалов с указанием характеристик
- Редактирование существующих позиций
- Удаление материалов из системы
- Контроль остатков и минимальных запасов

### Управление продукцией
- Ведение каталога выпускаемой продукции
- Настройка состава продукции
- Управление ассортиментом

### Аналитика и отчеты
- Расчет потребности в материалах
- Анализ использования ресурсов
- Формирование отчетов

## Установка и настройка

### Требования
- Python 3.7+
- SQLite 3
- Пакеты: pandas, openpyxl, pillow

### Инструкция по установке
1. Клонировать репозиторий:
```bash
   git clone https://github.com/slozhkai/DEM

   cd furniture-materials-system
```

2. Установить зависимости:
```bash
   pip install -r requirements.txt
```

3. Запустить приложение:
```bash
   python main.py
```

## Структура базы данных

### Система использует реляционную базу данных SQLite со следующей структурой:
```
material_types (material_type_id, name)
materials (material_id, name, material_type_id, unit_id, unit_price, stock_quantity, min_quantity, package_quantity)
units (unit_id, name, abbreviation)
product_types (product_type_id, name, coefficient)
products (product_id, name, description, product_type_id)
product_materials (product_material_id, product_id, material_id, required_quantity, loss_percentage)
```

# НА ВСЯКИЙ:

1. python -m venv venv
2. venv/Scripts/Activate
3. pip3 install
