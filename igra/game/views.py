from django.shortcuts import render, redirect
import random

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
LETTERS_TO_EAT = 5
MAX_WORLDS = 3
START_LIVES = 3

def get_game_state(request):
    request.session.setdefault("count", 0)
    request.session.setdefault("world", 1)
    request.session.setdefault("lives", START_LIVES)
    return request.session


def game_page(request):
    state = get_game_state(request)

    # ❌ жизни закончились
    if state["lives"] <= 0:
        return render(request, "game/game_over.html")
    
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

    return render(
        request,
        template_name,
        {
            "letters": random.sample(LETTERS, 3),
            "count": state["count"],
            "world": state["world"],
            "lives": state["lives"],
            "time": 5,
        },
    )


def miss_letter(request):
    state = get_game_state(request)
    request.session.modified = True

    if request.method == "POST":
        state["lives"] -= 1

    return redirect("game:game_page")


def finish_page(request):
    return render(request, "game/finish_page.html")

def reset_game(request):
    request.session.flush()
    return redirect("game:game_page")
