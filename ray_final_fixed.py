import pygame
import math
import os
import sys
import ast
import numpy as np

# --- Inicialización ---
pygame.init()
WIDTH, HEIGHT = 800, 600
HALF_HEIGHT = HEIGHT // 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raycaster Textured + Puertas - Christian")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 18)

# --- Configuración del jugador ---
posX, posY = 22.0, 12.0
dirX, dirY = -1.0, 0.0
planeX, planeY = 0.0, 0.66
moveSpeed = 0.12
rotSpeed = 0.05

# --- Mapa ---
defaultMap = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,9,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

level_path = os.path.join(os.path.dirname(__file__), "level.txt")

# --- Texturas ---
TEX_SIZE = 64
textures = {}
expected_textures = [
    "eagle", "redbrick", "purplestone", "greystone", "1","2","3","4","5","6",
    "bluestone", "mossy", "wood", "colorstone", "door"
]

def load_level(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = ast.literal_eval(f.read())
            if isinstance(data, list) and all(isinstance(r, list) for r in data):
                h = len(data)
                w = max((len(r) for r in data), default=0)
                for i, row in enumerate(data):
                    new_row = []
                    for v in row:
                        if isinstance(v, int):
                            new_row.append(v)
                        elif isinstance(v, str):
                            name = os.path.splitext(v)[0]
                            if name in expected_textures:
                                idx = expected_textures.index(name) + 1
                            else:
                                idx = 0
                            new_row.append(idx)
                        else:
                            new_row.append(0)
                    data[i] = new_row + [0] * (w - len(row))
                print(f"Mapa cargado desde {path} ({w}x{h})")
                return data
        except Exception as e:
            print("Error cargando level.txt:", e)
    print("Usando mapa por defecto.")
    return default

worldMap = load_level(level_path, defaultMap)

# --- Puertas ---
doors = {}
def is_door(x, y):
    """Devuelve la puerta en (x, y) si existe."""
    return doors.get((x, y))

# Detectar puertas (valor 9 en el mapa) - usar worldMap (posible nivel cargado)
# Detectar puertas (valor "door" convertido a índice 16)
# --- Detección de puertas (por nombre de textura) ---
for y, row in enumerate(worldMap):
    for x, val in enumerate(row):
        tex_name = expected_textures[val - 1] if 1 <= val <= len(expected_textures) else None
        if tex_name == "door":
            if (x, y) not in doors:
                doors[(x, y)] = {
                    "open": False,
                    "progress": 0.0,
                    "timer": 0.0  # tiempo desde que se abrió
                }


            
            
for name in expected_textures:
    path = os.path.join("textures", f"{name}.png")
    if os.path.exists(path):
        img = pygame.image.load(path).convert()
        if img.get_width() != TEX_SIZE or img.get_height() != TEX_SIZE:
            img = pygame.transform.smoothscale(img, (TEX_SIZE, TEX_SIZE))
        textures[name] = img

print(f"Cargadas {len(textures)} texturas.")

# --- Dibujar escena ---
def draw_scene():
    floor_tex = textures.get("colorstone")
    ceiling_tex = textures.get("wood") or floor_tex

    if floor_tex:
        tex_array_floor = pygame.surfarray.array3d(floor_tex)
        tex_array_ceil = pygame.surfarray.array3d(ceiling_tex)
        fh = HEIGHT // 2
        floor_buffer = np.zeros((WIDTH, fh, 3), dtype=np.uint8)
        ceiling_buffer = np.zeros((WIDTH, fh, 3), dtype=np.uint8)
        rayDirX0 = dirX - planeX
        rayDirY0 = dirY - planeY
        rayDirX1 = dirX + planeX
        rayDirY1 = dirY + planeY
        posZ = 0.5 * HEIGHT
        x_indices = np.arange(WIDTH)
        for y in range(fh):
            p = y + 0.5
            rowDist = posZ / p
            floorStepX = rowDist * (rayDirX1 - rayDirX0) / WIDTH
            floorStepY = rowDist * (rayDirY1 - rayDirY0) / WIDTH
            floorX = posX + rowDist * rayDirX0
            floorY = posY + rowDist * rayDirY0
            fx = floorX + floorStepX * x_indices
            fy = floorY + floorStepY * x_indices
            tx = (np.floor((fx % 1) * TEX_SIZE)).astype(int)
            ty = (np.floor((fy % 1) * TEX_SIZE)).astype(int)
            floor_buffer[:, y, :] = tex_array_floor[tx, ty, :]
            ceiling_buffer[:, fh - 1 - y, :] = tex_array_ceil[tx, ty, :]
        floor_surface = pygame.surfarray.make_surface(floor_buffer)
        screen.blit(floor_surface, (0, HALF_HEIGHT))
        ceiling_surface = pygame.surfarray.make_surface(ceiling_buffer)
        screen.blit(ceiling_surface, (0, 0))

    # --- Paredes y puertas ---
    for x in range(WIDTH):
        cameraX = 2 * x / float(WIDTH) - 1.0
        rayDirX = dirX + planeX * cameraX
        rayDirY = dirY + planeY * cameraX
        mapX = int(posX)
        mapY = int(posY)
        deltaDistX = abs(1 / rayDirX) if rayDirX != 0 else 1e30
        deltaDistY = abs(1 / rayDirY) if rayDirY != 0 else 1e30

        if rayDirX < 0:
            stepX = -1; sideDistX = (posX - mapX) * deltaDistX
        else:
            stepX = 1; sideDistX = (mapX + 1.0 - posX) * deltaDistX
        if rayDirY < 0:
            stepY = -1; sideDistY = (posY - mapY) * deltaDistY
        else:
            stepY = 1; sideDistY = (mapY + 1.0 - posY) * deltaDistY

        hit = False; side = 0
        while not hit:
            if sideDistX < sideDistY:
                sideDistX += deltaDistX; mapX += stepX; side = 0
            else:
                sideDistY += deltaDistY; mapY += stepY; side = 1
            cell = worldMap[mapY][mapX]
            if cell > 0:
                door = is_door(mapX, mapY)
                if door:
                    if door['progress'] < 1.0:
                        hit = True
                else:
                    hit = True

        # Evitar divisiones negativas o nulas
        perpWallDist = max(0.0001, abs((mapX - posX + (1 - stepX) / 2.0) / (rayDirX if side == 0 else rayDirY)))

        # --- Cálculo de distancia perpendicular corregido ---
        if side == 0:
            perpWallDist = (mapX - posX + (1 - stepX) / 2.0) / (rayDirX if rayDirX != 0 else 0.0001)
        else:
            perpWallDist = (mapY - posY + (1 - stepY) / 2.0) / (rayDirY if rayDirY != 0 else 0.0001)

        perpWallDist = max(perpWallDist, 0.8)  # evita deformación si la pared está demasiado cerca

        # Evita valores absurdos sin alterar la geometría
        if perpWallDist < 0.01:
            perpWallDist = 0.01
        # --- efecto de puerta (deslizamiento visual al abrir) ---
        door = is_door(mapX, mapY)
        if door:
            offset = door["progress"] * 0.9
            # mueve el muro según su orientación
            if side == 0:
                perpWallDist += offset if rayDirX > 0 else -offset
            else:
                perpWallDist += offset if rayDirY < 0 else -offset

        lineHeight = int(HEIGHT / perpWallDist)
        drawStart = max(-lineHeight // 2 + HALF_HEIGHT, 0)
        drawEnd = min(lineHeight // 2 + HALF_HEIGHT, HEIGHT - 1)



        texIndex = worldMap[mapY][mapX]
        texName = expected_textures[texIndex - 1] if 1 <= texIndex <= len(expected_textures) else None
        tex = textures.get(texName)
        if tex:
            if side == 0: wallX = posY + perpWallDist * rayDirY
            else: wallX = posX + perpWallDist * rayDirX
            wallX -= math.floor(wallX)
            texX = int(wallX * TEX_SIZE)
            if side == 0 and rayDirX > 0: texX = TEX_SIZE - texX - 1
            if side == 1 and rayDirY < 0: texX = TEX_SIZE - texX - 1

            # --- Desplazamiento de puerta ---
            door = is_door(mapX, mapY)
            if door:
                offset = int(TEX_SIZE * door['progress'])
                texX = (texX + offset) % TEX_SIZE

            column = tex.subsurface((texX, 0, 1, TEX_SIZE))
            column = pygame.transform.scale(column, (1, lineHeight))
            if side == 1: column.fill((180,180,180), special_flags=pygame.BLEND_MULT)
            screen.blit(column, (x, drawStart))
        else:
            pygame.draw.line(screen, (150,150,150), (x, drawStart), (x, drawEnd))

    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255,255,0))
    screen.blit(fps_text, (WIDTH - 120, 10))

# --- Colisión mejorada ---
def can_move(x, y):
    # radio de colisión: cuanto mayor, más lejos de la pared
    radius = 0.35
    # revisa 8 puntos alrededor del jugador
    for ox, oy in [(-radius, -radius), (-radius, radius), (radius, -radius), (radius, radius),
                   (-radius, 0), (radius, 0), (0, -radius), (0, radius)]:
        cell_x = int(x + ox)
        cell_y = int(y + oy)
        # validación de límites
        if not (0 <= cell_y < len(worldMap) and 0 <= cell_x < len(worldMap[0])):
            return False
        cell = worldMap[cell_y][cell_x]
        if cell != 0:
            door = is_door(cell_x, cell_y)
            # si es una puerta parcialmente cerrada o pared, bloquear
            if not door or door["progress"] < 0.9:
                return False
    return True





# --- Bucle principal ---
running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    
    # --- Movimiento del jugador ---
    # --- Movimiento del jugador ---
    nx, ny = posX, posY
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        nx = posX + dirX * moveSpeed
        ny = posY + dirY * moveSpeed
    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
        nx = posX - dirX * moveSpeed
        ny = posY - dirY * moveSpeed

    # Aplicar colisiones
    if can_move(nx, posY):
        posX = nx
    if can_move(posX, ny):
        posY = ny

        
    target = worldMap[int(ny)][int(nx)]
    door = is_door(int(nx), int(ny))
    
    if target == 0 or (door and door['progress'] > 0.8):
        posX, posY = nx, ny

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        oldDirX = dirX; dirX = dirX*math.cos(rotSpeed)-dirY*math.sin(rotSpeed)
        dirY = oldDirX*math.sin(rotSpeed)+dirY*math.cos(rotSpeed)
        oldPlaneX = planeX; planeX = planeX*math.cos(rotSpeed)-planeY*math.sin(rotSpeed)
        planeY = oldPlaneX*math.sin(rotSpeed)+planeY*math.cos(rotSpeed)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        oldDirX = dirX; dirX = dirX*math.cos(-rotSpeed)-dirY*math.sin(-rotSpeed)
        dirY = oldDirX*math.sin(-rotSpeed)+dirY*math.cos(-rotSpeed)
        oldPlaneX = planeX; planeX = planeX*math.cos(-rotSpeed)-planeY*math.sin(-rotSpeed)
        planeY = oldPlaneX*math.sin(-rotSpeed)+planeY*math.cos(-rotSpeed)

    # --- Interacción con puertas ---
    if keys[pygame.K_e]:
        fx = int(posX + dirX)
        fy = int(posY + dirY)
        door = is_door(fx, fy)
        if door:
            door["open"] = not door["open"]

    
    # --- Actualizar animación de puertas con temporizador ---
    for d in doors.values():
        speed = 0.04  # velocidad de apertura/cierre (más lenta = más suave)
        max_time_open = 5.0  # segundos antes de cerrar sola

        if d["open"]:
            if d["progress"] < 1.0:
                d["progress"] += speed
            else:
                d["timer"] += 1 / 40.0  # aprox. 1 frame = 1/60 seg
                if d["timer"] >= max_time_open:
                    d["open"] = False  # cerrar automáticamente
                    d["timer"] = 0.0
        else:
            if d["progress"] > 0.0:
                d["progress"] -= speed
                d["timer"] = 0.0  # reinicia contador

        d["progress"] = max(0.0, min(1.0, d["progress"]))


    screen.fill((80,160,255))
    draw_scene()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
