# CSCI 331 - Game_logic
# Author: Ulrik Bucksteg-Neuhoff
# Date: March 12, 2025

class GameState():
    def __init__(self):
        self.rows = 10
        self.cols = 10
        self.row_ship = (3, 1) #3 row 1 col size
        self.cols_ship = (1, 3) #1 row 3 col size
        #save idea about ship placing method

class Player1(GameState):
    def __init__(self):
        super().__init__() #call GameState constructor
        self.player1_grid = [[0] * self.cols for _ in range(self.rows)] #fill all cols and rows with 0's 
        self.player1_grid[3][4] = "x" #rows/coloums count from 0-9. this sets 4th row 5th column to a x

    def PrintGrid(self) -> list:
        print("Player1 grid")
        for row in self.player1_grid:
            print(" ".join(map(str, row)))

class Player2(GameState):
    def __init__(self):
        super().__init__() #call GameState constructor
        self.player2_grid = [[0] * self.cols for _ in range(self.rows)] #fill all cols and rows with 0's 

    def PrintGrid(self) -> list:
        print("Player2 grid")
        for row in self.player2_grid:
            print(" ".join(map(str, row)))


if __name__ == '__main__':
    print("*" * 10)
    Player1 = Player1()
    Player1.PrintGrid()
    Player2 = Player2()
    Player2.PrintGrid()
    print("*" * 10)