from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path("", views.game_page, name="game_page"),
    path("miss/", views.miss_letter, name="miss_letter"),
    path("finish/", views.finish_page, name="finish_page"),
    path("reset/", views.reset_game, name="reset_game"),
]
