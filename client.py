import asyncio
import json

import websockets


# Asyncio queue as params to recieve data that can be then used by
# the game while it is running
# TODO: figure out logic to transfer and recieve player names
async def handle_server_connection(
    player: asyncio.Queue,
    ships: asyncio.Queue,
    turn: asyncio.Queue,
    shot: asyncio.Queue,
    hit: asyncio.Queue,
    hit_miss: asyncio.Queue,
    health: asyncio.Queue,
    winner: asyncio.Queue,
):
    print("Client started!")
    async with websockets.connect("ws://127.0.0.1:5050/client") as server:
        print("Waiting to recieve player name from the game...")
        player_name = await player.get()
        print(f"Player name recieved from the game: {player_name}")
        await server.send(player_name)
        print(f"Player name sent to server {player_name}")

        print("Waiting to recieve opponent name from the server...")
        opponent_name = await server.recv()
        print(f"Enemy name recieved from the server {opponent_name}")
        await player.put(opponent_name)

        # sending the ships coords to the server
        print("Waiting to recieve ship coords from the game...")
        ship_coords = await ships.get()
        print(f"Ship coords recieved from the game: {ship_coords}")
        await server.send(ship_coords)
        print("Sent ship coords")

        # setting the initial turn message
        # as recieved from the server
        print("Waiting for initial turn message...")
        turn_message = await server.recv()
        print(f"Turn message recieved from server: {turn_message}")
        await turn.put(turn_message)
        print("Initial turn message now acceible to the game")

        while True:
            # if it is the player's turn we need to now
            # wait for shot coords
            if turn_message == "Your turn":
                shot_coords = await shot.get()
                await server.send(shot_coords)
                print("Sending shot coords to server")

                hit_miss_message = await server.recv()
                print(
                    f"Shot taken hit or miss message recieved from server: {hit_miss_message}"
                )
                await hit_miss.put(hit_miss_message)

            print("Waiting for info message from the server...")

            # Winner message after every turn played
            winner_message = await server.recv()
            print(f"Winner message from server: {winner_message}")
            await winner.put(winner_message)

            # message from the server telling if its
            # the player's turn
            turn_message = await server.recv()
            print(f"Turn message recieved from server: {turn_message}")
            await turn.put(turn_message)

            # hit coords of where the enemy player hit
            print("Waiting for opponent's shot message...")
            shot_message = await server.recv()
            print(f"Recieved opponent shot message: {shot_message}")
            shot_message = json.loads(shot_message)
            shot_coords = shot_message[0]
            print(f"Shot coords of opponent shot: {shot_coords}")
            print(f"Opponent shot hit or miss: {shot_message[1]}")
            await hit.put(json.dumps([shot_coords, shot_message[1]]))

            health_value = json.dumps(shot_message[2])
            print(f"Updated health recieved from the server {health_value}")
            await health.put(health_value)
