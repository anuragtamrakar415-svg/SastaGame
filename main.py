from ursina import *
import random

app = Ursina(title="Real 3D Racing")

# Environment setup
window.color = color.light_gray
Sky()

# Load Textures
road_tex = load_texture('assets/road_texture.png')
grass_tex = load_texture('assets/grass_texture.png')

# Create Road and Grass with textures
road = Entity(model='cube', texture=road_tex, color=color.white, scale=(12, 0.1, 200), position=(0, 0, 80), texture_scale=(1, 20))
grass_left = Entity(model='cube', texture=grass_tex, color=color.white, scale=(100, 0.1, 200), position=(-56, 0, 80), texture_scale=(10, 20))
grass_right = Entity(model='cube', texture=grass_tex, color=color.white, scale=(100, 0.1, 200), position=(56, 0, 80), texture_scale=(10, 20))

# --- Car Generator Function ---
def create_car(base_color, pos_x, pos_z, is_player=False):
    # Main parent entity
    car = Entity(position=(pos_x, 0.5, pos_z))
    
    # Chassis (Body)
    body = Entity(parent=car, model='cube', color=base_color, scale=(1.6, 0.6, 3.5), position=(0, 0, 0))
    
    # Cabin (Windows)
    cabin = Entity(parent=car, model='cube', color=color.dark_gray, scale=(1.2, 0.5, 1.8), position=(0, 0.5, -0.2))
    
    # Wheels
    wheel_scale = (0.3, 0.8, 0.8)
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(-0.9, -0.2, 1.2)) # Front Left
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(0.9, -0.2, 1.2))  # Front Right
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(-0.9, -0.2, -1.2))# Back Left
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(0.9, -0.2, -1.2)) # Back Right
    
    # Headlights
    Entity(parent=car, model='cube', color=color.white, scale=(0.4, 0.2, 0.1), position=(-0.5, 0.1, 1.8))
    Entity(parent=car, model='cube', color=color.white, scale=(0.4, 0.2, 0.1), position=(0.5, 0.1, 1.8))
    
    # Taillights
    Entity(parent=car, model='cube', color=color.red, scale=(0.4, 0.2, 0.1), position=(-0.5, 0.1, -1.8))
    Entity(parent=car, model='cube', color=color.red, scale=(0.4, 0.2, 0.1), position=(0.5, 0.1, -1.8))
    
    # Add Collider to the main entity for intersections
    car.collider = BoxCollider(car, center=(0,0,0), size=(1.6, 1.2, 3.5))
    
    return car

# Player Car
player = create_car(color.cyan, 0, 0, is_player=True)

# Camera follows behind the player
camera.position = (0, 6, -14)
camera.rotation_x = 18

# Game variables
enemies = []
score = 0
game_over = False
speed = 35
spawn_timer = 0
texture_offset = 0

# UI
score_text = Text(text=f'Score: {score}', position=(-0.85, 0.45), scale=2, color=color.white)
game_over_text = Text(text='', position=(0,0), scale=4, origin=(0,0), color=color.red, font='VeraMono.ttf')

def update():
    global score, game_over, speed, spawn_timer, texture_offset
    
    if game_over:
        if held_keys['space']:
            restart_game()
        return

    # Scroll road texture to simulate movement
    texture_offset += speed * time.dt * 0.05
    road.texture_offset = (0, texture_offset)
    grass_left.texture_offset = (0, texture_offset)
    grass_right.texture_offset = (0, texture_offset)

    # Player movement
    if held_keys['a'] or held_keys['left arrow']:
        player.x -= 15 * time.dt
        player.rotation_y = -12
    elif held_keys['d'] or held_keys['right arrow']:
        player.x += 15 * time.dt
        player.rotation_y = 12
    else:
        player.rotation_y = 0

    # Keep player on the road
    player.x = clamp(player.x, -5, 5)

    # Spawn enemies
    spawn_timer -= time.dt
    if spawn_timer <= 0:
        spawn_enemy()
        spawn_timer = max(0.4, 1.8 - (speed * 0.02))

    # Move enemies
    for e in enemies[:]:
        # Move enemies towards player (relative speed)
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
    x_pos = random.uniform(-4.5, 4.5)
    c = random.choice([color.red, color.yellow, color.magenta, color.orange, color.blue])
    e = create_car(c, x_pos, 120)
    # Enemy cars face us (or we face them), but let's make them face away from us as traffic
    enemies.append(e)

def restart_game():
    global score, game_over, speed, spawn_timer
    game_over = False
    game_over_text.text = ''
    score = 0
    score_text.text = f'Score: {score}'
    speed = 35
    spawn_timer = 0
    player.x = 0
    player.rotation_y = 0
    for e in enemies:
        destroy(e)
    enemies.clear()

# Add basic lighting
DirectionalLight(y=2, z=3, shadows=True, rotation=(45, -45, 45))
AmbientLight(color=color.rgba(100, 100, 100, 1))

app.run()
