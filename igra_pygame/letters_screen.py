import pygame


class LettersScreen:
    def __init__(self, game, letters, next_world_func, lives=None):
        self.game = game
        self.letters = letters
        self.next_world_func = next_world_func

        self.lives = lives if lives is not None else 1

        self.cat = None
        self.camera = None

        self.anim_time = 0
        self.img_anim_time = 0
        self.per_letter_time = 80  # сколько кадров на появление одной буквы
        self.img_anim_duration = 40  # сколько кадров на появление картинки

        self.side_img = pygame.image.load("images/world_1/letters_screen/sun_1.png").convert_alpha()

        self.font_big = pygame.font.Font('fonts/GHEAGpalatBld.otf', 150)
        self.font_big_handwriting = pygame.font.Font('fonts/Vrdznagir.otf', 150)
        self.font_small = pygame.font.Font('fonts/GHEAGpalatBld.otf', 30)

    def start(self):
        self.anim_time = 0
        self.img_anim_time = 0

    def scale_contain(self, image, max_w, max_h):
        w, h = image.get_size()
        scale = min(max_w / w, max_h / h)
        return pygame.transform.smoothscale(
            image, (int(w * scale), int(h * scale))
        )

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    # делаем переход на следующий мир
                    self.game.world = self.next_world_func()
                    if self.game.world:
                        self.game.world.start()

    def update(self):
        self.anim_time += 1

        # анимируем картинку только после всех букв
        if self.anim_time >= self.per_letter_time * len(self.letters):
            if self.img_anim_time < self.img_anim_duration:
                self.img_anim_time += 1

    def draw_hud(self, screen):
        pass

    def is_finished(self):
        return False

    def draw(self, screen):
        screen.fill((93, 173, 226))  # светло-голубой фон
        next_btn_text = f"{self.letters[0]} տառը սովորելու համար "
        next_btn_text_2 = " սեղմիր SPACE կամ ENTER "

        next_btn = self.font_small.render(next_btn_text, True, (6, 48, 48))
        next_btn_2 = self.font_small.render(next_btn_text_2, True, (6, 48 , 48))

        screen.blit(
            next_btn,
            (screen.get_width() // 2 - next_btn.get_width() // 2, screen.get_height() - next_btn.get_height() - next_btn_2.get_height() - 40),
        )
        screen.blit(
            next_btn_2,
            (screen.get_width() // 2 - next_btn_2.get_width() // 2, screen.get_height() - next_btn_2.get_height() - 40),
        )

        # Расставляем буквы 2x2
        rows = 2
        cols = 2
        spacing_x = 200
        spacing_y = 200

        start_x = screen.get_width() // 2 - spacing_x - spacing_x // 2
        start_y = screen.get_height() // 2 - spacing_y - 30
        letters_width = spacing_x * 1.5
        letters_height = spacing_y 

        num_letters = min(4, len(self.letters))

        for idx, ch in enumerate(self.letters[:num_letters]):
            t_letter = min(max((self.anim_time - idx * self.per_letter_time) / self.per_letter_time, 0), 1)
            if t_letter < 0:  # буква уже начинается
                continue
            scale = 0.3 + 0.7 * t_letter
            letter_alpha = int(255 * t_letter)

            row = idx // cols
            col = idx % cols

            font = self.font_big if idx == 0 or idx == 2 else self.font_big_handwriting
            img = font.render(ch, True, (2,36,36))
            img = pygame.transform.smoothscale(
                img,
                (int(img.get_width() * scale), int(img.get_height() * scale))
            )
            img.set_alpha(letter_alpha)

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y - img.get_height() + 150
            screen.blit(img, (x, y))

        # --- Анимация картинки справа ---
        total_letters_time = self.per_letter_time * len(self.letters)
        if self.anim_time >= total_letters_time:
            # картинка появляется после букв
            t_img = min(1, self.img_anim_time / self.img_anim_duration)
            img_alpha = int(255 * t_img)
            side_img = self.scale_contain(self.side_img, letters_width, letters_height)
            side_img.set_alpha(img_alpha)
            side_x = (start_x + spacing_x * 2 + 40) 
            side_y = start_y + 80
            screen.blit(side_img, (side_x, side_y))

        # полупрозрачный фон под буквой
        bg_rect = img.get_rect(topleft=(x, y))
        bg_surf = pygame.Surface((bg_rect.width + 20, bg_rect.height + 20), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 100))
        # screen.blit(bg_surf, (x - 10, y - 10))
        # рендер буквы
