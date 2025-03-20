# CSCI 331 - Game_logic
# Author: Ulrik Bucksteg-Neuhoff
# Date: March 12, 2025

class GameState():
    def __init__(self):
        self.rows = 10
        self.cols = 10
        self.row_ship = (1, 3) #1 row 3 col size
        self.cols_ship = (3, 1) #3 row 1 col size
        #save idea about ship placing method

class Player1(GameState):
    def __init__(self):
        super().__init__() #call GameState constructor
        self.player1_grid = [[0] * self.cols for _ in range(self.rows)] #fill all cols and rows with 0's 

    def PrintGrid(self) -> list:
        print("Player1 grid")
        for row in self.player1_grid:
            print(" ".join(map(str, row))) #statement to remove extra syntax for printing lists.

    def place_ship(self, ship_size: tuple, row: int, col: int, orientation: str) -> bool:
        ship_rows, ship_cols = ship_size
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return False
        if orientation == 'horizontal':
            if col + ship_cols > self.cols:
                print("Error: ship goes out of bounds")
                return False  # Ensure ship fits horizontally
            if any(self.player1_grid[row][c] != 0 for c in range(col, col + ship_cols)):
                print("Error: Overlapping ships")
                return False  # Check for overlapping ships
            for c in range(col, col + ship_cols): # Place the ship
                print(f"Placing 'x' at ({row},{c})")  # Debug statement
                self.player1_grid[row][c] = "x"
        elif orientation == 'vertical':
            if row + ship_rows > self.rows:
                print("Error: Ship goes out of bounds vertically.")
                return False  # Ensure ship fits vertically
            if any(self.player1_grid[r][col] != 0 for r in range(row, row + ship_rows)):
                print("Error: Overlapping ships detected in vertical placement.")
                return False  # Check for overlapping ships
            for r in range(row, row + ship_rows):   # Place the ship
                print(f"Placing 'x' at ({r},{col})")  # Debug statement
                self.player1_grid[r][col] = "x"
        else:
            print("Error: Invalid orientation. Choose 'horizontal' or 'vertical'.")
            return False
        return True  # Ship placed successfully
    
    def take_shot(self,shot: tuple) -> bool: #change so input for shot is a tuple
        shot_row, shot_col = shot
        if shot_row < 0 or shot_col < 0 or shot_row >= self.rows or shot_col >= self.cols:
            print("Invalid shot! out of bounds")
            return 0
        if self.player1_grid [shot_row][shot_col] == 'x':
            print("Hit!")
            self.player1_grid [shot_row][shot_col] = 'H'
            return 1
        else:
            print("Miss!")
            self.player1_grid [shot_row][shot_col] = 'M'
            return 0

class Player2(GameState):
    def __init__(self):
        super().__init__() #call GameState constructor
        self.player2_grid = [[0] * self.cols for _ in range(self.rows)] #fill all cols and rows with 0's 

    def PrintGrid(self) -> list:
        print("Player2 grid")
        for row in self.player2_grid:
            print(" ".join(map(str, row)))



if __name__ == '__main__':
    player1 = Player1()
    print("Placing ship at (2,3 - horizontal)")
    success = player1.place_ship(player1.row_ship, 2, 3, 'horizontal')
    print("Ship placed:", success)
    player1.PrintGrid()
    print("Placing ship at (4,5 - vertical)")
    success = player1.place_ship(player1.cols_ship, 4, 5, 'vertical')
    player1.PrintGrid()
    print("Placing ship at (8,8) - invalid orientation")
    success = player1.place_ship(player1.cols_ship, 8, 8, 'diagonal')
    print("Ship placed:", success)
    player1.PrintGrid()
    player1.take_shot((2, 3))
    player1.PrintGrid()
    player1.take_shot((4, 4))
    player1.PrintGrid()