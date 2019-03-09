
class Menu:

    SHOW = True
    NOSHOW = False
    def __init__(self, window, morse, grid, stdscr):
        self.window = window
        self.morse = morse
        self.grid = grid
        self.stdscr = stdscr
        self.state = "Main"
        self.key = " "
        self.hidden_state = 0
        self.doexit = False
        self.maxy, self.maxx = window.getmaxyx()
        self.state_machine = {
            "Morse": {
                "+": (self.morse.increase_volume, "Morse", "increase volume", self.SHOW),
                "-": (self.morse.decrease_volume, "Morse", "decrease volume", self.SHOW),
                "9": (self.morse.increase_speed, "Morse", "increase speed", self.SHOW),
                "6": (self.morse.decrease_speed, "Morse", "decrease speed", self.SHOW),
                "0": (self.morse.toggle_send_receive, "Morse", "Switch Send/Receive", self.SHOW),
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),
            },
            "Main" : {
                "1": (self.no_action, "Morse", "Enter the Morse Menu", self.SHOW),
                "2": (self.no_action, "Grid", "Enter the Grid Menu", self.SHOW),
                "0": (self.hidden_check, "Main", "Enter a Admin Code", self.NOSHOW),
                "7": (self.hidden_check, "Main", "Enter a Admin Code", self.NOSHOW),
                "8": (self.hidden_check, "Main", "Enter a Admin Code", self.NOSHOW),
                "9": (self.hidden_check, "Main", "Enter a Admin Code", self.NOSHOW),
                "q": (self.exit, "Main", "QUIT", self.NOSHOW),
            },
            "Grid" : {
                "1" : (self.no_action, "UBoat Place", "(Un)Place UBOAT", self.SHOW),
                "3": (self.no_action, "Mine Place", "(Un)Place Mine", self.SHOW),
                "8": (self.no_action, "Grid", "Move Convoi Up", self.SHOW),
                "2": (self.no_action, "Grid", "Move Convoi Down", self.SHOW),
                "4": (self.no_action, "Grid", "Move Convoi Left", self.SHOW),
                "6": (self.no_action, "Grid", "Move Convoi Right", self.SHOW),
                "a": (self.no_action, "Grid", "SUBMIT", self.SHOW),
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),

            },
            "UBoat Place" : {
                "\n": (self.no_action, "Grid", "Go the Grid Menu", self.SHOW),
            },
            "Mine Place" : {
                "\n": (self.no_action, "Grid", "Go the Grid Menu", self.SHOW),
            },
            "Hidden" : {
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),
                "q": (self.exit, "Main", "Go the main Menu", self.SHOW),

            }
        }

    def run(self):
        self.update_menu()
        while not self.doexit:
            try:
                self.key = self.stdscr.getkey()
            except:
                self.key = " "
            self.morse.update_status()
            func, self.state, _, show = self.state_machine[self.state].get(self.key, (self.no_action, self.state, "", self.SHOW))
            func()
            self.update_menu()

    def update_menu(self):
        self.window.erase()
        self.window.addstr(0,0, " Current Menu is {}".format(self.state))
        index = 0
        index_y = 1
        state_options = self.state_machine[self.state]
        for key in state_options:
            _, _ , explenation, show = self.state_machine[self.state].get(key, (self.no_action, self.state, ""))
            if show:
                if key == "\n":
                    key = "Enter"
                info = key + " -> " + explenation + " | "
                if index + len(info) >= self.maxx:
                    index_y += 1
                    index = 0
                self.window.addstr(index_y, index, info)
                index += len(info)
        self.window.refresh()

    def hidden_check(self):
        if self.key == "0":
            self.hidden_state += 1
        elif self.key == "7" and self.hidden_state == 3:
            self.hidden_state += 1
        elif self.key == "9" and self.hidden_state == 4:
            self.hidden_state += 1
        elif self.key == "8" and self.hidden_state == 5:
            self.hidden_state = 0
            self.state = "Hidden"

    def no_action(self):
        self.hidden_state = 0

    def exit(self):
        self.doexit = True
