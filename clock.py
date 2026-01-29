import tkinter as tk
import math
import datetime

# Размер окна и параметры циферблата
WIDTH = HEIGHT = 500
CENTER = WIDTH // 2
RADIUS = 220

root = tk.Tk()
root.title("Analog Clock")
root.resizable(False, False)
root.configure(bg="#222222")

canvas = tk.Canvas(
    root,
    width=WIDTH,
    height=HEIGHT,
    bg="#222222",
    highlightthickness=0
)
canvas.pack()

cx = cy = CENTER

# Фон с лёгким градиентом
edge_color = (220, 220, 220)
center_color = (255, 255, 255)

for i in range(RADIUS, 0, -1):
    t = i / RADIUS  # 1 на краю, 0 в центре
    r = int(edge_color[0] * t + center_color[0] * (1 - t))
    g = int(edge_color[1] * t + center_color[1] * (1 - t))
    b = int(edge_color[2] * t + center_color[2] * (1 - t))
    color = f"#{r:02x}{g:02x}{b:02x}"
    canvas.create_oval(cx - i, cy - i, cx + i, cy + i,
                       outline=color, fill=color)

# Внешняя граница
canvas.create_oval(
    cx - RADIUS,
    cy - RADIUS,
    cx + RADIUS,
    cy + RADIUS,
    width=4,
    outline="#000000"
)

# Риски (минутные и часовые)
for i in range(60):
    angle = math.radians(i * 6)
    if i % 5 == 0:  # каждые 5 минут – толстая риска
        inner = RADIUS - 25
        width_line = 4
    else:
        inner = RADIUS - 15
        width_line = 1

    x1 = cx + inner * math.sin(angle)
    y1 = cy - inner * math.cos(angle)
    x2 = cx + RADIUS * math.sin(angle)
    y2 = cy - RADIUS * math.cos(angle)

    canvas.create_line(x1, y1, x2, y2,
                       fill="#000000", width=width_line)

# Цифры 1–12
for h in range(1, 13):
    angle = math.radians(h * 30)
    num_radius = RADIUS - 55
    x = cx + num_radius * math.sin(angle)
    y = cy - num_radius * math.cos(angle)
    canvas.create_text(
        x, y,
        text=str(h),
        font=("Arial", 26, "bold")
    )

# Стрелки (изначально просто создаём, потом двигаем)
hour_hand = canvas.create_line(
    cx, cy, cx, cy - RADIUS * 0.5,
    width=8,
    fill="#000000",
    capstyle=tk.ROUND
)
min_hand = canvas.create_line(
    cx, cy, cx, cy - RADIUS * 0.75,
    width=4,
    fill="#000000",
    capstyle=tk.ROUND
)
sec_hand = canvas.create_line(
    cx, cy, cx, cy - RADIUS * 0.85,
    width=2,
    fill="#ff0000",
    capstyle=tk.ROUND
)

# Красная точка в центре
canvas.create_oval(
    cx - 8, cy - 8, cx + 8, cy + 8,
    fill="#ff0000",
    outline="#000000",
    width=2
)


def update_clock():
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

    xh, yh = get_xy(angle_hour, RADIUS * 0.5)
    xm, ym = get_xy(angle_min, RADIUS * 0.75)
    xs, ys = get_xy(angle_sec, RADIUS * 0.85)

    canvas.coords(hour_hand, cx, cy, xh, yh)
    canvas.coords(min_hand, cx, cy, xm, ym)
    canvas.coords(sec_hand, cx, cy, xs, ys)

    # Обновляем примерно 25 раз в секунду (плавная секундная стрелка)
    root.after(40, update_clock)


update_clock()
root.mainloop()