import pygame
import sys
import random

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 40
FPS = 60

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRASS_GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Directions
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

# Map Layout
MAP = [
    "BBBBBBBBBBBBBBBBBBBB",
    "B..................B",
    "B..BBB.......BBB...B",
    "B..B B.......B B...B",
    "B..BBB.......BBB...B",
    "B..................B",
    "B.......GGGG.......B",
    "B.......G..G.......B",
    "B.......G..G.......B",
    "B.......GGGG.......B",
    "B..................B",
    "B..BBB.......BBB...B",
    "B..B B.......B B...B",
    "B..BBB.......BBB...B",
    "B..................B",
    "BBBBBBBBBBBBBBBBBBBB",
]

def create_wall_grid():
    walls = []
    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            if tile == 'B':
                walls.append(pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE))
    return walls

class Tank:
    def __init__(self, x, y, color, controls, is_ai=False):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.color = color
        self.direction = UP
        self.speed = 3
        self.controls = controls
        self.is_ai = is_ai
        self.ai_timer = 0
        self.ai_direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.shoot_cooldown = 0

    def move(self, dx, dy, walls):
        new_rect = self.rect.move(dx, dy)
        for wall in walls:
            if new_rect.colliderect(wall):
                return
        if 0 <= new_rect.left and new_rect.right <= SCREEN_WIDTH:
            if 0 <= new_rect.top and new_rect.bottom <= SCREEN_HEIGHT:
                self.rect = new_rect

    def update(self, keys, walls, enemy, bullets):
        if self.is_ai:
            self.ai_update(walls, enemy, bullets)
        else:
            if keys[self.controls['up']]:
                self.direction = UP
                self.move(0, -self.speed, walls)
            elif keys[self.controls['down']]:
                self.direction = DOWN
                self.move(0, self.speed, walls)
            elif keys[self.controls['left']]:
                self.direction = LEFT
                self.move(-self.speed, 0, walls)
            elif keys[self.controls['right']]:
                self.direction = RIGHT
                self.move(self.speed, 0, walls)
            if keys[self.controls['shoot']]:
                self.shoot(bullets)
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)

    def ai_update(self, walls, enemy, bullets):
        self.ai_timer += 1
        if self.ai_timer >= FPS * 2:
            self.ai_direction = random.choice([UP, DOWN, LEFT, RIGHT])
            self.ai_timer = 0
        
        dx, dy = 0, 0
        if self.ai_direction == UP: dy = -self.speed
        elif self.ai_direction == DOWN: dy = self.speed
        elif self.ai_direction == LEFT: dx = -self.speed
        else: dx = self.speed
        
        self.direction = self.ai_direction
        self.move(dx, dy, walls)
        
        if random.random() < 0.02:
            self.shoot(bullets)

    def shoot(self, bullets):
        if self.shoot_cooldown <= 0:
            offset = TILE_SIZE//2
            if self.direction == UP:
                bullet = Bullet(self.rect.centerx, self.rect.top, UP, self)
            elif self.direction == DOWN:
                bullet = Bullet(self.rect.centerx, self.rect.bottom, DOWN, self)
            elif self.direction == LEFT:
                bullet = Bullet(self.rect.left, self.rect.centery, LEFT, self)
            else:
                bullet = Bullet(self.rect.right, self.rect.centery, RIGHT, self)
            bullets.append(bullet)
            self.shoot_cooldown = 30

class Bullet:
    def __init__(self, x, y, direction, owner):
        self.rect = pygame.Rect(x-2, y-2, 4, 4)
        self.direction = direction
        self.speed = 8
        self.owner = owner

    def update(self, walls, tanks):
        dx, dy = 0, 0
        if self.direction == UP: dy = -self.speed
        elif self.direction == DOWN: dy = self.speed
        elif self.direction == LEFT: dx = -self.speed
        else: dx = self.speed
        
        self.rect.move_ip(dx, dy)
        
        for wall in walls[:]:
            if self.rect.colliderect(wall):
                walls.remove(wall)
                return True
        
        for tank in tanks:
            if tank != self.owner and self.rect.colliderect(tank.rect):
                return True
        
        if not (0 <= self.rect.left <= SCREEN_WIDTH and 0 <= self.rect.top <= SCREEN_HEIGHT):
            return True
        
        return False

def draw_game(screen, tanks, bullets, walls, game_over, winner):
    screen.fill(GRASS_GREEN)
    
    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, BROWN, wall)
    
    # Draw tanks
    for tank in tanks:
        pygame.draw.rect(screen, tank.color, tank.rect)
        turret_length = TILE_SIZE//2
        center = tank.rect.center
        if tank.direction == UP:
            end = (center[0], center[1] - turret_length)
        elif tank.direction == DOWN:
            end = (center[0], center[1] + turret_length)
        elif tank.direction == LEFT:
            end = (center[0] - turret_length, center[1])
        else:
            end = (center[0] + turret_length, center[1])
        pygame.draw.line(screen, BLACK, center, end, 3)
    
    # Draw bullets
    for bullet in bullets:
        pygame.draw.rect(screen, bullet.owner.color, bullet.rect)
    
    # Game over text
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render(f'{winner} WINS!', True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
    
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tank Battle")
    clock = pygame.time.Clock()

    walls = create_wall_grid()
    
    player_controls = {
        'up': pygame.K_w,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'right': pygame.K_d,
        'shoot': pygame.K_SPACE
    }
    
    tanks = [
        Tank(2*TILE_SIZE, 2*TILE_SIZE, GREEN, player_controls),
        Tank(SCREEN_WIDTH-3*TILE_SIZE, SCREEN_HEIGHT-3*TILE_SIZE, PURPLE, None, is_ai=True)
    ]
    
    bullets = []
    game_over = False
    winner = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        
        if not game_over:
            # Update tanks
            for tank in tanks:
                if tank.is_ai:
                    tank.update(None, walls, tanks[0], bullets)
                else:
                    tank.update(keys, walls, None, bullets)
            
            # Update bullets
            for bullet in bullets[:]:
                if bullet.update(walls, tanks):
                    bullets.remove(bullet)
                    # Check for tank hit
                    for tank in tanks:
                        if tank.rect.colliderect(bullet.rect) and tank != bullet.owner:
                            game_over = True
                            winner = "GREEN" if bullet.owner == tanks[0] else "PURPLE"

        draw_game(screen, tanks, bullets, walls, game_over, winner)
        clock.tick(FPS)

if __name__ == "__main__":
    main()