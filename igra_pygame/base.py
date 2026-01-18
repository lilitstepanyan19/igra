import os
import importlib
import pygame
from cat import Cat
from camera import Camera


WORLD_WIDTH = 10000
WORLD_HEIGHT = 600

WIDTH, HEIGHT = 900, 600

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

LIVES_COUNT = 3

class WorldBase:
    armenian_letters = "ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՈՒՓՔԵՕՖ"

    def __init__(self, game):
        self.game = game
        self.score = 0
        self.need = 1
        self.target = None
        self.cat = None
        self.camera = None

        self.lives = LIVES_COUNT
        self.heart_img = pygame.image.load("images/heart.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (32, 32))

        self.hit_cooldown = 1000   # мс (1 секунда)
        self.last_hit_time = 0

        self.letter_bg_imgs = []

        # --- определяем мир и уровень по имени класса ---
        name = self.__class__.__name__  # например World_1_1
        _, w, l = name.split("_")
        self.world_num = int(w)
        self.level_num = int(l)

    def start(self):
        self.cat = Cat(SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
        self.camera = Camera(WIDTH, WORLD_WIDTH)

    def load_letter_bgs(self, world_num, folder_name="letter_bg"):
        """Динамически загружает все картинки для букв данного мира"""
        folder = f"images/world_{world_num}/{folder_name}/"
        if not os.path.exists(folder):
            return []

        imgs = []
        for name in sorted(os.listdir(folder)):
            if name.startswith("letter_bg") and name.endswith(".png"):
                path = os.path.join(folder, name)
                img = pygame.image.load(path).convert_alpha()
                imgs.append(img)
        self.letter_bg_imgs = imgs
        return imgs

    def update(self):
        if not self.cat or not self.camera:
            return
        self.cat.update(self.camera.camera_x)
        self.camera.update(self.cat.cat_x)

    def draw(self, screen):
        pass

    def draw_hud(self, screen):
        take_text = "Բռնիր "
        count_text = f" {self.need - self.score} հատ"

        # Рендерим части
        take_surf = self.game.font_hud.render(take_text, True, (0, 0, 0))
        count_surf = self.game.font_hud.render(count_text, True, (0, 0, 0))

        # Позиции
        x, y = 20, 60

        screen.blit(take_surf, (x, y))
        x += take_surf.get_width()

        if self.letter_bg_imgs:
            bg_img = self.letter_bg_imgs[0]  # или random.choice(self.letter_bg_imgs)
            bg_rect = bg_img.get_rect(topleft=(x, y - 10))
            screen.blit(bg_img, bg_rect)

            # текст поверх фона
            target_surf = self.game.font_good.render(self.target, True, (0, 180, 0))
            target_rect = target_surf.get_rect(center=bg_rect.center)
            screen.blit(target_surf, target_rect)
            x += bg_rect.width
        else:
            # если фона нет — обычная буква
            target_surf = self.game.font_good.render(self.target, True, (0, 220, 0))
            screen.blit(target_surf, (x, y - 5))
            x += target_surf.get_width()

        screen.blit(count_surf, (x, y))

        # --- Большое сердце и количество жизней ---
        max_heart_size = 80  # максимальный размер сердца
        min_heart_size = 40  # размер, если lives = 1

        # размер сердца пропорционален количеству жизней
        if self.lives > 0:
            heart_size = min_heart_size + (max_heart_size - min_heart_size) * (self.lives / LIVES_COUNT)
        else:
            heart_size = min_heart_size

        heart_img_scaled = pygame.transform.scale(self.heart_img, (int(heart_size), int(heart_size)))
        # координаты справа сверху
        heart_x = SCREEN_WIDTH - heart_size - 20
        heart_y = 20
        screen.blit(heart_img_scaled, (heart_x, heart_y))

        # показываем число жизней рядом
        lives_text = f"x {self.lives}"
        lives_surf = self.game.font_hud.render(lives_text, True, (0, 0, 0))
        lives_x = SCREEN_WIDTH - heart_size / 2 - lives_surf.get_width() / 2 - 20
        lives_y = heart_y + (heart_size - lives_surf.get_height()) / LIVES_COUNT
        screen.blit(lives_surf, (lives_x, lives_y))

        # --- WORLD / LEVEL и счет ---
        header_text = f"Աշխարհ {self.world_num}, Փուլ- {self.level_num}   {self.score}/{self.need}"
        header_surf = self.game.font_hud.render(header_text, True, (0, 0, 0))
        screen.blit(header_surf, (20, 20))

    def is_finished(self):
        return self.score >= self.need

    def next_world(self):
        w, l = self.world_num, self.level_num + 1

        for next_world_num, next_level_num in [(w, l), (w + 1, 1)]:
            class_name = f"World_{next_world_num}_{next_level_num}"
            module_name = f"worlds.world_{next_world_num}.world_{next_world_num}_{next_level_num}"
            try:
                module = importlib.import_module(module_name)
                next_cls = getattr(module, class_name)
                return next_cls(self.game)
            except (ModuleNotFoundError, AttributeError):
                continue

        # следующего уровня или мира нет
        return None
