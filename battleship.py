import pygame
import websockets
import asyncio
import json


async def websocket_client():
    url = "ws://127.0.0.1:5050"

    async with websockets.connect(url) as ws:
        await ws.send("Pygame websocket connected!")

        while True:
            await ws.send(input("Send server a message: "))
            msg = await ws.recv()
            print(msg)

            if msg == "close":
                break


asyncio.run(websocket_client())
