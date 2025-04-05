import pygame
import sys
import random
import os # Добавляем импорт os
from collections import deque
from typing import List, Tuple, Set, Deque, Dict, Optional, Any, Union, TypedDict
import itertools
import heapq
from pygame import Surface
from pygame.font import Font

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы игры
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRIDSIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRIDSIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRIDSIZE

# --- Цветовая Палитра (Темная Тема) ---
COLOR_BACKGROUND = pygame.Color("#282c34")
COLOR_GRID = pygame.Color("#4a4f58")
COLOR_SNAKE = pygame.Color("#61afef")         # Основной цвет змейки
COLOR_SNAKE_HEAD = pygame.Color("#98c379")     # Цвет для отрисовки отдельной головы (если змейка = 1 сегмент)
COLOR_SNAKE_HEAD_GRADIENT = pygame.Color("#c678dd") # Новый цвет головы для градиента
COLOR_SNAKE_TAIL = pygame.Color("#5c6370")      # Цвет хвоста (близкий к цвету пути)
COLOR_FOOD = pygame.Color("#e06c75")
COLOR_PATH_VISUALIZATION = pygame.Color("#d19a66") # Цвет для визуализации пути AI
COLOR_TEXT = pygame.Color("#abb2bf")
COLOR_TEXT_HIGHLIGHT = pygame.Color("#e5c07b")
COLOR_TEXT_WHITE = pygame.Color("#ffffff")
COLOR_BUTTON = pygame.Color("#61afef")
COLOR_BUTTON_HOVER = pygame.Color("#98c379")
COLOR_BUTTON_CLICK = pygame.Color("#56b6c2")
COLOR_SLIDER_BG = pygame.Color("#4a4f58")
COLOR_SLIDER_HANDLE = pygame.Color("#98c379")
COLOR_PANEL_BG = pygame.Color(40, 44, 52, 210) # Полупрозрачный фон панелей
COLOR_CHECKBOX_BORDER = pygame.Color("#abb2bf")
COLOR_CHECKBOX_CHECK = pygame.Color("#98c379")
COLOR_GAMEOVER = pygame.Color("#e06c75")

# --- Шрифты ---
FONT_NAME_PRIMARY = 'Consolas, Calibri, Arial' # Pygame выберет первый доступный
FONT_SIZE_SMALL = 18
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 36
FONT_SIZE_XLARGE = 72

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Определяем директорию текущего скрипта
script_dir = os.path.dirname(__file__)
sound_file_path = os.path.join(script_dir, 'eat.wav') # Строим путь к файлу

# Звук (опционально)
try:
    eat_sound = pygame.mixer.Sound(sound_file_path) # Используем динамический путь
    eat_sound.set_volume(0.05)
except pygame.error:
    eat_sound = None
    print(f"Warning: Sound file '{sound_file_path}' not found or cannot be loaded.")

# Звук Game Over
melody_sound_path = os.path.join(script_dir, 'melody.wav')
try:
    melody_sound = pygame.mixer.Sound(melody_sound_path)
    melody_sound.set_volume(0.1) # Можно настроить громкость отдельно
except pygame.error:
    melody_sound = None
    print(f"Warning: Sound file '{melody_sound_path}' not found or cannot be loaded.")

def draw_object(surface, color, pos):
    rect = pygame.Rect((pos[0] * GRIDSIZE, pos[1] * GRIDSIZE), (GRIDSIZE, GRIDSIZE))
    pygame.draw.rect(surface, color, rect)

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRIDSIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRIDSIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

def draw_button(surface, button, base_color, text, is_hovered, is_clicked):
    button_color = base_color
    if is_clicked:
        button_color = COLOR_BUTTON_CLICK
    elif is_hovered:
        button_color = COLOR_BUTTON_HOVER

    button_rect = pygame.Rect(button)
    pygame.draw.rect(surface, button_color, button_rect, border_radius=8)

    try:
        font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    text_surf = font.render(text, True, COLOR_TEXT_WHITE)
    text_rect = text_surf.get_rect(center=button_rect.center)
    surface.blit(text_surf, text_rect)

def draw_path(surface, path):
    """Отрисовывает предполагаемый путь змейки (для автопилота)."""
    try:
        for p in path:
            draw_object(surface, COLOR_PATH_VISUALIZATION, p)
    except Exception as e:
        print(f"Error drawing path: {e}")
        pass

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.handle_radius = height
        self.handle_width = height
        self.handle_rect = pygame.Rect(0, 0, self.handle_width, self.handle_radius)
        self.handle_rect.centery = self.rect.centery
        self.update_handle_pos()
        self.dragging = False
        try:
            self.font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        except:
            self.font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    def update_handle_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_center_x = self.rect.x + int(ratio * self.rect.width)
        self.handle_rect.centerx = handle_center_x

    def get_handle_bounds_for_collision(self):
        # Увеличиваем область клика для удобства пользователя
        return self.handle_rect.inflate(10, 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_handle_bounds_for_collision().collidepoint(event.pos):
                self.dragging = True
                # Сразу перемещаем ручку к месту клика
                self.move_handle_to_pos(event.pos[0])
            elif self.rect.collidepoint(event.pos): # Клик по треку вне ручки
                self.dragging = True
                self.move_handle_to_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.move_handle_to_pos(event.pos[0])

    def move_handle_to_pos(self, mouse_x):
        mouse_x = max(self.rect.x, min(mouse_x, self.rect.right))
        self.handle_rect.centerx = mouse_x
        ratio = (self.handle_rect.centerx - self.rect.x) / self.rect.width
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        # Округляем значение для внутреннего использования и отображения
        self.value = round(self.value)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_SLIDER_BG, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_SLIDER_HANDLE, self.handle_rect, border_radius=3)
        if self.label:
            label_surf = self.font.render(f"{self.label}: {int(self.value)}", True, COLOR_TEXT)
            label_rect = label_surf.get_rect(midbottom=(self.rect.centerx, self.rect.top - 8))
            surface.blit(label_surf, label_rect)

class Checkbox:
    def __init__(self, x, y, size, label, initial=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = initial
        self.label = label
        try:
            self.font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        except:
            self.font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_CHECKBOX_BORDER, self.rect, border_radius=3, width=2)
        if self.checked:
            check_margin = 5
            points = [
                (self.rect.left + check_margin, self.rect.centery - 2),
                (self.rect.centerx - check_margin / 3, self.rect.bottom - check_margin + 1),
                (self.rect.right - check_margin + 2, self.rect.top + check_margin - 2)
            ]
            pygame.draw.lines(surface, COLOR_CHECKBOX_CHECK, False, points, 3)
        label_surf = self.font.render(self.label, True, COLOR_TEXT)
        surface.blit(label_surf, (self.rect.right + 10, self.rect.centery - label_surf.get_height() // 2))

class PathFind:
    def __init__(self):
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT

    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = position
        directions = [UP, DOWN, LEFT, RIGHT]
        neighbors = []
        for dx, dy in directions:
            nx, ny = (x + dx) % self.grid_width, (y + dy) % self.grid_height
            neighbors.append((nx, ny))
        return neighbors

    def _heuristic(self, pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
        """Манхэттенское расстояние с учетом 'зацикленности' поля."""
        ax, ay = pos_a
        bx, by = pos_b

        # Расстояние по X с учетом "перехода" через край
        dx = abs(ax - bx)
        dist_x = min(dx, self.grid_width - dx)

        # Расстояние по Y с учетом "перехода" через край
        dy = abs(ay - by)
        dist_y = min(dy, self.grid_height - dy)

        return dist_x + dist_y

    def reconstruct_path(self, came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]], goal_node: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Восстанавливает путь от цели к старту по словарю came_from."""
        path = []
        current_pos = goal_node
        while current_pos is not None:
            path.append(current_pos)
            current_pos = came_from.get(current_pos)
        path.reverse() # Разворачиваем путь, т.к. собрали его от цели к старту
        return path

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], snake_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Находит кратчайший путь с помощью A*, УЧИТЫВАЯ движение хвоста змейки.
        Клетка считается проходимой, если к моменту достижения ее змейкой,
        сегмент хвоста, который ее занимал, уже исчезнет.
        """
        snake_length = len(snake_positions)
        snake_body_indices = {pos: i for i, pos in enumerate(snake_positions)}

        # A*: Очередь с приоритетом (f_cost, g_cost, position)
        open_set_heap = [(self._heuristic(start, goal), 0, start)]
        # A*: Откуда пришли в узел { position: parent_position }
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        # A*: Стоимость пути от start { position: g_cost }
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        # f_score не храним отдельно, он есть в heap

        while open_set_heap:
            current_f_cost, current_g_cost, current_pos = heapq.heappop(open_set_heap)

            if current_pos == goal:
                return self.reconstruct_path(came_from, goal) # Путь найден

            for neighbor_pos in self.get_neighbors(current_pos):
                tentative_g_cost = current_g_cost + 1

                # Проверка на столкновение с телом змейки с учетом движения хвоста
                is_collision = False
                if neighbor_pos in snake_body_indices:
                    segment_index = snake_body_indices[neighbor_pos]
                    # Столкновение происходит, если мы достигаем клетки РАНЬШЕ,
                    # чем этот сегмент хвоста исчезнет.
                    # Сегмент `idx` исчезнет на шаге `snake_length - idx`.
                    if tentative_g_cost < snake_length - segment_index:
                        is_collision = True

                # Если клетка свободна ИЛИ мы достигнем ее после ухода хвоста:
                if not is_collision:
                    # Проверяем, не нашли ли мы БОЛЕЕ КОРОТКИЙ путь до этой клетки
                    if tentative_g_cost < g_score.get(neighbor_pos, float('inf')):
                        # Нашли лучший путь до соседа - обновляем информацию
                        came_from[neighbor_pos] = current_pos
                        g_score[neighbor_pos] = tentative_g_cost
                        f_cost = tentative_g_cost + self._heuristic(neighbor_pos, goal)
                        heapq.heappush(open_set_heap, (f_cost, tentative_g_cost, neighbor_pos))

        return [] # Путь не найден

class Snake:
    def __init__(self, mode='manual'):
        self.length = 1
        initial_pos = ((GRID_WIDTH) // 2, (GRID_HEIGHT) // 2)
        self.positions: Deque[Tuple[int, int]] = deque([initial_pos]) # Используем deque для эффективности
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = COLOR_SNAKE
        self.mode = mode
        self.next_direction = self.direction
        self.path = []
        self.path_find = PathFind()
        self.speed = 10
        # Храним последние 101 состояние (позиции змейки как список, позиция еды) для реплея
        self.history: deque[Tuple[List[Tuple[int, int]], Optional[Tuple[int, int]]]] = deque(maxlen=101)
        self.current_food_pos = None # Храним текущую позицию еды (нужно для истории и проверки роста)

    def draw(self, surface):
        num_segments = len(self.positions)
        if num_segments == 0:
            return

        positions_list = list(self.positions)
        positions_set = set(positions_list)

        # --- Первый проход: Рисуем сплошные сегменты --- 
        # Голова
        draw_object(surface, COLOR_SNAKE_HEAD, positions_list[0])

        # Тело и хвост (только цвет, без линий)
        if num_segments > 1:
            head_color = COLOR_SNAKE_HEAD_GRADIENT
            body_color = COLOR_SNAKE
            tail_color = COLOR_SNAKE_TAIL

            for i in range(1, num_segments):
                current_pos = positions_list[i]
                # Рассчитываем цвет
                progress = (i - 1) / (num_segments - 1) if num_segments > 1 else 0
                segment_color: pygame.Color = pygame.Color(0, 0, 0)
                if progress < 0.5:
                    local_progress = progress / 0.5
                    segment_color = head_color.lerp(body_color, local_progress)
                else:
                    local_progress = (progress - 0.5) / 0.5
                    segment_color = body_color.lerp(tail_color, local_progress)
                # Рисуем сегмент
                draw_object(surface, segment_color, current_pos)
        
        # --- Второй проход: Рисуем ВНУТРЕННИЕ границы --- 
        if num_segments > 1:
            internal_border_color = COLOR_GRID # Цвет для внутренних линий
            line_width = 1
            for i in range(num_segments): # Итерируем по ВСЕМ сегментам
                current_pos = positions_list[i]
                x, y = current_pos
                x_px, y_px = x * GRIDSIZE, y * GRIDSIZE

                # Определяем фактических соседей по цепочке
                prev_actual_pos = positions_list[i-1] if i > 0 else None
                next_actual_pos = positions_list[i+1] if i < num_segments - 1 else None

                # Проверяем соседа СПРАВА
                neighbor_right = ((x + 1) % GRID_WIDTH, y)
                if (neighbor_right in positions_set and 
                    neighbor_right != prev_actual_pos and 
                    neighbor_right != next_actual_pos):
                    pygame.draw.line(surface, internal_border_color, 
                                     (x_px + GRIDSIZE - line_width, y_px), 
                                     (x_px + GRIDSIZE - line_width, y_px + GRIDSIZE -1), 
                                     line_width)

                # Проверяем соседа СНИЗУ
                neighbor_down = (x, (y + 1) % GRID_HEIGHT)
                if (neighbor_down in positions_set and
                    neighbor_down != prev_actual_pos and
                    neighbor_down != next_actual_pos):
                    pygame.draw.line(surface, internal_border_color, 
                                     (x_px, y_px + GRIDSIZE - line_width), 
                                     (x_px + GRIDSIZE - 1, y_px + GRIDSIZE - line_width), 
                                     line_width)

    def get_head_position(self):
        return self.positions[0]

    def turn(self,point):
        # Запрещаем разворот на 180 градусов
        if (point[0]*-1, point[1]*-1)==self.direction:
            return
        head_x, head_y = self.positions[0]
        new_head = ((head_x + point[0]) % GRID_WIDTH, (head_y + point[1]) % GRID_HEIGHT)
        # Оператор 'in' для deque достаточно быстр для типичных длин змейки
        if new_head not in self.positions:
             self.next_direction = point

    def move(self, food_pos):
        """Основная функция движения: выбирает направление (если авто) и делает ход."""
        self.current_food_pos = food_pos # Запоминаем позицию еды для истории и проверки роста
        self.direction = self.next_direction # Применяем выбранное/заданное направление
        collision = False
        if self.mode == 'auto':
            collision = self.auto_move(food_pos)
        else:
            collision = self.manual_move()

        # Записываем состояние в историю ПОСЛЕ хода, но ДО проверки коллизии на след. шаге
        # Это позволяет увидеть и последний (фатальный) ход в реплее.
        if self.positions:
             self.history.append((list(self.positions), self.current_food_pos)) # Храним копию списка

        return collision

    def manual_move(self):
        """Движение вперед в ручном режиме на основе self.direction."""
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        return self.move_forward(new)

    def auto_move(self, food_pos):
        """Выбор направления и движение вперед в авто-режиме."""
        head = self.get_head_position()
        # Ищем путь к еде
        path_to_food = self.path_find.find_path(head, food_pos, list(self.positions))

        # Если путь к еде найден и он "безопасен" (оставляет путь к хвосту после еды)
        if path_to_food and self.is_path_safe_to_food(path_to_food):
            self.path = path_to_food # Сохраняем для отрисовки
            if len(path_to_food) > 1:
                next_move_pos = path_to_food[1] # Берем следующую клетку из пути
                self.next_direction = self.get_direction_to(next_move_pos)
            else:
                # Еда прямо перед нами (path_to_food == [head]). Не меняем направление.
                self.next_direction = self.direction
        else:
            # Путь к еде не найден или небезопасен -> переходим в режим выживания
            self.path = [] # Сбрасываем путь для отрисовки
            survival_direction = self.find_survival_move() # Ищем ход, максимизирующий "свободу"
            if survival_direction:
                self.next_direction = survival_direction
            else:
                # Если даже выжить не получается, ищем любой безопасный немедленный ход
                safe_immediate_direction = self.find_immediate_safe_direction()
                if safe_immediate_direction:
                    self.next_direction = safe_immediate_direction
                else:
                    # Тупик, оставляем текущее направление (скорее всего, врежемся)
                    self.next_direction = self.direction

        # Применяем выбранное (AI) направление и делаем ход
        self.direction = self.next_direction
        cur = self.get_head_position()
        x, y = self.direction
        new_head_pos = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        return self.move_forward(new_head_pos)

    def move_forward(self, new_head_pos):
        """Обновляет позицию змейки: добавляет голову, удаляет хвост (если не растет), проверяет коллизии."""
        collision = False
        # Проверяем коллизию с телом ДО добавления новой головы.
        # Столкновение с последним сегментом (хвостом) не считается, т.к. он сдвинется.
        if len(self.positions) > 1:
            # Используем islice для проверки по всем сегментам, КРОМЕ последнего (хвоста)
            if new_head_pos in itertools.islice(self.positions, 0, len(self.positions) - 1):
                     collision = True

        self.positions.appendleft(new_head_pos) # Добавляем новую голову

        # Проверяем, съела ли змейка еду на этом шаге (сравниваем новую голову с позицией еды)
        grows = (new_head_pos == self.current_food_pos)

        # Удаляем хвост, если змейка не съела еду на этом шаге
        if not grows and len(self.positions) > self.length:
            self.positions.pop() # Удаляем последний элемент (хвост)
        elif grows:
             # Если съели еду, увеличиваем целевую длину. Хвост не удаляется в этот раз.
             self.length += 1

        # Возвращаем True, если произошло столкновение (проверено до добавления головы)
        return collision

    def get_direction_to(self, position):
        """Определяет направление (UP/DOWN/LEFT/RIGHT) от головы змейки к цели, учитывая 'зацикленность' поля."""
        head_x, head_y = self.get_head_position()
        pos_x, pos_y = position

        dx = pos_x - head_x
        # Коррекция разницы по X для 'зацикленности'
        if abs(dx) > GRID_WIDTH / 2:
            sign = 1 if dx > 0 else -1
            dx = - (GRID_WIDTH - abs(dx)) * sign

        dy = pos_y - head_y
        # Коррекция разницы по Y для 'зацикленности'
        if abs(dy) > GRID_HEIGHT / 2:
            sign = 1 if dy > 0 else -1
            dy = - (GRID_HEIGHT - abs(dy)) * sign

        # Определяем основное направление по большей разнице
        if abs(dx) > abs(dy):
            return RIGHT if dx > 0 else LEFT
        elif abs(dy) > abs(dx):
            return DOWN if dy > 0 else UP
        else: # Случай dx == dy (включая 0,0 - цель на голове)
            # Приоритет горизонтальному движению, если возможно
            if dx != 0:
                 return RIGHT if dx > 0 else LEFT
            # Иначе вертикальному, если возможно
            elif dy != 0:
                 return DOWN if dy > 0 else UP
            # Если цель на голове (dx=0, dy=0), возвращаем текущее направление
            else:
                 return self.direction

    def find_immediate_safe_direction(self):
        """Находит любое направление, которое не ведет к немедленной смерти (столкновению с телом)."""
        head = self.get_head_position()
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        random.shuffle(possible_directions) # Пробуем в случайном порядке

        for d in possible_directions:
            next_pos = ((head[0] + d[0]) % GRID_WIDTH, (head[1] + d[1]) % GRID_HEIGHT)
            # Проверяем столкновение со ВСЕМ телом
            if next_pos not in self.positions:
                return d

        # Если не нашли пустую клетку, проверяем, можно ли пойти на место хвоста
        # (это безопасно, т.к. хвост сдвинется на этом же шаге)
        if len(self.positions) > 1:
            tail_pos = self.positions[-1]
            for d in possible_directions:
                next_pos = ((head[0] + d[0]) % GRID_WIDTH, (head[1] + d[1]) % GRID_HEIGHT)
                if next_pos == tail_pos:
                    return d

        # Безопасных ходов нет
        return None

    def find_survival_move(self) -> Tuple[int, int] | None:
        """
        Находит лучший ход для выживания: выбирает направление, которое после хода
        оставляет максимально длинный путь до собственного хвоста.
        Это эвристика, помогающая избегать самозапирания.
        Возвращает направление или None, если безопасных ходов нет.
        """
        best_direction = None
        max_freedom = -1 # Длина пути до хвоста (-1 означает отсутствие пути)

        head = self.get_head_position()
        # Рассматриваем только ходы вперед и вбок (не разворот)
        possible_directions = [d for d in [UP, DOWN, LEFT, RIGHT] if d != (self.direction[0] * -1, self.direction[1] * -1)]

        current_positions_list = list(self.positions)

        for direction in possible_directions:
            next_head = ((head[0] + direction[0]) % GRID_WIDTH, (head[1] + direction[1]) % GRID_HEIGHT)

            # 1. Проверяем, не ведет ли ход сразу в тело (кроме хвоста)
            if len(self.positions) > 1 and next_head in itertools.islice(self.positions, 0, len(self.positions) - 1):
                 continue # Немедленное столкновение - пропускаем направление

            # 2. Симулируем этот один шаг (змейка НЕ растет)
            sim_snake_list = self.simulate_move([head, next_head], grows=False, initial_state=current_positions_list)
            if sim_snake_list is None: # Симуляция не удалась (хотя на 1 шаг не должна)
                continue

            # 3. Ищем путь от новой головы к новому хвосту в симулированном состоянии
            sim_head = sim_snake_list[0]
            sim_tail = sim_snake_list[-1]
            path_to_tail = self.path_find.find_path(sim_head, sim_tail, sim_snake_list)

            freedom = len(path_to_tail) # Длина пути = "свобода"

            # Обновляем лучший ход, если текущий дает больше свободы
            if freedom > max_freedom:
                max_freedom = freedom
                best_direction = direction

        return best_direction

    def is_path_safe_to_food(self, path_to_food: List[Tuple[int, int]]) -> bool:
        """
        Проверяет, является ли путь к еде "безопасным":
        оставляет ли он возможность добраться до хвоста ПОСЛЕ поедания еды.
        Это помогает избегать ситуаций, когда змейка съедает еду и запирает сама себя.
        """
        if not path_to_food or len(path_to_food) <= 1:
            return False

        current_positions_list = list(self.positions)

        # 1. Симулируем движение к еде и ее поедание (grows=True)
        sim_snake_after_eat = self.simulate_move(path_to_food, grows=True, initial_state=current_positions_list)

        if sim_snake_after_eat is None:
            return False # Сам путь к еде привел к самопересечению в симуляции

        # 2. Проверяем, есть ли путь от новой головы (где была еда) до нового хвоста
        sim_head = sim_snake_after_eat[0]
        sim_tail = sim_snake_after_eat[-1]
        path_to_tail_after_eat = self.path_find.find_path(sim_head, sim_tail, sim_snake_after_eat)

        # Если путь до хвоста существует, считаем путь к еде безопасным
        return bool(path_to_tail_after_eat)

    def simulate_move(self, path: List[Tuple[int, int]], grows: bool, initial_state: List[Tuple[int, int]] | None = None) -> List[Tuple[int, int]] | None:
        """
        Симулирует движение змейки по заданному пути.
        Возвращает новое состояние змейки (список координат) или None, если путь ведет к самопересечению.
        `grows`: True, если последний шаг пути - это поедание еды (хвост не удаляется).
        `initial_state`: Опциональное начальное состояние (список) для симуляции.
        """
        if not path or len(path) <= 1:
            # Если путь пуст или состоит только из текущей головы, возвращаем исходное состояние
            return list(self.positions) if initial_state is None else initial_state

        sim_snake = deque(initial_state if initial_state is not None else self.positions)
        current_path = path[1:] # Путь для симуляции (без текущей головы)

        for i, step in enumerate(current_path):
            # Проверка на самопересечение в симуляции: нельзя врезаться в сегмент,
            # который НЕ станет хвостом на следующем шаге симуляции.
            if len(sim_snake) > 1 and step in itertools.islice(sim_snake, 0, len(sim_snake) - 1):
                 return None # Самопересечение

            sim_snake.appendleft(step) # Делаем шаг вперед

            # Определяем, нужно ли удалять хвост на этом шаге симуляции
            is_last_step = (i == len(current_path) - 1)
            # Удаляем хвост, если это не последний шаг ИЛИ если это последний шаг, но змейка не растет
            if not (is_last_step and grows):
                sim_snake.pop()

        return list(sim_snake) # Возвращаем результат симуляции как список

    def reset(self):
        self.length = 1
        initial_pos = ((GRID_WIDTH) // 2, (GRID_HEIGHT) // 2)
        self.positions = deque([initial_pos])
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = self.direction
        self.path = []
        self.speed = 10 # Сброс скорости к значению по умолчанию
        self.history.clear() # Очищаем историю ходов
        self.current_food_pos = None

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = COLOR_FOOD
        self.randomize_position([]) # Первоначальная рандомизация без змейки

    def randomize_position(self, snake_positions: List[Tuple[int, int]] | Deque[Tuple[int, int]]):
        # Генерируем позицию, пока она не окажется вне тела змейки
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions:
                break

    def draw(self, surface):
        draw_object(surface, self.color, self.position)

class StatsCache(TypedDict):
    score: Optional[int]
    high_score: Optional[int]
    snake_length: Optional[int]
    current_speed: Optional[int] # или float, если скорость может быть дробной
    score_surf: Optional[Surface]
    high_score_surf: Optional[Surface]
    area_surf: Optional[Surface]
    speed_surf: Optional[Surface]
    font: Optional[Font]

# Кэш для отрисовки статистики
stats_cache: StatsCache = {
    "score": None, "high_score": None, "snake_length": None, "current_speed": None,
    "score_surf": None, "high_score_surf": None, "area_surf": None, "speed_surf": None,
    "font": None
}

def display_statistics(surface, score, snake_length, high_score, current_speed):
    global stats_cache

    # Инициализируем или берем шрифт из кэша
    if stats_cache["font"] is None:
        try:
            stats_cache["font"] = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        except:
            stats_cache["font"] = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
    font = stats_cache["font"]

    # --- Отрисовка текста вверху слева (Score, High Score) ---
    y_offset = 10
    # Score (рендерим только если значение изменилось)
    if score != stats_cache["score"] or stats_cache["score_surf"] is None:
        stats_cache["score"] = score
        stats_cache["score_surf"] = font.render(f'Score: {score}', True, COLOR_TEXT_WHITE)
    text_surf = stats_cache["score_surf"]
    text_rect = text_surf.get_rect(topleft=(15, y_offset))
    surface.blit(text_surf, text_rect)
    y_offset += font.get_height() + 2

    # High Score (рендерим только если значение изменилось)
    if high_score != stats_cache["high_score"] or stats_cache["high_score_surf"] is None:
        stats_cache["high_score"] = high_score
        stats_cache["high_score_surf"] = font.render(f'High Score: {high_score}', True, COLOR_TEXT_WHITE)
    text_surf = stats_cache["high_score_surf"]
    text_rect = text_surf.get_rect(topleft=(15, y_offset))
    surface.blit(text_surf, text_rect)

    # --- Отрисовка текста внизу слева (Area, Speed) ---
    y_offset = SCREEN_HEIGHT - 10
    texts_to_render = []

    # Area % (рендерим только если значение изменилось)
    if snake_length != stats_cache["snake_length"] or stats_cache["area_surf"] is None:
        stats_cache["snake_length"] = snake_length
        area_percentage = (snake_length / (GRID_WIDTH * GRID_HEIGHT)) * 100
        stats_cache["area_surf"] = font.render(f'Area: {area_percentage:.1f}%', True, COLOR_TEXT_WHITE)
    texts_to_render.append(stats_cache["area_surf"])

    # Speed (рендерим только если значение изменилось)
    rounded_speed = int(current_speed) # Используем целое значение для кэширования/отображения
    if rounded_speed != stats_cache["current_speed"] or stats_cache["speed_surf"] is None:
        stats_cache["current_speed"] = rounded_speed
        stats_cache["speed_surf"] = font.render(f'Speed: {rounded_speed}', True, COLOR_TEXT_WHITE)
    texts_to_render.append(stats_cache["speed_surf"])

    # Рисуем нижние тексты снизу вверх
    for text_surf in reversed(texts_to_render):
        y_offset -= font.get_height()
        text_rect = text_surf.get_rect(bottomleft=(15, y_offset + font.get_height()))
        surface.blit(text_surf, text_rect)
        y_offset -= 2 # Пробел между строками

def button_animation(surface, button, color, text):
    # Простая анимация нажатия: затемнение фона и кнопки
    button_rect = pygame.Rect(button)
    start_time = pygame.time.get_ticks()
    duration = 200 # мс

    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        progress = elapsed / duration

        # Затемняем фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(int(150 * progress))
        overlay.fill(COLOR_BACKGROUND)
        surface.blit(overlay, (0,0))

        # Рисуем кнопку чуть темнее
        current_button_color = color.lerp(COLOR_BACKGROUND, 0.3)
        draw_button(surface, button_rect, current_button_color, text, False, True)

        pygame.display.update(button_rect) # Обновляем только область кнопки для производительности
        pygame.time.Clock().tick(60)

def replay_screen(surface, history: deque, final_score: int, high_score: int):
    """Экран перемотки последних ходов после Game Over."""
    if not history:
        return False # Нет истории для показа, возвращаем False (не перезапускать)

    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE, bold=True)
        font_info = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2, bold=True)
        font_info = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    # Кэшируем текстовые поверхности для статистики
    final_score_surf = font_info.render(f'Final Score: {final_score}', True, COLOR_TEXT)
    high_score_surf = font_info.render(f'High Score: {high_score}', True, COLOR_TEXT)

    title_surf = font_title.render("Game Replay", True, COLOR_TEXT_HIGHLIGHT)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))

    history_len = len(history)
    max_replay_index = history_len - 1
    replay_index = max_replay_index # Начинаем просмотр с последнего хода

    # --- Определяем параметры кнопок и слайдера --- 
    button_width = 180
    button_height = 50
    slider_height = 20
    slider_y = SCREEN_HEIGHT - 100 # Поднимаем слайдер чуть выше
    button_y = slider_y + slider_height + 40 # Увеличиваем отступ до 40

    # --- Рассчитываем геометрию --- 
    # Центры кнопок
    retry_button_center_x = SCREEN_WIDTH // 3
    quit_button_center_x = SCREEN_WIDTH * 2 // 3
    # Позиция и ширина слайдера (теперь button_width определена)
    slider_x = retry_button_center_x - button_width // 2
    slider_width = quit_button_center_x + button_width // 2 - slider_x

    # --- Создаем виджеты --- 
    # Слайдер
    replay_slider = Slider(slider_x, slider_y, slider_width, slider_height,
                           0, max_replay_index, replay_index, f"Step: {replay_index+1}/{history_len}")
    # Кнопки
    retry_button_rect = pygame.Rect(0, 0, button_width, button_height)
    quit_button_rect = pygame.Rect(0, 0, button_width, button_height)
    retry_button_rect.center = (retry_button_center_x, button_y)
    quit_button_rect.center = (quit_button_center_x, button_y)

    # Вспомогательные объекты для отрисовки состояния из истории
    replay_snake = Snake()
    replay_food = Food()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        is_retry_hovered = retry_button_rect.collidepoint(mouse_pos)
        is_quit_hovered = quit_button_rect.collidepoint(mouse_pos)
        is_retry_clicked = False
        is_quit_clicked = False

        prev_replay_index = replay_index # Запоминаем индекс до обработки событий

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Передаем события слайдеру для обработки перетаскивания
            replay_slider.handle_event(event)

            # Управление перемоткой с клавиатуры
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    replay_index = max(0, replay_index - 1)
                elif event.key == pygame.K_RIGHT:
                    replay_index = min(max_replay_index, replay_index + 1)
                elif event.key == pygame.K_HOME:
                     replay_index = 0
                elif event.key == pygame.K_END:
                     replay_index = max_replay_index
                # Обновляем позицию слайдера при использовании клавиш
                replay_slider.value = replay_index
                replay_slider.update_handle_pos()

            # Обработка кликов по кнопкам
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_retry_hovered:
                    is_retry_clicked = True
                    if eat_sound: eat_sound.play()
                    return True # Сигнал для рестарта игры
                elif is_quit_hovered:
                    is_quit_clicked = True
                    if eat_sound:
                        eat_sound.play()
                    pygame.quit()
                    sys.exit()

        # Обновляем индекс из слайдера, если он изменился
        slider_index = int(replay_slider.value)
        if slider_index != replay_index:
            replay_index = slider_index

        # Обновляем текст слайдера, если индекс изменился (клавишами или мышью)
        if replay_index != prev_replay_index:
             replay_slider.label = f"Step: {replay_index+1}/{history_len}"

        # Получаем состояние (позиции змейки и еды) для текущего индекса перемотки
        current_snake_positions_list, current_food_pos = history[replay_index]
        replay_snake.positions = deque(current_snake_positions_list) # Используем deque для согласованности с Snake.draw
        replay_food.position = current_food_pos if current_food_pos else (-1, -1) # Скрываем еду, если ее не было в этом состоянии

        # --- Отрисовка экрана реплея ---
        surface.fill(COLOR_BACKGROUND)
        draw_grid(surface)
        surface.blit(title_surf, title_rect)

        # Отрисовка змейки и еды из выбранного шага истории
        replay_snake.draw(surface)
        if replay_food.position != (-1, -1):
             replay_food.draw(surface)

        # Отрисовка UI (слайдер, кнопки)
        replay_slider.draw(surface)
        draw_button(surface, retry_button_rect, COLOR_BUTTON, "Retry Game", is_retry_hovered, is_retry_clicked)
        draw_button(surface, quit_button_rect, COLOR_BUTTON, "Quit", is_quit_hovered, is_quit_clicked)

        # Отрисовка финальной статистики
        y_offset = title_rect.bottom + 15
        info_rect = final_score_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=y_offset)
        surface.blit(final_score_surf, info_rect)
        y_offset += font_info.get_height() + 5

        info_rect = high_score_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=y_offset)
        surface.blit(high_score_surf, info_rect)

        pygame.display.update()
        clock.tick(60) # Поддерживаем стандартную частоту кадров для плавности UI

def game_over_screen(surface, score, snake_length, high_score, current_speed, history: deque):
    """Экран Game Over теперь просто вызывает replay_screen."""
    # Передаем управление экрану перемотки.
    # Он вернет True, если пользователь нажал "Retry", иначе False или выход.
    return replay_screen(surface, history, score, high_score)

def settings_screen(surface, current_speed, current_volume, mute) -> Tuple[int, int, bool]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    title_surf = font_title.render("Settings", True, COLOR_TEXT_WHITE)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 220))

    # Виджеты настроек
    slider_width = 350
    slider_height = 25
    speed_slider = Slider(SCREEN_WIDTH // 2 - slider_width // 2, SCREEN_HEIGHT // 2 - 140,
                          slider_width, slider_height, 1, 500, current_speed, "Game Speed")
    volume_slider = Slider(SCREEN_WIDTH // 2 - slider_width // 2, SCREEN_HEIGHT // 2 - 60,
                           slider_width, slider_height, 0, 100, current_volume, "Sound Volume")
    checkbox_size = 25
    mute_checkbox = Checkbox(SCREEN_WIDTH // 2 - slider_width // 2, SCREEN_HEIGHT // 2 + 20,
                             checkbox_size, "Mute Sound", mute)
    button_width = 220
    button_height = 55
    back_button_rect = pygame.Rect(0, 0, button_width, button_height)
    back_button_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        is_back_hovered = back_button_rect.collidepoint(mouse_pos)
        is_back_clicked = False # Сброс состояния клика в начале кадра

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Сначала передаем события виджетам (слайдеры, чекбокс)
            speed_slider.handle_event(event)
            volume_slider.handle_event(event)
            mute_checkbox.handle_event(event)

            # Затем проверяем клик по кнопке "Back"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_back_hovered:
                    is_back_clicked = True
                    if eat_sound:
                        eat_sound.play()
                    running = False # Выходим из цикла настроек
            # MOUSEBUTTONUP не обрабатываем для кнопки, т.к. действие происходит по нажатию

        # Получаем текущие значения из виджетов
        selected_speed = speed_slider.value
        selected_volume = volume_slider.value
        is_muted = mute_checkbox.checked

        # Применяем громкость немедленно
        if eat_sound:
            eat_sound.set_volume(0 if is_muted else selected_volume / 100)

        # Отрисовка
        surface.fill(COLOR_BACKGROUND)
        surface.blit(title_surf, title_rect)
        speed_slider.draw(surface)
        volume_slider.draw(surface)
        mute_checkbox.draw(surface)
        draw_button(surface, back_button_rect, COLOR_BUTTON, "Back", is_back_hovered, is_back_clicked)

        pygame.display.update()
        clock.tick(60)

    # Возвращаем выбранные значения ПОСЛЕ выхода из цикла
    return selected_speed, selected_volume, is_muted

def start_screen(surface) -> Tuple[str, int, int, bool]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    title_surf = font_title.render("Modern Snake", True, COLOR_TEXT_WHITE)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    # Параметры кнопок
    button_width = 250
    button_height = 55
    button_y_start = title_rect.bottom + 60
    button_spacing = 30

    # Создаем Rect для каждой кнопки
    manual_button_rect = pygame.Rect(0, 0, button_width, button_height)
    auto_button_rect = pygame.Rect(0, 0, button_width, button_height)
    settings_button_rect = pygame.Rect(0, 0, button_width, button_height)
    quit_button_rect = pygame.Rect(0, 0, button_width, button_height)

    # Центрируем кнопки
    manual_button_rect.center = (SCREEN_WIDTH // 2, button_y_start)
    auto_button_rect.center = (SCREEN_WIDTH // 2, manual_button_rect.bottom + button_spacing)
    settings_button_rect.center = (SCREEN_WIDTH // 2, auto_button_rect.bottom + button_spacing)
    quit_button_rect.center = (SCREEN_WIDTH // 2, settings_button_rect.bottom + button_spacing)

    # Словарь для удобного управления кнопками
    buttons = {
        "manual": {"rect": manual_button_rect, "text": "Manual Play", "color": COLOR_BUTTON},
        "auto": {"rect": auto_button_rect, "text": "Auto Play (AI)", "color": COLOR_BUTTON},
        "settings": {"rect": settings_button_rect, "text": "Settings", "color": COLOR_TEXT_HIGHLIGHT}, # Выделяем настройки
        "quit": {"rect": quit_button_rect, "text": "Quit Game", "color": COLOR_BUTTON}
    }

    # Начальные значения настроек (будут изменены, если зайти в Settings)
    current_speed = 15
    current_volume = 1 # Громкость по умолчанию (0-100)
    mute = False
    waiting = True

    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        # Определяем состояния hover и click для всех кнопок динамически
        hover_states = {key: data["rect"].collidepoint(mouse_pos) for key, data in buttons.items()}
        click_states = {key: False for key in buttons} # Сбрасываем состояние клика каждый кадр

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, data in buttons.items():
                    if hover_states[key]: # Если кликнули по кнопке, над которой курсор
                        click_states[key] = True # Устанавливаем флаг клика для отрисовки
                        if eat_sound and not mute:
                            eat_sound.play()

                        # Выполняем действие в зависимости от нажатой кнопки
                        if key == 'manual':
                            return 'manual', int(current_speed), int(current_volume), mute
                        elif key == 'auto':
                            return 'auto', int(current_speed), int(current_volume), mute
                        elif key == 'settings':
                            # Открываем экран настроек и получаем обновленные значения
                            current_speed, current_volume, mute = settings_screen(surface, current_speed, current_volume, mute)
                            # Применяем новую громкость сразу после возврата из настроек
                            if eat_sound:
                                eat_sound.set_volume(0 if mute else current_volume / 100)
                        elif key == 'quit':
                            pygame.quit()
                            sys.exit()
                        break # Выходим из цикла по кнопкам, т.к. клик обработан

        # Отрисовка стартового экрана
        surface.fill(COLOR_BACKGROUND)
        surface.blit(title_surf, title_rect)

        for key, data in buttons.items():
            # Передаем состояния hover и click в функцию отрисовки кнопки
            draw_button(surface, data['rect'], data['color'], data['text'], hover_states[key], click_states[key])

        pygame.display.update()
        clock.tick(60)

def pause_screen(surface):
    # Затемненный оверлей
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(COLOR_BACKGROUND)
    surface.blit(overlay, (0, 0))

    try:
        font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    pause_text = font.render("Paused", True, COLOR_TEXT_WHITE)
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(pause_text, pause_rect)

    # Подсказка для возобновления
    try:
        font_hint = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_hint = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
    hint_text = font_hint.render("Press 'P' to resume", True, COLOR_TEXT)
    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, pause_rect.bottom + 40))
    surface.blit(hint_text, hint_rect)

    pygame.display.update()

    # Цикл ожидания снятия паузы
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False # Выход из цикла паузы
        pygame.time.Clock().tick(15) # Снижаем нагрузку на CPU во время паузы

def get_direction_vector(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> Tuple[int, int]:
    """Вычисляет вектор (dx, dy) от pos1 к pos2, учитывая зацикленность поля."""
    x1, y1 = pos1
    x2, y2 = pos2
    dx = x2 - x1
    dy = y2 - y1

    # Коррекция перехода через край по X
    if abs(dx) > GRID_WIDTH / 2:
        sign = 1 if dx > 0 else -1
        dx = - (GRID_WIDTH - abs(dx)) * sign
    # Коррекция перехода через край по Y
    if abs(dy) > GRID_HEIGHT / 2:
        sign = 1 if dy > 0 else -1
        dy = - (GRID_HEIGHT - abs(dy)) * sign

    # Нормализуем вектор до единичной длины (если он не нулевой)
    if dx != 0: dx //= abs(dx)
    if dy != 0: dy //= abs(dy)

    return dx, dy

def main():
    pygame.display.set_caption('Modern Snake Game')
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Шрифты для UI в главном цикле
    try:
        font_icon = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        font_panel = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_SMALL)
    except:
        font_icon = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
        font_panel = pygame.font.SysFont('arial', FONT_SIZE_SMALL - 2)

    # Получаем режим игры и начальные настройки со стартового экрана
    mode, initial_current_speed, current_volume, mute = start_screen(screen)
    # Применяем начальную громкость
    if eat_sound:
        eat_sound.set_volume(0 if mute else current_volume / 100)

    # Инициализация игровых объектов
    snake = Snake(mode)
    snake.speed = initial_current_speed # Устанавливаем скорость, выбранную/сохраненную в меню
    food = Food()
    food.randomize_position(snake_positions=snake.positions)
    score = 0
    high_score = 0 # TODO: Загружать/сохранять high score?

    # --- Переменные для UI панели скорости ---
    speed_panel_visible = False
    panel_width = 160
    panel_height = 70
    panel_margin_top = 5
    panel_margin_right = 5
    speed_panel_rect = pygame.Rect(SCREEN_WIDTH - panel_width - panel_margin_right, panel_margin_top, panel_width, panel_height)

    # Слайдер внутри панели скорости
    slider_margin_h = 15
    slider_margin_top = 35
    slider_height = 15
    game_speed_slider = Slider(speed_panel_rect.x + slider_margin_h,
                               speed_panel_rect.y + slider_margin_top,
                               speed_panel_rect.width - 2 * slider_margin_h,
                               slider_height,
                               1, 500, snake.speed, "") # Label не нужен у этого слайдера

    # Иконка для открытия/закрытия панели скорости
    icon_text = "SPD"
    icon_surf = font_icon.render(icon_text, True, COLOR_TEXT_HIGHLIGHT)
    icon_padding = 8
    speed_icon_rect = icon_surf.get_rect(topright=(SCREEN_WIDTH - icon_padding, icon_padding))
    speed_icon_bg_rect = speed_icon_rect.inflate(icon_padding, icon_padding) # Область клика для иконки

    game_controls_active = True # Флаг: активно ли управление игрой (змейкой)
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Обновляем значение слайдера на панели (если она видима), чтобы соответствовать snake.speed
        if speed_panel_visible:
             game_speed_slider.value = snake.speed
             game_speed_slider.update_handle_pos()

        # --- Обработка событий ---
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- Управление панелью скорости ---
            panel_interaction = False # Флаг: было ли взаимодействие с панелью в этом событии
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Клик по иконке скорости (открыть/закрыть панель)
                if speed_icon_bg_rect.collidepoint(event.pos):
                    speed_panel_visible = not speed_panel_visible
                    game_controls_active = not speed_panel_visible # Деактивируем управление игрой, если панель открыта
                    panel_interaction = True
                # Клик внутри видимой панели (взаимодействие со слайдером)
                elif speed_panel_visible and speed_panel_rect.collidepoint(event.pos):
                     game_speed_slider.handle_event(event) # Слайдер сам разберется, кликнули по ручке или треку
                     snake.speed = int(game_speed_slider.value) # Обновляем скорость змейки сразу
                     panel_interaction = True
                # Клик вне видимой панели (закрываем панель)
                elif speed_panel_visible and not speed_panel_rect.collidepoint(event.pos):
                     speed_panel_visible = False
                     game_controls_active = True # Активируем управление

            # Передача событий MOUSEMOTION / MOUSEBUTTONUP слайдеру, если панель видима
            elif event.type in [pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                if speed_panel_visible:
                     # Передаем событие всегда, если панель видима, handle_event проверит dragging
                     game_speed_slider.handle_event(event)
                     snake.speed = int(game_speed_slider.value) # Обновляем скорость змейки при движении слайдера
                     panel_interaction = True # Считаем взаимодействием

            # --- Управление игрой (только если активно и не было взаимодействия с панелью) ---
            elif event.type == pygame.KEYDOWN:
                if game_controls_active:
                     # Пауза
                     if event.key == pygame.K_p:
                         pause_screen(screen)
                         # game_controls_active остается True после паузы

                     # Ручное управление
                     if snake.mode == 'manual':
                         if event.key == pygame.K_UP: snake.turn(UP)
                         elif event.key == pygame.K_DOWN: snake.turn(DOWN)
                         elif event.key == pygame.K_LEFT: snake.turn(LEFT)
                         elif event.key == pygame.K_RIGHT: snake.turn(RIGHT)

                     # Управление скоростью +/- (для отладки/настройки)
                     if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                         snake.speed = min(500, snake.speed + 5)
                         # game_speed_slider.value = snake.speed # Обновится в начале след. кадра
                     elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                         snake.speed = max(1, snake.speed - 5)
                         # game_speed_slider.value = snake.speed

        # --- Логика игры ---
        # Движение змейки происходит всегда, независимо от активности контролов
        # (AI должен двигаться, даже если панель открыта)
        collision = snake.move(food.position)

        # --- Обработка коллизии ---
        if collision:
            final_history = deque(snake.history) # Копируем историю перед сбросом
            if score > high_score:
                high_score = score

            # Воспроизводим звук поражения, если он есть и звук не выключен
            if melody_sound and not mute:
                melody_sound.play()

            # Вызываем экран Game Over / Replay
            should_restart = game_over_screen(screen, score, snake.length, high_score, int(snake.speed), final_history)

            if should_restart:
                # Сброс игры для рестарта
                snake.reset()
                snake.speed = initial_current_speed # Возвращаем скорость из настроек меню
                food.randomize_position(snake_positions=snake.positions)
                score = 0
                speed_panel_visible = False # Скрываем панель
                game_controls_active = True # Активируем управление
            else:
                # Пользователь выбрал Quit в replay_screen
                running = False # Завершаем главный цикл

        # --- Обработка поедания еды ---
        elif snake.get_head_position() == food.position:
            # Логика роста змейки и обновления длины находится внутри snake.move_forward()
            current_food_pos = food.position # Запоминаем позицию съеденной еды (для истории в след. шаге)
            food.randomize_position(snake_positions=snake.positions) # Новая еда
            # Обновляем `current_food_pos` у змейки, если она в авторежиме,
            # чтобы история записалась корректно на следующем шаге snake.move
            if snake.mode == 'auto':
                 snake.current_food_pos = food.position

            if eat_sound and not mute:
                eat_sound.play()
            score += 10 + int(snake.speed // 10) # Бонус за скорость
            if score > high_score:
                high_score = score

        # --- Отрисовка ---
        screen.fill(COLOR_BACKGROUND)
        draw_grid(screen)

        # Отрисовка пути AI, если он есть
        if snake.mode == 'auto' and snake.path:
            draw_path(screen, snake.path)

        snake.draw(screen)
        food.draw(screen)
        display_statistics(screen, score, snake.length, high_score, snake.speed)

        # Отрисовка иконки скорости (всегда видна)
        pygame.draw.rect(screen, COLOR_PANEL_BG, speed_icon_bg_rect, border_radius=4)
        screen.blit(icon_surf, speed_icon_rect)

        # Отрисовка панели скорости, если она видима
        if speed_panel_visible:
            panel_bg_color = COLOR_PANEL_BG[:3] + (180,) # Используем чуть более прозрачный фон
            pygame.draw.rect(screen, panel_bg_color, speed_panel_rect, border_radius=4)
            # Рисуем заголовок панели
            panel_title_surf = font_panel.render("Speed", True, COLOR_TEXT_WHITE)
            panel_title_rect = panel_title_surf.get_rect(centerx=speed_panel_rect.centerx, top=speed_panel_rect.top + 8)
            screen.blit(panel_title_surf, panel_title_rect)
            # Рисуем сам слайдер
            game_speed_slider.draw(screen)

        pygame.display.update()
        clock.tick(snake.speed)

    pygame.quit()

if __name__ == '__main__':
    # Инициализация Pygame и Mixer перед использованием их модулей
    pygame.init()
    pygame.mixer.init()
    # Глобальный или переданный объект Clock для управления FPS
    clock = pygame.time.Clock()
    main()
