import string
import random
from curses.textpad import rectangle


def random_generator(size=15, chars=string.ascii_uppercase + string.digits, padsize=15):
    str_size = random.randint(1, size)
    ret = ''.join(random.choice(chars) for x in range(str_size))
    ret = ret + (" " * (padsize-str_size))
    return ret

class Morse():
    def __init__(self, window, status_color, receive_array_color, receive_array_strings, volume_color, speed_color, backround):
        y = 0
        self.window = window
        self.backround_color = backround
        self.maxy, self.maxx = window.getmaxyx()
        self.speed_color = speed_color
        self.volume_color = volume_color
        self.receive_array_color = receive_array_color
        self.receive_array_strings = receive_array_strings
        self.receive_index =0
        self.speed = 0
        self.volume = 0


        window.addstr(y ,0, "MORSE CODE SECTION")
        y = y+ 2

        window.addstr(y, 0, "SEND VS RECEIVE")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.send_receive_y = y + 2
        self.toggle_send_receive()
        y = y + 4

        window.addstr(y, 0, "STATUS")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.status_y = y + 2
        self.update_status(status_color)
        y = y + 4

        window.addstr(y, 0, "SPEED")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.speed_y = y + 2
        self.set_speed(1)
        y = y + 4

        window.addstr(y, 0, "VOLUME")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.volume_y = y + 2
        self.set_volume((self.maxx-2)/2)
        y = y + 4

    def update_status(self, color=None):
        if color:
            self.status_color = color
        status = random_generator(self.maxx - 2, padsize=self.maxx - 2)
        self.window.addnstr(self.status_y, 1, status, self.maxx - 2, self.status_color)
        self.window.refresh()

    def set_volume(self, volume):
        self.window.addnstr(self.volume_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.volume_y, 1, " " * volume, self.maxx - 2, self.volume_color)
        self.window.refresh()
        self.volume = volume

    def increase_volume(self):
        if self.volume +1 <= self.maxx-2:
            self.volume = self.volume+1
        self.window.addnstr(self.volume_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.volume_y, 1, " " * self.volume, self.maxx - 2, self.volume_color)
        self.window.refresh()

    def decrease_volume(self):
        if self.volume -1 >= 0:
            self.volume = self.volume-1
        self.window.addnstr(self.volume_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.volume_y, 1, " " * self.volume, self.maxx - 2, self.volume_color)
        self.window.refresh()

    def set_speed(self, speed):
        self.window.addnstr(self.speed_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.speed_y, 1, " " * speed, self.maxx - 2, self.speed_color)
        self.window.refresh()
        self.speed = speed

    def increase_speed(self):
        if self.speed +1 <= self.maxx-2:
            self.speed = self.speed+1
        self.window.addnstr(self.speed_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.speed_y, 1, " " * self.speed, self.maxx - 2, self.speed_color)
        self.window.refresh()

    def decrease_speed(self):
        if self.speed -1 >= 0:
            self.speed = self.speed-1
        self.window.addnstr(self.speed_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.speed_y, 1, " " * self.speed, self.maxx - 2, self.speed_color)
        self.window.refresh()

    def update_send_receive(self, color, string):
        self.window.addnstr(self.send_receive_y, 1, string + (" " * self.maxx), self.maxx - 2, color)
        self.window.refresh()

    def toggle_send_receive(self):
        if self.receive_index == 0:
            self.receive_index = 1
        else:
            self.receive_index = 0
        self.window.addnstr(self.send_receive_y, 1,
                            self.receive_array_strings[self.receive_index] + (" " * self.maxx),
                            self.maxx - 2,
                            self.receive_array_color[self.receive_index])
        self.window.refresh()