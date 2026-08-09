import os
import pygame

from paths import file_path


class LettersScreen:

    def __init__(self, game, letters, world_num, next_world_func, lives=None):
        self.game = game
        self.letters = letters
        self.next_world_func = next_world_func
        self.world_num = world_num

        self.lives = lives if lives is not None else 1

        self.cat = None
        self.camera = None

        self.anim_time = 0
        self.img_anim_time = 0
        self.per_letter_time = 80  # сколько кадров на появление одной буквы
        self.img_anim_duration = 40  # сколько кадров на появление картинки

        folder = f"images/world_{self.world_num}/letters_screen"
        self.raw_side_img = None
        self.scaled_side_img = None

        if os.path.exists(folder):
            files = [f for f in os.listdir(folder) if f.lower().endswith(".webp")]
            if files:
                path = os.path.join(folder, files[0])
                self.raw_side_img = pygame.image.load(file_path(path)).convert_alpha()

        self.font_big = self.game.font_big
        self.font_big_handwriting = self.game.font_big_handwriting
        self.font_small = self.game.font_small

        self.is_android = self.game.is_android
        self.next_triggered = False

        # Кэширование зарендеренного текста подсказок
        next_btn_text = f"{self.letters[0]} տառը սովորելու համար "
        next_btn_text_2 = (
            " սեղմիր էկրանին" if self.is_android else " սեղմիր SPACE կամ ENTER"
        )

        self.next_btn_surf = self.font_small.render(
            next_btn_text, True, (6, 48, 48)
        ).convert_alpha()
        self.next_btn_2_surf = self.font_small.render(
            next_btn_text_2, True, (6, 48, 48)
        ).convert_alpha()

        # Предварительный рендеринг исходных букв
        self.rendered_letters = []
        num_letters = min(4, len(self.letters))
        for idx, ch in enumerate(self.letters[:num_letters]):
            font = self.font_big if idx == 0 or idx == 2 else self.font_big_handwriting
            surf = font.render(ch, True, (2, 36, 36)).convert_alpha()
            self.rendered_letters.append(surf)

    def start(self):
        self.anim_time = 0
        self.img_anim_time = 0

    def scale_contain(self, image, max_w, max_h):
        w, h = image.get_size()
        scale = min(max_w / w, max_h / h)
        # На Android лучше применять быструю scale вместо медленной smoothscale
        return pygame.transform.scale(
            image, (max(1, int(w * scale)), max(1, int(h * scale)))
        ).convert_alpha()

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self._go_next()

            elif e.type == pygame.MOUSEBUTTONDOWN:
                self._go_next()

    def _go_next(self):
        if not hasattr(self, "next_triggered") or not self.next_triggered:
            self.next_triggered = True
            self.game.world = self.next_world_func()
            if self.game.world:
                self.game.world.start()

    def update(self):
        self.anim_time += 1

        # Анимируем картинку только после появления всех букв
        if self.anim_time >= self.per_letter_time * len(self.letters):
            if self.img_anim_time < self.img_anim_duration:
                self.img_anim_time += 1

    def draw_hud(self, screen):
        pass

    def is_finished(self):
        return False

    def draw(self, screen):
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        center_x = screen_width // 2
        center_y = screen_height // 2

        screen.fill((93, 173, 226))  # Светло-голубой фон

        # Вывод готового подсказочного текста (без создания нового объекта на каждом кадре)
        screen.blit(
            self.next_btn_surf,
            (
                center_x - self.next_btn_surf.get_width() // 2,
                screen_height
                - self.next_btn_surf.get_height()
                - self.next_btn_2_surf.get_height()
                - screen_height * 0.04,
            ),
        )
        screen.blit(
            self.next_btn_2_surf,
            (
                center_x - self.next_btn_2_surf.get_width() // 2,
                screen_height
                - self.next_btn_2_surf.get_height()
                - screen_height * 0.04,
            ),
        )

        # Расстановка букв 2x2
        cols = 2
        spacing_x = int(screen_width * 0.20)
        spacing_y = int(screen_height * 0.20)

        start_x = center_x - spacing_x - spacing_x // 2
        start_y = center_y - spacing_y - 30
        letters_width = spacing_x * 1.5
        letters_height = spacing_y

        # Подготовка боковой картинки (если ещё не подготовлена)
        if self.raw_side_img and self.scaled_side_img is None:
            self.scaled_side_img = self.scale_contain(
                self.raw_side_img, letters_width, letters_height
            )

        for idx, base_img in enumerate(self.rendered_letters):
            t_letter = min(
                max(
                    (self.anim_time - idx * self.per_letter_time)
                    / self.per_letter_time,
                    0,
                ),
                1,
            )
            if t_letter <= 0:  # Буква ещё не появилась
                continue

            scale = 0.3 + 0.7 * t_letter
            letter_alpha = int(255 * t_letter)

            row = idx // cols
            col = idx % cols

            # Масштабируем готовую букву быстрой функцией scale
            w = max(1, int(base_img.get_width() * scale))
            h = max(1, int(base_img.get_height() * scale))
            img = pygame.transform.scale(base_img, (w, h)).convert_alpha()
            img.set_alpha(letter_alpha)

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y - h + 150
            screen.blit(img, (x, y))

        # --- Анимация картинки справа ---
        total_letters_time = self.per_letter_time * len(self.letters)
        if self.scaled_side_img and self.anim_time >= total_letters_time:
            t_img = min(1.0, self.img_anim_time / self.img_anim_duration)
            img_alpha = int(255 * t_img)

            # Используем готовую отмасштабированную картинку
            side_img = self.scaled_side_img.copy()
            side_img.set_alpha(img_alpha)

            side_x = start_x + spacing_x * 2 + 40
            side_y = start_y + 80
            screen.blit(side_img, (side_x, side_y))

    def draw_overlay(self, screen):
        self.draw(screen)
