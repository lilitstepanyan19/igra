from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import GameState


def game_page(request):
    state, _ = GameState.objects.get_or_create(id=1)
    return render(request, "game/start.html", {"state": state})

def eat_letter(request):
    state, _ = GameState.objects.get_or_create(id=1)

    # Увеличиваем буквы, только если меньше 5
    if state.letters_eaten < 5:
        state.letters_eaten += 1
        state.save()

    # Всегда возвращаем JSON
    return JsonResponse({"letters": state.letters_eaten, "portal": state.portal_open()})


@require_POST
def reset_game(request):
    state, _ = GameState.objects.get_or_create(id=1)
    state.letters_eaten = 0
    state.save()
    return JsonResponse({"ok": True})
