#!/usr/bin/env python3
import pygame
import sys
import random
import os
from collections import deque
from typing import List, Tuple, Set, Deque, Dict, Optional, Any, Union, TypedDict
import itertools
import heapq
from pygame import Surface
from pygame.font import Font

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRIDSIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRIDSIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRIDSIZE

# --- Цветовая Палитра (Темная Тема) ---
COLOR_BACKGROUND = pygame.Color("#282c34")
COLOR_GRID = pygame.Color("#4a4f58")
COLOR_SNAKE = pygame.Color("#61afef")
COLOR_SNAKE_HEAD = pygame.Color("#98c379")
COLOR_SNAKE_HEAD_GRADIENT = pygame.Color("#c678dd")
COLOR_SNAKE_TAIL = pygame.Color("#5c6370")
COLOR_FOOD = pygame.Color("#e06c75")
COLOR_PATH_VISUALIZATION = pygame.Color("#d19a66")
COLOR_TEXT = pygame.Color("#abb2bf")
COLOR_TEXT_HIGHLIGHT = pygame.Color("#e5c07b")
COLOR_TEXT_WHITE = pygame.Color("#ffffff")
COLOR_BUTTON = pygame.Color("#61afef")
COLOR_BUTTON_HOVER = pygame.Color("#98c379")
COLOR_BUTTON_CLICK = pygame.Color("#56b6c2")
COLOR_SLIDER_BG = pygame.Color("#4a4f58")
COLOR_SLIDER_HANDLE = pygame.Color("#98c379")
COLOR_PANEL_BG = pygame.Color(40, 44, 52, 210)
COLOR_CHECKBOX_BORDER = pygame.Color("#abb2bf")
COLOR_CHECKBOX_CHECK = pygame.Color("#98c379")
COLOR_GAMEOVER = pygame.Color("#e06c75")

# --- Шрифты ---
FONT_NAME_PRIMARY = 'Consolas, Calibri, Arial'
FONT_SIZE_SMALL = 18
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 36
FONT_SIZE_XLARGE = 72
FONT_SIZE_TINY = 14

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

script_dir = os.path.dirname(__file__)
sound_file_path = os.path.join(script_dir, 'eat.wav')

try:
    eat_sound = pygame.mixer.Sound(sound_file_path)
    eat_sound.set_volume(0.05)
except pygame.error:
    eat_sound = None
    print(f"Warning: Sound file '{sound_file_path}' not found or cannot be loaded.")

melody_sound_path = os.path.join(script_dir, 'melody.wav')
try:
    melody_sound = pygame.mixer.Sound(melody_sound_path)
    melody_sound.set_volume(0.1)
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
        # --- Изменяем эффект наведения: делаем кнопку темнее --- 
        # button_color = COLOR_BUTTON_HOVER
        button_color = base_color.lerp(COLOR_BACKGROUND, 0.2) # Смешиваем с цветом фона
        # --- Конец изменения --- 

    button_rect = pygame.Rect(button)
    pygame.draw.rect(surface, button_color, button_rect, border_radius=8)

    try:
        font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    text_surf = font.render(text, True, COLOR_TEXT_WHITE)
    text_rect = text_surf.get_rect(center=button_rect.center)
    text_rect.centery += 3
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
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, label, power=1.0):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.power = power
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
        """Обновляет позицию ручки на основе текущего значения self.value с учетом self.power."""
        value_range = self.max_val - self.min_val
        if value_range == 0:
             ratio = 0
        else:
             normalized_value = (self.value - self.min_val) / value_range
             normalized_value = max(0.0, min(1.0, normalized_value))
             ratio = normalized_value ** (1.0 / self.power)

        handle_center_x = self.rect.x + int(ratio * self.rect.width)
        self.handle_rect.centerx = max(self.rect.x, min(handle_center_x, self.rect.right))

    def get_handle_bounds_for_collision(self):
        # Увеличиваем область клика для удобства пользователя
        return self.handle_rect.inflate(10, 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_handle_bounds_for_collision().collidepoint(event.pos):
                self.dragging = True
                self.move_handle_to_pos(event.pos[0])
                # --- Захватываем ввод при начале перетаскивания ---
                # pygame.event.set_grab(True) # <<< УБРАНО
                # --- Конец изменения ---
            elif self.rect.collidepoint(event.pos):
                self.dragging = True
                self.move_handle_to_pos(event.pos[0])
                # --- Захватываем ввод при начале перетаскивания ---
                # pygame.event.set_grab(True) # <<< УБРАНО
                # --- Конец изменения ---
        elif event.type == pygame.MOUSEBUTTONUP:
            # Сбрасываем dragging при ЛЮБОМ MOUSEBUTTONUP
            # --- Добавляем проверку, если вдруг мы не тащили ---
            if self.dragging:
                # --- Освобождаем захват ввода при отпускании кнопки ---
                # pygame.event.set_grab(False) # <<< УБРАНО
                # --- Конец изменения ---
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # --- Добавляем проверку реального состояния кнопки мыши ---
                mouse_buttons = pygame.mouse.get_pressed()
                if not mouse_buttons[0]: # Если левая кнопка НЕ нажата
                    self.dragging = False # Принудительно останавливаем перетаскивание
                    # pygame.event.set_grab(False) # <<< УБРАНО Освобождаем захват на всякий случай
                else: # Если кнопка все еще нажата, продолжаем перетаскивать
                    self.move_handle_to_pos(event.pos[0])
                # --- Конец изменения ---

    def move_handle_to_pos(self, mouse_x):
        mouse_x = max(self.rect.x, min(mouse_x, self.rect.right))
        self.handle_rect.centerx = mouse_x
        ratio = (self.handle_rect.centerx - self.rect.x) / self.rect.width
        value_range = self.max_val - self.min_val
        self.value = self.min_val + (ratio ** self.power) * value_range
        self.value = round(self.value)
        self.value = max(self.min_val, min(self.value, self.max_val))

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_SLIDER_BG, self.rect, border_radius=5)

        value_range = self.max_val - self.min_val
        if value_range == 0:
            ratio = 0
        else:
            normalized_value = max(0.0, min(1.0, (self.value - self.min_val) / value_range))
            ratio = normalized_value ** (1.0 / self.power)

        filled_width = int(ratio * self.rect.width)
        filled_width = max(0, min(filled_width, self.rect.width))

        if filled_width > 0:
            filled_rect = pygame.Rect(self.rect.x, self.rect.y, filled_width, self.rect.height)
            pygame.draw.rect(surface, COLOR_SLIDER_HANDLE, filled_rect, border_radius=5)

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
            check_margin = 4 # Отступ от границы
            inner_rect = self.rect.inflate(-check_margin * 2, -check_margin * 2)
            pygame.draw.rect(surface, COLOR_CHECKBOX_CHECK, inner_rect, border_radius=2)
        label_surf = self.font.render(self.label, True, COLOR_TEXT)
        label_rect = label_surf.get_rect()
        label_rect.left = self.rect.right + 10
        label_rect.centery = self.rect.centery + 3
        surface.blit(label_surf, label_rect)

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

        dx = abs(ax - bx)
        dist_x = min(dx, self.grid_width - dx)

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
        path.reverse()
        return path

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], snake_positions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Находит кратчайший путь с помощью A*, УЧИТЫВАЯ движение хвоста змейки.
        Клетка считается проходимой, если к моменту достижения ее змейкой,
        сегмент хвоста, который ее занимал, уже исчезнет.
        """
        snake_length = len(snake_positions)
        snake_body_indices = {pos: i for i, pos in enumerate(snake_positions)}

        open_set_heap = [(self._heuristic(start, goal), 0, start)]
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0}

        while open_set_heap:
            current_f_cost, current_g_cost, current_pos = heapq.heappop(open_set_heap)

            if current_pos == goal:
                return self.reconstruct_path(came_from, goal)

            for neighbor_pos in self.get_neighbors(current_pos):
                tentative_g_cost = current_g_cost + 1

                is_collision = False
                if neighbor_pos in snake_body_indices:
                    segment_index = snake_body_indices[neighbor_pos]
                    # Столкновение происходит, если мы достигаем клетки РАНЬШЕ,
                    # чем этот сегмент хвоста исчезнет.
                    # Сегмент `idx` исчезнет на шаге `snake_length - idx`.
                    if tentative_g_cost < snake_length - segment_index:
                        is_collision = True

                if not is_collision:
                    if tentative_g_cost < g_score.get(neighbor_pos, float('inf')):
                        came_from[neighbor_pos] = current_pos
                        g_score[neighbor_pos] = tentative_g_cost
                        f_cost = tentative_g_cost + self._heuristic(neighbor_pos, goal)
                        heapq.heappush(open_set_heap, (f_cost, tentative_g_cost, neighbor_pos))

        return []

def generate_accordion_snake(percentage: int, grid_width: int, grid_height: int) -> Tuple[Deque[Tuple[int, int]], Tuple[int, int]]:
    """Генерирует начальную позицию змейки 'гармошкой' заданной длины."""
    target_length = max(1, int((grid_width * grid_height) * percentage / 100))

    if target_length <= 1:
         initial_pos = (grid_width // 2, grid_height // 2)
         possible_directions = [UP, DOWN, LEFT, RIGHT]
         return deque([initial_pos]), random.choice(possible_directions)

    positions = deque()
    x, y = 1, 1
    direction = RIGHT
    generated_count = 0
    stuck = False

    min_x, max_x = 1, grid_width - 2
    min_y, max_y = 1, grid_height - 2

    while generated_count < target_length:
        if not (min_x <= x <= max_x and min_y <= y <= max_y):
            stuck = True
            print(f"Warning: Accordion generation stuck or hit boundary at ({x},{y}). Generated: {generated_count}/{target_length}")
            break

        positions.appendleft((x, y))
        generated_count += 1

        if generated_count >= target_length:
            break

        next_x, next_y = x, y
        next_direction = direction

        if direction == RIGHT:
            if x + 1 <= max_x:
                next_x = x + 1
            else:
                if y + 1 <= max_y:
                    next_y = y + 1
                    next_direction = LEFT
                else:
                    stuck = True
                    break
        elif direction == LEFT:
            if x - 1 >= min_x:
                next_x = x - 1
            else:
                if y + 1 <= max_y:
                    next_y = y + 1
                    next_direction = RIGHT
                else:
                    stuck = True
                    break

        x, y = next_x, next_y
        direction = next_direction

    if not positions:
        print("Error: Snake generation failed, defaulting to center.")
        initial_pos = (grid_width // 2, grid_height // 2)
        return deque([initial_pos]), random.choice([UP, DOWN, LEFT, RIGHT])

    # Важно: 'direction' после цикла содержит направление, КУДА двинулся генератор
    # для ПОСЛЕДНЕЙ добавленной клетки (головы). Это и есть начальное направление змейки.
    return positions, direction

class Snake:
    def __init__(self, mode='manual', initial_fill_percentage=0):
        self.length = 1
        initial_pos = ((GRID_WIDTH) // 2, (GRID_HEIGHT) // 2)
        self.positions: Deque[Tuple[int, int]] = deque([initial_pos])
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = COLOR_SNAKE
        self.mode = mode
        self.next_direction = self.direction
        self.path = []
        self.path_find = PathFind()
        self.speed = 10
        self.history: deque[Tuple[List[Tuple[int, int]], Optional[Tuple[int, int]]]] = deque(maxlen=1001)
        self.current_food_pos = None
        self.recalculate_path = True
        self.current_path: List[Tuple[int, int]] = []
        # --- Добавляем set для быстрой проверки наличия сегмента ---
        self.positions_set: set[Tuple[int, int]] = set(self.positions)
        # --- Конец добавления ---

        if initial_fill_percentage > 0:
            generated_positions, generated_direction = generate_accordion_snake(
                initial_fill_percentage, GRID_WIDTH, GRID_HEIGHT
            )
            if generated_positions:
                self.positions = generated_positions
                self.length = len(generated_positions)
                self.direction = generated_direction
                self.next_direction = generated_direction
                # --- Обновляем set после генерации ---
                self.positions_set = set(self.positions)
                # --- Конец обновления ---
            else:
                 print(f"Warning: Failed to generate snake for {initial_fill_percentage}%, starting with default.")

    def draw(self, surface):
        num_segments = len(self.positions)
        if num_segments == 0:
            return

        # --- Убираем создание list и set здесь ---
        # positions_list = list(self.positions)
        # positions_set = set(positions_list)
        # --- Конец уборки ---

        # --- Первый проход: Рисуем сплошные сегменты (используем self.positions) ---
        # Голова
        head_pos = self.positions[0]
        draw_object(surface, COLOR_SNAKE_HEAD, head_pos)

        # Тело и хвост (только цвет, без линий)
        if num_segments > 1:
            head_color = COLOR_SNAKE_HEAD_GRADIENT
            body_color = COLOR_SNAKE
            tail_color = COLOR_SNAKE_TAIL

            # Итерируем напрямую по deque, пропуская голову (i=0)
            for i, current_pos in enumerate(itertools.islice(self.positions, 1, None)):
                # Рассчитываем цвет
                # Индекс в islice начинается с 0, а нам нужен оригинальный индекс, начиная с 1
                original_index = i + 1
                progress = (original_index - 1) / (num_segments - 1) if num_segments > 1 else 0
                segment_color: pygame.Color = pygame.Color(0, 0, 0)
                if progress < 0.5:
                    local_progress = progress / 0.5
                    segment_color = head_color.lerp(body_color, local_progress)
                else:
                    local_progress = (progress - 0.5) / 0.5
                    segment_color = body_color.lerp(tail_color, local_progress)
                # Рисуем сегмент
                draw_object(surface, segment_color, current_pos)

        # --- Второй проход: Рисуем ВНУТРЕННИЕ границы (используем self.positions и self.positions_set) ---
        if num_segments > 1:
            internal_border_color = COLOR_GRID # Цвет для внутренних линий
            line_width = 1
            for i, current_pos in enumerate(self.positions): # Итерируем по ВСЕМ сегментам deque
                x, y = current_pos
                x_px, y_px = x * GRIDSIZE, y * GRIDSIZE

                # Определяем фактических соседей по цепочке
                prev_actual_pos = self.positions[i-1] if i > 0 else None
                # Обращение к i+1 безопасно, если i < num_segments - 1
                next_actual_pos = self.positions[i+1] if i < num_segments - 1 else None

                # Проверяем соседа СПРАВА (используем self.positions_set для быстрой проверки)
                neighbor_right = ((x + 1) % GRID_WIDTH, y)
                if (neighbor_right in self.positions_set and
                    neighbor_right != prev_actual_pos and
                    neighbor_right != next_actual_pos):
                    pygame.draw.line(surface, internal_border_color,
                                     (x_px + GRIDSIZE - line_width, y_px),
                                     (x_px + GRIDSIZE - line_width, y_px + GRIDSIZE -1),
                                     line_width)

                # Проверяем соседа СНИЗУ (используем self.positions_set)
                neighbor_down = (x, (y + 1) % GRID_HEIGHT)
                if (neighbor_down in self.positions_set and
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
        self.current_food_pos = food_pos
        self.direction = self.next_direction
        collision = False
        if self.mode == 'auto':
            collision = self.auto_move(food_pos)
        else:
            collision = self.manual_move()

        if self.positions:
             self.history.append((list(self.positions), self.current_food_pos))

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
        new_head_pos = None # Инициализируем

        # --- Логика пересчета пути ---
        if self.recalculate_path or not self.current_path:
            path_to_food = self.path_find.find_path(head, food_pos, list(self.positions))

            if path_to_food and self.is_path_safe_to_food(path_to_food):
                self.current_path = path_to_food
                self.path = self.current_path # Обновляем path для визуализации
                self.recalculate_path = False # Путь найден, пока не пересчитываем
                if len(self.current_path) > 1:
                    next_move_pos = self.current_path[1]
                    self.next_direction = self.get_direction_to(next_move_pos)
                else: # Путь состоит только из головы? Маловероятно, но сохраняем тек. направление
                    self.next_direction = self.direction
            else:
                # Безопасного пути к еде нет, ищем выживание
                self.current_path = []
                self.path = [] # Очищаем path для визуализации
                self.recalculate_path = True # Нужно будет искать путь на след. шаге
                survival_direction = self.find_survival_move()
                if survival_direction:
                    self.next_direction = survival_direction
                else:
                    safe_immediate_direction = self.find_immediate_safe_direction()
                    if safe_immediate_direction:
                        self.next_direction = safe_immediate_direction
                    else:
                        # Полный тупик, сохраняем текущее направление (все равно врежется)
                        self.next_direction = self.direction
        else:
            # Путь уже рассчитан и валиден, следуем ему
            if len(self.current_path) > 1:
                next_move_pos = self.current_path[1]
                self.next_direction = self.get_direction_to(next_move_pos)
            else:
                # Достигли конца пути (или путь некорректен), запрашиваем пересчет
                self.recalculate_path = True
                self.current_path = []
                self.path = []
                self.next_direction = self.find_immediate_safe_direction() or self.direction # Пытаемся хоть куда-то

        # --- Выполняем ход ---
        self.direction = self.next_direction
        cur = self.get_head_position()
        x, y = self.direction
        new_head_pos = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        collision = self.move_forward(new_head_pos)

        # --- Обновляем current_path после хода (если не было съедено или ошибки) ---
        # Удаляем узел, ИЗ которого только что вышли (старая голова)
        if not self.recalculate_path and self.current_path:
             # Убедимся, что первый элемент - это действительно старая голова
             if self.current_path[0] == cur:
                 self.current_path.pop(0)
             else:
                 # Если это не так, что-то пошло не так, лучше пересчитать путь
                 self.recalculate_path = True
                 self.current_path = []
                 self.path = []


        return collision

    def move_forward(self, new_head_pos):
        """Обновляет позицию змейки: добавляет голову, удаляет хвост (если не растет), проверяет коллизии."""
        collision = False
        # Проверяем коллизию с телом ДО добавления новой головы.
        # Используем self.positions_set для быстрой проверки O(1), кроме хвоста.
        tail_pos = self.positions[-1] if len(self.positions) > 0 else None
        if new_head_pos in self.positions_set and new_head_pos != tail_pos:
             collision = True

        # --- Обновляем set ПЕРЕД изменением deque ---
        self.positions_set.add(new_head_pos)
        # --- Конец обновления ---
        self.positions.appendleft(new_head_pos)

        # Проверяем, съела ли змейка еду на этом шаге (сравниваем новую голову с позицией еды)
        grows = (new_head_pos == self.current_food_pos)

        # Удаляем хвост, если змейка не съела еду на этом шаге
        if not grows:
            # --- Обновляем set ПЕРЕД изменением deque ---
            # Проверяем, есть ли хвост для удаления
            if self.positions:
                removed_tail = self.positions.pop()
                # Удаляем из set только если это действительно был последний уникальный сегмент хвоста
                # (на случай, если голова и хвост были в одной клетке - редкий баг)
                # Однако, deque.pop() удаляет элемент, так что проверка на дубликат не нужна,
                # если он был в set, он должен быть удален.
                # Но нужна проверка, что удаляемый хвост вообще есть в set (хотя должен быть).
                if removed_tail in self.positions_set:
                     # Дополнительная проверка: не удалять, если этот же сегмент все еще есть в deque
                     # (это может случиться при длине 1 или при очень коротких замыканиях)
                     if removed_tail not in self.positions:
                           self.positions_set.remove(removed_tail)
                # Если хвоста не было в set, это ошибка, но игнорируем
            # --- Конец обновления ---
        # Если змейка растет (grows=True), хвост не удаляется, и set не меняется (кроме добавления головы)
        elif grows:
             # Если съели еду, увеличиваем целевую длину. Хвост не удаляется в этот раз.
             self.length += 1
             self.recalculate_path = True
             self.current_path = []
             self.path = []

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

        if abs(dx) > abs(dy):
            return RIGHT if dx > 0 else LEFT
        elif abs(dy) > abs(dx):
            return DOWN if dy > 0 else UP
        else:
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
        random.shuffle(possible_directions)

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
        max_freedom = -1

        head = self.get_head_position()
        # Рассматриваем только ходы вперед и вбок (не разворот)
        possible_directions = [d for d in [UP, DOWN, LEFT, RIGHT] if d != (self.direction[0] * -1, self.direction[1] * -1)]

        current_positions_list = list(self.positions)

        for direction in possible_directions:
            next_head = ((head[0] + direction[0]) % GRID_WIDTH, (head[1] + direction[1]) % GRID_HEIGHT)

            # 1. Проверяем, не ведет ли ход сразу в тело (кроме хвоста)
            if len(self.positions) > 1 and next_head in itertools.islice(self.positions, 0, len(self.positions) - 1):
                 continue

            # 2. Симулируем этот один шаг (змейка НЕ растет)
            sim_snake_list = self.simulate_move([head, next_head], grows=False, initial_state=current_positions_list)
            if sim_snake_list is None:
                continue

            # 3. Ищем путь от новой головы к новому хвосту в симулированном состоянии
            sim_head = sim_snake_list[0]
            sim_tail = sim_snake_list[-1]
            path_to_tail = self.path_find.find_path(sim_head, sim_tail, sim_snake_list)

            # --- Изменяем метрику оценки хода ---
            # freedom = len(path_to_tail) # Старая метрика
            # Новая метрика: длина пути + 0.5 * эвристическое расстояние до хвоста
            # Это должно сильнее отталкивать от хвоста
            if path_to_tail:
                 freedom = len(path_to_tail) + self.path_find._heuristic(sim_head, sim_tail) * 0.5
            else:
                 # Если пути до хвоста нет, свобода минимальна, но все же попробуем учесть расстояние
                 freedom = self.path_find._heuristic(sim_head, sim_tail) * 0.2 
            # --- Конец изменения ---

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
            return False

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
        current_path = path[1:]

        for i, step in enumerate(current_path):
            # Проверка на самопересечение в симуляции: нельзя врезаться в сегмент,
            # который НЕ станет хвостом на следующем шаге симуляции.
            if len(sim_snake) > 1 and step in itertools.islice(sim_snake, 0, len(sim_snake) - 1):
                 return None

            sim_snake.appendleft(step)

            is_last_step = (i == len(current_path) - 1)
            # Удаляем хвост, если это не последний шаг ИЛИ если это последний шаг, но змейка не растет
            if not (is_last_step and grows):
                sim_snake.pop()

        return list(sim_snake)

    def reset(self, initial_fill_percentage=0):
        self.length = 1
        initial_pos = ((GRID_WIDTH) // 2, (GRID_HEIGHT) // 2)
        self.positions = deque([initial_pos])
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = self.direction
        self.path = []
        self.speed = 10
        self.history.clear()
        self.current_food_pos = None
        self.recalculate_path = True
        self.current_path = []
        self.path = []
        # --- Обновляем set после сброса ---
        self.positions_set = set(self.positions)
        # --- Конец обновления ---

        if initial_fill_percentage > 0:
            generated_positions, generated_direction = generate_accordion_snake(
                initial_fill_percentage, GRID_WIDTH, GRID_HEIGHT
            )
            if generated_positions:
                self.positions = generated_positions
                self.length = len(generated_positions)
                self.direction = generated_direction
                self.next_direction = generated_direction
                # --- Обновляем set после генерации ---
                self.positions_set = set(self.positions)
                # --- Конец обновления ---
            else:
                 print(f"Warning: Failed to generate snake for {initial_fill_percentage}% on reset, starting with default.")

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
    current_speed: Optional[int]
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
    rounded_speed = int(current_speed)
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
        is_main_menu_hovered = quit_button_rect.collidepoint(mouse_pos)
        is_retry_clicked = False
        is_main_menu_clicked = False

        prev_replay_index = replay_index # Запоминаем индекс до обработки событий

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # --- Исправляем: используем surface вместо screen --- 
                if confirmation_dialog(surface, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
                # --- Конец исправления --- 

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
                elif is_main_menu_hovered:
                    is_main_menu_clicked = True
                    if eat_sound:
                        eat_sound.play()
                    # Instead of quitting, return False to signal going back to main menu
                    return False

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
        draw_button(surface, quit_button_rect, COLOR_BUTTON, "Main Menu", is_main_menu_hovered, is_main_menu_clicked)

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

def settings_screen(surface, current_speed, current_volume, mute, current_fill_percent) -> Tuple[int, int, bool, int]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    title_surf = font_title.render("Settings", True, COLOR_TEXT_WHITE)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 220))

    # Виджеты настроек
    slider_width = 350
    slider_height = 25
    checkbox_size = 25
    widget_x = SCREEN_WIDTH // 2 - slider_width // 2
    y_pos = SCREEN_HEIGHT // 2 - 140 # Начальная Y позиция

    # --- Устанавливаем min_val = 5 для слайдера скорости ---
    speed_slider = Slider(widget_x, y_pos, slider_width, slider_height, 5, 5000, current_speed, "Game Speed", power=2.5)
    # --- Конец изменения ---
    y_pos += 70 # Стандартный отступ

    volume_slider = Slider(widget_x, y_pos, slider_width, slider_height, 0, 100, current_volume, "Sound Volume")
    y_pos += 70 # Стандартный отступ

    # --- Меняем порядок: сначала слайдер заполнения ---
    fill_slider = Slider(widget_x, y_pos, slider_width, slider_height, 0, 95, current_fill_percent, "Initial Fill (%)")
    y_pos += 70 # Стандартный отступ

    mute_checkbox = Checkbox(widget_x, y_pos, checkbox_size, "Mute Sound", mute)
    y_pos += 70 # Стандартный отступ перед кнопкой

    button_width = 180 # Уменьшаем ширину кнопок, чтобы поместились две
    button_height = 55
    button_spacing = 24 # Расстояние между кнопками
    # --- Добавляем кнопку Reset Defaults ---
    reset_button_rect = pygame.Rect(0, 0, button_width, button_height)
    back_button_rect = pygame.Rect(0, 0, button_width, button_height)
    
    # Располагаем кнопки по горизонтали с отступом
    total_width = 2 * button_width + button_spacing
    reset_button_rect.topleft = (SCREEN_WIDTH // 2 - total_width // 2, y_pos)
    back_button_rect.topleft = (reset_button_rect.right + button_spacing, y_pos)
    # --- Конец добавления ---

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        is_back_hovered = back_button_rect.collidepoint(mouse_pos)
        is_back_clicked = False # Сброс состояния клика в начале кадра
        # --- Добавляем состояния для кнопки Reset ---
        is_reset_hovered = reset_button_rect.collidepoint(mouse_pos)
        is_reset_clicked = False # Сброс состояния клика
        # --- Конец добавления ---

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # --- Добавляем подтверждение при закрытии окна --- 
                if confirmation_dialog(surface, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
                # --- Конец добавления --- 

            # Сначала передаем события виджетам (слайдеры, чекбокс)
            speed_slider.handle_event(event)
            volume_slider.handle_event(event)
            fill_slider.handle_event(event)
            mute_checkbox.handle_event(event)

            # Затем проверяем клик по кнопкам
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_back_hovered:
                    is_back_clicked = True
                    if eat_sound:
                        eat_sound.play()
                    running = False # Выходим из цикла настроек
                # --- Добавляем обработку нажатия на кнопку Reset ---
                elif is_reset_hovered:
                    is_reset_clicked = True
                    if eat_sound:
                        eat_sound.play()
                    # Сбрасываем настройки к значениям по умолчанию
                    selected_speed = 15 # Значение по умолчанию
                    selected_volume = 1 # Громкость по умолчанию
                    is_muted = False # Звук включен
                    selected_fill_percent = 0 # Начальное заполнение 0%
                    # Обновляем виджеты
                    speed_slider.value = selected_speed
                    speed_slider.update_handle_pos()
                    volume_slider.value = selected_volume
                    volume_slider.update_handle_pos()
                    fill_slider.value = selected_fill_percent
                    fill_slider.update_handle_pos()
                    mute_checkbox.checked = is_muted
                    # Применяем громкость немедленно
                    if eat_sound:
                        eat_sound.set_volume(0 if is_muted else selected_volume / 100)
                # --- Конец добавления ---
            # --- Добавляем выход из настроек по Escape --- 
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False # Выходим из цикла настроек
            # --- Конец добавления --- 
            # MOUSEBUTTONUP не обрабатываем для кнопки, т.к. действие происходит по нажатию

        # Получаем текущие значения из виджетов
        selected_speed = speed_slider.value
        selected_volume = volume_slider.value
        is_muted = mute_checkbox.checked
        selected_fill_percent = fill_slider.value

        # Применяем громкость немедленно
        if eat_sound:
            eat_sound.set_volume(0 if is_muted else selected_volume / 100)

        # Отрисовка
        surface.fill(COLOR_BACKGROUND)
        surface.blit(title_surf, title_rect)
        speed_slider.draw(surface)
        volume_slider.draw(surface)
        fill_slider.draw(surface)
        mute_checkbox.draw(surface)
        draw_button(surface, back_button_rect, COLOR_BUTTON, "Back", is_back_hovered, is_back_clicked)
        # --- Изменяем текст кнопки Reset ---
        draw_button(surface, reset_button_rect, COLOR_TEXT_HIGHLIGHT, "Reset", is_reset_hovered, is_reset_clicked)
        # --- Конец изменения ---

        pygame.display.update()
        clock.tick(60)

    # Возвращаем выбранные значения ПОСЛЕ выхода из цикла
    # --- Обновляем возвращаемое значение: добавляем selected_fill_percent --- 
    return selected_speed, selected_volume, is_muted, selected_fill_percent

def start_screen(surface, initial_speed, initial_volume, initial_mute, initial_fill_percent) -> Tuple[str, int, int, bool, int]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    # --- Добавляем font_small, если он отсутствует (на всякий случай) --- 
    try:
        font_small = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_small = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
    # --- Конец добавления --- 

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
    # --- Сдвигаем кнопку Quit выше, т.к. убрали настройку заполнения ---
    quit_button_rect.center = (SCREEN_WIDTH // 2, settings_button_rect.bottom + button_spacing)

    # Словарь для удобного управления кнопками
    buttons = {
        "manual": {"rect": manual_button_rect, "text": "Manual Play", "color": COLOR_BUTTON},
        "auto": {"rect": auto_button_rect, "text": "Auto Play (AI)", "color": COLOR_BUTTON},
        "settings": {"rect": settings_button_rect, "text": "Settings", "color": COLOR_TEXT_HIGHLIGHT}, # Выделяем настройки
        "quit": {"rect": quit_button_rect, "text": "Quit Game", "color": COLOR_BUTTON}
    }

    # Начальные значения настроек (будут изменены, если зайти в Settings)
    current_speed = initial_speed
    current_volume = initial_volume
    mute = initial_mute
    current_fill_percent = initial_fill_percent
    waiting = True

    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        hover_states = {key: data["rect"].collidepoint(mouse_pos) for key, data in buttons.items()}
        click_states = {key: False for key in buttons}

        for event in pygame.event.get():
            # --- Убедимся, что обработка QUIT здесь есть --- 
            if event.type == pygame.QUIT:
                if confirmation_dialog(surface, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
            # --- Конец проверки --- 
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                button_clicked = False
                for key, data in buttons.items():
                    if hover_states[key]: # Если кликнули по кнопке, над которой курсор
                        click_states[key] = True # Устанавливаем флаг клика для отрисовки
                        if eat_sound and not mute:
                            eat_sound.play()

                        # Выполняем действие в зависимости от нажатой кнопки
                        if key == 'manual':
                            # --- Возвращаем current_fill_percent --- 
                            return 'manual', int(current_speed), int(current_volume), mute, current_fill_percent
                        elif key == 'auto':
                            # --- Возвращаем current_fill_percent --- 
                            return 'auto', int(current_speed), int(current_volume), mute, current_fill_percent
                        elif key == 'settings':
                            # Открываем экран настроек и получаем обновленные значения
                            # Передаем ТЕКУЩИЕ значения из start_screen в settings_screen
                            current_speed, current_volume, mute, current_fill_percent = settings_screen(surface, current_speed, current_volume, mute, current_fill_percent)
                            # Применяем новую громкость сразу после возврата из настроек
                            if eat_sound:
                                eat_sound.set_volume(0 if mute else current_volume / 100)
                        elif key == 'quit':
                            # --- Вызываем диалог подтверждения перед выходом --- 
                            if confirmation_dialog(surface, "Quit Game?"):
                                pygame.quit()
                                sys.exit()
                            # Если пользователь нажал "No", ничего не делаем
                            # --- Конец изменения ---
                        button_clicked = True
                        break # Выходим из цикла по кнопкам, т.к. клик обработан

        # Отрисовка стартового экрана
        surface.fill(COLOR_BACKGROUND)
        surface.blit(title_surf, title_rect)

        for key, data in buttons.items():
            # Передаем состояния hover и click в функцию отрисовки кнопки
            draw_button(surface, data['rect'], data['color'], data['text'], hover_states[key], click_states[key])

        pygame.display.update()
        clock.tick(60)
    # --- Добавляем return, чтобы удовлетворить линтер (хотя эта ветка маловероятна) --- 
    # Этот return не должен достигаться при нормальной работе, 
    # так как выход происходит через кнопки Manual/Auto/Quit или закрытие окна.
    # Возвращаем значения по умолчанию или выбрасываем исключение.
    # --- Возвращаем current_fill_percent по умолчанию --- 
    return 'manual', 15, 1, False, 0 # Пример значений по умолчанию

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
                    paused = False
        pygame.time.Clock().tick(15)

# --- Добавляем функцию диалога подтверждения выхода ---
def confirmation_dialog(surface, question) -> bool:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(210) # Сильнее затемнение
    overlay.fill(COLOR_BACKGROUND)
    surface.blit(overlay, (0, 0))

    try:
        font_question = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE)
        font_button = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_question = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2)
        font_button = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    question_surf = font_question.render(question, True, COLOR_TEXT_WHITE)
    question_rect = question_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    surface.blit(question_surf, question_rect)

    button_width = 150
    button_height = 50
    button_spacing = 30
    yes_button_rect = pygame.Rect(0, 0, button_width, button_height)
    no_button_rect = pygame.Rect(0, 0, button_width, button_height)

    total_width = button_width * 2 + button_spacing
    yes_button_rect.topleft = (SCREEN_WIDTH // 2 - total_width // 2, question_rect.bottom + 40)
    no_button_rect.topleft = (yes_button_rect.right + button_spacing, yes_button_rect.top)

    clock = pygame.time.Clock() # Нужен свой clock для цикла диалога
    while True:
        mouse_pos = pygame.mouse.get_pos()
        is_yes_hovered = yes_button_rect.collidepoint(mouse_pos)
        is_no_hovered = no_button_rect.collidepoint(mouse_pos)
        is_yes_clicked = False
        is_no_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Если пытаются закрыть во время диалога, считаем это отказом
                return False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                     # Escape в диалоге = отказ
                     return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_yes_hovered:
                    is_yes_clicked = True
                    if eat_sound: eat_sound.play()
                    pygame.time.wait(150) # Небольшая задержка для звука
                    return True # Подтверждение выхода
                elif is_no_hovered:
                    is_no_clicked = True
                    if eat_sound: eat_sound.play()
                    pygame.time.wait(150)
                    return False # Отказ от выхода

        # Перерисовка кнопок в цикле диалога
        temp_surface = surface.copy() # Копируем фон с текстом вопроса
        draw_button(temp_surface, yes_button_rect, COLOR_GAMEOVER, "Yes", is_yes_hovered, is_yes_clicked) # Используем цвет Game Over для "Yes"
        draw_button(temp_surface, no_button_rect, COLOR_BUTTON, "No", is_no_hovered, is_no_clicked)
        # --- Исправляем: используем surface вместо screen ---
        surface.blit(temp_surface, (0,0)) # Рисуем обновленный кадр
        # --- Конец исправления --- 

        pygame.display.update()
        clock.tick(60)
# --- Конец добавления функции --- 

def get_direction_vector(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> Tuple[int, int]:
    """Вычисляет вектор (dx, dy) от pos1 к pos2, учитывая зацикленность поля."""
    x1, y1 = pos1
    x2, y2 = pos2
    dx = x2 - x1
    dy = y2 - y1

    if abs(dx) > GRID_WIDTH / 2:
        sign = 1 if dx > 0 else -1
        dx = - (GRID_WIDTH - abs(dx)) * sign
    if abs(dy) > GRID_HEIGHT / 2:
        sign = 1 if dy > 0 else -1
        dy = - (GRID_HEIGHT - abs(dy)) * sign

    if dx != 0: dx //= abs(dx)
    if dy != 0: dy //= abs(dy)

    return dx, dy

# --- Функция для отрисовки графика FPS ---
def draw_fps_graph(surface: Surface, history: Deque[float], x: int, y: int, width: int, height: int, color: pygame.Color):
    """Рисует простой линейный график на основе истории значений."""
    if not history:
        return
    history_len = len(history)
    max_fps_hist = max(history)
    dynamic_max_y = max(30.0, max_fps_hist * 1.1)
 
    points = []
    for i, fps in enumerate(history):
        normalized_y = 1.0 - max(0.0, min(1.0, fps / dynamic_max_y))
        point_x = x + int((i / (history_len - 1 if history_len > 1 else 1)) * width)
        point_y = y + int(normalized_y * height)
        points.append((point_x, point_y))

    if len(points) >= 2:
        try:
            pygame.draw.aalines(surface, color, False, points)
        except TypeError:
            pygame.draw.lines(surface, color, False, points, 1)
    elif len(points) == 1:
        pygame.draw.circle(surface, color, points[0], 2)

def main():
    # --- Инициализация Pygame и общих ресурсов (выполняется один раз) ---
    pygame.display.set_caption('Modern Snake Game')
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Шрифты для UI (загружаем один раз)
    try:
        font_icon = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        font_panel = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_SMALL)
        font_tiny = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_TINY)
    except:
        font_icon = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
        font_panel = pygame.font.SysFont('arial', FONT_SIZE_SMALL - 2)
        font_tiny = pygame.font.SysFont('arial', FONT_SIZE_TINY - 1)

    high_score = 0
    # --- Определяем переменные настроек ЗДЕСЬ, до главного цикла --- 
    current_speed = 15
    current_volume = 1 # Громкость по умолчанию (0-100)
    mute = False
    current_fill_percent = 0 # Начальное значение по умолчанию
    fps_history: Deque[float] = deque(maxlen=2222)

    while True:
        # --- Передаем текущие настройки в start_screen --- 
        mode, updated_speed, updated_volume, updated_mute, updated_fill_percent = start_screen(
            screen,
            current_speed, 
            current_volume, 
            mute, 
            current_fill_percent
        )
        # --- Обновляем настройки в main значениями, вернувшимися из start_screen --- 
        current_speed = updated_speed
        current_volume = updated_volume
        mute = updated_mute
        current_fill_percent = updated_fill_percent
        # --- Конец обновления --- 

        # --- Используем обновленные настройки для игры --- 
        initial_current_speed = current_speed # Переименовали для ясности внутри игрового цикла

        if eat_sound:
            eat_sound.set_volume(0 if mute else current_volume / 100)

        # Передаем current_fill_percent в конструктор Snake
        snake = Snake(mode, initial_fill_percentage=current_fill_percent)
        # Используем initial_current_speed (которое теперь равно обновленному current_speed)
        snake.speed = initial_current_speed 
        food = Food()
        food.randomize_position(snake_positions=snake.positions)
        score = 0

        panel_width = 160
        panel_height = 70
        panel_margin_top = 5
        panel_margin_right = 5
        speed_panel_rect = pygame.Rect(SCREEN_WIDTH - panel_width - panel_margin_right, panel_margin_top, panel_width, panel_height)

        slider_margin_h = 15
        slider_margin_top = 35
        slider_height = 15
        # --- Устанавливаем min_val = 5 для игрового слайдера скорости ---
        game_speed_slider = Slider(speed_panel_rect.x + slider_margin_h,
                                   speed_panel_rect.y + slider_margin_top,
                                   speed_panel_rect.width - 2 * slider_margin_h,
                                   slider_height,
                                   5, 5000, snake.speed, "",
                                   power=2.5)
        # --- Конец изменения ---

        # --- Инициализируем panel_alpha перед циклом --- 
        panel_alpha = 76 # Начальное значение (не наведено)

        # --- Внутренний игровой цикл ---
        game_running = True
        while game_running:
            # --- Получаем позицию мыши и вычисляем panel_alpha в начале кадра --- 
            mouse_pos = pygame.mouse.get_pos()
            is_panel_hovered = speed_panel_rect.collidepoint(mouse_pos)
            panel_alpha = 255 if is_panel_hovered else 76
            # --- Конец вычислений --- 

            game_controls_active = not is_panel_hovered

            game_speed_slider.value = snake.speed
            game_speed_slider.update_handle_pos()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    # --- Добавляем подтверждение при закрытии окна --- 
                    if confirmation_dialog(screen, "Quit Game?"):
                        pygame.quit()
                        sys.exit()
                    # --- Конец добавления --- 

                panel_interaction = False
                if is_panel_hovered:
                    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                        game_speed_slider.handle_event(event)
                        snake.speed = int(game_speed_slider.value)
                        panel_interaction = True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # --- При выходе из игры через Escape возвращаемся в start_screen --- 
                        game_running = False
                        # Не используем break здесь, чтобы цикл завершился естественным образом

                    if game_controls_active:
                         if event.key == pygame.K_p:
                             pause_screen(screen)
                         if snake.mode == 'manual':
                             if event.key == pygame.K_UP: snake.turn(UP)
                             elif event.key == pygame.K_DOWN: snake.turn(DOWN)
                             elif event.key == pygame.K_LEFT: snake.turn(LEFT)
                             elif event.key == pygame.K_RIGHT: snake.turn(RIGHT)
                            # --- Добавляем управление WASD --- 
                             elif event.key == pygame.K_w: snake.turn(UP)
                             elif event.key == pygame.K_s: snake.turn(DOWN)
                             elif event.key == pygame.K_a: snake.turn(LEFT)
                             elif event.key == pygame.K_d: snake.turn(RIGHT)
                            # --- Конец добавления --- 
                         if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                             snake.speed = min(5000, snake.speed + 5)
                         elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                             snake.speed = max(1, snake.speed - 5)

                # --- Проверка game_running перед ходом змейки --- 
                if not game_running:
                    break # Выходим из игрового цикла, чтобы вернуться в start_screen

            if not game_running:
                break

            collision = snake.move(food.position)

            if collision:
                final_history = deque(snake.history)
                if score > high_score:
                    high_score = score

                if melody_sound and not mute:
                    melody_sound.play()

                # --- Получаем текущие настройки для передачи в replay/game_over --- 
                # (Хотя replay_screen их пока не использует, но логично передать)
                current_speed_on_death = int(snake.speed)
                # current_volume, mute, current_fill_percent - эти значения не меняются в игровом цикле,
                # можно использовать те, что были при старте игры.

                should_restart = game_over_screen(screen, score, snake.length, high_score, current_speed_on_death, final_history)

                if should_restart:
                    # --- Передаем current_fill_percent в snake.reset --- 
                    snake.reset(initial_fill_percentage=current_fill_percent)
                    # Восстанавливаем скорость, которая была выбрана ДО смерти (или из настроек)
                    snake.speed = initial_current_speed
                    food.randomize_position(snake_positions=snake.positions)
                    score = 0
                    game_controls_active = True # Снова активируем управление
                else:
                    # Если не рестарт, выходим из игрового цикла, чтобы вернуться в start_screen
                    game_running = False

            elif snake.get_head_position() == food.position:
                food.randomize_position(snake_positions=snake.positions)
                if snake.mode == 'auto':
                     snake.current_food_pos = food.position

                if eat_sound and not mute:
                    eat_sound.play()
                score += 10 + int(snake.speed // 10)
                if score > high_score:
                    high_score = score

            screen.fill(COLOR_BACKGROUND)
            draw_grid(screen)

            if snake.mode == 'auto' and snake.path:
                draw_path(screen, snake.path)

            snake.draw(screen)
            food.draw(screen)
            display_statistics(screen, score, snake.length, high_score, snake.speed)

            # --- Обновляем историю и рисуем график FPS ---
            current_fps = clock.get_fps()
            fps_history.append(current_fps)

            # --- Параметры для графика и текста --- 
            graph_width = 100 # Возвращаем ширину графика
            text_width = 45   # Чуть больше места для текста
            padding = 5       # Отступ между графиком и текстом
            total_width = graph_width + padding + text_width # Общая ширина
            graph_height = 50 # Делаем виджет чуть выше
            margin_right = 10
            margin_bottom = 10

            # --- Координаты всего виджета FPS ---
            widget_x = SCREEN_WIDTH - total_width - margin_right
            widget_y = SCREEN_HEIGHT - graph_height - margin_bottom
            fps_widget_rect = pygame.Rect(widget_x, widget_y, total_width, graph_height)

            # --- Координаты для составных частей внутри виджета ---
            # --- Теперь координаты относительно НУЛЯ, т.к. рисуем на отдельной поверхности ---
            graph_x_rel = 0 # Относительно fps_widget_surface
            graph_y_rel = 0 # Относительно fps_widget_surface
            text_x_rel = graph_width + padding # Относительно fps_widget_surface
            text_y_rel = 0 # Относительно fps_widget_surface
            # --- Конец изменения относительных координат ---

            # --- Определяем прозрачность виджета FPS (при наведении на него) ---
            is_fps_widget_hovered = fps_widget_rect.collidepoint(mouse_pos)
            fps_widget_alpha = 255 if is_fps_widget_hovered else 76
            # --- Цвет фона теперь берем без альфа-канала сначала ---
            fps_bg_color_opaque = COLOR_PANEL_BG

            # --- Создаем отдельную поверхность для виджета FPS ---
            fps_widget_surface = pygame.Surface(fps_widget_rect.size, pygame.SRCALPHA)

            # --- Рисуем единый фон для всего виджета FPS НА ОТДЕЛЬНОЙ ПОВЕРХНОСТИ (НЕПРОЗРАЧНЫМ ЦВЕТОМ) ---
            pygame.draw.rect(fps_widget_surface, fps_bg_color_opaque, fps_widget_surface.get_rect(), border_radius=4)

            # --- Рисуем сам график НА ОТДЕЛЬНОЙ ПОВЕРХНОСТИ ---
            # Передаем ОТНОСИТЕЛЬНЫЕ координаты и размеры ГРАФИКА
            draw_fps_graph(fps_widget_surface, fps_history, graph_x_rel, graph_y_rel, graph_width, graph_height, color=COLOR_TEXT_HIGHLIGHT)

            # --- Рисуем текст справа от графика НА ОТДЕЛЬНОЙ ПОВЕРХНОСТИ ---
            if fps_history:
                min_fps = min(fps_history)
                max_fps_hist = max(fps_history)
                avg_fps = sum(fps_history) / len(fps_history)
                text_margin_in_area = 3

                # Max FPS
                max_text_surf = font_tiny.render(f"{max_fps_hist:.0f}", True, COLOR_TEXT)
                # --- Используем относительные координаты ---
                max_text_rect = max_text_surf.get_rect(topright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + text_margin_in_area))
                fps_widget_surface.blit(max_text_surf, max_text_rect)
                # Avg FPS
                avg_text_surf = font_tiny.render(f"{avg_fps:.0f}", True, COLOR_TEXT)
                # --- Используем относительные координаты ---
                avg_text_rect = avg_text_surf.get_rect(midright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height // 2))
                fps_widget_surface.blit(avg_text_surf, avg_text_rect)
                # Min FPS
                min_text_surf = font_tiny.render(f"{min_fps:.0f}", True, COLOR_TEXT)
                # --- Используем относительные координаты ---
                min_text_rect = min_text_surf.get_rect(bottomright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height - text_margin_in_area))
                fps_widget_surface.blit(min_text_surf, min_text_rect)
            # --- Конец блока FPS ---

            # --- Устанавливаем общую прозрачность для всей поверхности виджета FPS ---
            fps_widget_surface.set_alpha(fps_widget_alpha)

            # --- Копируем готовую поверхность FPS виджета на основной экран ---
            screen.blit(fps_widget_surface, fps_widget_rect.topleft)

            # --- Теперь рисуем панель скорости ПОСЛЕ графика FPS ---
            panel_bg_color_tuple = (COLOR_PANEL_BG.r, COLOR_PANEL_BG.g, COLOR_PANEL_BG.b, panel_alpha)
            panel_surface = pygame.Surface(speed_panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, panel_bg_color_tuple, panel_surface.get_rect(), border_radius=4)

            panel_title_surf = font_panel.render("Speed", True, COLOR_TEXT_WHITE)
            panel_title_rect = panel_title_surf.get_rect(centerx=panel_surface.get_rect().centerx, top=8)
            panel_surface.blit(panel_title_surf, panel_title_rect)

            original_slider_rect = game_speed_slider.rect.copy()
            game_speed_slider.rect.topleft = (slider_margin_h, slider_margin_top)
            game_speed_slider.draw(panel_surface)
            game_speed_slider.rect = original_slider_rect

            panel_surface.set_alpha(panel_alpha)

            screen.blit(panel_surface, speed_panel_rect.topleft)

            pygame.display.update()
            clock.tick(snake.speed)

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    clock = pygame.time.Clock()
    main()
