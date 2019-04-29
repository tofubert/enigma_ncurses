import sys
import string
import random
from curses.textpad import rectangle

from multiprocessing import Process

try:
    from morse.game_engine import MorseCodeGameEngine
    from switches import Switch
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
        self.dial_increments = 8
        self.maxy, self.maxx = window.getmaxyx()
        self.speed_color = speed_color
        self.volume_color = volume_color
        self.receive_array_color = receive_array_color
        self.receive_array_strings = receive_array_strings
        self.receive_index = 0
        self.status_color = backround

        window.addstr(y ,0, "MORSE CODE SECTION")
        y = y+ 2

        window.addstr(y, 0, "SEND VS RECEIVE")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.send_receive_y = y + 2
        self.ui_update_send_receive_wrapper(1)
        y = y + 4

        window.addstr(y, 0, "SECURE LINK")
        rectangle(window, y + 1, 0, y + 3, self.maxx - 1)
        self.status_y = y + 2
        self.update_status(backround)
        y = y + 4

        window.addstr(y, 0, "SPEED 1 - {}".format(self.dial_increments))
        rectangle(window, y + 1, 0, y + 3, self.dial_increments)
        self.speed_y = y + 2
        y = y + 4

        window.addstr(y, 0, "VOLUME")
        rectangle(window, y + 1, 0, y + 3, self.dial_increments)
        self.volume_y = y + 2
        y = y + 4

        if "switches" in sys.modules:
            self.mcge = MorseCodeGameEngine(speeds=8, volumes=8,
                                            set_speed_callback=self.ui_set_speed,
                                            set_volume_callback=self.ui_set_volume,
                                            set_send_receive_callback=self.ui_update_send_receive_wrapper)

            speed_switch = Switch([22, 27, 17], self.mcge.set_speed)
            self.mcge.set_speed(speed_switch.get_switch_value())
            volume_switch = Switch([19, 13, 6], self.mcge.set_volume)
            self.mcge.set_volume(volume_switch.get_switch_value())

            # thread me
            self.mcge.start()
        
    def update_status(self, color=None):
        if color:
            self.status_color = color
        status = random_generator(self.maxx - 2, padsize=self.maxx - 2)
        self.window.addnstr(self.status_y, 1, status, self.maxx - 2, self.status_color)
        self.window.refresh()

    def ui_set_volume(self, volume):
        self.window.addnstr(self.volume_y, 1, " " * (self.dial_increments - 1), self.dial_increments - 1, self.backround_color)
        self.window.addnstr(self.volume_y, 1, " " * int(volume), self.dial_increments - 1, self.volume_color)
        self.window.refresh()

    def increase_volume(self):
        self.mcge.increase_volume()

    def decrease_volume(self):
        self.mcge.decrease_volume()

    def ui_toggle_status(self, sound=False):
        if sound:
            self.update_status(self.status_color)
        else:
            self.update_status(self.backround_color)

    def ui_set_speed(self, speed):
        self.window.addnstr(self.speed_y, 1, " " * (self.dial_increments - 1), self.dial_increments - 1, self.backround_color)
        self.window.addnstr(self.speed_y, 1, " " * speed, self.dial_increments - 1, self.speed_color)
        self.window.refresh()
        
    def increase_speed(self):
        self.mcge.increase_speed()

    def decrease_speed(self):
        self.mcge.decrease_speed()

    def ui_update_send_receive_wrapper(self, receive):
        self.receive_index = receive
        self.window.addnstr(self.send_receive_y, 1,
                            self.receive_array_strings[self.receive_index] + (" " * self.maxx),
                            self.maxx - 2,
                            self.receive_array_color[self.receive_index])
        self.ui_update_send_receive(self.receive_array_color[self.receive_index],
                                 self.receive_array_strings[self.receive_index])

    def ui_update_send_receive(self, color, string):
        self.window.addnstr(self.send_receive_y, 1, string + (" " * self.maxx), self.maxx - 2, color)
        self.window.refresh()

    def toggle_send_receive(self):
        self.mcge.toggle_txrx_mode()

