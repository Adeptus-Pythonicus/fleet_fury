import websockets
import asyncio
import json

PORT = 5050


async def client(ws):
    print(f"Pygame {ws} connected")
    print(await ws.recv())

    while True:
        msg = tuple(json.loads(await ws.recv()))
        print(f"Message from game: {msg}")

        if msg == "close":
            await ws.send("close")
        else:
            await ws.send("Ok")


async def main():
    print("Server Started!")
    async with websockets.serve(client, "localhost", PORT):
        await asyncio.Future()


asyncio.run(main())
