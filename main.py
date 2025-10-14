import pygame
import math
from constants import *
from player import *
from collision import wall_collision


# this is here so I don't have to import the entire torch library just for clamp
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))
# the amount of googling to figure out this function was insane
# save yourself the trouble and just copy this
# hours of my life .... wasted

game_map = [
    "##########",
    "#........#",
    "#..##....#",
    "#........#",
    "#........#",
    "#........#",
    "#...##...#",
    "#........#",
    "#........#",
    "##########"
]


player_x = 100
player_y = 100
player_angle = 0
light_radius = 150
light_falloff = (light_radius / 2) ** 2

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

wall_texture = pygame.image.load("assets/textures/wall.png").convert()
texture_size = wall_texture.get_width()

# Unfortuantely I cannot move this function to another file
# without causing heaps of issues at least
# so all scene rendering lives here
# as much as it hurts me to not categorize
# moving it to a render.py file causes player movement to break, idk why
# spaghetti code :)
def cast_rays():
    start_angle = player_angle - FOV / 2
    ray_angle_step = FOV / NUM_RAYS

    for ray in range(NUM_RAYS):
        ray_angle = start_angle + ray * ray_angle_step
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        map_x = int(player_x / TILE_SIZE)
        map_y = int(player_y / TILE_SIZE)

        step_x = 1 if cos_a > 0 else -1
        step_y = 1 if sin_a > 0 else -1

        delta_dist_x = abs(TILE_SIZE / (cos_a + 1e-6))
        delta_dist_y = abs(TILE_SIZE / (sin_a + 1e-6))

        if cos_a > 0:
            side_dist_x = ((map_x + 1) * TILE_SIZE - player_x) / (cos_a + 1e-6)
        else:
            side_dist_x = (player_x - map_x * TILE_SIZE) / (-cos_a + 1e-6)

        if sin_a > 0:
            side_dist_y = ((map_y + 1) * TILE_SIZE - player_y) / (sin_a + 1e-6)
        else:
            side_dist_y = (player_y - map_y * TILE_SIZE) / (-sin_a + 1e-6)

        hit = False
        side = None
        depth = 0
        while not hit and depth < MAX_DEPTH:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
                depth = (map_x * TILE_SIZE - player_x + (1 - step_x) / 2 * TILE_SIZE) / (cos_a + 1e-6)
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                depth = (map_y * TILE_SIZE - player_y + (1 - step_y) / 2 * TILE_SIZE) / (sin_a + 1e-6)

            if game_map[map_y][map_x] == "#":
                hit = True

        if not hit:
            continue

        corrected_depth = depth * math.cos(player_angle - ray_angle)
        wall_height = (TILE_SIZE * SCREEN_HEIGHT) / (corrected_depth + 0.0001)

        hit_x = player_x + cos_a * depth
        hit_y = player_y + sin_a * depth

        if side == 0:
            texture_x = int(hit_y % TILE_SIZE / TILE_SIZE * texture_size)
            if cos_a < 0:
                texture_x = texture_size - texture_x - 1
        else:
            texture_x = int(hit_x % TILE_SIZE / TILE_SIZE * texture_size)
            if sin_a > 0:
                texture_x = texture_size - texture_x - 1

        texture_column = wall_texture.subsurface((texture_x, 0, 1, texture_size))

        if corrected_depth <= light_radius:
            global light_falloff
            brightness = 1 / (1 + (corrected_depth ** 2) / light_falloff)
            brightness = clamp(brightness, 0.0, 1.0)
        else:
            brightness = 0.1

        scaled_column = pygame.transform.scale(
            texture_column,
            (SCREEN_WIDTH // NUM_RAYS, int(wall_height))
        )

        light_surface = pygame.Surface(scaled_column.get_size()).convert_alpha()
        val = int(brightness * 255)
        light_surface.fill((val, val, val))
        scaled_column.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        screen.blit(
            scaled_column,
            (ray * (SCREEN_WIDTH // NUM_RAYS), SCREEN_HEIGHT // 2 - wall_height // 2)
        )


def game_loop():
    global player_x, player_y, player_angle
    running = True
    while running:
        delta_time = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player_angle = rotate_player(keys, player_angle, delta_time)
        player_x, player_y = wall_collision(keys, player_x, player_y, player_angle, delta_time, game_map)
        screen.fill(DARK_GRAY)
        cast_rays()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    game_loop()
