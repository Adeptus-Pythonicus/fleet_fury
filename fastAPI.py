import json
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket
from gamelogic import Player

app = FastAPI()
connection_list = []
players = []
ships_placed = [False, False]
current_turn = 0

@app.websocket("/client")
async def client_endpoint(websocket: WebSocket):
    global current_turn
    await websocket.accept()
    print("client connected!")
    connection_list.append(websocket)
    players.append(Player())
    current_player_idx = connection_list.index(websocket)
    is_connected = True

    ship_coords_received = False
    player_name_received = False
    
    try:
        while True:
            if not player_name_received:
                player_name = await websocket.receive_text()
                print(f"Player name received from client: {player_name}")
                if websocket == connection_list[0]:
                    await connection_list[1].send_text(player_name)
                else:
                    await connection_list[0].send_text(player_name)
                player_name_received = True

            if not ship_coords_received:
                ship_coords = await websocket.receive_json()
                print(f"Ship coords received from client: {ship_coords}")
                
                # Validate ship coordinates
                if not all(len(ship) == 3 and ship[2] in ['h','v'] for ship in ship_coords):
                    await websocket.send_text("ERROR: Invalid ship format")
                    return
                
                players[current_player_idx].place_ship(ship_coords)
                ship_coords_received = True
                ships_placed[current_player_idx] = True

                # Wait for both players to be ready
                while not all(ships_placed):
                    await asyncio.sleep(0.1)

                # Set initial turns
                if websocket == connection_list[0]:
                    await connection_list[0].send_text("Your turn")
                    await connection_list[1].send_text("Not your turn")
                else:
                    await connection_list[1].send_text("Not your turn")

            # Gameplay phase
            hit_coords = await websocket.receive_json()
            print(f"Hit coords received from client: {hit_coords}")

            # Validate hit coordinates
            if not (isinstance(hit_coords, list) and len(hit_coords) == 2):
                await websocket.send_text("ERROR: Invalid coordinates")
                continue

            # Check turn validity
            if current_player_idx != current_turn:
                await websocket.send_text("Not your turn!")
                continue

            # Process hit
            opponent_idx = 1 - current_player_idx
            hit_result = players[opponent_idx].take_shot(hit_coords)

            # Broadcast results
            for player in connection_list:
                if player != websocket:
                    await player.send_json({
                        "coordinates": hit_coords,
                        "result": "hit" if hit_result else "miss"
                    })
                    await player.send_text("Your turn" if not hit_result else "Not your turn")

            # Update turn state
            if not hit_result:
                current_turn = 1 - current_turn
                await websocket.send_text("Not your turn")
            else:
                await websocket.send_text("Your turn")

    except Exception as e:
        print(f"Connection error: {e}")
        
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)