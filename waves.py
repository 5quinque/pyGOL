#!/usr/bin/python3

import curses
import time

class GameOfLife:
    def __init__(self):
        """ Create variable and set up curses """
        self.screen = curses.initscr()
        # Hide the cursor
        curses.curs_set(False)
        curses.mousemask(True)
        # make getch() non-blocking
        self.screen.nodelay(True)
    
        curses.start_color()
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_BLACK)

        self.running = True
        self.paused = False

    def main(self, stdscr):
        """ The main loop handling the game """
        while self.running:
            event = self.screen.getch() 
            if event: self.handleinput(event)
            if self.paused:
                self.showpaused()
            else:
                self.update()
            time.sleep(.01)

    def showpaused(self):
        """ If the game is currently paused, this function will print
            'Paused' in big letters 
        """
        screen_rows, screen_cols = self.screen.getmaxyx()
        middle = int(screen_cols / 2) - 29

        self.screen.addstr(0, middle, '                                                     ,,')
        self.screen.addstr(1, middle, '`7MM"""Mq.                                         `7MM')
        self.screen.addstr(2, middle, '  MM   `MM.                                          MM')
        self.screen.addstr(3, middle, '  MM   ,M9 ,6"Yb.`7MM  `7MM  ,pP"Ybd  .gP"Ya    ,M""bMM')
        self.screen.addstr(4, middle, '  MMmmdM9 8)   MM  MM    MM  8I   `" ,M\'   Yb ,AP    MM')
        self.screen.addstr(5, middle, '  MM       ,pm9MM  MM    MM  `YMMMa. 8M"""""" 8MI    MM')
        self.screen.addstr(6, middle, '  MM      8M   MM  MM    MM  L.   I8 YM.    , `Mb    MM')
        self.screen.addstr(7, middle, '.JMML.    `Moo9^Yo.`Mbod"YML.M9mmmP\'  `Mbmmd\'  `Wbmd"MML.')

        # Add some colour
        """ We're using colours 4 - 9 (6 in total)
            We first get the remainder from 'x' / 6, add the 'y' and get the remainder again
            plus 4 since we start our colours at 4.
            Colours are in the first 8 bits, so shift the colour to the left 8 bits and 'or'
            it with the character value. Then we can print it on the screen
        """
        for y in range(8):
            for x in range(middle, middle+57):
                char_value = self.screen.inch(y,x)
                colour = ((x % 6 + y) % 6) + 4
                char_w_attr = (colour << 8) | char_value
                self.screen.addch(y, x, char_w_attr)

    def handleinput(self, event):
        """ Handle mouse clicks and keypresses """
        if event == ord("q"): self.running = False
        if event == ord(" "): self.paused ^= 1
        if event == curses.KEY_MOUSE:
            _, x, y, _, _ = curses.getmouse()
            self.togglelife(y, x)
    
    def togglelife(self, row, col):
        """ When clicking on a square,
            life is either given or taken away
        """

        if self.getcharvalue(row, col) == ord('X'):
            self.screen.addstr(row, col, ' ', curses.color_pair(3))
        else:
            self.screen.addstr(row, col, 'X', curses.color_pair(2))

    def countneighbour(self, row, col):
        count = 0;
        screen_rows, screen_cols = self.screen.getmaxyx()
        for y in range(row - 1, row + 2):
            for x in range(col - 1, col + 2):
                if ((y | x) >> 31 or y > screen_rows - 1 or x > screen_cols - 1 or
                        (y == row and x == col)):
                    continue
                if self.getcharvalue(y, x) == ord('X'): count += 1
        return count

    def getcharvalue(self, y, x):
        """ https://docs.python.org/2/library/curses.html#curses.window.inch
            window.inch([y, x])
            Return the character at the given position in the window.
            The bottom 8 bits are the character proper, and upper bits are the attributes.

            We only want the character so use a bitwise `and` to get the lower 8 bits
        """
        return 255 & self.screen.inch(y, x)

    def update(self):
        """ Apply the rules of life """
        values_to_update = []
        screen_rows, screen_cols = self.screen.getmaxyx()
        for y in range(0, screen_rows):
            for x in range(0, screen_cols - 1):
                count = self.countneighbour(y, x)
                if count < 2 or count > 3:
                    values_to_update.append({'y': y, 'x': x, 'value': ' ',
                                             'attr': curses.color_pair(3)})
                if count == 3:
                    values_to_update.append({'y': y, 'x': x, 'value': 'X',
                                             'attr': curses.color_pair(2)})
        for value in values_to_update:
            self.screen.addstr(value['y'], value['x'], value['value'], value['attr'])

if __name__ == "__main__":
    x = GameOfLife()
    curses.wrapper(x.main)
