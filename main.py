# Импорт библиотек
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.simpledialog import Dialog
import os
import pandas as pd
from PIL import Image, ImageTk


class MaterialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление материалами и продукцией - Мебельная компания")
        self.root.geometry("1200x700")

        # Установка иконки приложения
        try:
            if os.path.exists("Образ плюс.ico"):
                self.root.iconbitmap("Образ плюс.ico")
        except:
            pass

        # Подключение к БД
        self.conn = sqlite3.connect('furniture_company.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

        # Загрузка логотипа
        self.logo_image = None
        try:
            if os.path.exists("Образ плюс.png"):
                img = Image.open("Образ плюс.png")
                img = img.resize((100, 100), Image.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")

        # Применение стилей
        self.apply_styles()

        # GUI
        self.create_widgets()
        self.load_materials()
        self.load_products()

    def apply_styles(self):
        # Основные цвета
        self.primary_bg = "#FFFFFF"  # Белый
        self.secondary_bg = "#BFD6F6"  # Светло-голубой
        self.accent_color = "#405C73"  # Темно-синий

        # Настройка шрифта
        self.font_name = "Calibri"
        self.normal_font = (self.font_name, 10)
        self.bold_font = (self.font_name, 10, "bold")
        self.title_font = (self.font_name, 12, "bold")

        # Общие настройки
        self.style = ttk.Style()
        self.style.configure(".", background=self.primary_bg, font=self.normal_font)
        self.root.configure(background=self.primary_bg)

        # Стиль для фреймов
        self.style.configure("TFrame", background=self.primary_bg)
        self.style.configure("Secondary.TFrame", background=self.secondary_bg)

        # Стиль для кнопок
        self.style.configure("TButton",
                             background=self.accent_color,
                             foreground="black",
                             font=self.bold_font,
                             padding=5)
        self.style.map("TButton",
                       background=[('active', self.accent_color), ('pressed', '#0F2C4B')])

        # Стиль для вкладок
        self.style.configure("TNotebook", background=self.secondary_bg)
        self.style.configure("TNotebook.Tab",
                             background=self.secondary_bg,
                             foreground="black",
                             font=self.bold_font,
                             padding=[10, 5])
        self.style.map("TNotebook.Tab",
                       background=[('selected', self.primary_bg)],
                       foreground=[('selected', 'black')])

        # Стиль для таблиц
        self.style.configure("Treeview",
                             background=self.primary_bg,
                             foreground="black",
                             fieldbackground=self.primary_bg,
                             font=self.normal_font)
        self.style.configure("Treeview.Heading",
                             background=self.accent_color,
                             foreground="black",
                             font=self.bold_font,
                             padding=5)
        self.style.map("Treeview",
                       background=[('selected', self.secondary_bg)])

        # Стиль для меток
        self.style.configure("TLabel",
                             background=self.primary_bg,
                             foreground="black",
                             font=self.normal_font)
        self.style.configure("Title.TLabel",
                             background=self.primary_bg,
                             foreground=self.accent_color,
                             font=self.title_font)

        # Стиль для полей ввода
        self.style.configure("TEntry",
                             fieldbackground="black",
                             foreground="black",
                             font=self.normal_font)

        # Стиль для выпадающих списков
        self.style.configure("TCombobox",
                             fieldbackground="black",
                             foreground="black",
                             font=self.normal_font)

    def create_tables(self):
        # Создаем тестовые таблицы только если они не существуют
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS material_types
                            (
                                material_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL
                            )""")

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS units
                            (
                                unit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                abbreviation TEXT NOT NULL
                            )""")

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS materials
                            (
                                material_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                material_type_id INTEGER NOT NULL,
                                unit_id INTEGER NOT NULL,
                                unit_price REAL NOT NULL CHECK (unit_price >= 0),
                                stock_quantity REAL NOT NULL,
                                min_quantity REAL NOT NULL CHECK (min_quantity >= 0),
                                package_quantity INTEGER NOT NULL,
                                FOREIGN KEY (material_type_id) REFERENCES material_types (material_type_id),
                                FOREIGN KEY (unit_id) REFERENCES units (unit_id)
                            )""")

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS product_types
                            (
                                product_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                coefficient REAL NOT NULL
                            )""")

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS products
                            (
                                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                description TEXT,
                                product_type_id INTEGER NOT NULL,
                                FOREIGN KEY (product_type_id) REFERENCES product_types (product_type_id)
                            )""")

        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS product_materials
                            (
                                product_material_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                product_id INTEGER NOT NULL,
                                material_id INTEGER NOT NULL,
                                required_quantity REAL NOT NULL,
                                loss_percentage REAL NOT NULL,
                                FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
                                FOREIGN KEY (material_id) REFERENCES materials (material_id) ON DELETE CASCADE,
                                UNIQUE (product_id, material_id)
                            )""")

        self.conn.commit()

    def insert_test_data(self):
        # Проверяем, есть ли уже данные
        self.cursor.execute("SELECT COUNT(*) FROM material_types")
        if self.cursor.fetchone()[0] > 0:
            return

        # Заполняем тестовыми данными
        material_types = [('Дерево',), ('Металл',), ('Ткань',), ('Пластик',), ('Стекло',)]
        self.cursor.executemany("INSERT INTO material_types (name) VALUES (?)", material_types)

        units = [
            ('килограмм', 'кг'),
            ('метр', 'м'),
            ('штука', 'шт'),
            ('литр', 'л'),
            ('квадратный метр', 'м²')
        ]
        self.cursor.executemany("INSERT INTO units (name, abbreviation) VALUES (?, ?)", units)

        product_types = [
            ('Стол', 1.2),
            ('Стул', 0.8),
            ('Шкаф', 1.5),
            ('Полка', 0.5),
            ('Диван', 1.8)
        ]
        self.cursor.executemany("INSERT INTO product_types (name, coefficient) VALUES (?, ?)", product_types)

        materials = [
            ('Дубовая доска', 1, 2, 1500.50, 100.5, 20.0, 10),
            ('Стальной уголок', 2, 1, 200.75, 500.25, 100.0, 20),
            ('Хлопковая ткань', 3, 2, 300.00, 200.0, 50.0, 5),
            ('Пластик ABS', 4, 1, 450.25, 300.75, 75.0, 15),
            ('Стекло закаленное', 5, 2, 800.00, 50.0, 10.0, 5)
        ]
        self.cursor.executemany(
            """INSERT INTO materials (name, material_type_id, unit_id,
                                      unit_price, stock_quantity, min_quantity, package_quantity)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            materials
        )

        products = [
            ('Офисный стол', 'Большой стол для офиса', 1),
            ('Офисный стул', 'Удобный стул для офиса', 2),
            ('Книжный шкаф', 'Шкаф для книг', 3),
            ('Настенная полка', 'Полка для книг и декора', 4),
            ('Угловой диван', 'Комфортный диван для офиса', 5)
        ]
        self.cursor.executemany(
            "INSERT INTO products (name, description, product_type_id) VALUES (?, ?, ?)",
            products
        )

        product_materials = [
            (1, 1, 2.5, 5.0), (1, 2, 1.0, 3.0),
            (2, 1, 1.0, 5.0), (2, 3, 0.5, 2.0),
            (3, 1, 5.0, 8.0), (3, 2, 2.0, 5.0),
            (4, 1, 1.5, 5.0), (4, 4, 0.8, 3.0),
            (5, 3, 3.0, 10.0), (5, 4, 2.5, 5.0)
        ]
        self.cursor.executemany(
            """INSERT INTO product_materials (product_id, material_id,
                                              required_quantity, loss_percentage)
               VALUES (?, ?, ?, ?)""",
            product_materials
        )

        self.conn.commit()

    def create_widgets(self):
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок с логотипом
        header_frame = ttk.Frame(main_container, style="Secondary.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))

        if self.logo_image:
            logo_label = ttk.Label(header_frame, image=self.logo_image, background=self.secondary_bg)
            logo_label.pack(side=tk.LEFT, padx=10, pady=5)

        title_label = ttk.Label(header_frame,
                                text="Система управления материалами и продукцией",
                                style="Title.TLabel")
        title_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Создаем Notebook (вкладки)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка материалов
        materials_frame = ttk.Frame(self.notebook)
        self.notebook.add(materials_frame, text="Управление материалами")
        self.create_materials_tab(materials_frame)

        # Вкладка продукции
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="Управление продукцией")
        self.create_products_tab(products_frame)

        # Вкладка связей
        links_frame = ttk.Frame(self.notebook)
        self.notebook.add(links_frame, text="Связи материалов и продукции")
        self.create_links_tab(links_frame)

        # Вкладка импорта
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="Импорт данных")
        self.create_import_tab(import_frame)

    def create_import_tab(self, parent):
        # Фрейм для кнопок импорта
        import_buttons_frame = ttk.Frame(parent, style="Secondary.TFrame")
        import_buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        # Кнопки импорта
        ttk.Button(import_buttons_frame, text="Импорт типов материалов",
                   command=self.import_material_types, style="TButton").pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(import_buttons_frame, text="Импорт материалов",
                   command=self.import_materials, style="TButton").pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(import_buttons_frame, text="Импорт типов продукции",
                   command=self.import_product_types, style="TButton").pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(import_buttons_frame, text="Импорт продукции",
                   command=self.import_products, style="TButton").pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(import_buttons_frame, text="Импорт связей",
                   command=self.import_product_materials, style="TButton").pack(side=tk.LEFT, padx=5, pady=5)

        # Кнопка полного импорта
        ttk.Button(import_buttons_frame, text="Полный импорт",
                   command=self.full_import, style="TButton").pack(side=tk.LEFT, padx=5, pady=5)

        # Область для логов
        self.log_text = tk.Text(parent, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(parent, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def add_log(self, message):
        """Добавляет сообщение в лог-панель"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)  # Автоскролл к последнему сообщению
        self.log_text.config(state=tk.DISABLED)

    def full_import(self):
        """Выполняет полный импорт всех данных в правильном порядке"""
        try:
            self.add_log("=== НАЧАЛО ПОЛНОГО ИМПОРТА ===")

            # Импорт в правильной последовательности
            self.import_material_types()
            self.import_product_types()
            self.import_materials()
            self.import_products()
            self.import_product_materials()

            self.add_log("=== ПОЛНЫЙ ИМПОРТ УСПЕШНО ЗАВЕРШЕН ===")
            messagebox.showinfo("Успех", "Полный импорт данных успешно завершен")
        except Exception as e:
            self.add_log(f"Ошибка при полном импорте: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка при полном импорте: {str(e)}")

    def import_material_types(self):
        """Импорт типов материалов из Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл импорта типов материалов",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            )
            if not file_path:
                return

            self.add_log(f"Импорт типов материалов из: {file_path}")

            # Чтение данных из Excel
            df = pd.read_excel(file_path)
            self.add_log(f"Найдено записей: {len(df)}")

            # Очистка таблицы перед импортом
            self.cursor.execute("DELETE FROM material_types")

            # Импорт данных
            for index, row in df.iterrows():
                material_type_name = row['Тип материала']
                self.cursor.execute(
                    "INSERT INTO material_types (name) VALUES (?)",
                    (material_type_name,)
                )

            self.conn.commit()
            self.add_log("Импорт типов материалов успешно завершен")
            messagebox.showinfo("Успех", "Типы материалов успешно импортированы")
        except Exception as e:
            self.add_log(f"Ошибка импорта типов материалов: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка импорта типов материалов: {str(e)}")

    def import_product_types(self):
        """Импорт типов продукции из Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл импорта типов продукции",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            )
            if not file_path:
                return

            self.add_log(f"Импорт типов продукции из: {file_path}")

            # Чтение данных из Excel
            df = pd.read_excel(file_path)
            self.add_log(f"Найдено записей: {len(df)}")

            # Очистка таблицы перед импортом
            self.cursor.execute("DELETE FROM product_types")

            # Импорт данных
            for index, row in df.iterrows():
                product_type_name = row['Тип продукции']
                coefficient = row['Коэффициент типа продукции']
                self.cursor.execute(
                    "INSERT INTO product_types (name, coefficient) VALUES (?, ?)",
                    (product_type_name, coefficient)
                )

            self.conn.commit()
            self.add_log("Импорт типов продукции успешно завершен")
            messagebox.showinfo("Успех", "Типы продукции успешно импортированы")
        except Exception as e:
            self.add_log(f"Ошибка импорта типов продукции: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка импорта типов продукции: {str(e)}")

    def import_materials(self):
        """Импорт материалов из Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл импорта материалов",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            )
            if not file_path:
                return

            self.add_log(f"Импорт материалов из: {file_path}")

            # Чтение данных из Excel
            df = pd.read_excel(file_path)
            self.add_log(f"Найдено записей: {len(df)}")

            # Очистка таблицы перед импортом
            self.cursor.execute("DELETE FROM materials")

            # Создаем словарь единиц измерения
            units_map = {}
            self.cursor.execute("SELECT unit_id, abbreviation FROM units")
            for row in self.cursor.fetchall():
                units_map[row[1]] = row[0]

            # Создаем словарь типов материалов
            material_types_map = {}
            self.cursor.execute("SELECT material_type_id, name FROM material_types")
            for row in self.cursor.fetchall():
                material_types_map[row[1]] = row[0]

            # Импорт данных
            for index, row in df.iterrows():
                name = row['Наименование материала']
                material_type = row['Тип материала']
                unit_price = row['Цена единицы материала']
                stock_quantity = row['Количество на складе']
                min_quantity = row['Минимальное количество']
                package_quantity = row['Количество в упаковке']
                unit_abbr = row['Единица измерения']

                # Получаем ID типа материала
                material_type_id = material_types_map.get(material_type)
                if material_type_id is None:
                    raise ValueError(f"Тип материала '{material_type}' не найден")

                # Получаем ID единицы измерения
                unit_id = units_map.get(unit_abbr)
                if unit_id is None:
                    # Если единица измерения не найдена, создаем новую
                    self.cursor.execute(
                        "INSERT INTO units (name, abbreviation) VALUES (?, ?)",
                        (unit_abbr, unit_abbr)
                    )
                    unit_id = self.cursor.lastrowid
                    units_map[unit_abbr] = unit_id
                    self.add_log(f"Добавлена новая единица измерения: {unit_abbr}")

                # Вставка материала
                self.cursor.execute(
                    """INSERT INTO materials (name, material_type_id, unit_id, unit_price,
                                              stock_quantity, min_quantity, package_quantity)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, material_type_id, unit_id, unit_price, stock_quantity, min_quantity, package_quantity)
                )

            self.conn.commit()
            self.add_log("Импорт материалов успешно завершен")
            messagebox.showinfo("Успех", "Материалы успешно импортированы")
        except Exception as e:
            self.add_log(f"Ошибка импорта материалов: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка импорта материалов: {str(e)}")

    def import_products(self):
        """Импорт продукции из Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл импорта продукции",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            )
            if not file_path:
                return

            self.add_log(f"Импорт продукции из: {file_path}")

            # Чтение данных из Excel
            df = pd.read_excel(file_path)
            self.add_log(f"Найдено записей: {len(df)}")

            # Очистка таблицы перед импортом
            self.cursor.execute("DELETE FROM products")

            # Создаем словарь типов продукции
            product_types_map = {}
            self.cursor.execute("SELECT product_type_id, name FROM product_types")
            for row in self.cursor.fetchall():
                product_types_map[row[1]] = row[0]

            # Импорт данных
            for index, row in df.iterrows():
                product_type = row['Тип продукции']
                name = row['Наименование продукции']

                # Получаем ID типа продукции
                product_type_id = product_types_map.get(product_type)
                if product_type_id is None:
                    raise ValueError(f"Тип продукции '{product_type}' не найден")

                # Вставка продукта
                self.cursor.execute(
                    "INSERT INTO products (name, description, product_type_id) VALUES (?, '', ?)",
                    (name, product_type_id)
                )

            self.conn.commit()
            self.add_log("Импорт продукции успешно завершен")
            messagebox.showinfo("Успех", "Продукция успешно импортирована")
        except Exception as e:
            self.add_log(f"Ошибка импорта продукции: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка импорта продукции: {str(e)}")

    def import_product_materials(self):
        """Импорт связей между материалами и продукцией из Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл импорта связей",
                filetypes=(("Excel files", "*.xlsx"), ("All files", "*.*"))
            )
            if not file_path:
                return

            self.add_log(f"Импорт связей материалов и продукции из: {file_path}")

            # Чтение данных из Excel
            df = pd.read_excel(file_path)
            self.add_log(f"Найдено записей: {len(df)}")

            # Очистка таблицы перед импортом
            self.cursor.execute("DELETE FROM product_materials")

            # Создаем словарь материалов
            materials_map = {}
            self.cursor.execute("SELECT material_id, name FROM materials")
            for row in self.cursor.fetchall():
                materials_map[row[1]] = row[0]

            # Создаем словарь продукции
            products_map = {}
            self.cursor.execute("SELECT product_id, name FROM products")
            for row in self.cursor.fetchall():
                products_map[row[1]] = row[0]

            # Импорт данных
            for index, row in df.iterrows():
                material_name = row['Наименование материала']
                product_name = row['Продукция']
                required_quantity = row['Необходимое количество материала']

                # Получаем ID материала
                material_id = materials_map.get(material_name)
                if material_id is None:
                    self.add_log(f"Материал '{material_name}' не найден, пропуск")
                    continue

                # Получаем ID продукции
                product_id = products_map.get(product_name)
                if product_id is None:
                    self.add_log(f"Продукция '{product_name}' не найдена, пропуск")
                    continue

                # Вставка связи
                self.cursor.execute(
                    """INSERT INTO product_materials (product_id, material_id,
                                                      required_quantity, loss_percentage)
                       VALUES (?, ?, ?, 0)""",
                    (product_id, material_id, required_quantity)
                )

            self.conn.commit()
            self.add_log("Импорт связей успешно завершен")
            messagebox.showinfo("Успех", "Связи материалов и продукции успешно импортированы")

            # Обновляем данные в интерфейсе
            self.load_materials()
            self.load_products()
            self.load_links()
        except Exception as e:
            self.add_log(f"Ошибка импорта связей: {str(e)}")
            messagebox.showerror("Ошибка", f"Ошибка импорта связей: {str(e)}")

    def create_materials_tab(self, parent):
        # Панель инструментов для материалов
        toolbar = ttk.Frame(parent, style="Secondary.TFrame")
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Добавить материал", command=self.add_material, style="TButton").pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(toolbar, text="Обновить", command=self.load_materials, style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Просмотр продукции", command=self.view_products, style="TButton").pack(side=tk.LEFT,
                                                                                                         padx=5)

        # Таблица материалов
        columns = ("ID", "Название", "Тип", "Ед.изм", "Цена", "На складе", "Мин.кол-во", "Упаковка", "Требуется")
        self.materials_tree = ttk.Treeview(parent, columns=columns, show="headings")

        for col in columns:
            self.materials_tree.heading(col, text=col,
                                        command=lambda c=col: self.sort_column(self.materials_tree, c, False))

        self.materials_tree.column("ID", width=50, anchor=tk.CENTER)
        self.materials_tree.column("Название", width=150)
        self.materials_tree.column("Тип", width=100)
        self.materials_tree.column("Ед.изм", width=70)
        self.materials_tree.column("Цена", width=100, anchor=tk.E)
        self.materials_tree.column("На складе", width=100, anchor=tk.E)
        self.materials_tree.column("Мин.кол-во", width=100, anchor=tk.E)
        self.materials_tree.column("Упаковка", width=80, anchor=tk.E)
        self.materials_tree.column("Требуется", width=100, anchor=tk.E)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.materials_tree.yview)
        self.materials_tree.configure(yscroll=scrollbar.set)

        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Двойной клик для редактирования
        self.materials_tree.bind("<Double-1>", self.edit_material)

    def create_products_tab(self, parent):
        # Панель инструментов для продукции
        toolbar = ttk.Frame(parent, style="Secondary.TFrame")
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Добавить продукцию", command=self.add_product, style="TButton").pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(toolbar, text="Обновить", command=self.load_products, style="TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Управление материалами", command=self.link_materials_to_product,
                   style="TButton").pack(side=tk.LEFT, padx=5)

        # Таблица продукции
        columns = ("ID", "Название", "Тип", "Коэффициент", "Описание")
        self.products_tree = ttk.Treeview(parent, columns=columns, show="headings")

        for col in columns:
            self.products_tree.heading(col, text=col,
                                       command=lambda c=col: self.sort_column(self.products_tree, c, False))

        self.products_tree.column("ID", width=50, anchor=tk.CENTER)
        self.products_tree.column("Название", width=200)
        self.products_tree.column("Тип", width=150)
        self.products_tree.column("Коэффициент", width=100, anchor=tk.E)
        self.products_tree.column("Описание", width=400)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscroll=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Двойной клик для редактирования
        self.products_tree.bind("<Double-1>", self.edit_product)

    def create_links_tab(self, parent):
        # Панель инструментов для связей
        toolbar = ttk.Frame(parent, style="Secondary.TFrame")
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Обновить", command=self.load_links, style="TButton").pack(side=tk.LEFT, padx=5)

        # Таблица связей
        columns = ("Продукция", "Материал", "Требуемое кол-во", "Потери (%)")
        self.links_tree = ttk.Treeview(parent, columns=columns, show="headings")

        for col in columns:
            self.links_tree.heading(col, text=col)

        self.links_tree.column("Продукция", width=250)
        self.links_tree.column("Материал", width=250)
        self.links_tree.column("Требуемое кол-во", width=150, anchor=tk.E)
        self.links_tree.column("Потери (%)", width=100, anchor=tk.E)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.links_tree.yview)
        self.links_tree.configure(yscroll=scrollbar.set)

        self.links_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Загрузка данных о связях
        self.load_links()

    def sort_column(self, tree, column, reverse):
        # Получаем все значения из столбца
        data = [(tree.set(item, column), item) for item in tree.get_children('')]

        # Сортируем данные
        try:
            # Пытаемся преобразовать к числам
            data.sort(key=lambda x: float(x[0]) if x[0].replace('.', '', 1).isdigit() else x[0], reverse=reverse)
        except:
            # Если не получилось, сортируем как строки
            data.sort(reverse=reverse)

        # Переставляем элементы в Treeview
        for index, (_, item) in enumerate(data):
            tree.move(item, '', index)

        # Устанавливаем обратный порядок для следующего клика
        tree.heading(column, command=lambda c=column: self.sort_column(tree, c, not reverse))

    def calculate_required_quantity(self, material_id):
        self.cursor.execute("""
                            SELECT SUM(required_quantity)
                            FROM product_materials
                            WHERE material_id = ?
                            """, (material_id,))
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    def load_materials(self):
        # Очищаем таблицу
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)

        # Загружаем данные
        self.cursor.execute("""
                            SELECT m.material_id,
                                   m.name,
                                   mt.name,
                                   u.abbreviation,
                                   m.unit_price,
                                   m.stock_quantity,
                                   m.min_quantity,
                                   m.package_quantity
                            FROM materials m
                                     JOIN material_types mt ON m.material_type_id = mt.material_type_id
                                     JOIN units u ON m.unit_id = u.unit_id
                            """)

        for row in self.cursor.fetchall():
            material_id = row[0]
            required = self.calculate_required_quantity(material_id)
            self.materials_tree.insert("", tk.END, values=row + (required,))

    def load_products(self):
        # Очищаем таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        # Загружаем данные
        self.cursor.execute("""
                            SELECT p.product_id, p.name, pt.name, pt.coefficient, p.description
                            FROM products p
                                     JOIN product_types pt ON p.product_type_id = pt.product_type_id
                            """)

        for row in self.cursor.fetchall():
            self.products_tree.insert("", tk.END, values=row)

    def load_links(self):
        # Очищаем таблицу
        for item in self.links_tree.get_children():
            self.links_tree.delete(item)

        # Загружаем данные
        self.cursor.execute("""
                            SELECT p.name AS product_name,
                                   m.name AS material_name,
                                   pm.required_quantity,
                                   pm.loss_percentage
                            FROM product_materials pm
                                     JOIN products p ON pm.product_id = p.product_id
                                     JOIN materials m ON pm.material_id = m.material_id
                            ORDER BY p.name, m.name
                            """)

        for row in self.cursor.fetchall():
            self.links_tree.insert("", tk.END, values=row)

    def add_material(self):
        MaterialForm(self.root, self, None)

    def edit_material(self, event):
        item = self.materials_tree.selection()[0]
        material_id = self.materials_tree.item(item, "values")[0]
        MaterialForm(self.root, self, material_id)

    def save_material(self, data, material_id=None):
        try:
            unit_price = float(data['unit_price'])
            stock_quantity = float(data['stock_quantity'])
            min_quantity = float(data['min_quantity'])
            package_quantity = int(data['package_quantity'])

            if unit_price < 0 or min_quantity < 0:
                raise ValueError("Цена и минимальное количество не могут быть отрицательными")

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректные данные: {str(e)}")
            return

        if material_id:  # Редактирование
            self.cursor.execute("""
                                UPDATE materials
                                SET name             = ?,
                                    material_type_id = ?,
                                    unit_id          = ?,
                                    unit_price       = ?,
                                    stock_quantity   = ?,
                                    min_quantity     = ?,
                                    package_quantity = ?
                                WHERE material_id = ?
                                """, (
                                    data['name'],
                                    data['material_type_id'],
                                    data['unit_id'],
                                    unit_price,
                                    stock_quantity,
                                    min_quantity,
                                    package_quantity,
                                    material_id
                                ))
        else:  # Добавление
            self.cursor.execute("""
                                INSERT INTO materials (name, material_type_id, unit_id,
                                                       unit_price, stock_quantity, min_quantity, package_quantity)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    data['name'],
                                    data['material_type_id'],
                                    data['unit_id'],
                                    unit_price,
                                    stock_quantity,
                                    min_quantity,
                                    package_quantity
                                ))

        self.conn.commit()
        self.load_materials()
        messagebox.showinfo("Успех", "Данные материала сохранены")

    def delete_material(self, material_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить материал?"):
            self.cursor.execute("DELETE FROM materials WHERE material_id = ?", (material_id,))
            self.conn.commit()
            self.load_materials()

    def view_products(self):
        try:
            item = self.materials_tree.selection()[0]
            material_id = self.materials_tree.item(item, "values")[0]
            ProductsView(self.root, self, material_id)
        except IndexError:
            messagebox.showwarning("Выбор материала", "Пожалуйста, выберите материал из списка")

    def add_product(self):
        ProductForm(self.root, self, None)

    def edit_product(self, event):
        item = self.products_tree.selection()[0]
        product_id = self.products_tree.item(item, "values")[0]
        ProductForm(self.root, self, product_id)

    def save_product(self, data, product_id=None):
        try:
            if not data['name']:
                raise ValueError("Название продукции обязательно")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return

        if product_id:  # Редактирование
            self.cursor.execute("""
                                UPDATE products
                                SET name            = ?,
                                    product_type_id = ?,
                                    description     = ?
                                WHERE product_id = ?
                                """, (
                                    data['name'],
                                    data['product_type_id'],
                                    data['description'],
                                    product_id
                                ))
        else:  # Добавление
            self.cursor.execute("""
                                INSERT INTO products (name, product_type_id, description)
                                VALUES (?, ?, ?)
                                """, (
                                    data['name'],
                                    data['product_type_id'],
                                    data['description']
                                ))

        self.conn.commit()
        self.load_products()
        messagebox.showinfo("Успех", "Данные продукции сохранены")

    def delete_product(self, product_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить продукцию?"):
            self.cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            self.conn.commit()
            self.load_products()

    def link_materials_to_product(self):
        try:
            item = self.products_tree.selection()[0]
            product_id = self.products_tree.item(item, "values")[0]
            product_name = self.products_tree.item(item, "values")[1]
            ProductMaterialsForm(self.root, self, product_id, product_name)
        except IndexError:
            messagebox.showwarning("Выбор продукции", "Пожалуйста, выберите продукцию из списка")

    def save_product_material(self, product_id, material_id, required_quantity, loss_percentage):
        try:
            required_quantity = float(required_quantity)
            loss_percentage = float(loss_percentage)

            if required_quantity <= 0 or loss_percentage < 0:
                raise ValueError("Количество должно быть положительным, а потери не могут быть отрицательными")

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректные данные: {str(e)}")
            return

        # Проверяем, существует ли уже связь
        self.cursor.execute("""
                            SELECT *
                            FROM product_materials
                            WHERE product_id = ?
                              AND material_id = ?
                            """, (product_id, material_id))

        if self.cursor.fetchone():
            # Обновляем существующую запись
            self.cursor.execute("""
                                UPDATE product_materials
                                SET required_quantity = ?,
                                    loss_percentage   = ?
                                WHERE product_id = ?
                                  AND material_id = ?
                                """, (required_quantity, loss_percentage, product_id, material_id))
        else:
            # Создаем новую запись
            self.cursor.execute("""
                                INSERT INTO product_materials (product_id, material_id, required_quantity,
                                                               loss_percentage)
                                VALUES (?, ?, ?, ?)
                                """, (product_id, material_id, required_quantity, loss_percentage))

        self.conn.commit()
        self.load_materials()  # Обновляем расчет требуемого количества
        self.load_links()  # Обновляем таблицу связей
        return True

    def delete_product_material(self, product_id, material_id):
        self.cursor.execute("""
                            DELETE
                            FROM product_materials
                            WHERE product_id = ?
                              AND material_id = ?
                            """, (product_id, material_id))
        self.conn.commit()
        self.load_materials()  # Обновляем расчет требуемого количества
        self.load_links()  # Обновляем таблицу связей


class MaterialForm(Dialog):
    def __init__(self, parent, app, material_id):
        self.app = app
        self.material_id = material_id
        self.title_text = "Добавить материал" if material_id is None else "Редактировать материал"
        super().__init__(parent, title=self.title_text)

    def body(self, master):
        self.geometry("500x400")
        self.resizable(False, False)

        # Применение стилей
        master.configure(background=self.app.primary_bg)

        ttk.Label(master, text="Название:", style="TLabel").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.name_entry = ttk.Entry(master, width=40, style="TEntry")
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Типы материалов
        ttk.Label(master, text="Тип материала:", style="TLabel").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.material_types = self.get_material_types()
        self.material_type_combo = ttk.Combobox(master, values=list(self.material_types.values()),
                                                state="readonly", width=37, style="TCombobox")
        self.material_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Единицы измерения
        ttk.Label(master, text="Единица измерения:", style="TLabel").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.units = self.get_units()
        self.unit_combo = ttk.Combobox(master, values=list(self.units.values()),
                                       state="readonly", width=37, style="TCombobox")
        self.unit_combo.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(master, text="Цена за единицу:", style="TLabel").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.unit_price_entry = ttk.Entry(master, width=15, style="TEntry")
        self.unit_price_entry.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(master, text="Количество на складе:", style="TLabel").grid(row=4, column=0, padx=10, pady=5,
                                                                             sticky=tk.W)
        self.stock_entry = ttk.Entry(master, width=15, style="TEntry")
        self.stock_entry.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(master, text="Минимальное количество:", style="TLabel").grid(row=5, column=0, padx=10, pady=5,
                                                                               sticky=tk.W)
        self.min_entry = ttk.Entry(master, width=15, style="TEntry")
        self.min_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(master, text="Количество в упаковке:", style="TLabel").grid(row=6, column=0, padx=10, pady=5,
                                                                              sticky=tk.W)
        self.package_entry = ttk.Entry(master, width=15, style="TEntry")
        self.package_entry.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)

        # Кнопка удаления (только для редактирования)
        if self.material_id:
            ttk.Button(master, text="Удалить материал",
                       command=self.delete_material, style="TButton").grid(row=7, column=1, padx=10, pady=10,
                                                                           sticky=tk.E)

        # Загрузка данных при редактировании
        if self.material_id:
            self.load_data()

        return self.name_entry

    def get_material_types(self):
        self.app.cursor.execute("SELECT material_type_id, name FROM material_types")
        return {row[0]: row[1] for row in self.app.cursor.fetchall()}

    def get_units(self):
        self.app.cursor.execute("SELECT unit_id, abbreviation FROM units")
        return {row[0]: row[1] for row in self.app.cursor.fetchall()}

    def load_data(self):
        self.app.cursor.execute("""
                                SELECT m.name,
                                       m.material_type_id,
                                       m.unit_id,
                                       m.unit_price,
                                       m.stock_quantity,
                                       m.min_quantity,
                                       m.package_quantity
                                FROM materials m
                                WHERE m.material_id = ?
                                """, (self.material_id,))

        data = self.app.cursor.fetchone()

        self.name_entry.insert(0, data[0])
        self.unit_price_entry.insert(0, str(data[3]))
        self.stock_entry.insert(0, str(data[4]))
        self.min_entry.insert(0, str(data[5]))
        self.package_entry.insert(0, str(data[6]))

        # Устанавливаем значения в выпадающие списки
        for key, value in self.material_types.items():
            if key == data[1]:
                self.material_type_combo.set(value)
                break

        for key, value in self.units.items():
            if key == data[2]:
                self.unit_combo.set(value)
                break

    def apply(self):
        # Получаем данные из формы
        data = {
            'name': self.name_entry.get(),
            'material_type_id': None,
            'unit_id': None,
            'unit_price': self.unit_price_entry.get(),
            'stock_quantity': self.stock_entry.get(),
            'min_quantity': self.min_entry.get(),
            'package_quantity': self.package_entry.get()
        }

        # Проверяем обязательные поля
        if not data['name']:
            messagebox.showerror("Ошибка", "Название материала обязательно")
            return

        # Получаем ID выбранного типа материала
        material_type_name = self.material_type_combo.get()
        for key, value in self.material_types.items():
            if value == material_type_name:
                data['material_type_id'] = key
                break

        if data['material_type_id'] is None:
            messagebox.showerror("Ошибка", "Выберите тип материала")
            return

        # Получаем ID выбранной единицы измерения
        unit_name = self.unit_combo.get()
        for key, value in self.units.items():
            if value == unit_name:
                data['unit_id'] = key
                break

        if data['unit_id'] is None:
            messagebox.showerror("Ошибка", "Выберите единицу измерения")
            return

        # Сохраняем материал
        self.app.save_material(data, self.material_id)

    def delete_material(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить материал?"):
            self.app.delete_material(self.material_id)
            self.destroy()


class ProductForm(Dialog):
    def __init__(self, parent, app, product_id):
        self.app = app
        self.product_id = product_id
        self.title_text = "Добавить продукцию" if product_id is None else "Редактировать продукцию"
        super().__init__(parent, title=self.title_text)

    def body(self, master):
        self.geometry("500x300")
        self.resizable(False, False)

        # Применение стилей
        master.configure(background=self.app.primary_bg)

        ttk.Label(master, text="Название продукции:", style="TLabel").grid(row=0, column=0, padx=10, pady=5,
                                                                           sticky=tk.W)
        self.name_entry = ttk.Entry(master, width=40, style="TEntry")
        self.name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Типы продукции
        ttk.Label(master, text="Тип продукции:", style="TLabel").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.product_types = self.get_product_types()
        self.product_type_combo = ttk.Combobox(master, values=list(self.product_types.values()),
                                               state="readonly", width=37, style="TCombobox")
        self.product_type_combo.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(master, text="Описание:", style="TLabel").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        self.description_entry = tk.Text(master, width=37, height=5, font=self.app.normal_font)
        self.description_entry.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Кнопка удаления (только для редактирования)
        if self.product_id:
            ttk.Button(master, text="Удалить продукцию",
                       command=self.delete_product, style="TButton").grid(row=3, column=1, padx=10, pady=10,
                                                                          sticky=tk.E)

        # Загрузка данных при редактировании
        if self.product_id:
            self.load_data()

        return self.name_entry

    def get_product_types(self):
        self.app.cursor.execute("SELECT product_type_id, name FROM product_types")
        return {row[0]: row[1] for row in self.app.cursor.fetchall()}

    def load_data(self):
        self.app.cursor.execute("""
                                SELECT p.name, p.product_type_id, p.description
                                FROM products p
                                WHERE p.product_id = ?
                                """, (self.product_id,))

        data = self.app.cursor.fetchone()

        self.name_entry.insert(0, data[0])
        self.description_entry.insert("1.0", data[2])

        # Устанавливаем значение в выпадающий список
        for key, value in self.product_types.items():
            if key == data[1]:
                self.product_type_combo.set(value)
                break

    def apply(self):
        # Получаем данные из формы
        data = {
            'name': self.name_entry.get(),
            'product_type_id': None,
            'description': self.description_entry.get("1.0", tk.END).strip()
        }

        # Проверяем обязательные поля
        if not data['name']:
            messagebox.showerror("Ошибка", "Название продукции обязательно")
            return

        # Получаем ID выбранного типа продукции
        product_type_name = self.product_type_combo.get()
        for key, value in self.product_types.items():
            if value == product_type_name:
                data['product_type_id'] = key
                break

        if data['product_type_id'] is None:
            messagebox.showerror("Ошибка", "Выберите тип продукции")
            return

        # Сохраняем продукцию
        self.app.save_product(data, self.product_id)

    def delete_product(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить продукцию?"):
            self.app.delete_product(self.product_id)
            self.destroy()


class ProductMaterialsForm(tk.Toplevel):
    def __init__(self, parent, app, product_id, product_name):
        super().__init__(parent)
        self.app = app
        self.product_id = product_id
        self.product_name = product_name
        self.title(f"Материалы для продукции: {product_name}")
        self.geometry("800x500")
        self.resizable(False, False)

        # Применение стилей
        self.configure(background=self.app.primary_bg)

        self.create_widgets()
        self.load_materials()

    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Панель инструментов
        toolbar = ttk.Frame(main_frame, style="Secondary.TFrame")
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="Добавить материал", command=self.add_material, style="TButton").pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(toolbar, text="Обновить", command=self.load_materials, style="TButton").pack(side=tk.LEFT, padx=5)

        # Таблица материалов продукта
        columns = ("Материал", "Требуемое кол-во", "Потери (%)", "Действия")
        self.materials_tree = ttk.Treeview(main_frame, columns=columns, show="headings")

        for col in columns:
            self.materials_tree.heading(col, text=col)

        self.materials_tree.column("Материал", width=300)
        self.materials_tree.column("Требуемое кол-во", width=150, anchor=tk.E)
        self.materials_tree.column("Потери (%)", width=100, anchor=tk.E)
        self.materials_tree.column("Действия", width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.materials_tree.yview)
        self.materials_tree.configure(yscroll=scrollbar.set)

        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_materials(self):
        # Очищаем таблицу
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)

        # Загружаем материалы для продукта
        self.app.cursor.execute("""
                                SELECT pm.material_id,
                                       m.name,
                                       pm.required_quantity,
                                       pm.loss_percentage
                                FROM product_materials pm
                                         JOIN materials m ON pm.material_id = m.material_id
                                WHERE pm.product_id = ?
                                """, (self.product_id,))

        for row in self.app.cursor.fetchall():
            material_id, material_name, req_qty, loss = row
            self.materials_tree.insert("", tk.END, values=(
                material_name,
                req_qty,
                loss,
                "✏️ Редактировать ❌ Удалить"
            ), tags=(material_id,))

        # Привязываем обработчик двойного клика
        self.materials_tree.bind("<Double-1>", self.on_material_double_click)

    def on_material_double_click(self, event):
        region = self.materials_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.materials_tree.identify_column(event.x)
            if column == "#4":  # Колонка "Действия"
                item = self.materials_tree.identify_row(event.y)
                material_id = self.materials_tree.item(item, "tags")[0]
                material_name = self.materials_tree.item(item, "values")[0]

                # Определяем позицию клика в колонке
                x, y = event.x, event.y
                bbox = self.materials_tree.bbox(item, column)

                # Если клик по иконке редактирования
                if bbox and x < bbox[0] + bbox[2] / 2:
                    self.edit_material(material_id, material_name)
                # Если клик по иконке удаления
                elif bbox:
                    self.delete_material(material_id, material_name)

    def add_material(self):
        # Получаем список всех материалов
        self.app.cursor.execute("SELECT material_id, name FROM materials")
        materials = {row[0]: row[1] for row in self.app.cursor.fetchall()}

        # Получаем материалы, уже связанные с продуктом
        self.app.cursor.execute("""
                                SELECT material_id
                                FROM product_materials
                                WHERE product_id = ?
                                """, (self.product_id,))
        linked_ids = [row[0] for row in self.app.cursor.fetchall()]

        # Фильтруем материалы, оставляя только не связанные
        available_materials = {k: v for k, v in materials.items() if k not in linked_ids}

        if not available_materials:
            messagebox.showinfo("Нет материалов", "Все материалы уже добавлены в эту продукцию")
            return

        # Диалог выбора материала
        material_name = simpledialog.askstring(
            "Добавить материал",
            "Выберите материал:",
            initialvalue=list(available_materials.values())[0]
        )

        if not material_name:
            return

        # Находим ID материала по имени
        material_id = None
        for mid, name in available_materials.items():
            if name == material_name:
                material_id = mid
                break

        if not material_id:
            return

        # Диалог ввода количества и потерь
        self.edit_material(material_id, material_name, is_new=True)

    def edit_material(self, material_id, material_name, is_new=False):
        # Получаем текущие значения (если редактирование)
        req_qty = 0.0
        loss = 0.0

        if not is_new:
            self.app.cursor.execute("""
                                    SELECT required_quantity, loss_percentage
                                    FROM product_materials
                                    WHERE product_id = ?
                                      AND material_id = ?
                                    """, (self.product_id, material_id))
            result = self.app.cursor.fetchone()
            if result:
                req_qty, loss = result

        # Диалог редактирования
        edit_dialog = tk.Toplevel(self)
        edit_dialog.title(f"Редактирование: {material_name}")
        edit_dialog.geometry("300x200")
        edit_dialog.resizable(False, False)
        edit_dialog.transient(self)
        edit_dialog.grab_set()

        ttk.Label(edit_dialog, text="Требуемое количество:", style="TLabel").grid(row=0, column=0, padx=10, pady=5,
                                                                                  sticky=tk.W)
        req_entry = ttk.Entry(edit_dialog, style="TEntry")
        req_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        req_entry.insert(0, str(req_qty))

        ttk.Label(edit_dialog, text="Потери (%):", style="TLabel").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        loss_entry = ttk.Entry(edit_dialog, style="TEntry")
        loss_entry.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        loss_entry.insert(0, str(loss))

        def save():
            if self.app.save_product_material(
                    self.product_id,
                    material_id,
                    req_entry.get(),
                    loss_entry.get()
            ):
                edit_dialog.destroy()
                self.load_materials()

        ttk.Button(edit_dialog, text="Сохранить", command=save, style="TButton").grid(row=2, column=0, columnspan=2,
                                                                                      pady=10)

    def delete_material(self, material_id, material_name):
        if messagebox.askyesno(
                "Подтверждение",
                f"Вы уверены, что хотите удалить материал '{material_name}' из продукции?"
        ):
            self.app.delete_product_material(self.product_id, material_id)
            self.load_materials()


class ProductsView(tk.Toplevel):
    def __init__(self, parent, app, material_id):
        super().__init__(parent)
        self.app = app
        self.material_id = material_id
        self.title("Продукция, использующая материал")
        self.geometry("800x400")

        # Применение стилей
        self.configure(background=self.app.primary_bg)

        # Получаем название материала
        self.app.cursor.execute("SELECT name FROM materials WHERE material_id = ?", (material_id,))
        material_name = self.app.cursor.fetchone()[0]

        title_frame = ttk.Frame(self, style="Secondary.TFrame")
        title_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(title_frame,
                  text=f"Продукция, использующая материал: {material_name}",
                  style="Title.TLabel").pack(pady=5)

        # Таблица продукции
        self.tree = ttk.Treeview(self, columns=("Продукт", "Требуемое количество"), show="headings")
        self.tree.heading("Продукт", text="Продукт")
        self.tree.heading("Требуемое количество", text="Требуемое количество")

        self.tree.column("Продукт", width=400)
        self.tree.column("Требуемое количество", width=200, anchor=tk.E)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Загрузка данных
        self.load_products()

    def load_products(self):
        self.app.cursor.execute("""
                                SELECT p.name, pm.required_quantity, u.abbreviation
                                FROM products p
                                         JOIN product_materials pm ON p.product_id = pm.product_id
                                         JOIN materials m ON pm.material_id = m.material_id
                                         JOIN units u ON m.unit_id = u.unit_id
                                WHERE pm.material_id = ?
                                """, (self.material_id,))

        for row in self.app.cursor.fetchall():
            product_name = row[0]
            quantity = f"{row[1]} {row[2]}"
            self.tree.insert("", tk.END, values=(product_name, quantity))


def main():
    root = tk.Tk()
    app = MaterialApp(root)
    root.mainloop()
    app.conn.close()

# Точка входа (запуск)
if __name__ == "__main__":
    main()