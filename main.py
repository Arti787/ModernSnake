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

SURVIVAL_MODE_DURATION = 100 # Количество шагов в режиме выживания

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
        button_color = base_color.lerp(current_colors['background'], 0.2) # Смешиваем с цветом фона


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
        self.clicked = False  # Флаг для отслеживания нажатия
        try:
            self.font = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        except:
            self.font = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверяем, что это именно кнопка мыши, а не колесико
            if event.button in [1, 2, 3]:  # Левая, средняя или правая кнопка мыши
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
        self.label_rect = label_rect # Сохраняем Rect метки
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
            
            # Рисуем 4 цветных квадратика для отображения основных цветов
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
        self._update_caches()

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
            
            # Кэшируем цвета для всех возможных сегментов
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
        """Обновляет кэш соседних сегментов."""
        self._neighboring_segments_cache = {}
        num_segments = len(self.positions)
        for i, pos in enumerate(self.positions):
            neighbors = set()
            if i > 0:
                prev_pos = self.positions[i-1]
                neighbors.add(prev_pos)
            if i < num_segments - 1:
                next_pos = self.positions[i+1]
                neighbors.add(next_pos)
            if neighbors: # Добавляем в кэш только если есть соседи
                self._neighboring_segments_cache[pos] = neighbors
                
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
            
            neighbors = self._neighboring_segments_cache.get(current_pos, set()) # Используем кэш
            
            # Проверяем правого соседа
            if (neighbor_right in self.positions_set and 
                neighbor_right not in neighbors):
                pygame.draw.line(surface, internal_border_color,
                                (x_px + GRIDSIZE - line_width, y_px),
                                (x_px + GRIDSIZE - line_width, y_px + GRIDSIZE - 1),
                                line_width)
            
            # Проверяем нижнего соседа
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
            collision = self.manual_move() # Ручной ход не меняется

        if self.positions:
             self.history.append((list(self.positions), self.current_food_pos))

        return collision

    def manual_move(self):
        """Движение вперед в ручном режиме на основе self.next_direction."""
        self.direction = self.next_direction # Обновляем текущее направление
        cur = self.get_head_position()
        x, y = self.direction
        new_head_pos = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        return self.move_forward(new_head_pos)

    def auto_move(self, food_pos):
        """Выбор направления и движение вперед в авто-режиме."""
        head = self.get_head_position()

        if self.survival_mode_steps_remaining > 0:
            self.survival_mode_steps_remaining -= 1
            survival_direction = self.find_survival_move()
            if not survival_direction:
                survival_direction = self.find_immediate_safe_direction()

            if survival_direction:
                self.next_direction = survival_direction
            else:
                self.next_direction = self.direction

            self.current_path = []
            self.path = []
            self.recalculate_path = False

        else:
            if self.recalculate_path or not self.current_path:
                path_to_food = self.path_find.find_path(head, food_pos, list(self.positions))

                if path_to_food and self.is_path_safe_to_food(path_to_food):
                    self.current_path = path_to_food
                    self.path = self.current_path
                    self.recalculate_path = False
                    if len(self.current_path) > 1:
                        self.next_direction = self.get_direction_to(self.current_path[1])
                    else:
                        self.next_direction = self.direction

                else:
                    self.current_path = []
                    self.path = []
                    survival_direction = self.find_survival_move()

                    if survival_direction:
                        self.next_direction = survival_direction
                        self.survival_mode_steps_remaining = SURVIVAL_MODE_DURATION
                        self.recalculate_path = False
                    else:
                        safe_immediate_direction = self.find_immediate_safe_direction()
                        if safe_immediate_direction:
                            self.next_direction = safe_immediate_direction
                        else:
                            self.next_direction = self.direction
                        self.recalculate_path = True

            else:
                if len(self.current_path) > 1:
                    self.next_direction = self.get_direction_to(self.current_path[1])
                else:
                    self.recalculate_path = True
                    self.current_path = []
                    self.path = []
                    self.next_direction = self.find_immediate_safe_direction() or self.direction

        self.direction = self.next_direction
        cur = self.get_head_position()
        x, y = self.direction
        new_head_pos = ((cur[0] + x) % GRID_WIDTH, (cur[1] + y) % GRID_HEIGHT)
        collision = self.move_forward(new_head_pos)

        if self.survival_mode_steps_remaining == 0 and not self.recalculate_path and self.current_path and not collision:
             if self.current_path[0] == cur:
                 self.current_path.pop(0)
             else:
                 self.recalculate_path = True
                 self.current_path = []
                 self.path = []

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
        
        # Обновляем кэши, ТОЛЬКО если структура змейки изменилась
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
        possible_directions = [d for d in [UP, DOWN, LEFT, RIGHT] if d != (self.direction[0] * -1, self.direction[1] * -1)]

        current_positions_list = list(self.positions)

        for direction in possible_directions:
            next_head = ((head[0] + direction[0]) % GRID_WIDTH, (head[1] + direction[1]) % GRID_HEIGHT)

            if len(self.positions) > 1 and next_head in itertools.islice(self.positions, 0, len(self.positions) - 1):
                 continue

            sim_snake_list = self.simulate_move([head, next_head], grows=False, initial_state=current_positions_list)
            if sim_snake_list is None:
                continue

            sim_head = sim_snake_list[0]
            sim_tail = sim_snake_list[-1]
            path_to_tail = self.path_find.find_path(sim_head, sim_tail, sim_snake_list)


            if path_to_tail:
                 freedom = len(path_to_tail) + self.path_find._heuristic(sim_head, sim_tail) * 0.5
            else:
                 freedom = self.path_find._heuristic(sim_head, sim_tail) * 0.2 

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
                 print(f"Warning: Failed to generate snake for {initial_fill_percentage}% on reset, starting with default.")

        self._update_caches() # Обновляем кэши при ресете

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = current_colors['food']
        self.randomize_position([])

    def randomize_position(self, snake_positions: List[Tuple[int, int]] | Deque[Tuple[int, int]]):
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_positions:
                break

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
        clock.tick(60)

def game_over_screen(surface, clock, snake_length, current_speed, history: deque):
    """Экран Game Over теперь просто вызывает replay_screen."""
    return replay_screen(surface, clock, history)

def settings_screen(surface, clock, current_speed, current_volume, mute, current_fill_percent, current_show_path, current_theme="default") -> Tuple[int, int, bool, int, bool, str]:
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_XLARGE, bold=True)
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_XLARGE - 4, bold=True)

    title_surf = font_title.render("Settings", True, current_colors['text_white'])
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 220))

    slider_width = 350
    slider_height = 25
    checkbox_size = 25
    widget_x = SCREEN_WIDTH // 2 - slider_width // 2
    y_pos = SCREEN_HEIGHT // 2 - 150

    speed_slider = Slider(widget_x, y_pos, slider_width, slider_height, 5, 5000, current_speed, "Game Speed", power=2.5)
    y_pos += 70

    volume_slider = Slider(widget_x, y_pos, slider_width, slider_height, 0, 100, current_volume, "Sound Volume")
    y_pos += 70

    fill_slider = Slider(widget_x, y_pos, slider_width, slider_height, 0, 95, current_fill_percent, "Initial Fill (%)")
    y_pos += 70

    mute_checkbox = Checkbox(widget_x, y_pos, checkbox_size, "Mute Sound", mute)
    y_pos += 45
    show_path_checkbox = Checkbox(widget_x, y_pos, checkbox_size, "Show AI Path", current_show_path)
    
    y_pos += 60
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
    
    # Всплывающее уведомление
    notification_active = False
    notification_text = ""
    notification_timer = 0
    notification_duration = 2000  # 2 секунды
    notification_alpha = 0

    # Сохраняем исходные значения для возможности отмены
    original_speed = current_speed
    original_volume = current_volume
    original_mute = mute
    original_fill_percent = current_fill_percent
    original_show_path = current_show_path
    original_theme = current_theme
    
    # Для предотвращения мигания диалога после применения настроек
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
                # Проверяем, что это именно кнопка мыши, а не колесико
                if event.button in [1, 2, 3]:  # Левая, средняя или правая кнопка мыши
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

                    # Проверяем, были ли изменены настройки и не были ли они применены
                    selected_speed = speed_slider.value
                    selected_volume = volume_slider.value
                    is_muted = mute_checkbox.checked
                    selected_fill_percent = fill_slider.value
                    should_show_path = show_path_checkbox.checked
                    selected_theme = theme_selector.current_theme_name

                    settings_changed = (
                        selected_speed != original_speed or
                        selected_volume != original_volume or
                        is_muted != original_mute or
                        selected_fill_percent != original_fill_percent or
                        should_show_path != original_show_path or
                        selected_theme != original_theme
                    )

                    if settings_changed and not settings_just_applied:
                        # Показываем диалог с предложением сохранить или отменить изменения
                        dialog_result = unsaved_settings_dialog(surface, clock)

                        if dialog_result == "save":
                            # Сохраняем изменения как новые оригинальные значения
                            original_speed = selected_speed
                            original_volume = selected_volume
                            original_mute = is_muted
                            original_fill_percent = selected_fill_percent
                            original_show_path = should_show_path
                            original_theme = selected_theme

                            if eat_sound:
                                eat_sound.set_volume(0 if is_muted else selected_volume / 100)

                            running = False
                        elif dialog_result == "discard":
                            # Отменяем изменения и выходим
                            # Восстанавливаем оригинальную тему перед выходом
                            set_theme(original_theme)
                            if eat_sound:
                                eat_sound.set_volume(0 if original_mute else original_volume / 100)
                            running = False
                        # Если dialog_result == "cancel", просто продолжаем настройки
                    else:
                        # Восстанавливаем оригинальную тему перед выходом, если не было изменений или только что применили
                        set_theme(original_theme)
                        if eat_sound:
                            eat_sound.set_volume(0 if original_mute else original_volume / 100)
                        running = False
                elif apply_clicked and is_apply_hovered:
                    if eat_sound:
                        eat_sound.play()
                    
                    # Применяем настройки и сохраняем как новые оригинальные значения
                    current_speed = speed_slider.value
                    current_volume = volume_slider.value
                    mute = mute_checkbox.checked
                    current_fill_percent = fill_slider.value
                    current_show_path = show_path_checkbox.checked
                    current_theme = theme_selector.current_theme_name
                    
                    # Обновляем "оригинальные" значения
                    original_speed = current_speed
                    original_volume = current_volume
                    original_mute = mute
                    original_fill_percent = current_fill_percent
                    original_show_path = current_show_path
                    original_theme = current_theme
                    
                    # Применяем звук
                    if eat_sound:
                        eat_sound.set_volume(0 if mute else current_volume / 100)
                        
                    # Активируем уведомление
                    notification_active = True
                    notification_text = "Settings Applied!"
                    notification_timer = pygame.time.get_ticks()
                    notification_alpha = 0
                    
                    # Отмечаем, что настройки только что применены
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
            
            # Для theme_selector используем handle_event без изменений - он обработает правильно,
            # т.к. мы модифицировали event для него с учетом прокрутки
            theme_selector.handle_event(adjusted_event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Проверяем, были ли изменены настройки при нажатии ESC
                    selected_speed = speed_slider.value
                    selected_volume = volume_slider.value
                    is_muted = mute_checkbox.checked
                    selected_fill_percent = fill_slider.value
                    should_show_path = show_path_checkbox.checked
                    selected_theme = theme_selector.current_theme_name

                    settings_changed = (
                        selected_speed != original_speed or
                        selected_volume != original_volume or
                        is_muted != original_mute or
                        selected_fill_percent != original_fill_percent or
                        should_show_path != original_show_path or
                        selected_theme != original_theme
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
                            if eat_sound:
                                eat_sound.set_volume(0 if is_muted else selected_volume / 100)
                            running = False
                        elif dialog_result == "discard":
                            # Восстанавливаем оригинальную тему перед выходом
                            set_theme(original_theme)
                            if eat_sound:
                                eat_sound.set_volume(0 if original_mute else original_volume / 100)
                            running = False
                        # Если "cancel", ничего не делаем, остаемся в настройках
                    else:
                        # Восстанавливаем оригинальную тему перед выходом, если не было изменений или только что применили
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
        
        # Временно применяем звук для предпросмотра изменений
        if eat_sound:
            eat_sound.set_volume(0 if is_muted else selected_volume / 100)

        surface.fill(current_colors['background'])
        
        content_surface = pygame.Surface((SCREEN_WIDTH, content_height))
        content_surface.fill(current_colors['background'])
        
        title_rect_onscreen = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 60))
        surface.blit(title_surf, title_rect_onscreen)
        
        y_pos_draw = 150
        
        original_speed_rect = speed_slider.rect.copy()
        speed_slider.rect.topleft = (widget_x, y_pos_draw)
        speed_slider.draw(content_surface)
        speed_slider.rect = original_speed_rect
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
        y_pos_draw += 60
        
        original_theme_rect = theme_selector.rect.copy()
        theme_selector.rect.topleft = (widget_x, y_pos_draw)
        # Передаем правильную позицию мыши с учетом прокрутки для определения подсветки при наведении
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
        clock.tick(60)

    return original_speed, original_volume, original_mute, original_fill_percent, original_show_path, original_theme

def start_screen(surface, clock, initial_speed, initial_volume, initial_mute, initial_fill_percent, initial_show_path, initial_theme="default") -> Tuple[str, int, int, bool, int, bool, str]:
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
                            return 'manual', int(current_speed), int(current_volume), mute, current_fill_percent, show_path_visualization, current_theme
                        elif key == 'auto':
                            return 'auto', int(current_speed), int(current_volume), mute, current_fill_percent, show_path_visualization, current_theme
                        elif key == 'settings':
                            current_speed, current_volume, mute, current_fill_percent, show_path_visualization, current_theme = settings_screen(
                                surface, clock, current_speed, current_volume, mute, current_fill_percent, show_path_visualization, current_theme
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
        clock.tick(60)
    return 'manual', 15, 1, False, 0, False, "default"

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
        clock.tick(15)

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
        clock.tick(60)

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
    max_fps_hist = 1.0
    if history_len > 0:
        max_fps_hist = max(history)
    dynamic_max_y = max(60.0, max_fps_hist * 1.1)
 
    points = []
    for i, fps in enumerate(history):
        normalized_y = 1.0 - max(0.0, min(1.0, fps / dynamic_max_y if dynamic_max_y > 1e-6 else 0.0))
        point_x = x + int((i / (history_len - 1 if history_len > 1 else 1)) * width)
        point_y = y + int(normalized_y * height)
        points.append((point_x, point_y))

    if len(points) >= 2:
        pygame.draw.lines(surface, color, False, points, 1)
    elif len(points) == 1:
        pygame.draw.circle(surface, color, points[0], 2)

def main():
    pygame.display.set_caption('Modern Snake Game')
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    try:
        font_icon = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_MEDIUM)
        font_panel = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_SMALL)
        font_tiny = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_TINY)
    except:
        font_icon = pygame.font.SysFont('arial', FONT_SIZE_MEDIUM - 2)
        font_panel = pygame.font.SysFont('arial', FONT_SIZE_SMALL - 2)
        font_tiny = pygame.font.SysFont('arial', FONT_SIZE_TINY - 1)

    current_speed = 15
    current_volume = 1
    mute = False
    current_fill_percent = 0
    show_path_visualization = False
    current_theme = "default"
    fps_history: Deque[float] = deque(maxlen=200)

    while True:
        mode, updated_speed, updated_volume, updated_mute, updated_fill_percent, updated_show_path, updated_theme = start_screen(
            screen,
            clock,
            current_speed,
            current_volume,
            mute,
            current_fill_percent,
            show_path_visualization,
            current_theme
        )
        current_speed = updated_speed
        current_volume = updated_volume
        mute = updated_mute
        current_fill_percent = updated_fill_percent
        show_path_visualization = updated_show_path
        current_theme = updated_theme
        set_theme(current_theme)

        initial_current_speed = current_speed
        min_speed = 5  # Минимальная скорость игры

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
                                   min_speed, 5000, snake.speed, "",
                                   power=2.5)

        panel_alpha = 76

        game_running = True
        while game_running:
            mouse_pos = pygame.mouse.get_pos()
            is_panel_hovered = speed_panel_rect.collidepoint(mouse_pos)
            panel_alpha = 255 if is_panel_hovered else 76

            game_controls_active = not is_panel_hovered

            game_speed_slider.value = snake.speed
            game_speed_slider.update_handle_pos()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    if confirmation_dialog(screen, clock, "Quit Game?"):
                        pygame.quit()
                        sys.exit()

                panel_interaction = False
                if is_panel_hovered:
                    if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                        game_speed_slider.handle_event(event)
                        snake.speed = int(game_speed_slider.value)
                        panel_interaction = True

                # Обработка клавиатурного ввода ВСЕГДА, даже при наведении на ползунок
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # ESC - выход в главное меню
                        game_running = False
                    
                    # Управление змейкой
                    if snake.mode == 'manual':
                        if event.key == pygame.K_UP: snake.turn(UP)
                        elif event.key == pygame.K_DOWN: snake.turn(DOWN)
                        elif event.key == pygame.K_LEFT: snake.turn(LEFT)
                        elif event.key == pygame.K_RIGHT: snake.turn(RIGHT)
                        elif event.key == pygame.K_w: snake.turn(UP)
                        elif event.key == pygame.K_s: snake.turn(DOWN)
                        elif event.key == pygame.K_a: snake.turn(LEFT)
                        elif event.key == pygame.K_d: snake.turn(RIGHT)
                    
                    # Обрабатываем нажатие клавиш скорости игры
                    if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                        snake.speed = min(5000, snake.speed + 10)
                        game_speed_slider.value = snake.speed
                        game_speed_slider.update_handle_pos()
                    if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                        snake.speed = max(min_speed, snake.speed - 10)
                        game_speed_slider.value = snake.speed
                        game_speed_slider.update_handle_pos()
                    
                    # Пауза по кнопке P или пробел
                    if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                        pause_screen(screen, clock)
                    
                    # Обрабатываем изменение темы по Q/E
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
                            # Обработка случая, если current_theme некорректен
                            print(f"Warning: Current theme '{current_theme}' not found in definitions during switch.")
                            current_theme = "default" # Сброс на дефолт
                            set_theme(current_theme)
                            snake._update_caches()
                            food.color = current_colors['food'] # Обновляем цвет еды


                if not game_running:
                    break

            if not game_running:
                break

            collision = snake.move(food.position)

            if collision:
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

            elif snake.get_head_position() == food.position:
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

            current_fps = clock.get_fps()
            fps_history.append(current_fps)

            graph_width = 100
            text_width = 45
            padding = 5
            total_width = graph_width + padding + text_width
            graph_height = 50
            margin_right = 10
            margin_bottom = 10

            widget_x = SCREEN_WIDTH - total_width - margin_right
            widget_y = SCREEN_HEIGHT - graph_height - margin_bottom
            fps_widget_rect = pygame.Rect(widget_x, widget_y, total_width, graph_height)

            graph_x_rel = 0
            graph_y_rel = 0
            text_x_rel = graph_width + padding
            text_y_rel = 0

            is_fps_widget_hovered = fps_widget_rect.collidepoint(mouse_pos)
            fps_widget_alpha = 255 if is_fps_widget_hovered else 76
            fps_bg_color_opaque = COLOR_PANEL_BG

            fps_widget_surface = pygame.Surface(fps_widget_rect.size, pygame.SRCALPHA)

            pygame.draw.rect(fps_widget_surface, fps_bg_color_opaque, fps_widget_surface.get_rect(), border_radius=4)

            draw_fps_graph(fps_widget_surface, fps_history, graph_x_rel, graph_y_rel, graph_width, graph_height, color=current_colors['text_highlight'])

            if fps_history:
                min_fps = min(fps_history)
                max_fps_hist = max(fps_history)
                avg_fps = sum(fps_history) / len(fps_history)
                text_margin_in_area = 3

                max_text_surf = font_tiny.render(f"{max_fps_hist:.0f}", True, current_colors['text'])
                max_text_rect = max_text_surf.get_rect(topright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + text_margin_in_area))
                fps_widget_surface.blit(max_text_surf, max_text_rect)
                avg_text_surf = font_tiny.render(f"{avg_fps:.0f}", True, current_colors['text'])
                avg_text_rect = avg_text_surf.get_rect(midright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height // 2))
                fps_widget_surface.blit(avg_text_surf, avg_text_rect)
                min_text_surf = font_tiny.render(f"{min_fps:.0f}", True, current_colors['text'])
                min_text_rect = min_text_surf.get_rect(bottomright=(text_x_rel + text_width - text_margin_in_area, graph_y_rel + graph_height - text_margin_in_area))
                fps_widget_surface.blit(min_text_surf, min_text_rect)

            fps_widget_surface.set_alpha(fps_widget_alpha)

            screen.blit(fps_widget_surface, fps_widget_rect.topleft)

            panel_bg_color_tuple = (current_colors['panel_bg'].r, current_colors['panel_bg'].g, current_colors['panel_bg'].b, panel_alpha)
            panel_surface = pygame.Surface(speed_panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(panel_surface, panel_bg_color_tuple, panel_surface.get_rect(), border_radius=4)

            panel_title_surf = font_panel.render("Speed", True, current_colors['text_white'])
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

# Добавляем новую функцию для диалога несохраненных изменений
def unsaved_settings_dialog(surface, clock):
    # Создаем затемненный фон
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(210) # Устанавливаем базовую прозрачность
    overlay.fill(current_colors['background']) # Используем цвет фона темы
    # Уменьшаем альфу еще немного для большего затемнения (убедимся, что не станет < 0)
    current_alpha = overlay.get_alpha() or 255 # Получаем альфу, если None, берем 255
    overlay.set_alpha(max(0, int(current_alpha * 0.85))) # Уменьшаем и ставим новую, не ниже 0

    surface.blit(overlay, (0, 0))

    # Определяем шрифты
    try:
        font_title = pygame.font.SysFont(FONT_NAME_PRIMARY, FONT_SIZE_LARGE, bold=True)
        # font_text больше не нужен
    except:
        font_title = pygame.font.SysFont('arial', FONT_SIZE_LARGE - 2, bold=True)
        # font_text больше не нужен

    # Заголовок диалога
    title_surf = font_title.render("Unsaved Changes", True, current_colors['text_white'])
    # message_surf больше не нужен

    # Определяем размеры диалога (уменьшаем высоту)
    dialog_width = 500
    dialog_height = 160 # Уменьшенная высота
    dialog_rect = pygame.Rect(0, 0, dialog_width, dialog_height)
    dialog_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Размещаем заголовок (ближе к центру по вертикали)
    title_rect = title_surf.get_rect(center=(dialog_rect.centerx, dialog_rect.top + 40))
    # message_rect больше не нужен

    # Определяем кнопки (поднимаем выше)
    button_width = 130
    button_height = 50
    button_spacing = 25
    total_buttons_width = 3 * button_width + 2 * button_spacing

    save_button_rect = pygame.Rect(0, 0, button_width, button_height)
    discard_button_rect = pygame.Rect(0, 0, button_width, button_height)
    cancel_button_rect = pygame.Rect(0, 0, button_width, button_height)

    start_x = dialog_rect.centerx - total_buttons_width // 2
    buttons_y = dialog_rect.bottom - 65 # Подняли кнопки
    save_button_rect.topleft = (start_x, buttons_y)
    discard_button_rect.topleft = (save_button_rect.right + button_spacing, buttons_y)
    cancel_button_rect.topleft = (discard_button_rect.right + button_spacing, buttons_y)

    buttons = {
        "save": {"rect": save_button_rect, "text": "Save", "color": current_colors['button_hover'], "hovered": False, "clicked": False}, # Цвет "Успех/Применить"
        "discard": {"rect": discard_button_rect, "text": "Discard", "color": current_colors['gameover'], "hovered": False, "clicked": False}, # Цвет "Предупреждение/Отмена"
        "cancel": {"rect": cancel_button_rect, "text": "Cancel", "color": current_colors['button'], "hovered": False, "clicked": False} # Стандартный цвет кнопки
    }

    running = True
    result = "cancel" # По умолчанию отмена, если просто закрыть окно

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Обновляем состояния кнопок
        for key, data in buttons.items():
            buttons[key]["hovered"] = data["rect"].collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Позволяем закрыть игру из этого диалога
                if confirmation_dialog(surface, clock, "Quit Game?"):
                    pygame.quit()
                    sys.exit()
                else: # Если отказались выходить, возвращаем на фон
                    temp_surface = surface.copy()
                    surface.blit(overlay, (0,0)) # Перерисовываем оверлей


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    for key, data in buttons.items():
                        if data["hovered"]:
                            buttons[key]["clicked"] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                clicked_on_button = False
                for key, data in buttons.items():
                    if data["clicked"] and data["hovered"]:
                        if eat_sound: # Используем глобальную переменную eat_sound
                            eat_sound.play()
                        result = key
                        running = False
                        clicked_on_button = True
                    buttons[key]["clicked"] = False
                # Если клик был вне кнопок, можно считать это отменой? Или оставить как есть.
                # Пока оставляем как есть - нужно кликнуть на кнопку для действия.

            elif event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE: # Escape из диалога = Cancel
                      result = "cancel"
                      running = False


        # Рисуем диалоговое окно (на временной поверхности, чтобы не перерисовывать фон каждый раз)
        temp_surface = surface.copy() # Копируем текущее состояние экрана (с оверлеем)
        pygame.draw.rect(temp_surface, current_colors['panel_bg'], dialog_rect, border_radius=10) # Используем цвет панели для фона
        pygame.draw.rect(temp_surface, current_colors['text_highlight'], dialog_rect, width=2, border_radius=10) # Рамка в цвет темы

        temp_surface.blit(title_surf, title_rect)
        # temp_surface.blit(message_surf, message_rect) # Убрали отрисовку сообщения

        # Рисуем кнопки
        for key, data in buttons.items():
            # Передаем правильные цвета в draw_button
            base_color = data["color"]
            hover_color = data["color"].lerp(current_colors['background'], 0.2) # Используем логику из draw_button
            click_color = current_colors['button_click']
            button_color_to_use = base_color
            if data["clicked"]:
                button_color_to_use = click_color
            elif data["hovered"]:
                 # Не используем hover_color напрямую, draw_button сама обработает подсветку при hover
                 pass

            draw_button(temp_surface, data["rect"], base_color, data["text"], data["hovered"], data["clicked"])

        surface.blit(temp_surface, (0,0)) # Отображаем временную поверхность

        pygame.display.update(dialog_rect.inflate(4,4)) # Обновляем только область диалога для производительности
        clock.tick(60)

    # Восстанавливаем фон перед выходом (важно, чтобы не остался оверлей)
    # Это будет сделано в вызывающей функции (settings_screen) при перерисовке

    return result

if __name__ == '__main__':
    pygame.init()
    pygame.mixer.init()
    set_theme("default")
    main()
