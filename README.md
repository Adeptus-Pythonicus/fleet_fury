# Fleet Fury

<p align="center">
  <img src="https://i.imgur.com/6g0pFtB.jpeg" width="600">
</p>

" The greatest implementation of Python ever conceived. " - Guido Van Rossum (probably) 


Fleety Fury is a Python-based Battleship game that utilizes websockets as our project for VIU's CSCI 331 Object Oriented Programming course.
The codebase features code for the client, client-side UI, the server, and the game logic.

At its core, the game operates on a client-server architecture. The server, initalized by **fastAPI.py**, starts by waiting for two clients ( 2x instances of **client.py**, invoked by running **battleship.py**) to connect to its websocket endpoint. The first client to connnect assumes Player 1, while the other becomes Player 2. 

**battleship.py** handles the display of UI elements and imports the client code for establishing a connection to the server.

Every message sent to the server is relayed to **gamelogic.py**, which manages the game state and keeps tracks of the clients' ship placement and health.
=======
# fleet_fury

Fleety Fury is a Python-based Battleship game that utilizes websockets as
our project for CSCI 331 Object Oriented Programming course.
The codebase features code for the client, client-side UI, the server, and the game logic.



## Requirements

Python3.10 or greater, specific libraries and frameworks are outlined in **requirements.txt**




## Installation


A virtual environment is recommended to maintain the project's dependencies.

```
python -m venv virtual_environment_name
```

Activate the virtual environment prior to installing the required modules
```
<<<<<<< HEAD
source virtual_environment_name/bin/activate    
```

Once in the virtual environment, change the directory to the root of the project and install the required dependencies.
```
pip install -r requirements.txt
```
## Usage

Testing the project is done by having
three separate terminals. Start the server by running
```
python3 fastAPI.py
```


![server](https://i.imgur.com/DQERGEE.png)


Then, from a different terminal, we will launch the UI and client by activating battleship.py.

*IMPORTANT*:

Note that you will need two instances of battleship.py to start playing, with the second one running from another terminal. 

```
python3 battleship.py
```

![client](https://i.imgur.com/oKibdVh.png)

WIP: The Player and Opponent's Grids
![grids](https://i.imgur.com/TRVRX4x.png)

### Scope Status

Since our planning phase at the beginning weeks of the semester, we have decided on a simple architecture and our modules interface with each other
through lists or tuples. This has thankfully worked well and resulted in a stable project where we didn't deviate from our original scope and plan.

## Credits

Jamie
Saksham
Ulrik
Yulia
Johann
=======
source virtual_environment_name/bin/activate
```
