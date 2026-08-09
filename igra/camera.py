import pygame


class Camera:

    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        self.camera_x = 0
        self.camera_y = 0
        self._raw_x = 0.0  # Дробный накопитель для плавности
        self.CAMERA_SPEED = 0.08  # Подправленная скорость для стабильного кадра

    def update(self, cat_x, cat_y):
        # Зона, в которой камера НЕ двигается
        left_margin = self.screen_width * 0.3
        right_margin = (
            self.screen_width * 0.5
            if self.screen_width < 1000
            else self.screen_width * 0.7
        )

        screen_cat_x = cat_x - self._raw_x

        # Если кот ушел влево
        if screen_cat_x < left_margin:
            target_x = cat_x - left_margin
        # Если кот ушел вправо
        elif screen_cat_x > right_margin:
            target_x = cat_x - right_margin
        else:
            target_x = self._raw_x

        # Ограничение по границам мира
        max_x = self.world_width - self.screen_width
        if target_x < 0:
            target_x = 0
        elif target_x > max_x:
            target_x = max_x

        # Плавное приближение (плавающая точка)
        self._raw_x += (target_x - self._raw_x) * self.CAMERA_SPEED

        # ВАЖНО: Приводим координаты строго к целым числам пикселей для отрисовки!
        self.camera_x = int(self._raw_x)
        self.camera_y = 0  # Уровень фиксирован по высоте
