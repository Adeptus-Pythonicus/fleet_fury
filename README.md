# Fleet Fury

![Screenshot_20250325_140054_Samsung_Notes](https://hackmd.io/_uploads/H1JXWoe6Jl.jpg)


" The greatest implementation of Python ever conceived. " - Guido Van Rossum (probably) 


Fleety Fury is a Python-based Battleship game that utilizes websockets as our project for CSCI 331 Object Oriented Programming course.
The codebase features code for the client, client-side UI, the server, and the game logic.

At its core, the game operates on a client-server architecture. The server, initalized by **fastAPI.py**, starts by waiting for two clients ( 2x instances of **client.py**, invoked by running **battleship.py**) to connect to its websocket endpoint. The first client to connnect assumes Player 1, while the other becomes Player 2. 

**battleship.py** handles the display of UI elements and imports the client code for establishing a connection to the server.

Every message sent to the server is relayed to **gamelogic.py**, which manages the game state and keeps tracks of the clients' ship placement and health.



## Requirements

Python3.10 or greater, specific libraries and frameworks
are outlined in **requirements.txt**




## Installation


A virtual environment is recommended to maintain the project's dependencies.

```
python -m venv virtual_environment_name
```

Activate the virtual environment prior to installing the required modules
```
source virtual_environment_name/bin/activate
```

Once in the virtual environment, change the directory to the root of the project and install the required dependencies.
```
pip install -r requirements.txt
```


## Usage

Testing the project is done by having
three seperate terminals. Start the server by running
```
python3 fastAPI.py
```


[![asciicast](https://asciinema.org/a/2aIRLh40jqOjBwSgSP78OCp3c.svg)](https://asciinema.org/a/2aIRLh40jqOjBwSgSP78OCp3c)


## Credits

Jamie
Saksham
Ulrik
Yulia
Johann
