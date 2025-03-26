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

    ship_coords_recieved = False
    player_name_recieved = False
    while True:
        if not player_name_recieved:
            player_name = await websocket.receive_text()
            print(f"Player name received from client: {player_name}")
            if websocket == connection_list[0]:
                await connection_list[1].send_text(player_name)
            else:
                await connection_list[0].send_text(player_name)
            player_name_recieved = True

        # if statement to make sure we dont await for ship coords once
        # they are received
        if not ship_coords_recieved:
            ship_coords = await websocket.receive_text()
            print(f"Ship coords received from client: {ship_coords}")
            ship_coords_recieved = True
            # When ships are placed, sending initial turn message
            # based on who connected first
            if websocket == connection_list[1]:
                await connection_list[0].send_text("Your turn")
            elif websocket == connection_list[0]:
                await connection_list[1].send_text("Not your turn")

        # Wait for the hit message
        hit_coords = await websocket.receive_json()
        print(f"Hit coords received from client: {hit_coords}")
        # whenever we get a hit message we tell the other
        # player that its their turn and also send the hit
        # coords
        for player in connection_list:
            if player != websocket:
                await player.send_text("Your turn")
                await player.send_json(hit_coords)

        # will process the data from game logic from Ulrik
        # sending it back in a tuple
        # response = f"Processed: {data}"
        # await websocket.send_text(json.dumps(response))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)
