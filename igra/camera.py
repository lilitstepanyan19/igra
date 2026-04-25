import pygame

class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        self.camera_x = 0
        self.camera_y = 0
        self.CAMERA_SPEED = 0.07  # 0.02 — очень плавно, 0.1 — быстрее

    def update(self, cat_x, cat_y):
        # зона, в которой камера НЕ двигается
        left_margin = self.screen_width * 0.3
        right_margin = self.screen_width * 0.7
        
        if self.screen_width < 1000:
            left_margin = self.screen_width * 0.3
            right_margin = self.screen_width * 0.5

        screen_cat_x = cat_x - self.camera_x

        # если кот ушёл влево
        if screen_cat_x < left_margin:
            target_x = cat_x - left_margin

        # если кот ушёл вправо
        elif screen_cat_x > right_margin:
            target_x = cat_x - right_margin

        else:
            target_x = self.camera_x  # камера не двигается

        # ограничение по миру
        target_x = max(0, min(target_x, self.world_width - self.screen_width))

        # плавность
        self.camera_x += (target_x - self.camera_x) * self.CAMERA_SPEED


        # Y можно оставить как есть
        target_y = cat_y - self.screen_height // 2
        target_y = max(0, min(target_y, self.world_height - self.screen_height))
        self.camera_y += (target_y - self.camera_y) * self.CAMERA_SPEED
