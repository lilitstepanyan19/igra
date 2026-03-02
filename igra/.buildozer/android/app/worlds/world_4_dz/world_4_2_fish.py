import pygame
import math
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT, NEED, SCORE, LETTER_COUNT, ARMENIAN_LETTERS
from letter import Letter, LETTER_SPEED


class FishDrop:
    def __init__(self, x, y, speed, img, water_level):
        self.x = x
        self.base_y = y
        self.y = y
        self.speed = speed
        self.img = img
        self.water_level = water_level

        self.dir = random.choice([-1, 1])  # -1 ← , 1 →
        self.wave_offset = random.uniform(0, 6.28)
        self.wave_speed = random.uniform(0.02, 0.05)
        self.wave_amplitude = random.randint(25, 35)

        # разворот картинки
        if self.dir == -1:
            self.img = pygame.transform.flip(self.img, True, False)

    def update(self, world_width, world_height):
        # движение влево / вправо
        self.x += self.speed * self.dir

        # волнообразное плавание
        self.wave_offset += self.wave_speed
        self.y = self.base_y + math.sin(self.wave_offset) * self.wave_amplitude
        self.y = max(self.water_level, self.y)
        self.y = min(self.y, world_height - 100)

        # если уплыла за экран — появиться с другой стороны
        if self.dir == 1 and self.x > world_width + 50:
            self.x = -50
            self.base_y = random.randint(100, world_height - 100)

        if self.dir == -1 and self.x < -50:
            self.x = world_width + 50
            self.base_y = random.randint(100, world_height - 100)

    def draw(self, screen, camera_x):
        screen.blit(self.img, (self.x - camera_x, self.y))


class World_4_2(WorldBase):
    def start(self):
        self.person_name = "fish"
        self.JUMP_POWER = -15
        self.cat_y_offset = 120
        super().start()  # ← создаёт self.cat и self.camera

        self.target = ARMENIAN_LETTERS[self.world_num - 1].lower()
        self.hud_target_color = (20, 60, 222)  # синий цвет для цели
        self.letter_count = LETTER_COUNT
        self.need = NEED
        self.score = SCORE

        # ===== ФОН =====
        bg_img = self.load_bg()

        scale = SCREEN_HEIGHT / bg_img.get_height()
        w = int(bg_img.get_width() * scale)
        h = SCREEN_HEIGHT
        self.bg = pygame.transform.smoothscale(bg_img, (w, h))
        self.bg_w = self.bg.get_width()

        self.letters = []
        self.load_letter_bgs(self.world_num, self.level_num)

        # ===== Fish =====
        self.water_level = 280

        self.drop_img = [
            pygame.transform.scale(
                pygame.image.load("images/world_4/world_4_2/fish/seahorse.png").convert_alpha(), (70, 40)
            ),
            pygame.transform.scale(
                pygame.image.load("images/world_4/world_4_2/fish/fish_blue.png").convert_alpha(), (110, 55)
            ),
            pygame.transform.scale(
                pygame.image.load("images/world_4/world_4_2/fish/fish_red.png").convert_alpha(), (100, 75)
            ),
            pygame.transform.scale(
                pygame.image.load("images/world_4/world_4_2/fish/medusa.png").convert_alpha(), (60, 80)
            ),]

        # задний слой
        self.rain_back = [
            FishDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(100, WORLD_HEIGHT - 100),
                random.uniform(1, 2),
                random.choice(self.drop_img).copy(),
                self.water_level,
            )
            for _ in range(20)
        ]

        self.rain_front = [
            FishDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(100, WORLD_HEIGHT - 100),
                random.uniform(1.5, 2.2),
                random.choice(self.drop_img).copy(), 
                self.water_level,
            )
            for _ in range(16)
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
                else random.choice(ARMENIAN_LETTERS)
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
                    self.eat_sound.play()
                else:
                    now = pygame.time.get_ticks()
                    if now - self.last_hit_time > self.hit_cooldown:
                        self.lives -= 1
                        self.last_hit_time = now
                        self.eat_bad_sound.play()
                self.letters.remove(letter)

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
