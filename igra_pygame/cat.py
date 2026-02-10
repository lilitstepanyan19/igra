import pygame
import os
import math

CAT_SPEED = 0.3
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

        self.cat_kangaroo_jump_amplitude = 20  # высота подпрыгивания
        self.cat_kangaroo_jump_speed = 0.1  # скорость подпрыгивания
        self.cat_kangaroo_phase = 0  # для синуса

        # --- load cat frames ---
        self.cat_right = self.load_cat("right", world_num, level_num, person_name)
        self.cat_left = self.load_cat("left", world_num, level_num, person_name)
        self.cat_frames = self.cat_right
        self.cat_index = 0

        self.cat_x, self.cat_y = self.screen_width // 2, self.screen_height // 2
        self.CAT_BOUNDS = pygame.Rect(0, 100, self.world_width, self.world_height - 150)

        # --- physics ---
        self.cat_vy = 0
        self.GRAVITY = 0.6
        self.JUMP_POWER = -20
        self.cat_anim_speed = CAT_ANIM_SPEED
        self.on_ground = False

        self.GROUND_Y = self.world_height - int(self.cat_default_height) - self.cat_y_offset

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
                    img = pygame.image.load(path).convert_alpha()
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

        # бег по стрелкам
        if keys[pygame.K_LEFT]:
            self.cat_x -= CAT_SPEED
            self.cat_frames = self.cat_left
            moved = True
        if keys[pygame.K_RIGHT]:
            self.cat_x += CAT_SPEED
            self.cat_frames = self.cat_right
            moved = True

        # прыжок
        if keys[pygame.K_SPACE] and self.on_ground:
            self.cat_vy = self.JUMP_POWER
            self.on_ground = False

        # гравитация
        self.cat_vy += self.GRAVITY

        if self.cat_y > self.GROUND_Y:
            self.cat_y = self.GROUND_Y
            self.cat_vy = 0
            self.on_ground = True

        # mouse X только
        mx, _ = pygame.mouse.get_pos()
        mx_world = mx + camera_x
        dx = mx_world - self.cat_x
        if abs(dx) > 5:
            self.cat_x += dx * MOUSE_SPEED
            self.cat_frames = self.cat_right if dx > 0 else self.cat_left
            moved = True

        # --- кенгуру-ходьба или обычная гравитация ---
        if self.on_ground and moved:
            self.cat_kangaroo_phase += self.cat_kangaroo_jump_speed
            self.cat_y = (
                self.GROUND_Y
                - math.sin(self.cat_kangaroo_phase) * self.cat_kangaroo_jump_amplitude
            )
        else:
            # если в воздухе — прыжок с гравитацией
            self.cat_y += self.cat_vy
            if self.cat_y >= self.GROUND_Y:
                self.cat_y = self.GROUND_Y
                self.cat_vy = 0
                self.on_ground = True

        # границы X
        rect = self.cat_rect
        if rect.left < self.CAT_BOUNDS.left:
            self.cat_x += self.CAT_BOUNDS.left - rect.left
        if rect.right > self.CAT_BOUNDS.right:
            self.cat_x -= rect.right - self.CAT_BOUNDS.right

        # анимация
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
