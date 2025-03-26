import asyncio
import json

import websockets


# Asyncio queue as params to recieve data that can be then used by
# the game while it is running
# TODO: handle logic for ship placement phase and game phase
async def handle_server_connection(
    target: asyncio.Queue, ships: asyncio.Queue, turn: asyncio.Queue, hit: asyncio.Queue
):
    print("Client started!")
    async with websockets.connect("ws://127.0.0.1:5050/client") as server:
        ships_coords = await ships.get()
        await server.send(ships_coords)
        print("Sent ship coords")

        turn_message = await server.recv()
        await turn.put(turn_message)
        print(f"Turn message recieved from server: {turn_message}")

        while True:
            if turn_message == "Your turn":
                target_coords = await target.get()
                await server.send(target_coords)
                print("Sending target coords to server")

            # message from the server telling if its
            # the player's turn
            turn_message = await server.recv()
            print(f"Turn message recieved from server: {turn_message}")
            await turn.put(turn_message)

            hit_coords = await server.recv()
            await hit.put(hit_coords)

            # if it is the player's turn we need to now
            # wait for target coords
