import pygame, sys, random

WIDTH, HEIGHT = 800, 450
GROUND_Y = 360
BG_COLOR = (20, 24, 31)
PLAYER_COLOR = (80, 200, 120)
SPIKE_COLOR = (240, 80, 80)

PLAYER_W, PLAYER_H = 40,40

pygame.mixer.init()
pygame.mixer.music.load("byte-blast-8-bit-arcade-music-background-music-for-video-208780.mp3")
pygame.mixer.music.play(-1)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dash-game")

background = pygame.image.load("rapterra.jpg").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_img = pygame.image.load("sock.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (PLAYER_W, PLAYER_H))

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

player_rect = pygame.Rect(120, GROUND_Y - PLAYER_H, PLAYER_W, PLAYER_H)
 
vel_y = 0.0
gravity = 0.7
jump_strength = -12.0
on_ground = True
coyote_frames = 6  
coyote_timer = 0

spikes = []
scroll_speed = 6
spawn_cooldown = 0
score = 0
alive = True
 
 
def reset():
    global player_rect, vel_y, on_ground, coyote_timer, spikes, scroll_speed, spawn_cooldown, score, alive
    player_rect.x = 120
    player_rect.y = GROUND_Y - PLAYER_H
    player_rect.width = PLAYER_W
    player_rect.height = PLAYER_H
    vel_y = 0.0
    on_ground = True
    coyote_timer = 0
    spikes = []
    scroll_speed = 6
    spawn_cooldown = 0
    score = 0
    alive = True
    
def spawn_spike():
    base_w = random.choice([40, 50, 60])
    height = base_w
    x = WIDTH + random.randint(0, 100)
    points = [(x, GROUND_Y), (x + base_w, GROUND_Y), (x + base_w // 2, GROUND_Y - height)]
    return points

def move_spikes(spikes_list, dx):
    return [[(px - dx, py) for (px, py) in tri] for tri in spikes_list]
 
 
def draw_ground():
    pygame.draw.rect(screen, (35, 40, 52), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
 
 
def draw_spike(tri):
    pygame.draw.polygon(screen, SPIKE_COLOR, tri)
 
 
def tri_to_rect(tri):
    xs = [p[0] for p in tri]
    ys = [p[1] for p in tri]
    return pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
 
 
def rect_triangle_collision(rect, tri):
    r = tri_to_rect(tri)
    if not rect.colliderect(r):
        return False
 
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
 
    def point_in_tri(pt, a, b, c):
        d1 = sign(pt, a, b)
        d2 = sign(pt, b, c)
        d3 = sign(pt, c, a)
        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
        return not (has_neg and has_pos)
 
    corners = [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom),
    ]
    a, b, c = tri[0], tri[1], tri[2]
    if any(point_in_tri(pt, a, b, c) for pt in corners):
        return True
 
    for x in range(rect.left, rect.right, 6):
        if point_in_tri((x, rect.bottom), a, b, c):
            return True
    return False
 
 
reset()
 # figure out how to get jumping and collision sounds to work
jump_sound = pygame.mixer.Sound("jump.mp3")
jump_sound.set_volume(0.9)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset()
            if alive and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                if on_ground or coyote_timer > 0:
                    vel_y = jump_strength
                    on_ground = False
                    coyote_timer = 0
                    jump_sound.play()
 
    if alive:
        vel_y += gravity
        player_rect.y += int(vel_y)
 
        if player_rect.bottom >= GROUND_Y:
            player_rect.bottom = GROUND_Y
            vel_y = 0
            if not on_ground:
                on_ground = True
            coyote_timer = coyote_frames
        else:
            on_ground = False
            coyote_timer = max(0, coyote_timer - 1)
 
        spawn_cooldown -= 1
        if spawn_cooldown <= 0:
            spikes.append(spawn_spike())
            spawn_cooldown = random.randint(30, 70)
 
        spikes = move_spikes(spikes, scroll_speed)
 
        spikes = [tri for tri in spikes if tri_to_rect(tri).right > -5]
 
        for tri in spikes:
            if rect_triangle_collision(player_rect, tri):
                alive = False
                break
 
        score += 1
        if score % 600 == 0:
            scroll_speed += 0.7
 
    screen.blit(background, (0, 0))
    draw_ground()
 
    for tri in spikes:
        draw_spike(tri)
 
    screen.blit(player_img, player_rect)
 
    s_text = font.render(f"Score: {score}", True, (220, 220, 220))
    tip_text = font.render("Space/Up to jump • R to reset", True, (160, 160, 180))
    status_text = font.render("Game Over — press R to try again" if not alive else "", True, (255, 120, 120))
    screen.blit(s_text, (20, 20))
    screen.blit(tip_text, (20, 54))
    if not alive:
        screen.blit(status_text, (20, 88))
 
    pygame.display.flip()
    clock.tick(60)