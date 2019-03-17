#!/usr/bin/python3

import curses
import time
import copy
import random

class GameOfLife:
    """ 

    """
    def __init__(self):
        """ Create variable and set up curses"""
        self.screen = curses.initscr()
        # Hide the cursor
        curses.curs_set(False)
        curses.mousemask(True)
        # make getch() non-blocking
        self.screen.nodelay(True)
    
        curses.start_color()
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLACK)

        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)

        self.running = True
        self.paused = False

        self.board = []
        self.temp_board = []

        self.screen_rows, self.screen_cols = self.screen.getmaxyx()

        # https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions
        for yy in range(0, self.screen_rows):
            self.board.append([0 for _ in range(self.screen_cols)])
            self.temp_board.append([0 for _ in range(self.screen_cols)])

    # todo - do we need stdscr? i think no
    def main(self, stdscr):
        """ The main loop handling the game
        Parameters
        ----------
        stdscr : 
        """

        random_count = int((self.screen_rows * self.screen_cols) / 5)
        self.addrandomlife(random_count)

        while self.running:
            event = self.screen.getch() 
            if event: self.handleinput(event)
            if not self.paused:
                self.update()

            self.printgame()
            self.screen.refresh()
            
            time.sleep(.05)

    def printgame(self):
        """ Print the game of life onto the terminal """
        for y in range(0, self.screen_rows):
            for x in range(0, self.screen_cols - 1):
                c = self.board[y][x] ^ 3
                self.screen.addstr(y, x, '{}'.format(self.board[y][x]), curses.color_pair(c))
        if self.paused:
            self.showpaused()

    def showpaused(self):
        """ If the game is currently paused, this function will print
        'Paused' in big letters 
        """
        middle = int(self.screen_cols / 2) - 29

        self.screen.addstr(0, middle, '                                                     ,,  ')
        self.screen.addstr(1, middle, '`7MM"""Mq.                                         `7MM  ')
        self.screen.addstr(2, middle, '  MM   `MM.                                          MM  ')
        self.screen.addstr(3, middle, '  MM   ,M9 ,6"Yb.`7MM  `7MM  ,pP"Ybd  .gP"Ya    ,M""bMM  ')
        self.screen.addstr(4, middle, '  MMmmdM9 8)   MM  MM    MM  8I   `" ,M\'   Yb ,AP    MM  ')
        self.screen.addstr(5, middle, '  MM       ,pm9MM  MM    MM  `YMMMa. 8M"""""" 8MI    MM  ')
        self.screen.addstr(6, middle, '  MM      8M   MM  MM    MM  L.   I8 YM.    , `Mb    MM  ')
        self.screen.addstr(7, middle, '.JMML.    `Moo9^Yo.`Mbod"YML.M9mmmP\'  `Mbmmd\'  `Wbmd"MML.')

        # Add some colour
        """ We're using colours 4 - 9 (6 in total)
        We first get the remainder from 'x' / 6, add the 'y' and get the remainder again
        plus 4 since we start our colours at 4.
        Colours are in the first 8 bits, so shift the colour to the left 8 bits and 'or'
        it with the character value. Then we can print it on the screen
        """
        for y in range(8):
            for x in range(middle, middle + 57):
                char_value = self.screen.inch(y,x)
                colour = ((x % 6 + y) % 6) + 4
                char_w_attr = (colour << 8) | char_value
                self.screen.addch(y, x, char_w_attr)
        # We could probably do addstr(y, x, char_value, curses.color_pair(colour))

    def handleinput(self, event):
        """ Handle mouse clicks and keypresses
        Parameters
        ----------
        event : obj
            User inputted events, keypresses/mouse clicks
        """
        if event == ord("q"): self.running = False
        if event == ord(" "): self.paused ^= 1
        if event == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            self.togglelife(y, x)
    
    def togglelife(self, row, col):
        """ When clicking on a square, life is either given or taken away
        Parameters
        ----------
        row : int
            y axis
        col : int
            x axis
        """

        self.board[row][col] ^= 1

    def countneighbour(self, row, col):
        """ Count the number of live cells next the given cell
        Parameters
        ----------
        row : int
            y axis
        col : int
            x axis
        Returns
        -------
        count : int
            Number of live cells next to given cell
        """
        count = 0
        for y in range(row - 1, row + 2):
            for x in range(col - 1, col + 2):
                # If the neighbouring cell isn't on screen, continue
                if ((y | x) >> 31 or y > self.screen_rows - 1 or x > self.screen_cols - 1 or
                        (y == row and x == col)):
                    continue
                if self.board[y][x]: count += 1
        return count

    def getcharvalue(self, y, x):
        """ Get /only/ the character value of given y,x 
        Parameters
        ----------
        y : int
            y axis
        x : int
            x axis

        https://docs.python.org/2/library/curses.html#curses.window.inch
        window.inch([y, x])
        Return the character at the given position in the window.
        The bottom 8 bits are the character proper, and upper bits are the attributes.

        We only want the character so use a bitwise `and` to get the lower 8 bits
        """
        return 255 & self.screen.inch(y, x)

    def update(self):
        """ Apply the rules of life """
        for y in range(0, self.screen_rows):
            for x in range(0, self.screen_cols - 1):
                count = self.countneighbour(y, x)
                if self.board[y][x]:
                    self.temp_board[y][x] = 0 if (count < 2 or count > 3) else 1
                elif count == 3:
                    self.temp_board[y][x] = 1

        self.board = copy.deepcopy(self.temp_board)
    
    def addrandomlife(self, count):
        """ Add random life to the game
        Parameters
        ----------
        count : int
            Number of cells to give life
        """
        for i in range(count):
            y = random.randrange(1, self.screen_rows)
            x = random.randrange(1, self.screen_cols)
            self.board[y][x] = 1

def main():
    game = GameOfLife()
    curses.wrapper(game.main)

if __name__ == "__main__":
    main()
