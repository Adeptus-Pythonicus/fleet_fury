import asyncio
import json

import websockets


# async def handle_battleship_connection(websocket):
#     # this is to connect to /client at port 5050
#     async with websockets.connect("ws://127.0.0.1:5050/client") as server_ws:
#
#         # this is a loop? that listens to the battleship
#         # single client connection
#         while True:
#             message = json.loads(await websocket.recv())
#             print(f"Received from battleship.py: {message}")
#
#             # forward the message to server.py
#             await server_ws.send(json.loads(message))
#             # # wait for the reply
#             # response = await server_ws.recv()
#             # print(f"Received from server.py: {response}")
#
#             # relay the response to battleship.py
#             # await websocket.send(json.dumps(response))
async def connect_server(target_coords):
    print(target_coords)
    # async with websockets.connect("ws://127.0.0.1:5050/client") as server_ws:
    #     while True:


async def send_message(message):
    asyncio.run(connect_server(message))
