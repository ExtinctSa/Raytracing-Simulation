Hello!
This is my attempt to create a psuedo 3D environment in Pygame.
I want this project to be so much more than it currently is, as of right now it's a room with just walls.
I will probably come back to this in my free time to actually make a game, but for right now it's enough.
The program uses a 2 dimensional map and raytracing to create the illusion of walls
and collision is done by tracking the player's input and current location over the grid.

The video series by 3DSage called "Make Your Own Raycaster" was incredibly helpful for this project
They made theirs in C so I had a bit of a time getting it to work in Python.
I genuinely don't think I would've gotten this to work without it as raytracing uses
a lot of math.

Here's how the cast_rays() function works since it's the most interesting part:
1. Setup for Raycasting
start_angle = player_angle - FOV / 2
ray_angle_step = FOV / NUM_RAYS
Defines the leftmost starting angle of the player’s field of view.
Each ray will be cast in small steps (ray_angle_step) across the FOV.

2. Loop Over Rays
for ray in range(NUM_RAYS):
    ray_angle = start_angle + ray * ray_angle_step
    sin_a = math.sin(ray_angle)
    cos_a = math.cos(ray_angle)
Each iteration represents one vertical slice of the screen.
ray_angle: the direction this ray points in.
sin_a, cos_a: used for movement along the grid.

3. Initial Map Position
map_x = int(player_x / TILE_SIZE)
map_y = int(player_y / TILE_SIZE)
Converts the player’s position (world coordinates) into grid cell indices.

4. Ray Step Direction
step_x = 1 if cos_a > 0 else -1
step_y = 1 if sin_a > 0 else -1
Determines whether the ray moves right/left (x-axis) or up/down (y-axis).

5. Distance to Next Gridline
delta_dist_x = abs(TILE_SIZE / (cos_a + 1e-6))
delta_dist_y = abs(TILE_SIZE / (sin_a + 1e-6))
Precomputed step distance for when the ray crosses a vertical/horizontal gridline.
Prevents division by zero with + 1e-6.

6. Initial Side Distances
if cos_a > 0:
    side_dist_x = ((map_x + 1) * TILE_SIZE - player_x) / (cos_a + 1e-6)
else:
    side_dist_x = (player_x - map_x * TILE_SIZE) / (-cos_a + 1e-6)

if sin_a > 0:
    side_dist_y = ((map_y + 1) * TILE_SIZE - player_y) / (sin_a + 1e-6)
else:
    side_dist_y = (player_y - map_y * TILE_SIZE) / (-sin_a + 1e-6)
Calculates how far the ray must travel to hit the first vertical and horizontal gridline.

7. DDA (Digital Differential Analyzer) Grid Traversal
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
This is the ray marching loop.
At each step, the ray moves to the next vertical or horizontal grid boundary.
side = 0 → hit a vertical wall; side = 1 → horizontal wall.
Stops when the ray hits a wall ("#") or exceeds max render depth.

8. Fish-Eye Correction & Wall Height
corrected_depth = depth * math.cos(player_angle - ray_angle)
wall_height = (TILE_SIZE * SCREEN_HEIGHT) / (corrected_depth + 0.0001)
Corrects fish-eye distortion by projecting depth onto player’s viewing angle.
wall_height determines how tall the wall slice should appear on screen.

9. Texture Mapping
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
Finds the exact intersection point (hit_x, hit_y).
Chooses the column of pixels from the texture to display.
Flips texture horizontally depending on wall orientation.

10. Lighting / Brightness
if corrected_depth <= light_radius:
    global light_falloff
    brightness = 1 / (1 + (corrected_depth ** 2) / light_falloff)
    brightness = clamp(brightness, 0.0, 1.0)
else:
    brightness = 0.1
Simulates a light source with distance-based falloff.
Near walls are brighter, far walls dimmer.
I planned to implement a torch but I really want to move on to the next module.

11. Scale Column to Screen
scaled_column = pygame.transform.scale(
    texture_column,
    (SCREEN_WIDTH // NUM_RAYS, int(wall_height))
)
Scales the 1-pixel wide texture slice to the correct on-screen height.

12. Apply Lighting
light_surface = pygame.Surface(scaled_column.get_size()).convert_alpha()
val = int(brightness * 255)
light_surface.fill((val, val, val))
scaled_column.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
Creates a surface filled with grayscale brightness.
Multiplies with the texture slice to darken it properly.

13. Render to Screen
screen.blit(
    scaled_column,
    (ray * (SCREEN_WIDTH // NUM_RAYS), SCREEN_HEIGHT // 2 - wall_height // 2)
)
Places the textured, lit wall column at the right screen position.
Vertically centers it (SCREEN_HEIGHT // 2 - wall_height // 2).

Collision works as such:
It takes 6 parameters:
1. The keys pressed: "keys"
    This is done very similarly to how we did it in the Asteroids project.

2 and 3. The player's current x and y positions respectively: "player_x, player_y"

4. The player's current rotation angle: "player_angle"

5. delta_time

6. game_map

Movement vector starts at (0,0).
Speed is scaled by delta_time so movement stays smooth regardless of FPS.
move_x, move_y = 0, 0
speed = PLAYER_SPEED * delta_time
It's important to remember that while the cast_rays() function makes the game Look 3D it's still a 2 dimensional space.

if keys[pygame.K_UP]:
    move_x += math.cos(player_angle) * speed
    move_y += math.sin(player_angle) * speed
If up arrow is pressed: move forward in the direction of player_angle.
cos(angle) → movement along the x-axis.
sin(angle) → movement along the y-axis.
if keys[pygame.K_DOWN]:
    move_x -= math.cos(player_angle) * speed
    move_y -= math.sin(player_angle) * speed
If down arrow is pressed: move backward (opposite direction).

Next possible position for the player
next_x = player_x + move_x
next_y = player_y + move_y
This calculates where the player would be after movement.

Map tile position
tile_x = int(next_x / TILE_SIZE)
tile_y = int(next_y / TILE_SIZE)
Converts the pixel/world coordinates into grid indices.
For example: If TILE_SIZE = 64, then (128, 64) → (2, 1) in the map.

Collision check
if 0 <= tile_x < MAP_WIDTH and 0 <= tile_y < MAP_HEIGHT:
    if game_map[tile_y][tile_x] != "#":
        player_x = next_x
        player_y = next_y
First ensures the new tile is inside the map (bounds check).
Then checks the map cell:
If it’s not a wall ("#"), the move is valid → update player position.
If it is a wall, the move is blocked → player stays in place.

Finally, the return
return player_x, player_y
Returns the (possibly updated) position after handling collisions.
