import pygame
import math
from constants import *
from player import *
from collision import wall_collision

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


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

def cast_rays():
    start_angle = player_angle - FOV / 2
    for ray in range(NUM_RAYS):
        ray_angle = start_angle + (ray / NUM_RAYS) * FOV
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        for depth in range(1, MAX_DEPTH):
            target_x = int((player_x + cos_a * depth) / TILE_SIZE)
            target_y = int((player_y + sin_a * depth) / TILE_SIZE)
            # Add bounds check
            if (0 <= target_x < MAP_WIDTH) and (0 <= target_y < MAP_HEIGHT):
                if game_map[target_y][target_x] == "#":
                    # Wall hit
                    depth *= math.cos(player_angle - ray_angle)
                    wall_height = 20000 / (depth + 0.0001)
                    color = 255 / (1 + depth * depth * 0.0001)
                    pygame.draw.rect(screen, (color, color, color),
                                     (ray * (SCREEN_WIDTH // NUM_RAYS),
                                      SCREEN_HEIGHT // 2 - wall_height // 2,
                                      (SCREEN_WIDTH // NUM_RAYS),
                                      wall_height))
                    break
            else:
                break  # Out of bounds, stop this ray


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
