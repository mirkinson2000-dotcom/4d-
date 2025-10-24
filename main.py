import pygame
import numpy as np
from math import *
import random
import os
import sys
#если кто спросит как работает код я отвечу 42 для справки код писала нейросеть

# УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ДЛЯ ПУТЕЙ
def get_resource_path(relative_path):
    """Работает и в PyCharm и в собранном приложении"""
    try:
        # Для собранного приложения
        base_path = sys._MEIPASS
    except AttributeError:
        # Для PyCharm и обычного запуска
        base_path = os.path.abspath(".")

    # Пробуем найти файл в разных местах
    possible_paths = [
        os.path.join(base_path, relative_path),  # Прямо в папке
        os.path.join(base_path, "4d", relative_path),  # В папке 4d
        os.path.join(os.path.dirname(__file__), relative_path),  # Рядом со скриптом
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Если файл не найден, возвращаем исходный путь
    return relative_path


# РАБОТАЕТ И В PYCHARM И В ПРИЛОЖЕНИИ
# Если запуск из PyCharm - раскомментируй следующую строку:
# os.chdir('4d')  # ← РАСКОММЕНТИРУЙ ДЛЯ PYCHARM если не работает только

# Инициализация Pygame
pygame.init()

# Оконный режим
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4D ВИЗУАЛИЗАТОР")
clock = pygame.time.Clock()

# ========== НАСТРОЙКИ ==========
COLOR_MODE = True
ROTATION_SPEED = 1.0
CURRENT_SHAPE = 0
SHOW_TRAILS = False
SHOW_GLOW = False
RGB_MODE = False
PAUSED = False
ZOOM_LEVEL = 1.0

# Для кнопок вращения
rotation_buttons = []
manual_rotation_speed = 0.05

# Для следа
TRAILS = []
TRAIL_DURATION = 1.5

# Сохраняем углы для каждой фигуры отдельно
shape_angles = {
    0: [0, 0, 0, 0, 0, 0],  # Тессеракт
    1: [0, 0, 0, 0, 0, 0],  # Гиперсфера
    2: [0, 0, 0, 0, 0, 0],  # Гипертетраэдр
    3: [0, 0, 0, 0, 0, 0],  # 4D Тор
    4: [0, 0, 0, 0, 0, 0]  # Гипероктаэдр
}

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (80, 80, 255)
YELLOW = (255, 255, 80)
PURPLE = (255, 80, 255)
CYAN = (80, 255, 255)
ORANGE = (255, 160, 40)
BRIGHT_GREEN = (100, 255, 100)

# Цвета для UI
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (200, 200, 200)
ACCENT_COLOR = (0, 150, 255)
HOVER_COLOR = (0, 180, 255)
ACTIVE_COLOR = (0, 200, 100)

# Цвета для серого режима
GRAY_DARK = (20, 20, 20)
GRAY_MEDIUM = (120, 120, 120)
GRAY_LIGHT = (180, 180, 180)
GRAY_BRIGHT = (220, 220, 220)

# Угол обзора камеры
fov = 90
aspect_ratio = WIDTH / HEIGHT
near = 0.1
far = 1000

# Загружаем иконки с универсальными путями
ICONS = {}
icon_files = {
    'left': 'arrow_left.png',
    'right': 'arrow_right.png',
    'up': 'arrow_up.png',
    'down': 'arrow_down.png',
    'up_left': 'arrow_up_left.png',
    'up_right': 'arrow_up_right.png',
    'down_left': 'arrow_down_left.png',
    'down_right': 'arrow_down_right.png',
    'rotate_left': 'rotate_left.png',
    'rotate_right': 'rotate_right.png',
    'reset': 'reset.png'
}

print("=== ЗАГРУЗКА ИКОНОК ===")
for key, filename in icon_files.items():
    try:
        full_path = get_resource_path(filename)
        print(f"Пробуем загрузить: {filename} -> {full_path}")

        if os.path.exists(full_path):
            icon = pygame.image.load(full_path).convert_alpha()
            ICONS[key] = pygame.transform.smoothscale(icon, (30, 30))
            print(f"✓ Успешно: {filename}")
        else:
            print(f"✗ Файл не найден: {filename}")
            ICONS[key] = None
    except Exception as e:
        print(f"✗ Ошибка загрузки {filename}: {e}")
        ICONS[key] = None

print("=== ЗАГРУЗКА ЗАВЕРШЕНА ===")


# Остальной код без изменений...
# Матрица проекции
def projection_matrix(fov, aspect_ratio, near, far):
    f = 1 / tan(radians(fov) / 2)
    return np.array([
        [f / aspect_ratio, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
        [0, 0, -1, 0]
    ])


projection = projection_matrix(fov, aspect_ratio, near, far)


# ========== ФИГУРЫ ==========
def create_tesseract():
    vertices = np.array([
        [-1, -1, -1, -1], [1, -1, -1, -1], [1, 1, -1, -1], [-1, 1, -1, -1],
        [-1, -1, 1, -1], [1, -1, 1, -1], [1, 1, 1, -1], [-1, 1, 1, -1],
        [-1, -1, -1, 1], [1, -1, -1, 1], [1, 1, -1, 1], [-1, 1, -1, 1],
        [-1, -1, 1, 1], [1, -1, 1, 1], [1, 1, 1, 1], [-1, 1, 1, 1]
    ]) * 0.8

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7),
        (8, 9), (9, 10), (10, 11), (11, 8), (12, 13), (13, 14), (14, 15), (15, 12), (8, 12), (9, 13), (10, 14),
        (11, 15),
        (0, 8), (1, 9), (2, 10), (3, 11), (4, 12), (5, 13), (6, 14), (7, 15)
    ]
    return vertices, edges, "ТЕССЕРАКТ"


def create_hypersphere(resolution=20):
    vertices = []
    edges = []

    for i in range(resolution):
        for j in range(resolution):
            u = i * pi / resolution
            v = j * 2 * pi / resolution
            x = sin(u) * cos(v)
            y = sin(u) * sin(v)
            z = cos(u) * cos(v)
            w = cos(u) * sin(v)
            vertices.append([x, y, z, w])

    for i in range(resolution):
        for j in range(resolution):
            current = i * resolution + j
            next_i = ((i + 1) % resolution) * resolution + j
            next_j = i * resolution + ((j + 1) % resolution)
            edges.append((current, next_i))
            edges.append((current, next_j))

    vertices = np.array(vertices) * 1.5
    return vertices, edges, "ГИПЕРСФЕРА"


def create_hypertetrahedron():
    vertices = np.array([
        [1, 0, 0, -0.5],
        [-0.5, 0.866, 0, -0.5],
        [-0.5, -0.866, 0, -0.5],
        [0, 0, 1, 0.5],
        [0, 0, -1, 0.5]
    ]) * 1.3
    edges = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            edges.append((i, j))
    return vertices, edges, "ГИПЕРТЕТРАЭДР"


def create_torus4d(major_radius=1.0, minor_radius=0.3, resolution=20):
    vertices = []
    edges = []

    for i in range(resolution):
        for j in range(resolution):
            u = i * 2 * pi / resolution
            v = j * 2 * pi / resolution
            x = (major_radius + minor_radius * cos(v)) * cos(u)
            y = (major_radius + minor_radius * cos(v)) * sin(u)
            z = minor_radius * sin(v) * cos(u)
            w = minor_radius * sin(v) * sin(u)
            vertices.append([x, y, z, w])

    for i in range(resolution):
        for j in range(resolution):
            current = i * resolution + j
            next_i = ((i + 1) % resolution) * resolution + j
            next_j = i * resolution + ((j + 1) % resolution)
            edges.append((current, next_i))
            edges.append((current, next_j))

    return np.array(vertices) * 1.2, edges, "4D ТОР"


def create_hyperoctahedron():
    vertices = np.array([
        [1, 0, 0, 0],
        [-1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, -1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, -1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, -1]
    ]) * 1.2
    edges = []
    for i in range(len(vertices)):
        for j in range(i + 1, len(vertices)):
            non_zero_i = np.where(vertices[i] != 0)[0]
            non_zero_j = np.where(vertices[j] != 0)[0]
            if len(non_zero_i) == 1 and len(non_zero_j) == 1:
                edges.append((i, j))
    return vertices, edges, "ГИПЕРОКТАЭДР"


# Функция для получения RGB цвета
def get_rgb_color(angle, saturation=0.8, value=0.9):
    angle = angle % 360
    h = angle / 60.0
    i = int(h)
    f = h - i
    p = value * (1 - saturation)
    q = value * (1 - saturation * f)
    t = value * (1 - saturation * (1 - f))

    if i == 0:
        return (int(value * 255), int(t * 255), int(p * 255))
    elif i == 1:
        return (int(q * 255), int(value * 255), int(p * 255))
    elif i == 2:
        return (int(p * 255), int(value * 255), int(t * 255))
    elif i == 3:
        return (int(p * 255), int(q * 255), int(value * 255))
    elif i == 4:
        return (int(t * 255), int(p * 255), int(value * 255))
    else:
        return (int(value * 255), int(p * 255), int(q * 255))


# Функция для вращения в 4D пространстве
def rotate_4d(point, angles):
    x, y, z, w = point

    xy_angle, xz_angle, xw_angle, yz_angle, yw_angle, zw_angle = angles

    # Вращение XY
    cos_xy, sin_xy = cos(xy_angle), sin(xy_angle)
    x, y = x * cos_xy - y * sin_xy, x * sin_xy + y * cos_xy

    # Вращение XZ
    cos_xz, sin_xz = cos(xz_angle), sin(xz_angle)
    x, z = x * cos_xz - z * sin_xz, x * sin_xz + z * cos_xz

    # Вращение XW
    cos_xw, sin_xw = cos(xw_angle), sin(xw_angle)
    x, w = x * cos_xw - w * sin_xw, x * sin_xw + w * cos_xw

    # Вращение YZ
    cos_yz, sin_yz = cos(yz_angle), sin(yz_angle)
    y, z = y * cos_yz - z * sin_yz, y * sin_yz + z * cos_yz

    # Вращение YW
    cos_yw, sin_yw = cos(yw_angle), sin(yw_angle)
    y, w = y * cos_yw - w * sin_yw, y * sin_yw + w * cos_yw

    # Вращение ZW
    cos_zw, sin_zw = cos(zw_angle), sin(zw_angle)
    z, w = z * cos_zw - w * sin_zw, z * sin_zw + w * cos_zw

    return [x, y, z, w]


# Функция для получения цвета
def get_color(edge_index, vertex_index, total_edges, color_mode, shape_type, speed_factor, rgb_angle):
    if RGB_MODE and color_mode:
        return get_rgb_color(rgb_angle, 0.9, 0.9)

    if not color_mode:
        if shape_type == 0:
            if edge_index < 12:
                return (180, 180, 180)
            elif edge_index < 24:
                return (140, 140, 140)
            else:
                return (100, 100, 100)
        elif shape_type == 1:
            return (160, 160, 160)
        elif shape_type == 2:
            colors = [(180, 180, 180), (160, 160, 160), (140, 140, 140), (200, 200, 200), (120, 120, 120)]
            return colors[vertex_index % len(colors)]
        elif shape_type == 3:
            return (150, 150, 150)
        elif shape_type == 4:
            return (170, 170, 170)
        else:
            return (130, 130, 130)

    if shape_type == 0:
        if edge_index < 12:
            return RED
        elif edge_index < 24:
            return BLUE
        else:
            return GREEN
    elif shape_type == 1:
        return CYAN
    elif shape_type == 2:
        colors = [RED, GREEN, BLUE, YELLOW, PURPLE]
        return colors[vertex_index % len(colors)]
    elif shape_type == 3:
        return (200, 150, 100)
    elif shape_type == 4:
        return (100, 200, 200)
    else:
        return (150, 100, 200)


def get_vertex_color(color_mode, shape_type, speed_factor, rgb_angle):
    if RGB_MODE and color_mode:
        return get_rgb_color(rgb_angle + 180, 0.9, 1.0)

    if not color_mode:
        return (220, 220, 220)

    if shape_type == 0:
        return YELLOW
    elif shape_type == 1:
        return CYAN
    elif shape_type == 2:
        return ORANGE
    elif shape_type == 3:
        return (255, 200, 100)
    elif shape_type == 4:
        return (200, 255, 200)
    else:
        return (255, 100, 255)


# Функция для отрисовки иконки
def draw_icon(surface, rect, icon_key, size=None):
    icon = ICONS.get(icon_key)
    if icon is not None:
        if size:
            icon = pygame.transform.smoothscale(icon, size)
        icon_rect = icon.get_rect(center=rect.center)
        surface.blit(icon, icon_rect)
    else:
        pygame.draw.circle(surface, WHITE, rect.center, 10)


# Класс для красивых кнопок
class Button:
    def __init__(self, x, y, width, height, text, action=None, tooltip=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.tooltip = tooltip
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, surface):
        if self.is_pressed:
            bg_color = ACTIVE_COLOR
            border_color = (min(ACTIVE_COLOR[0] + 40, 255),
                            min(ACTIVE_COLOR[1] + 40, 255),
                            min(ACTIVE_COLOR[2] + 40, 255))
        elif self.is_hovered:
            bg_color = HOVER_COLOR
            border_color = (min(HOVER_COLOR[0] + 30, 255),
                            min(HOVER_COLOR[1] + 30, 255),
                            min(HOVER_COLOR[2] + 30, 255))
        else:
            bg_color = ACCENT_COLOR
            border_color = (min(ACCENT_COLOR[0] + 20, 255),
                            min(ACCENT_COLOR[1] + 20, 255),
                            min(ACCENT_COLOR[2] + 20, 255))

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=8)

        font = pygame.font.Font(None, 24)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                if self.action:
                    return self.action()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False
        return False


# Класс для кнопок вращения
class RotationButton:
    def __init__(self, x, y, width, height, icon_key, description, axis_index, direction):
        self.rect = pygame.Rect(x, y, width, height)
        self.icon_key = icon_key
        self.description = description
        self.axis_index = axis_index
        self.direction = direction
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, surface):
        if self.is_pressed:
            bg_color = ACTIVE_COLOR
            border_color = (min(ACTIVE_COLOR[0] + 40, 255), min(ACTIVE_COLOR[1] + 40, 255),
                            min(ACTIVE_COLOR[2] + 40, 255))
        elif self.is_hovered:
            bg_color = HOVER_COLOR
            border_color = (min(HOVER_COLOR[0] + 30, 255), min(HOVER_COLOR[1] + 30, 255), min(HOVER_COLOR[2] + 30, 255))
        else:
            bg_color = ACCENT_COLOR
            border_color = (min(ACCENT_COLOR[0] + 20, 255), min(ACCENT_COLOR[1] + 20, 255),
                            min(ACCENT_COLOR[2] + 20, 255))

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=8)

        draw_icon(surface, self.rect, self.icon_key)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False
        return False

    def update(self):
        if self.is_pressed:
            shape_angles[CURRENT_SHAPE][self.axis_index] += self.direction * manual_rotation_speed


# Класс для кнопки сброса
class ResetButton:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.is_pressed = False

    def draw(self, surface):
        if self.is_pressed:
            bg_color = ACTIVE_COLOR
            border_color = (min(ACTIVE_COLOR[0] + 40, 255), min(ACTIVE_COLOR[1] + 40, 255),
                            min(ACTIVE_COLOR[2] + 40, 255))
        elif self.is_hovered:
            bg_color = HOVER_COLOR
            border_color = (min(HOVER_COLOR[0] + 30, 255), min(HOVER_COLOR[1] + 30, 255), min(HOVER_COLOR[2] + 30, 255))
        else:
            bg_color = ACCENT_COLOR
            border_color = (min(ACCENT_COLOR[0] + 20, 255), min(ACCENT_COLOR[1] + 20, 255),
                            min(ACCENT_COLOR[2] + 20, 255))

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, 3, border_radius=8)

        draw_icon(surface, self.rect, 'reset')

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_pressed = False
        return False

    def update(self):
        if self.is_pressed:
            for i in range(len(shape_angles[CURRENT_SHAPE])):
                shape_angles[CURRENT_SHAPE][i] = 0


# Функции для кнопок
def toggle_pause():
    global PAUSED
    PAUSED = not PAUSED
    return True


def toggle_trails():
    global SHOW_TRAILS
    SHOW_TRAILS = not SHOW_TRAILS
    if not SHOW_TRAILS:
        TRAILS.clear()
    return True


def toggle_glow():
    global SHOW_GLOW
    SHOW_GLOW = not SHOW_GLOW
    return True


def toggle_rgb():
    global RGB_MODE
    RGB_MODE = not RGB_MODE
    return True


def random_orientation():
    for i in range(len(shape_angles[CURRENT_SHAPE])):
        shape_angles[CURRENT_SHAPE][i] = random.uniform(0, 2 * pi)
    return True


# Создаём фигуры
shapes = [
    create_tesseract(),
    create_hypersphere(20),
    create_hypertetrahedron(),
    create_torus4d(),
    create_hyperoctahedron()
]

# Создаём основные кнопки
buttons = []
button_x = WIDTH - 150
button_y = 25
button_width = 130
button_height = 35

buttons.append(Button(button_x, button_y, button_width, button_height, "ПАУЗА", toggle_pause))
buttons.append(Button(button_x, button_y + 45, button_width, button_height, "СЛЕД", toggle_trails))
buttons.append(Button(button_x, button_y + 90, button_width, button_height, "СВЕЧЕНИЕ", toggle_glow))
buttons.append(Button(button_x, button_y + 135, button_width, button_height, "RGB", toggle_rgb))
buttons.append(Button(button_x, button_y + 180, button_width, button_height, "ПЕРЕМЕШАТЬ", random_orientation))

# Создаём кнопки вращения с иконками
rotation_buttons = []
rotation_button_size = 50
rotation_start_x = WIDTH - 180
rotation_start_y = HEIGHT - 200

rotation_buttons.append(RotationButton(rotation_start_x - rotation_button_size, rotation_start_y,
                                       rotation_button_size, rotation_button_size, 'left', "XY вращение", 0, -1))
rotation_buttons.append(RotationButton(rotation_start_x + rotation_button_size, rotation_start_y,
                                       rotation_button_size, rotation_button_size, 'right', "XY вращение", 0, 1))
rotation_buttons.append(RotationButton(rotation_start_x, rotation_start_y - rotation_button_size,
                                       rotation_button_size, rotation_button_size, 'up', "XZ вращение", 1, -1))
rotation_buttons.append(RotationButton(rotation_start_x, rotation_start_y + rotation_button_size,
                                       rotation_button_size, rotation_button_size, 'down', "XZ вращение", 1, 1))

rotation_buttons.append(RotationButton(rotation_start_x - rotation_button_size, rotation_start_y - rotation_button_size,
                                       rotation_button_size, rotation_button_size, 'up_left', "XW вращение", 2, -1))
rotation_buttons.append(RotationButton(rotation_start_x + rotation_button_size, rotation_start_y - rotation_button_size,
                                       rotation_button_size, rotation_button_size, 'up_right', "XW вращение", 2, 1))
rotation_buttons.append(RotationButton(rotation_start_x - rotation_button_size, rotation_start_y + rotation_button_size,
                                       rotation_button_size, rotation_button_size, 'down_left', "YZ вращение", 3, -1))
rotation_buttons.append(RotationButton(rotation_start_x + rotation_button_size, rotation_start_y + rotation_button_size,
                                       rotation_button_size, rotation_button_size, 'down_right', "YZ вращение", 3, 1))

rotation_buttons.append(RotationButton(rotation_start_x - rotation_button_size * 2, rotation_start_y,
                                       rotation_button_size, rotation_button_size, 'rotate_left', "YW вращение", 4, -1))
rotation_buttons.append(RotationButton(rotation_start_x + rotation_button_size * 2, rotation_start_y,
                                       rotation_button_size, rotation_button_size, 'rotate_right', "YW вращение", 4, 1))

reset_button = ResetButton(rotation_start_x, rotation_start_y,
                           rotation_button_size, rotation_button_size)

# Основной цикл игры
running = True
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
very_small_font = pygame.font.Font(None, 20)
rgb_angle = 0

while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks() / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                COLOR_MODE = not COLOR_MODE
            elif event.key == pygame.K_1:
                CURRENT_SHAPE = 0;
                TRAILS.clear()
            elif event.key == pygame.K_2:
                CURRENT_SHAPE = 1;
                TRAILS.clear()
            elif event.key == pygame.K_3:
                CURRENT_SHAPE = 2;
                TRAILS.clear()
            elif event.key == pygame.K_4:
                CURRENT_SHAPE = 3;
                TRAILS.clear()
            elif event.key == pygame.K_5:
                CURRENT_SHAPE = 4;
                TRAILS.clear()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                ROTATION_SPEED = min(ROTATION_SPEED + 0.5, 3.0)
            elif event.key == pygame.K_MINUS:
                ROTATION_SPEED = max(ROTATION_SPEED - 0.5, 0.5)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                ZOOM_LEVEL = min(ZOOM_LEVEL * 1.1, 3.0)
            elif event.button == 5:
                ZOOM_LEVEL = max(ZOOM_LEVEL / 1.1, 1.0)

        for button in buttons:
            button.handle_event(event)

        if PAUSED:
            for rotation_button in rotation_buttons:
                rotation_button.handle_event(event)
            reset_button.handle_event(event)

    if PAUSED:
        for rotation_button in rotation_buttons:
            rotation_button.update()
        reset_button.update()

    if not PAUSED:
        angles = shape_angles[CURRENT_SHAPE]
        angles[0] += ROTATION_SPEED * 0.3 * dt
        angles[1] += ROTATION_SPEED * 0.5 * dt
        angles[2] += ROTATION_SPEED * 0.7 * dt
        angles[3] += ROTATION_SPEED * 0.4 * dt
        angles[4] += ROTATION_SPEED * 0.6 * dt
        angles[5] += ROTATION_SPEED * 0.8 * dt

    rgb_angle += dt * 60

    for button in buttons:
        button.check_hover(mouse_pos)

    if PAUSED:
        for rotation_button in rotation_buttons:
            rotation_button.check_hover(mouse_pos)
        reset_button.check_hover(mouse_pos)

    screen.fill(BLACK if COLOR_MODE else GRAY_DARK)

    vertices, edges, shape_name = shapes[CURRENT_SHAPE]

    projected_points = []

    for vertex in vertices:
        rotated_4d = rotate_4d(vertex, shape_angles[CURRENT_SHAPE])

        scale_4d = 1.8 * ZOOM_LEVEL
        perspective = 1.0 / (rotated_4d[3] + 3.5)

        x_3d = rotated_4d[0] * scale_4d * perspective
        y_3d = rotated_4d[1] * scale_4d * perspective
        z_3d = rotated_4d[2] * scale_4d * perspective

        z_3d += 4

        point_4d = np.array([x_3d, y_3d, z_3d, 1])
        projected = np.dot(projection, point_4d)

        if projected[3] != 0:
            projected /= projected[3]

        x = int(round(projected[0] * WIDTH / 2 + WIDTH / 2))
        y = int(round(projected[1] * HEIGHT / 2 + HEIGHT / 2))

        projected_points.append((x, y))

    if SHOW_TRAILS and len(projected_points) > 0:
        if COLOR_MODE:
            trail_color = get_rgb_color(rgb_angle, 0.9, 0.8)
        else:
            trail_color = (120, 120, 120)

        TRAILS.append({
            'points': [(x, y) for x, y in projected_points],
            'time': current_time,
            'color': trail_color
        })

        TRAILS = [trail for trail in TRAILS if current_time - trail['time'] <= TRAIL_DURATION]

        for trail in TRAILS:
            points = trail['points']
            trail_color = trail['color']
            age = current_time - trail['time']

            fade_progress = age / TRAIL_DURATION
            if fade_progress > 0.5:
                alpha = 1.0 - (fade_progress - 0.5) / 0.5
                faded_color = tuple(int(c * alpha) for c in trail_color)
            else:
                faded_color = trail_color

            for edge in edges:
                if (edge[0] < len(points) and edge[1] < len(points)):
                    start_pos = points[edge[0]]
                    end_pos = points[edge[1]]
                    pygame.draw.line(screen, faded_color, start_pos, end_pos, 2)

    for i, edge in enumerate(edges):
        if edge[0] < len(projected_points) and edge[1] < len(projected_points):
            start_pos = projected_points[edge[0]]
            end_pos = projected_points[edge[1]]

            color = get_color(i, edge[0], len(edges), COLOR_MODE, CURRENT_SHAPE,
                              ROTATION_SPEED / 3.0, rgb_angle)

            if SHOW_GLOW:
                glow_color = tuple(min(255, c + 60) for c in color)
                pygame.draw.line(screen, glow_color, start_pos, end_pos, 5)

            line_width = 3
            pygame.draw.line(screen, color, start_pos, end_pos, line_width)

    vertex_color = get_vertex_color(COLOR_MODE, CURRENT_SHAPE, ROTATION_SPEED / 3.0, rgb_angle)
    for i, point in enumerate(projected_points):
        radius = 4
        pygame.draw.circle(screen, vertex_color, point, radius)

    for button in buttons:
        button.draw(screen)

    if PAUSED:
        for rotation_button in rotation_buttons:
            rotation_button.draw(screen)
        reset_button.draw(screen)

    mode_text = "ЦВЕТНОЙ" if COLOR_MODE else "СЕРЫЙ"
    if RGB_MODE and COLOR_MODE:
        mode_text = "RGB"

    text = font.render(f"{shape_name}", True, WHITE)
    screen.blit(text, (20, 20))

    status_text = f"Скорость: {ROTATION_SPEED:.1f}x | Масштаб: {ZOOM_LEVEL:.1f}x | {mode_text}"
    if PAUSED:
        status_text += " | ПАУЗА"

    speed_text = small_font.render(status_text, True, WHITE if COLOR_MODE else LIGHT_GRAY)
    screen.blit(speed_text, (20, 60))

    controls = [
        "1-5: Выбор фигур    +/-: Скорость",
        "ПРОБЕЛ: Цвета       Колесико: Масштаб",
        "ESC: Выход"
    ]

    for i, control in enumerate(controls):
        control_text = small_font.render(control, True, WHITE if COLOR_MODE else LIGHT_GRAY)
        screen.blit(control_text, (20, 100 + i * 25))

    if PAUSED:
        hint_bg = pygame.Rect(WIDTH - 320, 250, 300, 220)
        pygame.draw.rect(screen, (0, 0, 0, 180), hint_bg, border_radius=8)
        pygame.draw.rect(screen, ACCENT_COLOR, hint_bg, 2, border_radius=8)

        hint_title = small_font.render("РУЧНОЕ УПРАВЛЕНИЕ ВРАЩЕНИЕМ", True, BRIGHT_GREEN if COLOR_MODE else LIGHT_GRAY)
        screen.blit(hint_title, (WIDTH - 310, 260))

        rotation_hints = [
            ('left', 'right', "Вращение XY (горизонталь)"),
            ('up', 'down', "Вращение XZ (вертикаль)"),
            ('up_left', 'up_right', "Вращение XW (4D-диагональ)"),
            ('down_left', 'down_right', "Вращение YZ (глубина)"),
            ('rotate_left', 'rotate_right', "Вращение YW (4D-круг)"),
            ('reset', None, "Сброс вращения")
        ]

        y_offset = 290
        icon_size = (20, 20)

        for left_icon, right_icon, description in rotation_hints:
            if left_icon:
                left_rect = pygame.Rect(WIDTH - 300, y_offset, 20, 20)
                draw_icon(screen, left_rect, left_icon, icon_size)

            if right_icon:
                sep_text = very_small_font.render(" / ", True, BRIGHT_GREEN if COLOR_MODE else LIGHT_GRAY)
                screen.blit(sep_text, (WIDTH - 275, y_offset))

                right_rect = pygame.Rect(WIDTH - 260, y_offset, 20, 20)
                draw_icon(screen, right_rect, right_icon, icon_size)

            desc_text = very_small_font.render(description, True, BRIGHT_GREEN if COLOR_MODE else LIGHT_GRAY)
            screen.blit(desc_text, (WIDTH - 235, y_offset))

            y_offset += 25

        info_text = very_small_font.render("Зажимайте кнопки для вращения", True, YELLOW if COLOR_MODE else LIGHT_GRAY)
        screen.blit(info_text, (WIDTH - 300, y_offset + 10))

    info_bg = pygame.Rect(20, 180, 250, 120)
    pygame.draw.rect(screen, (0, 0, 0, 180), info_bg, border_radius=8)
    pygame.draw.rect(screen, ACCENT_COLOR, info_bg, 2, border_radius=8)

    shape_info = [
        f"Вершин: {len(vertices)}",
        f"Рёбер: {len(edges)}",
        f"Фигура: {CURRENT_SHAPE + 1}/5",
        "Автономное сохранение",
        "положения для каждой фигуры"
    ]

    for i, info in enumerate(shape_info):
        info_text = very_small_font.render(info, True, WHITE if COLOR_MODE else LIGHT_GRAY)
        screen.blit(info_text, (30, 190 + i * 20))

    pygame.display.flip()

pygame.quit()