from RPi import GPIO
from threading import Thread, Lock
from time import sleep


def empty_callback(*_, **__):
    pass


class Switch:
    def __init__(self, input_pins, callback=empty_callback, debounce_time=0.3):
        self.input_pins = input_pins
        self.callback = callback
        self.debounce_time = debounce_time
        self.handler_lock = Lock()
        self.setup_pins()

    def setup_pins(self):
        for pin in self.input_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, edge=GPIO.BOTH, callback=self.handler)

    def handler(self, _):
        Thread(target=self.singleton_handler).start()
    
    def singleton_handler(self):
        if not self.handler_lock.acquire(blocking=False):
            return
        
        sleep(self.debounce_time)
        self.callback(self.get_switch_value())
        self.handler_lock.release()

    def get_switch_value(self):
        switch_value = 0
        for exp, pin in enumerate(self.input_pins):
            switch_value += GPIO.input(pin) * 2**exp
        return switch_value

    def __del__(self):
        self.handler_lock.acquire()
        for pin in self.input_pins:
            GPIO.remove_event_detect(pin)


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

