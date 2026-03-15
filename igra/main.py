import pygame
import sys
import importlib
import os
from base import FPS, ARMENIAN_LETTERS
from save import load_progress, save_progress, SAVE_FILE

from paths import file_path

from letters_screen import LettersScreen
from worlds.world_1_a.world_1_1 import World_1_1  # стартовый мир
# from worlds.world_6_k.world_6_3 import World_6_3


class Game:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except:
            print("Mixer not available")

        self.is_android = 'ANDROID_ARGUMENT' in os.environ or 'P4A_BOOTSTRAP' in os.environ

        if self.is_android:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((900, 600), pygame.RESIZABLE)

        # Реальный размер экрана
        self.screen_width, self.screen_height = self.screen.get_size()

        # Базовый размер (как будто игра на 900×600)
        self.base_width = 900
        self.base_height = 600

        # Масштаб (берём минимальный, чтобы не растягивать)
        self.scale = min(
            self.screen_width / self.base_width, self.screen_height / self.base_height
        )
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2

        pygame.display.set_caption("Cat Catch Letters 😺")
        self.clock = pygame.time.Clock()

        font_scale = self.scale * (1.3 if self.is_android else 1.0)
        self.font_good = pygame.font.Font(file_path("fonts/GHEAGpalatBld.otf"), int(48 * font_scale))
        self.font_bad = pygame.font.Font(file_path("fonts/GHEAGpalatBld.otf"), int(36 * font_scale))
        self.font_hud = pygame.font.Font(file_path("fonts/GHEAGpalatBld.otf"), int(24 * font_scale))

        self.font_big = pygame.font.Font(file_path('fonts/GHEAGpalatBld.otf'), int(150 * font_scale))
        self.font_big_handwriting = pygame.font.Font(file_path('fonts/Vrdznagir.otf'), int(150 * font_scale))
        self.font_small = pygame.font.Font(file_path('fonts/GHEAGpalatBld.otf'), int(30 * font_scale))

        # -- Sounds ---
        self.game_over_sound = pygame.mixer.Sound(file_path("sounds/game_over.wav"))
        self.you_win_sound = pygame.mixer.Sound(file_path("sounds/you_win.wav"))

        self.world = None

    def start_screen(self):
        """Экран с кнопками Продолжить / Новая игра"""
        running = True
        while running:
            self.screen.fill((200, 230, 255))  # светлый фон

            # --- Заголовок ---
            title = self.font_good.render("Տառերն ու կենդանիները", True, (0, 0, 0))
            title_x = self.center_x - title.get_width() // 2
            title_y = int(80 * self.scale)
            self.screen.blit(title, (title_x, title_y))

            # --- Кнопки ---
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Кнопки — крупные, с отступом
            btn_width = int(400 * self.scale)
            btn_height = int(100 * self.scale)
            btn_spacing = int(180 * self.scale)
            btn_start_y = int(280 * self.scale)

            buttons = []

            # Продолжить
            cont_text = "Շարունակել"
            cont_surf = self.font_hud.render(cont_text, True, (0, 0, 0))
            cont_rect = pygame.Rect(
                self.center_x - btn_width // 2,
                btn_start_y,
                btn_width,
                btn_height
            )
            pygame.draw.rect(self.screen, (100, 255, 100), cont_rect, border_radius=int(30 * self.scale))
            pygame.draw.rect(self.screen, (0, 120, 0), cont_rect, int(6 * self.scale), border_radius=int(30 * self.scale))
            cont_text_rect = cont_surf.get_rect(center=cont_rect.center)
            self.screen.blit(cont_surf, cont_text_rect)
            buttons.append(("continue", cont_rect))

            # Новая игра
            new_text = "Նոր խաղ"
            new_surf = self.font_hud.render(new_text, True, (0, 0, 0))
            new_rect = pygame.Rect(
                self.center_x - btn_width // 2,
                btn_start_y + btn_spacing,
                btn_width,
                btn_height
            )
            pygame.draw.rect(self.screen, (255, 100, 100), new_rect, border_radius=int(30 * self.scale))
            pygame.draw.rect(self.screen, (180, 0, 0), new_rect, int(6 * self.scale), border_radius=int(30 * self.scale))
            new_text_rect = new_surf.get_rect(center=new_rect.center)
            self.screen.blit(new_surf, new_text_rect)
            buttons.append(("new", new_rect))

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for action, rect in buttons:
                        if rect.collidepoint(event.pos):
                            if action == "continue":
                                self.load_last_world()
                                running = False
                            elif action == "new":
                                if os.path.exists(SAVE_FILE):
                                    os.remove(SAVE_FILE)
                                first_letters = [ARMENIAN_LETTERS[0], ARMENIAN_LETTERS[0],
                                                 ARMENIAN_LETTERS[0].lower(), ARMENIAN_LETTERS[0].lower()]
                                self.world = LettersScreen(self, first_letters, 1, lambda: World_1_1(self))
                                self.world.start()
                                running = False

    def load_last_world(self):
        world_name = load_progress()  # например "World_1_2"

        if not world_name:
            world_num = 1
            def start_first_world():
                world = World_1_1(self)
                world.start()
                return world
            first_letters = [
                ARMENIAN_LETTERS[0],
                ARMENIAN_LETTERS[0],
                ARMENIAN_LETTERS[0].lower(),
                ARMENIAN_LETTERS[0].lower(),
            ]
            self.world = LettersScreen(self, first_letters, world_num, start_first_world)
            self.world.start()
            return

        try:
            _, w, l = world_name.split("_")
            world_num = int(w)
            level_num = int(l)

            worlds_root = "worlds"

            # --- ищем папку мира: world_1_a, world_2_s и т.д. ---
            world_folder = None
            for d in os.listdir(worlds_root):
                if d.startswith(f"world_{world_num}_"):
                    world_folder = d
                    break

            if not world_folder:
                raise Exception("world folder not found")

            # --- ищем файл уровня ---
            level_file = None
            for f in os.listdir(os.path.join(worlds_root, world_folder)):
                if f.startswith(f"world_{world_num}_{level_num}") and f.endswith(".py"):
                    level_file = f
                    break

            if not level_file:
                raise Exception("level file not found")

            module_name = f"worlds.{world_folder}.{level_file[:-3]}"
            module = importlib.import_module(module_name)

            WorldClass = getattr(module, world_name)

            self.world = WorldClass(self)
            self.world.start()

        except Exception as e:
            self.world = LettersScreen(self, "ABC", None)
            self.world.start()

    def run(self):
        self.start_screen()  # сначала экран выбора

        running = True
        while running:
            # Пересчитываем размер и масштаб каждый кадр (важно для RESIZABLE на ПК)
            self.screen_width, self.screen_height = self.screen.get_size()
            self.scale = min(self.screen_width / self.base_width, self.screen_height / self.base_height)
            self.center_x = self.screen_width // 2
            self.center_y = self.screen_height // 2

            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    running = False

            # --- обновления ---
            self.world.update()

            # --- проверка завершения уровня ---
            if hasattr(self.world, "game_completed") and self.world.game_completed:
                self.you_win_sound.play()

                self.screen.fill((0, 0, 0))
                win = self.font_good.render("Դու արդեն գիտես բոլոր տառեըը", True, (255, 255, 255))
                self.screen.blit(
                    win,
                    (self.screen_width // 2 - win.get_width() // 2, self.screen_height // 2)
                )

                pygame.display.flip()
                pygame.time.wait(4000)
                running = False
                continue

            if self.world.lives <= 0:
                self.game_over_sound.play()  # ← звук проигрыша
                self.screen.fill((0, 0, 0))
                lose = self.font_good.render("GAME OVER 😿", True, (255, 0, 0))
                self.screen.blit(lose, (self.screen_width // 2 - 120, self.screen_height // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False
                continue

            # --- ОЧИСТКА ЭКРАНА ---
            self.screen.fill((255, 255, 255))

            # --- РИСУЕМ МИР ---
            self.world.draw(self.screen)
            self.world.draw_hud(self.screen)

            # --- РИСУЕМ КОТА ЧЕРЕЗ КАМЕРУ ---
            if self.world.cat and self.world.camera:
                cat = self.world.cat
                cam = self.world.camera
                screen_x = cat.cat_x - cam.camera_x
                screen_y = cat.cat_y
                img = cat.cat_frames[int(cat.cat_index)]
                self.screen.blit(img, img.get_rect(center=(screen_x, screen_y)))

                # --- обработка событий ---
            self.world.handle_events(events)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
