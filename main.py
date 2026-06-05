from ursina import *
import random

app = Ursina(title="3D Retro Racing")

# Environment setup
window.color = color.light_gray
Sky()

# The Road and Grass
road = Entity(model='cube', color=color.dark_gray, scale=(12, 0.1, 200), position=(0, 0, 80))
grass_left = Entity(model='cube', color=color.lime, scale=(100, 0.1, 200), position=(-56, 0, 80))
grass_right = Entity(model='cube', color=color.lime, scale=(100, 0.1, 200), position=(56, 0, 80))

# Player Car
player = Entity(
    model='cube', 
    color=color.cyan, 
    scale=(1.5, 0.8, 3), 
    position=(0, 0.5, 0), 
    collider='box'
)

# Camera follows behind the player
camera.position = (0, 5, -12)
camera.rotation_x = 15

# Game variables
enemies = []
score = 0
game_over = False
speed = 30
spawn_timer = 0

# UI
score_text = Text(text=f'Score: {score}', position=(-0.85, 0.45), scale=2, color=color.white)
game_over_text = Text(text='', position=(0,0), scale=4, origin=(0,0), color=color.red, font='VeraMono.ttf')

def update():
    global score, game_over, speed, spawn_timer
    
    if game_over:
        if held_keys['space']:
            restart_game()
        return

    # Player movement
    if held_keys['a'] or held_keys['left arrow']:
        player.x -= 12 * time.dt
        player.rotation_y = -10
    elif held_keys['d'] or held_keys['right arrow']:
        player.x += 12 * time.dt
        player.rotation_y = 10
    else:
        player.rotation_y = 0

    # Keep player on the road
    player.x = clamp(player.x, -5, 5)

    # Infinite road effect (texture scrolling trick, but here we just move lines or let it be solid)
    # Ursina automatically makes it look like we move forward due to enemies coming at us.

    # Spawn enemies
    spawn_timer -= time.dt
    if spawn_timer <= 0:
        spawn_enemy()
        spawn_timer = max(0.5, 2.0 - (speed * 0.02))

    # Move enemies
    for e in enemies[:]:
        e.z -= speed * time.dt
        if e.z < -15:
            enemies.remove(e)
            destroy(e)
            score += 10
            score_text.text = f'Score: {score}'
            speed += 0.5 # Increase difficulty
        
        # Collision Detection
        if e.intersects(player).hit:
            game_over = True
            game_over_text.text = f'CRASHED!\nFinal Score: {score}\nPress SPACE to Restart'

def spawn_enemy():
    x_pos = random.uniform(-5, 5)
    c = random.choice([color.red, color.yellow, color.magenta, color.orange])
    # Vary size slightly for different vehicles
    w = random.uniform(1.5, 2.5)
    l = random.uniform(3, 5)
    e = Entity(model='cube', color=c, scale=(w, 1.2, l), position=(x_pos, 0.6, 120), collider='box')
    enemies.append(e)

def restart_game():
    global score, game_over, speed, spawn_timer
    game_over = False
    game_over_text.text = ''
    score = 0
    score_text.text = f'Score: {score}'
    speed = 30
    spawn_timer = 0
    player.x = 0
    player.rotation_y = 0
    for e in enemies:
        destroy(e)
    enemies.clear()

# Add basic lighting
DirectionalLight(y=2, z=3, shadows=True, rotation=(45, -45, 45))

app.run()
