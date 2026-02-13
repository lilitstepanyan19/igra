import os
import importlib
import inspect
import pygame
import pygame.mixer

from cat import Cat
from camera import Camera
from save import save_progress
from letters_screen import LettersScreen


WORLD_WIDTH = 15000
WORLD_HEIGHT = 600

WIDTH, HEIGHT = 900, 600

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

LIVES_COUNT = 3
NEED = 4
SCORE = 0
LETTER_COUNT = 20

#                             "ԶԷԸԹԺԻԼԽԾՀՂՃՄՅՆՉՊՋՌՎՏՐՑՈՒՓԵՕՖ"
ARMENIAN_LETTERS = "ԱՍՇՁԲԿԵԳՈՔԴԶԷԸԹԺԻԼԽԾՀՂՃՄՅՆՉՊՋՌՎՏՐՑՈՒՓԵՕՖ"


class WorldBase:
    def __init__(self, game, lives=None):
        pygame.mixer.init()
        self.game = game
        self.score = 0
        self.need = 1
        self.target = None
        self.cat = None
        self.camera = None

        self.person_name = "cat"

        self.eat_sound = pygame.mixer.Sound("sounds/eat.wav")
        self.eat_bad_sound = pygame.mixer.Sound("sounds/eat.wav")
        self.level_up_sound = pygame.mixer.Sound("sounds/level_up.wav")

        self.lives = LIVES_COUNT if lives is None else lives
        self.heart_img = pygame.image.load("images/heart.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (32, 32))

        self.finish_time = None        # момент завершения уровня
        self.next_level_class = None   # класс следующего уровня
        self.game_completed = False
        self.level_wait_time = 3000
        
        self.hit_cooldown = 1000   # мс (1 секунда)
        self.last_hit_time = 0

        self.letter_bg_imgs = []

        # --- определяем мир и уровень по имени класса ---
        name = self.__class__.__name__  # например World_1_1
        _, w, l = name.split("_")
        self.world_num = int(w)
        self.level_num = int(l)

    def start(self):
        self.cat = Cat(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            WORLD_WIDTH,
            WORLD_HEIGHT,
            self.world_num,
            self.level_num,
            self.person_name,
            cat_scale=getattr(self, "cat_scale", 1.0),  # ✅ ВАЖНО
            cat_width=getattr(self, "cat_width", 120),
            cat_height=getattr(self, "cat_height", 120),
            cat_y_offset=getattr(self, "cat_y_offset", 0),
        )
        self.cat.GRAVITY = getattr(self, "GRAVITY", 0.6)
        self.cat.JUMP_POWER = getattr(self, "JUMP_POWER", -20)
        self.cat.cat_anim_speed = getattr(self, 'cat_anim_speed', 0.15)
        self.cat.cat_speed = getattr(self, 'cat_speed', 0.3)
        self.cat.cat_kangaroo_jump_amplitude = getattr(self, "cat_kangaroo_jump_amplitude", 1)
        self.cat.cat_kangaroo_jump_speed = getattr(self, "cat_kangaroo_jump_speed", 0.1)

        self.camera = Camera(WIDTH, WORLD_WIDTH)

    def load_bg(self, bg_img_num=1):
        path = f"images/world_{self.world_num}/world_{self.world_num}_{self.level_num}/bg_img/bg_{bg_img_num}.png"

        if not os.path.exists(path):
            path = "images/world_1/world_1_1/bg_img/bg_1.png"

        return pygame.image.load(path).convert_alpha()

    def load_letter_bgs(self, world_num, level_num, folder_name="letter_bg"):
        folder = f"images/world_{world_num}/world_{world_num}_{level_num}/{folder_name}/"

        imgs = []

        if os.path.exists(folder):
            for name in sorted(os.listdir(folder)):
                if name.startswith("letter_bg") and name.endswith(".png"):
                    path = os.path.join(folder, name)
                    img = pygame.image.load(path).convert_alpha()
                    imgs.append(img)

        # 👉 если в мире нет своих фонов — берём из world_1_1
        if not imgs:
            fallback = "images/world_1/world_1_1/letter_bg/"
            if os.path.exists(fallback):
                for name in sorted(os.listdir(fallback)):
                    if name.startswith("letter_bg") and name.endswith(".png"):
                        path = os.path.join(fallback, name)
                        img = pygame.image.load(path).convert_alpha()
                        imgs.append(img)

        # ===== обработка фонов букв (общие параметры) =====
        new_imgs = []
        for img in imgs:
            img = pygame.transform.smoothscale(img, (80, 80)).convert_alpha()  # размер
            img.set_alpha(220)  # прозрачность
            new_imgs.append(img)

        imgs = new_imgs
        self.letter_bg_imgs = imgs
        return imgs

    def update(self):
        if self.camera:
            self.camera.update(self.cat.cat_x if self.cat else 0)

        if self.cat:
            self.cat.update(self.camera.camera_x)

        if self.is_finished():
            if self.finish_time is None:
                self.finish_time = pygame.time.get_ticks()
                self.level_up_sound.play()
                self.next_level = self.next_world()

                if self.next_level is None:
                    self.game_completed = True

            else:
                if pygame.time.get_ticks() - self.finish_time >= self.level_wait_time:
                    if self.next_level:
                        self.next_level.start()
                        self.game.world = self.next_level

    def draw(self, screen):
        pass

    def handle_events(self, events):
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
            color = getattr(self, "good_target_color", (0, 180, 0))  # если нет — зелёный
            target_surf = self.game.font_good.render(self.target, True, color)
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

        # --- текущий файл и папка ---
        file_path = inspect.getfile(self.__class__)
        folder = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        # world_1_2_rain.py -> 1_2_rain
        name = file_name.replace("world_", "").replace(".py", "")
        parts = name.split("_")

        world_num = int(parts[0])
        level_num = int(parts[1]) + 1

        package = self.__class__.__module__.rsplit(".", 1)[0]

        # ========== 1. ищем следующий уровень в той же папке ==========
        for f in os.listdir(folder):
            if f.startswith(f"world_{world_num}_{level_num}"):
                module_name = f"{package}.{f[:-3]}"
                module = importlib.import_module(module_name)

                save_progress(f"World_{world_num}_{level_num}")

                WorldClass = getattr(module, f"World_{world_num}_{level_num}")

                return WorldClass(self.game, lives=self.lives)

        # ========== 2. ищем следующий мир ==========
        worlds_root = os.path.dirname(folder)

        next_world_num = world_num + 1
        next_world_folder = None

        for d in os.listdir(worlds_root):
            if d.startswith(f"world_{next_world_num}_"):
                next_world_folder = d
                break

        if not next_world_folder:
            return None

        next_folder_path = os.path.join(worlds_root, next_world_folder)

        first_world_class = None
        first_world_module = None

        for f in os.listdir(next_folder_path):
            if f.startswith(f"world_{next_world_num}_1"):
                module_name = f"worlds.{next_world_folder}.{f[:-3]}"
                first_world_module = importlib.import_module(module_name)
                first_world_class = getattr(first_world_module, f"World_{next_world_num}_1")
                break

        if not first_world_class:
            return None

        target = ARMENIAN_LETTERS[next_world_num - 1]
        target_lower = target.lower()

        letters = [target, target, target_lower, target_lower]

        # --- функция перехода в первый уровень следующего мира ---
        def go_next_world():
            save_progress(f"World_{next_world_num}_1")
            return first_world_class(self.game, lives=self.lives)

        return LettersScreen(self.game, letters, next_world_num, go_next_world)

        return None
