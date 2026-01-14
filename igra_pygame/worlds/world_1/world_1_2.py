import pygame
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT
from main import SCREEN_HEIGHT, LETTER_SPEED


class World_1_2(WorldBase):

    def start(self):
        self.target = self.armenian_letters[self.world_num - 1]
        self.letter_count = 7

        self.need = 4
        self.score = 0

        bg_img = pygame.image.load("images/world_1/bg_2.jpg").convert()

        h = SCREEN_HEIGHT
        scale = h / bg_img.get_height()
        w = int(bg_img.get_width() * scale)

        self.bg = pygame.transform.smoothscale(bg_img, (w, h))
        self.bg_w = self.bg.get_width()

        self.letters = []
        self.spawn(7)

    def spawn(self, count):
        # Считаем, сколько правильных букв уже на экране
        target_count = sum(1 for l in self.letters if l[0] == self.target)

        # если нет ни одной правильной буквы, добавляем
        if target_count == 0:
            x = random.randint(60, WORLD_WIDTH - 60)
            y = random.randint(140, WORLD_HEIGHT - 60)
            vx = random.choice([-1, 1]) * LETTER_SPEED
            vy = random.choice([-1, 1]) * LETTER_SPEED
            self.letters.append([self.target, x, y, vx, vy])

        while len(self.letters) < count:
            l = (
                self.target
                if random.random() < 0.7
                else random.choice(self.armenian_letters)
            )
            x = random.randint(60, WORLD_WIDTH - 60)
            y = random.randint(140, WORLD_HEIGHT - 60)
            vx = random.choice([-1, 1])
            vy = random.choice([-1, 1])
            self.letters.append([l, x, y, vx, vy])

    def update(self):
        cat_rect = self.game.cat_rect

        for l in self.letters:
            l[1] += l[3]
            l[2] += l[4]
            if l[1] < 30 or l[1] > WORLD_WIDTH - 30:
                l[3] *= -1
            if l[2] < 120 or l[2] > WORLD_HEIGHT - 30:
                l[4] *= -1

        for l in self.letters[:]:
            text = self.game.font_good.render(l[0], True, (0, 180, 0))
            rect = text.get_rect(center=(l[1], l[2]))
            if cat_rect.colliderect(rect):
                if l[0] == self.target:
                    self.score += 1
                self.letters.remove(l)

        # --- добиваем буквы до нужного количества ---
        self.spawn(self.letter_count)

    def draw(self, screen):
        for x in range(0, WORLD_WIDTH, self.bg_w):
            screen.blit(self.bg, (x - self.game.camera_x, 0))

        for l in self.letters:
            if l[0] == self.target:
                text = self.game.font_good.render(l[0], True, (0, 180, 0))
            else:
                text = self.game.font_bad.render(l[0], True, (180, 0, 0))
            screen.blit(text, (l[1] - self.game.camera_x, l[2]))
