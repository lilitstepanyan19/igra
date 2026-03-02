import pygame
import sys
import importlib
import os
from base import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, ARMENIAN_LETTERS
from save import load_progress, save_progress, SAVE_FILE

from letters_screen import LettersScreen
from worlds.world_1_a.world_1_1 import World_1_1  # стартовый мир
# from worlds.world_6_k.world_6_3 import World_6_3

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Cat Catch Letters 😺")
        self.clock = pygame.time.Clock()

        self.font_good = pygame.font.Font("fonts/GHEAGpalatBld.otf", 48)
        self.font_bad = pygame.font.Font("fonts/GHEAGpalatBld.otf", 36)
        self.font_hud = pygame.font.Font("fonts/GHEAGpalatBld.otf", 24)

        self.font_big = pygame.font.Font('fonts/GHEAGpalatBld.otf', 150)
        self.font_big_handwriting = pygame.font.Font('fonts/Vrdznagir.otf', 150)
        self.font_small = pygame.font.Font('fonts/GHEAGpalatBld.otf', 30)

        #-- Sounds ---
        self.game_over_sound = pygame.mixer.Sound("sounds/game_over.wav")
        self.you_win_sound = pygame.mixer.Sound("sounds/game_over.wav")

        self.world = None

    def start_screen(self):
        """Экран с кнопками Продолжить / Новая игра"""
        running = True
        while running:
            self.screen.fill((200, 230, 255))  # светлый фон

            # --- Заголовок ---
            title = self.font_good.render("Cat Catch Letters 😺", True, (0, 0, 0))
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

            # --- Кнопки ---
            mouse_x, mouse_y = pygame.mouse.get_pos()
            buttons = []

            # Продолжить
            cont_text = "Շարունակել"
            cont_surf = self.font_hud.render(cont_text, True, (0, 0, 0))
            cont_rect = cont_surf.get_rect(center=(SCREEN_WIDTH // 2, 250))
            pygame.draw.rect(self.screen, (100, 255, 100), cont_rect.inflate(20, 20))
            self.screen.blit(cont_surf, cont_rect)
            buttons.append(("continue", cont_rect))

            # Новая игра
            new_text = "Նոր խաղ"
            new_surf = self.font_hud.render(new_text, True, (0, 0, 0))
            new_rect = new_surf.get_rect(center=(SCREEN_WIDTH // 2, 350))
            pygame.draw.rect(self.screen, (255, 100, 100), new_rect.inflate(20, 20))
            self.screen.blit(new_surf, new_rect)
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
                                    # функция для перехода в первый мир
                                def start_first_world():
                                    world = World_1_1(self)
                                    world.start()
                                    return world

                                first_letters = [ARMENIAN_LETTERS[0], 
                                                ARMENIAN_LETTERS[0],
                                                ARMENIAN_LETTERS[0].lower(), 
                                                ARMENIAN_LETTERS[0].lower()]  
                                self.world = LettersScreen(self, first_letters, 1, start_first_world)
                                self.world.start()
                                running = False

    def load_last_world(self):
        world_name = load_progress()  # например "World_1_2"

        if not world_name:
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
                win = self.font_good.render("YOU WIN 😺🎉", True, (255, 255, 255))
                self.screen.blit(
                    win,
                    (SCREEN_WIDTH // 2 - win.get_width() // 2, SCREEN_HEIGHT // 2)
                )
            
                pygame.display.flip()
                pygame.time.wait(4000)
                running = False
                continue

            if self.world.lives <= 0:
                self.game_over_sound.play()  # ← звук проигрыша
                self.screen.fill((0, 0, 0))
                lose = self.font_good.render("GAME OVER 😿", True, (255, 0, 0))
                self.screen.blit(lose, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
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
