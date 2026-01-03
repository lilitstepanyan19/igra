from django.urls import path
from .views import game_page, eat_letter, reset_game


urlpatterns = [
    path("", game_page, name="game"),
    path("api/eat/", eat_letter, name="eat_letter"),
    path("api/reset/", reset_game, name="reset_game"),
]
