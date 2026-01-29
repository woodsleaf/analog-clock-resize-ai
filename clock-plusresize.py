import tkinter as tk
import math
import datetime

BASE_SIZE = 500  # стартовый размер окна

root = tk.Tk()
root.title("Analog Clock (Resizable)")
root.geometry(f"{BASE_SIZE}x{BASE_SIZE}")
root.minsize(250, 250)       # чтобы окно совсем крошечным не было
root.configure(bg="#222222")

canvas = tk.Canvas(root, bg="#222222", highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Глобальные переменные для центра, радиуса и стрелок
cx = cy = BASE_SIZE / 2
radius = BASE_SIZE / 2 - 20

hour_hand = None
min_hand = None
sec_hand = None


def draw_static():
    """Рисуем фон, риски, цифры и создаём стрелки под текущий размер."""
    global cx, cy, radius, hour_hand, min_hand, sec_hand

    canvas.delete("all")

    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 10 or h < 10:
        return

    size = min(w, h)
    radius = size / 2 - 20
    cx = w / 2
    cy = h / 2

    # Градиентный фон
    edge_color = (220, 220, 220)
    center_color = (255, 255, 255)
    r_int = int(radius)

    for i in range(r_int, 0, -1):
        t = i / radius
        r = int(edge_color[0] * t + center_color[0] * (1 - t))
        g = int(edge_color[1] * t + center_color[1] * (1 - t))
        b = int(edge_color[2] * t + center_color[2] * (1 - t))
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_oval(cx - i, cy - i, cx + i, cy + i,
                           outline=color, fill=color)

    # Внешняя граница
    canvas.create_oval(
        cx - radius, cy - radius,
        cx + radius, cy + radius,
        width=4, outline="#000000"
    )

    # Риски (минутные и часовые)
    for i in range(60):
        angle = math.radians(i * 6)
        if i % 5 == 0:  # часовая риска
            inner = radius * 0.88
            width_line = 4
        else:           # минутная тонкая риска
            inner = radius * 0.93
            width_line = 1

        x1 = cx + inner * math.sin(angle)
        y1 = cy - inner * math.cos(angle)
        x2 = cx + radius * math.sin(angle)
        y2 = cy - radius * math.cos(angle)
        canvas.create_line(x1, y1, x2, y2,
                           fill="#000000", width=width_line)

    # Цифры 1–12
    num_radius = radius * 0.75
    font_size = max(int(size / 18), 10)

    for h_ in range(1, 13):
        angle = math.radians(h_ * 30)
        x = cx + num_radius * math.sin(angle)
        y = cy - num_radius * math.cos(angle)
        canvas.create_text(
            x, y,
            text=str(h_),
            font=("Arial", font_size, "bold")
        )

    # Стрелки (пока просто создаём, координаты задаём в update_clock)
    hour_hand = canvas.create_line(
        cx, cy, cx, cy - radius * 0.5,
        width=max(int(size / 40), 4),
        fill="#000000", capstyle=tk.ROUND
    )
    min_hand = canvas.create_line(
        cx, cy, cx, cy - radius * 0.75,
        width=max(int(size / 80), 3),
        fill="#000000", capstyle=tk.ROUND
    )
    sec_hand = canvas.create_line(
        cx, cy, cx, cy - radius * 0.85,
        width=max(int(size / 120), 2),
        fill="#ff0000", capstyle=tk.ROUND
    )

    # Красная точка в центре
    dot_r = max(int(size / 80), 5)
    canvas.create_oval(
        cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r,
        fill="#ff0000", outline="#000000", width=2
    )


def on_resize(event):
    """Вызывается при изменении размера окна — перерисовываем циферблат."""
    if event.width < 50 or event.height < 50:
        return
    draw_static()


def update_clock():
    """Обновляем положение стрелок по текущему времени."""
    global hour_hand, min_hand, sec_hand, cx, cy, radius

    now = datetime.datetime.now()
    second = now.second + now.microsecond / 1_000_000
    minute = now.minute + second / 60.0
    hour = (now.hour % 12) + minute / 60.0

    angle_sec = math.radians(second * 6)   # 360 / 60
    angle_min = math.radians(minute * 6)
    angle_hour = math.radians(hour * 30)   # 360 / 12

    def get_xy(angle, length):
        x = cx + length * math.sin(angle)
        y = cy - length * math.cos(angle)
        return x, y

    if radius > 0 and hour_hand and min_hand and sec_hand:
        xh, yh = get_xy(angle_hour, radius * 0.5)
        xm, ym = get_xy(angle_min, radius * 0.75)
        xs, ys = get_xy(angle_sec, radius * 0.85)

        canvas.coords(hour_hand, cx, cy, xh, yh)
        canvas.coords(min_hand, cx, cy, xm, ym)
        canvas.coords(sec_hand, cx, cy, xs, ys)

    # примерно 25 раз в секунду
    root.after(40, update_clock)


# Перерисовывать циферблат при изменении размера окна
canvas.bind("<Configure>", on_resize)

# Первичная отрисовка и запуск обновления стрелок
root.update_idletasks()
draw_static()
update_clock()

root.mainloop()