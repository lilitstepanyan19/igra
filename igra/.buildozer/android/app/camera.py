import pygame


class Camera:
    def __init__(self, screen_width, world_width):
        self.screen_width = screen_width
        self.world_width = world_width

        self.camera_x = 0
        self.CAMERA_SPEED = 0.05   # 0.02 — очень плавно, 0.1 — быстрее

    def update(self, cat_x):
        target = cat_x - self.screen_width // 2
        target = max(0, min(target, self.world_width - self.screen_width))
        self.camera_x += (target - self.camera_x) * self.CAMERA_SPEED
