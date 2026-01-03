from django.db import models


class GameState(models.Model):
    letters_eaten = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


    def portal_open(self):
        return self.letters_eaten >= 5