import pygame
import random
from base import WorldBase

WIDTH, HEIGHT = 900, 600


class World_2_2(WorldBase):

    def start(self):
        self.sub = int(self.__class__.__name__.split("_")[-1]) - 1
        self.levels = [
            {"target": "B", "need": 6, "count": 9, "bg": "images/world_2/bg_2.jpg"},
        ]
        self.load_sublevel()

    def load_sublevel(self):
        lvl = self.levels[0]
        self.target = lvl["target"]
        self.need = lvl["need"]
        self.score = 0

        self.bg = pygame.image.load(lvl["bg"]).convert()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))

        self.speed = 1.5 + self.sub
        self.letters = []
        self.spawn(lvl["count"])

    def spawn(self, count):
        self.letters.clear()
        for _ in range(count):
            l = self.target if random.random() < 0.7 else random.choice("ADEFGHIJK")
            x = random.randint(60, WIDTH - 60)
            y = random.randint(140, HEIGHT - 60)
            vx = random.choice([-1, 1]) * self.speed
            vy = random.choice([-1, 1]) * self.speed
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
            if l[0] == self.target:
                text = self.game.font_good.render(l[0], True, (0, 200, 0))
            else:
                text = self.game.font_bad.render(l[0], True, (200, 0, 0))

            rect = text.get_rect(center=(l[1], l[2]))

            if cat_rect.colliderect(rect):
                if l[0] == self.target:
                    self.score += 1
                    self.letters.remove(l)

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        for l in self.letters:
            if l[0] == self.target:
                text = self.game.font_good.render(l[0], True, (0, 200, 0))
            else:
                text = self.game.font_bad.render(l[0], True, (200, 0, 0))
            screen.blit(text, (l[1], l[2]))

        hud = self.game.font_bad.render(
            f"WORLD 2  Level {self.sub +1}  {self.score}/{self.need}", True, (0, 0, 0)
        )
        screen.blit(hud, (20, 20))

    def is_finished(self):
        if self.score >= self.need:
            self.sub += 1
            if self.sub < len(self.levels):
                self.load_sublevel()
                return False
            return True
        return False

    def next_world(self):
        return None
