import tkinter as tk
from tkinter import font as tkfont
import datetime
import time
import math

# ---------------------------------------------------------
# Базовый класс "карточки" (элемента, который можно таскать)
# ---------------------------------------------------------

class BaseCard(tk.Frame):
    def __init__(self, parent, app, key, title):
        super().__init__(parent, bg="#222222", bd=1, relief="raised")
        self.app = app
        self.key = key

        # Шапка для перетаскивания
        header = tk.Frame(self, bg="#444444")
        header.pack(fill="x")
        title_lbl = tk.Label(
            header, text=title, bg="#444444",
            fg="#ffffff", anchor="w"
        )
        title_lbl.pack(side="left", padx=4, pady=2)

        # Событие "взяли карточку" — за шапку
        for w in (header, title_lbl):
            w.bind("<Button-1>", self._on_header_press)

        # Тело карточки (сюда кладём содержимое)
        self.body = tk.Frame(self, bg="#222222")
        self.body.pack(fill="both", expand=True)

    def _on_header_press(self, event):
        # Сообщаем приложению, что начали перетаскивать эту карточку
        self.app.start_drag(self.key)

    def tick(self, now_dt, now_ts):
        """Переопределяется в наследниках."""
        pass


# ---------------------------------------------------------
# Аналоговые часы
# ---------------------------------------------------------

class AnalogClockCard(BaseCard):
    def __init__(self, parent, app):
        super().__init__(parent, app, "A", "Аналоговые часы (A)")

        self.canvas = tk.Canvas(self.body, bg="#222222", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Configure>", self.on_resize)

        self.cx = self.cy = 0
        self.radius = 0
        self.hour_hand = None
        self.min_hand = None
        self.sec_hand = None

    def on_resize(self, event):
        self.redraw()

    def redraw(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        size = min(w, h)
        if size < 50:
            return

        self.canvas.delete("all")

        self.cx = w / 2
        self.cy = h / 2
        self.radius = size / 2 - 10

        edge_color = (220, 220, 220)
        center_color = (255, 255, 255)
        r_int = int(self.radius)

        # Градиентный фон
        for i in range(r_int, 0, -1):
            t = i / self.radius
            r = int(edge_color[0] * t + center_color[0] * (1 - t))
            g = int(edge_color[1] * t + center_color[1] * (1 - t))
            b = int(edge_color[2] * t + center_color[2] * (1 - t))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_oval(
                self.cx - i, self.cy - i,
                self.cx + i, self.cy + i,
                outline=color, fill=color
            )

        # Внешняя граница
        self.canvas.create_oval(
            self.cx - self.radius, self.cy - self.radius,
            self.cx + self.radius, self.cy + self.radius,
            width=4, outline="#000000"
        )

        # Риски
        for i in range(60):
            angle = math.radians(i * 6)
            if i % 5 == 0:
                inner = self.radius * 0.88
                width_line = 4
            else:
                inner = self.radius * 0.93
                width_line = 1

            x1 = self.cx + inner * math.sin(angle)
            y1 = self.cy - inner * math.cos(angle)
            x2 = self.cx + self.radius * math.sin(angle)
            y2 = self.cy - self.radius * math.cos(angle)

            self.canvas.create_line(
                x1, y1, x2, y2,
                fill="#000000", width=width_line
            )

        # Цифры
        num_radius = self.radius * 0.75
        font_size = max(int(size / 18), 8)
        for h_ in range(1, 13):
            angle = math.radians(h_ * 30)
            x = self.cx + num_radius * math.sin(angle)
            y = self.cy - num_radius * math.cos(angle)
            self.canvas.create_text(
                x, y,
                text=str(h_),
                font=("Arial", font_size, "bold")
            )

        # Толщина стрелок масштабируем
        size_factor = size / 500
        hour_w = max(int(8 * size_factor), 3)
        min_w = max(int(4 * size_factor), 2)
        sec_w = max(int(2 * size_factor), 1)

        # Стрелки
        self.hour_hand = self.canvas.create_line(
            self.cx, self.cy, self.cx, self.cy - self.radius * 0.5,
            width=hour_w, fill="#000000", capstyle=tk.ROUND
        )
        self.min_hand = self.canvas.create_line(
            self.cx, self.cy, self.cx, self.cy - self.radius * 0.75,
            width=min_w, fill="#000000", capstyle=tk.ROUND
        )
        self.sec_hand = self.canvas.create_line(
            self.cx, self.cy, self.cx, self.cy - self.radius * 0.85,
            width=sec_w, fill="#ff0000", capstyle=tk.ROUND
        )

        # Центральная точка
        dot_r = max(int(size / 80), 4)
        self.canvas.create_oval(
            self.cx - dot_r, self.cy - dot_r,
            self.cx + dot_r, self.cy + dot_r,
            fill="#ff0000", outline="#000000", width=2
        )

    def tick(self, now_dt, now_ts):
        if not self.radius or not self.hour_hand:
            return

        second = now_dt.second
        minute = now_dt.minute + second / 60.0
        hour = (now_dt.hour % 12) + minute / 60.0

        angle_sec = math.radians(second * 6)
        angle_min = math.radians(minute * 6)
        angle_hour = math.radians(hour * 30)

        def get_xy(angle, length):
            x = self.cx + length * math.sin(angle)
            y = self.cy - length * math.cos(angle)
            return x, y

        xh, yh = get_xy(angle_hour, self.radius * 0.5)
        xm, ym = get_xy(angle_min, self.radius * 0.75)
        xs, ys = get_xy(angle_sec, self.radius * 0.85)

        self.canvas.coords(self.hour_hand, self.cx, self.cy, xh, yh)
        self.canvas.coords(self.min_hand, self.cx, self.cy, xm, ym)
        self.canvas.coords(self.sec_hand, self.cx, self.cy, xs, ys)


# ---------------------------------------------------------
# Цифровые часы
# ---------------------------------------------------------

class DigitalClockCard(BaseCard):
    def __init__(self, parent, app):
        super().__init__(parent, app, "D", "Цифровые часы (D)")

        self.font = tkfont.Font(family="Consolas", size=32, weight="bold")
        self.label = tk.Label(
            self.body, text="00:00:00",
            font=self.font, bg="#222222", fg="#ffffff"
        )
        self.label.pack(expand=True)

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        size = min(event.width // 7, event.height // 2)
        self.font.configure(size=max(size, 10))

    def tick(self, now_dt, now_ts):
        self.label.config(text=now_dt.strftime("%H:%M:%S"))


# ---------------------------------------------------------
# Секундомер
# ---------------------------------------------------------

class StopwatchCard(BaseCard):
    def __init__(self, parent, app):
        super().__init__(parent, app, "S", "Секундомер (S)")

        self.display_font = tkfont.Font(family="Consolas", size=28, weight="bold")
        self.button_font = tkfont.Font(family="Arial", size=12)

        self.label = tk.Label(
            self.body, text="00:00:00",
            font=self.display_font, bg="#222222", fg="#ffffff"
        )
        self.label.pack(pady=(10, 5), expand=True)

        btn_frame = tk.Frame(self.body, bg="#222222")
        btn_frame.pack(pady=(0, 10))

        self.start_btn = tk.Button(
            btn_frame, text="Старт",
            font=self.button_font, command=self.toggle_start
        )
        self.start_btn.pack(side="left", padx=5)

        self.reset_btn = tk.Button(
            btn_frame, text="Сброс",
            font=self.button_font, command=self.reset
        )
        self.reset_btn.pack(side="left", padx=5)

        self.running = False
        self.elapsed = 0.0  # секунд
        self.last_ts = None

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        size = min(event.width // 7, event.height // 3)
        self.display_font.configure(size=max(size, 10))
        self.button_font.configure(size=max(int(size * 0.5), 8))

    def _update_label(self):
        total = int(self.elapsed)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        self.label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

    def toggle_start(self):
        if not self.running:
            self.running = True
            self.last_ts = time.time()
            self.start_btn.config(text="Пауза")
        else:
            self.running = False
            self.last_ts = None
            self.start_btn.config(text="Старт")

    def reset(self):
        self.elapsed = 0.0
        if self.running:
            self.last_ts = time.time()
        self._update_label()

    def tick(self, now_dt, now_ts):
        if self.running:
            if self.last_ts is None:
                self.last_ts = now_ts
            dt = now_ts - self.last_ts
            self.last_ts = now_ts
            self.elapsed += dt
        self._update_label()


# ---------------------------------------------------------
# Таймер обратного отсчёта
# ---------------------------------------------------------

class TimerCard(BaseCard):
    def __init__(self, parent, app):
        super().__init__(parent, app, "C", "Таймер обратного отсчёта (C)")

        self.display_font = tkfont.Font(family="Consolas", size=28, weight="bold")
        self.small_font = tkfont.Font(family="Arial", size=11)

        self.label = tk.Label(
            self.body, text="00:00:00",
            font=self.display_font, bg="#222222", fg="#ffffff"
        )
        self.label.pack(pady=(10, 5), expand=True)

        entry_frame = tk.Frame(self.body, bg="#222222")
        entry_frame.pack(pady=(0, 5))

        self.entry_label = tk.Label(
            entry_frame, text="Установить (ч:м:с):",
            font=self.small_font, bg="#222222", fg="#dddddd"
        )
        self.entry_label.pack(side="left", padx=4)

        self.entry = tk.Entry(
            entry_frame, width=9,
            font=self.small_font, justify="center"
        )
        self.entry.insert(0, "00:01:00")
        self.entry.pack(side="left", padx=4)

        self.set_btn = tk.Button(
            entry_frame, text="Set",
            font=self.small_font, command=self.apply_entry
        )
        self.set_btn.pack(side="left", padx=4)

        btn_frame = tk.Frame(self.body, bg="#222222")
        btn_frame.pack(pady=(0, 10))

        self.start_btn = tk.Button(
            btn_frame, text="Старт",
            font=self.small_font, command=self.toggle_start
        )
        self.start_btn.pack(side="left", padx=5)

        self.reset_btn = tk.Button(
            btn_frame, text="Сброс",
            font=self.small_font, command=self.reset
        )
        self.reset_btn.pack(side="left", padx=5)

        self.remaining = 0.0  # секунд
        self.running = False
        self.last_ts = None

        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        size = min(event.width // 7, event.height // 3)
        self.display_font.configure(size=max(size, 10))
        small = max(int(size * 0.5), 8)
        self.small_font.configure(size=small)

    def _update_label(self):
        total = max(int(self.remaining), 0)
        h = total // 3600
        m = (total % 3600) // 60
        s = total % 60
        self.label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.label.config(fg="#ff5555" if total == 0 else "#ffffff")

    def apply_entry(self):
        text = self.entry.get().strip()
        if not text:
            return
        try:
            parts = text.split(":")
            if len(parts) == 3:
                h, m, s = parts
            elif len(parts) == 2:
                h = "0"
                m, s = parts
            elif len(parts) == 1:
                h, m, s = "0", "0", parts[0]
            else:
                raise ValueError
            h = max(int(h), 0)
            m = max(int(m), 0)
            s = max(int(s), 0)
        except ValueError:
            # Если формат неверный — просто игнорируем
            return

        total = h * 3600 + m * 60 + s
        self.remaining = float(total)
        self.running = False
        self.last_ts = None
        self.start_btn.config(text="Старт")
        self._update_label()

    def toggle_start(self):
        if not self.running:
            if self.remaining <= 0:
                self.apply_entry()
                if self.remaining <= 0:
                    return
            self.running = True
            self.last_ts = time.time()
            self.start_btn.config(text="Пауза")
        else:
            self.running = False
            self.last_ts = None
            self.start_btn.config(text="Старт")

    def reset(self):
        self.running = False
        self.last_ts = None
        self.remaining = 0.0
        self.start_btn.config(text="Старт")
        self._update_label()

    def tick(self, now_dt, now_ts):
        if self.running and self.remaining > 0:
            if self.last_ts is None:
                self.last_ts = now_ts
            dt = now_ts - self.last_ts
            self.last_ts = now_ts
            self.remaining -= dt
            if self.remaining <= 0:
                self.remaining = 0
                self.running = False
                self.start_btn.config(text="Старт")
        self._update_label()


# ---------------------------------------------------------
# Главное приложение
# ---------------------------------------------------------

class ClockApp:
    MIN_SIZE = 600  # минимальный размер окна (квадрат)

    def __init__(self, root):
        self.root = root
        self.root.title("Clock Suite")
        self.root.configure(bg="#222222")
        self.root.geometry(f"{self.MIN_SIZE}x{self.MIN_SIZE}")
        self.root.minsize(self.MIN_SIZE, self.MIN_SIZE)

        self.auto_resizing = False
        self.two_columns = False
        self.dragging_key = None

        # Панель кнопок
        self.control_frame = tk.Frame(self.root, bg="#333333")
        self.control_frame.pack(side="top", fill="x")

        self.main_frame = tk.Frame(self.root, bg="#222222")
        self.main_frame.pack(side="top", fill="both", expand=True)

        self.main_frame.grid_columnconfigure(0, weight=1, uniform="col")
        self.main_frame.grid_columnconfigure(1, weight=0, uniform="col")

        self.buttons = {}
        self.cards = {}
        self.layout = {}

        # Создаём карточки
        self.cards["A"] = AnalogClockCard(self.main_frame, self)
        self.cards["D"] = DigitalClockCard(self.main_frame, self)
        self.cards["S"] = StopwatchCard(self.main_frame, self)
        self.cards["C"] = TimerCard(self.main_frame, self)

        # Начальная раскладка: все 4 видимы в одном столбце
        order = 0
        for key in ["A", "D", "S", "C"]:
            self.layout[key] = {"visible": True, "col": 0, "order": order}
            order += 1

        # Кнопки A/D/S/C
        for key, text in [("A", "A"), ("D", "D"), ("S", "S"), ("C", "C")]:
            btn = tk.Button(
                self.control_frame,
                text=text,
                width=3,
                command=lambda k=key: self.toggle_element(k),
                bg="#555555", fg="#ffffff", relief="sunken"
            )
            btn.pack(side="left", padx=3, pady=3)
            self.buttons[key] = btn

        # Кнопка столбца
        self.columns_btn = tk.Button(
            self.control_frame,
            text="►",
            width=3,
            command=self.toggle_columns,
            bg="#444444", fg="#ffffff"
        )
        self.columns_btn.pack(side="right", padx=5, pady=3)

        # Следим за изменением размера окна (чтобы оставалось квадратным)
        self.root.bind("<Configure>", self.on_root_configure)

        # Событие окончания перетаскивания (отпускание кнопки мыши)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_release)

        # Первая раскладка + подгонка окна
        self.relayout()

    # ---------- управление раскладкой и окном ----------

    def on_root_configure(self, event):
        # интересует только главное окно
        if event.widget is not self.root:
            return
        if self.auto_resizing:
            return

        w, h = event.width, event.height
        size = max(w, h, self.MIN_SIZE)
        if w == size and h == size:
            return

        self.auto_resizing = True
        self.root.geometry(f"{size}x{size}")
        self.auto_resizing = False

    def autosize_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        size = max(w, h, self.MIN_SIZE)

        self.auto_resizing = True
        self.root.geometry(f"{size}x{size}")
        self.auto_resizing = False

    def get_visible_in_column(self, col):
        items = [
            k for k, meta in self.layout.items()
            if meta["visible"] and meta["col"] == col
        ]
        items.sort(key=lambda k: self.layout[k]["order"])
        return items

    def relayout(self):
        # Убираем все карточки
        for card in self.cards.values():
            card.grid_forget()

        col_rows = {0: 0, 1: 0}

        # Колонки 0 и 1
        for col in [0, 1]:
            items = self.get_visible_in_column(col)
            for key in items:
                card = self.cards[key]
                card.grid(
                    row=col_rows[col], column=col,
                    sticky="nsew", padx=6, pady=6
                )
                col_rows[col] += 1

        max_rows = max(col_rows.values())
        for r in range(max_rows):
            self.main_frame.grid_rowconfigure(r, weight=1)

        # Настройка ширины колонок
        if self.two_columns:
            self.main_frame.grid_columnconfigure(0, weight=1, uniform="col")
            self.main_frame.grid_columnconfigure(1, weight=1, uniform="col")
        else:
            self.main_frame.grid_columnconfigure(0, weight=1, uniform="col")
            self.main_frame.grid_columnconfigure(1, weight=0, uniform="col")

        self.autosize_window()

    def toggle_element(self, key):
        meta = self.layout[key]
        meta["visible"] = not meta["visible"]

        btn = self.buttons[key]
        if meta["visible"]:
            btn.config(relief="sunken", bg="#555555")
            # новый элемент ставим в конец своего столбца
            col = 0
            meta["col"] = col
            existing = self.get_visible_in_column(col)
            meta["order"] = (max(
                [self.layout[k]["order"] for k in existing],
                default=-1
            ) + 1)
        else:
            btn.config(relief="raised", bg="#222222")

        self.relayout()

    def toggle_columns(self):
        self.two_columns = not self.two_columns
        if self.two_columns:
            self.columns_btn.config(text="◄")
        else:
            self.columns_btn.config(text="►")
            # Переносим все элементы в левый столбец, упорядоченно
            visible = [
                k for k, m in self.layout.items() if m["visible"]
            ]
            visible.sort(key=lambda k: (
                self.layout[k]["col"], self.layout[k]["order"]
            ))
            for idx, k in enumerate(visible):
                self.layout[k]["col"] = 0
                self.layout[k]["order"] = idx

        self.relayout()

    # ---------- перетаскивание карточек ----------

    def start_drag(self, key):
        self.dragging_key = key

    def on_mouse_release(self, event):
        if not self.dragging_key:
            return

        key = self.dragging_key
        self.dragging_key = None

        main = self.main_frame
        main_x = main.winfo_rootx()
        main_y = main.winfo_rooty()
        main_w = main.winfo_width()
        main_h = main.winfo_height()

        x_root = event.x_root
        y_root = event.y_root

        # Если отпустили вне основной области — не двигаем
        if not (main_x <= x_root <= main_x + main_w and
                main_y <= y_root <= main_y + main_h):
            return

        # Определяем колонку
        if self.two_columns and x_root > main_x + main_w / 2:
            target_col = 1
        else:
            target_col = 0

        # Список видимых в этой колонке, кроме перетаскиваемого
        col_items = self.get_visible_in_column(target_col)
        col_items = [k for k in col_items if k != key]

        if not col_items:
            # единственный элемент в колонке
            self.layout[key]["col"] = target_col
            self.layout[key]["order"] = 0
            self.relayout()
            return

        # Центры карточек в этой колонке
        centers = []
        for k in col_items:
            w = self.cards[k]
            cy = w.winfo_rooty() + w.winfo_height() / 2
            centers.append((k, cy))

        y = y_root
        # Определяем позицию вставки
        if y < centers[0][1]:
            insert_idx = 0
        elif y > centers[-1][1]:
            insert_idx = len(centers)
        else:
            insert_idx = len(centers)
            for i in range(len(centers) - 1):
                if centers[i][1] <= y < centers[i + 1][1]:
                    insert_idx = i + 1
                    break

        new_list = [k for (k, _) in centers]
        new_list.insert(insert_idx, key)

        for idx, k in enumerate(new_list):
            self.layout[k]["col"] = target_col
            self.layout[k]["order"] = idx

        self.relayout()

    # ---------- обновление всех элементов ----------

    def update_all(self):
        now_dt = datetime.datetime.now()
        now_ts = time.time()
        for card in self.cards.values():
            card.tick(now_dt, now_ts)
        self.root.after(100, self.update_all)

    def start(self):
        self.update_all()
        self.root.mainloop()


# ---------------------------------------------------------
# Запуск
# ---------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ClockApp(root)
    app.start()