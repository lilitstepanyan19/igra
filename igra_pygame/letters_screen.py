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
        self.anim_duration = 60 

        self.font_big = pygame.font.Font('fonts/GHEAGpalatBld.otf', 150)
        self.font_big_handwriting = pygame.font.Font('fonts/Vrdznagir.otf', 150)
        self.font_small = pygame.font.Font('fonts/GHEAGpalatBld.otf', 30)

    def start(self):
        self.anim_time = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    # делаем переход на следующий мир
                    self.game.world = self.next_world_func()
                    if self.game.world:
                        self.game.world.start()

    def update(self):
        if self.anim_time < self.anim_duration:
            self.anim_time += 1

    def draw_hud(self, screen):
        pass

    def is_finished(self):
        return False

    def draw(self, screen):
        screen.fill((93, 173, 226))  # светло-голубой фон
        next_btn_text = "Այս տառը սովորելու համար "
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

        t = self.anim_time / self.anim_duration
        scale = 0.3 + 0.7 * t   # от маленькой к нормальной
        alpha = int(255 * t)

        # Расставляем буквы 2x2
        rows = 2
        cols = 2
        spacing_x = 160
        spacing_y = 200

        start_x = screen.get_width() // 2 - spacing_x
        start_y = screen.get_height() // 2 - spacing_y - 80
        
        for idx, ch in enumerate(self.letters[:4]):
            row = idx % cols
            col = idx // cols

            if isinstance(ch, pygame.Surface):
                img = ch
            else:
                if row == 0:
                    font = self.font_big
                else:
                    font = self.font_big_handwriting

                img = font.render(ch, True, (2, 36, 36))
            img = pygame.transform.smoothscale(
                img,
                (int(img.get_width() * scale), int(img.get_height() * scale))
            )
            img.set_alpha(alpha)

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y

            # полупрозрачный фон под буквой
            bg_rect = img.get_rect(topleft=(x, y))
            bg_surf = pygame.Surface((bg_rect.width + 20, bg_rect.height + 20), pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 100))
            # screen.blit(bg_surf, (x - 10, y - 10))

            # рендер буквы
            screen.blit(img, (x, y))
