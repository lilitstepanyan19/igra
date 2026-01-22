# worlds/world_1/world_1_2.py
import pygame
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT
from letter import Letter, LETTER_SPEED
import letter  # импортируем класс Letter


class RainDrop:
    def __init__(self, x, y, speed, img):
        self.x = x
        self.y = y
        self.speed = speed
        self.img = img

    def update(self, world_width, world_height):
        self.y += self.speed
        self.x -= self.speed * 0.4  # наклон капли справа налево

        # нижняя граница немного выше пола (например, 50 пикселей выше)
        max_y = world_height - 50
        if self.y > max_y or self.x < -50:
            self.y = random.randint(-200, -50)
            self.x = random.randint(0, world_width)

    def draw(self, screen, camera_x):
        screen.blit(self.img, (self.x - camera_x, self.y))


class World_1_2(WorldBase):
    def start(self):
        super().start()  # ← создаёт self.cat и self.camera

        self.target = self.armenian_letters[self.world_num - 1].lower()
        self.hud_target_color = (20, 60, 222)  # синий цвет для цели
        self.letter_count = 20
        self.need = 4
        self.score = 0

        # ===== ФОН =====
        bg_img = self.load_bg()

        scale = SCREEN_HEIGHT / bg_img.get_height()
        w = int(bg_img.get_width() * scale)
        h = SCREEN_HEIGHT
        self.bg = pygame.transform.smoothscale(bg_img, (w, h))
        self.bg_w = self.bg.get_width()

        self.letters = []
        self.load_letter_bgs(self.world_num, self.level_num)

        # ===== ДОЖДЬ =====
        drop_img = pygame.image.load("images/world_1/world_1_2/rain/rain_1.png").convert_alpha()
        drop_img = pygame.transform.scale(drop_img, (4, 60))  # ширина/высота капли

        # задний слой
        self.rain_back = [
            RainDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(0, WORLD_HEIGHT),
                random.uniform(2, 3),
                drop_img,
            )
            for _ in range(1500)
        ]

        # передний слой
        self.rain_front = [
            RainDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(0, WORLD_HEIGHT),
                random.uniform(4, 5),
                drop_img,
            )
            for _ in range(1000)
        ]

        # ===== ВРЕМЯ ДЛЯ ПОЯВЛЕНИЯ БУКВ =====
        self.start_time = pygame.time.get_ticks()
        self.spawn_delay_start = 20  # 2 секунды перед первым появлением
        self.spawn_delay = 20  # пауза между появлениями
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

        while target_count < 2 and len(self.letters) < count:
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
            self.letters.append(Letter(char.lower(), x, y, vx, vy, letter_bg))

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
            x = letter.x - self.camera.camera_x
            y = letter.y

            # фон под буквой
            if letter.bg_img:
                rect = letter.bg_img.get_rect(center=(x, y))
                screen.blit(letter.bg_img, rect)

            # другие цвета ТОЛЬКО для этого мира
            if letter.char == self.target:
                color = self.hud_target_color 
                font = self.game.font_good
            else:
                color = (41, 42, 74)  # тёмно-синий
                font = self.game.font_bad

            text = font.render(letter.char, True, color)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

        # дождь спереди
        for drop in self.rain_front:
            drop.draw(screen, self.camera.camera_x)
