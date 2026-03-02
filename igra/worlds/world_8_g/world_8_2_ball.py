import pygame
import math
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT, NEED, SCORE, LETTER_COUNT, ARMENIAN_LETTERS
from letter import Letter, LETTER_SPEED


class BallDrop:
    def __init__(self, x, y, speed, img):
        self.x = x
        self.y = y
        self.speed = speed

        # вращение
        self.original_img = img
        self.angle = 0

        self.dir = random.choice([-1, 1])

        # ===== ФИЗИКА =====
        self.vy = random.uniform(-12, -6)  # начальный прыжок вверх
        self.gravity = 0.4  # сила притяжения
        self.bounce = 0.9  # сила отскока (0–1)
        self.ground = WORLD_HEIGHT - 70  # уровень земли

        if self.dir == -1:
            self.original_img = pygame.transform.flip(self.original_img, True, False)

    def update(self, world_width, world_height):
        # движение по X
        self.x += self.speed * self.dir

        # вращение при движении
        self.angle -= self.speed * 5 * self.dir

        # ===== ГРАВИТАЦИЯ =====
        self.vy += self.gravity
        self.y += self.vy

        # ===== СТОЛКНОВЕНИЕ С ЗЕМЛЁЙ =====
        if self.y >= self.ground:
            self.y = self.ground
            self.vy *= -self.bounce  # отскок

            # если почти остановился — дать маленький прыжок
            if abs(self.vy) < 1:
                self.vy = random.uniform(-6, -3)

        # телепорт с другой стороны
        if self.dir == 1 and self.x > world_width + 50:
            self.x = -50

        if self.dir == -1 and self.x < -50:
            self.x = world_width + 50

    def draw(self, screen, camera_x):
        rotated = pygame.transform.rotate(self.original_img, self.angle)
        rect = rotated.get_rect(center=(self.x - camera_x, self.y))
        screen.blit(rotated, rect)


class World_8_3(WorldBase):
    def start(self):
        self.person_name = "lamp"
        self.JUMP_POWER = -15
        self.cat_y_offset = 30
        self.cat_kangaroo_jump_amplitude = 10
        
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

        self.drop_img = pygame.transform.scale(
                pygame.image.load("images/world_8/world_8_3/ball/ball_1.png").convert_alpha(), (70, 70)
            )

        # задний слой
        self.rain_back = [
            BallDrop(
                random.randint(0, WORLD_WIDTH),
                random.randint(100, WORLD_HEIGHT - 100),
                random.uniform(1, 2),
                self.drop_img,
            )
            for _ in range(20)
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
        for drop in self.rain_back:
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
