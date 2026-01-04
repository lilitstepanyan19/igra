from django.shortcuts import render, redirect
import random

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LETTERS_TO_EAT = 5


def get_game_state(request):
    if "count" not in request.session:
        request.session["count"] = 0
    return request.session


# Главная страница - первый мир
def game_page(request):
    state = get_game_state(request)

    if request.method == "POST":
        state["count"] += 1
        if state["count"] >= LETTERS_TO_EAT:
            state["count"] = 0
            return redirect("game:world_page")  # переход на другой мир

    letter = random.choice(LETTERS)
    return render(
        request, "game/start.html", {"letter": letter, "count": state["count"]}
    )


# Страница второго мира
def world_page(request):
    state = get_game_state(request)

    if request.method == "POST":
        state["count"] += 1
        letter = random.choice(LETTERS)
        return render(
            request, "game/world.html", {"letter": letter, "count": state["count"]}
        )

    return render(request, "game/world.html", {"letter": None, "count": state["count"]})


# Сброс игры
def reset_game(request):
    request.session["count"] = 0
    return redirect("game:game_page")
