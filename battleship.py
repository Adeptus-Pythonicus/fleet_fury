import asyncio
import json

import pygame as pg
import websockets

import client

# Initialize pygame
pg.init()

# Window size
WIDTH, HEIGHT = 1600, 1000
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH * 0.03
PADDING = 50

# A single player's grid width
GRID_WIDTH = COLS * CELL_SIZE
GRID_HEIGHT = GRID_WIDTH

# offset values of the grid from the screen to calculate the cell index
GRID1_X_OFFSET = (WIDTH - (GRID_WIDTH * 2 + PADDING)) // 2
GRID2_X_OFFSET = GRID1_X_OFFSET + GRID_WIDTH + PADDING
GRID_Y_OFFSET = (HEIGHT - (ROWS * CELL_SIZE)) // 2

# Colors
WHITE = (255, 255, 255)
LIGHT_BLUE = (218, 237, 244)
DARK_BLUE = (25, 69, 83)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BROWN = (111, 78, 55)

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

boats = []

hp = pg.Rect(
    GRID2_X_OFFSET + CELL_SIZE * 5, GRID_Y_OFFSET, CELL_SIZE * 1, CELL_SIZE * 6
)

text_font = pg.font.Font(None, 30)

target_coords = asyncio.Queue()
player_turn = asyncio.Queue()
turn = False


def create_boats():
    boat_y = GRID_Y_OFFSET
    for _ in range(5):
        boat = pg.Rect(GRID1_X_OFFSET - CELL_SIZE * 5, boat_y, CELL_SIZE * 3, CELL_SIZE)
        boats.append(boat)
        boat_y += CELL_SIZE * 1.5


def reset_boat(boat: pg.Rect):
    boat_index = boats.index(boat)
    boat.width = CELL_SIZE * 3
    boat.height = CELL_SIZE
    boat.update(
        GRID1_X_OFFSET - CELL_SIZE * 5,
        (GRID_Y_OFFSET + (boat_index * (CELL_SIZE * 1.5))),
        boat.width,
        boat.height,
    )


def draw_grid(grid, x_offset):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pg.Rect(
                x_offset + col * CELL_SIZE,
                GRID_Y_OFFSET + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            color = BLUE if grid[row][col] else GRAY
            pg.draw.rect(screen, color, rect)
            pg.draw.rect(screen, WHITE, rect, 1)
    num_y = GRID_Y_OFFSET + CELL_SIZE * 0.4
    for i in range(10):
        draw_text(str(i), text_font, DARK_BLUE, x_offset - CELL_SIZE * 0.5, num_y)
        num_y += CELL_SIZE
    num_x = x_offset + CELL_SIZE * 0.4
    for i in range(10):
        draw_text(str(i), text_font, DARK_BLUE, num_x, GRID_Y_OFFSET - CELL_SIZE * 0.5)
        num_x += CELL_SIZE


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def is_over_player_grid(pos):
    x, y = pos
    wiggle_room = CELL_SIZE * 0.48

    if (
        x > GRID1_X_OFFSET - wiggle_room
        and x < GRID1_X_OFFSET + GRID_WIDTH + wiggle_room
    ) and (
        y > GRID_Y_OFFSET - wiggle_room
        and y < GRID_Y_OFFSET + GRID_HEIGHT + wiggle_room
    ):
        return True

    return False


async def select_tile(grid, x_offset, pos, selected_tiles):
    x, y = pos

    # calculate the cell index
    col = int((x - x_offset) // CELL_SIZE)
    row = int((y - GRID_Y_OFFSET) // CELL_SIZE)

    if 0 <= col < COLS and 0 <= row < ROWS:
        if not grid[row][col]:
            grid[row][col] = True
            tile_coord = (row, col)

            selected_tiles.append(tile_coord)
            await target_coords.put(json.dumps(tile_coord))

            global turn
            turn = False


# to snap blocks into place
def place_boat(boat: pg.Rect):
    if (
        is_over_player_grid(boat.topleft)
        and is_over_player_grid(boat.bottomright)
        and is_over_player_grid(boat.center)
    ):
        x, y = boat.center

        # TODO: need to send this using queue
        # ship coords
        grid_x = (x - GRID1_X_OFFSET) // CELL_SIZE
        grid_y = (y - GRID_Y_OFFSET) // CELL_SIZE

        # calculate the cell to be placed on the screen
        col = ((x - GRID1_X_OFFSET) // CELL_SIZE) * CELL_SIZE + (
            GRID1_X_OFFSET + (CELL_SIZE // 2)
        )
        row = ((y - GRID_Y_OFFSET) // CELL_SIZE) * CELL_SIZE + (
            GRID_Y_OFFSET + (CELL_SIZE // 2)
        )

        temp_boat = boat.copy()
        temp_boat.center = (int(col), int(row))

        for other_boat in boats:
            if other_boat != boat and temp_boat.colliderect(other_boat):
                reset_boat(boat)
                return

        boat.center = (int(col), int(row))
    else:
        reset_boat(boat)


# TODO: set ship phase and game phase, fix hp bar, get orientation of boat
async def battleship():
    global turn
    active_boat = None
    create_boats()
    running = True

    turn_message = await player_turn.get()
    if turn_message == "Your turn":
        turn = True
    else:
        turn = False

    while running:
        screen.fill(LIGHT_BLUE)

        draw_grid(grid1, GRID1_X_OFFSET)
        draw_grid(grid2, GRID2_X_OFFSET)

        for boat in boats:
            pg.draw.rect(screen, BROWN, boat, border_radius=10)

        # pg.draw.rect(screen, BROWN, hp)

        pg.display.flip()

        if not turn:
            try:
                turn_message = await asyncio.wait_for(player_turn.get(), 0.1)
                if turn_message == "Your turn":
                    turn = True
            except asyncio.TimeoutError:
                pass

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if turn:
                    await select_tile(
                        grid2, GRID2_X_OFFSET, event.pos, selected_tiles_opponent
                    )
                if event.button == 1:
                    for num, boat in enumerate(boats):
                        if boat.collidepoint(event.pos):
                            active_boat = num
                elif event.button == 3 and active_boat is not None:
                    boats[active_boat].width, boats[active_boat].height = (
                        boats[active_boat].height,
                        boats[active_boat].width,
                    )

            if event.type == pg.MOUSEBUTTONUP:
                if event.button == 1 and active_boat is not None:
                    place_boat(boats[active_boat])
                    active_boat = None

            if event.type == pg.MOUSEMOTION:
                if active_boat != None:
                    boats[active_boat].move_ip(event.rel)

            if event.type == pg.QUIT:
                running = False

        await asyncio.sleep(0.01)

    pg.quit()


async def main():
    battleship_task = asyncio.create_task(battleship())
    server_connection_task = asyncio.create_task(
        client.handle_server_connection(target_coords, 5, player_turn)
    )

    await asyncio.gather(battleship_task, server_connection_task)


asyncio.run(main())
