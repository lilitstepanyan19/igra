# rain.py
import random
import pygame


class Splash:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = random.randint(8, 14)

        self.particles = []
        for _ in range(8):
            vx = random.uniform(-5.5, -2.5)
            vy = random.uniform(-3.5, -1.5)
            self.particles.append([0, 0, vx, vy])

    def update(self):
        self.life -= 1
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.3  # gravity

    def draw(self, screen, camera_x):
        for p in self.particles:
            pygame.draw.circle(
                screen,
                (200, 200, 255),
                (int(self.x + p[0] - camera_x), int(self.y + p[1])),
                1,
            )


class RainDrop:
    def __init__(self, x, y, speed, length, width):
        self.x = x
        self.y = y
        self.speed = speed
        self.length = length
        self.width = width

    def update(self, world_width, world_height, splashes):
        self.y += self.speed
        self.x -= self.speed * 0.3

        if self.y > world_height - 18:
            splashes.append(Splash(self.x, world_height - 18))
            self.y = random.randint(-100, -10)
            self.x = random.randint(0, world_width)

    def draw(self, screen, camera_x, color):
        rect = pygame.Rect(
        int(self.x - camera_x), int(self.y), self.width, self.length
    )
        pygame.draw.ellipse(screen, color, rect)
