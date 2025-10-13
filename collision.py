import math
from constants import PLAYER_SPEED, TILE_SIZE, MAP_WIDTH, MAP_HEIGHT
import pygame

def wall_collision(keys, player_x, player_y, player_angle, delta_time, game_map):
    move_x, move_y = 0, 0
    speed = PLAYER_SPEED * delta_time

    if keys[pygame.K_UP]:
        move_x += math.cos(player_angle) * speed
        move_y += math.sin(player_angle) * speed
    if keys[pygame.K_DOWN]:
        move_x -= math.cos(player_angle) * speed
        move_y -= math.sin(player_angle) * speed

    next_x = player_x + move_x
    next_y = player_y + move_y

    tile_x = int(next_x / TILE_SIZE)
    tile_y = int(next_y / TILE_SIZE)

    # Bounds check
    if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
        if game_map[tile_y][tile_x] != "#":
            player_x = next_x
            player_y = next_y

    return player_x, player_y


