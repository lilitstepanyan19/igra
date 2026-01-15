import pygame
import sys
import math
from base import WORLD_WIDTH, WORLD_HEIGHT

from worlds.world_1 import world_1_1

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60


CAT_SPEED = 0.3
MOUSE_SPEED = 0.02
LETTER_SPEED = 0.5
LETTER_MIN_SPEED = 0.5
LETTER_MAX_SPEED = 2.0

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.camera_x = 0
        self.camera_target_x = 0
        self.CAMERA_SPEED = 0.05   # 0.02 — очень плавно, 0.1 — быстрее


        pygame.display.set_caption("Cat Catch Letters 😺")
        self.clock = pygame.time.Clock()

        self.font_good = pygame.font.Font("fonts/GHEAGpalatBld.otf", 48)
        self.font_bad = pygame.font.Font("fonts/GHEAGpalatBld.otf", 36)
        self.font_hud = pygame.font.Font("fonts/GHEAGpalatBld.otf", 24)

        # --- load cat frames ---
        self.cat_right = self.load_cat("right")
        self.cat_left = self.load_cat("left")
        self.cat_frames = self.cat_right
        self.cat_index = 0

        self.cat_x, self.cat_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.CAT_BOUNDS = pygame.Rect(0, 100, WORLD_WIDTH, WORLD_HEIGHT - 150)

        # --- physics ---
        self.cat_vy = 0
        self.GRAVITY = 0.8
        self.JUMP_POWER = -14
        self.on_ground = False

        self.GROUND_Y = WORLD_HEIGHT - 120   # уровень земли (подбери под фон)
        
        # --- world system ---
        self.world = world_1_1.World_1_1(self)
        self.world.start()

    def load_cat(self, direction):
        frames = []
        for i in range(1, 9):
            img = pygame.image.load(f"images/cat_{i}_{direction}.png").convert_alpha()
            img = pygame.transform.scale(img, (120, 120))
            frames.append(img)
        return frames

    @property
    def cat_rect(self):
        return self.cat_frames[int(self.cat_index)].get_rect(
            center=(self.cat_x, self.cat_y)
        )

    def update_cat(self):
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
        self.cat_y += self.cat_vy
    
        if self.cat_y > self.GROUND_Y:
            self.cat_y = self.GROUND_Y
            self.cat_vy = 0
            self.on_ground = True
    
        # камера по X
        self.camera_target_x = self.cat_x - SCREEN_WIDTH // 2
        self.camera_target_x = max(0, min(self.camera_target_x, WORLD_WIDTH - SCREEN_WIDTH))
        self.camera_x += (self.camera_target_x - self.camera_x) * self.CAMERA_SPEED
    
        # mouse X только
        mx, _ = pygame.mouse.get_pos()
        mx_world = mx + self.camera_x
        dx = mx_world - self.cat_x
        if abs(dx) > 5:
            self.cat_x += dx * MOUSE_SPEED
            self.cat_frames = self.cat_right if dx > 0 else self.cat_left
            moved = True
    
        # границы X
        rect = self.cat_rect
        if rect.left < self.CAT_BOUNDS.left:
            self.cat_x += self.CAT_BOUNDS.left - rect.left
        if rect.right > self.CAT_BOUNDS.right:
            self.cat_x -= rect.right - self.CAT_BOUNDS.right
    
        # анимация
        if moved:
            self.cat_index += 0.15
            if self.cat_index >= len(self.cat_frames):
                self.cat_index = 0
        else:
            self.cat_index = 0

    def run(self):
        running = True
        while running:

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

            # --- обновления ---
            self.update_cat()
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

            # --- РИСОВАНИЕ ---
            self.screen.fill((255, 255, 255))                      # очищаем экран
            self.world.draw(self.screen)                            # фон + буквы
            self.world.draw_hud(self.screen)                        # HUD

            screen_x = self.cat_x - self.camera_x
            screen_y = self.cat_y
            self.screen.blit(self.cat_frames[int(self.cat_index)],
                             self.cat_frames[int(self.cat_index)].get_rect(center=(screen_x, screen_y)))
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
