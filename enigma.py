import curses

from curses import wrapper
from curses.textpad import rectangle
from Morse import Morse
from Grid import Grid




def main(stdscr):
    curses.start_color()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)

    BLACK_ON_CYAN = curses.color_pair(1)
    BLACK_ON_RED = curses.color_pair(2)
    BLACK_ON_GREEN = curses.color_pair(3)
    BLACK_ON_BLUE = curses.color_pair(4)
    BLACK_ON_YELLOW = curses.color_pair(5)
    WHITE_ON_BLACK = curses.color_pair(6)

    class WinDim:
        def __init__(self, y0, x0, y1, x1):
            self.x0 = x0
            self.y0 = y0
            self.x1 = x1
            self.y1 = y1
            self.cols = x1-x0
            self.lines = y1-y0

    BOAT_WIN = WinDim(2, 1, int(curses.LINES * 0.8), int(curses.COLS * 0.8))
    MENU_WIN = WinDim(BOAT_WIN.y1+1, 1, curses.LINES - 1, curses.COLS - 1)
    MORSE_WIN = WinDim(2, BOAT_WIN.x1+1, BOAT_WIN.y1, curses.COLS - 1)



    stdscr.addstr(0, 0, "Enigma: Save out Convoy  y{} x{}".format( curses.LINES, curses.COLS))

    boatwin = curses.newwin(BOAT_WIN.lines, BOAT_WIN.cols, BOAT_WIN.y0, BOAT_WIN.x0)
    rectangle(stdscr, BOAT_WIN.y0-1, BOAT_WIN.x0-1, BOAT_WIN.y1, BOAT_WIN.x1)

    morsewin = curses.newwin(MORSE_WIN.lines, MORSE_WIN.cols, MORSE_WIN.y0, MORSE_WIN.x0)
    rectangle(stdscr, MORSE_WIN.y0-1, MORSE_WIN.x0-1, MORSE_WIN.y1, MORSE_WIN.x1)

    menuwin = curses.newwin(MENU_WIN.lines, MENU_WIN.cols, MENU_WIN.y0, MENU_WIN.x0)
    #rectangle(stdscr, MENU_WIN.y0-1, MENU_WIN.x0-1, MENU_WIN.y1, MENU_WIN.x1)

    stdscr.refresh()

    # boatwin.bkgd(curses.color_pair(1))
    boatwin.refresh()

    morse = Morse(morsewin,
                  receive_array_color=[BLACK_ON_GREEN, BLACK_ON_RED],
                  receive_array_strings=["RECEIVE", "SEND"],
                  status_color=BLACK_ON_YELLOW,
                  speed_color=BLACK_ON_BLUE,
                  volume_color=BLACK_ON_BLUE,
                  backround=WHITE_ON_BLACK)

    grid = Grid(boatwin,
                convoi_color = BLACK_ON_BLUE,
                mine_color = BLACK_ON_YELLOW,
                uboat_color = BLACK_ON_RED,
                path_color = BLACK_ON_CYAN)

    menuwin.addstr(0,0, "MENU STUFF")
    # menuwin.bkgd(curses.color_pair(2))
    menuwin.refresh()
    # box = Textbox(boatwin)

    key = " "
    while(key != "q"):
        try:
            key = stdscr.getkey()
        except:
            key = " "
        morse.update_status()
        if key == "+":
            morse.increase_volume()
        if key == "-":
            morse.decrease_volume()
        if key == "9":
            morse.increase_speed()
        if key == "6":
            morse.decrease_speed()
        if key == "1":
            morse.toggle_send_receive()

    # # Let the user edit until Ctrl-G is struck.
    # box.edit()
    #
    # # Get resulting contents
    # message = box.gather()

wrapper(main)