# Современная Змейка

Реализация классической игры "Змейка" на Python с использованием библиотеки Pygame.

## Возможности

*   **Ручной режим:** Классическое управление змейкой с клавиатуры.
*   **Автопилот (AI):** Змейка сама ищет путь к еде (A*), пытаясь при этом не запереть себя (эвристика пути к хвосту).
*   **Начальное заполнение:** Возможность выбрать на старте процент поля (от 0% до 95%), который змейка будет занимать изначально, укладываясь "гармошкой".
*   **Реплей:** После проигрыша доступна запись последних ~100 ходов с ползунком перемотки.
*   **Настройка скорости:** Регулируется ползунком (иконка SPD) или клавишами +/-.
*   **Звуки:** Эффекты поедания еды (`eat.wav`) и проигрыша (`melody.wav`). Громкость настраивается, звук можно отключить.
*   **UI:** Темная тема, ползунки, кнопки, чекбоксы.

## Запуск

1.  Требуется Python 3 и Pygame. Установка Pygame:
    ```bash
    pip install pygame
    ```
2.  Запуск скрипта:
    ```bash
    python main.py
    ```

## Управление

*   **Стрелки клавиатуры:** Управление змейкой в ручном режиме.
*   **P:** Пауза / Возобновить игру.
*   **+/- (на основной или цифровой клавиатуре):** Увеличение/уменьшение скорости.
*   **Клик по иконке "SPD":** Открыть/закрыть панель настройки скорости.
*   **Мышь:** Взаимодействие с кнопками, ползунками, чекбоксами в меню и на экране реплея.

## Сборка в EXE

Для сборки можно использовать PyInstaller:

```bash
pyinstaller --onefile --windowed --add-data "eat.wav;." --add-data "melody.wav;." main.py
```

Готовый `.exe` файл будет создан в папке `dist`.

---
*Змейка на Pygame.*
