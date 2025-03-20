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

asyncio.run(main())