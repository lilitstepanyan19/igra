import pygame
import random
import sys
import math

# ---------- SETTINGS ----------
WIDTH, HEIGHT = 900, 600
FPS = 60

CAT_SPEED = 1
MOUSE_SPEED = 0.08
LETTER_SPEED = 1

TARGETS = ["A", "B", "C", "D"]  # Letters for worlds
NEED_TO_EAT = 5
START_LIVES = 3
TIME_LIMIT = 10  # seconds

# ---------- PYGAME ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat Catch Letters 😺")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 42)

# ---------- LOAD IMAGES ----------
bg_img = pygame.image.load("images/nebo_i_zemlya_bg.jpg").convert()
bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))


def load_cat(direction):
    frames = []
    for i in range(1, 9):
        img = pygame.image.load(f"images/cat_{i}_{direction}.png").convert_alpha()
        img = pygame.transform.scale(img, (120, 120))
        frames.append(img)
    return frames


cat_right = load_cat("right")
cat_left = load_cat("left")
cat_frames = cat_right
cat_index = 0
cat_x, cat_y = WIDTH // 2, HEIGHT // 2

# ---------- BOUNDS FOR CAT ----------
CAT_BOUNDS = pygame.Rect(0, 100, WIDTH, HEIGHT - 100)  # кот не выходит выше 100px

# ---------- GAME STATE ----------
world = 0
lives = START_LIVES
score = 0
timer = TIME_LIMIT
last_time = pygame.time.get_ticks()
letters = []

bg_x = 0
BG_SPEED = 1


def spawn_letters():
    letters.clear()
    target = TARGETS[world]
    for _ in range(7):
        if random.random() < 0.4:
            l = target
        else:
            l = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        x = random.randint(50, WIDTH - 50)
        y = random.randint(120, HEIGHT - 50)
        vx = random.choice([-1, 1]) * LETTER_SPEED
        vy = random.choice([-1, 1]) * LETTER_SPEED
        letters.append([l, x, y, vx, vy])


spawn_letters()

# ---------- GAME LOOP ----------
running = True
while running:
    screen.fill((235, 245, 255))

    # ---- move background ----
    bg_x -= BG_SPEED
    screen.blit(bg_img, (bg_x, 0))
    screen.blit(bg_img, (bg_x + WIDTH, 0))
    if bg_x <= -WIDTH:
        bg_x = 0

    # ---- events ----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- keyboard movement ----
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        cat_x -= CAT_SPEED
        cat_frames = cat_left
    if keys[pygame.K_RIGHT]:
        cat_x += CAT_SPEED
        cat_frames = cat_right
    if keys[pygame.K_UP]:
        cat_y -= CAT_SPEED
    if keys[pygame.K_DOWN]:
        cat_y += CAT_SPEED

    # ---- mouse movement ----
    mx, my = pygame.mouse.get_pos()
    dx = mx - cat_x
    dy = my - cat_y
    dist = math.hypot(dx, dy)
    if dist > 5:
        cat_x += dx * MOUSE_SPEED
        cat_y += dy * MOUSE_SPEED
        cat_frames = cat_right if dx > 0 else cat_left

    # ---- enforce cat bounds ----
    cat_rect = cat_frames[int(cat_index)].get_rect(center=(cat_x, cat_y))
    if cat_rect.left < CAT_BOUNDS.left:
        cat_x += CAT_BOUNDS.left - cat_rect.left
    if cat_rect.right > CAT_BOUNDS.right:
        cat_x -= cat_rect.right - CAT_BOUNDS.right
    if cat_rect.top < CAT_BOUNDS.top:
        cat_y += CAT_BOUNDS.top - cat_rect.top
    if cat_rect.bottom > CAT_BOUNDS.bottom:
        cat_y -= cat_rect.bottom - CAT_BOUNDS.bottom
    cat_rect.center = (cat_x, cat_y)

    # ---- animate cat ----
    cat_index += 0.25
    if cat_index >= len(cat_frames):
        cat_index = 0
    cat_img = cat_frames[int(cat_index)]

    # ---- timer ----
    now = pygame.time.get_ticks()
    if now - last_time >= 1000:
        timer -= 1
        last_time = now
        if timer <= 0:
            timer = TIME_LIMIT
            spawn_letters()  # respawn letters if time runs out

    # ---- move letters ----
    for l in letters:
        l[1] += l[3]
        l[2] += l[4]
        if l[1] < 0 or l[1] > WIDTH:
            l[3] *= -1
        if l[2] < 100 or l[2] > HEIGHT:
            l[4] *= -1

    # ---- collision ----
    for l in letters[:]:
        text = font.render(l[0], True, (0, 0, 0))
        rect = text.get_rect(center=(l[1], l[2]))
        if cat_rect.colliderect(rect):
            if l[0] == TARGETS[world]:
                score += 1
            letters.remove(l)  # убираем букву только если правильная

    # ---- next world ----
    if score >= NEED_TO_EAT:
        world += 1
        score = 0
        timer = TIME_LIMIT
        spawn_letters()
        if world >= len(TARGETS):
            screen.fill((0, 0, 0))
            win = font.render("YOU WIN! 😺🎉", True, (255, 255, 255))
            screen.blit(win, (WIDTH // 2 - 140, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(4000)
            running = False

    # ---- draw letters ----
    for l in letters:
        text = font.render(l[0], True, (0, 0, 0))
        screen.blit(text, (l[1], l[2]))

    # ---- draw cat ----
    screen.blit(cat_img, cat_rect)

    # ---- HUD ----
    hud1 = font.render(f"World: {world+1}  Target: {TARGETS[world]}", True, (0, 0, 0))
    hud2 = font.render(
        f"Score: {score}/{NEED_TO_EAT}   ❤️ {lives}   ⏱ {timer}", True, (0, 0, 0)
    )
    screen.blit(hud1, (20, 10))
    screen.blit(hud2, (20, 45))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
