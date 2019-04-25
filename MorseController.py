import sys
import string
import random
from curses.textpad import rectangle

from multiprocessing import Process

try:
    from morse.game_engine import MorseCodeGameEngine
except:
    # silently ignore the failure. this one's for Jan
    print('do nothing')


def random_generator(size=15, chars=string.ascii_uppercase + string.digits, padsize=15):
    str_size = random.randint(1, size)
    ret = ''.join(random.choice(chars) for x in range(str_size))
    ret = ret + (" " * (padsize-str_size))
    return ret


class MorseController():
    def __init__(self, window, status_color, receive_array_color, receive_array_strings, volume_color, speed_color, backround):
        y = 0
        self.window = window
        self.backround_color = backround
        self.maxy, self.maxx = window.getmaxyx()
        self.speed_color = speed_color
        self.volume_color = volume_color
        self.receive_array_color = receive_array_color
        self.receive_array_strings = receive_array_strings
        self.receive_index = 0
        self.dial_increments = 8

        window.addstr(y ,0, "MORSE CODE SECTION")
        y = y+ 2

        window.addstr(y, 0, "SEND VS RECEIVE")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.send_receive_y = y + 2
        self.update_send_receive_wrapper(1)
        y = y + 4

        window.addstr(y, 0, "SECURE LINK")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.status_y = y + 2
        self.update_status(status_color)
        y = y + 4

        window.addstr(y, 0, "SPEED 0 - {}".format(self.dial_increments-1))
        rectangle(window, y + 1, 0, y + 3, self.dial_increments)
        self.speed_y = y + 2
        y = y + 4

        window.addstr(y, 0, "VOLUME")
        rectangle(window, y + 1, 0, y + 3, self.dial_increments)
        self.volume_y = y + 2
        y = y + 4

        if "morse.game_engine" in sys.modules:
            self.mcge = MorseCodeGameEngine(speeds=8, volumes=8,
                                            set_speed_callback=self.set_speed,
                                            set_volume_callback=self.set_volume,
                                            set_send_receive_callback=self.update_send_receive_wrapper)
            # thread me
            self.mcge.start()
        
    def update_status(self, color=None):
        if color:
            self.status_color = color
        status = random_generator(self.maxx - 2, padsize=self.maxx - 2)
        self.window.addnstr(self.status_y, 1, status, self.maxx - 2, self.status_color)
        self.window.refresh()

    def set_volume(self, volume):
        self.window.addnstr(self.volume_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.volume_y, 1, " " * int(volume), self.maxx - 2, self.volume_color)
        self.window.refresh()

    def increase_volume(self):
        self.mcge.increase_volume()

    def decrease_volume(self):
        self.mcge.decrease_volume()

    def set_speed(self, speed):
        self.window.addnstr(self.speed_y, 1, " " * (self.maxx - 2), self.maxx - 2, self.backround_color)
        self.window.addnstr(self.speed_y, 1, " " * speed, self.maxx - 2, self.speed_color)
        self.window.refresh()
        
    def increase_speed(self):
        self.mcge.increase_speed()

    def decrease_speed(self):
        self.mcge.decrease_speed()

    def update_send_receive_wrapper(self, receive):
        self.receive_index = receive
        self.window.addnstr(self.send_receive_y, 1,
                            self.receive_array_strings[self.receive_index] + (" " * self.maxx),
                            self.maxx - 2,
                            self.receive_array_color[self.receive_index])
        self.update_send_receive(self.receive_array_color[self.receive_index],
                                 self.receive_array_strings[self.receive_index])

    def update_send_receive(self, color, string):
        self.window.addnstr(self.send_receive_y, 1, string + (" " * self.maxx), self.maxx - 2, color)
        self.window.refresh()

    def toggle_send_receive(self):
        self.mcge.toggle_txrx_mode()

