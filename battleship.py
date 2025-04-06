import asyncio
import json

import pygame as pg

import client
from weather import WindModifier

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
GRAY = (169, 169, 169)
BROWN = (111, 78, 55)
DARK_BROWN = (148, 137, 121)
PLATINUM = (217, 217, 217)
VERY_DARK_BLUE = (3, 16, 24)
DARK_TEAL = (22, 44, 61)
MEDIUM_TEAL = (1, 104, 138)
OUTERBOX = (7, 26, 52)
INNERBOX = (35, 60, 93)
RED = (52, 7, 7)
GREEN = (12, 82, 7)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)

# Images
battleship_img = pg.image.load("./battleship.png")

# Create Window
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("BATTLESHIP")

boat_img = pg.image.load("./ship_medium_body.png")
boat_img = pg.transform.scale(boat_img, (CELL_SIZE * 3, CELL_SIZE))

boat_img_array = [boat_img for _ in range(6)]

water_img = pg.image.load("./water_tile.png")
water_img = pg.transform.scale(boat_img, (CELL_SIZE * 3, CELL_SIZE))

water_tile = pg.image.load("./water_tile.png")
water_tile = pg.transform.scale(water_tile, (CELL_SIZE, CELL_SIZE))

hit_mark = pg.image.load("./hit.png")
hit_mark = pg.transform.scale(hit_mark, (CELL_SIZE, CELL_SIZE))

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
winner = asyncio.Queue()

turn = False
player_title = ""
enemy_title = ""
winner_message = ""
is_winner = False
is_loser = False

boat_coords = {}

weather_data = WindModifier()
weather_data.get_weather_data()
weather_data.determine_shift([0, 0])

clock = pg.time.Clock()


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
            if grid[row][col]:
                screen.blit(hit_mark, rect)
    num_y = GRID_Y_OFFSET + CELL_SIZE // 2
    for i in range(10):
        draw_text(str(i), medium_font, WHITE, x_offset - CELL_SIZE // 2, num_y)
        num_y += CELL_SIZE
    num_x = x_offset + CELL_SIZE // 2
    for i in range(10):
        draw_text(str(i), medium_font, WHITE, num_x, GRID_Y_OFFSET - CELL_SIZE // 2)
        num_x += CELL_SIZE


def draw_water_overlay(x_offset):
    for row in range(ROWS):
        for col in range(COLS):
            tile_rect = pg.Rect(
                x_offset + col * CELL_SIZE,
                GRID_Y_OFFSET + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            screen.blit(water_tile, tile_rect)
            pg.draw.rect(screen, VERY_DARK_BLUE, tile_rect, 1)


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
    row, col = weather_data.determine_shift([row, col])

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

        grid_col = int((x - GRID1_X_OFFSET) // CELL_SIZE)
        grid_row = int((y - GRID_Y_OFFSET) // CELL_SIZE)

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

        boat_coords[boats.index(boat)] = (grid_row, grid_col, orientation)
    else:
        reset_boat(boat)


async def welcome_screen():
    global player_title

    box_outer = pg.Rect(0, 0, WIDTH * 0.6, HEIGHT * 0.6)
    box_outer.center = (WIDTH // 2, HEIGHT // 2)

    box_inner = pg.Rect(0, 0, box_outer.width - 50, box_outer.height - 50)
    box_inner.center = (WIDTH // 2, HEIGHT // 2)

    _, y = box_inner.midtop

    input_box = pg.Rect(0, 0, 250, 50)
    input_box.center = (WIDTH // 2, int(y * 1.65))
    start_button = pg.Rect(0, 0, 180, 60)
    start_button.center = (WIDTH // 2, int(y * 3.125))

    line = pg.Rect(0, 0, box_inner.width * 0.75, 1)
    line.center = (WIDTH // 2, int(y * 1.45))

    color_inactive = OUTERBOX
    color_active = WHITE
    color = color_inactive
    active = False

    background_img = pg.image.load("sea_storm1.jpg")
    background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))

    logo_img = pg.image.load("light_logo.png")
    logo_img = pg.transform.scale(logo_img, (123, 103))

    running = True
    while running:
        screen.blit(background_img, (0, 0))
        screen.blit(logo_img, (0, 0))
        pg.draw.rect(screen, OUTERBOX, box_outer, border_radius=5)
        pg.draw.rect(screen, INNERBOX, box_inner, border_radius=5)
        pg.draw.rect(screen, WHITE, line)

        draw_text(
            "WELCOME TO FLEET FURY",
            big_font,
            WHITE,
            (WIDTH) // 2,
            y * 1.2,
        )
        draw_text(
            "Enter a nickname to begin", small_font, PLATINUM, (WIDTH // 2), y * 1.35
        )

        draw_text("How to play:", big_font, WHITE, (WIDTH // 2), y * 2)
        draw_text(
            "Place your boats - Use left click to drag them onto the board and right click to rotate",
            small_font,
            WHITE,
            (WIDTH // 2) - 45,
            y * 2.2,
        )
        draw_text(
            "Take turns shooting - Pick a spot to fire at on your opponent's grid",
            small_font,
            WHITE,
            (WIDTH // 2) - 120,
            y * 2.35,
        )
        draw_text(
            "Wind affects your shots - Wind in Nanaimo might push your shot in a different direction!",
            small_font,
            WHITE,
            (WIDTH // 2) - 25,
            y * 2.5,
        )
        draw_text(
            "Goal: sink all of your opponent's ships before they sink yours!",
            medium_font,
            WHITE,
            (WIDTH // 2),
            y * 2.80,
        )

        display_text = player_title + "|" if active else player_title

        pg.draw.rect(screen, color, input_box, 2, border_radius=10)
        txt_surface = big_font.render(display_text, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        # Draw start button
        pg.draw.rect(screen, OUTERBOX, start_button, border_radius=10)
        draw_text("START", big_font, WHITE, start_button.centerx, start_button.centery)

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
                if start_button.collidepoint(event.pos):
                    if player_title.strip():
                        await player_name.put(player_title)
                        running = False

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

        clock.tick(60)

        await asyncio.sleep(0)


# TODO: Get enemy name to display
async def boat_phase():
    global enemy_title
    active_boat = None

    background_img = pg.image.load("sea_storm.jpg")
    background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))

    click_img = pg.image.load("right-click.png")
    click_img = pg.transform.scale(click_img, (60, 60))

    while True:
        screen.blit(background_img, (0, 0))

        draw_grid(grid1, GRID1_X_OFFSET)
        draw_grid(grid2, GRID2_X_OFFSET)
        draw_water_overlay(GRID1_X_OFFSET)
        draw_water_overlay(GRID2_X_OFFSET)

        # screen.blit(
        #     click_img,
        #     (
        #         WIDTH - GRID1_X_OFFSET + 75 - click_img.get_width() // 2,
        #         HEIGHT // 2 - click_img.get_height() // 2,
        #     ),
        # )
        # draw_text(
        #     "Rotate",
        #     big_font,
        #     WHITE,
        #     WIDTH - GRID1_X_OFFSET // 2,
        #     HEIGHT // 2,
        # )

        draw_text(
            player_title,
            big_font,
            WHITE,
            GRID1_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        draw_text(
            enemy_title,
            big_font,
            WHITE,
            GRID2_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        for index, boat in enumerate(boats):
            screen.blit(boat_img_array[index], boat)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for num, boat in enumerate(boats):
                        if boat.collidepoint(event.pos):
                            active_boat = num
                elif event.button == 3 and active_boat is not None:
                    boat_img_array[active_boat] = pg.transform.rotate(
                        boat_img_array[active_boat], 90
                    )
                    boats[active_boat].height, boats[active_boat].width = (
                        boats[active_boat].width,
                        boats[active_boat].height,
                    )
                    # rotate
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

        clock.tick(60)

        await asyncio.sleep(0)


async def send_grenade_to_your_enemy_boat_phase():
    global turn
    global enemy_title
    global is_winner
    global is_loser

    background_img = pg.image.load("sea_storm.jpg")
    background_img = pg.transform.scale(background_img, (WIDTH, HEIGHT))

    while True:
        screen.blit(background_img, (0, 0))
        hp_value = 4
        hp_rect = pg.Rect(
            GRID1_X_OFFSET,
            GRID_Y_OFFSET + (CELL_SIZE * 10.1),
            CELL_SIZE * (0.6666 * hp_value),
            CELL_SIZE * 0.3,
        )

        draw_text(
            str("Wind direction: " + weather_data.string_direction),
            small_font,
            WHITE,
            (WIDTH - GRID1_X_OFFSET // 2) - 32,
            GRID_Y_OFFSET + 30,
        )

        draw_text(
            ("Wind speed: " + str(weather_data.wind_values[0]) + " km/h"),
            small_font,
            WHITE,
            (WIDTH - GRID1_X_OFFSET // 2) - 30,
            GRID_Y_OFFSET + 10,
        )

        draw_water_overlay(GRID1_X_OFFSET)
        draw_water_overlay(GRID2_X_OFFSET)

        draw_text(
            player_title,
            big_font,
            WHITE,
            GRID1_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        draw_text(
            enemy_title,
            big_font,
            WHITE,
            GRID2_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        for index, boat in enumerate(boats):
            screen.blit(boat_img_array[index], boat)

        draw_grid(grid1, GRID1_X_OFFSET)
        draw_grid(grid2, GRID2_X_OFFSET)

        if hp_value > 10:
            pg.draw.rect(screen, GREEN, hp_rect, border_radius=3)
        elif hp_value < 10 and hp_value > 6:
            pg.draw.rect(screen, YELLOW, hp_rect, border_radius=3)
        elif hp_value < 7 and hp_value > 3:
            pg.draw.rect(screen, ORANGE, hp_rect, border_radius=3)
        else:
            pg.draw.rect(screen, RED, hp_rect, border_radius=3)

        if is_winner:
            draw_text("WINNER!", big_font, WHITE, WIDTH // 2, HEIGHT - 100)
        if is_loser:
            draw_text("LOSER!", big_font, WHITE, WIDTH // 2, HEIGHT - 100)

        pg.display.flip()

        if not is_winner:
            try:
                winner_message = await asyncio.wait_for(winner.get(), 0.1)
                if winner_message == "Winner":
                    is_winner = True
                if winner_message == "Loser":
                    is_loser = True
            except asyncio.TimeoutError:
                pass

        if not turn:
            try:
                turn_message = await asyncio.wait_for(player_turn.get(), 0.1)
                if turn_message == "Your turn":
                    turn = True
                hit = await asyncio.wait_for(hit_coords.get(), 0.1)
                row, col = list(json.loads(hit))
                grid1[row][col] = True
            except asyncio.TimeoutError:
                pass

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and not is_winner and not is_loser:
                if turn:
                    await select_tile(
                        grid2, GRID2_X_OFFSET, event.pos, selected_tiles_opponent
                    )

            if event.type == pg.QUIT:
                return

        clock.tick(60)

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
            winner,
        )
    )

    await asyncio.gather(battleship_task, server_connection_task)


asyncio.run(main())
