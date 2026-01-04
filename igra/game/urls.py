from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path("", views.game_page, name="game_page"),
    path("world/", views.world_page, name="world_page"),
    path("reset/", views.reset_game, name="reset_game"),
]
