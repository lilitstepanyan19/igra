# worlds/world_1/world_1_2.py
import pygame
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT
from letter import Letter, LETTER_SPEED  # импортируем класс Letter


class RainDrop:
    def __init__(self, x, y, speed, img):
        self.x = x
        self.y = y
        self.speed = speed
        self.img = img

    def update(self, world_width, world_height):
        self.y += self.speed
        self.x -= self.speed * 0.5  # наклон капли справа налево
        if self.y > world_height or self.x < -50:
            self.y = random.randint(-200, -50)
            self.x = random.randint(0, world_width)

    def draw(self, screen, camera_x):
        screen.blit(self.img, (self.x - camera_x, self.y))


class World_1_2(WorldBase):
    def start(self):
        super().start()  # ← создаёт self.cat и self.camera

        self.target = self.armenian_letters[self.world_num - 1]
        self.letter_count = 7
        self.need = 4
        self.score = 0

        # ===== ФОН =====
        bg_img = pygame.image.load(
            f"images/world_{self.world_num}/world_{self.world_num}_{self.level_num}/bg_img/bg_1.jpg"
        ).convert()
        scale = SCREEN_HEIGHT / bg_img.get_height()
        w = int(bg_img.get_width() * scale)
        h = SCREEN_HEIGHT
        self.bg = pygame.transform.smoothscale(bg_img, (w, h))
        self.bg_w = self.bg.get_width()

        self.letters = []
        self.load_letter_bgs(self.world_num, self.level_num)

        # ===== ДОЖДЬ =====
        drop_img = pygame.image.load(
            "images/world_1/world_1_2/rain/rain_1.png"
        ).convert_alpha()
        drop_img = pygame.transform.scale(drop_img, (12, 35))  # ширина/высота капли

        # задний слой
        self.rain_back = [
            RainDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(0, WORLD_HEIGHT),
                random.uniform(1, 2),
                drop_img,
            )
            for _ in range(1500)
        ]

        # передний слой
        self.rain_front = [
            RainDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(0, WORLD_HEIGHT),
                random.uniform(2, 4),
                drop_img,
            )
            for _ in range(500)
        ]

        # ===== ВРЕМЯ ДЛЯ ПОЯВЛЕНИЯ БУКВ =====
        self.start_time = pygame.time.get_ticks()
        self.spawn_delay_start = 2000  # 2 секунды перед первым появлением
        self.spawn_delay = 700  # пауза между появлениями
        self.last_spawn_time = self.start_time

    def spawn(self, count):
        target_count = sum(1 for l in self.letters if l.char == self.target)

        if target_count == 0:
            letter_bg = random.choice(self.letter_bg_imgs)
            x = random.randint(60, WORLD_WIDTH - 60)
            y = random.randint(140, WORLD_HEIGHT - 60)
            vx = random.choice([-1, 1]) * LETTER_SPEED
            vy = random.choice([-1, 1]) * LETTER_SPEED
            self.letters.append(Letter(self.target, x, y, vx, vy, letter_bg))

        while (
            sum(1 for l in self.letters if l.char == self.target) < 2
            and len(self.letters) < count
        ):
            char = (
                self.target
                if random.random() < 0.6
                else random.choice(self.armenian_letters)
            )
            letter_bg = random.choice(self.letter_bg_imgs)
            x = random.randint(60, WORLD_WIDTH - 60)
            y = random.randint(140, WORLD_HEIGHT - 60)
            vx = random.choice([-1, 1]) * LETTER_SPEED
            vy = random.choice([-1, 1]) * LETTER_SPEED
            self.letters.append(Letter(char, x, y, vx, vy, letter_bg))

    def update(self):
        super().update()

        # обновление дождя
        for drop in self.rain_back + self.rain_front:
            drop.update(WORLD_WIDTH, WORLD_HEIGHT)

        cat_rect = self.cat.cat_rect

        for letter in self.letters[:]:
            letter.update(WORLD_WIDTH, WORLD_HEIGHT)
            if letter.check_collision(cat_rect):
                if letter.char == self.target:
                    self.score += 1
                    self.letters.remove(letter)
                else:
                    now = pygame.time.get_ticks()
                    if now - self.last_hit_time > self.hit_cooldown:
                        self.lives -= 1
                        self.last_hit_time = now

        # появление букв
        now = pygame.time.get_ticks()
        if now - self.start_time < self.spawn_delay_start:
            return
        if now - self.last_spawn_time > self.spawn_delay:
            self.spawn(self.letter_count)
            self.last_spawn_time = now
        self.spawn(self.letter_count)

    def draw(self, screen):
        # фон
        for x in range(0, WORLD_WIDTH, self.bg_w):
            screen.blit(self.bg, (x - self.camera.camera_x, 0))

        # дождь сзади
        for drop in self.rain_back:
            drop.draw(screen, self.camera.camera_x)

        # буквы
        for letter in self.letters:
            letter.draw(
                screen,
                self.game.font_good,
                self.game.font_bad,
                self.camera.camera_x,
                self.target,
            )

        # дождь спереди
        for drop in self.rain_front:
            drop.draw(screen, self.camera.camera_x)
