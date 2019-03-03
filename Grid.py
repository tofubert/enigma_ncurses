import logging

from curses.textpad import rectangle
import curses

class WinDim:
    def __init__(self, y0, x0, y1, x1):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.cols = x1 - x0
        self.lines = y1 - y0


class Field:
    def __init__(self, parent, dim):
        self.window = parent.derwin(dim.lines - 1, dim.cols - 1, dim.y0+2, dim.x0+2)
        # self.window.bkgd("~")
        self.window.refresh()

    def set_color(self, color):
        self.window.bkgd(" ", color)

    def set_convoi(self, color):
        # self.window.bkgd(" ", color)
        self.window.addstr(0,0,"       |\\")
        self.window.addstr(1,0,"       | \\")
        self.window.addstr(2,0,"       |  \\")
        self.window.addstr(3,0,"       |___\\")
        self.window.addstr(4,0,"___\--|----/____")
        self.window.addstr(5,0,"    \_____/")
        self.window.refresh()

    def set_uboat(self, color):
        # self.window.bkgd(" ", color)
        self.window.addstr(0,0,"         __  |__")
        self.window.addstr(1,0,"       __L L_|L L__")
        self.window.addstr(2,0," ...[+(____________)")
        self.window.addstr(3,0,"        C_________/")
        self.window.refresh()



class Grid:

    def __init__(self, window, convoi_color, mine_color, uboat_color, path_color):
        self.window = window
        self.maxy, self.maxx = window.getmaxyx()
        self.grid_w = 5
        self.grid_h = 4
        self.convoi_color, self.mine_color, self.uboat_color, self.path_color = convoi_color, mine_color, uboat_color, path_color

        self.fields = [[0 for x in range(self.grid_w)] for y in range(self.grid_h)]

        self.draw_axis()

        for field_x in range(self.grid_w):
            for field_y in range(self.grid_h):
                dim = self.calc_dimensions(field_x, field_y)
                self.draw_border(dim, field_x, field_y)
                self.fields[field_y][field_x] = Field(self.window, dim)
        self.set_convoi(3,0)
        self.set_uboat(0,0)
        self.set_uboat(1,4)
        self.window.refresh()


    def set_convoi(self, y, x):
        (self.fields[y][x]).set_convoi(self.convoi_color)

    def set_uboat(self, y, x):
        (self.fields[y][x]).set_uboat(self.convoi_color)

    def draw_axis(self):
        width = (self.maxx - 2) / self.grid_w
        hight = (self.maxy - 2) / self.grid_h

        for field_x in range(self.grid_w):
            x = 1 + (width * field_x) + int(width/2)
            self.window.addch(1 , x, chr(65+field_x), curses.A_BOLD)
            self.window.addch(1, x+1, chr(65+field_x), curses.A_BOLD)
        for field_y in range(self.grid_h):
            y = 1 + (hight * field_y) + int(hight/2)

            self.window.addch(y , 0, chr(65+field_y), curses.A_BOLD)

    def draw_border(self, dim, field_x, field_y):
        rectangle(self.window, dim.y0+1, dim.x0+1, dim.y1+1, dim.x1+1)
        if field_x == 0:
            if field_y == 0:
                self.window.addch(dim.y0 + 1, dim.x0 + 1, curses.ACS_ULCORNER)
            else:
                self.window.addch(dim.y0 + 1, dim.x0 + 1, curses.ACS_LTEE)
            if field_y == self.grid_h-1:
                self.window.addch(dim.y1 + 1, dim.x0 + 1, curses.ACS_LLCORNER)
            else:
                self.window.addch(dim.y1 + 1, dim.x0 + 1, curses.ACS_LTEE)
        elif field_x == self.grid_w -1:
            if field_y == 0:
                self.window.addch(dim.y0 + 1, dim.x1 + 1, curses.ACS_URCORNER)
            else:
                self.window.addch(dim.y0 + 1, dim.x1 + 1, curses.ACS_RTEE)
            if field_y == self.grid_h-1:
                self.window.addch(dim.y1 + 1, dim.x1 + 1, curses.ACS_LRCORNER)
            else:
                self.window.addch(dim.y1 + 1, dim.x1 + 1, curses.ACS_RTEE)
            if field_y == 0:
                self.window.addch(dim.y0 + 1, dim.x0 + 1, curses.ACS_TTEE)
            else:
                self.window.addch(dim.y0 + 1, dim.x0 + 1, curses.ACS_SSSS)
            if field_y == self.grid_h-1:
                self.window.addch(dim.y1 + 1, dim.x0 + 1, curses.ACS_BTEE)
            else:
                self.window.addch(dim.y1 + 1, dim.x0 + 1, curses.ACS_SSSS)
        else:
            if field_y == 0:
                self.window.addch(dim.y0 + 1, dim.x0 + 1, curses.ACS_TTEE)
            else:
                self.window.addch(dim.y0 + 1, dim.x0 + 1, curses.ACS_SSSS)
            if field_y == self.grid_h-1:
                self.window.addch(dim.y1 + 1, dim.x0 + 1, curses.ACS_BTEE)
            else:
                self.window.addch(dim.y1 + 1, dim.x0 + 1, curses.ACS_SSSS)

    def calc_dimensions(self, field_x, field_y):
        width = (self.maxx - 2) / self.grid_w
        hight = (self.maxy - 2) / self.grid_h
        startx = 1 + (width * field_x)
        starty = 1 + (hight * field_y)
        return WinDim(starty, startx, starty + hight, startx + width)


