import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
TILE_SIZE = 40
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BG_COLOR = (30, 30, 30)
WALL_COLOR = (100, 100, 100)
PLAYER_COLOR = (50, 150, 255)
GOAL_COLOR = (50, 255, 50)
COIN_COLOR = (255, 215, 0)
ENEMY_COLOR = (255, 50, 50)
TEXT_COLOR = (255, 255, 255)

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_VICTORY = 3

# Levels
# 0=empty, 1=wall, 2=start, 3=goal, 4=coin, 5=enemy_horz, 6=enemy_vert
LEVELS = [
    [
        "11111111111111111111",
        "12000000000000000001",
        "11111111011111111141",
        "10040001010004000101",
        "10111101010111110101",
        "10100001000100010001",
        "10101111111101011111",
        "10101000000051000001",
        "10101111111111111101",
        "14000000000000000031",
        "11111111111111111111"
    ],
    [
        "11111111111111111111",
        "12010000004000001041",
        "10010111111111101001",
        "11010100000000101101",
        "10000101111110100001",
        "10111101000010111101",
        "10000501011010000501",
        "11111111010011111101",
        "14000000011110000001",
        "10111111110000111131",
        "11111111111111111111"
    ],
    [
        "11111111111111111111",
        "12000410000010000401",
        "10111010111010111101",
        "10061000106010100001",
        "11101111101111101111",
        "10000050000000000001",
        "10111111111111111101",
        "10140000005000000101",
        "10101111111111110101",
        "14001000000000003101",
        "11111111111111111111"
    ]
]

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 10, TILE_SIZE - 10)
        self.speed = 5
        self.color = PLAYER_COLOR

    def move(self, dx, dy, walls):
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                elif dx < 0: self.rect.left = wall.right
        
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0: self.rect.bottom = wall.top
                elif dy < 0: self.rect.top = wall.bottom

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)

class Enemy:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 10, TILE_SIZE - 10)
        self.dx = dx
        self.dy = dy
        self.speed = 3
        self.color = ENEMY_COLOR

    def update(self, walls):
        self.rect.x += self.dx * self.speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.dx > 0: self.rect.right = wall.left
                elif self.dx < 0: self.rect.left = wall.right
                self.dx *= -1 # reverse direction
                
        self.rect.y += self.dy * self.speed
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.dy > 0: self.rect.bottom = wall.top
                elif self.dy < 0: self.rect.top = wall.bottom
                self.dy *= -1 # reverse direction

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x + 10, y + 10, TILE_SIZE - 20, TILE_SIZE - 20)
        self.color = COIN_COLOR

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Casual Action Maze")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont("arial", 60, bold=True)
        self.font_small = pygame.font.SysFont("arial", 30)
        
        self.state = STATE_MENU
        self.current_level = 0
        self.score = 0
        
    def init_level(self):
        if self.current_level >= len(LEVELS):
            self.state = STATE_VICTORY
            return

        self.walls = []
        self.coins = []
        self.enemies = []
        self.goal = None
        self.player = None
        
        level_data = LEVELS[self.current_level]
        maze_width = len(level_data[0]) * TILE_SIZE
        maze_height = len(level_data) * TILE_SIZE
        self.offset_x = (SCREEN_WIDTH - maze_width) // 2
        self.offset_y = (SCREEN_HEIGHT - maze_height) // 2

        for row_idx, row in enumerate(level_data):
            for col_idx, col in enumerate(row):
                x = self.offset_x + col_idx * TILE_SIZE
                y = self.offset_y + row_idx * TILE_SIZE
                if col == "1":
                    self.walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
                elif col == "2":
                    self.player = Player(x + 5, y + 5)
                elif col == "3":
                    self.goal = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                elif col == "4":
                    self.coins.append(Coin(x, y))
                elif col == "5":
                    self.enemies.append(Enemy(x + 5, y + 5, 1, 0)) # horizontal
                elif col == "6":
                    self.enemies.append(Enemy(x + 5, y + 5, 0, 1)) # vertical

    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        if self.state == STATE_MENU:
            if keys[pygame.K_SPACE]:
                self.current_level = 0
                self.score = 0
                self.init_level()
                self.state = STATE_PLAYING
                
        elif self.state == STATE_GAME_OVER or self.state == STATE_VICTORY:
            if keys[pygame.K_SPACE]:
                self.state = STATE_MENU
                
        elif self.state == STATE_PLAYING:
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -self.player.speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = self.player.speed
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -self.player.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = self.player.speed
                
            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.walls)

    def update(self):
        if self.state != STATE_PLAYING:
            return

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.walls)
            if self.player.rect.colliderect(enemy.rect):
                self.state = STATE_GAME_OVER

        # Check coin collisions
        coins_to_remove = []
        for coin in self.coins:
            if self.player.rect.colliderect(coin.rect):
                self.score += 10
                coins_to_remove.append(coin)
        for c in coins_to_remove:
            self.coins.remove(c)

        # Check goal collision
        if self.goal and self.player.rect.colliderect(self.goal):
            self.current_level += 1
            self.init_level()

    def draw_text_centered(self, text, y_offset, font, color=TEXT_COLOR):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + y_offset))
        self.screen.blit(surface, rect)

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if self.state == STATE_MENU:
            self.draw_text_centered("CASUAL MAZE", -50, self.font_large)
            self.draw_text_centered("Press SPACE to Start", 50, self.font_small)
            
        elif self.state == STATE_GAME_OVER:
            self.draw_text_centered("GAME OVER", -50, self.font_large, (255, 100, 100))
            self.draw_text_centered(f"Final Score: {self.score}", 20, self.font_small)
            self.draw_text_centered("Press SPACE to return to Menu", 70, self.font_small)
            
        elif self.state == STATE_VICTORY:
            self.draw_text_centered("YOU WIN!", -50, self.font_large, GOAL_COLOR)
            self.draw_text_centered(f"Final Score: {self.score}", 20, self.font_small)
            self.draw_text_centered("Press SPACE to return to Menu", 70, self.font_small)
            
        elif self.state == STATE_PLAYING:
            for wall in self.walls:
                pygame.draw.rect(self.screen, WALL_COLOR, wall, border_radius=2)
            
            for coin in self.coins:
                coin.draw(self.screen)
                
            if self.goal:
                pygame.draw.rect(self.screen, GOAL_COLOR, self.goal, border_radius=5)
                
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            if self.player:
                self.player.draw(self.screen)
                
            # HUD
            lvl_text = self.font_small.render(f"Level: {self.current_level + 1}", True, TEXT_COLOR)
            score_text = self.font_small.render(f"Score: {self.score}", True, COIN_COLOR)
            self.screen.blit(lvl_text, (20, 20))
            self.screen.blit(score_text, (20, 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
