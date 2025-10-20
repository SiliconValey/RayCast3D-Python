import pygame
import sys
import os

pygame.init()
# Tamaño del mapa por defecto (igual que tu juego)
COLS, ROWS = 24, 20
TILE = 28
MARGIN = 8
PALETTE = {
    0: ((30, 30, 30), "Empty"),
    1: ((200, 80, 80), "Wall"),
    2: ((120, 200, 120), "Type 2"),
    3: ((120, 160, 240), "Type 3"),
    4: ((200, 200, 120), "Type 4"),
    5: ((180, 120, 200), "Type 5"),
}
FONT = pygame.font.SysFont("Consolas", 16)

W = COLS * TILE + MARGIN * 2
H = ROWS * TILE + 140
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Level Editor - Raycasting3D")
clock = pygame.time.Clock()

# archivo por defecto para guardar/cargar
SAVE_FILE = "level.txt"

def make_empty(cols, rows, border_walls=True):
    grid = [[0 for _ in range(cols)] for __ in range(rows)]
    if border_walls:
        for x in range(cols):
            grid[0][x] = 1
            grid[rows-1][x] = 1
        for y in range(rows):
            grid[y][0] = 1
            grid[y][cols-1] = 1
    return grid

# intenta cargar si existe el archivo de guardado
def load_from_file(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        data = eval(txt, {})  # archivo controlado por el usuario; evaluar como literal
        if isinstance(data, list) and all(isinstance(r, list) for r in data):
            return data
    except Exception as e:
        print("Error cargando:", e)
    return None

def save_to_file(path, grid):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("[\n")
            for row in grid:
                f.write("  " + repr(row) + ",\n")
            f.write("]\n")
        print("Guardado en", path)
    except Exception as e:
        print("Error guardando:", e)

grid = load_from_file(SAVE_FILE) or make_empty(COLS, ROWS)
selected = 1

def draw_ui():
    screen.fill((40, 40, 40))
    # grid
    for y in range(ROWS):
        for x in range(COLS):
            val = grid[y][x]
            color = PALETTE.get(val, ((120, 120, 120), ""))[0]
            rect = pygame.Rect(MARGIN + x*TILE, MARGIN + y*TILE, TILE-1, TILE-1)
            pygame.draw.rect(screen, color, rect)
    # palette
    py = MARGIN + ROWS*TILE + 10
    px = MARGIN
    screen.fill((20,20,20), (0, ROWS*TILE + MARGIN + 6, W, H - (ROWS*TILE + MARGIN + 6)))
    for key in sorted(PALETTE.keys()):
        col, name = PALETTE[key]
        rect = pygame.Rect(px, py, 36, 36)
        pygame.draw.rect(screen, col, rect)
        txt = FONT.render(str(key), True, (255,255,255))
        screen.blit(txt, (px+40, py+8))
        name_txt = FONT.render(name, True, (200,200,200))
        screen.blit(name_txt, (px+60, py+8))
        px += 200
    # selección actual
    sel_txt = FONT.render(f"Selected: {selected}", True, (255,255,0))
    screen.blit(sel_txt, (MARGIN, H-32))
    help_lines = [
        "Left click: paint    Right click: erase    Middle click: sample",
        "Keys 0-9: select tile   S: save   L: load   C: clear   +/-: tile size"
    ]
    for i, line in enumerate(help_lines):
        screen.blit(FONT.render(line, True, (200,200,200)), (MARGIN+200, H-34 - (i*18)))

def pos_to_cell(mx, my):
    if mx < MARGIN or my < MARGIN or mx >= MARGIN + COLS*TILE or my >= MARGIN + ROWS*TILE:
        return None
    cx = (mx - MARGIN) // TILE
    cy = (my - MARGIN) // TILE
    return int(cx), int(cy)

running = True
while running:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mx, my = ev.pos
            cell = pos_to_cell(mx, my)
            if ev.button == 1 and cell:
                x,y = cell
                grid[y][x] = selected
            elif ev.button == 3 and cell:
                x,y = cell
                grid[y][x] = 0
            elif ev.button == 2 and cell:
                x,y = cell
                selected = grid[y][x]
            elif ev.button == 4:  # wheel up
                TILE = min(64, TILE + 2)
                W = COLS * TILE + MARGIN * 2
                H = ROWS * TILE + 140
                screen = pygame.display.set_mode((W, H))
            elif ev.button == 5:  # wheel down
                TILE = max(8, TILE - 2)
                W = COLS * TILE + MARGIN * 2
                H = ROWS * TILE + 140
                screen = pygame.display.set_mode((W, H))
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_s:
                save_to_file(SAVE_FILE, grid)
            elif ev.key == pygame.K_l:
                loaded = load_from_file(SAVE_FILE)
                if loaded:
                    grid = loaded
            elif ev.key == pygame.K_c:
                grid = make_empty(COLS, ROWS, border_walls=False)
            elif ev.key in (pygame.K_PLUS, pygame.K_EQUALS):
                TILE = min(64, TILE + 2)
                W = COLS * TILE + MARGIN * 2
                H = ROWS * TILE + 140
                screen = pygame.display.set_mode((W, H))
            elif ev.key == pygame.K_MINUS:
                TILE = max(8, TILE - 2)
                W = COLS * TILE + MARGIN * 2
                H = ROWS * TILE + 140
                screen = pygame.display.set_mode((W, H))
            elif pygame.K_0 <= ev.key <= pygame.K_9:
                selected = ev.key - pygame.K_0
            elif ev.key == pygame.K_ESCAPE:
                running = False

    draw_ui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()