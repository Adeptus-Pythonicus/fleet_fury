import asyncio
import json

import uvicorn
from fastapi import FastAPI, WebSocket

from gamelogic import Player

app = FastAPI()
connection_list = []  # connection list
players = []  # player as a list
ships_placed = [False, False]  # setting up that ships are not placed yet
current_turn = 0  # as player 1


@app.websocket("/client")
async def client_endpoint(websocket: WebSocket):
    global current_turn  # to be able to change current_turn within this function

    await websocket.accept()
    print("client connected!")

    # append the websocket to the connection
    connection_list.append(websocket)

    players.append(Player())  # append the player that calls on Ulrik's player class

    # set the index of the current player as the first websocket that got connected.
    current_player_idx = connection_list.index(websocket)

    # Getting player name and sending it to opponent
    player_name = await websocket.receive_text()
    print(f"Player name received from client: {player_name}")
    if websocket == connection_list[0]:
        await connection_list[1].send_text(player_name)
    else:
        await connection_list[0].send_text(player_name)
    print("Player name sent to opponent")

    # Receive ship coords from the player
    # this receives this as list of any data type, this should good
    print("Waiting for ship coordinates from the client...")
    ship_coords = await websocket.receive_json()
    print(f"Ship coords received from client: {ship_coords}")

    # Setting up ship placement for the player
    # this should be right
    players[current_player_idx].place_ship(ship_coords)
    ships_placed[current_player_idx] = True

    # sending initial message turns
    print("Sending initial turn message...")
    if websocket == connection_list[0]:
        await connection_list[1].send_text("Not your turn")
    else:
        await connection_list[0].send_text("Your turn")
    print("Sent initial turn message")

    """
    validate incoming ship format
    if not all(len(ship) == 3 and ship[2] in ['h','v'] for ship in ship_coords):
        await websocket.send_text("ERROR: Invalid ship format")
        return
    """

    try:
        while True:
            # hit process
            hit_coords = await websocket.receive_json()
            print(f"Hit coords received from client: {hit_coords}")

            """"
            TODO: same issue as the block of comment; must be fixed
            if not (isinstance(hit_coords, list) and len(hit_coords) == 2):
                await websocket.send_text("ERROR: Invalid coordinates")
                continuefalse
            """

            # should be right
            opponent_idx = 1 - current_player_idx  # just between 1 and 0
            hit_result = players[opponent_idx].take_shot(hit_coords)

            message = "hit" if hit_result else "miss"
            await connection_list[current_player_idx].send_text(message)

            # check winner
            result = players[opponent_idx].check_winner()
            if result == 1:
                print("Sending no winner messages")
                await connection_list[opponent_idx].send_text("No winner")
            if result == 0:
                print(f"Winner is {player_name}")
                await connection_list[current_player_idx].send_text("Winner")
                await connection_list[opponent_idx].send_text("Loser")

            print("Sending your turn to opponent")
            await connection_list[opponent_idx].send_text("Your turn")

            message = [
                hit_coords,
                "hit" if hit_result else "miss",
                players[opponent_idx].player_health,
            ]
            print("Sending hit message to opponent")
            await connection_list[opponent_idx].send_json(message)

    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
