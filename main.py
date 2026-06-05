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
TEXT_COLOR = (255, 255, 255)

# Levels (0 = empty, 1 = wall, 2 = start, 3 = goal)
LEVELS = [
    [
        "11111111111111111111",
        "12000000000000000001",
        "11111111011111111101",
        "10000001010000000101",
        "10111101010111110101",
        "10100001000100010001",
        "10101111111101011111",
        "10101000000001000001",
        "10101111111111111101",
        "10000000000000000031",
        "11111111111111111111"
    ],
    [
        "11111111111111111111",
        "12010000000000001001",
        "10010111111111101001",
        "11010100000000101101",
        "10000101111110100001",
        "10111101000010111101",
        "10000001011010000001",
        "11111111010011111101",
        "10000000011110000001",
        "10111111110000111131",
        "11111111111111111111"
    ],
    [
        "11111111111111111111",
        "12000010000010000001",
        "10111010111010111101",
        "10001000100010100001",
        "11101111101111101111",
        "10000000000000000001",
        "10111111111111111101",
        "10100000000000000101",
        "10101111111111110101",
        "10001000000000003101",
        "11111111111111111111"
    ]
]

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 10, TILE_SIZE - 10)
        self.speed = 5
        self.color = PLAYER_COLOR

    def move(self, dx, dy, walls):
        # Move X
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: # moving right
                    self.rect.right = wall.left
                elif dx < 0: # moving left
                    self.rect.left = wall.right
        
        # Move Y
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0: # moving down
                    self.rect.bottom = wall.top
                elif dy < 0: # moving up
                    self.rect.top = wall.bottom

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Casual Maze Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 36)
        
        self.current_level = 0
        self.load_level()

    def load_level(self):
        if self.current_level >= len(LEVELS):
            self.game_over = True
            return

        self.game_over = False
        self.walls = []
        self.goal = None
        self.player = None
        
        level_data = LEVELS[self.current_level]
        # Center the maze on screen
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

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.player.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.player.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.player.speed
            
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.walls)

    def update(self):
        if self.game_over:
            return

        # Check goal collision
        if self.goal and self.player.rect.colliderect(self.goal):
            self.current_level += 1
            self.load_level()

    def draw(self):
        self.screen.fill(BG_COLOR)
        
        if self.game_over:
            text = self.font.render("You Win! Thanks for playing.", True, TEXT_COLOR)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(text, text_rect)
        else:
            # Draw walls
            for wall in self.walls:
                pygame.draw.rect(self.screen, WALL_COLOR, wall, border_radius=2)
                
            # Draw goal
            if self.goal:
                pygame.draw.rect(self.screen, GOAL_COLOR, self.goal, border_radius=5)
                
            # Draw player
            if self.player:
                self.player.draw(self.screen)
                
            # Draw level text
            level_text = self.font.render(f"Level {self.current_level + 1}", True, TEXT_COLOR)
            self.screen.blit(level_text, (10, 10))

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
