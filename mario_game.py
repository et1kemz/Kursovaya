import pygame
import sys

# Инициализация pygame
pygame.init()

# Константы
WIDTH = 800
HEIGHT = 600
FPS = 60
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_STRENGTH = -15

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros. (Simplified)")
clock = pygame.time.Clock()

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.vel_y = 0
        self.on_ground = False

    def update(self):
        # Гравитация
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Ограничение падения на землю
        if self.rect.bottom > HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.on_ground = True
            self.vel_y = 0

        # Управление движением
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # Ограничение выхода за границы экрана
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

# Класс платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Создание игрока и платформ
player = Player()
platforms = pygame.sprite.Group()
platforms.add(Platform(0, HEIGHT - 50, WIDTH, 50))  # Основная платформа (земля)
platforms.add(Platform(200, HEIGHT - 150, 150, 20))  # Дополнительная платформа
platforms.add(Platform(500, HEIGHT - 250, 150, 20))  # Ещё одна платформа

# Группа спрайтов
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(platforms)

# Основной игровой цикл
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    # Обновление спрайтов
    all_sprites.update()

    # Проверка коллизий игрока с платформами
    hits = pygame.sprite.spritecollide(player, platforms, False)
    if hits:
        if player.vel_y > 0:  # Если игрок падает
            player.rect.bottom = hits[0].rect.top
            player.vel_y = 0
            player.on_ground = True

    # Отрисовка
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Обновление экрана
    pygame.display.flip()

pygame.quit()
sys.exit()