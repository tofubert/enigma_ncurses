import logging

from curses.textpad import rectangle
import curses

class WinDim:
    def __init__(self, y0, x0, y1, x1):
        self.x0 = int(x0)
        self.y0 = int(y0)
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.cols = int(x1 - x0)
        self.lines = int(y1 - y0)


class Field:
    def __init__(self, parent, dim, default_color):
        self.window = parent.derwin(dim.lines - 1, dim.cols - 1, dim.y0+2, dim.x0+2)
        # self.window.bkgd("~")
        self.window.refresh()
        self.default_color = default_color
        self.danger_reffs = []
        self.uboat_name = ""

    def set_color(self, color):
        self.window.bkgd(" ", color)
        self.window.refresh()

    def set_convoi(self, color):
        self.set_color(color)

    def set_mine(self, color):
        self.set_color(color)


    def set_uboat(self, color, name):
        self.set_color(color)
        self.window.addstr(1,0, name)
        self.uboat_name = name
        self.window.refresh()

    def set_uboat_danger(self, color, name):
        self.set_color(color)
        self.danger_reffs.append(name)
        self.window.refresh()

    def unset_convoi(self):
        self.set_color(self.default_color)

    def unset_mine(self):
        self.set_color(self.default_color)

    def unset_uboat(self, color, name):
        self.window.erase()
        self.set_color(self.default_color)
        self.uboat_name = ""
        self.window.refresh()

    def unset_uboat_danger(self, name):
        try:
            index = self.danger_reffs.index(name)
            del self.danger_reffs[index]
            if len(self.danger_reffs) == 0:
                self.set_color(self.default_color)
                self.window.refresh()
        except:
            pass


class Grid:

    def __init__(self, window, convoi_color, mine_color, uboat_color, uboat_danger_color, path_color, default_color):
        self.window = window
        self.maxy, self.maxx = window.getmaxyx()
        self.grid_w = 9
        self.grid_h = 6
        self.convoi_color, self.mine_color, self.uboat_color, self.path_color = convoi_color, mine_color, uboat_color, path_color
        self.uboat_danger_color = uboat_danger_color
        self.default_color = default_color

        self.fields = [[0 for x in range(self.grid_w)] for y in range(self.grid_h)]

        self.draw_axis()

        for field_x in range(self.grid_w):
            for field_y in range(self.grid_h):
                dim = self.calc_dimensions(field_x, field_y)
                try:
                    self.draw_border(dim, field_x, field_y)
                except:
                    pass
                self.fields[field_y][field_x] = Field(self.window, dim, self.default_color)
        self.set_convoi(3,0)
        self.set_uboat(0,0, "U110")
        self.set_uboat(1,4, "U888")
        legend = 0
        uboat_legent = "UBOAT"
        uboat_danger_legent = "UBOAT_RANGE"
        mine_legent = "MINE"
        convoi_legent = "CONVOI"
        self.window.addstr(0,legend,uboat_legent, self.uboat_color)
        legend = legend + len(uboat_legent) + 1

        self.window.addstr(0,legend,uboat_danger_legent, self.uboat_danger_color)
        legend = legend + len(uboat_danger_legent) + 1

        self.window.addstr(0,legend,mine_legent, self.mine_color)
        legend = legend + len(mine_legent) + 1

        self.window.addstr(0,legend,convoi_legent, self.convoi_color)
        legend = legend + len(convoi_legent) + 1

        self.window.refresh()

    def set_convoi(self, y, x):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            (self.fields[y][x]).set_convoi(self.convoi_color)

    def set_uboat(self, y, x, name):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            (self.fields[y][x]).set_uboat(self.uboat_color, name)


    def draw_axis(self):
        width = int((self.maxx - 2) / self.grid_w)
        hight = int((self.maxy - 2) / self.grid_h)

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
        width = int((self.maxx - 2) / (self.grid_w))
        hight = int((self.maxy - 2) / (self.grid_h))
        startx = 1 + (width * field_x)
        starty = 1 + (hight * field_y)
        return WinDim(starty, startx, starty + hight, startx + width)


