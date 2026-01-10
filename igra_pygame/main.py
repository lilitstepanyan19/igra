import pygame
import random
import sys

# ---------- Настройки ----------
WIDTH, HEIGHT = 800, 600
FPS = 60
LETTERS_TO_EAT = 15
START_LIVES = 3
TIME_PER_ROUND = 5  # секунд
LETTER_SPEED = 1.5
BABY_START_SIZE = 32
MUSIC_FILE = "assets/music.mp3"  # положи сюда свою музыку
FONT_SIZE = 48

LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# ---------- Инициализация ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Малыш и буквы")
clock = pygame.time.Clock()

# ---------- Загрузка музыки ----------
try:
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.play(-1)  # бесконечный цикл
except Exception as e:
    print("Не удалось загрузить музыку:", e)

# ---------- Игровые переменные ----------
target_letter = random.choice(LETTERS)
letters = [target_letter] * 10 + random.sample(
    [l for l in LETTERS if l != target_letter], 2
)
random.shuffle(letters)

letter_objects = []

font = pygame.font.SysFont(None, FONT_SIZE)

for l in letters:
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    vx = (random.random() - 0.5) * LETTER_SPEED * 2
    vy = (random.random() - 0.5) * LETTER_SPEED * 2
    letter_objects.append({"letter": l, "x": x, "y": y, "vx": vx, "vy": vy})

score = 0
lives = START_LIVES
baby_size = BABY_START_SIZE
time_left = TIME_PER_ROUND

# ---------- Таймер ----------
pygame.time.set_timer(pygame.USEREVENT, 1000)  # каждую секунду

# ---------- Основной цикл ----------
running = True
while running:
    screen.fill((255, 255, 255))  # белый фон

    # ---------- События ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Таймер
        if event.type == pygame.USEREVENT:
            time_left -= 1
            if time_left <= 0:
                lives -= 1
                time_left = TIME_PER_ROUND
                if lives <= 0:
                    print("Игра окончена!")
                    running = False

        # Клик мышью
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for obj in letter_objects:
                text_surf = font.render(obj["letter"], True, (0, 0, 0))
                rect = text_surf.get_rect(topleft=(obj["x"], obj["y"]))
                if rect.collidepoint(mx, my):
                    if obj["letter"] == target_letter:
                        score += 1
                        baby_size += 5
                        letter_objects.remove(obj)
                        if score >= LETTERS_TO_EAT:
                            score = 0
                            target_letter = random.choice(LETTERS)
                            letters = [target_letter] * 3 + random.sample(
                                [l for l in LETTERS if l != target_letter], 2
                            )
                            random.shuffle(letters)
                            letter_objects = []
                            for l in letters:
                                x = random.randint(50, WIDTH - 50)
                                y = random.randint(50, HEIGHT - 50)
                                vx = (random.random() - 0.5) * LETTER_SPEED * 2
                                vy = (random.random() - 0.5) * LETTER_SPEED * 2
                                letter_objects.append(
                                    {"letter": l, "x": x, "y": y, "vx": vx, "vy": vy}
                                )
                    else:
                        lives -= 1
                        if lives <= 0:
                            print("Игра окончена!")
                            running = False

    # ---------- Движение букв ----------
    for obj in letter_objects:
        obj["x"] += obj["vx"]
        obj["y"] += obj["vy"]

        if obj["x"] < 0 or obj["x"] > WIDTH - FONT_SIZE:
            obj["vx"] *= -1
        if obj["y"] < 0 or obj["y"] > HEIGHT - FONT_SIZE:
            obj["vy"] *= -1

        text_surf = font.render(obj["letter"], True, (0, 0, 0))
        screen.blit(text_surf, (obj["x"], obj["y"]))

    # ---------- Рисуем малышку вместо курсора ----------
    mx, my = pygame.mouse.get_pos()
    baby_surf = font.render("👶", True, (0, 0, 0))
    baby_surf = pygame.transform.scale(baby_surf, (baby_size, baby_size))
    screen.blit(baby_surf, (mx - baby_size // 2, my - baby_size // 2))
    pygame.mouse.set_visible(False)

    # ---------- HUD ----------
    hud_font = pygame.font.SysFont(None, 36)
    hud = hud_font.render(
        f"Счёт: {score} | Жизни: {lives} | Время: {time_left} | Собери: {target_letter}",
        True,
        (0, 0, 0),
    )
    screen.blit(hud, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
