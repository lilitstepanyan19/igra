import pygame
import random
from base import WorldBase

WIDTH, HEIGHT = 900, 600


class World_2_1(WorldBase):

    def start(self):
        name = self.__class__.__name__  # World_1_1
        _, world_num, level_num = name.split("_")

        self.target = self.armenian_letters[int(world_num) - 1]

        self.need = 4
        self.score = 0

        self.bg = pygame.image.load("images/world_2/bg_1.jpg").convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))

        self.letters = []
        self.spawn(7)

    def spawn(self, count):
        self.letters.clear()

        for _ in range(count):
            l = (
                self.target
                if random.random() < 0.7
                else random.choice(self.armenian_letters)
            )
            x = random.randint(60, WIDTH - 60)
            y = random.randint(140, HEIGHT - 60)
            vx = random.choice([-1, 1])
            vy = random.choice([-1, 1])
            self.letters.append([l, x, y, vx, vy])

    def update(self):
        cat_rect = self.game.cat_rect

        for l in self.letters:
            l[1] += l[3]
            l[2] += l[4]
            if l[1] < 30 or l[1] > WIDTH - 30:
                l[3] *= -1
            if l[2] < 120 or l[2] > HEIGHT - 30:
                l[4] *= -1

        for l in self.letters[:]:
            text = self.game.font_good.render(l[0], True, (0, 180, 0))
            rect = text.get_rect(center=(l[1], l[2]))

            if cat_rect.colliderect(rect):
                if l[0] == self.target:
                    self.score += 1
                    self.letters.remove(l)

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        for l in self.letters:
            if l[0] == self.target:
                text = self.game.font_good.render(l[0], True, (0, 180, 0))
            else:
                text = self.game.font_bad.render(l[0], True, (180, 0, 0))
            screen.blit(text, (l[1], l[2]))
