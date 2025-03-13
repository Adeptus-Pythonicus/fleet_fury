import pygame as pg
import websockets
import asyncio
import json

# Initialize pygame
pg.init()

# Window size
WIDTH, HEIGHT = 1600, 900
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH * 0.03
PADDING = 50

# A single player's grid width
GRID_WIDTH = COLS * CELL_SIZE

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
    running = True
    while running:
        screen.fill(WHITE)

        draw_grid(grid1, GRID1_X, OFFSET_Y)
        draw_grid(grid2, GRID2_X, OFFSET_Y)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                await select_tile(
                    grid2, GRID2_X, OFFSET_Y, event.pos, selected_tiles_opponent
                )
            if event.type == pg.QUIT:
                running = False

        await asyncio.sleep(0)

    pg.quit()


async def main():
    battleship_task = asyncio.create_task(battleship())
    websocket_client_task = asyncio.create_task(websocket_client())

    await asyncio.gather(battleship_task, websocket_client_task)


asyncio.run(main())
