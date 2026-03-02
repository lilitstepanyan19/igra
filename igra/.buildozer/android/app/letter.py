# letter.py
import pygame

LETTER_SPEED = 0.9
LETTER_MIN_SPEED = 0.5
LETTER_MAX_SPEED = 2.0

class Letter:

    def __init__(self, char, x, y, vx, vy, bg_img=None):
        self.char = char  # символ буквы
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.bg_img = bg_img

    def update(self, world_width, world_height):
        # движение буквы
        self.x += self.vx
        self.y += self.vy

        # отражение от стен
        if self.x < 30 or self.x > world_width - 30:
            self.vx *= -1
        if self.y < 120 or self.y > world_height - 30:
            self.vy *= -1

    def draw(self, screen, font_good, font_bad, camera_x, target):
        if self.bg_img:
            rect = self.bg_img.get_rect(center=(self.x - camera_x, self.y))
            screen.blit(self.bg_img, rect)

        # выбираем цвет: зелёный для цели, красный для остальных
        font = font_good if self.char == target else font_bad
        color = (0, 180, 0) if self.char == target else (180, 0, 0)
    
        # рендерим букву
        text_surf = font.render(self.char, True, color)
        text_rect = text_surf.get_rect(center=(self.x - camera_x, self.y))
        screen.blit(text_surf, text_rect)

    def check_collision(self, cat_rect):
        # прямоугольник буквы для столкновения
        temp_font = pygame.font.Font(None, 48)  # временный, просто для расчёта rect
        text_rect = temp_font.render(self.char, True, (0, 0, 0)).get_rect(
            center=(self.x, self.y)
        )
        return cat_rect.colliderect(text_rect)
