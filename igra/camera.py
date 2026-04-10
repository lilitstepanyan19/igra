import pygame

class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.world_width = world_width
        self.world_height = world_height

        self.camera_x = 0
        self.camera_y = 0
        self.CAMERA_SPEED = 0.05  # 0.02 — очень плавно, 0.1 — быстрее

    def update(self, cat_x, cat_y):
    
        target_x = cat_x - self.screen_width // 2
        self.camera_x += (
            max(0, min(target_x, self.world_width - self.screen_width)) - self.camera_x
        ) * self.CAMERA_SPEED

 
        target_y = cat_y - self.screen_height // 2
        self.camera_y += (
            max(0, min(target_y, self.world_height - self.screen_height))
            - self.camera_y
        ) * self.CAMERA_SPEED
