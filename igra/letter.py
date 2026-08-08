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

        # Выбираем шрифт и цвет
        font = font_good if self.char == target else font_bad
        color = (0, 180, 0) if self.char == target else (180, 0, 0)

        # Рендерим текст с ускоренным форматом пикселей
        text_surf = font.render(self.char, True, color).convert_alpha()

        # Если есть фон — объединяем фон и текст в ОДНУ поверхность (один surface)
        if bg_img:
            # Клонируем фоновую картинку
            self.image = bg_img.copy()
            # Накладываем текст строго по центру фоновой картинки
            t_rect = text_surf.get_rect(
                center=(self.image.get_width() // 2, self.image.get_height() // 2)
            )
            self.image.blit(text_surf, t_rect)
        else:
            self.image = text_surf

        # Кэшируем Rect (создаём прямоугольник один раз при инициализации)
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

        # Обновляем координаты центра сгенерированного прямоугольника
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

    def draw(self, screen, camera_x):
        # Делаем ВСЕГО один blit вместо двух
        # Быстро вычисляем положение на экране без создания новых Rect
        screen.blit(self.image, (self.rect.x - int(camera_x), self.rect.y))

    def check_collision(self, cat_rect):
        # Используем уже готовый self.rect
        return cat_rect.colliderect(self.rect)
