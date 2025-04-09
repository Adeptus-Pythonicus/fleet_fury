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
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PLATINUM = (217, 217, 217)
VERY_DARK_BLUE = (3, 16, 24)

# welcome screen box colors
OUTERBOX = (7, 26, 52)
INNERBOX = (35, 60, 93)

# hp bar colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 140, 0)

# Images
boat_img = pg.image.load("./assets/ship_medium_body.png")
boat_img = pg.transform.scale(boat_img, (CELL_SIZE * 3, CELL_SIZE))

water_tile = pg.image.load("./assets/water_tile.png")
water_tile = pg.transform.scale(water_tile, (CELL_SIZE, CELL_SIZE))

hit_mark = pg.image.load("./assets/hit.png")
hit_mark = pg.transform.scale(hit_mark, (CELL_SIZE, CELL_SIZE))

miss_mark = pg.image.load("./assets/miss.png")
miss_mark = pg.transform.scale(miss_mark, (CELL_SIZE, CELL_SIZE))

bg_img_welcome = pg.image.load("./assets/sea_storm1.jpg")
bg_img_welcome = pg.transform.scale(bg_img_welcome, (WIDTH, HEIGHT))

bg_img_game = pg.image.load("./assets/sea_storm.jpg")
bg_img_game = pg.transform.scale(bg_img_game, (WIDTH, HEIGHT))

logo_img = pg.image.load("./assets/light_logo.png")
logo_img = pg.transform.scale(logo_img, (123, 103))

# fonts
font_big = pg.font.Font("./assets/times.ttf", 30)
font_medium = pg.font.Font("./assets/times.ttf", 25)
font_small = pg.font.Font("./assets/times.ttf", 20)

# Create Window
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("BATTLESHIP")

# Grids stored
grid_player = [[0 for _ in range(COLS)] for _ in range(ROWS)]
grid_opponent = [[0 for _ in range(COLS)] for _ in range(ROWS)]

# list of boat rectagles
boats = []

# boat images in an array matching the boats
boat_img_list = [boat_img for _ in range(6)]

# dict of boat's center coords and orientation
# keys are the indexes of rects in boats
boat_coords = {}

# Queues to share data between client and game
player_name = asyncio.Queue()
ship_list = asyncio.Queue()
player_turn = asyncio.Queue()
shot_coords = asyncio.Queue()
hit = asyncio.Queue()
hit_miss = asyncio.Queue()
health = asyncio.Queue()
winner = asyncio.Queue()

# Values update based on info from server
turn = False
is_winner = False
is_loser = False
player_title = ""
enemy_title = ""
winner_message = ""
hp_value = 15

# Initializing weather data
weather_data = WindModifier()
weather_data.get_weather_data()
weather_data.determine_shift([0, 0])

# Clock object for controlling fps
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
    boat_coords[boat_index] = None
    boat_img_list[boat_index] = boat_img


def draw_hit(grid, x_offset):
    for row in range(ROWS):
        for col in range(COLS):
            rect = pg.Rect(
                x_offset + col * CELL_SIZE,
                GRID_Y_OFFSET + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            # if the shot was a hit
            if grid[row][col] == 1:
                screen.blit(hit_mark, rect)
            # if the shot was a miss
            elif grid[row][col] == 2:
                screen.blit(miss_mark, rect)

    # drawing grid indexes
    num_y = GRID_Y_OFFSET + CELL_SIZE // 2
    for i in range(10):
        draw_text_center(str(i), font_medium, WHITE, x_offset - CELL_SIZE // 2, num_y)
        num_y += CELL_SIZE
    num_x = x_offset + CELL_SIZE // 2
    for i in range(10):
        draw_text_center(
            str(i), font_medium, WHITE, num_x, GRID_Y_OFFSET - CELL_SIZE // 2
        )
        num_x += CELL_SIZE


def draw_water_grid(x_offset):
    for row in range(ROWS):
        for col in range(COLS):
            tile_rect = pg.Rect(
                x_offset + col * CELL_SIZE,
                GRID_Y_OFFSET + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            screen.blit(water_tile, tile_rect)
            # grid lines
            pg.draw.rect(screen, VERY_DARK_BLUE, tile_rect, 1)


# draws text based of the center of the text box
def draw_text_center(text, font, color, x, y):
    text = font.render(text, True, color)
    screen.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))


# draws text based of left center of the text box
def draw_text_left(text, font, color, x, y):
    text = font.render(text, True, color)
    screen.blit(text, (x, y - text.get_height() // 2))


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


def is_over_opponent_grid(pos):
    x, y = pos

    if (x > GRID2_X_OFFSET and x < GRID2_X_OFFSET + GRID_WIDTH) and (
        y > GRID_Y_OFFSET and y < GRID_Y_OFFSET + GRID_HEIGHT
    ):
        return True

    return False


async def take_shot(grid, x_offset, pos):
    global turn

    if not is_over_opponent_grid(pos):
        return

    x, y = pos

    # calculate the cell index
    row = int((y - GRID_Y_OFFSET) // CELL_SIZE)
    col = int((x - x_offset) // CELL_SIZE)

    # adjust shot based on weather data
    row, col = weather_data.determine_shift([row, col])

    if 0 <= col < COLS and 0 <= row < ROWS:
        if grid[row][col] == 0:
            tile_coord = (row, col)
            # sending shot coords to the client to send to the server
            await shot_coords.put(json.dumps(tile_coord))

            # Get info about whether shot was hit or miss
            hit_miss_message = await hit_miss.get()

            # adjust cell value based of hit or miss
            if hit_miss_message == "hit":
                grid[row][col] = 1
            else:
                grid[row][col] = 2

            # auto set turn to false after the shot
            turn = False


def place_boat(boat: pg.Rect):
    global boat_coords

    orientation = None

    if (
        is_over_player_grid(boat.topleft)
        and is_over_player_grid(boat.bottomright)
        and is_over_player_grid(boat.center)
    ):
        x, y = boat.center

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

        # calculate actual index to be sent
        grid_col = int((x - GRID1_X_OFFSET) // CELL_SIZE)
        grid_row = int((y - GRID_Y_OFFSET) // CELL_SIZE)

        # get orientation
        if boat.height > boat.width:
            orientation = "v"
        else:
            orientation = "h"

        # add to the boat coords dict based on the key equal to index of boat
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

    running = True
    while running:
        screen.blit(bg_img_welcome, (0, 0))
        screen.blit(logo_img, (0, 0))

        pg.draw.rect(screen, OUTERBOX, box_outer, border_radius=5)
        pg.draw.rect(screen, INNERBOX, box_inner, border_radius=5)
        pg.draw.rect(screen, WHITE, line)

        draw_text_center(
            "WELCOME TO FLEET FURY",
            font_big,
            WHITE,
            (WIDTH) // 2,
            y * 1.2,
        )
        draw_text_center(
            "Enter a nickname to begin", font_small, PLATINUM, (WIDTH // 2), y * 1.35
        )
        draw_text_center("How to play:", font_big, WHITE, (WIDTH // 2), y * 2)
        draw_text_left(
            "Place your boats - Use left click to drag them onto the board and right click to rotate",
            font_small,
            WHITE,
            (WIDTH // 4) + 12,
            y * 2.2,
        )
        draw_text_left(
            "Take turns shooting - Pick a spot to fire at on your opponent's grid",
            font_small,
            WHITE,
            (WIDTH // 4) + 12,
            y * 2.35,
        )
        draw_text_left(
            "Wind affects your shots - Wind in Nanaimo might push your shot in a different direction!",
            font_small,
            WHITE,
            (WIDTH // 4) + 12,
            y * 2.5,
        )
        draw_text_center(
            "Goal: sink all of your opponent's ships before they sink yours!",
            font_medium,
            WHITE,
            (WIDTH // 2),
            y * 2.80,
        )

        display_text = player_title + "|" if active else player_title

        # Draw name input box
        pg.draw.rect(screen, color, input_box, 2, border_radius=10)
        txt_surface = font_big.render(display_text, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))

        # Draw start button
        pg.draw.rect(screen, OUTERBOX, start_button, border_radius=10)
        draw_text_center(
            "START", font_big, WHITE, start_button.centerx, start_button.centery
        )

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
                        draw_text_center(
                            "Waiting for other player to connect...",
                            font_small,
                            WHITE,
                            WIDTH // 2,
                            y * 1.85,
                        )
                        pg.display.flip()
                        await player_name.put(player_title)
                        running = False

            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_RETURN:
                        if player_title.strip():
                            draw_text_center(
                                "Waiting for other player to connect...",
                                font_small,
                                WHITE,
                                WIDTH // 2,
                                y * 1.85,
                            )
                            pg.display.flip()
                            await player_name.put(player_title)
                            running = False
                    elif event.key == pg.K_BACKSPACE:
                        player_title = player_title[:-1]
                    elif len(player_title) < 15:
                        player_title += event.unicode

        clock.tick(60)

        await asyncio.sleep(0)

async def boat_phase():
    global enemy_title

    active_boat = None

    while True:
        screen.blit(bg_img_game, (0, 0))

        # draw grids with water texture overlay
        draw_water_grid(GRID1_X_OFFSET)
        draw_water_grid(GRID2_X_OFFSET)

        # draws coordinates + hit
        # only need the coordinates for now
        draw_hit(grid_player, GRID1_X_OFFSET)
        draw_hit(grid_opponent, GRID2_X_OFFSET)

        # draw player and enemy names
        draw_text_center(
            player_title,
            font_big,
            WHITE,
            GRID1_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        draw_text_center(
            enemy_title,
            font_big,
            WHITE,
            GRID2_X_OFFSET + GRID_WIDTH // 2,
            GRID_Y_OFFSET // 2,
        )

        # drawing wind info on right side of screen
        draw_text_left(
            str("Wind direction: " + weather_data.string_direction),
            font_small,
            WHITE,
            WIDTH - GRID1_X_OFFSET + 10,
            GRID_Y_OFFSET + 40,
        )

        draw_text_left(
            ("Wind speed: " + str(weather_data.wind_values[0]) + " km/h"),
            font_small,
            WHITE,
            WIDTH - GRID1_X_OFFSET + 10,
            GRID_Y_OFFSET + 10,
        )

        for index, boat in enumerate(boats):
            screen.blit(boat_img_list[index], boat)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for num, boat in enumerate(boats):
                        if boat.collidepoint(event.pos):
                            active_boat = num
                elif event.button == 3 and active_boat is not None:
                    boat_img_list[active_boat] = pg.transform.rotate(
                        boat_img_list[active_boat], 90
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
            await ship_list.put(json.dumps(final_boat_coords))
            return

        clock.tick(60)

        await asyncio.sleep(0)


async def send_nuke_to_enemy_boat_phase():
    global turn
    global enemy_title
    global is_winner
    global is_loser
    global hp_value

    while True:
        screen.blit(bg_img_game, (0, 0))

        # draw grids with water texture overlay
        draw_water_grid(GRID1_X_OFFSET)
        draw_water_grid(GRID2_X_OFFSET)

        # define dimensions for health bar
        hp_rect = pg.Rect(
            GRID1_X_OFFSET,
            GRID_Y_OFFSET + (CELL_SIZE * 10.1),
            CELL_SIZE * (0.6666 * hp_value),
            CELL_SIZE * 0.3,
        )

        # drawing wind info and rules on right side of screen
        draw_text_left(
            str("Wind direction: " + weather_data.string_direction),
            font_small,
            WHITE,
            WIDTH - GRID1_X_OFFSET + 10,
            GRID_Y_OFFSET + 40,
        )

        draw_text_left(
            ("Wind speed: " + str(weather_data.wind_values[0]) + " km/h"),
            font_small,
            WHITE,
            WIDTH - GRID1_X_OFFSET + 10,
            GRID_Y_OFFSET + 10,
        )

        screen.blit(
            hit_mark, ((WIDTH - GRID1_X_OFFSET // 2) - 120, GRID_Y_OFFSET + 100)
        )

        draw_text_center(
            " means hit",
            font_small,
            WHITE,
            (WIDTH - GRID1_X_OFFSET // 2) - 30,
            GRID_Y_OFFSET + 130,
        )

        screen.blit(
            miss_mark, ((WIDTH - GRID1_X_OFFSET // 2) - 120, GRID_Y_OFFSET + 150)
        )

        draw_text_center(
            " means miss",
            font_small,
            WHITE,
            (WIDTH - GRID1_X_OFFSET // 2) - 20,
            GRID_Y_OFFSET + 180,
        )

        # changing color of players name depending on turn
        if turn:
            draw_text_center(
                player_title,
                font_big,
                GREEN,
                GRID1_X_OFFSET + GRID_WIDTH // 2,
                GRID_Y_OFFSET // 2,
            )
            draw_text_center(
                enemy_title,
                font_big,
                WHITE,
                GRID2_X_OFFSET + GRID_WIDTH // 2,
                GRID_Y_OFFSET // 2,
            )
        else:
            draw_text_center(
                player_title,
                font_big,
                WHITE,
                GRID1_X_OFFSET + GRID_WIDTH // 2,
                GRID_Y_OFFSET // 2,
            )
            draw_text_center(
                enemy_title,
                font_big,
                GREEN,
                GRID2_X_OFFSET + GRID_WIDTH // 2,
                GRID_Y_OFFSET // 2,
            )

        for index, boat in enumerate(boats):
            screen.blit(boat_img_list[index], boat)

        draw_hit(grid_player, GRID1_X_OFFSET)
        draw_hit(grid_opponent, GRID2_X_OFFSET)

        # drawing health bar with different length and color depending on its value
        if hp_value > 10:
            pg.draw.rect(screen, GREEN, hp_rect, border_radius=3)
        elif hp_value < 11 and hp_value > 6:
            pg.draw.rect(screen, YELLOW, hp_rect, border_radius=3)
        elif hp_value < 7 and hp_value > 3:
            pg.draw.rect(screen, ORANGE, hp_rect, border_radius=3)
        else:
            pg.draw.rect(screen, RED, hp_rect, border_radius=3)
            
        # display winner or loser when game ends at bottom middle of the screen
        if is_winner:
            pg.draw.rect(
                screen,
                OUTERBOX,
                (WIDTH // 2 - 105, HEIGHT - 130, 210, 60),
                border_radius=10,
            )
            draw_text_center("YOU WON!", font_big, WHITE, WIDTH // 2, HEIGHT - 100)
        if is_loser:
            pg.draw.rect(
                screen,
                OUTERBOX,
                (WIDTH // 2 - 105, HEIGHT - 130, 210, 60),
                border_radius=10,
            )
            draw_text_center("YOU LOST!", font_big, WHITE, WIDTH // 2, HEIGHT - 100)

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
                hit_message = await asyncio.wait_for(hit.get(), 0.1)
                hit_message = list(json.loads(hit_message))
                row, col = hit_message[0]
                if hit_message[1] == "hit":
                    grid_player[row][col] = 1
                else:
                    grid_player[row][col] = 2

                hp_value = await asyncio.wait_for(health.get(), 0.1)
                hp_value = int(json.loads(hp_value))
            except asyncio.TimeoutError:
                pass

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and not is_winner and not is_loser:
                if turn:
                    await take_shot(
                        grid_opponent,
                        GRID2_X_OFFSET,
                        event.pos,
                    )

            if event.type == pg.QUIT:
                return

        clock.tick(60)

        await asyncio.sleep(0)


async def battleship():
    global enemy_title

    create_boats()

    await welcome_screen()

    enemy_title = await player_name.get()

    await boat_phase()
    await send_nuke_to_enemy_boat_phase()

    pg.quit()


async def main():
    battleship_task = asyncio.create_task(battleship())
    server_connection_task = asyncio.create_task(
        client.handle_server_connection(
            player_name,
            ship_list,
            player_turn,
            shot_coords,
            hit,
            hit_miss,
            health,
            winner,
        )
    )

    await asyncio.gather(battleship_task, server_connection_task)


asyncio.run(main())
