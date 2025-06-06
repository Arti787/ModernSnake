#!/usr/bin/env python3
import pygame
import sys
import random
import os
from collections import deque
from typing import List, Tuple, Set, Deque, Dict, Optional, Any, Union, TypedDict
import itertools
import heapq
import time # Import time for performance counter
from pygame import Surface
from pygame.font import Font

# --- Класс для значений с временными метками для статистики ---
class TimestampedValue:
    def __init__(self, value: float, timestamp: Optional[float] = None):
        self.value = value
        self.timestamp = time.time() if timestamp is None else timestamp

    def __lt__(self, other):
        return self.value < other.value if isinstance(other, TimestampedValue) else self.value < other

    def __gt__(self, other):
        return self.value > other.value if isinstance(other, TimestampedValue) else self.value > other

    def __eq__(self, other):
        return self.value == other.value if isinstance(other, TimestampedValue) else self.value == other

    def __float__(self):
        return float(self.value)

def get_values_in_timespan(history: Deque[TimestampedValue], seconds: float = 5.0) -> List[float]:
    """Get only values from the last N seconds."""
    now = time.time()
    return [item.value for item in history if now - item.timestamp <= seconds]

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
# --- Tyamba Theme ---
COLOR_TYAMBA = pygame.Color("#28675d")
# --- Sergaris Theme ---
COLOR_SERGARIS_DARK = pygame.Color("#1a1a1a")
COLOR_SERGARIS_GRAY = pygame.Color("#4d4d4d")
COLOR_SERGARIS_ORANGE = pygame.Color("#ff7733")
COLOR_SERGARIS_BLUE = pygame.Color("#66cccc")

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

SURVIVAL_MODE_DURATION = 20

# --- Централизованное определение тем ---
def _generate_tyamba_colors():
    """Генерирует палитру для темы Tyamba."""
    base_color = COLOR_TYAMBA
    darker = pygame.Color(base_color.r // 2, base_color.g // 2, base_color.b // 2)
    lighter = pygame.Color(min(base_color.r + 70, 255), min(base_color.g + 70, 255), min(base_color.b + 70, 255))
    accent = pygame.Color(min(base_color.r + 50, 255), min(base_color.g, 255), min(base_color.b + 80, 255))
    return {
        'background': darker,
        'grid': base_color,
        'snake': lighter,
        'snake_head': accent,
        'snake_head_gradient': pygame.Color(min(accent.r + 30, 255), min(accent.g + 30, 255), min(accent.b, 255)),
        'snake_tail': darker.lerp(base_color, 0.3),
        'food': pygame.Color(min(base_color.r + 100, 255), min(base_color.g, 255), min(base_color.b, 255)),
        'path_visualization': pygame.Color(min(base_color.r + 120, 255), min(base_color.g + 60, 255), min(base_color.b, 255)),
        'text': pygame.Color(220, 220, 220),
        'text_highlight': pygame.Color(min(base_color.r + 120, 255), min(base_color.g + 120, 255), min(base_color.b + 20, 255)),
        'text_white': pygame.Color(255, 255, 255),
        'button': lighter,
        'button_hover': accent,
        'button_click': pygame.Color(min(base_color.r, 255), min(base_color.g + 60, 255), min(base_color.b + 60, 255)),
        'slider_bg': base_color,
        'slider_handle': accent,
        'panel_bg': pygame.Color(int(darker.r), int(darker.g), int(darker.b), 210),
        'checkbox_border': pygame.Color(200, 200, 200),
        'checkbox_check': accent,
        'gameover': pygame.Color(min(base_color.r + 100, 255), min(base_color.g, 255), min(base_color.b, 255)),
    }

def _generate_sergaris_colors():
    """Генерирует палитру для темы Sergaris."""
    return {
        'background': COLOR_SERGARIS_DARK,
        'grid': COLOR_SERGARIS_GRAY,
        'snake': COLOR_SERGARIS_GRAY,
        'snake_head': COLOR_SERGARIS_BLUE,
        'snake_head_gradient': COLOR_SERGARIS_ORANGE,
        'snake_tail': COLOR_SERGARIS_GRAY.lerp(COLOR_SERGARIS_DARK, 0.7),
        'food': COLOR_SERGARIS_BLUE,
        'path_visualization': COLOR_SERGARIS_BLUE,
        'text': pygame.Color(220, 220, 220),
        'text_highlight': COLOR_SERGARIS_ORANGE,
        'text_white': pygame.Color(255, 255, 255),
        'button': COLOR_SERGARIS_GRAY,
        'button_hover': COLOR_SERGARIS_ORANGE,
        'button_click': COLOR_SERGARIS_BLUE,
        'slider_bg': COLOR_SERGARIS_GRAY,
        'slider_handle': COLOR_SERGARIS_ORANGE,
        'panel_bg': pygame.Color(COLOR_SERGARIS_DARK.r, COLOR_SERGARIS_DARK.g, COLOR_SERGARIS_DARK.b, 210),
        'checkbox_border': COLOR_SERGARIS_GRAY,
        'checkbox_check': COLOR_SERGARIS_ORANGE,
        'gameover': COLOR_SERGARIS_ORANGE,
    }

THEME_DEFINITIONS = {
    "default": {
        "title": "Default Theme",
        "palette": {
            'background': COLOR_BACKGROUND,
            'grid': COLOR_GRID,
            'snake': COLOR_SNAKE,
            'snake_head': COLOR_SNAKE_HEAD,
            'snake_head_gradient': COLOR_SNAKE_HEAD_GRADIENT,
            'snake_tail': COLOR_SNAKE_TAIL,
            'food': COLOR_FOOD,
            'path_visualization': COLOR_PATH_VISUALIZATION,
            'text': COLOR_TEXT,
            'text_highlight': COLOR_TEXT_HIGHLIGHT,
            'text_white': COLOR_TEXT_WHITE,
            'button': COLOR_BUTTON,
            'button_hover': COLOR_BUTTON_HOVER,
            'button_click': COLOR_BUTTON_CLICK,
            'slider_bg': COLOR_SLIDER_BG,
            'slider_handle': COLOR_SLIDER_HANDLE,
            'panel_bg': COLOR_PANEL_BG,
            'checkbox_border': COLOR_CHECKBOX_BORDER,
            'checkbox_check': COLOR_CHECKBOX_CHECK,
            'gameover': COLOR_GAMEOVER
        }
    },
    "tyamba": {
        "title": "Tyamba Theme",
        "palette": _generate_tyamba_colors()
    },
    "sergaris": {
        "title": "Sergaris Theme",
        "palette": _generate_sergaris_colors()
    }
}

current_theme = "default"
current_colors = THEME_DEFINITIONS["default"]["palette"].copy()

def set_theme(theme_name):
    """Устанавливает цветовую тему игры, используя THEME_DEFINITIONS."""
    global current_theme, current_colors
    
    if theme_name not in THEME_DEFINITIONS:
        print(f"Warning: Theme '{theme_name}' not found. Using default theme.")
        theme_name = "default"
        
    current_theme = theme_name
    new_palette = THEME_DEFINITIONS[theme_name]["palette"]
    
    default_palette = THEME_DEFINITIONS["default"]["palette"]
    for key in default_palette:
        current_colors[key] = new_palette.get(key, default_palette[key])

def draw_object(surface, color, pos):
    rect = pygame.Rect((pos[0] * GRIDSIZE, pos[1] * GRIDSIZE), (GRIDSIZE, GRIDSIZE))
    pygame.draw.rect(surface, color, rect)

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRIDSIZE):
        pygame.draw.line(surface, current_colors['grid'], (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRIDSIZE):
        pygame.draw.line(surface, current_colors['grid'], (0, y), (SCREEN_WIDTH, y))

def draw_button(surface, button, base_color, text, is_hovered, is_clicked):
    button_color = base_color
    if is_clicked:
        button_color = current_colors['button_click']
    elif is_hovered:
        button_color = base_color.lerp(current_colors['background'], 0.2)


    button_rect = pygame.Rect(button)
    pygame.draw.rect(surface, button_color, button_rect, border_radius=8)

    try:
        font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    text_surf = font.render(text, True, current_colors['text_white'])
    text_rect = text_surf.get_rect(center=button_rect.center)
    text_rect.centery += 3
    surface.blit(text_surf, text_rect)

def draw_path(surface, path):
    """Отрисовывает предполагаемый путь змейки (для автопилота)."""
    try:
        for p in path:
            draw_object(surface, current_colors['path_visualization'], p)
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
        self.pending_click = False
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
        return self.handle_rect.inflate(10, 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [1, 2, 3]:
                if self.get_handle_bounds_for_collision().collidepoint(event.pos):
                    self.dragging = True
                    self.move_handle_to_pos(event.pos[0])
                elif self.rect.collidepoint(event.pos):
                    self.dragging = True
                    self.move_handle_to_pos(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.dragging:
                self.dragging = False
        elif event.type == pygame.ACTIVEEVENT:
            if event.state & pygame.APPACTIVE:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_buttons = pygame.mouse.get_pressed()
                if not mouse_buttons[0]:
                    self.dragging = False
                else:
                    self.move_handle_to_pos(event.pos[0])

    def move_handle_to_pos(self, mouse_x):
        mouse_x = max(self.rect.x, min(mouse_x, self.rect.right))
        self.handle_rect.centerx = mouse_x
        ratio = (self.handle_rect.centerx - self.rect.x) / self.rect.width
        value_range = self.max_val - self.min_val
        self.value = self.min_val + (ratio ** self.power) * value_range
        self.value = round(self.value)
        self.value = max(self.min_val, min(self.value, self.max_val))

    def draw(self, surface):
        pygame.draw.rect(surface, current_colors['slider_bg'], self.rect, border_radius=5)

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
            pygame.draw.rect(surface, current_colors['slider_handle'], filled_rect, border_radius=5)

        if self.label:
            label_surf = self.font.render(f"{self.label}: {int(self.value)}", True, current_colors['text'])
            label_rect = label_surf.get_rect(midbottom=(self.rect.centerx, self.rect.top - 8))
            surface.blit(label_surf, label_rect)

class Checkbox:
    def __init__(self, x, y, size, label, initial=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = initial
        self.label = label
        self.label_rect = None
        self.clicked = False
        try:
            self.font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        except:
            self.font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button in [1, 2, 3]:
                checkbox_clicked = self.rect.collidepoint(event.pos)
                label_clicked = self.label_rect and self.label_rect.collidepoint(event.pos)
                if checkbox_clicked or label_clicked:
                    self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.clicked:
                checkbox_clicked = self.rect.collidepoint(event.pos)
                label_clicked = self.label_rect and self.label_rect.collidepoint(event.pos)
                if checkbox_clicked or label_clicked:
                    self.checked = not self.checked
                self.clicked = False

    def draw(self, surface):
        pygame.draw.rect(surface, current_colors['checkbox_border'], self.rect, border_radius=3, width=2)
        if self.checked:
            check_margin = 4
            inner_rect = self.rect.inflate(-check_margin * 2, -check_margin * 2)
            pygame.draw.rect(surface, current_colors['checkbox_check'], inner_rect, border_radius=2)
        label_surf = self.font.render(self.label, True, current_colors['text'])
        label_rect = label_surf.get_rect()
        label_rect.left = self.rect.right + 10
        label_rect.centery = self.rect.centery + 3
        self.label_rect = label_rect
        surface.blit(label_surf, label_rect)

class ThemeSelector:
    """Класс для визуального выбора темы списком."""
    
    def __init__(self, x, y, width, current_theme_name="default"):
        self.x = x
        self.y = y
        self.width = width
        self.themes = [{"name": name, "title": data["title"]} for name, data in THEME_DEFINITIONS.items()]
        self.selected_index = 0
        self.current_theme_name = current_theme_name
        
        for i, theme in enumerate(self.themes):
            if theme["name"] == self.current_theme_name:
                self.selected_index = i
                break
                
        self.item_height = 40
        self.padding = 5
        self.preview_size = self.item_height - 2 * self.padding
        self.title_height = 30
        self.total_height = self.title_height + len(self.themes) * self.item_height + self.padding
        self.rect = pygame.Rect(x, y, width, self.total_height)
        
        try:
            self.font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
            self.title_font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM, bold=True)
        except:
            self.font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
            self.title_font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2, bold=True)
            
        self.theme_previews = self._generate_theme_previews()
        
    def _generate_theme_previews(self):
        """Генерирует маленькие иконки-превью для каждой темы, используя THEME_DEFINITIONS."""
        previews = []
        
        for theme_info in self.themes:
            theme_name = theme_info["name"]
            try:
                theme_palette = THEME_DEFINITIONS[theme_name]["palette"]
            except KeyError:
                print(f"Warning: Palette for theme '{theme_name}' not found in THEME_DEFINITIONS during preview generation. Skipping.")
                theme_palette = THEME_DEFINITIONS["default"]["palette"]
            preview = pygame.Surface((self.preview_size, self.preview_size))
            
            preview.fill(theme_palette['background'])
            
            sq_size = self.preview_size // 2
            pygame.draw.rect(preview, theme_palette['snake_head'], (0, 0, sq_size, sq_size))
            pygame.draw.rect(preview, theme_palette['snake'], (sq_size, 0, sq_size, sq_size))
            pygame.draw.rect(preview, theme_palette['food'], (0, sq_size, sq_size, sq_size))
            pygame.draw.rect(preview, theme_palette['grid'], (sq_size, sq_size, sq_size, sq_size))
            
            previews.append(preview)
        
        return previews
    
    def handle_event(self, event):
        """Обрабатывает события клика для выбора темы из списка."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            current_y = self.y + self.title_height + self.padding
            for i in range(len(self.themes)):
                item_rect = pygame.Rect(self.x, current_y, self.width, self.item_height)
                if item_rect.collidepoint(mouse_x, mouse_y):
                    self.selected_index = i
                    self.current_theme_name = self.themes[self.selected_index]["name"]
                    set_theme(self.current_theme_name)
                    self.theme_previews = self._generate_theme_previews()
                    return True
                current_y += self.item_height
        
        return False
            
    def draw(self, surface, scroll_y=0, mouse_pos=None):
        """
        Отрисовывает селектор тем в виде списка.
        
        Args:
            surface: Поверхность для отрисовки
            scroll_y: Смещение прокрутки по вертикали
            mouse_pos: Позиция курсора мыши, с учетом прокрутки (если None, используется pygame.mouse.get_pos())
        """
        title_surf = self.title_font.render("Theme Selection", True, current_colors['text_highlight'])
        title_rect = title_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top)
        surface.blit(title_surf, title_rect)
        
        current_y = self.y + self.title_height + self.padding
        
        if mouse_pos is None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_y += int(scroll_y)
        else:
            mouse_x, mouse_y = mouse_pos
        
        for i, theme in enumerate(self.themes):
            item_rect = pygame.Rect(self.x, current_y, self.width, self.item_height)
            is_hovered = item_rect.collidepoint(mouse_x, mouse_y)
            is_selected = (i == self.selected_index)
            
            if is_hovered:
                item_bg_color = current_colors['background'].lerp(pygame.Color(100,100,100), 0.1)
                pygame.draw.rect(surface, item_bg_color, item_rect, border_radius=4)
            
            preview_x = self.x + self.padding
            preview_y = current_y + self.padding
            surface.blit(self.theme_previews[i], (preview_x, preview_y))
            
            text_x = preview_x + self.preview_size + self.padding * 2
            theme_name = theme["title"]
            text_color = current_colors['text_highlight'] if is_selected else current_colors['text']
            name_surf = self.font.render(theme_name, True, text_color)
            name_rect = name_surf.get_rect(left=text_x, centery=item_rect.centery)
            surface.blit(name_surf, name_rect)
            
            if is_selected:
                pygame.draw.rect(surface, current_colors['text_highlight'], item_rect, 2, border_radius=4)
            
            current_y += self.item_height

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

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], snake_positions: List[Tuple[int, int]], is_target_food: bool = True) -> List[Tuple[int, int]]:
        """
        Находит кратчайший путь с помощью A*, УЧИТЫВАЯ движение хвоста змейки.
        Клетка считается проходимой, если к моменту достижения ее змейкой,
        сегмент хвоста, который ее занимал, уже исчезнет.
        is_target_food влияет только на то, как будет интерпретирован путь в вызывающем коде
        (например, для is_path_safe_to_food), сам поиск пути A* не меняется.
        """
        snake_length = len(snake_positions)
        # Оптимизация: Преобразование в set для быстрой проверки принадлежности
        snake_body_indices = {pos: i for i, pos in enumerate(snake_positions)}
        obstacles_set = set(snake_positions) # Для быстрой проверки статических препятствий

        open_set_heap = [(self._heuristic(start, goal), 0, start)]
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        # Множество для хранения узлов в open_set_heap для быстрой проверки
        open_set_nodes = {start} 

        while open_set_heap:
            # Извлекаем узел с наименьшей f_cost
            current_f_cost, current_g_cost, current_pos = heapq.heappop(open_set_heap)
            open_set_nodes.remove(current_pos) # Удаляем из множества

            if current_pos == goal:
                return self.reconstruct_path(came_from, goal)

            for neighbor_pos in self.get_neighbors(current_pos):
                tentative_g_cost = current_g_cost + 1

                # Проверка на столкновение с движущимся хвостом
                is_collision = False
                if neighbor_pos in snake_body_indices:
                    segment_index = snake_body_indices[neighbor_pos]
                    # Столкновение, если время достижения клетки (tentative_g_cost)
                    # меньше времени, когда хвост освободит эту клетку (snake_length - segment_index)
                    if tentative_g_cost < snake_length - segment_index:
                        is_collision = True

                # Если нет столкновения с хвостом, проверяем дальше
                if not is_collision:
                    # Проверяем, лучше ли этот путь, чем предыдущий найденный к соседу
                    if tentative_g_cost < g_score.get(neighbor_pos, float('inf')):
                        came_from[neighbor_pos] = current_pos
                        g_score[neighbor_pos] = tentative_g_cost
                        f_cost = tentative_g_cost + self._heuristic(neighbor_pos, goal)
                        # Добавляем в кучу и множество, только если его там еще нет или новый путь лучше
                        if neighbor_pos not in open_set_nodes:
                            heapq.heappush(open_set_heap, (f_cost, tentative_g_cost, neighbor_pos))
                            open_set_nodes.add(neighbor_pos)
                        # Если узел уже в куче, но мы нашли лучший путь - нужно обновить его приоритет.
                        # Прямое обновление приоритета в heapq сложно, проще добавить новый узел.
                        # Старый узел с худшим приоритетом останется, но будет извлечен позже и проигнорирован,
                        # так как g_score[neighbor_pos] уже будет обновлен на меньшее значение.
                        # (Это стандартный подход при работе с heapq без поддержки decrease-key)


        return [] # Путь не найден

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

    return positions, direction

class Snake:
    def __init__(self, mode='manual', initial_fill_percentage=0):
        self.length = 1
        initial_pos = ((GRID_WIDTH) // 2, (GRID_HEIGHT) // 2)
        self.positions: Deque[Tuple[int, int]] = deque([initial_pos])
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = current_colors['snake']
        self.mode = mode
        self.next_direction = self.direction
        self.path = []
        self.path_find = PathFind()
        self.speed = 10
        self.history: deque[Tuple[List[Tuple[int, int]], Optional[Tuple[int, int]]]] = deque(maxlen=1001)
        self.current_food_pos = None
        self.recalculate_path = True
        self.current_path: List[Tuple[int, int]] = []
        self.positions_set: set[Tuple[int, int]] = set(self.positions)
        self.survival_mode_steps_remaining = 0
        self._segments_colors_cache = []
        self._last_cache_segments = 0
        self._colors_theme_cache = current_theme
        self._neighboring_segments_cache: Dict[Tuple[int, int], Set[Tuple[int, int]]] = {}
        self.hamiltonian_path: List[Tuple[int, int]] = self._generate_hamiltonian_cycle_path()

        if initial_fill_percentage > 0:
            generated_positions, generated_direction = generate_accordion_snake(
                initial_fill_percentage, GRID_WIDTH, GRID_HEIGHT
            )
            if generated_positions:
                self.positions = generated_positions
                self.length = len(generated_positions)
                self.direction = generated_direction
                self.next_direction = generated_direction
                self.positions_set = set(self.positions)
            else:
                 print(f"Warning: Failed to generate snake for {initial_fill_percentage}%, starting with default.")
    
    def _update_colors_cache(self, num_segments):
        """Обновляет кэш цветов для сегментов змейки."""
        if (num_segments != self._last_cache_segments or 
            self._colors_theme_cache != current_theme):
            
            self._segments_colors_cache = []
            head_color = current_colors['snake_head_gradient']
            body_color = current_colors['snake']
            tail_color = current_colors['snake_tail']
            
            for i in range(1, num_segments):
                progress = (i - 1) / (num_segments - 1) if num_segments > 1 else 0
                segment_color = pygame.Color(0, 0, 0)
                
                if progress < 0.5:
                    local_progress = progress / 0.5
                    segment_color = head_color.lerp(body_color, local_progress)
                else:
                    local_progress = (progress - 0.5) / 0.5
                    segment_color = body_color.lerp(tail_color, local_progress)
                
                self._segments_colors_cache.append(segment_color)
            
            self._last_cache_segments = num_segments
            self._colors_theme_cache = current_theme
            
    def _update_neighboring_segments_cache(self):
        """Обновляет кэш соседних сегментов (оптимизированная версия)."""
        self._neighboring_segments_cache = {}
        num_segments = len(self.positions)
        if num_segments <= 1:
            return # Нет соседей для змейки из 0 или 1 сегмента

        # Используем итератор для эффективного доступа к соседним элементам
        iter_pos = iter(self.positions)

        prev_pos = None
        current_pos = next(iter_pos)
        # Пытаемся получить следующий элемент для обработки змейки > 1 сегмента
        try:
            next_pos = next(iter_pos)
            # Голова имеет только следующего соседа
            self._neighboring_segments_cache[current_pos] = {next_pos}
            prev_pos = current_pos
            current_pos = next_pos
        except StopIteration:
            # Это произойдет только если змейка состоит из 2 сегментов
            # В оригинальной версии prev_pos головы был None, а у хвоста была только голова.
            # Чтобы сохранить консистентность, второй сегмент (хвост) должен иметь соседа - голову.
            # Голова уже обработана выше.
            if prev_pos is not None: # Убедимся, что prev_pos (голова) существует
                self._neighboring_segments_cache[current_pos] = {prev_pos}
            return # Завершаем, если было всего 2 сегмента

        # Обрабатываем средние сегменты
        while True:
            try:
                next_pos = next(iter_pos)
                # Текущий сегмент имеет предыдущий и следующий
                self._neighboring_segments_cache[current_pos] = {prev_pos, next_pos}
                prev_pos = current_pos
                current_pos = next_pos
            except StopIteration: # Дошли до последнего сегмента (хвоста)
                # Последний сегмент (current_pos) имеет только предыдущего (prev_pos)
                self._neighboring_segments_cache[current_pos] = {prev_pos}
                break # Завершаем цикл

    def _update_caches(self):
        """Обновляет все кэши."""
        num_segments = len(self.positions)
        self._update_colors_cache(num_segments)
        self._update_neighboring_segments_cache()

    def draw(self, surface):
        num_segments = len(self.positions)
        if num_segments == 0:
            return

        head_pos = self.positions[0]
        draw_object(surface, current_colors['snake_head'], head_pos)

        if num_segments <= 1:
            return

        segment_positions = list(itertools.islice(self.positions, 1, None))
        for i, current_pos in enumerate(segment_positions):
            segment_color = self._segments_colors_cache[i]
            draw_object(surface, segment_color, current_pos)

        internal_border_color = current_colors['grid']
        line_width = 1
        for current_pos in self.positions:
            x, y = current_pos
            x_px, y_px = x * GRIDSIZE, y * GRIDSIZE
            neighbor_right = ((x + 1) % GRID_WIDTH, y)
            neighbor_down = (x, (y + 1) % GRID_HEIGHT)
            
            neighbors = self._neighboring_segments_cache.get(current_pos, set())
            
            if (neighbor_right in self.positions_set and 
                neighbor_right not in neighbors):
                pygame.draw.line(surface, internal_border_color,
                                (x_px + GRIDSIZE - line_width, y_px),
                                (x_px + GRIDSIZE - line_width, y_px + GRIDSIZE - 1),
                                line_width)
            
            if (neighbor_down in self.positions_set and 
                neighbor_down not in neighbors):
                pygame.draw.line(surface, internal_border_color,
                                (x_px, y_px + GRIDSIZE - line_width),
                                (x_px + GRIDSIZE - 1, y_px + GRIDSIZE - line_width),
                                line_width)

    def get_head_position(self):
        return self.positions[0]

    def turn(self,point):
        if (point[0]*-1, point[1]*-1)==self.direction:
            return
        head_x, head_y = self.positions[0]
        new_head = ((head_x + point[0]) % GRID_WIDTH, (head_y + point[1]) % GRID_HEIGHT)
        if new_head not in self.positions:
             self.next_direction = point

    def move(self, food_pos):
        """Основная функция движения: выбирает направление (если авто) и делает ход."""
        self.current_food_pos = food_pos
        collision = False
        if self.mode == 'auto':
            collision = self.auto_move(food_pos)
        else:
            collision = self.manual_move()

        if self.positions:
             self.history.append((list(self.positions), self.current_food_pos))

        return collision

    def manual_move(self):
        """Движение вперед в ручном режиме на основе self.next_direction."""
        self.direction = self.next_direction
        cur = self.get_head_position()
        x, y = self.direction
        new_head_pos = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        return self.move_forward(new_head_pos)

    def auto_move(self, food_pos):
        """Выбор направления и движение вперед в авто-режиме."""
        head = self.get_head_position()
        fill_percentage = self.length / (GRID_WIDTH * GRID_HEIGHT)
        force_survival_fill_mode = fill_percentage > 0.80 # Используем твой порог 80%

        # Флаг больше не нужен для идеального следования,
        # но оставим для обновления пути в конце
        path_calculated_for_cycle = False 

        if force_survival_fill_mode:
            # --- Режим Следования Гамильтонову Циклу (>80%) ---
            # ВСЕГДА пытаемся найти безопасный путь к циклу
            self.current_path = [] 
            self.path = []
            self.recalculate_path = False
            self.survival_mode_steps_remaining = 0

            try:
                head_index = self.hamiltonian_path.index(head)
                path_found_on_cycle = False
                for lookahead_steps in [1, 2]: # Пробуем +1 и +2 шага
                    target_index = (head_index + lookahead_steps) % len(self.hamiltonian_path)
                    target_cell = self.hamiltonian_path[target_index]
                    path_to_cycle_target = self.path_find.find_path(head, target_cell, list(self.positions), is_target_food=False)

                    # ВСЕГДА проверяем безопасность пути к цели
                    if path_to_cycle_target and self._is_path_to_target_safe(path_to_cycle_target):
                        self.current_path = path_to_cycle_target
                        self.path = path_to_cycle_target
                        if len(self.current_path) > 1:
                            # Расчет направления (как было)
                            next_step = self.current_path[1]
                            dx = next_step[0] - head[0]; dy = next_step[1] - head[1]
                            if abs(dx) > GRID_WIDTH / 2: dx = - (GRID_WIDTH - abs(dx)) * (1 if dx > 0 else -1)
                            if abs(dy) > GRID_HEIGHT / 2: dy = - (GRID_HEIGHT - abs(dy)) * (1 if dy > 0 else -1)
                            if dx != 0: dx = dx // abs(dx); dy = 0
                            elif dy != 0: dy = dy // abs(dy); dx = 0
                            else: dx, dy = self.direction
                            self.next_direction = (dx, dy)

                            calc_next_pos = ((head[0] + dx) % GRID_WIDTH, (head[1] + dy) % GRID_HEIGHT)
                            if calc_next_pos != next_step:
                                print(f"WARN: Cycle Direction mismatch! Head:{head}, Next:{next_step}, Dir:{self.next_direction}")
                                self.next_direction = self._find_standard_survival_move() or self.direction
                                path_calculated_for_cycle = False
                            else:
                                path_calculated_for_cycle = True # Путь рассчитан (хоть и не идеальный)
                                path_found_on_cycle = True
                                break # Нашли безопасный путь
                        else:
                            self.next_direction = self._find_standard_survival_move() or self.direction
                            path_calculated_for_cycle = False
                            break # Странный путь

                if not path_found_on_cycle: # Не нашли безопасный путь ни к +1, ни к +2
                    self.next_direction = self._find_standard_survival_move() or self.direction
                    path_calculated_for_cycle = False

            except ValueError: # Голова не на цикле
                print(f"WARN: Head {head} not on Hamiltonian cycle during >80% mode!")
                self.next_direction = self._find_standard_survival_move() or self.direction
                path_calculated_for_cycle = False

        else:
            # --- Стандартный режим (<80%) ---
            # ... (логика без изменений) ...
             if self.survival_mode_steps_remaining > 0:
                 self.survival_mode_steps_remaining -= 1
                 survival_direction = self._find_standard_survival_move()
                 if not survival_direction: survival_direction = self.find_immediate_safe_direction()
                 self.next_direction = survival_direction or self.direction
                 self.current_path = []; self.path = []; self.recalculate_path = False
             else:
                 if self.recalculate_path or not self.current_path:
                      path_to_food = self.path_find.find_path(head, food_pos, list(self.positions), is_target_food=True)
                      if path_to_food and self.is_path_safe_to_food(path_to_food):
                          self.current_path = path_to_food; self.path = self.current_path; self.recalculate_path = False
                          if len(self.current_path) > 1: self.next_direction = self.get_direction_to(self.current_path[1])
                          else: self.next_direction = self._find_standard_survival_move() or self.direction; self.recalculate_path = True; self.current_path = []; self.path = []
                      else:
                          self.current_path = []; self.path = []
                          survival_direction = self._find_standard_survival_move()
                          if survival_direction:
                              self.next_direction = survival_direction; self.survival_mode_steps_remaining = SURVIVAL_MODE_DURATION; self.recalculate_path = False
                          else:
                              self.next_direction = self.find_immediate_safe_direction() or self.direction; self.recalculate_path = True
                 else:
                      if len(self.current_path) > 1: self.next_direction = self.get_direction_to(self.current_path[1])
                      else: self.recalculate_path = True; self.current_path = []; self.path = []; self.next_direction = self._find_standard_survival_move() or self.direction


        # --- Общее для всех режимов: Движение ---
        self.direction = self.next_direction
        cur = self.get_head_position() 
        x, y = self.direction
        new_head_pos = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        collision = self.move_forward(new_head_pos)

        # --- Обновление пути (если это был НЕ путь по циклу) ---
        if not path_calculated_for_cycle and self.survival_mode_steps_remaining == 0 and not self.recalculate_path and self.current_path and not collision:
             if self.current_path and self.current_path[0] == cur:
                 self.current_path.pop(0)
             elif self.recalculate_path is False:
                 self.recalculate_path = True
                 self.current_path = []; self.path = []

        return collision

    def move_forward(self, new_head_pos):
        """Обновляет позицию змейки: добавляет голову, удаляет хвост (если не растет), проверяет коллизии."""
        collision = False
        tail_pos = self.positions[-1] if len(self.positions) > 0 else None
        
        grows = (new_head_pos == self.current_food_pos)
        structure_changed = grows
        if not grows and self.positions:
             removed_tail = self.positions[-1]
             if removed_tail != new_head_pos:
                 structure_changed = True
        elif not self.positions:
             structure_changed = True
        
        if new_head_pos in self.positions_set and new_head_pos != tail_pos:
             collision = True

        history_positions = list(self.positions)
        history_food_pos = self.current_food_pos

        self.positions_set.add(new_head_pos)
        self.positions.appendleft(new_head_pos)

        if not grows:
            if self.positions:
                removed_tail = self.positions.pop()
                if removed_tail in self.positions_set:
                     if removed_tail not in self.positions:
                           self.positions_set.remove(removed_tail)
        elif grows:
             self.length += 1
             self.survival_mode_steps_remaining = 0
             self.recalculate_path = True
             self.current_path = []
             self.path = []

        self.history.append((history_positions, history_food_pos))
        
        if structure_changed:
            self._update_caches()

        return collision

    def get_direction_to(self, position):
        """Определяет направление (UP/DOWN/LEFT/RIGHT) от головы змейки к цели, учитывая 'зацикленность' поля."""
        head_x, head_y = self.get_head_position()
        pos_x, pos_y = position

        dx = pos_x - head_x
        if abs(dx) > GRID_WIDTH / 2:
            sign = 1 if dx > 0 else -1
            dx = - (GRID_WIDTH - abs(dx)) * sign

        dy = pos_y - head_y
        if abs(dy) > GRID_HEIGHT / 2:
            sign = 1 if dy > 0 else -1
            dy = - (GRID_HEIGHT - abs(dy)) * sign

        if abs(dx) > abs(dy):
            return RIGHT if dx > 0 else LEFT
        elif abs(dy) > abs(dx):
            return DOWN if dy > 0 else UP
        else:
            if dx != 0:
                 return RIGHT if dx > 0 else LEFT
            elif dy != 0:
                 return DOWN if dy > 0 else UP
            else:
                 return self.direction

    def find_immediate_safe_direction(self):
        """Находит любое направление, которое не ведет к немедленной смерти (столкновению с телом)."""
        head = self.get_head_position()
        possible_directions = [UP, DOWN, LEFT, RIGHT]
        random.shuffle(possible_directions)

        for d in possible_directions:
            next_pos = ((head[0] + d[0]) % GRID_WIDTH, (head[1] + d[1]) % GRID_HEIGHT)
            if next_pos not in self.positions:
                return d

        if len(self.positions) > 1:
            tail_pos = self.positions[-1]
            for d in possible_directions:
                next_pos = ((head[0] + d[0]) % GRID_WIDTH, (head[1] + d[1]) % GRID_HEIGHT)
                if next_pos == tail_pos:
                    return d

        return None

    def _get_all_empty_cells(self, obstacles: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Возвращает множество всех пустых клеток на поле."""
        # Можно оптимизировать, кэшируя all_cells, если GRID_WIDTH/HEIGHT не меняются
        all_cells = set((x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT))
        return all_cells - obstacles

    def _calculate_fragmentation_score(self, obstacles: Set[Tuple[int, int]]) -> int:
        """
        Вычисляет 'счет фрагментации' - количество несвязанных регионов пустых клеток.
        Меньше -> лучше. Использует BFS для обхода.
        """
        empty_cells = self._get_all_empty_cells(obstacles)
        if not empty_cells:
            return 0 # Нет пустых клеток - нет фрагментации

        visited_overall = set()
        region_count = 0

        # Продолжаем, пока не посетим все пустые клетки
        while len(visited_overall) < len(empty_cells):
            region_count += 1
            # Находим стартовую клетку для нового региона (любую не посещенную)
            try:
                 # iter(empty_cells - visited_overall) создает итератор по разности множеств
                 start_node = next(iter(empty_cells - visited_overall))
            except StopIteration:
                 # Этого не должно произойти, если while условие верно, но для безопасности
                 break 

            # Запускаем BFS для поиска всех клеток в текущем регионе
            q = deque([start_node])
            visited_overall.add(start_node) # Отмечаем как посещенную глобально

            while q:
                current_pos = q.popleft()
                # Проверяем соседей
                for neighbor_pos in self.path_find.get_neighbors(current_pos):
                    # Сосед должен быть пустым и еще не посещенным глобально
                    if neighbor_pos in empty_cells and neighbor_pos not in visited_overall:
                        visited_overall.add(neighbor_pos)
                        q.append(neighbor_pos)
                        
        # Возвращаем количество найденных регионов
        return region_count

    def _find_standard_survival_move(self) -> Tuple[int, int] | None:
        """
        Стандартный режим выживания:
        1. Максимизирует достижимую пустую область от головы.
        2. При равенстве областей, максимизирует путь до хвоста.
        3. Если все эвристики равны, выбирает случайно из лучших.
        """
        candidate_directions_data = {} # direction -> (freedom, tail_path_len)
        max_freedom = -1

        head = self.get_head_position()
        possible_directions = []
        current_positions_set = self.positions_set
        tail_pos = self.positions[-1] if len(self.positions) > 1 else None
        for d in [UP, DOWN, LEFT, RIGHT]:
            if len(self.positions) > 1 and d == (self.direction[0] * -1, self.direction[1] * -1): continue
            next_head = ((head[0] + d[0]) % GRID_WIDTH, (head[1] + d[1]) % GRID_HEIGHT)
            is_collision = next_head in current_positions_set and next_head != tail_pos
            if not is_collision: possible_directions.append(d)

        if not possible_directions:
             for d in [UP, DOWN, LEFT, RIGHT]:
                 if len(self.positions) > 1 and d == (self.direction[0] * -1, self.direction[1] * -1): continue
                 next_head = ((head[0] + d[0]) % GRID_WIDTH, (head[1] + d[1]) % GRID_HEIGHT)
                 if next_head == tail_pos: return d
             return None
        if len(possible_directions) == 1: return possible_directions[0]

        current_positions_list = list(self.positions)
        safe_directions_after_sim = set(possible_directions) # Начнем со всех возможных

        for direction in possible_directions:
            next_head = ((head[0] + direction[0]) % GRID_WIDTH, (head[1] + direction[1]) % GRID_HEIGHT)
            sim_snake_list = self.simulate_move([head, next_head], grows=False, initial_state=current_positions_list)
            if sim_snake_list is None:
                safe_directions_after_sim.discard(direction)
                continue

            sim_head = sim_snake_list[0]
            sim_obstacles = set(sim_snake_list)
            freedom = self._calculate_reachable_empty_space(sim_head, sim_obstacles)

            if freedom >= max_freedom:
                sim_tail = sim_snake_list[-1]
                path_to_tail = self.path_find.find_path(sim_head, sim_tail, sim_snake_list, is_target_food=False) # Цель - хвост, не еда
                tail_path_len = len(path_to_tail) if path_to_tail else 0

                if freedom > max_freedom:
                     max_freedom = freedom
                candidate_directions_data[direction] = (freedom, tail_path_len)

        # --- Фильтрация кандидатов ---
        # Убираем направления, которые симуляция посчитала небезопасными
        valid_candidates = {d: data for d, data in candidate_directions_data.items() if d in safe_directions_after_sim}

        if not valid_candidates:
             return random.choice(list(safe_directions_after_sim)) if safe_directions_after_sim else (self.find_immediate_safe_direction() or self.direction)

        # Оставляем только тех, у кого максимальный freedom
        current_max_freedom = -1
        for free, _ in valid_candidates.values():
             if free > current_max_freedom: current_max_freedom = free
        best_freedom_candidates = {d: data for d, data in valid_candidates.items() if data[0] == current_max_freedom}

        if not best_freedom_candidates: return random.choice(list(safe_directions_after_sim)) if safe_directions_after_sim else (self.find_immediate_safe_direction() or self.direction)
        if len(best_freedom_candidates) == 1: return list(best_freedom_candidates.keys())[0]

        # Фильтруем по максимальной длине пути до хвоста
        max_tail_len = -1
        for _, tail_len in best_freedom_candidates.values():
             if tail_len > max_tail_len: max_tail_len = tail_len
        best_tail_len_candidates = {d: data for d, data in best_freedom_candidates.items() if data[1] == max_tail_len}

        # --- Финальный случайный выбор ---
        final_choices = list(best_tail_len_candidates.keys())
        return random.choice(final_choices) if final_choices else (self.find_immediate_safe_direction() or self.direction)

    def _is_path_to_target_safe(self, path_to_target: List[Tuple[int, int]]) -> bool:
         """Проверяет, безопасен ли путь к ЦЕЛИ (не еде)."""
         if not path_to_target: return False
         sim_snake_after_reach = self.simulate_move(path_to_target, grows=False, initial_state=list(self.positions))
         if sim_snake_after_reach:
             sim_head = sim_snake_after_reach[0]
             sim_tail = sim_snake_after_reach[-1]
             path_to_tail_after_reach = self.path_find.find_path(sim_head, sim_tail, sim_snake_after_reach, is_target_food=False)
             return bool(path_to_tail_after_reach)
         return False

    def _find_empty_regions(self, obstacles: Set[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
        """Находит все несвязанные регионы пустых клеток."""
        empty_cells = self._get_all_empty_cells(obstacles)
        if not empty_cells:
            return []

        visited_overall = set()
        regions = []

        while len(visited_overall) < len(empty_cells):
            current_region = []
            # Находим стартовую клетку для нового региона
            try:
                 start_node = next(iter(empty_cells - visited_overall))
            except StopIteration:
                 break

            q = deque([start_node])
            visited_overall.add(start_node)
            current_region.append(start_node)

            while q:
                current_pos = q.popleft()
                for neighbor_pos in self.path_find.get_neighbors(current_pos):
                    if neighbor_pos in empty_cells and neighbor_pos not in visited_overall:
                        visited_overall.add(neighbor_pos)
                        q.append(neighbor_pos)
                        current_region.append(neighbor_pos)

            if current_region:
                regions.append(current_region)

        return regions

    def _find_closest_cell_in_region(self, start_pos: Tuple[int, int], region_cells: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Находит ближайшую клетку из region_cells к start_pos с помощью BFS."""
        if not region_cells: return None
        region_set = set(region_cells) # Для быстрой проверки принадлежности
        q = deque([(start_pos, 0)]) # (position, distance)
        visited = {start_pos}

        while q:
            current_pos, dist = q.popleft()

            if current_pos in region_set:
                return current_pos # Нашли первую (ближайшую)

            # Ищем соседей, не являющихся препятствиями (в данном контексте препятствия - это тело змеи)
            for neighbor_pos in self.path_find.get_neighbors(current_pos):
                # Не проверяем на столкновение с хвостом здесь, только базовый BFS
                if neighbor_pos not in self.positions_set and neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    q.append((neighbor_pos, dist + 1))
                # Если сосед - это искомая клетка региона
                elif neighbor_pos in region_set and neighbor_pos not in visited:
                     return neighbor_pos # Нашли ближайшего соседа в регионе

        # Если BFS завершился, а клетка не найдена (маловероятно, если регион существует)
        return None # Или можно вернуть случайную из региона? Пока None

    def is_path_safe_to_food(self, path_to_food: List[Tuple[int, int]]) -> bool:
        """
        Проверяет, является ли путь к еде "безопасным":
        оставляет ли он возможность добраться до хвоста ПОСЛЕ поедания еды.
        Это помогает избегать ситуаций, когда змейка съедает еду и запирает сама себя.
        """
        if not path_to_food or len(path_to_food) <= 1:
            return False

        current_positions_list = list(self.positions)

        sim_snake_after_eat = self.simulate_move(path_to_food, grows=True, initial_state=current_positions_list)

        if sim_snake_after_eat is None:
            return False

        sim_head = sim_snake_after_eat[0]
        sim_tail = sim_snake_after_eat[-1]
        path_to_tail_after_eat = self.path_find.find_path(sim_head, sim_tail, sim_snake_after_eat)

        return bool(path_to_tail_after_eat)

    def simulate_move(self, path: List[Tuple[int, int]], grows: bool, initial_state: List[Tuple[int, int]] | None = None) -> List[Tuple[int, int]] | None:
        """
        Симулирует движение змейки по заданному пути.
        Возвращает новое состояние змейки (список координат) или None, если путь ведет к самопересечению.
        `grows`: True, если последний шаг пути - это поедание еды (хвост не удаляется).
        `initial_state`: Опциональное начальное состояние (список) для симуляции.
        """
        if not path or len(path) <= 1:
            return list(self.positions) if initial_state is None else initial_state

        sim_snake = deque(initial_state if initial_state is not None else self.positions)
        current_path = path[1:]

        for i, step in enumerate(current_path):
            if len(sim_snake) > 1 and step in itertools.islice(sim_snake, 0, len(sim_snake) - 1):
                 return None

            sim_snake.appendleft(step)

            is_last_step = (i == len(current_path) - 1)
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
        self.positions_set = set(self.positions)
        self.survival_mode_steps_remaining = 0

        if initial_fill_percentage > 0:
            generated_positions, generated_direction = generate_accordion_snake(
                initial_fill_percentage, GRID_WIDTH, GRID_HEIGHT
            )
            if generated_positions:
                self.positions = generated_positions
                self.length = len(generated_positions)
                self.direction = generated_direction
                self.next_direction = generated_direction
                self.positions_set = set(self.positions)
            else:
                 print(f"Warning: Failed to generate snake for {initial_fill_percentage}%, starting with default.")

        self._update_caches()

    def _calculate_reachable_empty_space(self, start_pos: Tuple[int, int], obstacles: Set[Tuple[int, int]]) -> int:
        """
        Вычисляет количество достижимых пустых клеток от start_pos с помощью BFS,
        избегая клеток из obstacles.
        """
        if start_pos in obstacles:
            return 0

        q = deque([start_pos])
        visited = {start_pos}
        count = 0

        while q:
            current_pos = q.popleft()
            count += 1

            # Используем существующий метод get_neighbors из PathFind
            for neighbor_pos in self.path_find.get_neighbors(current_pos):
                if neighbor_pos not in obstacles and neighbor_pos not in visited:
                    visited.add(neighbor_pos)
                    q.append(neighbor_pos)
        return count

    def _generate_hamiltonian_cycle_path(self) -> List[Tuple[int, int]]:
        """Генерирует простой змеевидный Гамильтонов цикл для всего поля."""
        path = []
        for y in range(GRID_HEIGHT):
            if y % 2 == 0: # Двигаемся вправо
                for x in range(GRID_WIDTH):
                    path.append((x, y))
            else: # Двигаемся влево
                for x in range(GRID_WIDTH - 1, -1, -1):
                    path.append((x, y))
        print(f"Generated Hamiltonian cycle with {len(path)} steps.") # Отладка
        return path

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = current_colors['food']  # Сохраняем атрибут color
        self.randomize_position([])

    def randomize_position(self, snake_positions: List[Tuple[int, int]] | Deque[Tuple[int, int]]):
        # Проверка на полное заполнение поля
        occupied = set(snake_positions)
        fill_percentage = len(occupied) / (GRID_WIDTH * GRID_HEIGHT)
        
        # Защита от ошибки: если все клетки заняты, не пытаемся найти позицию
        if len(occupied) >= GRID_WIDTH * GRID_HEIGHT:
            print("Все клетки заняты, победа!")
            return
        
        if len(snake_positions) >= GRID_WIDTH * GRID_HEIGHT - 1:
            # Осталась только одна клетка - последняя еда
            try:
                self.position = next(pos for pos in 
                                  ((x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT))
                                  if pos not in occupied)
            except StopIteration:
                print("Не удалось найти свободную клетку, хотя должна быть одна.")
                # В крайнем случае устанавливаем любую позицию
                self.position = (0, 0)
            return
        
        # При высоком заполнении (>90%) сразу переходим к последовательному поиску
        if fill_percentage > 0.9:
            self._find_sequential(occupied)
            return
            
        # Ограничиваем количество попыток найти свободную клетку
        # Уменьшаем число попыток при высоком заполнении
        max_attempts = max(100, int(1000 * (1 - fill_percentage)))
        attempts = 0
        
        while attempts < max_attempts:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in occupied:
                return
            attempts += 1
            
        # Если после max_attempts не удалось найти случайную позицию, 
        # находим первую свободную клетку последовательным перебором
        self._find_sequential(occupied)
    
    def _find_sequential(self, occupied: Set[Tuple[int, int]]):
        """Оптимизированный последовательный поиск свободной клетки."""
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pos = (x, y)
                if pos not in occupied:
                    self.position = pos
                    return

    def draw(self, surface):
        draw_object(surface, self.color, self.position)

class StatsCache(TypedDict):
    snake_length: Optional[int]
    current_speed: Optional[int]
    area_surf: Optional[Surface]
    speed_surf: Optional[Surface]
    font: Optional[Font]

stats_cache: StatsCache = {
    "snake_length": None, "current_speed": None,
    "area_surf": None, "speed_surf": None,
    "font": None
}

def display_statistics(surface, snake_length, current_speed):
    global stats_cache

    if stats_cache["font"] is None:
        try:
            stats_cache["font"] = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        except:
            stats_cache["font"] = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
    font = stats_cache["font"]

    y_offset = 10
    texts_to_render = []

    if snake_length != stats_cache["snake_length"] or stats_cache["area_surf"] is None:
        stats_cache["snake_length"] = snake_length
        area_percentage = (snake_length / (GRID_WIDTH * GRID_HEIGHT)) * 100
        stats_cache["area_surf"] = font.render(f'Area: {area_percentage:.1f}%', True, current_colors['text_white'])
    texts_to_render.append(stats_cache["area_surf"])

    rounded_speed = int(current_speed)
    if rounded_speed != stats_cache["current_speed"] or stats_cache["speed_surf"] is None:
        stats_cache["current_speed"] = rounded_speed
        stats_cache["speed_surf"] = font.render(f'Speed: {rounded_speed}', True, current_colors['text_white'])
    texts_to_render.append(stats_cache["speed_surf"])

    for text_surf in texts_to_render:
        text_rect = text_surf.get_rect(topleft=(15, y_offset))
        surface.blit(text_surf, text_rect)
        y_offset += font.get_height() + 2

def button_animation(surface, button, color, text):
    button_rect = pygame.Rect(button)
    start_time = pygame.time.get_ticks()
    duration = 200

    while pygame.time.get_ticks() - start_time < duration:
        elapsed = pygame.time.get_ticks() - start_time
        progress = elapsed / duration

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(int(150 * progress))
        overlay.fill(current_colors['background'])
        surface.blit(overlay, (0,0))

        current_button_color = color.lerp(current_colors['background'], 0.3)
        draw_button(surface, button_rect, current_button_color, text, False, True)

        pygame.display.update(button_rect)
        pygame.time.Clock().tick(60)

def replay_screen(surface, clock, history: deque):
    """Экран перемотки последних ходов после Game Over."""
    if not history:
        return False

    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE, bold=True)
        font_info = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2, bold=True)
        font_info = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    title_surf = font_title.render("Game Replay", True, current_colors['text_highlight'])
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 40))

    history_len = len(history)
    max_replay_index = history_len - 1
    replay_index = max_replay_index

    button_width = 180
    button_height = 50
    slider_height = 20
    slider_y = SCREEN_HEIGHT - 100
    button_y = slider_y + slider_height + 40

    retry_button_center_x = SCREEN_WIDTH // 3
    quit_button_center_x = SCREEN_WIDTH * 2 // 3
    slider_x = retry_button_center_x - button_width // 2
    slider_width = quit_button_center_x + button_width // 2 - slider_x

    replay_slider = Slider(slider_x, slider_y, slider_width, slider_height,
                           0, max_replay_index, replay_index, f"Step: {replay_index+1}/{history_len}")

    retry_button_rect = pygame.Rect(0, 0, button_width, button_height)
    quit_button_rect = pygame.Rect(0, 0, button_width, button_height)
    retry_button_rect.center = (retry_button_center_x, button_y)
    quit_button_rect.center = (quit_button_center_x, button_y)

    retry_clicked = False
    main_menu_clicked = False

    replay_snake = Snake()
    replay_food = Food()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        is_retry_hovered = retry_button_rect.collidepoint(mouse_pos)
        is_main_menu_hovered = quit_button_rect.collidepoint(mouse_pos)
        is_retry_clicked = retry_clicked
        is_main_menu_clicked = main_menu_clicked

        prev_replay_index = replay_index

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if confirmation_dialog(surface, clock, "Quit Game?"):
                    pygame.quit()
                    sys.exit()

            replay_slider.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    replay_index = max(0, replay_index - 1)
                elif event.key == pygame.K_RIGHT:
                    replay_index = min(max_replay_index, replay_index + 1)
                elif event.key == pygame.K_HOME:
                     replay_index = 0
                elif event.key == pygame.K_END:
                     replay_index = max_replay_index
                replay_slider.value = replay_index
                replay_slider.update_handle_pos()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Проверяем, что это именно кнопка мыши, а не колесико
                if event.button in [1, 2, 3]:  # Левая, средняя или правая кнопка мыши
                    if is_retry_hovered:
                        retry_clicked = True
                    elif is_main_menu_hovered:
                        main_menu_clicked = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if retry_clicked and is_retry_hovered:
                    if eat_sound: eat_sound.play()
                    return True
                elif main_menu_clicked and is_main_menu_hovered:
                    if eat_sound:
                        eat_sound.play()
                    return False
                retry_clicked = False
                main_menu_clicked = False

        slider_index = int(replay_slider.value)
        if slider_index != replay_index:
            replay_index = slider_index

        if replay_index != prev_replay_index:
             replay_slider.label = f"Step: {replay_index+1}/{history_len}"

        current_snake_positions_list, current_food_pos = history[replay_index]
        replay_snake.positions = deque(current_snake_positions_list)
        replay_snake.positions_set = set(replay_snake.positions)
        replay_snake._update_caches()
        replay_food.position = current_food_pos if current_food_pos else (-1, -1)

        surface.fill(current_colors['background'])
        draw_grid(surface)
        surface.blit(title_surf, title_rect)

        replay_snake.draw(surface)
        if replay_food.position != (-1, -1):
             replay_food.draw(surface)

        replay_slider.draw(surface)
        draw_button(surface, retry_button_rect, current_colors['button'], "Retry Game", is_retry_hovered, is_retry_clicked)
        draw_button(surface, quit_button_rect, current_colors['button'], "Main Menu", is_main_menu_hovered, is_main_menu_clicked)

        pygame.display.update()
        clock.tick(60) # Высокий FPS для экрана повтора чтобы UI был отзывчивым

def game_over_screen(surface, clock, snake_length, current_speed, history: deque):
    """Экран Game Over теперь просто вызывает replay_screen."""
    return replay_screen(surface, clock, history)

def settings_screen(surface, clock, current_speed, current_volume, mute, current_fill_percent, current_show_path, current_theme="default", current_max_fps=60) -> Tuple[int, int, bool, int, bool, str, int]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    title_surf = font_title.render("Settings", True, current_colors['text_white'])
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))

    slider_width = 350
    slider_height = 25
    checkbox_size = 25
    widget_x = SCREEN_WIDTH // 2 - slider_width // 2
    y_pos = title_rect.bottom + 50

    speed_slider = Slider(widget_x, y_pos, slider_width, slider_height, 5, 99999, current_speed, "Game Speed (LPS)", power=5)
    y_pos += 70

    max_fps_slider = Slider(widget_x, y_pos, slider_width, slider_height, 15, 240, current_max_fps, "Max Render FPS")
    y_pos += 70

    volume_slider = Slider(widget_x, y_pos, slider_width, slider_height, 0, 100, current_volume, "Sound Volume")
    y_pos += 70

    fill_slider = Slider(widget_x, y_pos, slider_width, slider_height, 0, 95, current_fill_percent, "Initial Fill (%)")
    y_pos += 70

    mute_checkbox = Checkbox(widget_x, y_pos, checkbox_size, "Mute Sound", mute)
    y_pos += 45

    show_path_checkbox = Checkbox(widget_x, y_pos, checkbox_size, "Show AI Path", current_show_path)
    y_pos += 45

    theme_selector = ThemeSelector(widget_x, y_pos, slider_width, current_theme_name=current_theme)
    y_pos += theme_selector.total_height + 40

    button_width = 120
    button_height = 55
    button_spacing = 20
    reset_button_rect = pygame.Rect(0, 0, button_width, button_height)
    apply_button_rect = pygame.Rect(0, 0, button_width, button_height)
    back_button_rect = pygame.Rect(0, 0, button_width, button_height)

    total_width = 3 * button_width + 2 * button_spacing
    reset_button_rect.topleft = (SCREEN_WIDTH // 2 - total_width // 2, y_pos)
    apply_button_rect.topleft = (reset_button_rect.right + button_spacing, y_pos)
    back_button_rect.topleft = (apply_button_rect.right + button_spacing, y_pos)

    scroll_y = 0
    content_height = y_pos + button_height + 40
    view_height = SCREEN_HEIGHT
    scrollbar_width = 15
    scrollbar_margin = 5
    scrollbar_x = SCREEN_WIDTH - scrollbar_width - scrollbar_margin
    scrollbar_rect = pygame.Rect(scrollbar_x, scrollbar_margin, scrollbar_width, 0)
    scrollbar_handle_rect = pygame.Rect(scrollbar_x, scrollbar_margin, scrollbar_width, 0)
    dragging_scrollbar = False
    drag_start_y = 0

    reset_clicked = False
    apply_clicked = False
    back_clicked = False
    
    notification_active = False
    notification_text = ""
    notification_timer = 0
    notification_duration = 2000
    notification_alpha = 0

    original_speed = current_speed
    original_volume = current_volume
    original_mute = mute
    original_fill_percent = current_fill_percent
    original_show_path = current_show_path
    original_theme = current_theme
    original_max_fps = current_max_fps
    
    settings_just_applied = False

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        scroll_mouse_pos = (mouse_pos[0], mouse_pos[1] + scroll_y)
        
        if content_height > view_height:
            scrollbar_height = int(view_height - 2 * scrollbar_margin)
            handle_height = int(max(20, round(scrollbar_height * (view_height / content_height))))
            scroll_ratio = scroll_y / (content_height - view_height) if content_height > view_height else 0
            handle_y = int(scrollbar_margin + int(scroll_ratio * (scrollbar_height - handle_height)))
            
            scrollbar_rect = pygame.Rect(int(scrollbar_x), int(scrollbar_margin), int(scrollbar_width), scrollbar_height)
            scrollbar_handle_rect = pygame.Rect(int(scrollbar_x), handle_y, int(scrollbar_width), handle_height)
        else:
            scrollbar_rect = pygame.Rect(int(scrollbar_x), int(scrollbar_margin), int(scrollbar_width), 0)
            scrollbar_handle_rect = pygame.Rect(int(scrollbar_x), int(scrollbar_margin), int(scrollbar_width), 0)

        is_back_hovered = back_button_rect.collidepoint(scroll_mouse_pos)
        is_back_clicked = back_clicked
        is_apply_hovered = apply_button_rect.collidepoint(scroll_mouse_pos)
        is_apply_clicked = apply_clicked
        is_reset_hovered = reset_button_rect.collidepoint(scroll_mouse_pos)
        is_reset_clicked = reset_clicked

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if confirmation_dialog(surface, clock, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1, 2, 3]:
                    if scrollbar_handle_rect.height > 0 and scrollbar_handle_rect.collidepoint(mouse_pos):
                        dragging_scrollbar = True
                        drag_start_y = mouse_pos[1]
                    elif is_back_hovered:
                        back_clicked = True
                    elif is_apply_hovered:
                        apply_clicked = True
                    elif is_reset_hovered:
                        reset_clicked = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if back_clicked and is_back_hovered:
                    if eat_sound:
                        eat_sound.play()

                    selected_speed = speed_slider.value
                    selected_volume = volume_slider.value
                    is_muted = mute_checkbox.checked
                    selected_fill_percent = fill_slider.value
                    should_show_path = show_path_checkbox.checked
                    selected_theme = theme_selector.current_theme_name
                    selected_max_fps = max_fps_slider.value

                    settings_changed = (
                        selected_speed != original_speed or
                        selected_volume != original_volume or
                        is_muted != original_mute or
                        selected_fill_percent != original_fill_percent or
                        should_show_path != original_show_path or
                        selected_theme != original_theme or
                        selected_max_fps != original_max_fps
                    )

                    if settings_changed and not settings_just_applied:
                        dialog_result = unsaved_settings_dialog(surface, clock)

                        if dialog_result == "save":
                            original_speed = selected_speed
                            original_volume = selected_volume
                            original_mute = is_muted
                            original_fill_percent = selected_fill_percent
                            original_show_path = should_show_path
                            original_theme = selected_theme
                            original_max_fps = selected_max_fps

                            if eat_sound:
                                eat_sound.set_volume(0 if is_muted else selected_volume / 100)

                            running = False
                        elif dialog_result == "discard":
                            set_theme(original_theme)
                            if eat_sound:
                                eat_sound.set_volume(0 if original_mute else original_volume / 100)
                            running = False
                    else:
                        set_theme(original_theme)
                        if eat_sound:
                            eat_sound.set_volume(0 if original_mute else original_volume / 100)
                        running = False
                elif apply_clicked and is_apply_hovered:
                    if eat_sound:
                        eat_sound.play()
                    
                    current_speed = speed_slider.value
                    current_volume = volume_slider.value
                    mute = mute_checkbox.checked
                    current_fill_percent = fill_slider.value
                    current_show_path = show_path_checkbox.checked
                    current_theme = theme_selector.current_theme_name
                    current_max_fps = max_fps_slider.value
                    
                    original_speed = current_speed
                    original_volume = current_volume
                    original_mute = mute
                    original_fill_percent = current_fill_percent
                    original_show_path = current_show_path
                    original_theme = current_theme
                    original_max_fps = current_max_fps
                    
                    if eat_sound:
                        eat_sound.set_volume(0 if mute else current_volume / 100)
                        
                    notification_active = True
                    notification_text = "Settings Applied!"
                    notification_timer = pygame.time.get_ticks()
                    notification_alpha = 0
                    
                    settings_just_applied = True
                        
                elif reset_clicked and is_reset_hovered:
                    if eat_sound:
                        eat_sound.play()
                    selected_speed = 15
                    selected_volume = 1
                    is_muted = False
                    selected_fill_percent = 0
                    should_show_path = False
                    selected_theme = "default"
                    selected_max_fps = 60
                    
                    theme_selector.current_theme_name = selected_theme
                    for i, theme in enumerate(theme_selector.themes):
                        if theme["name"] == selected_theme:
                            theme_selector.selected_index = i
                            break
                    set_theme(selected_theme)
                    
                    scroll_y = 0
                    
                    speed_slider.value = selected_speed
                    speed_slider.update_handle_pos()
                    volume_slider.value = selected_volume
                    volume_slider.update_handle_pos()
                    fill_slider.value = selected_fill_percent
                    fill_slider.update_handle_pos()
                    mute_checkbox.checked = is_muted
                    show_path_checkbox.checked = should_show_path
                    max_fps_slider.value = selected_max_fps
                    max_fps_slider.update_handle_pos()
                    
                    if eat_sound:
                        eat_sound.set_volume(0 if is_muted else selected_volume / 100)
                dragging_scrollbar = False
                back_clicked = False
                apply_clicked = False
                reset_clicked = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_scrollbar:
                    delta_y = mouse_pos[1] - drag_start_y
                    max_scroll_handle_y = scrollbar_rect.height - scrollbar_handle_rect.height
                    handle_y = scrollbar_margin + scroll_ratio * max_scroll_handle_y + delta_y
                    handle_y = max(scrollbar_margin, min(handle_y, scrollbar_margin + max_scroll_handle_y))
                    
                    if max_scroll_handle_y > 0:
                        new_scroll_ratio = (handle_y - scrollbar_margin) / max_scroll_handle_y
                        scroll_y = new_scroll_ratio * (content_height - view_height)
                        scroll_y = max(0, min(scroll_y, content_height - view_height))
                    drag_start_y = mouse_pos[1]
            elif event.type == pygame.MOUSEWHEEL:
                if content_height > view_height:
                    scroll_y -= event.y * 30
                    scroll_y = max(0, min(scroll_y, content_height - view_height))
            
            adjusted_event = event
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                adjusted_event = pygame.event.Event(event.type, {'pos': scroll_mouse_pos, 'button': event.button if hasattr(event, 'button') else 1})
            
            speed_slider.handle_event(adjusted_event)
            volume_slider.handle_event(adjusted_event)
            fill_slider.handle_event(adjusted_event)
            mute_checkbox.handle_event(adjusted_event)
            show_path_checkbox.handle_event(adjusted_event)
            max_fps_slider.handle_event(adjusted_event)

            theme_selector.handle_event(adjusted_event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selected_speed = speed_slider.value
                    selected_volume = volume_slider.value
                    is_muted = mute_checkbox.checked
                    selected_fill_percent = fill_slider.value
                    should_show_path = show_path_checkbox.checked
                    selected_theme = theme_selector.current_theme_name
                    selected_max_fps = max_fps_slider.value

                    settings_changed = (
                        selected_speed != original_speed or
                        selected_volume != original_volume or
                        is_muted != original_mute or
                        selected_fill_percent != original_fill_percent or
                        should_show_path != original_show_path or
                        selected_theme != original_theme or
                        selected_max_fps != original_max_fps
                    )

                    if settings_changed and not settings_just_applied:
                        dialog_result = unsaved_settings_dialog(surface, clock)
                        if dialog_result == "save":
                            original_speed = selected_speed
                            original_volume = selected_volume
                            original_mute = is_muted
                            original_fill_percent = selected_fill_percent
                            original_show_path = should_show_path
                            original_theme = selected_theme
                            original_max_fps = selected_max_fps
                            if eat_sound:
                                eat_sound.set_volume(0 if is_muted else selected_volume / 100)
                            running = False
                        elif dialog_result == "discard":
                            set_theme(original_theme)
                            if eat_sound:
                                eat_sound.set_volume(0 if original_mute else original_volume / 100)
                            running = False
                    else:
                        set_theme(original_theme)
                        if eat_sound:
                            eat_sound.set_volume(0 if original_mute else original_volume / 100)
                        running = False

        selected_speed = speed_slider.value
        selected_volume = volume_slider.value
        is_muted = mute_checkbox.checked
        selected_fill_percent = fill_slider.value
        should_show_path = show_path_checkbox.checked
        selected_theme = theme_selector.current_theme_name
        selected_max_fps = max_fps_slider.value
        
        if eat_sound:
            eat_sound.set_volume(0 if is_muted else selected_volume / 100)

        surface.fill(current_colors['background'])
        
        content_surface = pygame.Surface((SCREEN_WIDTH, content_height))
        content_surface.fill(current_colors['background'])
        
        title_rect_onscreen = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(title_surf, title_rect_onscreen)
        
        y_pos_draw = title_rect_onscreen.bottom + 50
        
        original_speed_rect = speed_slider.rect.copy()
        speed_slider.rect.topleft = (widget_x, y_pos_draw)
        speed_slider.draw(content_surface)
        speed_slider.rect = original_speed_rect
        y_pos_draw += 70
        
        original_max_fps_rect = max_fps_slider.rect.copy()
        max_fps_slider.rect.topleft = (widget_x, y_pos_draw)
        max_fps_slider.draw(content_surface)
        max_fps_slider.rect = original_max_fps_rect
        y_pos_draw += 70
        
        original_volume_rect = volume_slider.rect.copy()
        volume_slider.rect.topleft = (widget_x, y_pos_draw)
        volume_slider.draw(content_surface)
        volume_slider.rect = original_volume_rect
        y_pos_draw += 70
        
        original_fill_rect = fill_slider.rect.copy()
        fill_slider.rect.topleft = (widget_x, y_pos_draw)
        fill_slider.draw(content_surface)
        fill_slider.rect = original_fill_rect
        y_pos_draw += 70
        
        original_mute_rect = mute_checkbox.rect.copy()
        mute_checkbox.rect.topleft = (widget_x, y_pos_draw)
        mute_checkbox.draw(content_surface)
        mute_checkbox.rect = original_mute_rect
        y_pos_draw += 45
        
        original_show_path_rect = show_path_checkbox.rect.copy()
        show_path_checkbox.rect.topleft = (widget_x, y_pos_draw)
        show_path_checkbox.draw(content_surface)
        show_path_checkbox.rect = original_show_path_rect
        y_pos_draw += 45
        
        original_theme_rect = theme_selector.rect.copy()
        theme_selector.rect.topleft = (widget_x, y_pos_draw)
        theme_selector.draw(content_surface, scroll_y=int(scroll_y), mouse_pos=scroll_mouse_pos)
        theme_selector.rect = original_theme_rect
        y_pos_draw += theme_selector.total_height + 40
        
        original_reset_rect = reset_button_rect.copy()
        original_apply_rect = apply_button_rect.copy()
        original_back_rect = back_button_rect.copy()
        reset_button_rect.topleft = (SCREEN_WIDTH // 2 - total_width // 2, y_pos_draw)
        apply_button_rect.topleft = (reset_button_rect.right + button_spacing, y_pos_draw)
        back_button_rect.topleft = (apply_button_rect.right + button_spacing, y_pos_draw)
        draw_button(content_surface, back_button_rect, current_colors['button'], "Back", is_back_hovered, is_back_clicked)
        draw_button(content_surface, apply_button_rect, current_colors['button'], "Apply", is_apply_hovered, is_apply_clicked)
        draw_button(content_surface, reset_button_rect, current_colors['text_highlight'], "Reset", is_reset_hovered, is_reset_clicked)
        reset_button_rect = original_reset_rect
        apply_button_rect = original_apply_rect
        back_button_rect = original_back_rect

        visible_content_rect = pygame.Rect(0, int(scroll_y), SCREEN_WIDTH - (scrollbar_width + 2 * scrollbar_margin if scrollbar_rect.height > 0 else 0), view_height)
        surface.blit(content_surface, (0, 0), visible_content_rect)
        
        if scrollbar_rect.height > 0:
            pygame.draw.rect(surface, current_colors['slider_bg'], scrollbar_rect, border_radius=7)
            pygame.draw.rect(surface, current_colors['slider_handle'], scrollbar_handle_rect, border_radius=7)
        
        if notification_active:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - notification_timer
            
            if elapsed < notification_duration:
                if elapsed < 300:
                    notification_alpha = min(255, int(255 * elapsed / 300))
                elif elapsed > notification_duration - 300:
                    notification_alpha = max(0, int(255 * (notification_duration - elapsed) / 300))
                else:
                    notification_alpha = 255
                
                try:
                    notification_font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE, bold=True)
                except:
                    notification_font = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2, bold=True)
                
                notification_surf = notification_font.render(notification_text, True, current_colors['text_highlight'])
                notification_surf.set_alpha(notification_alpha)
                
                padding = 20
                notification_bg = pygame.Surface((notification_surf.get_width() + padding * 2, 
                                                notification_surf.get_height() + padding * 2))
                notification_bg.fill(current_colors['background'])
                notification_bg.set_alpha(min(200, notification_alpha))
                
                pygame.draw.rect(notification_bg, current_colors['snake'], 
                                pygame.Rect(0, 0, notification_bg.get_width(), notification_bg.get_height()), 
                                width=3, border_radius=10)
                
                notification_rect = notification_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                notification_bg_rect = notification_bg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                
                surface.blit(notification_bg, notification_bg_rect)
                surface.blit(notification_surf, notification_rect)
            else:
                notification_active = False

        pygame.display.update()
        clock.tick(current_max_fps)

    return original_speed, original_volume, original_mute, original_fill_percent, original_show_path, original_theme, original_max_fps

def start_screen(surface, clock, initial_speed, initial_volume, initial_mute, initial_fill_percent, initial_show_path, initial_theme="default", initial_max_fps=60) -> Tuple[str, int, int, bool, int, bool, str, int]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    try:
        font_small = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_small = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    title_surf = font_title.render("Modern Snake", True, current_colors['text_white'])
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    button_width = 250
    button_height = 55
    button_y_start = title_rect.bottom + 60
    button_spacing = 30

    manual_button_rect = pygame.Rect(0, 0, button_width, button_height)
    auto_button_rect = pygame.Rect(0, 0, button_width, button_height)
    settings_button_rect = pygame.Rect(0, 0, button_width, button_height)
    quit_button_rect = pygame.Rect(0, 0, button_width, button_height)

    manual_button_rect.center = (SCREEN_WIDTH // 2, button_y_start)
    auto_button_rect.center = (SCREEN_WIDTH // 2, manual_button_rect.bottom + button_spacing)
    settings_button_rect.center = (SCREEN_WIDTH // 2, auto_button_rect.bottom + button_spacing)
    quit_button_rect.center = (SCREEN_WIDTH // 2, settings_button_rect.bottom + button_spacing)

    buttons = {
        "manual": {"rect": manual_button_rect, "text": "Manual Play", "color": current_colors['button'], "clicked": False},
        "auto": {"rect": auto_button_rect, "text": "Auto Play (AI)", "color": current_colors['button'], "clicked": False},
        "settings": {"rect": settings_button_rect, "text": "Settings", "color": current_colors['text_highlight'], "clicked": False},
        "quit": {"rect": quit_button_rect, "text": "Quit Game", "color": current_colors['button'], "clicked": False}
    }
    
    current_speed = initial_speed
    current_volume = initial_volume
    mute = initial_mute
    current_fill_percent = initial_fill_percent
    show_path_visualization = initial_show_path
    current_theme = initial_theme
    current_max_fps = initial_max_fps
    set_theme(current_theme)
    waiting = True

    while waiting:
        mouse_pos = pygame.mouse.get_pos()
        hover_states = {key: data["rect"].collidepoint(mouse_pos) for key, data in buttons.items()}
        click_states = {key: data["clicked"] for key, data in buttons.items()}

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if confirmation_dialog(surface, clock, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1, 2, 3]:
                    for key, data in buttons.items():
                        if hover_states[key]:
                            buttons[key]["clicked"] = True
            if event.type == pygame.MOUSEBUTTONUP:
                for key, data in buttons.items():
                    if data["clicked"] and hover_states[key]:
                        if eat_sound and not mute:
                            eat_sound.play()

                        if key == 'manual':
                            return 'manual', int(current_speed), int(current_volume), mute, current_fill_percent, show_path_visualization, current_theme, int(current_max_fps)
                        elif key == 'auto':
                            return 'auto', int(current_speed), int(current_volume), mute, current_fill_percent, show_path_visualization, current_theme, int(current_max_fps)
                        elif key == 'settings':
                            current_speed, current_volume, mute, current_fill_percent, show_path_visualization, current_theme, current_max_fps = settings_screen(
                                surface, clock, current_speed, current_volume, mute, current_fill_percent, show_path_visualization, current_theme, current_max_fps
                            )
                            if eat_sound:
                                eat_sound.set_volume(0 if mute else current_volume / 100)
                            buttons["manual"]["color"] = current_colors['button']
                            buttons["auto"]["color"] = current_colors['button']
                            buttons["settings"]["color"] = current_colors['text_highlight']
                            buttons["quit"]["color"] = current_colors['button']
                            title_surf = font_title.render("Modern Snake", True, current_colors['text_white'])
                        elif key == 'quit':
                            if confirmation_dialog(surface, clock, "Quit Game?"):
                                pygame.quit()
                                sys.exit()
                    buttons[key]["clicked"] = False

        surface.fill(current_colors['background'])
        surface.blit(title_surf, title_rect)

        for key, data in buttons.items():
            draw_button(surface, data['rect'], data['color'], data['text'], hover_states[key], click_states[key])

        pygame.display.update()
        clock.tick(current_max_fps)
    return 'manual', 15, 1, False, 0, False, "default", 60

def pause_screen(surface, clock):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(current_colors['background'])
    surface.blit(overlay, (0, 0))

    try:
        font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    pause_text = font.render("Paused", True, current_colors['text_white'])
    pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(pause_text, pause_rect)

    try:
        font_hint = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_hint = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
    hint_text = font_hint.render("Press 'P' or Space to resume", True, current_colors['text'])
    hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, pause_rect.bottom + 40))
    surface.blit(hint_text, hint_rect)

    pygame.display.update()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                    paused = False
        
        clock.tick(60) # Высокий FPS для меню паузы чтобы UI был отзывчивым

def confirmation_dialog(surface, clock, question) -> bool:
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(210)
    overlay.fill(current_colors['background'])
    surface.blit(overlay, (0, 0))

    try:
        font_question = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE)
        font_button = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
    except:
        font_question = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2)
        font_button = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    question_surf = font_question.render(question, True, current_colors['text_white'])
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

    yes_clicked = False
    no_clicked = False

    while True:
        mouse_pos = pygame.mouse.get_pos()
        is_yes_hovered = yes_button_rect.collidepoint(mouse_pos)
        is_no_hovered = no_button_rect.collidepoint(mouse_pos)
        is_yes_clicked = yes_clicked
        is_no_clicked = no_clicked

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in [1, 2, 3]:
                    if is_yes_hovered:
                        yes_clicked = True
                    elif is_no_hovered:
                        no_clicked = True
            if event.type == pygame.MOUSEBUTTONUP:
                if yes_clicked and is_yes_hovered:
                    if eat_sound: eat_sound.play()
                    pygame.time.wait(150)
                    return True
                elif no_clicked and is_no_hovered:
                    if eat_sound: eat_sound.play()
                    pygame.time.wait(150)
                    return False
                yes_clicked = False
                no_clicked = False

        temp_surface = surface.copy()
        draw_button(temp_surface, yes_button_rect, current_colors['gameover'], "Yes", is_yes_hovered, is_yes_clicked)
        draw_button(temp_surface, no_button_rect, current_colors['button'], "No", is_no_hovered, is_no_clicked)
        surface.blit(temp_surface, (0,0))

        pygame.display.update()
        clock.tick(60) # Высокий FPS для диалогов чтобы UI был отзывчивым

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

# --- Функция для отрисовки графика LPS (бывший FPS) ---
def draw_lps_graph(surface: Surface, history: Deque[TimestampedValue], x: int, y: int, width: int, height: int, color: pygame.Color, font: Font):
    """Рисует простой линейный график на основе истории значений (LPS) и добавляет подпись."""
    if not history:
        return
    history_len = len(history)
    max_lps_hist = 1.0
    if history_len > 0:
        # Фильтруем только последние 5 секунд для графика
        recent_values = get_values_in_timespan(history, 5.0)
        if recent_values:
            # Масштабируем по недавним РЕАЛЬНЫМ значениям
            max_lps_hist = max(15.0, max(recent_values) * 1.1) # Минимум 15 для адекватного вида
    # Dynamic scaling based on logic speed
    dynamic_max_y = max(30.0, max_lps_hist) # Убрал множитель 1.1, т.к. уже есть в max_lps_hist

    points = []
    for i, item in enumerate(history):
        lps = item.value # Actual LPS value
        # Normalize based on dynamic_max_y for logic speed
        normalized_y = 1.0 - max(0.0, min(1.0, lps / dynamic_max_y if dynamic_max_y > 1e-6 else 0.0))
        point_x = x + int((i / (history_len - 1 if history_len > 1 else 1)) * width)
        point_y = y + int(normalized_y * height)
        points.append((point_x, point_y))

    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 1)
    elif len(points) == 1:
        pygame.draw.circle(surface, color, points[0], 2)

    # Добавляем подпись "LPS"
    label_surf = font.render("LPS", True, color.lerp((255,255,255), 0.5))
    label_rect = label_surf.get_rect(bottomleft=(x + 3, y + height - 3))
    surface.blit(label_surf, label_rect)

# --- Функция для отрисовки графика FPS (аналогично LPS) ---
def draw_fps_graph(surface: Surface, history: Deque[TimestampedValue], x: int, y: int, width: int, height: int, color: pygame.Color, target_fps: float, font: Font):
    """Рисует простой линейный график для FPS и добавляет подпись."""
    if not history:
        return
    history_len = len(history)
    max_fps_hist = 1.0
    if history_len > 0:
        # Фильтруем только последние 5 секунд для графика
        recent_values = get_values_in_timespan(history, 5.0)
        if recent_values:
            # Scale based on target FPS and actual recent history max
            max_fps_hist = max(target_fps * 1.1, max(recent_values) * 1.1)
    # Ensure a minimum sensible scale
    dynamic_max_y = max(30.0, max_fps_hist)

    points = []
    for i, item in enumerate(history):
        fps = item.value
        # Normalize based on dynamic_max_y for FPS values
        normalized_y = 1.0 - max(0.0, min(1.0, fps / dynamic_max_y if dynamic_max_y > 1e-6 else 0.0))
        point_x = x + int((i / (history_len - 1 if history_len > 1 else 1)) * width)
        point_y = y + int(normalized_y * height)
        points.append((point_x, point_y))

    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 1)
    elif len(points) == 1:
        pygame.draw.circle(surface, color, points[0], 2)

    # Добавляем подпись "FPS"
    label_surf = font.render("FPS", True, color.lerp((255,255,255), 0.5))
    label_rect = label_surf.get_rect(bottomleft=(x + 3, y + height - 3))
    surface.blit(label_surf, label_rect)

MAX_LOGIC_TIME_PER_FRAME = 0.85 # Max % of frame time for logic
STATS_DISPLAY_SECONDS = 5.0 # Display stats for the last 5 seconds

def main():
    pygame.display.set_caption('Modern Snake Game')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    eat_sound = None
    melody_sound = None # Initialize melody_sound

    # --- Font Initialization ---
    try:
        font_icon = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        font_panel = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_SMALL)
        font_tiny = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_TINY)
        font_graph_label = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_TINY - 2) # Шрифт для подписей графиков
    except Exception as e:
        print(f"Primary font ('{FONT_NAME_PRIMARY}') not found, using fallback 'arial'. Error: {e}")
        try:
            font_icon = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
            font_panel = pygame.font.SysFont('arial', FONT_SIZE_SMALL - 2)
            font_tiny = pygame.font.SysFont('arial', FONT_SIZE_TINY - 1)
            font_graph_label = pygame.font.SysFont('arial', FONT_SIZE_TINY - 3)
        except Exception as fallback_e:
            print(f"Fallback font 'arial' also not found. Text rendering might fail. Error: {fallback_e}")
            # As a last resort, use Pygame's default font
            font_icon = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            font_panel = pygame.font.Font(None, FONT_SIZE_SMALL)
            font_tiny = pygame.font.Font(None, FONT_SIZE_TINY)
            font_graph_label = pygame.font.Font(None, FONT_SIZE_TINY - 2)

    # --- Sound Initialization ---
    try:
        pygame.mixer.init()
        sound_file_path = os.path.join(script_dir, 'eat.wav') # Use script_dir
        eat_sound = pygame.mixer.Sound(sound_file_path)
        eat_sound.set_volume(0.05)
    except Exception as e:
        print(f"Could not load eat sound ('{sound_file_path}'): {e}")
        eat_sound = None

    try:
        melody_sound_path = os.path.join(script_dir, 'melody.wav') # Use script_dir
        melody_sound = pygame.mixer.Sound(melody_sound_path)
        melody_sound.set_volume(0.1)
    except Exception as e:
        print(f"Could not load melody sound ('{melody_sound_path}'): {e}")
        melody_sound = None

    current_speed = 15
    current_volume = 50
    mute = False
    current_fill_percent = 0
    show_path_visualization = False
    current_theme = "default"
    current_max_fps = 60 # Initialize max FPS
    target_lps_history: Deque[TimestampedValue] = deque(maxlen=300) # History of target speed with timestamp
    actual_lps_history: Deque[TimestampedValue] = deque(maxlen=300) # Увеличен размер истории LPS до соответствия с FPS
    render_fps_history: Deque[TimestampedValue] = deque(maxlen=300) # History for actual render FPS
    last_lps_values = deque(maxlen=30)  # Буфер для сглаживания LPS по 30 последним значениям
    for _ in range(30):  # Заполняем начальными нулевыми значениями
        last_lps_values.append(0.0)

    while True:
        mode, updated_speed, updated_volume, updated_mute, updated_fill_percent, updated_show_path, updated_theme, updated_max_fps = start_screen( # Receive max FPS
            screen,
            clock,
            current_speed,
            current_volume,
            mute,
            current_fill_percent,
            show_path_visualization,
            current_theme,
            current_max_fps # Передаем ТЕКУЩЕЕ значение, а не будущее
        )
        current_speed = updated_speed
        current_volume = updated_volume
        mute = updated_mute
        current_fill_percent = updated_fill_percent
        show_path_visualization = updated_show_path
        current_theme = updated_theme
        current_max_fps = updated_max_fps # Присваиваем обновленное значение FPS
        set_theme(current_theme)

        initial_current_speed = current_speed
        min_speed = 5

        if eat_sound:
            eat_sound.set_volume(0 if mute else current_volume / 100)

        snake = Snake(mode, initial_fill_percentage=current_fill_percent)
        snake.speed = initial_current_speed
        food = Food()
        food.randomize_position(snake_positions=snake.positions)

        panel_width = 160
        panel_height = 70
        panel_margin_top = 5
        panel_margin_right = 5
        speed_panel_rect = pygame.Rect(SCREEN_WIDTH - panel_width - panel_margin_right, panel_margin_top, panel_width, panel_height)

        slider_margin_h = 15
        slider_margin_top = 35
        slider_height = 15
        game_speed_slider = Slider(speed_panel_rect.x + slider_margin_h,
                                   speed_panel_rect.y + slider_margin_top,
                                   speed_panel_rect.width - 2 * slider_margin_h,
                                   slider_height,
                                   min_speed, 99999, snake.speed, "",
                                   power=5)

        panel_alpha = 76
        time_since_last_logic_update = 0.0 # Time accumulator for logic steps
        # Variables for actual LPS calculation
        lps_steps_since_last_calc = 0
        actual_lps_display = 0.0 # Value to show in stats
        last_frame_time = time.perf_counter()  # Время предыдущего кадра для расчета LPS

        game_running = True
        while game_running:
            frame_start_time = time.perf_counter()
            # Limit rendering loop by max_fps setting
            dt_ms = clock.tick(current_max_fps) # Use the user-defined max FPS
            dt_seconds = dt_ms / 1000.0

            # Calculate actual render FPS and add to history with timestamp
            current_render_fps = clock.get_fps()
            render_fps_history.append(TimestampedValue(current_render_fps))

            # Расчет LPS с той же частотой, что и FPS
            current_time = time.perf_counter()
            frame_time = current_time - last_frame_time
            if frame_time > 0:  # Избегаем деления на ноль
                current_actual_lps = lps_steps_since_last_calc / frame_time
                # Сглаживание значений LPS по 30 последним значениям
                last_lps_values.append(current_actual_lps)  # Добавляем новое значение (старое автоматически удаляется)
                smoothed_lps = sum(last_lps_values) / len(last_lps_values)  # Среднее за последние 30 значений
                actual_lps_display = smoothed_lps  # Обновляем отображаемое значение
                actual_lps_history.append(TimestampedValue(smoothed_lps))  # Сохраняем сглаженное значение
                lps_steps_since_last_calc = 0  # Сбрасываем счетчик шагов логики
                last_frame_time = current_time  # Обновляем время предыдущего кадра

            time_since_last_logic_update += dt_seconds
            # lps_calc_timer += dt_seconds # Accumulate time for actual LPS calculation - больше не нужно

            mouse_pos = pygame.mouse.get_pos()
            is_panel_hovered = speed_panel_rect.collidepoint(mouse_pos)
            panel_alpha = 255 if is_panel_hovered else 76

            # Allow game controls only if panel is not interacted with
            # Panel interaction is checked within its event handling logic now
            game_controls_active = True # Assume active unless panel interaction overrides

            game_speed_slider.value = snake.speed
            game_speed_slider.update_handle_pos()

            events = pygame.event.get()
            panel_interacted_this_frame = False # Flag to check if slider was moved
            for event in events:
                if event.type == pygame.QUIT:
                    if confirmation_dialog(screen, clock, "Quit Game?"):
                        pygame.quit()
                        sys.exit()

                # Handle speed panel interaction first
                if is_panel_hovered:
                     original_speed_before_slider = snake.speed
                     game_speed_slider.handle_event(event)
                     new_speed_after_slider = int(game_speed_slider.value)
                     if new_speed_after_slider != original_speed_before_slider:
                         snake.speed = new_speed_after_slider
                         time_since_last_logic_update = 0.0 # Reset accumulator on interactive speed change
                         panel_interacted_this_frame = True


                if not panel_interacted_this_frame and event.type == pygame.KEYDOWN: # Process other keys only if panel wasn't interacted with
                    if event.key == pygame.K_ESCAPE:
                        game_running = False # Exit current game loop to show start screen

                    # Manual movement controls
                    if snake.mode == 'manual':
                        if event.key in [pygame.K_UP, pygame.K_w]: snake.turn(UP)
                        elif event.key in [pygame.K_DOWN, pygame.K_s]: snake.turn(DOWN)
                        elif event.key in [pygame.K_LEFT, pygame.K_a]: snake.turn(LEFT)
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]: snake.turn(RIGHT)

                    # Speed adjustment keys
                    if event.key in [pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS]:
                        snake.speed = min(99999, snake.speed + 10)
                        game_speed_slider.value = snake.speed
                        game_speed_slider.update_handle_pos()
                        time_since_last_logic_update = 0.0 # Reset accumulator
                    if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                        snake.speed = max(min_speed, snake.speed - 10)
                        game_speed_slider.value = snake.speed
                        game_speed_slider.update_handle_pos()
                        time_since_last_logic_update = 0.0 # Reset accumulator

                    # Pause
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        pause_screen(screen, clock)
                        # Reset time accumulator after unpausing to avoid sudden jump
                        time_since_last_logic_update = 0.0
                        

                    # Theme switching
                    if event.key == pygame.K_q or event.key == pygame.K_e:
                        try:
                            theme_names = list(THEME_DEFINITIONS.keys())
                            current_index = theme_names.index(current_theme)
                            num_themes = len(theme_names)

                            if event.key == pygame.K_q:
                                new_index = (current_index - 1 + num_themes) % num_themes
                            else: # event.key == pygame.K_e
                                new_index = (current_index + 1) % num_themes

                            current_theme = theme_names[new_index]
                            set_theme(current_theme)
                            snake._update_caches()
                            food.color = current_colors['food']
                        except ValueError:
                            print(f"Warning: Current theme '{current_theme}' not found in definitions during switch.")
                            current_theme = "default"
                            set_theme(current_theme)
                            snake._update_caches()
                            food.color = current_colors['food']

                if not game_running: # Check again if ESC was pressed
                    break

            if not game_running: # Break outer loop if necessary
                break

            # --- Time-Budgeted Game Logic Loop ---
            logic_time_step = 1.0 / snake.speed if snake.speed > 0 else float('inf')
            collision_detected_in_frame = False
            
            # Адаптируем бюджет времени на логику в зависимости от заполнения поля
            fill_percentage = snake.length / (GRID_WIDTH * GRID_HEIGHT)
            
            # При высоком заполнении увеличиваем доступное время на логику
            adjusted_max_logic_percent = MAX_LOGIC_TIME_PER_FRAME
            if fill_percentage > 0.95:
                # На финальном этапе заполнения даём больше времени на логику
                adjusted_max_logic_percent = 0.95  # 95% времени кадра на логику
            elif fill_percentage > 0.9:
                adjusted_max_logic_percent = 0.9  # 90% времени кадра на логику
            
            # Calculate time budget for logic in this frame
            max_logic_time_this_frame = (1.0 / current_max_fps if current_max_fps > 0 else 0) * adjusted_max_logic_percent
            logic_start_time = time.perf_counter()
            time_spent_on_logic_this_frame = 0.0

            while (time_since_last_logic_update >= logic_time_step and
                   not collision_detected_in_frame and
                   time_spent_on_logic_this_frame < max_logic_time_this_frame):

                # Process one step of game logic
                collision = snake.move(food.position)
                lps_steps_since_last_calc += 1 # Increment counter for actual LPS calculation

                if collision:
                    collision_detected_in_frame = True # Set flag, actual handling after loop
                elif snake.get_head_position() == food.position:
                    food.randomize_position(snake_positions=snake.positions)
                    if snake.mode == 'auto':
                         snake.current_food_pos = food.position
                    if eat_sound and not mute:
                        eat_sound.play()

                # Decrement accumulator *after* processing the step
                time_since_last_logic_update = max(0.0, time_since_last_logic_update - logic_time_step)

                # Update time spent on logic
                time_spent_on_logic_this_frame = time.perf_counter() - logic_start_time

            # --- Handle Collision (after logic loop for the frame) ---
            if collision_detected_in_frame:
                final_history = deque(snake.history)

                if melody_sound and not mute:
                    melody_sound.play()

                current_speed_on_death = int(snake.speed)

                should_restart = game_over_screen(screen, clock, snake.length, current_speed_on_death, final_history)

                if should_restart:
                    snake.reset(initial_fill_percentage=current_fill_percent)
                    snake.speed = initial_current_speed
                    food.randomize_position(snake_positions=snake.positions)
                    game_controls_active = True
                else:
                    game_running = False

            # Проверка на победу - змейка заполнила всё поле
            elif snake.length >= GRID_WIDTH * GRID_HEIGHT:
                # ВАЖНО: Сначала отрисовываем финальный кадр с полным полем
                screen.fill(current_colors['background'])
                draw_grid(screen)
                
                if snake.mode == 'auto' and show_path_visualization and snake.path:
                    draw_path(screen, snake.path)
                
                snake.draw(screen)
                display_statistics(screen, snake.length, snake.speed)
                
                # Отрисовываем виджеты (если они активны)
                pygame.display.update()
                
                # Небольшая задержка перед показом экрана победы
                pygame.time.delay(500)  # 500 мс = 0.5 секунды
                
                if melody_sound and not mute:
                    melody_sound.play()
                
                current_speed_on_victory = int(snake.speed)
                
                # Вызываем экран победы
                should_restart = win_screen(screen, clock, snake.length, current_speed_on_victory)
                
                if should_restart:
                    snake.reset(initial_fill_percentage=current_fill_percent)
                    snake.speed = initial_current_speed
                    food.randomize_position(snake_positions=snake.positions)
                    game_controls_active = True
                else:
                    game_running = False

            elif snake.get_head_position() == food.position:
                # Проверяем, является ли это последней едой перед победой
                if snake.length + 1 >= GRID_WIDTH * GRID_HEIGHT:
                    snake.length += 1  # Увеличиваем длину для победы
                    
                    # ВАЖНО: Сначала отрисовываем финальный кадр с полным полем
                    screen.fill(current_colors['background'])
                    draw_grid(screen)
                    
                    # Обновляем положения змейки для отрисовки полного поля
                    # Добавляем последнюю съеденную клетку в голову змеи
                    snake.positions.appendleft(snake.get_head_position())
                    snake._update_caches()
                    
                    if snake.mode == 'auto' and show_path_visualization and snake.path:
                        draw_path(screen, snake.path)
                    
                    snake.draw(screen)
                    display_statistics(screen, snake.length, snake.speed)
                    
                    # Отрисовываем виджеты FPS/LPS, если они активны
                    # (копия соответствующего кода отрисовки из основного цикла)
                    pygame.display.update()
                    
                    # Небольшая задержка, чтобы игрок успел увидеть заполненное поле
                    pygame.time.delay(500)  # 500 мс = 0.5 секунды
                    
                    if melody_sound and not mute:
                        melody_sound.play()
                    
                    current_speed_on_victory = int(snake.speed)
                    
                    # Вызываем экран победы
                    should_restart = win_screen(screen, clock, snake.length, current_speed_on_victory)
                    
                    if should_restart:
                        snake.reset(initial_fill_percentage=current_fill_percent)
                        snake.speed = initial_current_speed
                        food.randomize_position(snake_positions=snake.positions)
                        game_controls_active = True
                    else:
                        game_running = False
                else:
                    food.randomize_position(snake_positions=snake.positions)
                    if snake.mode == 'auto':
                         snake.current_food_pos = food.position

                    if eat_sound and not mute:
                        eat_sound.play()

            screen.fill(current_colors['background'])
            draw_grid(screen)

            if snake.mode == 'auto' and show_path_visualization and snake.path:
                draw_path(screen, snake.path)

            snake.draw(screen)
            food.draw(screen)
            display_statistics(screen, snake.length, snake.speed)

            # --- LPS/FPS Widget ---
            # Add the *target* logic speed (snake.speed) to the history for graphing with timestamp
            target_lps_history.append(TimestampedValue(snake.speed))

            graph_width = 100
            text_width = 45
            padding = 5
            total_width = graph_width + padding + text_width
            graph_height = 50
            margin_right = 10
            margin_bottom = 10

            widget_x = SCREEN_WIDTH - total_width - margin_right
            widget_y = SCREEN_HEIGHT - graph_height - margin_bottom
            # Renamed rect for clarity
            lps_widget_rect = pygame.Rect(widget_x, widget_y, total_width, graph_height)

            graph_x_rel = 0
            graph_y_rel = 0
            text_x_rel = graph_width + padding
            text_y_rel = 0

            # Renamed variables for clarity
            is_lps_widget_hovered = lps_widget_rect.collidepoint(mouse_pos)
            lps_widget_alpha = 255 if is_lps_widget_hovered else 76
            lps_bg_color_opaque = COLOR_PANEL_BG # Use existing panel color

            # Renamed surface for clarity
            lps_widget_surface = pygame.Surface(lps_widget_rect.size, pygame.SRCALPHA)

            # Draw background for the LPS widget
            pygame.draw.rect(lps_widget_surface, lps_bg_color_opaque, lps_widget_surface.get_rect(), border_radius=4)

            # Draw the graph using the history of *actual* calculated LPS
            draw_lps_graph(lps_widget_surface, actual_lps_history, graph_x_rel, graph_y_rel, graph_width, graph_height, color=current_colors['text_highlight'], font=font_graph_label)

            # Display Min/Avg/Max based on the *actual* calculated LPS history
            # Filter for only the last 5 seconds
            min_actual_lps = 0.0
            max_actual_lps = 0.0
            avg_actual_lps = 0.0

            recent_actual_lps = get_values_in_timespan(actual_lps_history, STATS_DISPLAY_SECONDS)
            if recent_actual_lps:
                min_actual_lps = min(recent_actual_lps)
                max_actual_lps = max(recent_actual_lps)
                avg_actual_lps = sum(recent_actual_lps) / len(recent_actual_lps)

            text_margin_in_area = 3

            # Display Max Actual LPS
            max_text_surf = font_tiny.render(f"{max_actual_lps:.0f}", True, current_colors['text'])
            max_text_rect = max_text_surf.get_rect(topright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + text_margin_in_area))
            lps_widget_surface.blit(max_text_surf, max_text_rect)

            # Displaying Average Actual LPS
            avg_text_surf = font_tiny.render(f"{avg_actual_lps:.0f}", True, current_colors['text'])
            avg_text_rect = avg_text_surf.get_rect(midright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height // 2))
            lps_widget_surface.blit(avg_text_surf, avg_text_rect)

            # Display Min Actual LPS
            min_text_surf = font_tiny.render(f"{min_actual_lps:.0f}", True, current_colors['text'])
            min_text_rect = min_text_surf.get_rect(bottomright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height - text_margin_in_area))
            lps_widget_surface.blit(min_text_surf, min_text_rect)

            # Set alpha and blit the LPS widget
            lps_widget_surface.set_alpha(lps_widget_alpha)
            screen.blit(lps_widget_surface, lps_widget_rect.topleft)

            # --- FPS Widget (Bottom Left) ---
            fps_widget_width = total_width # Same size as LPS widget
            fps_widget_height = graph_height
            fps_widget_margin_left = 10
            fps_widget_margin_bottom = 10
            fps_widget_x = fps_widget_margin_left
            fps_widget_y = SCREEN_HEIGHT - fps_widget_height - fps_widget_margin_bottom
            fps_widget_rect = pygame.Rect(fps_widget_x, fps_widget_y, fps_widget_width, fps_widget_height)

            is_fps_widget_hovered = fps_widget_rect.collidepoint(mouse_pos)
            fps_widget_alpha = 255 if is_fps_widget_hovered else 76
            fps_bg_color_opaque = COLOR_PANEL_BG # Use panel background color

            fps_widget_surface = pygame.Surface(fps_widget_rect.size, pygame.SRCALPHA)
            # Draw background for the FPS widget
            pygame.draw.rect(fps_widget_surface, fps_bg_color_opaque, fps_widget_surface.get_rect(), border_radius=4)

            # Draw the graph using the history of actual render FPS
            draw_fps_graph(fps_widget_surface, render_fps_history, graph_x_rel, graph_y_rel, graph_width, graph_height, color=current_colors['text_highlight'], target_fps=current_max_fps, font=font_graph_label)

            # Display Min/Avg/Max based on the actual render FPS history (last 5 seconds)
            min_render_fps = 0.0
            max_render_fps = 0.0
            avg_render_fps = 0.0

            recent_render_fps = get_values_in_timespan(render_fps_history, STATS_DISPLAY_SECONDS)
            if recent_render_fps:
                min_render_fps = min(recent_render_fps)
                max_render_fps = max(recent_render_fps)
                avg_render_fps = sum(recent_render_fps) / len(recent_render_fps)

            # Display Max Render FPS
            max_fps_text_surf = font_tiny.render(f"{max_render_fps:.0f}", True, current_colors['text'])
            max_fps_text_rect = max_fps_text_surf.get_rect(topright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + text_margin_in_area))
            fps_widget_surface.blit(max_fps_text_surf, max_fps_text_rect)

            # Displaying Average Render FPS
            avg_fps_text_surf = font_tiny.render(f"{avg_render_fps:.0f}", True, current_colors['text'])
            avg_fps_text_rect = avg_fps_text_surf.get_rect(midright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height // 2))
            fps_widget_surface.blit(avg_fps_text_surf, avg_fps_text_rect)

            # Display Min Render FPS
            min_fps_text_surf = font_tiny.render(f"{min_render_fps:.0f}", True, current_colors['text'])
            min_fps_text_rect = min_fps_text_surf.get_rect(bottomright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height - text_margin_in_area))
            fps_widget_surface.blit(min_fps_text_surf, min_fps_text_rect)

            # Set alpha and blit the FPS widget
            fps_widget_surface.set_alpha(fps_widget_alpha)
            screen.blit(fps_widget_surface, fps_widget_rect.topleft)

            # --- Speed Control Panel (remains the same) ---
            panel_bg_color_tuple = (current_colors['panel_bg'].r, current_colors['panel_bg'].g, current_colors['panel_bg'].b, panel_alpha)
            panel_surface = pygame.Surface(speed_panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, panel_bg_color_tuple, panel_surface.get_rect(), border_radius=4)

            panel_title_surf = font_panel.render("Speed (LPS)", True, current_colors['text_white']) # Changed label
            panel_title_rect = panel_title_surf.get_rect(centerx=panel_surface.get_rect().centerx, top=8)
            panel_surface.blit(panel_title_surf, panel_title_rect)

            # Draw slider within the panel surface (relative coordinates)
            original_slider_rect = game_speed_slider.rect.copy()
            game_speed_slider.rect.topleft = (slider_margin_h, slider_margin_top)
            game_speed_slider.draw(panel_surface)
            game_speed_slider.rect = original_slider_rect # Restore original rect if needed elsewhere

            panel_surface.set_alpha(panel_alpha)
            screen.blit(panel_surface, speed_panel_rect.topleft)
            # --- End Speed Control Panel ---


            pygame.display.update()
            # clock.tick(current_max_fps) is already called at the top

def unsaved_settings_dialog(surface, clock):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(210)
    overlay.fill(current_colors['background'])
    current_alpha = overlay.get_alpha() or 255
    overlay.set_alpha(max(0, int(current_alpha * 0.85)))

    surface.blit(overlay, (0, 0))

    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2, bold=True)

    title_surf = font_title.render("Unsaved Changes", True, current_colors['text_white'])

    dialog_width = 500
    dialog_height = 160
    dialog_rect = pygame.Rect(0, 0, dialog_width, dialog_height)
    dialog_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    title_rect = title_surf.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 40))

    button_width = 130
    button_height = 50
    button_spacing = 25
    total_buttons_width = 3 * button_width + 2 * button_spacing

    save_button_rect = pygame.Rect(0, 0, button_width, button_height)
    discard_button_rect = pygame.Rect(0, 0, button_width, button_height)
    cancel_button_rect = pygame.Rect(0, 0, button_width, button_height)

    start_x = dialog_rect.centerx - total_buttons_width // 2
    buttons_y = dialog_rect.bottom - 65
    save_button_rect.topleft = (start_x, buttons_y)
    discard_button_rect.topleft = (save_button_rect.right + button_spacing, buttons_y)
    cancel_button_rect.topleft = (discard_button_rect.right + button_spacing, buttons_y)

    buttons = {
        "save": {"rect": save_button_rect, "text": "Save", "color": current_colors['button_hover'], "hovered": False, "clicked": False}, # Цвет "Успех/Применить"
        "discard": {"rect": discard_button_rect, "text": "Discard", "color": current_colors['gameover'], "hovered": False, "clicked": False}, # Цвет "Предупреждение/Отмена"
        "cancel": {"rect": cancel_button_rect, "text": "Cancel", "color": current_colors['button'], "hovered": False, "clicked": False} # Стандартный цвет кнопки
    }

    running = True
    result = "cancel"

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for key, data in buttons.items():
            buttons[key]["hovered"] = data["rect"].collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if confirmation_dialog(surface, clock, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
                else:
                    temp_surface = surface.copy()
                    surface.blit(overlay, (0,0))


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    for key, data in buttons.items():
                        if data["hovered"]:
                            buttons[key]["clicked"] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                clicked_on_button = False
                for key, data in buttons.items():
                    if data["clicked"] and data["hovered"]:
                        if eat_sound:
                            eat_sound.play()
                        result = key
                        running = False
                        clicked_on_button = True
                    buttons[key]["clicked"] = False

            elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE:
                      result = "cancel"
                      running = False

        temp_surface = surface.copy()
        pygame.draw.rect(temp_surface, current_colors['panel_bg'], dialog_rect, border_radius=10)
        pygame.draw.rect(temp_surface, current_colors['text_highlight'], dialog_rect, width=2, border_radius=10)

        temp_surface.blit(title_surf, title_rect)
        for key, data in buttons.items():
            base_color = data["color"]
            hover_color = data["color"].lerp(current_colors['background'], 0.2)
            click_color = current_colors['button_click']
            button_color_to_use = base_color
            if data["clicked"]:
                button_color_to_use = click_color
            elif data["hovered"]:
                 pass

            draw_button(temp_surface, data["rect"], base_color, data["text"], data["hovered"], data["clicked"])

        surface.blit(temp_surface, (0,0))

        pygame.display.update(dialog_rect.inflate(4,4))
        clock.tick(60) # Высокий FPS для диалогов чтобы UI был отзывчивым

    return result

# Добавляем новую функцию win_screen

def win_screen(surface, clock, final_length, final_speed):
    """Shows the victory screen with stats and buttons."""
    fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fade_surf.fill((0, 0, 0, 200))  # Semi-transparent black background
    surface.blit(fade_surf, (0, 0))
    
    font_large = pygame.font.SysFont(FONT_NAME_PRIMARY, 48)
    font = pygame.font.SysFont(FONT_NAME_PRIMARY, 36)
    small_font = pygame.font.SysFont(FONT_NAME_PRIMARY, 24)
    
    # Title
    title = font_large.render("You Won!", True, (255, 255, 100))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    surface.blit(title, title_rect)
    
    # Statistics
    fill_percent = (final_length / (GRID_WIDTH * GRID_HEIGHT)) * 100
    stats_text = [
        f"Field Filled: {fill_percent:.2f}%",
        f"Snake Length: {final_length}",
        f"Speed: {final_speed}"
    ]
    
    for i, text in enumerate(stats_text):
        stat = font.render(text, True, (200, 200, 255))
        stat_rect = stat.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + i * 40))
        surface.blit(stat, stat_rect)
    
    # Buttons
    button_width, button_height = 220, 60
    button_y = SCREEN_HEIGHT * 2 // 3
    
    play_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width - 20, button_y, button_width, button_height)
    menu_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, button_y, button_width, button_height)
    
    # No need for play_text and quit_text variables anymore
    # Button states
    restart_hovered = False
    menu_hovered = False
    restart_clicked = False
    menu_clicked = False
    
    # Victory screen loop
    win_screen_active = True
    while win_screen_active:
        mouse_pos = pygame.mouse.get_pos()
        restart_hovered = play_button.collidepoint(mouse_pos)
        menu_hovered = menu_button.collidepoint(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_hovered:
                    restart_clicked = True
                if menu_hovered:
                    menu_clicked = True
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if restart_hovered and restart_clicked:
                    return True # Return True to indicate restart
                if menu_hovered and menu_clicked:
                    return False # Return False to indicate back to main menu
                restart_clicked = False
                menu_clicked = False
        
        # Draw buttons
        draw_button(surface, play_button, current_colors['button'], "Restart", restart_hovered, restart_clicked)
        draw_button(surface, menu_button, current_colors['button'], "Main Menu", menu_hovered, menu_clicked)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    set_theme("default")
    main()
