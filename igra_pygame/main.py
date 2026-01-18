import pygame
import sys
from base import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

from worlds.world_1 import world_1_1

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("Cat Catch Letters 😺")
        self.clock = pygame.time.Clock()

        self.font_good = pygame.font.Font("fonts/GHEAGpalatBld.otf", 48)
        self.font_bad = pygame.font.Font("fonts/GHEAGpalatBld.otf", 36)
        self.font_hud = pygame.font.Font("fonts/GHEAGpalatBld.otf", 24)


        # --- world system ---
        self.world = world_1_1.World_1_1(self)
        self.world.start()

    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

            # --- обновления ---
            self.world.update()

            # --- проверка завершения уровня ---
            if self.world.is_finished():
                nxt = self.world.next_world()
                if nxt:
                    self.world = nxt
                    self.world.start()
                else:
                    self.screen.fill((0, 0, 0))
                    win = self.font_good.render("YOU WIN 😺🎉", True, (255, 255, 255))
                    self.screen.blit(win, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
                    pygame.display.flip()
                    pygame.time.wait(4000)
                    running = False
                    continue  # пропускаем отрисовку остального кадра

            if self.world.lives <= 0:
                self.screen.fill((0, 0, 0))
                lose = self.font_bad.render("GAME OVER 😿", True, (255, 0, 0))
                self.screen.blit(lose, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                running = False
                continue

            # --- ОЧИСТКА ЭКРАНА ---
            self.screen.fill((255, 255, 255))  # или можно чёрный фон

            # --- РИСУЕМ МИР ---
            self.world.draw(self.screen)        # фон + буквы
            self.world.draw_hud(self.screen)    # HUD

            # --- РИСУЕМ КОТА ЧЕРЕЗ КАМЕРУ ---
            cat = self.world.cat
            cam = self.world.camera

            screen_x = cat.cat_x - cam.camera_x
            screen_y = cat.cat_y

            img = cat.cat_frames[int(cat.cat_index)]
            self.screen.blit(img, img.get_rect(center=(screen_x, screen_y)))
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
