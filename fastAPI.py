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
    is_connected = True

    ship_coords_received = False
    player_name_received = False

    try:
        while True:
            if not player_name_received:
                player_name = await websocket.receive_text()
                print(f"Player name received from client: {player_name}")
                if websocket == connection_list[0]:
                    await connection_list[1].send_text(player_name)
                else:
                    await connection_list[0].send_text(player_name)
                player_name_received = True

            if not ship_coords_received:
                ship_coords = (
                    await websocket.receive_json()
                )  # this receives this as list of any data type, this should good
                print(f"Ship coords received from client: {ship_coords}")

                """
                validate incoming ship format
                if not all(len(ship) == 3 and ship[2] in ['h','v'] for ship in ship_coords):
                    await websocket.send_text("ERROR: Invalid ship format")
                    return
                """

                # this should be right
                players[current_player_idx].place_ship(ship_coords)
                ship_coords_received = True
                ships_placed[current_player_idx] = True

                # sending message turns
                if websocket == connection_list[0]:
                    await connection_list[1].send_text("Not your turn")
                else:
                    await connection_list[0].send_text("Your turn")

            # hit process
            hit_coords = await websocket.receive_json()
            print(f"Hit coords received from client: {hit_coords}")

            """"
            TODO: same issue as the block of comment; must be fixed
            if not (isinstance(hit_coords, list) and len(hit_coords) == 2):
                await websocket.send_text("ERROR: Invalid coordinates")
                continue
            """

            # should be right
            opponent_idx = 1 - current_player_idx  # just between 1 and 0
            hit_result = players[opponent_idx].take_shot(hit_coords)

            for player in connection_list:
                if player != websocket:
                    # Notify the opponent about their turn
                    await player.send_text("Your turn")
                    message = [hit_coords, "hit" if hit_result else "miss"]
                    await player.send_json(message)

    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
