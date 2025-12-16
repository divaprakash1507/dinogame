import pygame
import sys
import random
import os

# ---------- Settings ----------
WIDTH, HEIGHT = 800, 400
FPS = 60
GROUND_Y = 330

DAY_SKY = (135, 206, 250)
NIGHT_SKY = (10, 15, 40)

DAY_GROUND = (76, 175, 80)
NIGHT_GROUND = (20, 60, 35)

DAY_TEXT = (0, 0, 0)
NIGHT_TEXT = (230, 230, 240)

CLOUD_COLOR = (255, 255, 255)
STAR_COLOR = (255, 255, 255)

NIGHT_CYCLE_TIME = 20000
MIN_GAP = 900


# ---------- Highscore ----------
def load_highscore():
    path = os.path.join(os.path.dirname(__file__), "highscore.txt")
    if not os.path.exists(path):
        return 0
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def save_highscore(score):
    path = os.path.join(os.path.dirname(__file__), "highscore.txt")
    with open(path, "w") as f:
        f.write(str(score))


# ---------- Image Loader ----------
def load_sprite(path, size):
    try:
        img = pygame.image.load(os.path.join(os.path.dirname(__file__), path)).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        fallback = pygame.Surface(size)
        fallback.fill((255, 0, 255))
        return fallback


# ---------- Classes ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, sprite):
        super().__init__()
        self.image = sprite
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.bottom = GROUND_Y
        self.rect.left = 50

        self.vel_y = 0
        self.jump_power = -16
        self.gravity = 1
        self.is_jumping = False

    def update(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.is_jumping = False

        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_power
            self.is_jumping = True


class Cactus(pygame.sprite.Sprite):
    def __init__(self, images, speed):
        super().__init__()
        self.image = random.choice(images)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.bottom = GROUND_Y
        self.rect.x = WIDTH + random.randint(0, 200)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class Bird(pygame.sprite.Sprite):
    def __init__(self, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = WIDTH + random.randint(0, 250)
        self.rect.y = random.randint(150, 250)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        w = random.randint(60, 110)
        h = random.randint(25, 40)

        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, CLOUD_COLOR, self.image.get_rect())
        self.rect = self.image.get_rect()

        self.rect.x = WIDTH + random.randint(0, 150)
        self.rect.y = random.randint(40, 130)
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()


class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(1, 3)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, STAR_COLOR, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH)
        self.rect.y = random.randint(0, 180)


# ---------- Sun & Moon ----------
def draw_crescent_moon(screen):
    pygame.draw.circle(screen, (230, 230, 230), (650, 80), 28)
    pygame.draw.circle(screen, NIGHT_SKY, (660, 75), 28)


def draw_sun(screen):
    pygame.draw.circle(screen, (255, 220, 120), (650, 80), 36)
    pygame.draw.circle(screen, (255, 200, 50), (650, 80), 28)
    for angle in range(0, 360, 30):
        v = pygame.math.Vector2(1, 0).rotate(angle)
        pygame.draw.line(
            screen,
            (255, 210, 80),
            (650 + 40 * v.x, 80 + 40 * v.y),
            (650 + 52 * v.x, 80 + 52 * v.y),
            3
        )


# ---------- Main ----------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Runner Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 24)

    # ONLY DINO
    player_sprite = load_sprite("dino.png", (70, 70))

    bird_sprite = load_sprite("bird.png", (60, 60))
    cactus_images = [
        load_sprite("cactus1.png", (60, 80)),
        load_sprite("cactus2.png", (70, 70)),
    ]

    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    stars = pygame.sprite.Group()

    player = Player(player_sprite)
    all_sprites.add(player)

    SPAWN_CACTUS = pygame.USEREVENT + 1
    SPAWN_BIRD = pygame.USEREVENT + 2
    SPAWN_CLOUD = pygame.USEREVENT + 3

    pygame.time.set_timer(SPAWN_CACTUS, 1200)
    pygame.time.set_timer(SPAWN_BIRD, 2000)
    pygame.time.set_timer(SPAWN_CLOUD, 1800)

    last_cactus = 0
    last_bird = 0

    score = 0
    highscore = load_highscore()
    speed = 8
    game_over = False

    is_night = False
    last_cycle = pygame.time.get_ticks()

    running = True
    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if not game_over:
                        player.jump()
                    else:
                        return main()

            if not game_over and event.type == SPAWN_CACTUS:
                now = pygame.time.get_ticks()
                if now - last_bird > MIN_GAP:
                    c = Cactus(cactus_images, speed)
                    all_sprites.add(c)
                    obstacles.add(c)
                    last_cactus = now

            if not game_over and event.type == SPAWN_BIRD:
                now = pygame.time.get_ticks()
                if now - last_cactus > MIN_GAP:
                    b = Bird(bird_sprite, speed + 1)
                    all_sprites.add(b)
                    obstacles.add(b)
                    last_bird = now

            if not game_over and event.type == SPAWN_CLOUD:
                all_sprites.add(Cloud())

        if not game_over:
            all_sprites.update()
            score += dt / 10
            speed = 8 + int(score // 300)

            for o in obstacles:
                o.speed = speed + 1 if isinstance(o, Bird) else speed

            if pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask):
                game_over = True
                if int(score) > highscore:
                    highscore = int(score)
                    save_highscore(highscore)

        now = pygame.time.get_ticks()
        if now - last_cycle > NIGHT_CYCLE_TIME:
            is_night = not is_night
            last_cycle = now
            if is_night:
                stars.empty()
                for _ in range(50):
                    stars.add(Star())

        if is_night:
            screen.fill(NIGHT_SKY)
            stars.draw(screen)
            draw_crescent_moon(screen)
            pygame.draw.rect(screen, NIGHT_GROUND, (0, GROUND_Y, WIDTH, HEIGHT))
            text_color = NIGHT_TEXT
        else:
            screen.fill(DAY_SKY)
            draw_sun(screen)
            pygame.draw.rect(screen, DAY_GROUND, (0, GROUND_Y, WIDTH, HEIGHT))
            text_color = DAY_TEXT

        all_sprites.draw(screen)

        screen.blit(font.render(f"Score: {int(score)}", True, text_color), (20, 20))
        screen.blit(font.render(f"Highscore: {highscore}", True, text_color), (20, 50))

        if game_over:
            msg = font.render("GAME OVER - Press SPACE", True, text_color)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
