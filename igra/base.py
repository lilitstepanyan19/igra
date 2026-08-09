import os
import importlib
import inspect
import pygame
import pygame.mixer

from paths import file_path

from cat import Cat
from camera import Camera
from save import save_progress
from letters_screen import LettersScreen
from levels_config import LEVELS_MAP

WORLD_WIDTH = 15000
WORLD_HEIGHT = 600

WIDTH, HEIGHT = 900, 600

FPS = 30

LIVES_COUNT = 3
NEED = 4
SCORE = 0
LETTER_COUNT = 20

#                              "ԴԶԷԸԹԺԻԼԽԾՀՂՃՅՉՊՋՌՎՏՐՑՈՒՓԵՕՖ"
ARMENIAN_LETTERS = "ԱՍՇՁԲԿԵԳՈՔՆՄԴԶԷԸԹԺԻԼԽԾՀՂՃՅՉՊՋՌՎՏՐՑՈՒՓԵՕՖ"


class WorldBase:
    def __init__(self, game, lives=None):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print("Mixer init error:", e)
        self.game = game
        self.score = 0
        self.need = 1
        self.target = None
        self.cat = None
        self.camera = None
        self.screen_width = game.base_width
        self.screen_height = game.base_height

        self.person_name = "cat"

        self.eat_sound = pygame.mixer.Sound(file_path("sounds/eat.ogg"))
        self.eat_bad_sound = pygame.mixer.Sound(file_path("sounds/eat.ogg"))
        self.level_up_sound = pygame.mixer.Sound(file_path("sounds/level_up.ogg"))

        self.lives = LIVES_COUNT if lives is None else lives
        
        # Оптимизация сердца
        self.heart_base_img = pygame.image.load(file_path("images/heart.webp")).convert_alpha()
        self.cached_heart_img = None
        self.cached_heart_lives = -1

        self.finish_time = None        # момент завершения уровня
        self.next_level_class = None   # класс следующего уровня
        self.game_completed = False
        self.level_wait_time = 3000

        self.hit_cooldown = 1000   # мс (1 секунда)
        self.last_hit_time = 0

        self.letter_bg_imgs = []

        # Кэш для текстовых поверхностей HUD
        self._hud_cache = {}

        # --- определяем мир и уровень по имени класса ---
        name = self.__class__.__name__  # например World_1_1
        _, w, l = name.split("_")
        self.world_num = int(w)
        self.level_num = int(l)

        self.touch_down = False
        self.touch_pos = (0, 0)

    def start(self):
        self.cat = Cat(
            FPS,
            self.screen_width,
            self.screen_height,
            WORLD_WIDTH,
            WORLD_HEIGHT,
            self.world_num,
            self.level_num,
            self.person_name,
            cat_scale=getattr(self, "cat_scale", 1.0),
            cat_width=getattr(self, "cat_width", 120),
            cat_height=getattr(self, "cat_height", 120),
            cat_y_offset=getattr(self, "cat_y_offset", 15),
        )
        self.cat.GRAVITY = getattr(self, "GRAVITY", 0.6)
        self.cat.JUMP_POWER = getattr(self, "JUMP_POWER", -(self.screen_height * 0.023))
        self.cat.cat_anim_speed = getattr(self, 'cat_anim_speed', 0.5)
        self.cat.cat_speed = getattr(self, 'cat_speed', 10)
        self.cat.cat_kangaroo_jump_amplitude = getattr(self, "cat_kangaroo_jump_amplitude", 1)
        self.cat.cat_kangaroo_jump_speed = getattr(self, "cat_kangaroo_jump_speed", 0.1)

        self.camera = Camera(WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)

    def load_bg(self, bg_img_num=1):
        path = f"images/world_{self.world_num}/world_{self.world_num}_{self.level_num}/bg_img/bg_{bg_img_num}.webp"

        if not os.path.exists(path):
            path = "images/world_1/world_1_1/bg_img/bg_1.webp"

        # ВАЖНО: используем convert() для фонов без прозрачности
        return pygame.image.load(file_path(path)).convert()

    def load_letter_bgs(self, world_num, level_num, folder_name="letter_bg"):
        folder = f"images/world_{world_num}/world_{world_num}_{level_num}/{folder_name}/"

        imgs = []

        if os.path.exists(folder):
            for name in sorted(os.listdir(folder)):
                if name.startswith("letter_bg") and name.endswith(".webp"):
                    path = os.path.join(folder, name)
                    img = pygame.image.load(file_path(path)).convert_alpha()
                    imgs.append(img)

        # если в мире нет своих фонов — берём из world_1_1
        if not imgs:
            fallback = "images/world_1/world_1_1/letter_bg/"
            if os.path.exists(fallback):
                for name in sorted(os.listdir(fallback)):
                    if name.startswith("letter_bg") and name.endswith(".webp"):
                        path = os.path.join(fallback, name)
                        img = pygame.image.load(file_path(path)).convert_alpha()
                        imgs.append(img)

        # ===== обработка фонов букв =====
        new_imgs = []
        bg_size = int(self.game.screen_height * 0.089)
        for img in imgs:
            # Используем быструю масштабируемость scale вместо smoothscale
            img = pygame.transform.scale(img, (bg_size, bg_size)).convert_alpha()
            img.set_alpha(220)
            new_imgs.append(img)

        imgs = new_imgs
        self.letter_bg_imgs = imgs
        return imgs

    def is_on_screen(self, obj_rect):
        """Проверяет, попадает ли объект в видимую область экрана."""
        screen_rect = pygame.Rect(
            self.camera.camera_x, 
            self.camera.camera_y, 
            self.screen_width, 
            self.screen_height
        )
        return screen_rect.colliderect(obj_rect)

    def update(self):
        if self.camera:
            self.camera.update(
                self.cat.cat_x if self.cat else 0, 
                self.cat.cat_y if self.cat else 0
            )

        if self.cat:
            self.cat.update(
                self.camera.camera_x,
                self.camera.camera_y,
                self.touch_down,
                self.touch_pos,
            )

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
        for event in events:
            if event.type == pygame.FINGERDOWN:
                self.touch_down = True
                self.touch_pos = (
                    event.x * self.game.base_width,
                    event.y * self.game.base_height,
                )

            elif event.type == pygame.FINGERUP:
                self.touch_down = False

            elif event.type == pygame.FINGERMOTION:
                self.touch_pos = (
                    event.x * self.game.base_width,
                    event.y * self.game.base_height,
                )

    def _get_cached_text(self, font, text, color):
        """Вспомогательный метод кэширования текста для предотвращения лагов."""
        key = (text, color)
        if key not in self._hud_cache:
            self._hud_cache[key] = font.render(text, True, color)
        return self._hud_cache[key]

    def draw_hud(self, screen):
        w = screen.get_width()
        h = screen.get_height()

        take_text = "Բռնիր "
        count_text = f" {max(0, self.need - self.score)} հատ"

        # Рендерим кэшированный текст
        take_surf = self._get_cached_text(self.game.font_hud, take_text, (0, 0, 0))
        count_surf = self._get_cached_text(self.game.font_hud, count_text, (0, 0, 0))

        # Позиции
        x = int(h * 0.022)
        y = int(h * 0.066)

        screen.blit(take_surf, (x, y))
        x += take_surf.get_width()

        if self.letter_bg_imgs and self.target:
            bg_img = self.letter_bg_imgs[0]
            bg_rect = bg_img.get_rect(topleft=(x, y - int(h * 0.01)))
            screen.blit(bg_img, bg_rect)

            # текст поверх фона
            color = getattr(self, "good_target_color", (0, 180, 0))
            target_surf = self._get_cached_text(self.game.font_good, self.target, color)
            target_rect = target_surf.get_rect(center=bg_rect.center)
            screen.blit(target_surf, target_rect)
            x += bg_rect.width
        elif self.target:
            target_surf = self._get_cached_text(self.game.font_good, self.target, (0, 220, 0))
            screen.blit(target_surf, (x, y - int(h * 0.005)))
            x += target_surf.get_width()

        screen.blit(count_surf, (x, y))

        # --- КЭШИРОВАННОЕ СЕРДЦЕ С ЖИЗНЯМИ ---
        if self.cached_heart_lives != self.lives:
            max_heart_size = int(h * 0.1)
            min_heart_size = int(h * 0.045)
            if self.lives > 0:
                heart_size = min_heart_size + (max_heart_size - min_heart_size) * (self.lives / LIVES_COUNT)
            else:
                heart_size = min_heart_size

            self.cached_heart_img = pygame.transform.scale(
                self.heart_base_img, (int(heart_size), int(heart_size))
            )
            self.cached_heart_lives = self.lives

        heart_size = self.cached_heart_img.get_width()
        heart_x = w - heart_size - int(h * 0.022)
        heart_y = int(h * 0.022)
        screen.blit(self.cached_heart_img, (heart_x, heart_y))

        # Число жизней
        lives_text = f"x {self.lives}"
        lives_surf = self._get_cached_text(self.game.font_hud, lives_text, (0, 0, 0))
        lives_x = heart_x + heart_size // 2 - lives_surf.get_width() // 2
        lives_y = heart_y + heart_size // 2 - lives_surf.get_height() // 2
        screen.blit(lives_surf, (lives_x, lives_y))

        # --- WORLD / LEVEL и счет ---
        header_text = f"Աշխարհ {self.world_num}, Փուլ- {self.level_num}   {self.score}/{self.need}"
        header_surf = self._get_cached_text(self.game.font_hud, header_text, (0, 0, 0))
        screen.blit(header_surf, (int(h * 0.022), int(h * 0.022)))

    def is_finished(self):
        return self.score >= self.need

    def next_world(self):
        next_level_num = self.level_num + 1
        next_world_num = self.world_num + 1

        target_key = (self.world_num, next_level_num)

        if target_key in LEVELS_MAP:
            mod_path, class_name = LEVELS_MAP[target_key]
            try:
                module = importlib.import_module(mod_path)
                WorldClass = getattr(module, class_name)
                save_progress(f"World_{self.world_num}_{next_level_num}")
                return WorldClass(self.game, lives=self.lives)
            except Exception as e:
                print(f"Ошибка загрузки уровня {target_key}: {e}")
                return None

        next_world_key = (next_world_num, 1)
        if next_world_key in LEVELS_MAP:
            mod_path, class_name = LEVELS_MAP[next_world_key]
            try:
                module = importlib.import_module(mod_path)
                first_world_class = getattr(module, class_name)

                if next_world_num - 1 < len(ARMENIAN_LETTERS):
                    target = ARMENIAN_LETTERS[next_world_num - 1]
                    target_lower = target.lower()
                    letters = [target, target, target_lower, target_lower]

                    def go_next_world():
                        save_progress(f"World_{next_world_num}_1")
                        return first_world_class(self.game, lives=self.lives)

                    return LettersScreen(
                        self.game, letters, next_world_num, go_next_world
                    )
            except Exception as e:
                print(f"Ошибка загрузки мира {next_world_num}: {e}")
                return None

        print("Игра полностью пройдена или уровень не найден!")
        return None
