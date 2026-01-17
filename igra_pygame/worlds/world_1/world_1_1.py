# worlds/world_1/world_1_1.py
import pygame
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT
from letter import Letter, LETTER_SPEED  # импортируем новый класс


class World_1_1(WorldBase):

    def start(self):
        super().start()  # ← создаёт self.cat и self.camera
        self.target = self.armenian_letters[self.world_num - 1]
        self.letter_count = 7

        self.need = 4
        self.score = 0

        bg_img = pygame.image.load("images/world_1/bg_1.jpg").convert()
        h = SCREEN_HEIGHT
        scale = h / bg_img.get_height()
        w = int(bg_img.get_width() * scale)
        self.bg = pygame.transform.smoothscale(bg_img, (w, h))
        self.bg_w = self.bg.get_width()

        self.letters = []
        self.start_time = pygame.time.get_ticks()
        self.spawn_delay_start = 2000  # 2 секунды перед первым появлением
        self.spawn_delay = 700  # пауза между появлениями
        self.last_spawn_time = self.start_time

    def spawn(self, count):
        target_count = sum(1 for l in self.letters if l.char == self.target)

        if target_count == 0:
            x = random.randint(60, WORLD_WIDTH - 60)
            y = random.randint(140, WORLD_HEIGHT - 60)
            vx = random.choice([-1, 1]) * LETTER_SPEED
            vy = random.choice([-1, 1]) * LETTER_SPEED
            self.letters.append(Letter(self.target, x, y, vx, vy))

        while target_count < 2 and len(self.letters) < count:
            char = (
                self.target
                if random.random() < 0.6
                else random.choice(self.armenian_letters)
            )
            x = random.randint(60, WORLD_WIDTH - 60)
            y = random.randint(140, WORLD_HEIGHT - 60)
            vx = random.choice([-1, 1])
            vy = random.choice([-1, 1])
            self.letters.append(Letter(char, x, y, vx, vy))

    def update(self):
        super().update()
        cat_rect = self.cat.cat_rect

        for letter in self.letters[:]:
            letter.update(WORLD_WIDTH, WORLD_HEIGHT)
            if letter.check_collision(cat_rect):
                if letter.char == self.target:
                    self.score += 1
                    self.letters.remove(letter)
                else:
                    self.score -= 1
                    if self.score < 0:
                        self.score = 0

        now = pygame.time.get_ticks()

        # ждём перед первым появлением
        if now - self.start_time < self.spawn_delay_start:
            return

        # постепенное появление букв
        if now - self.last_spawn_time > self.spawn_delay:
            self.spawn(self.letter_count)
            self.last_spawn_time = now

        # добиваем буквы до нужного количества
        self.spawn(self.letter_count)

    def draw(self, screen):
        # фон
        for x in range(0, WORLD_WIDTH, self.bg_w):
            screen.blit(self.bg, (x - self.camera.camera_x, 0))

        # буквы
        for letter in self.letters:
            letter.draw(
                screen,
                self.game.font_good,
                self.game.font_bad,
                self.camera.camera_x,
                self.target,
            )
