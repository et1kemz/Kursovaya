# doodle_jump.py
import pygame
import sys
import random

# Инициализация pygame
pygame.init()

# Константы
WIDTH = 400
HEIGHT = 600
FPS = 60
GRAVITY = 0.4  # Уменьшил гравитацию для более плавного прыжка
PLAYER_SPEED = 4
JUMP_STRENGTH = -12
PLATFORM_COUNT = 15  # Увеличил количество платформ
SCROLL_THRESHOLD = 200

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
GREEN = (100, 200, 100)
LIGHT_GREEN = (150, 250, 150)

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doodle Jump")
clock = pygame.time.Clock()

def create_player_surface():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (255, 100, 100), (0, 0, 40, 40))
    pygame.draw.ellipse(surf, BLACK, (10, 10, 8, 8))
    pygame.draw.ellipse(surf, BLACK, (22, 10, 8, 8))
    pygame.draw.arc(surf, BLACK, (10, 15, 20, 15), 0.2, 2.9, 2)
    return surf

def create_platform_surface(width):
    surf = pygame.Surface((width, 15), pygame.SRCALPHA)
    pygame.draw.rect(surf, GREEN, (0, 0, width, 12), border_radius=5)
    pygame.draw.rect(surf, LIGHT_GREEN, (0, 0, width, 8), border_radius=5)
    return surf

def create_bg_texture():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill(SKY_BLUE)
    for _ in range(10):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(30, 80)
        pygame.draw.ellipse(surf, WHITE, (x, y, size, size//2))
    return surf

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = create_player_surface()
        self.rect = self.image.get_rect()
        self.reset_position()
        self.vel_y = 0
        self.on_ground = False
        self.score = 0
        self.highest_point = HEIGHT
        self.is_alive = True
    
    def reset_position(self):
        self.rect.center = (WIDTH // 2, HEIGHT - 100)
        self.vel_y = 0
        self.on_ground = False
        self.highest_point = HEIGHT
        self.is_alive = True

    def update(self):
        if not self.is_alive:
            return
            
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        if self.rect.left < 0:
            self.rect.right = WIDTH
        if self.rect.right > WIDTH:
            self.rect.left = 0

        if self.rect.top < self.highest_point:
            self.highest_point = self.rect.top
            self.score = HEIGHT - self.highest_point

        if self.rect.top > HEIGHT:
            self.is_alive = False

    def jump(self):
        if self.on_ground and self.is_alive:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width=70):
        super().__init__()
        self.image = create_platform_surface(width)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

def create_platforms():
    platforms = pygame.sprite.Group()
    platforms.add(Platform(WIDTH//2 - 35, HEIGHT - 50))
    
    # Генерация платформ с меньшим расстоянием между ними
    for i in range(PLATFORM_COUNT):
        x = random.randint(0, WIDTH - 70)
        # Уменьшил вертикальное расстояние между платформами (100-200 вместо 50-HEIGHT-50)
        y = random.randint(100, 200) * (i+1) // 2
        platforms.add(Platform(x, y))
    
    return platforms

def show_game_over_screen():
    screen.fill(SKY_BLUE)
    font_large = pygame.font.SysFont('Arial', 48)
    font_small = pygame.font.SysFont('Arial', 24)
    
    game_over_text = font_large.render("Game Over!", True, RED)
    score_text = font_small.render(f"Your score: {int(player.score)}", True, BLACK)
    restart_text = font_small.render("Press R to restart", True, BLACK)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

# Инициализация игры
player = Player()
platforms = create_platforms()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
all_sprites.add(platforms)
bg_texture = create_bg_texture()
font = pygame.font.SysFont('Arial', 24)

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
    
    if player.is_alive:
        all_sprites.update()

        # Проверка коллизий с платформами только при падении (vel_y > 0)
        if player.vel_y > 0:
            hits = pygame.sprite.spritecollide(player, platforms, False)
            if hits:
                # Находим самую верхнюю платформу из всех столкнувшихся
                top_platform = min(hits, key=lambda p: p.rect.top)
                
                # Проверяем, что игрок находится выше центра платформы
                if player.rect.bottom < top_platform.rect.centery:
                    player.rect.bottom = top_platform.rect.top
                    player.vel_y = JUMP_STRENGTH
                    player.on_ground = True

        # Прокрутка мира вниз
        if player.rect.top < SCROLL_THRESHOLD and player.vel_y < 0:
            scroll_amount = player.vel_y  # Отрицательное значение, поэтому вычитаем
            
            for platform in platforms:
                platform.rect.y -= scroll_amount
                
                # Если платформа ушла за нижнюю границу, перемещаем ее наверх
                if platform.rect.top > HEIGHT:
                    platform.rect.x = random.randint(0, WIDTH - 70)
                    platform.rect.y = random.randint(-50, 0)
            
            # Корректируем позицию игрока
            player.rect.top = SCROLL_THRESHOLD
            player.highest_point = SCROLL_THRESHOLD

        screen.blit(bg_texture, (0, 0))
        all_sprites.draw(screen)
        score_text = font.render(f"Score: {int(player.score)}", True, BLACK)
        screen.blit(score_text, (10, 10))
    else:
        show_game_over_screen()
        # Сброс игры
        player = Player()
        platforms = create_platforms()
        all_sprites = pygame.sprite.Group()
        all_sprites.add(player)
        all_sprites.add(platforms)
        bg_texture = create_bg_texture()
    
    pygame.display.flip()

pygame.quit()
sys.exit()