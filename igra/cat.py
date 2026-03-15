import pygame
import os
import math

from paths import file_path

CAT_SPEED = 1
CAT_ANIM_SPEED = 0.15
MOUSE_SPEED = 0.02

class Cat:

    def __init__(
        self,
        screen_width,
        screen_height,
        world_width,
        world_height,
        world_num,
        level_num,
        person_name="cat",  # новый аргумент
        cat_scale=1.0,
        cat_width=120,
        cat_height=120,
        cat_default_height=120,
        cat_y_offset=0,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        self.cat_scale = cat_scale
        self.cat_width = cat_width
        self.cat_height = cat_height
        self.cat_default_height = cat_default_height
        self.cat_y_offset = cat_y_offset

        self.cat_kangaroo_jump_amplitude = 0  # высота подпрыгивания
        self.cat_kangaroo_jump_speed = 0.1  # скорость подпрыгивания
        self.cat_kangaroo_phase = 0  # для синуса

        # --- load cat frames ---
        self.cat_right = self.load_cat("right", world_num, level_num, person_name)
        self.cat_left = self.load_cat("left", world_num, level_num, person_name)
        self.cat_frames = self.cat_right
        self.cat_index = 0

        self.GROUND_Y = self.world_height - int(self.cat_default_height) - self.cat_y_offset
        self.cat_x, self.cat_y = self.screen_width // 2, self.GROUND_Y
        self.CAT_BOUNDS = pygame.Rect(0, 100, self.world_width, self.world_height - 150)

        # --- physics ---
        self.cat_vy = 0
        self.GRAVITY = 0.6
        self.JUMP_POWER = -20
        self.on_ground = False

        self.cat_anim_speed = CAT_ANIM_SPEED
        self.cat_speed = CAT_SPEED

    def load_cat(self, direction, world_num, level_num, person_name="cat"):
        frames = []
        folder = f"images/world_{world_num}/world_{world_num}_{level_num}/person"
        if not os.path.exists(folder):
            folder = f"images/world_1/world_1_1/person"

        for name in sorted(os.listdir(folder)):
            if name.endswith(f"_{direction}.png") and name.startswith(
                f"{person_name}_"
            ):
                path = os.path.join(folder, name)
                try:
                    img = pygame.image.load(file_path(path)).convert_alpha()
                    size_width = int(self.cat_width * self.cat_scale)
                    size_height = int(self.cat_height * self.cat_scale)
                    img = pygame.transform.scale(img, (size_width, size_height))
                    frames.append(img)
                except pygame.error as e:
                    print(f"Не удалось загрузить {path}: {e}")
        if not frames:
            raise Exception(
                f"No cat images for '{person_name}' direction '{direction}' in {folder}"
            )

        return frames

    @property
    def cat_rect(self):
        return self.cat_frames[int(self.cat_index)].get_rect(
            center=(self.cat_x, self.cat_y)
        )

    def update(self, camera_x):
        moved = False
        keys = pygame.key.get_pressed()

        # === 1. Клавиатура (ПК) — всегда работает ===
        if keys[pygame.K_LEFT]:
            self.cat_x -= self.cat_speed
            self.cat_frames = self.cat_left
            moved = True

        if keys[pygame.K_RIGHT]:
            self.cat_x += self.cat_speed
            self.cat_frames = self.cat_right
            moved = True

        if keys[pygame.K_SPACE] and self.on_ground:
            self.cat_vy = self.JUMP_POWER
            self.on_ground = False

        # === 2. Касание пальцем (Android) ===
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()

            # Левая половина экрана — влево
            if mx < self.screen_width // 2:
                self.cat_x -= self.cat_speed * 1.8
                self.cat_frames = self.cat_left
                moved = True

            # Правая половина экрана — вправо
            else:
                self.cat_x += self.cat_speed * 1.8
                self.cat_frames = self.cat_right
                moved = True

            # Прыжок — верхняя половина экрана
            if my < self.screen_height // 2 and self.on_ground:
                self.cat_vy = self.JUMP_POWER
                self.on_ground = False

        # === 3. Гравитация (всегда работает) ===
        self.cat_vy += self.GRAVITY
        self.cat_y += self.cat_vy

        # === 4. Приземление ===
        if self.cat_y >= self.GROUND_Y:
            self.cat_y = self.GROUND_Y
            self.cat_vy = 0
            self.on_ground = True

        # === 5. Кенгуру-эффект при ходьбе ===
        if self.on_ground and moved:
            self.cat_kangaroo_phase += self.cat_kangaroo_jump_speed
            self.cat_y = (
                self.GROUND_Y
                - math.sin(self.cat_kangaroo_phase) * self.cat_kangaroo_jump_amplitude
            )

        # === 6. Границы мира ===
        if self.cat_x < 50:
            self.cat_x = 50
        if self.cat_x > self.world_width - 50:
            self.cat_x = self.world_width - 50

        # === 7. Анимация ===
        if moved:
            self.cat_index += self.cat_anim_speed
            if self.cat_index >= len(self.cat_frames):
                self.cat_index = 0
        else:
            self.cat_index = 0

    def draw(self, screen, camera_x):
        """Рисует кота на экране с учётом камеры"""
        frame = self.cat_frames[int(self.cat_index)]

        rect = frame.get_rect(center=(self.cat_x - camera_x, self.cat_y))

        screen.blit(frame, rect)
