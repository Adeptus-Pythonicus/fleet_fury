from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

@app.websocket("/client")
async def client_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("client connected!")

    while True:           
        data = await websocket.receive_text()
        print(f"Received from client: {data}")

        #will process the data from game logic from Ulrik
        response = f"Processed: {data}"
        await websocket.send_text(response)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5050)