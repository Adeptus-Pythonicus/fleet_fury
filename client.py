import websockets
import asyncio
import json

async def handle_battleship_connection(websocket):
    #this is to connect to /client at port 5050
    async with websockets.connect("ws://127.0.0.1:5050/client") as server_ws:

        #this is a loop? that listens to the battleship
        #single client connection
        async for message in websocket:
            print(f"Received from battleship.py: {message}")

            #forward the message to server.py
            await server_ws.send(json.dumps(message))
            #wait for the reply
            response = await server_ws.recv()
            print(f"Received from server.py: {response}")

            #relay the response to battleship.py
            await websocket.send(json.dumps(response))

async def main():
    #this takes to run the connection to localhost at port 5051 in which battleship.py runs
    async with websockets.serve(handle_battleship_connection, "localhost", 5051):
        await asyncio.Future()

<<<<<<< Updated upstream
asyncio.run(main())
=======
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
>>>>>>> Stashed changes
