import pygame
import random
import os
import math
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT, NEED, SCORE, LETTER_COUNT, ARMENIAN_LETTERS
from letter import Letter, LETTER_SPEED  # импортируем новый класс


class World_12_2(WorldBase):

    def start(self):
        self.person_name = "ant"
        self.cat_width = 170
        self.cat_y_offset = -10
        self.JUMP_POWER = -30
        self.cat_anim_speed = 0.1
        self.cat_kangaroo_jump_amplitude = 30

        super().start()  # ← создаёт self.cat и self.camera
        self.target = ARMENIAN_LETTERS[self.world_num - 1]
        self.letter_count = LETTER_COUNT
        self.need = NEED
        self.score = SCORE

        self.good_target_color = (20, 38, 58)
        self.bad_target_color = (167, 16, 0)

        bg_img = self.load_bg()

        h = SCREEN_HEIGHT
        scale = SCREEN_HEIGHT / bg_img.get_height()
        w = int(bg_img.get_width() * scale)
        self.bg = pygame.transform.smoothscale(bg_img, (w, h))
        self.bg_w = self.bg.get_width()

        self.letters = []

        self.load_letter_bgs(self.world_num, self.level_num)

        self.start_time = pygame.time.get_ticks()
        self.spawn_delay_start = 2000  # 2 секунды перед первым появлением
        self.spawn_delay = 700  # пауза между появлениями
        self.last_spawn_time = self.start_time

        # ===== СОЛНЦЕ =====
        self.sun_imgs = []
        sun_folder = f"images/world_{self.world_num}/world_{self.world_num}_{self.level_num}/sun"

        if os.path.exists(sun_folder):
            for name in sorted(os.listdir(sun_folder)):
                if name.endswith(".png"):
                    img = pygame.image.load(os.path.join(sun_folder, name)).convert_alpha()
                    self.sun_imgs.append(img)

        self.sun_index = 0
        self.glow_alpha = 80
        # ===== ПАРАМЕТРЫ СОЛНЦА =====
        self.sun_x = SCREEN_HEIGHT - 100
        self.sun_y = 10

        self.sun_scale = 0.15     # размер
        self.sun_alpha = 230     # прозрачность 0–255

        self.sun_anim_speed = 0.02   # скорость анимации
        self.sun_float_amp = 5       # амплитуда плавания
        self.sun_float_speed = 0.2  # скорость плавания
        self.sun_time = 0

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
            vx = random.choice([-1, 1])
            vy = random.choice([-1, 1])
            self.letters.append(Letter(char, x, y, vx, vy, letter_bg))

    def update(self):
        super().update()
        cat_rect = self.cat.cat_rect

        ## ===== АНИМАЦИЯ СОЛНЦА =====
        if self.sun_imgs:
            self.sun_index += self.sun_anim_speed
            if self.sun_index >= len(self.sun_imgs):
                self.sun_index = 0

            self.sun_time += self.sun_float_speed

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

        # 🌞 солнце поверх фона
        if self.sun_imgs:
            img = self.sun_imgs[int(self.sun_index)]

            # масштаб
            w = int(img.get_width() * self.sun_scale)
            h = int(img.get_height() * self.sun_scale)
            img = pygame.transform.smoothscale(img, (w, h))

            # прозрачность
            img = img.copy()
            img.set_alpha(self.sun_alpha)

            # плавание вверх-вниз
            y_offset = int(math.sin(self.sun_time) * self.sun_float_amp)

            screen.blit(img, (self.sun_x, self.sun_y + y_offset))

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
                color = self.good_target_color
                font = self.game.font_good
            else:
                color = self.bad_target_color  # тёмно-синий
                font = self.game.font_bad

            text = font.render(letter.char, True, color)
            text_rect = text.get_rect(center=(x, y))
            screen.blit(text, text_rect)

        # буквы
        # for letter in self.letters:
        #     letter.draw(
        #         screen,
        #         self.game.font_good,
        #         self.game.font_bad,
        #         self.camera.camera_x,
        #         self.target,
        #     )
