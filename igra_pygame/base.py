import importlib

class WorldBase:
    armenian_letters = "ԱԲԳԴԵԶԷԸԹԺԻԼԽԾԿՀՁՂՃՄՅՆՇՈՉՊՋՌՍՎՏՐՑՈՒՓՔԵՕՖ"

    def __init__(self, game):
        self.game = game

    def start(self):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

    def draw_hud(self, screen):
        name = self.__class__.__name__          # World_1_1
        _, world_num, level_num = name.split("_")

        hud = self.game.font_hud.render(
            f"Աշխարհ {world_num}, Փուլ- {level_num}   {self.score}/{self.need}",
            True,
            (0, 0, 0)
        )
        take_text = f"Բռնիր "
        count_text = f" {self.need - self.score} հատ"

        # Рендерим отдельными текстами
        take_surf = self.game.font_hud.render(take_text, True, (0, 0, 0))
        target_surf = self.game.font_good.render(
            self.target, True, (0, 180, 0)
        )  # цвет можно как в игре
        count_surf = self.game.font_hud.render(count_text, True, (0, 0, 0))

        # Позиции на экране
        x = 20
        y = 60

        # Рисуем все подряд
        self.game.screen.blit(take_surf, (x, y))
        x += take_surf.get_width()  # сдвигаем X после первой части
        self.game.screen.blit(target_surf, (x, y - 15))
        x += target_surf.get_width()
        self.game.screen.blit(count_surf, (x, y))
        screen.blit(hud, (20, 20))

    def is_finished(self):
        return self.score >= self.need

    def next_world(self):
        name = self.__class__.__name__  # например, World_1_1
        _, world_num, level_num = name.split("_")
        world_num = int(world_num)
        level_num = int(level_num)
    
        # 1️⃣ Сначала пробуем следующий уровень в том же мире
        next_level_num = level_num + 1
        next_class_name = f"World_{world_num}_{next_level_num}"
        module_name = f"worlds.world_{world_num}.world_{world_num}_{next_level_num}"
    
        try:
            module = importlib.import_module(module_name)
            next_cls = getattr(module, next_class_name)
            return next_cls(self.game)
        except ModuleNotFoundError:
            # если модуля нет → попробуем следующий мир
            next_world_num = world_num + 1
            next_level_num = 1
            next_class_name = f"World_{next_world_num}_{next_level_num}"
            module_name = f"worlds.world_{next_world_num}.world_{next_world_num}_{next_level_num}"
            try:
                module = importlib.import_module(module_name)
                next_cls = getattr(module, next_class_name)
                return next_cls(self.game)
            except ModuleNotFoundError:
                # следующего мира тоже нет → конец игры
                return None
        except AttributeError:
            # если класс внутри модуля не найден
            return None
