from enum import Enum
import json
import requests

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


class FieldState(Enum):
    EMPTY = 0, "Empty"
    UBOAT = 1, "UBoat"
    MINE = 2, "Mine"
    DANGER_ZONE = 3, "Uboat Range"
    PATH = 4, "Convoi Path"
    CONVOI = 5, "Convoi Location"

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value

HIDE_DANGER_STATE = [
    FieldState.MINE,
    FieldState.CONVOI,
    FieldState.UBOAT
]

class Field:



    def __init__(self, parent, dim, default_color, path_color):
        self.window = parent.derwin(dim.lines - 1, dim.cols - 1, dim.y0+2, dim.x0+2)
        self.window.refresh()
        self.default_color = default_color
        self.path_color = path_color
        self.danger_reffs = []
        self.uboat_name = ""
        self.state = FieldState.EMPTY
        self.convoi_path = False
        self.danger_color = None

    def set_color(self, color):
        self.window.bkgd(" ", color)
        self.window.refresh()

    def toggle_convoi_path(self):
        if self.convoi_path:
            self.convoi_path = False
            self.state = FieldState.EMPTY
            self.set_color(self.default_color)
        else :
            self.convoi_path = True
            self.state = FieldState.PATH
            self.set_color(self.path_color)

    def set_convoi(self, color):
        self.set_color(color)
        self.state = FieldState.CONVOI

    def set_mine(self, color):
        self.set_color(color)
        self.state = FieldState.MINE

    def set_uboat(self, color, name):
        self.set_color(color)
        self.window.addstr(1,2, name)
        self.uboat_name = name
        self.state = FieldState.UBOAT
        self.window.refresh()

    def set_uboat_danger(self, color, name):
        self.danger_color = color
        self.danger_reffs.append(name)
        if self.state not in HIDE_DANGER_STATE:
            self.state = FieldState.DANGER_ZONE
            self.set_color(color)
        self.window.refresh()

    def set_convoi_path(self):
        self.convoi_path = True
        self.state = FieldState.PATH
        self.set_color(self.path_color)

    def check_for_danger_and_empty_field(self):
        if len(self.danger_reffs) == 0:
            self.set_color(self.default_color)
            self.state = FieldState.EMPTY
        else:
            self.state = FieldState.DANGER_ZONE
            self.set_color(self.danger_color)

    def unset_convoi_path(self):
        if self.state == FieldState.PATH:
            self.convoi_path = False
            self.check_for_danger_and_empty_field()

    def unset_convoi(self):
        if self.state == FieldState.CONVOI:
            self.check_for_danger_and_empty_field()

    def unset_mine(self):
        self.check_for_danger_and_empty_field()

    def unset_uboat(self):
        self.window.erase()
        name = self.uboat_name
        self.uboat_name = ""
        self.check_for_danger_and_empty_field()
        self.window.refresh()
        return name


    def unset_uboat_danger(self, name):
        try:
            index = self.danger_reffs.index(name)
            del self.danger_reffs[index]
            if len(self.danger_reffs) == 0 and self.state == FieldState.DANGER_ZONE:
                self.set_color(self.default_color)
                self.window.refresh()
                self.state = FieldState.EMPTY
        except:
            pass



class Grid:

    def __init__(self, window, convoi_color, mine_color, uboat_color, uboat_danger_color, path_color, default_color, preload_file=None, status_addr=None):
        self.window = window
        self.maxy, self.maxx = window.getmaxyx()
        self.grid_w = 9
        self.grid_h = 6
        self.start_x = 5
        self.start_y = self.grid_h-1
        self.convoi_x = self.start_x
        self.convoi_y = self.start_y
        self.convoi_color, self.mine_color, self.uboat_color, self.path_color = convoi_color, mine_color, uboat_color, path_color
        self.uboat_danger_color = uboat_danger_color
        self.default_color = default_color
        self.status_addr = status_addr

        self.fields = [[0 for x in range(self.grid_w)] for y in range(self.grid_h)]

        self.draw_axis()

        for field_x in range(self.grid_w):
            for field_y in range(self.grid_h):
                dim = self.calc_dimensions(field_x, field_y)
                try:
                    self.draw_border(dim, field_x, field_y)
                except:
                    pass
                self.fields[field_y][field_x] = Field(self.window, dim,
                                                      self.default_color,
                                                      path_color = self.path_color)
        if preload_file:
            self.preload(preload_file)
        else:
            (self.fields[self.convoi_y][self.convoi_x]).set_convoi_path()
            (self.fields[self.convoi_y][self.convoi_x]).set_convoi(self.convoi_color)
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

    def check_bounds(self, y , x):
        if y >= 0 and x >= 0 and y < self.grid_h and x < self.grid_w:
            return True
        else:
            False

    def move_convoi_up(self):
        self.move_convoi(self.convoi_y-1, self.convoi_x)

    def move_convoi_down(self):
        self.move_convoi(self.convoi_y+1, self.convoi_x)

    def move_convoi_left(self):
        self.move_convoi(self.convoi_y, self.convoi_x-1)

    def move_convoi_right(self):
        self.move_convoi(self.convoi_y, self.convoi_x+1)

    def move_convoi(self, y, x):
        if self.check_bounds(y, x) :
            if (self.fields[y][x]).state == FieldState.EMPTY:
                self.set_convoi(y, x)


    def set_convoi(self, y, x):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            if (self.fields[y][x]).state == FieldState.EMPTY:
                (self.fields[self.convoi_y][self.convoi_x]).unset_convoi()
                (self.fields[self.convoi_y][self.convoi_x]).set_convoi_path()
                (self.fields[y][x]).set_convoi(self.convoi_color)
                self.convoi_x = x
                self.convoi_y = y

    def set_danger(self, y, x, name):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            (self.fields[y][x]).set_uboat_danger(self.uboat_danger_color, name)

    def unset_danger(self, y, x, name):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            (self.fields[y][x]).unset_uboat_danger(name)

    def set_uboat(self, y, x, name):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            state = (self.fields[y][x]).state
            if state == FieldState.EMPTY or state == FieldState.DANGER_ZONE :
                (self.fields[y][x]).set_uboat(self.uboat_color, name)
                self.set_danger(y+1,x+1,name)
                self.set_danger(y+1,x,name)
                self.set_danger(y+1,x-1,name)
                self.set_danger(y-1,x+1,name)
                self.set_danger(y-1,x,name)
                self.set_danger(y-1,x-1,name)
                self.set_danger(y,x+1,name)
                self.set_danger(y,x-1,name)
            elif state == FieldState.UBOAT:
                old_name = (self.fields[y][x]).unset_uboat()
                self.unset_danger(y+1,x+1,old_name)
                self.unset_danger(y+1,x,old_name)
                self.unset_danger(y+1,x-1,old_name)
                self.unset_danger(y-1,x+1,old_name)
                self.unset_danger(y-1,x,old_name)
                self.unset_danger(y-1,x-1,old_name)
                self.unset_danger(y,x+1,old_name)
                self.unset_danger(y,x-1,old_name)

    def set_mine(self, y, x):
        if y >= 0 and x >= 0 and x < self.grid_w and y < self.grid_h:
            state = (self.fields[y][x]).state
            if state == FieldState.EMPTY or state == FieldState.DANGER_ZONE :
                (self.fields[y][x]).set_mine(self.mine_color)
            elif state == FieldState.MINE:
                (self.fields[y][x]).unset_mine()


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

    def reset_convoi(self):
        self.set_convoi(self.start_y, self.start_x)
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                (self.fields[y][x]).unset_convoi_path()
                (self.fields[y][x]).unset_convoi()
                (self.fields[y][x]).unset_convoi_path()
        (self.fields[self.convoi_y][self.convoi_x]).set_convoi(self.convoi_color)

    def serialize(self, file_name):
        data = {}
        for x in range(self.grid_w):
            data[x] = {}
            for y in range(self.grid_h):
                data[x][y] = {}
                state = int((self.fields[y][x]).state)
                data[x][y]["state"] = state
                if state == int(FieldState.UBOAT):
                    data[x][y]["name"] = (self.fields[y][x]).uboat_name
        with open(file_name, 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)
        if self.status_addr is not None:
            requests.post(self.status_addr, data=json.dumps(data))


    def preload(self, preload_file=None, data_input=None):
        if preload_file:
            with open(preload_file, 'r') as f:
                data = json.load(f)
        elif data_input:
            data = data_input
        else:
            return
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                state = data[str(x)][str(y)]["state"]
                if state == int(FieldState.UBOAT):
                    name = data[str(x)][str(y)]["name"]
                    self.set_uboat(y,x,name)
                elif state == int(FieldState.MINE):
                    self.set_mine(y,x)
                elif state == int(FieldState.PATH):
                    (self.fields[y][x]).set_convoi_path()
                elif state == int(FieldState.CONVOI):
                    self.set_convoi(y, x)





