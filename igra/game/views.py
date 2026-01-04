from django.shortcuts import render, redirect
import random

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LETTERS_TO_EAT = 5
MAX_WORLDS = 3


def get_game_state(request):
    if "count" not in request.session:
        request.session["count"] = 0
    if "world" not in request.session:
        request.session["world"] = 1
    return request.session


def game_page(request):
    state = get_game_state(request)

    # Проверяем, не вышли ли за пределы миров
    if state["world"] > MAX_WORLDS:
        return redirect("game:finish_page")  # можно создать финальную страницу

    world_number = state["world"]
    template_name = f"game/world_{world_number}.html"

    if request.method == "POST":
        state["count"] += 1
        if state["count"] >= LETTERS_TO_EAT:
            state["count"] = 0
            state["world"] += 1
            return redirect("game:game_page")  # переход на следующий мир

    letter = random.choice(LETTERS)
    return render(request, template_name, {"letter": letter, "count": state["count"]})


def reset_game(request):
    request.session["count"] = 0
    request.session["world"] = 1
    return redirect("game:game_page")


def finish_page(request):
    return render(request, "game/finish_page.html")
