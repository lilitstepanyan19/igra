import os
import math
import pygame

from paths import file_path


class Cat:

    def __init__(
        self,
        fps,
        screen_width,
        screen_height,
        world_width,
        world_height,
        world_num,
        level_num,
        person_name="cat",
        cat_scale=1.0,
        cat_width=120,
        cat_height=120,
        cat_y_offset=0,
    ):
        self.fps = fps
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        self.cat_scale = cat_scale
        self.cat_width = cat_width
        self.cat_height = cat_height
        self.cat_default_height = self.screen_height * 0.15  # базовая высота от нижнего края
        self.cat_y_offset = cat_y_offset

        self.cat_kangaroo_jump_amplitude = 0
        self.cat_kangaroo_jump_speed = 0.1
        self.cat_kangaroo_phase = 0

        # --- Загрузка кадров персонажа ---
        self.cat_right = self.load_cat("right", world_num, level_num, person_name)
        self.cat_left = self.load_cat("left", world_num, level_num, person_name)
        self.cat_frames = self.cat_right
        self.cat_index = 0.0

        self.GROUND_Y = self.world_height - int(self.cat_default_height) - self.cat_y_offset

        self.cat_x = 300.0
        self.cat_y = float(self.GROUND_Y)
        self.CAT_BOUNDS = pygame.Rect(0, 100, self.world_width, self.world_height - int(self.world_height * 0.15))
        self.cat_vy = 0.0
        self.GRAVITY = 0.6
        self.JUMP_POWER = -20.0
        self.on_ground = True

        self.cat_speed = 10.0
        self.cat_anim_speed = 0.5
        self.mouse_speed = 0.02

        # Кэшированный прямоугольник кота
        first_frame = self.cat_frames[0]
        self._rect = first_frame.get_rect(center=(int(self.cat_x), int(self.cat_y)))

    def load_cat(self, direction, world_num, level_num, person_name="cat"):
        frames = []
        folder = f"images/world_{world_num}/world_{world_num}_{level_num}/person"
        if not os.path.exists(folder):
            folder = "images/world_1/world_1_1/person"

        for name in sorted(os.listdir(folder)):
            if name.endswith(f"_{direction}.webp") and name.startswith(f"{person_name}_"):
                path = os.path.join(folder, name)
                try:
                    img = pygame.image.load(file_path(path)).convert_alpha()
                    size_width = int(self.cat_width * self.cat_scale)
                    size_height = int(self.cat_height * self.cat_scale)
                    img = pygame.transform.scale(img, (size_width, size_height)).convert_alpha()
                    frames.append(img)
                except pygame.error as e:
                    print(f"Не удалось загрузить {path}: {e}")

        if not frames:
            raise Exception(f"No cat images for '{person_name}' direction '{direction}' in {folder}")

        return frames

    @property
    def cat_rect(self):
        """Возвращает актуальный кэшированный Rect в мировых координатах."""
        self._rect.center = (int(self.cat_x), int(self.cat_y))
        return self._rect

    def update(self, camera_x, camera_y, touch_down=False, touch_pos=(0, 0)):
        moved = False
        keys = pygame.key.get_pressed()

        # 1. Бег по стрелкам (ПК)
        if keys[pygame.K_LEFT]:
            self.cat_x -= self.cat_speed * 1.2
            self.cat_frames = self.cat_left
            moved = True
        elif keys[pygame.K_RIGHT]:
            self.cat_x += self.cat_speed * 1.2
            self.cat_frames = self.cat_right
            moved = True

        # Прыжок (клавиатура)
        if keys[pygame.K_SPACE] and self.on_ground:
            self.cat_vy = self.JUMP_POWER
            self.on_ground = False

        # 2. ВОЗВРАЩЕНО: Движение за курсором мыши (если не зажата стрелка и нет касания Android)
        if not touch_down and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            mx, _ = pygame.mouse.get_pos()
            mx_world = mx + camera_x
            dx = mx_world - self.cat_x
            if abs(dx) > 5:
                self.cat_x += dx * self.mouse_speed
                self.cat_frames = self.cat_right if dx > 0 else self.cat_left
                moved = True

        # 3. Сенсорное управление на Android (при зажатии пальца)
        if touch_down:
            mx, my = touch_pos

            # Движение влево / вправо по половинам экрана
            if mx < self.screen_width // 2:
                self.cat_x -= self.cat_speed * 1.8
                self.cat_frames = self.cat_left
                moved = True
            else:
                self.cat_x += self.cat_speed * 1.8
                self.cat_frames = self.cat_right
                moved = True

            # Прыжок при касании верхней половины экрана
            if my < self.screen_height // 2 and self.on_ground:
                self.cat_vy = self.JUMP_POWER
                self.on_ground = False

        # 4. Кенгуру-прыжки или стандартная физика
        if self.on_ground and moved:
            self.cat_kangaroo_phase += self.cat_kangaroo_jump_speed
            self.cat_y = (
                self.GROUND_Y - math.sin(self.cat_kangaroo_phase) * self.cat_kangaroo_jump_amplitude
            )

        # Гравитация и падение
        if not self.on_ground:
            self.cat_vy += self.GRAVITY
            self.cat_y += self.cat_vy

            if self.cat_y >= self.GROUND_Y:
                self.cat_y = self.GROUND_Y
                self.cat_vy = 0.0
                self.on_ground = True

        # Обновляем координаты кэшированного прямоугольника
        self._rect.center = (int(self.cat_x), int(self.cat_y))

        # Ограничения по границам уровня
        if self._rect.left < self.CAT_BOUNDS.left:
            self.cat_x += self.CAT_BOUNDS.left - self._rect.left
        elif self._rect.right > self.CAT_BOUNDS.right:
            self.cat_x -= self._rect.right - self.CAT_BOUNDS.right

        # Обновляем кадр анимации
        if moved:
            self.cat_index += self.cat_anim_speed
            if self.cat_index >= len(self.cat_frames):
                self.cat_index = 0.0
        else:
            self.cat_index = 0.0

        # Мягкая оттяжка от краев видимого экрана
        screen_x = self.cat_x - camera_x
        margin = self.screen_width * 0.1

        if screen_x < margin:
            self.cat_x += (margin - screen_x) * 0.2
        elif screen_x > self.screen_width - margin:
            self.cat_x -= (screen_x - (self.screen_width - margin)) * 0.2

    def draw(self, screen, camera_x, camera_y):
        """Отрисовка кадра персонажа с округлением до целых пикселей"""
        frame = self.cat_frames[int(self.cat_index)]
        
        draw_x = int(self.cat_x - camera_x - frame.get_width() // 2)
        draw_y = int(self.cat_y - camera_y - frame.get_height() // 2)

        screen.blit(frame, (draw_x, draw_y))