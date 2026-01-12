import pygame
import sys
import math

from worlds.world_1 import world_1_1

WIDTH, HEIGHT = 900, 600
FPS = 60

CAT_SPEED = 1.2
MOUSE_SPEED = 0.08


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cat Catch Letters 😺")
        self.clock = pygame.time.Clock()

        self.font_good = pygame.font.SysFont(None, 48, bold=True)
        self.font_bad = pygame.font.SysFont(None, 36)

        # --- load cat frames ---
        self.cat_right = self.load_cat("right")
        self.cat_left = self.load_cat("left")
        self.cat_frames = self.cat_right
        self.cat_index = 0

        self.cat_x, self.cat_y = WIDTH // 2, HEIGHT // 2
        self.CAT_BOUNDS = pygame.Rect(0, 100, WIDTH, HEIGHT - 100)

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

        if keys[pygame.K_LEFT]:
            self.cat_x -= CAT_SPEED
            self.cat_frames = self.cat_left
            moved = True
        if keys[pygame.K_RIGHT]:
            self.cat_x += CAT_SPEED
            self.cat_frames = self.cat_right
            moved = True
        if keys[pygame.K_UP]:
            self.cat_y -= CAT_SPEED
        if keys[pygame.K_DOWN]:
            self.cat_y += CAT_SPEED

        # mouse follow
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.cat_x
        dy = my - self.cat_y
        dist = math.hypot(dx, dy)
        if dist > 5:
            self.cat_x += dx * MOUSE_SPEED
            self.cat_y += dy * MOUSE_SPEED
            self.cat_frames = self.cat_right if dx > 0 else self.cat_left
            moved = True

        # bounds
        rect = self.cat_rect
        if rect.left < self.CAT_BOUNDS.left:
            self.cat_x += self.CAT_BOUNDS.left - rect.left
        if rect.right > self.CAT_BOUNDS.right:
            self.cat_x -= rect.right - self.CAT_BOUNDS.right
        if rect.top < self.CAT_BOUNDS.top:
            self.cat_y += self.CAT_BOUNDS.top - rect.top
        if rect.bottom > self.CAT_BOUNDS.bottom:
            self.cat_y -= rect.bottom - self.CAT_BOUNDS.bottom

        # animation
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

            self.update_cat()
            self.world.update()

            if self.world.is_finished():
                nxt = self.world.next_world()
                if nxt:
                    self.world = nxt
                    self.world.start()
                else:
                    self.screen.fill((0, 0, 0))
                    win = self.font_good.render("YOU WIN 😺🎉", True, (255, 255, 255))
                    self.screen.blit(win, (WIDTH // 2 - 120, HEIGHT // 2))
                    pygame.display.flip()
                    pygame.time.wait(4000)
                    running = False

            self.world.draw(self.screen)
            self.screen.blit(self.cat_frames[int(self.cat_index)], self.cat_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    Game().run()
