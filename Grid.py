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

class Field():

    def __init__(self, parent, dim):
        # self.window = parent.subwin(dim.lines, dim.cols, dim.y0, dim.x0)
        pass

class Grid():

    def __init__(self, window):
        self.window = window
        self.maxy, self.maxx = window.getmaxyx()
        self.grid_w = 8
        self.grid_h = 6

        self.fields = [[0 for x in range(self.grid_w)] for y in range(self.grid_h)]
        for field_x in range(self.grid_w):
            for field_y in range(self.grid_h):
                dim = self.calc_dimensions(field_x, field_y)
                self.draw_border(dim)
                self.fields[field_y][field_x] = Field(self.window, dim)
        self.window.refresh()

    def draw_border(self, dim):
        rectangle(self.window, dim.y0+1, dim.x0+1, dim.y1+1, dim.x1+1)
        self.window.addch(dim.y0+1, dim.x0+1, curses.ACS_SSSS)
        self.window.addch(dim.y1+1, dim.x0+1, curses.ACS_SSSS)
        self.window.addch(dim.y1+1, dim.x1+1, curses.ACS_SSSS)
        self.window.addch(dim.y0+1, dim.x1+1, curses.ACS_SSSS)

    def calc_dimensions(self, field_x, field_y):
        width = (self.maxx - 2) / self.grid_w
        hight = (self.maxy - 2) / self.grid_h
        startx = (width * field_x)
        starty = (hight * field_y)
        return WinDim(starty, startx, starty + hight, startx + width)


