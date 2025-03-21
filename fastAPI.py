import json

import uvicorn
from fastapi import FastAPI, WebSocket

app = FastAPI()
connection_list = []


@app.websocket("/client")
async def client_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("client connected!")
    connection_list.append(websocket)
    if len(connection_list) == 1:
        await websocket.send_text("Your turn")
    else:
        await websocket.send_text("Not your turn")

    while True:
        data = await websocket.receive_text()
        print(f"Received from client: {data}")
        for player in connection_list:
            if player != websocket:
                await player.send_text("Your turn")

        # will process the data from game logic from Ulrik
        # sending it back in a tuple
        # response = f"Processed: {data}"
        # await websocket.send_text(json.dumps(response))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
