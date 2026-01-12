class WorldBase:
    def __init__(self, game):
        self.game = game

    def start(self):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

    def is_finished(self):
        return False

    def next_world(self):
        return None
