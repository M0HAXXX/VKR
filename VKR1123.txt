import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.colors as colors
from matplotlib.ticker import PercentFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure


class IlluminationCalculatorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Дискретизация освещенности")
        self.root.geometry("1800x900")
        self.root.configure(bg='#2c3e50')

        # Переменные для хранения результатов
        self.task1_results = None
        self.task2_results = None
        self.current_display_mode = "graph"

        # Создаем главное меню
        self.create_main_menu()

    def create_main_menu(self):
        """Создание главного меню с красивыми закругленными кнопками"""
        self.clear_window()

        # Основной фрейм с градиентным фоном
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True, fill='both')

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="Дискретизация освещенности",
            font=('JetBrains Mono', 28, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack(pady=(60, 40))

        # Фрейм для кнопок
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(expand=True)

        # Кнопки меню
        task1_btn = self.create_hover_button(
            button_frame,
            "Задача №1",
            self.show_task1_page,
            '#3498db'
        )
        task1_btn.pack(pady=12)

        task2_btn = self.create_hover_button(
            button_frame,
            "Задача №2",
            self.show_task2_page,
            '#3498db'
        )
        task2_btn.pack(pady=12)

        theory_btn = self.create_hover_button(
            button_frame,
            "Теория",
            self.show_theory_page,
            '#3498db'
        )
        theory_btn.pack(pady=12)

        exit_btn = self.create_hover_button(
            button_frame,
            "Выход",
            self.root.quit,
            '#e74c3c'
        )
        exit_btn.pack(pady=12)

        # Кнопка справки в правом нижнем углу
        help_btn = self.create_help_button(main_frame)
        help_btn.place(relx=0.95, rely=0.92, anchor='center')

    def create_hover_button(self, parent, text, command, bg_color='#3498db', width=25, height=3):
        """Создает стилизованную кнопку с эффектом наведения"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('JetBrains Mono', 16, 'bold'),
            width=width,
            height=height,
            relief='flat',
            bd=0,
            bg=bg_color,
            fg='#ffffff',
            activebackground='#2980b9',
            activeforeground='#ffffff',
            cursor='hand2'
        )

        # Эффект наведения
        def on_enter(e):
            btn.configure(bg='#2980b9' if bg_color == '#3498db' else '#c0392b')

        def on_leave(e):
            btn.configure(bg=bg_color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def create_help_button(self, parent):
        """Создает кнопку справки"""
        btn = tk.Button(
            parent,
            text="❓",
            command=self.show_help,
            font=('JetBrains Mono', 20, 'bold'),
            width=3,
            height=1,
            bg='#95a5a6',
            fg='white',
            relief='flat',
            bd=0,
            activebackground='#7f8c8d',
            activeforeground='white',
            cursor='hand2'
        )

        def on_enter(e):
            btn.configure(bg='#7f8c8d')

        def on_leave(e):
            btn.configure(bg='#95a5a6')

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def create_small_button(self, parent, text, command, bg_color='#3498db', width=12, height=1):
        """Создает маленькую стилизованную кнопку"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('JetBrains Mono', 10, 'bold'),
            width=width,
            height=height,
            relief='flat',
            bd=0,
            bg=bg_color,
            fg='#ffffff',
            activebackground='#2980b9',
            activeforeground='#ffffff',
            cursor='hand2'
        )

        # Эффект наведения
        def on_enter(e):
            if bg_color == '#3498db':
                btn.configure(bg='#2980b9')
            elif bg_color == '#e74c3c':
                btn.configure(bg='#c0392b')
            elif bg_color == '#f39c12':
                btn.configure(bg='#d68910')
            elif bg_color == '#27ae60':
                btn.configure(bg='#229954')
            else:
                btn.configure(bg='#2980b9')

        def on_leave(e):
            btn.configure(bg=bg_color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def show_task1_page(self):
        """Показать страницу задачи 1"""
        self.clear_window()
        self.create_task_page(task_num=1)

    def show_task2_page(self):
        """Показать страницу задачи 2"""
        self.clear_window()
        self.create_task_page(task_num=2)

    def create_task_page(self, task_num):
        """Создание страницы задачи"""
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True)

        # Фрейм для кнопки "Вернуться"
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill='x', pady=(10, 0))

        # Кнопка "Вернуться"
        back_btn = self.create_small_button(
            button_frame,
            "← Вернуться",
            self.create_main_menu,
            '#95a5a6'
        )
        back_btn.pack(side='right', padx=20)

        # Фрейм для содержимого (левая и правая панели)
        content_frame = tk.Frame(main_frame, bg='#2c3e50')
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Левая панель (1/3 экрана)
        left_frame = tk.Frame(content_frame, bg='#34495e', relief='flat', bd=0)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.configure(width=400)
        left_frame.pack_propagate(False)

        # Правая панель (2/3 экрана)
        right_frame = tk.Frame(content_frame, bg='#34495e', relief='flat', bd=0)
        right_frame.pack(side='right', fill='both', expand=True)

        # Создание содержимого левой панели
        self.create_left_panel(left_frame, task_num)

        # Создание содержимого правой панели
        self.create_right_panel(right_frame, task_num)

    def create_left_panel(self, parent, task_num):
        """Создание левой панели с параметрами"""
        # Заголовок
        title_label = tk.Label(
            parent,
            text=f"Задача №{task_num}",
            font=('JetBrains Mono', 20, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        )
        title_label.pack(pady=20)

        # Верхняя часть - параметры
        params_frame = tk.LabelFrame(
            parent,
            text="Параметры",
            font=('JetBrains Mono', 14, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            relief='flat',
            bd=2
        )
        params_frame.pack(fill='x', padx=15, pady=10)

        # Словари для хранения полей ввода
        if task_num == 1:
            self.task1_entries = {}
            entries_dict = self.task1_entries
            default_values = {
                'l_ap': 5.0,
                'l_sh': 7.0,
                'a': 70.0,
                'E1': 20,
                'E2': 80,
                'num_pixels': 20
            }
        else:
            self.task2_entries = {}
            entries_dict = self.task2_entries
            default_values = {
                'l_ap': 8.0,
                'l_sh': 10.0,
                'a': 70.0,
                'b': 110.0,
                'E1': 20,
                'E2': 80,
                'num_pixels': 20
            }

        # Создание полей ввода
        row = 0
        for param, default_val in default_values.items():
            label_text = f"{param} ({'мкм' if param not in ['E1', 'E2', 'num_pixels'] else '%' if param in ['E1', 'E2'] else ''}):"

            label = tk.Label(
                params_frame,
                text=label_text,
                bg='#34495e',
                fg='#ecf0f1',
                font=('JetBrains Mono', 11)
            )
            label.grid(row=row, column=0, sticky='w', padx=10, pady=8)

            entry = tk.Entry(
                params_frame,
                font=('JetBrains Mono', 11),
                width=15,
                bg='#ecf0f1',
                fg='#2c3e50',
                relief='flat',
                bd=5
            )
            entry.insert(0, str(default_val))
            entry.grid(row=row, column=1, padx=10, pady=8)

            entries_dict[param] = entry
            row += 1

        # Кнопка вычислить
        calc_btn = self.create_hover_button(
            params_frame,
            "Вычислить",
            lambda: self.calculate_task(task_num),
            '#27ae60',
            15,
            2
        )
        calc_btn.grid(row=row, column=0, columnspan=2, pady=25)

        # Нижняя часть - справка
        help_frame = tk.LabelFrame(
            parent,
            text="Справка",
            font=('JetBrains Mono', 14, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            relief='flat',
            bd=2
        )
        help_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Создание текста справки
        help_text = self.get_help_text(task_num)
        help_label = tk.Label(
            help_frame,
            text=help_text,
            bg='#34495e',
            fg='white',
            font=('JetBrains Mono', 10),
            justify='left',
            wraplength=350,
            anchor='nw'
        )
        help_label.pack(fill='both', expand=True, padx=10, pady=10)

    def create_right_panel(self, parent, task_num):
        """Создание правой панели с результатами"""
        # Заголовок панели
        title_label = tk.Label(
            parent,
            text="Результаты",
            font=('JetBrains Mono', 18, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        )
        title_label.pack(pady=(15, 10))

        # Кнопки переключения режима отображения
        mode_frame = tk.Frame(parent, bg='#34495e')
        mode_frame.pack(fill='x', padx=15, pady=10)

        graph_btn = self.create_small_button(
            mode_frame,
            "График",
            lambda: self.switch_display_mode("graph", task_num),
            '#3498db'
        )
        graph_btn.pack(side='left', padx=5)

        table_btn = self.create_small_button(
            mode_frame,
            "Таблица",
            lambda: self.switch_display_mode("table", task_num),
            '#f39c12'
        )
        table_btn.pack(side='left', padx=5)

        # Область для отображения результатов
        self.results_frame = tk.Frame(parent, bg='#34495e')
        self.results_frame.pack(fill='both', expand=True, padx=15, pady=10)

        # Начальное сообщение
        initial_label = tk.Label(
            self.results_frame,
            text="Введите параметры и нажмите 'Вычислить'\nдля отображения результатов",
            font=('JetBrains Mono', 14),
            bg='#34495e',
            fg='#95a5a6'
        )
        initial_label.pack(expand=True)

    def get_help_text(self, task_num):
        """Получить текст справки для задачи"""
        if task_num == 1:
            return """l_ap - ширина апертуры фотодиода (1-10 мкм)

l_sh - шаг дискретизации (1-10 мкм)

a - положение границы перехода освещенности

E1, E2 - уровни освещенности (0-100%)

num_pixels - размер матрицы

Условие: l_ap ≤ l_sh"""
        else:
            return """l_ap - ширина апертуры фотодиода (1-10 мкм)

l_sh - шаг дискретизации (1-10 мкм)

a - начало области размытия

b - конец области размытия

E1, E2 - уровни освещенности (0-100%)

num_pixels - размер матрицы

Условия: l_ap ≤ l_sh, a < b"""

    def calculate_task(self, task_num):
        """Выполнить расчет для задачи"""
        try:
            if task_num == 1:
                self.calculate_task1()
            else:
                self.calculate_task2()

            self.switch_display_mode(self.current_display_mode, task_num)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете: {str(e)}")

    def calculate_task1(self):
        """Расчет для задачи 1"""
        # Получение параметров
        params = {}
        for key, entry in self.task1_entries.items():
            try:
                if key in ['E1', 'E2', 'num_pixels']:
                    params[key] = int(entry.get())
                else:
                    params[key] = float(entry.get())
            except ValueError:
                raise ValueError(f"Некорректное значение для {key}")

        # Валидация
        self.validate_task1_parameters(**params)

        # Расчет
        l_ap, l_sh, a, E1, E2, num_pixels = params['l_ap'], params['l_sh'], params['a'], params['E1'], params['E2'], \
        params['num_pixels']

        n_a = int((a + l_sh / 2) // l_sh)
        matrix = np.zeros((num_pixels, num_pixels))

        for n in range(num_pixels):
            for m in range(num_pixels):
                if n < n_a - 1:
                    matrix[n, m] = E1
                elif n > n_a - 1:
                    matrix[n, m] = E2
                else:
                    delta = l_sh * n_a - a

                    if delta >= l_ap / 2:
                        matrix[n, m] = E2
                    elif delta <= -l_ap / 2:
                        matrix[n, m] = E1
                    else:
                        matrix[n, m] = ((l_ap / 2 - delta) * E1 + (l_ap / 2 + delta) * E2) / l_ap

        self.task1_results = (matrix, params)

    def calculate_task2(self):
        """Расчет для задачи 2"""
        # Получение параметров
        params = {}
        for key, entry in self.task2_entries.items():
            try:
                if key in ['E1', 'E2', 'num_pixels']:
                    params[key] = int(entry.get())
                else:
                    params[key] = float(entry.get())
            except ValueError:
                raise ValueError(f"Некорректное значение для {key}")

        # Валидация
        self.validate_task2_parameters(**params)

        # Расчет
        l_ap, l_sh, a, b, E1, E2, num_pixels = params['l_ap'], params['l_sh'], params['a'], params['b'], params['E1'], \
        params['E2'], params['num_pixels']

        def E(x):
            if x <= a:
                return E1
            elif x >= b:
                return E2
            else:
                return E1 + (E2 - E1) * (x - a) / (b - a)

        matrix = np.zeros((num_pixels, num_pixels))

        for n in range(num_pixels):
            for m in range(num_pixels):
                x_right = (n + 0.5) * l_sh + l_ap / 2
                matrix[n, m] = E(x_right)

        self.task2_results = (matrix, params)

    def validate_task1_parameters(self, l_ap, l_sh, a, E1, E2, num_pixels):
        """Валидация параметров задачи 1"""
        if not (1 <= l_ap <= 10 and 1 <= l_sh <= 10):
            raise ValueError("l_ap и l_sh должны быть в диапазоне 1-10 мкм")
        if l_ap > l_sh:
            raise ValueError("l_ap должна быть ≤ l_sh")
        if not (l_sh < a < (num_pixels - 1) * l_sh):
            raise ValueError(f"a должно быть в диапазоне {l_sh}..{(num_pixels - 1) * l_sh} мкм")
        if not (0 <= E1 <= 100 and 0 <= E2 <= 100):
            raise ValueError("E1 и E2 должны быть в диапазоне 0-100%")
        if num_pixels < 5 or num_pixels > 50:
            raise ValueError("Размер матрицы должен быть от 5 до 50")

    def validate_task2_parameters(self, l_ap, l_sh, a, b, E1, E2, num_pixels):
        """Валидация параметров задачи 2"""
        if not (1 <= l_ap <= 10 and 1 <= l_sh <= 10):
            raise ValueError("l_ap и l_sh должны быть в диапазоне 1-10 мкм")
        if l_ap > l_sh:
            raise ValueError("l_ap должна быть ≤ l_sh")
        if a >= b:
            raise ValueError("a должно быть меньше b")
        if not (0 < a < num_pixels * l_sh):
            raise ValueError(f"a должно быть в диапазоне 0..{num_pixels * l_sh} мкм")
        if not (0 < b < num_pixels * l_sh):
            raise ValueError(f"b должно быть в диапазоне 0..{num_pixels * l_sh} мкм")
        if not (0 <= E1 <= 100 and 0 <= E2 <= 100):
            raise ValueError("E1 и E2 должны быть в диапазоне 0-100%")
        if num_pixels < 5 or num_pixels > 50:
            raise ValueError("Размер матрицы должен быть от 5 до 50")

    def switch_display_mode(self, mode, task_num):
        """Переключение режима отображения"""
        self.current_display_mode = mode

        # Очистка области результатов
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        results = self.task1_results if task_num == 1 else self.task2_results

        if results is None:
            label = tk.Label(
                self.results_frame,
                text="❌ Нет данных для отображения",
                font=('JetBrains Mono', 14),
                bg='#34495e',
                fg='#e74c3c'
            )
            label.pack(expand=True)
            return

        matrix, params = results

        if mode == "graph":
            self.show_graph(matrix, params, task_num)
        else:
            self.show_table(matrix, params, task_num)

    def show_graph(self, matrix, params, task_num):
        """Отображение графика"""
        fig = matplotlib.figure.Figure(figsize=(8, 6), dpi=100, facecolor='#34495e')
        ax = fig.add_subplot(111, facecolor='#34495e')

        # Построение графика
        norm = colors.Normalize(vmin=0, vmax=100)
        im = ax.imshow(matrix.T, cmap='viridis', norm=norm, origin='lower',
                       extent=[0, matrix.shape[0], 0, matrix.shape[1]])

        # Установка тиков с шагом 1
        ax.set_xticks(np.arange(0, matrix.shape[0], 1))
        ax.set_yticks(np.arange(0, matrix.shape[1], 1))

        ax.set_title(f'Графическое представление',
                     color='#ecf0f1', fontsize=14, fontweight='bold')
        ax.set_xlabel('Номер пикселя по горизонтали (n)', color='#ecf0f1')
        ax.set_ylabel('Номер пикселя по вертикали (m)', color='#ecf0f1')

        # Стилизация осей
        ax.tick_params(colors='#ecf0f1')
        ax.spines['bottom'].set_color('#ecf0f1')
        ax.spines['top'].set_color('#ecf0f1')
        ax.spines['right'].set_color('#ecf0f1')
        ax.spines['left'].set_color('#ecf0f1')

        # Цветовая шкала
        cbar = fig.colorbar(im, ax=ax, format=PercentFormatter())
        cbar.set_label('Освещенность (%)', color='#ecf0f1')
        cbar.ax.tick_params(colors='#ecf0f1')

        fig.tight_layout()

        # Встраивание в tkinter
        canvas = FigureCanvasTkAgg(fig, self.results_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def show_table(self, matrix, params, task_num):
        rotated_matrix = np.rot90(matrix, k=1)

        # Создание фрейма с прокруткой
        canvas_frame = tk.Frame(self.results_frame, bg='#34495e')
        canvas_frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(canvas_frame, bg='#34495e')
        scrollbar_v = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = tk.Frame(canvas, bg='#34495e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)

        # Заголовок таблицы
        title_label = tk.Label(
            scrollable_frame,
            text=f'Табличное представление (%) ',
            font=('JetBrains Mono', 14, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        )
        title_label.grid(row=0, column=0, columnspan=rotated_matrix.shape[1] + 1, pady=15)

        # Заголовки столбцов
        tk.Label(
            scrollable_frame,
            text="",
            bg='#3498db',
            fg='white',
            relief='flat',
            bd=1,
            width=5,
            height=2,
            font=('JetBrains Mono', 9, 'bold')
        ).grid(row=1, column=0)

        for j in range(rotated_matrix.shape[1]):
            tk.Label(
                scrollable_frame,
                text=str(j + 1),
                bg='#3498db',
                fg='white',
                relief='flat',
                bd=1,
                width=8,
                height=2,
                font=('JetBrains Mono', 9, 'bold')
            ).grid(row=1, column=j + 1)

        # Данные таблицы
        for i in range(rotated_matrix.shape[0]):
            # Заголовок строки
            tk.Label(
                scrollable_frame,
                text=str(i + 1),
                bg='#3498db',
                fg='white',
                relief='flat',
                bd=1,
                width=5,
                height=2,
                font=('JetBrains Mono', 9, 'bold')
            ).grid(row=i + 2, column=0)

            # Данные
            for j in range(rotated_matrix.shape[1]):
                value = rotated_matrix[i, j]
                tk.Label(
                    scrollable_frame,
                    text=f"{value:.1f}",
                    bg='#ecf0f1',
                    fg='#2c3e50',
                    relief='flat',
                    bd=1,
                    width=8,
                    height=2,
                    font=('JetBrains Mono', 9)
                ).grid(row=i + 2, column=j + 1)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")

    def show_theory_page(self):
        """Показать страницу теории"""
        self.clear_window()

        # Основной фрейм
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill='both', expand=True)

        # Фрейм для кнопки "Вернуться"
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(fill='x', pady=(10, 0))

        # Кнопка "Вернуться"
        back_btn = self.create_small_button(
            button_frame,
            "← Вернуться",
            self.create_main_menu,
            '#95a5a6'
        )
        back_btn.pack(side='right', padx=20)

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="📚 Теоретические основы",
            font=('JetBrains Mono', 24, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack(pady=(20, 30))

        # Контейнер для содержимого с фоном
        content_container = tk.Frame(main_frame, bg='#34495e', relief='flat', bd=0)
        content_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Создание фрейма с прокруткой для текста
        canvas = tk.Canvas(content_container, bg='#34495e', highlightthickness=0)

        # Стилизованный скроллбар
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar",
                        background='#95a5a6',
                        troughcolor='#34495e',
                        bordercolor='#34495e',
                        arrowcolor='#ecf0f1',
                        darkcolor='#7f8c8d',
                        lightcolor='#bdc3c7')

        scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=canvas.yview,
                                  style="Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg='#34495e')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Теоретический текст с улучшенным форматированием
        theory_sections = self.get_theory_sections()

        for section_title, section_content in theory_sections:
            # Заголовок секции
            section_label = tk.Label(
                scrollable_frame,
                text=section_title,
                font=('JetBrains Mono', 16, 'bold'),
                bg='#34495e',
                fg='#3498db',
                anchor='w'
            )
            section_label.pack(fill='x', padx=25, pady=(20, 10))

            # Содержимое секции
            content_label = tk.Label(
                scrollable_frame,
                text=section_content,
                font=('JetBrains Mono', 11),
                bg='#34495e',
                fg='#ecf0f1',
                justify='left',
                wraplength=1000,
                anchor='nw'
            )
            content_label.pack(fill='x', padx=40, pady=(0, 15))

        # Привязка прокрутки колесиком мыши ко всем элементам
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)

        # Привязываем прокрутку к canvas и всем его дочерним элементам
        bind_mousewheel(canvas)
        bind_mousewheel(scrollable_frame)

        canvas.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=15)

    def get_theory_sections(self):
        """Получить разделы теории в структурированном виде"""
        return [
            ("1. ДИСКРЕТИЗАЦИЯ ОСВЕЩЕННОСТИ",
             """Дискретизация освещенности - это процесс преобразования непрерывного распределения освещенности в дискретные значения, соответствующие пикселям матрицы фотодиодов. Каждый фотодиод имеет определенную апертуру и расположен с определенным шагом дискретизации."""),

            ("2. ОСНОВНЫЕ ПАРАМЕТРЫ",
    """
    • l_ap - ширина апертуры фотодиода (мкм) - определяет размер светочувствительной области
    • l_sh - шаг дискретизации (мкм) - расстояние между центрами соседних пикселей  
    • a - координата границы перехода освещенности (мкм)
    • b - координата конца области размытия (для задачи 2)
    • E1, E2 - начальный и конечный уровни освещенности (%)"""),

            ("3. ЗАДАЧА №1 - РЕЗКИЙ ПЕРЕХОД",
             """В первой задаче рассматривается случай резкого перехода освещенности в точке a. Для каждого пикселя матрицы определяется освещенность в зависимости от того, как граница перехода пересекает апертуру фотодиода.

    Если граница проходит через апертуру пикселя, то его освещенность рассчитывается как взвешенное среднее значений E1 и E2 в зависимости от площадей, освещенных каждым уровнем.

    Алгоритм расчета:
    • Определяется номер пикселя n_a, через который проходит граница
    • Для пикселей n < n_a-1: освещенность = E1
    • Для пикселей n > n_a-1: освещенность = E2  
    • Для пикселя n_a: освещенность рассчитывается по формуле взвешенного среднего"""),

            ("4. ЗАДАЧА №2 - ПЛАВНЫЙ ПЕРЕХОД",
             """Во второй задаче рассматривается случай плавного перехода освещенности между точками a и b. В этой области освещенность изменяется линейно от E1 до E2.

    Функция освещенности:
    • E(x) = E1, если x ≤ a
    • E(x) = E1 + (E2-E1)×(x-a)/(b-a), если a < x < b
    • E(x) = E2, если x ≥ b

    Для каждого пикселя освещенность определяется по правой границе его апертуры."""),

    ]

    def show_help(self):
        """Показать справку"""
        help_text = """

    Программа "Дискретизация освещенности" предназначена для моделирования процесса дискретизации изображений в матричных фотоприемниках.

    ЗАДАЧА №1 - Резкий переход освещенности
    Моделирует случай, когда граница между областями с разной освещенностью проходит четко в одной точке.

    ЗАДАЧА №2 - Плавный переход освещенности  
    Моделирует случай, когда переход освещенности происходит плавно в определенной области.

    ПАРАМЕТРЫ:
    • l_ap - ширина апертуры фотодиода (1-10 мкм)
    • l_sh - шаг дискретизации (1-10 мкм)  
    • a, b - границы области перехода (мкм)
    • E1, E2 - уровни освещенности (0-100%)
    • num_pixels - размер матрицы (5-50 пикселей)

    РЕЗУЛЬТАТЫ:
    • График - цветовое представление матрицы
    • Таблица - числовые значения освещенности

    Для получения подробной информации используйте раздел "Теория"."""

        # Создание стилизованного окна справки
        help_window = tk.Toplevel(self.root)
        help_window.title("Справка")
        help_window.geometry("600x500")
        help_window.configure(bg='#2c3e50')
        help_window.resizable(False, False)

        # Центрирование окна
        help_window.transient(self.root)
        help_window.grab_set()

        # Заголовок
        title_label = tk.Label(
            help_window,
            text="Справка",
            font=('JetBrains Mono', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack(pady=20)

        # Контейнер для текста с прокруткой
        text_container = tk.Frame(help_window, bg='#34495e', relief='flat', bd=0)
        text_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Canvas и скроллбар для прокрутки
        help_canvas = tk.Canvas(text_container, bg='#34495e', highlightthickness=0)

        # Стилизованный скроллбар
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Help.Vertical.TScrollbar",
                        background='#95a5a6',
                        troughcolor='#34495e',
                        bordercolor='#34495e',
                        arrowcolor='#ecf0f1',
                        darkcolor='#7f8c8d',
                        lightcolor='#bdc3c7')

        help_scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=help_canvas.yview,
                                       style="Help.Vertical.TScrollbar")
        help_scrollable_frame = tk.Frame(help_canvas, bg='#34495e')

        help_scrollable_frame.bind(
            "<Configure>",
            lambda e: help_canvas.configure(scrollregion=help_canvas.bbox("all"))
        )

        help_canvas.create_window((0, 0), window=help_scrollable_frame, anchor="nw")
        help_canvas.configure(yscrollcommand=help_scrollbar.set)

        # Текст справки
        help_label = tk.Label(
            help_scrollable_frame,
            text=help_text,
            font=('JetBrains Mono', 11),
            bg='#34495e',
            fg='#ecf0f1',
            justify='left',
            wraplength=520,
            anchor='nw'
        )
        help_label.pack(fill='both', expand=True, padx=20, pady=20)

        # Привязка прокрутки колесиком мыши ко всем элементам
        def _on_help_mousewheel(event):
            help_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_help_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_help_mousewheel)
            for child in widget.winfo_children():
                bind_help_mousewheel(child)

        # Привязываем прокрутку к canvas и всем его дочерним элементам
        bind_help_mousewheel(help_canvas)
        bind_help_mousewheel(help_scrollable_frame)

        help_canvas.pack(side="left", fill="both", expand=True)
        help_scrollbar.pack(side="right", fill="y")

        # Кнопка закрытия
        close_btn = self.create_hover_button(
            help_window,
            "Ок",
            help_window.destroy,
            '#27ae60',
            15,
            2
        )
        close_btn.pack(pady=(0, 20))

    def clear_window(self):
        """Очистить окно"""
        for widget in self.root.winfo_children():
            widget.destroy()


# Основная функция для запуска приложения
def main():
    root = tk.Tk()
    app = IlluminationCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()