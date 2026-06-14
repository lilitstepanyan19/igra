# letter.py
import pygame

LETTER_SPEED = 0.9
LETTER_MIN_SPEED = 0.5
LETTER_MAX_SPEED = 2.0

class Letter:

    def __init__(self, char, x, y, vx, vy, bg_img=None, font_good=None, font_bad=None, target=None ):
        self.char = char  # символ буквы
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.bg_img = bg_img

        # выбираем цвет: зелёный для цели, красный для остальных
        self.font = font_good if self.char == target else font_bad
        self.color = (0, 180, 0) if self.char == target else (180, 0, 0)

        self.text_surf = self.font.render(self.char, True, self.color)
        self.draw_rect = self.text_surf.get_rect()

        self.collision_rect = self.text_surf.get_rect(center=(x, y))

    def update(self, world_width, world_height):
        # движение буквы
        self.x += self.vx
        self.y += self.vy

        # отражение от стен
        if self.x < 30 or self.x > world_width - 30:
            self.vx *= -1
        if self.y < 120 or self.y > world_height - 30:
            self.vy *= -1
        # обновляем прямоугольник для столкновения
        self.collision_rect.center = (self.x, self.y)   

    def draw(self, screen, camera_x):
        if self.bg_img:
            rect = self.bg_img.get_rect(center=(self.x - camera_x, self.y))
            screen.blit(self.bg_img, rect)

        # рендерим букву
        self.draw_rect.center = (self.x - camera_x, self.y)
        screen.blit(self.text_surf, self.draw_rect)

        # --- рамка вокруг буквы ---
        # pygame.draw.rect(screen, (0, 255, 0), text_rect, 2)  # зелёная рамка

    def check_collision(self, cat_rect):
        # прямоугольник буквы для столкновения
        return cat_rect.colliderect(self.collision_rect)
