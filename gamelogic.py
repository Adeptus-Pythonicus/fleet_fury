# CSCI 331 - Game_logic
# Author: Ulrik Bucksteg-Neuhoff
# Date: March 12, 2025

class GameState():
    def __init__(self):
        self.rows = 10
        self.cols = 10
        self.row_ship = (1, 3) #1 row 3 col size
        self.cols_ship = (3, 1) #3 row 1 col size

class Player(GameState):
    #Initilizer
    def __init__(self):
        super().__init__() # Call GameState constructor
        self.player_grid = [[0] * self.cols for _ in range(self.rows)] # Fill all cols and rows with 0's 

    # Print grid out
    def PrintGrid(self) -> list: 
        print("Player grid")
        for row in self.player_grid:
            print(" ".join(map(str, row))) # Statement to remove extra syntax for printing lists.

    # Function for logic behind placing ships
    def place_ship(self, placetuple: tuple, orientation: str) -> bool: # make a method for cood being center of ship and placing 1 left and right or 1 up and down
        row_ship = (1, 3) 
        col_ship = (3, 1)
        row, col = placetuple # for placing ship, i recieve center coord, -1 based on horizontal or vertical and use my ship place algorithm

        if orientation == 'horizontal': # Ensure ship fits horizontally
            ship_rows, ship_cols = row_ship
            col = col - 1
            if col + ship_cols > self.cols:
                print("Error: ship goes out of bounds")
                return False  
            
            if any(self.player_grid[row][c] != 0 for c in range(col, col + ship_cols)): # Check for overlapping ships
                print("Error: Overlapping ships")
                return False  
            for c in range(col, col + ship_cols): # Place the ship
                print(f"Placing 'x' at ({row},{c})")  # Debug statement
                self.player_grid[row][c] = "x"

        elif orientation == 'vertical': # Ensure ship fits vertically
            ship_rows, ship_cols = col_ship
            row = row - 1
            if row + ship_rows > self.rows:
                print("Error: Ship goes out of bounds vertically.")
                return False  
            
            if any(self.player_grid[r][col] != 0 for r in range(row, row + ship_rows)):  # Check for overlapping ships
                print("Error: Overlapping ships detected in vertical placement.")
                return False 
            for r in range(row, row + ship_rows):   # Place the ship
                print(f"Placing 'x' at ({r},{col})")  # Debug statement
                self.player_grid[r][col] = "x"

        else:
            print("Error: Invalid orientation. Choose 'horizontal' or 'vertical'.")
            return False
        
        return True  # Ship placed successfully
    
    #Takes shot as tuple for row and col and logic behind shot
    def take_shot(self,shot: tuple) -> bool: 
        shot_row, shot_col = shot

        if shot_row < 0 or shot_col < 0 or shot_row >= self.rows or shot_col >= self.cols: # out of bounds shot
            print("Invalid shot! out of bounds")
            return 0
        
        if self.player_grid [shot_row][shot_col] == 'H': # Hitting same spot twice
            print("Place on ship already hit!")
            return 0
        
        if self.player_grid [shot_row][shot_col] == 'x': # Successful hit
            print("Hit!")
            self.player_grid [shot_row][shot_col] = 'H'
            return 1
        
        else: # Miss
            print("Miss!")
            self.player_grid [shot_row][shot_col] = 'M'
            return 0

if __name__ == '__main__': # This main is used for testing and debugging
    player = Player() 
    print("Placing ship at (2,3 - horizontal)")
    success = player.place_ship((2, 3), 'horizontal')
    print("Ship placed:", success)
    player.PrintGrid()
    print("Placing ship at (4,5 - vertical)")
    success = player.place_ship((4, 5), 'vertical')
    player.PrintGrid()
    print("Placing ship at (8,8) - invalid orientation")
    success = player.place_ship((8, 8), 'diagonal')
    print("Ship placed:", success)
    player.PrintGrid()
    player.take_shot((2, 3))
    player.PrintGrid()
    player.take_shot((4, 4))
    player.PrintGrid()
    player.take_shot((2, 3))
    player.PrintGrid()