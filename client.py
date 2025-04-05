import asyncio
import json

import websockets


# Asyncio queue as params to recieve data that can be then used by
# the game while it is running
# TODO: figure out logic to transfer and recieve player names
async def handle_server_connection(
    player: asyncio.Queue,
    target: asyncio.Queue,
    ships: asyncio.Queue,
    turn: asyncio.Queue,
    hit: asyncio.Queue,
):
    print("Client started!")
    async with websockets.connect("ws://127.0.0.1:5050/client") as server:
        player_name = await player.get()
        await server.send(player_name)
        print(f"Player name sent to server {player_name}")

        enemy_name = await server.recv()
        print(f"Enemy name recieved from the server {enemy_name}")
        await player.put(enemy_name)

        # sending the ships coords to the server
        ships_coords = await ships.get()
        await server.send(ships_coords)
        print("Sent ship coords")

        # setting the initial turn message
        # as recieved from the server
        turn_message = await server.recv()
        await turn.put(turn_message)
        print(f"Turn message recieved from server: {turn_message}")

        while True:
            # if it is the player's turn we need to now
            # wait for target coords
            if turn_message == "Your turn":
                target_coords = await target.get()
                await server.send(target_coords)
                print("Sending target coords to server")

            # message from the server telling if its
            # the player's turn
            turn_message = await server.recv()
            print(f"Turn message recieved from server: {turn_message}")
            await turn.put(turn_message)

            if turn_message in ("You win!", "You lose"):
                print(turn_message)
                break

            # hit coords of where the enemy player hit
            hit_message = await server.recv()
            hit_message = json.loads(hit_message)
            hit_coords = json.dumps(hit_message[0])
            await hit.put(hit_coords)

            print(f"Hit or miss: {hit_message[1]} | Player health: {hit_message[2]}")
