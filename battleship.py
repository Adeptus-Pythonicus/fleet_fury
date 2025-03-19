import asyncio
import json

import pygame as pg
import websockets

# Initialize pygame
pg.init()

# Window size
WIDTH, HEIGHT = 1600, 900
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH * 0.03
PADDING = 50

# A single player's grid width
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = GRID_WIDTH

TOTAL_WIDTH = GRID_WIDTH * 2 + PADDING

# offset value to calculate the cell index
GRID1_X = (WIDTH - TOTAL_WIDTH) // 2
GRID2_X = GRID1_X + GRID_WIDTH + PADDING
OFFSET_Y = (HEIGHT - (ROWS * CELL_SIZE)) // 2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Images
battleship_img = pg.image.load("./battleship.png")

# Create Window
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
pg.display.set_caption("BATTLESHIP")

# Grids stored
grid1 = [[False for _ in range(COLS)] for _ in range(ROWS)]
grid2 = [[False for _ in range(COLS)] for _ in range(ROWS)]


boats = []
boat_y = OFFSET_Y

for i in range(5):
    boat = pg.Rect(GRID1_X - CELL_SIZE * 3, boat_y, CELL_SIZE * 3, CELL_SIZE)
    boats.append(boat)
    boat_y += CELL_SIZE * 1.5


selected_tiles_player = []
selected_tiles_opponent = []

target_coords = asyncio.Queue()


def draw_grid(grid, offset_x, offset_y):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pg.Rect(
                offset_x + col * CELL_SIZE,
                offset_y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            color = BLUE if grid[row][col] else GRAY
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, WHITE, rect, 1)


def is_over_grid(pos):
    x, y = pos

    if (x > GRID1_X and x < GRID1_X + TOTAL_WIDTH) and (
        y > OFFSET_Y and y < OFFSET_Y + GRID_HEIGHT
    ):
        return True

    return False


async def select_tile(grid, offset_x, offset_y, pos, selected_tiles):
    x, y = pos
    col = int((x - offset_x) // CELL_SIZE)
    row = int((y - offset_y) // CELL_SIZE)

    if 0 <= col < COLS and 0 <= row < ROWS:
        if not grid[row][col]:
            grid[row][col] = True
            tile_coord = (row, col)

            selected_tiles.append(tile_coord)
            await target_coords.put(tile_coord)

            return True

    return False


# to snap blocks into place
# TODO: name it better
def check_placement(grid):
    pass


async def websocket_client():
    url = "ws://127.0.0.1:5050"

    async with websockets.connect(url) as ws:
        await ws.send("Pygame websocket connected!")

        while True:
            print("Waiting for coords")
            hit_coords = await target_coords.get()
            print("Sending coords")
            await ws.send(json.dumps(hit_coords))
            msg = await ws.recv()
            print(msg)

            if msg == "close":
                break


async def battleship():
    active_boat = None
    running = True
    while running:
        screen.fill(WHITE)

        draw_grid(grid1, GRID1_X, OFFSET_Y)
        draw_grid(grid2, GRID2_X, OFFSET_Y)

        for boat in boats:
            pg.draw.rect(screen, "BLACK", boat)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                await select_tile(
                    grid2, GRID2_X, OFFSET_Y, event.pos, selected_tiles_opponent
                )
                if event.button == 1:
                    for num, boat in enumerate(boats):
                        if boat.collidepoint(event.pos):
                            active_boat = num

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    active_boat = None

            if event.type == pg.MOUSEMOTION:
                if active_boat != None:
                    boats[active_boat].move_ip(event.rel)

            if event.type == pg.QUIT:
                running = False

        await asyncio.sleep(0)

    pg.quit()


async def main():
    battleship_task = asyncio.create_task(battleship())
    websocket_client_task = asyncio.create_task(websocket_client())

    await asyncio.gather(battleship_task, websocket_client_task)


asyncio.run(main())
