# worlds/world_1/world_1_1.py
import pygame
import random
from base import WorldBase, WORLD_WIDTH, WORLD_HEIGHT, SCREEN_HEIGHT, NEED, SCORE, LETTER_COUNT, ARMENIAN_LETTERS
from letter import Letter, LETTER_SPEED  # импортируем новый класс


class World_3_2(WorldBase):

    def start(self):
        self.person_name = "dog"
        super().start()  # ← создаёт self.cat и self.camera
        self.target = ARMENIAN_LETTERS[self.world_num - 1]
        self.letter_count = LETTER_COUNT

        self.need = NEED
        self.score = SCORE

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

        # буквы
        for letter in self.letters:
            letter.draw(
                screen,
                self.game.font_good,
                self.game.font_bad,
                self.camera.camera_x,
                self.target,
            )
