from fastapi import FastAPI, WebSocket

#create an instance of the FastAPI class
app = FastAPI()

#endpoint for the websocket is like a decorator "/" and "ws" for WebSocket as the path
@app.websocket("/ws")

#define a function that takes an input websocket borrowed from the WebSocket class
#async is actually I dont know, the documentation does says so
async def websocket_endpoint(websocket: WebSocket):
    #await: it is like cin in c++ and waits for the user's input
    #accept the WebSocket connection
    await websocket.accept()
    
    #sends a send text message to the client
    await websocket.send_text("Hello, world!")
    
    #close the connection
    await websocket.close()
