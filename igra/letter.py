import pygame

LETTER_SPEED = 0.9
LETTER_MIN_SPEED = 0.5
LETTER_MAX_SPEED = 2.0


class Letter:

    def __init__(
        self,
        char,
        x,
        y,
        vx,
        vy,
        bg_img=None,
        font_good=None,
        font_bad=None,
        target=None,
    ):
        self.char = char
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.bg_img = bg_img

        # Выбираем шрифт и цвет с защитой от None
        font = font_good if self.char == target else font_bad
        if font is None:
            font = pygame.font.SysFont("arial", 32)

        color = (0, 180, 0) if self.char == target else (180, 0, 0)

        # Рендерим текст
        try:
            text_surf = font.render(self.char, True, color).convert_alpha()
        except Exception:
            text_surf = font.render(self.char, True, color)

        # Объединяем текст и фон
        if bg_img:
            self.image = bg_img.copy()
            t_rect = text_surf.get_rect(
                center=(self.image.get_width() // 2, self.image.get_height() // 2)
            )
            self.image.blit(text_surf, t_rect)
        else:
            self.image = text_surf

        # Кэшируем параметры
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        # Создаем Rect строго по центру координат
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self, world_width, world_height):
        # Движение
        self.x += self.vx
        self.y += self.vy

        # Отражение от границ
        if self.x < 30 or self.x > world_width - 30:
            self.vx *= -1
        if self.y < 120 or self.y > world_height - 30:
            self.vy *= -1

        # Точно обновляем координаты прямоугольника для коллизий
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def draw(self, screen, font_good=None, font_bad=None, camera_x=0, target=None):
        """
        Возвращены все необязательные параметры (font_good, font_bad, target),
        так как их передает код уровня при вызове draw!
        """
        # Если camera_x не передана или передана как позиционный аргумент
        if isinstance(font_good, (int, float)) and camera_x == 0:
            camera_x = font_good

        screen_x = self.rect.x - int(camera_x)

        # Отрисовка на экране
        if -self.width <= screen_x <= screen.get_width():
            screen.blit(self.image, (screen_x, self.rect.y))

    def check_collision(self, cat_rect):
        # Точная проверка столкновения с котом
        return cat_rect.colliderect(self.rect)
