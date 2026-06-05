from ursina import *
import random

app = Ursina(title="Real 3D Racing Challenge", fullscreen=True)

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
    car = Entity(position=(pos_x, 0.5, pos_z))
    body = Entity(parent=car, model='cube', color=base_color, scale=(1.6, 0.6, 3.5), position=(0, 0, 0))
    cabin = Entity(parent=car, model='cube', color=color.dark_gray, scale=(1.2, 0.5, 1.8), position=(0, 0.5, -0.2))
    wheel_scale = (0.3, 0.8, 0.8)
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(-0.9, -0.2, 1.2))
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(0.9, -0.2, 1.2))
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(-0.9, -0.2, -1.2))
    Entity(parent=car, model='cube', color=color.black, scale=wheel_scale, position=(0.9, -0.2, -1.2))
    Entity(parent=car, model='cube', color=color.white, scale=(0.4, 0.2, 0.1), position=(-0.5, 0.1, 1.8))
    Entity(parent=car, model='cube', color=color.white, scale=(0.4, 0.2, 0.1), position=(0.5, 0.1, 1.8))
    Entity(parent=car, model='cube', color=color.red, scale=(0.4, 0.2, 0.1), position=(-0.5, 0.1, -1.8))
    Entity(parent=car, model='cube', color=color.red, scale=(0.4, 0.2, 0.1), position=(0.5, 0.1, -1.8))
    car.collider = BoxCollider(car, center=(0,0,0), size=(1.6, 1.2, 3.5))
    return car

# Player Car
player = create_car(color.cyan, 0, 0, is_player=True)
camera.position = (0, 6, -14)
camera.rotation_x = 18

# Game variables
enemies = []
coins = []
score = 0
game_over = False
base_speed = 35
current_speed = 35
spawn_timer = 0
coin_timer = 0
texture_offset = 0

# UI
score_text = Text(text=f'Score: {int(score)}', position=(-0.85, 0.45), scale=2, color=color.white)
speed_text = Text(text=f'Speed: {int(current_speed * 2)} MPH', position=(0.55, 0.45), scale=2, color=color.yellow)
game_over_text = Text(text='', position=(0,0), scale=4, origin=(0,0), color=color.red, font='VeraMono.ttf')

def update():
    global score, game_over, base_speed, current_speed, spawn_timer, coin_timer, texture_offset
    
    if game_over:
        if held_keys['space']:
            restart_game()
        return

    # Accelerator and Brakes
    if held_keys['w'] or held_keys['up arrow']:
        current_speed = lerp(current_speed, base_speed * 2.5, time.dt * 2)
    elif held_keys['s'] or held_keys['down arrow']:
        current_speed = lerp(current_speed, base_speed * 0.4, time.dt * 4)
    else:
        current_speed = lerp(current_speed, base_speed, time.dt * 3)

    # Scroll texture based on current speed
    texture_offset += current_speed * time.dt * 0.05
    road.texture_offset = (0, texture_offset)
    grass_left.texture_offset = (0, texture_offset)
    grass_right.texture_offset = (0, texture_offset)

    # Score increases faster if you drive faster
    score += current_speed * time.dt * 0.1
    score_text.text = f'Score: {int(score)}'
    speed_text.text = f'Speed: {int(current_speed * 2)} MPH'

    # Player steering
    if held_keys['a'] or held_keys['left arrow']:
        player.x -= 15 * time.dt
        player.rotation_y = -12
    elif held_keys['d'] or held_keys['right arrow']:
        player.x += 15 * time.dt
        player.rotation_y = 12
    else:
        player.rotation_y = 0

    player.x = clamp(player.x, -5, 5)

    # Spawn enemies (spawn faster if driving faster)
    spawn_timer -= (current_speed / base_speed) * time.dt
    if spawn_timer <= 0:
        spawn_enemy()
        spawn_timer = max(0.4, 1.8 - (base_speed * 0.02))

    # Spawn coins
    coin_timer -= (current_speed / base_speed) * time.dt
    if coin_timer <= 0:
        spawn_coin()
        coin_timer = random.uniform(1.0, 3.0)

    # Move enemies
    for e in enemies[:]:
        e.z -= current_speed * time.dt
        if e.z < -15:
            enemies.remove(e)
            destroy(e)
            base_speed += 0.2 # Base difficulty increases over time
        elif e.intersects(player).hit:
            game_over = True
            game_over_text.text = f'CRASHED!\nFinal Score: {int(score)}\nPress SPACE to Restart'

    # Move and collect coins
    for c in coins[:]:
        c.rotation_y += 100 * time.dt
        c.z -= current_speed * time.dt
        if c.z < -15:
            coins.remove(c)
            destroy(c)
        elif c.intersects(player).hit:
            score += 50
            coins.remove(c)
            destroy(c)

def spawn_enemy():
    x_pos = random.uniform(-4.5, 4.5)
    c = random.choice([color.red, color.yellow, color.magenta, color.orange, color.blue])
    e = create_car(c, x_pos, 120)
    enemies.append(e)

def spawn_coin():
    x_pos = random.uniform(-4.5, 4.5)
    c = Entity(model='sphere', color=color.gold, scale=(1.5, 1.5, 1.5), position=(x_pos, 1, 120), collider='box')
    c.rotation_x = 90
    coins.append(c)

def restart_game():
    global score, game_over, base_speed, current_speed, spawn_timer, coin_timer
    game_over = False
    game_over_text.text = ''
    score = 0
    base_speed = 35
    current_speed = 35
    spawn_timer = 0
    coin_timer = 0
    player.x = 0
    player.rotation_y = 0
    for e in enemies: destroy(e)
    for c in coins: destroy(c)
    enemies.clear()
    coins.clear()

DirectionalLight(y=2, z=3, shadows=True, rotation=(45, -45, 45))
AmbientLight(color=color.rgba(100, 100, 100, 1))

app.run()
