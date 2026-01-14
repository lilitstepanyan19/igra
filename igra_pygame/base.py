import importlib


WORLD_WIDTH = 3000
WORLD_HEIGHT = 600

WIDTH, HEIGHT = 900, 600

class WorldBase:
    armenian_letters = "ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՈՒՓՔԵՕՖ"

    def __init__(self, game):
        self.game = game
        self.score = 0
        self.need = 1
        self.target = None

        # --- определяем мир и уровень по имени класса ---
        name = self.__class__.__name__  # например World_1_1
        _, w, l = name.split("_")
        self.world_num = int(w)
        self.level_num = int(l)

    def start(self):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

    def draw_hud(self, screen):
        take_text = "Բռնիր "
        count_text = f" {self.need - self.score} հատ"

        # Рендерим части
        take_surf = self.game.font_hud.render(take_text, True, (0, 0, 0))
        target_surf = self.game.font_good.render(self.target, True, (0, 180, 0))
        count_surf = self.game.font_hud.render(count_text, True, (0, 0, 0))

        # Позиции
        x, y = 20, 60

        # Рисуем HUD
        screen.blit(take_surf, (x, y))
        x += take_surf.get_width()
        screen.blit(target_surf, (x, y - 5))
        x += target_surf.get_width()
        screen.blit(count_surf, (x, y))

        # Дополнительно: WORLD / LEVEL
        header_text = f"Աշխարհ {self.world_num}, Փուլ- {self.level_num}   {self.score}/{self.need}"
        header_surf = self.game.font_hud.render(header_text, True, (0, 0, 0))
        screen.blit(header_surf, (20, 20))

    def is_finished(self):
        return self.score >= self.need

    def next_world(self):
        w, l = self.world_num, self.level_num + 1

        for next_world_num, next_level_num in [(w, l), (w + 1, 1)]:
            class_name = f"World_{next_world_num}_{next_level_num}"
            module_name = f"worlds.world_{next_world_num}.world_{next_world_num}_{next_level_num}"
            try:
                module = importlib.import_module(module_name)
                next_cls = getattr(module, class_name)
                return next_cls(self.game)
            except (ModuleNotFoundError, AttributeError):
                continue

        # следующего уровня или мира нет
        return None
