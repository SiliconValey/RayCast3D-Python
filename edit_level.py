import pygame
import sys
import os

pygame.init()

# --- Configuración general ---
COLS, ROWS = 24, 20
TILE = 28
MARGIN = 8
FONT = pygame.font.SysFont("Consolas", 16)
SAVE_FILE = "level.txt"
TEXTURE_PATH = "textures"

# --- Paleta por defecto ---
PALETTE = {
    0: ((30, 30, 30), "Empty"),
    1: ((200, 80, 80), "Wall"),
    2: ((120, 200, 120), "Type 2"),
    3: ((120, 160, 240), "Type 3"),
}

# --- Tamaños ---
SIDEBAR_WIDTH = 140
MENUBAR_HEIGHT = 28
W = COLS * TILE + MARGIN * 2 + SIDEBAR_WIDTH
H = ROWS * TILE + MARGIN * 2 + MENUBAR_HEIGHT + 100

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Level Editor - Raycasting3D")
clock = pygame.time.Clock()

# --- Cache de texturas cargadas ---
texture_cache = {}

def get_texture(name):
    """Carga la textura si no está en cache."""
    if name not in texture_cache:
        path = os.path.join(TEXTURE_PATH, name)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (TILE, TILE))
            texture_cache[name] = img
        else:
            texture_cache[name] = None
    return texture_cache[name]

# --- Utilidades ---
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

def load_from_file(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        data = eval(txt, {})
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

# --- Menú superior ---
class MenuBar:
    def __init__(self):
        self.items = ["Nuevo", "Abrir", "Guardar", "Salir"]
        self.rect = pygame.Rect(0, 0, W, MENUBAR_HEIGHT)

    def draw(self, surf):
        pygame.draw.rect(surf, (60, 60, 60), self.rect)
        x = 10
        for item in self.items:
            text = FONT.render(item, True, (255, 255, 255))
            surf.blit(text, (x, 5))
            x += text.get_width() + 40

    def click(self, pos, grid):
        x = 10
        for item in self.items:
            rect = pygame.Rect(x, 0, FONT.size(item)[0] + 20, MENUBAR_HEIGHT)
            if rect.collidepoint(pos):
                if item == "Nuevo":
                    return make_empty(COLS, ROWS)
                elif item == "Abrir":
                    loaded = load_from_file(SAVE_FILE)
                    if loaded: return loaded
                elif item == "Guardar":
                    save_to_file(SAVE_FILE, grid)
                elif item == "Salir":
                    pygame.quit()
                    sys.exit()
            x += FONT.size(item)[0] + 40
        return grid

# --- Panel de texturas ---
class TexturePanel:
    def __init__(self, path):
        self.path = path
        self.textures = []
        self.load_textures()
        self.selected = None

    def load_textures(self):
        self.textures.clear()
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        for file in os.listdir(self.path):
            if file.lower().endswith((".png", ".jpg", ".bmp")):
                img = pygame.image.load(os.path.join(self.path, file)).convert_alpha()
                img = pygame.transform.scale(img, (48, 48))
                self.textures.append((file, img))

    def draw(self, surf):
        x = 8
        y = MENUBAR_HEIGHT + 8
        pygame.draw.rect(surf, (30, 30, 30), (0, MENUBAR_HEIGHT, SIDEBAR_WIDTH, H))
        for i, (name, img) in enumerate(self.textures):
            rect = pygame.Rect(x, y, 48, 48)
            surf.blit(img, rect)
            if self.selected == i:
                pygame.draw.rect(surf, (255, 255, 0), rect, 2)
            y += 60

    def click(self, pos):
        x = 8
        y = MENUBAR_HEIGHT + 8
        for i, (name, img) in enumerate(self.textures):
            rect = pygame.Rect(x, y, 48, 48)
            if rect.collidepoint(pos):
                self.selected = i
                return name, img
            y += 60
        return None, None

# --- Inicialización ---
menu = MenuBar()
textures = TexturePanel(TEXTURE_PATH)
grid = load_from_file(SAVE_FILE) or make_empty(COLS, ROWS)
selected_tile = 1
dragging_texture = None
drag_texture_name = None

# --- Funciones de dibujo ---
def draw_ui(mouse_pos=None):
    screen.fill((40, 40, 40))
    menu.draw(screen)
    textures.draw(screen)

    offset_x = SIDEBAR_WIDTH + MARGIN
    offset_y = MENUBAR_HEIGHT + MARGIN

    for y in range(ROWS):
        for x in range(COLS):
            cell = grid[y][x]
            rect = pygame.Rect(offset_x + x*TILE, offset_y + y*TILE, TILE-1, TILE-1)

            if isinstance(cell, str):  # nombre de textura
                tex = get_texture(cell)
                if tex:
                    screen.blit(tex, rect)
                else:
                    pygame.draw.rect(screen, (100, 100, 100), rect)
            else:
                color = PALETTE.get(cell, ((80, 80, 80), ""))[0]
                pygame.draw.rect(screen, color, rect)

    # Dibuja textura arrastrada
    if dragging_texture and mouse_pos:
        img = dragging_texture
        rect = img.get_rect(center=mouse_pos)
        screen.blit(img, rect)

    sel_txt = FONT.render(f"Selected: {selected_tile}", True, (255, 255, 0))
    screen.blit(sel_txt, (SIDEBAR_WIDTH + 10, H - 30))

def pos_to_cell(mx, my):
    offset_x = SIDEBAR_WIDTH + MARGIN
    offset_y = MENUBAR_HEIGHT + MARGIN
    if mx < offset_x or my < offset_y:
        return None
    cx = (mx - offset_x) // TILE
    cy = (my - offset_y) // TILE
    if 0 <= cx < COLS and 0 <= cy < ROWS:
        return int(cx), int(cy)
    return None

# --- Bucle principal ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if ev.pos[1] < MENUBAR_HEIGHT:
                grid = menu.click(ev.pos, grid)
            elif ev.pos[0] < SIDEBAR_WIDTH:
                tex_name, tex_img = textures.click(ev.pos)
                if tex_img:
                    dragging_texture = tex_img
                    drag_texture_name = tex_name
            else:
                cell = pos_to_cell(*ev.pos)
                if cell and not dragging_texture:
                    x, y = cell
                    grid[y][x] = selected_tile

        elif ev.type == pygame.MOUSEBUTTONUP:
            if dragging_texture:
                cell = pos_to_cell(*ev.pos)
                if cell:
                    x, y = cell
                    grid[y][x] = drag_texture_name  # guarda el nombre de archivo
                    print(f"Textura '{drag_texture_name}' colocada en {cell}")
                dragging_texture = None
                drag_texture_name = None

        elif ev.type == pygame.KEYDOWN:
            if pygame.K_0 <= ev.key <= pygame.K_9:
                selected_tile = ev.key - pygame.K_0
            elif ev.key == pygame.K_ESCAPE:
                running = False

    draw_ui(mouse_pos)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


