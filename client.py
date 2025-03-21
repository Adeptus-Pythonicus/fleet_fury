import asyncio
import json

import websockets


# Asyncio queue as params to recieve data that can be then used by
# the game while it is running
# TODO: handle logic for ship placement phase and game phase
async def handle_server_connection(
    target: asyncio.Queue, ship: asyncio.Queue, turn: asyncio.Queue
):
    print("Client started!")
    async with websockets.connect("ws://127.0.0.1:5050/client") as server:
        while True:
            # message from the server telling if its
            # the player's turn
            turn_message = await server.recv()
            await turn.put(turn_message)
            # if it is the player's turn we need to now
            # wait for target coords
            if turn_message == "Your turn":
                target_coords = await target.get()
                await server.send(target_coords)
