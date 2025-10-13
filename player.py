import pygame
import math
from constants import *

def rotate_player(keys, player_angle, delta_time):
    rot_speed = 1.5 * delta_time
    if keys[pygame.K_LEFT]:
        player_angle -= rot_speed
    if keys[pygame.K_RIGHT]:
        player_angle += rot_speed
    return player_angle