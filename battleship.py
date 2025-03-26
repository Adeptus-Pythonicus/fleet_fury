import asyncio
import json

import pygame as pg

import client

# Initialize pygame
pg.init()

# Window size
WIDTH, HEIGHT = 1600, 900
ROWS, COLS = 10, 10
CELL_SIZE = WIDTH * 0.03
PADDING = 70

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
DARK_BLUE = (40, 75, 99)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
BROWN = (111, 78, 55)
DARK_BROWN = (148, 137, 121)
PLATINUM = (217, 217, 217)

# Images
battleship_img = pg.image.load("./battleship.png")

# Create Window
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("BATTLESHIP")

# Grids stored
grid1 = [[False for _ in range(COLS)] for _ in range(ROWS)]
grid2 = [[False for _ in range(COLS)] for _ in range(ROWS)]

selected_tiles_player = []
selected_tiles_opponent = []

boats = []

big_font = pg.font.Font("times.ttf", 30)
medium_font = pg.font.Font("times.ttf", 25)
small_font = pg.font.Font("times.ttf", 20)

player_name = asyncio.Queue()
ship_placement = asyncio.Queue()
target_coords = asyncio.Queue()
player_turn = asyncio.Queue()
hit_coords = asyncio.Queue()

turn = False
player_title = ""
enemy_title = ""

boat_coords = {}


def create_boats():
    boat_y = GRID_Y_OFFSET + CELL_SIZE * 1.5
    for _ in range(5):
        boat = pg.Rect(GRID1_X_OFFSET - CELL_SIZE * 5, boat_y, CELL_SIZE * 3, CELL_SIZE)
        boats.append(boat)
        boat_coords.setdefault(boats.index(boat), None)
        boat_y += CELL_SIZE * 1.5


def reset_boat(boat: pg.Rect):
    boat_index = boats.index(boat)
    boat.width = int(CELL_SIZE * 3)
    boat.height = int(CELL_SIZE)
    boat.update(
        GRID1_X_OFFSET - CELL_SIZE * 5,
        (GRID_Y_OFFSET + ((boat_index + 1) * (CELL_SIZE * 1.5))),
        boat.width,
        boat.height,
    )
    boat_coords[boats.index(boat)] = None


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
    num_y = GRID_Y_OFFSET + CELL_SIZE // 2
    for i in range(10):
        draw_text(str(i), medium_font, DARK_BLUE, x_offset - CELL_SIZE // 2, num_y)
        num_y += CELL_SIZE
    num_x = x_offset + CELL_SIZE // 2
    for i in range(10):
        draw_text(str(i), medium_font, DARK_BLUE, num_x, GRID_Y_OFFSET - CELL_SIZE // 2)
        num_x += CELL_SIZE


def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))


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
    global boat_coords
    orientation = None

    if (
        is_over_player_grid(boat.topleft)
        and is_over_player_grid(boat.bottomright)
        and is_over_player_grid(boat.center)
    ):
        x, y = boat.center

        grid_x = int((x - GRID1_X_OFFSET) // CELL_SIZE)
        grid_y = int((y - GRID_Y_OFFSET) // CELL_SIZE)

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

        if boat.height > boat.width:
            orientation = "v"
        else:
            orientation = "h"

        boat_coords[boats.index(boat)] = (grid_x, grid_y, orientation)
    else:
        reset_boat(boat)


async def welcome_screen():
    global player_title

    box_outer = pg.Rect(0, 0, WIDTH * 0.6, HEIGHT * 0.6)
    box_outer.center = (WIDTH // 2, HEIGHT // 2)

    box_inner = pg.Rect(0, 0, box_outer.width - 50, box_outer.height - 50)
    box_inner.center = (WIDTH // 2, HEIGHT // 2)

    _, y = box_inner.midtop

    input_box = pg.Rect(0, 0, 300, 60)
    input_box.center = (WIDTH // 2, int(y * 1.65))

    line = pg.Rect(0, 0, box_inner.width * 0.75, 1)
    line.center = (WIDTH // 2, int(y * 1.45))

    color_inactive = PLATINUM
    color_active = BLACK
    color = color_inactive
    active = False

    background_img = pg.image.load("ocean-waves-aerial-view.jpg")
    background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))

    running = True
    while running:
        screen.blit(background_img, (0, 0))
        pg.draw.rect(screen, (3, 16, 24), box_outer, border_radius=5)
        pg.draw.rect(screen, (0, 67, 89), box_inner, border_radius=5)
        pg.draw.rect(screen, WHITE, line)
        draw_text(
            "WELCOME TO FLEET FURY",
            big_font,
            WHITE,
            (WIDTH) // 2,
            y * 1.2,
        )
        draw_text("Enter a nickname to begin", small_font, GRAY, (WIDTH // 2), y * 1.35)

        # draw_text("RULES \n rule 1", big_font, WHITE, (WIDTH - 1100), (HEIGHT - 700))

        pg.draw.rect(screen, color, input_box, 2, border_radius=10)
        txt_surface = big_font.render(player_title, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        if player_title.strip():
                            await player_name.put(player_title)
                            running = False
                    elif event.key == pg.K_BACKSPACE:
                        player_title = player_title[:-1]
                    elif len(player_title) < 15:
                        player_title += event.unicode

        await asyncio.sleep(0)


# TODO: Get enemy name to display
async def boat_phase():
    global enemy_title
    active_boat = None

    while True:
        screen.fill(LIGHT_BLUE)

        draw_grid(grid1, GRID1_X_OFFSET)
        draw_grid(grid2, GRID2_X_OFFSET)

        draw_text(
            player_title,
            big_font,
            BLACK,
            GRID1_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        draw_text(
            enemy_title,
            big_font,
            BLACK,
            GRID2_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        for boat in boats:
            pg.draw.rect(screen, BROWN, boat, border_radius=10)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
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
                    print(boat_coords)
            if event.type == pg.MOUSEMOTION:
                if active_boat is not None:
                    boats[active_boat].move_ip(event.rel)
            if event.type == pg.QUIT:
                pg.quit()

        if None not in boat_coords.values():
            final_boat_coords = []
            for v in boat_coords.values():
                final_boat_coords.append(v)
            await ship_placement.put(json.dumps(final_boat_coords))
            return

        await asyncio.sleep(0)


# TODO: fix hp bar and figure out how to better diplay hit marks from the enemy
async def send_grenade_to_your_enemy_boat_phase():
    global turn
    global enemy_title

    while True:
        screen.fill(LIGHT_BLUE)

        draw_grid(grid1, GRID1_X_OFFSET)
        draw_grid(grid2, GRID2_X_OFFSET)

        draw_text(
            player_title,
            big_font,
            BLACK,
            GRID1_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        draw_text(
            enemy_title,
            big_font,
            BLACK,
            GRID2_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        for boat in boats:
            pg.draw.rect(screen, BROWN, boat, border_radius=10)

        pg.display.flip()

        if not turn:
            try:
                turn_message = await asyncio.wait_for(player_turn.get(), 0.1)
                if turn_message == "Your turn":
                    turn = True
                hit = await asyncio.wait_for(hit_coords.get(), 0.1)
                print(hit)
                hit = json.loads(hit)
                x = hit[0]
                y = hit[1]
                grid1[x][y] = True
            except asyncio.TimeoutError:
                pass

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if turn:
                    await select_tile(
                        grid2, GRID2_X_OFFSET, event.pos, selected_tiles_opponent
                    )

            if event.type == pg.QUIT:
                return

        await asyncio.sleep(0)


async def battleship():
    global turn
    global enemy_title

    create_boats()

    await welcome_screen()

    enemy_title = await player_name.get()

    await boat_phase()
    await send_grenade_to_your_enemy_boat_phase()

    pg.quit()


async def main():
    battleship_task = asyncio.create_task(battleship())
    server_connection_task = asyncio.create_task(
        client.handle_server_connection(
            player_name,
            target_coords,
            ship_placement,
            player_turn,
            hit_coords,
        )
    )

    await asyncio.gather(battleship_task, server_connection_task)


asyncio.run(main())
