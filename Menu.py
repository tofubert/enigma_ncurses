from time import sleep
from curses.textpad import Textbox, rectangle

class Menu:

    SHOW = True
    NOSHOW = False

    def __init__(self, window, morse, grid, status_server, stdscr, name="Test"):
        self.window = window
        self.morse = morse
        self.grid = grid
        self.status_server = status_server
        self.stdscr = stdscr
        self.name = name
        self.state = "Main"
        self.key = " "
        self.hidden_state = 0
        self.doexit = False
        self.maxy, self.maxx = window.getmaxyx()
        self.state_machine = {
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
                "1" : (self.no_action, "UBoat Place Y Axis", "(Un)Place UBOAT", self.SHOW),
                "3": (self.no_action, "Mine Place Y Axis", "(Un)Place Mine", self.SHOW),
                "8": (self.grid.move_convoi_up, "Grid", "Move Convoi Up", self.SHOW),
                "2": (self.grid.move_convoi_down, "Grid", "Move Convoi Down", self.SHOW),
                "4": (self.grid.move_convoi_left, "Grid", "Move Convoi Left", self.SHOW),
                "6": (self.grid.move_convoi_right, "Grid", "Move Convoi Right", self.SHOW),
                "0": (self.reset_convoi, "Grid", "Reset Convoi path", self.SHOW),
                "a": (self.submit, "Grid", "SUBMIT", self.SHOW),
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),

            },
            "UBoat Place Y Axis" : {
                "1": (self.stash_key, "UBoat Place X Axis", "A", self.SHOW),
                "2": (self.stash_key, "UBoat Place X Axis", "B", self.SHOW),
                "3": (self.stash_key, "UBoat Place X Axis", "C", self.SHOW),
                "4": (self.stash_key, "UBoat Place X Axis", "D", self.SHOW),
                "5": (self.stash_key, "UBoat Place X Axis", "E", self.SHOW),
                "6": (self.stash_key, "UBoat Place X Axis", "F", self.SHOW),
                "7": (self.stash_key, "UBoat Place X Axis", "G", self.SHOW),
                "8": (self.stash_key, "UBoat Place X Axis", "H", self.SHOW),
                "\n": (self.no_action, "Grid", "Go the Grid Menu", self.SHOW),
            },
            "UBoat Place X Axis": {
                "1": (self.place_Uboat, "Grid", "AA", self.SHOW),
                "2": (self.place_Uboat, "Grid", "BB", self.SHOW),
                "3": (self.place_Uboat, "Grid", "CC", self.SHOW),
                "4": (self.place_Uboat, "Grid", "DD", self.SHOW),
                "5": (self.place_Uboat, "Grid", "EE", self.SHOW),
                "6": (self.place_Uboat, "Grid", "FF", self.SHOW),
                "7": (self.place_Uboat, "Grid", "GG", self.SHOW),
                "8": (self.place_Uboat, "Grid", "HH", self.SHOW),
                "9": (self.place_Uboat, "Grid", "II", self.SHOW),
                "\n": (self.no_action, "Grid", "Go the Grid Menu", self.SHOW),
            },
            "Mine Place Y Axis": {
                "1": (self.stash_key, "Mine Place X Axis", "A", self.SHOW),
                "2": (self.stash_key, "Mine Place X Axis", "B", self.SHOW),
                "3": (self.stash_key, "Mine Place X Axis", "C", self.SHOW),
                "4": (self.stash_key, "Mine Place X Axis", "D", self.SHOW),
                "5": (self.stash_key, "Mine Place X Axis", "E", self.SHOW),
                "6": (self.stash_key, "Mine Place X Axis", "F", self.SHOW),
                "7": (self.stash_key, "Mine Place X Axis", "G", self.SHOW),
                "8": (self.stash_key, "Mine Place X Axis", "H", self.SHOW),
                "\n": (self.no_action, "Grid", "Go the Grid Menu", self.SHOW),
            },
            "Mine Place X Axis": {
                "1": (self.place_Mine, "Grid", "AA", self.SHOW),
                "2": (self.place_Mine, "Grid", "BB", self.SHOW),
                "3": (self.place_Mine, "Grid", "CC", self.SHOW),
                "4": (self.place_Mine, "Grid", "DD", self.SHOW),
                "5": (self.place_Mine, "Grid", "EE", self.SHOW),
                "6": (self.place_Mine, "Grid", "FF", self.SHOW),
                "7": (self.place_Mine, "Grid", "GG", self.SHOW),
                "8": (self.place_Mine, "Grid", "HH", self.SHOW),
                "9": (self.place_Mine, "Grid", "II", self.SHOW),
                "\n": (self.no_action, "Grid", "Go the Grid Menu", self.SHOW),
            },
            "Hidden" : {
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),
                "q": (self.exit, "Main", "Close Game ALL PROGRESS GONE!", self.SHOW),

            }
        }

        if self.morse is not None:
            self.state_machine["Morse"] = {
                "+": (self.morse.increase_volume, "Morse", "increase volume", self.SHOW),
                "-": (self.morse.decrease_volume, "Morse", "decrease volume", self.SHOW),
                "9": (self.morse.increase_speed, "Morse", "increase speed", self.SHOW),
                "6": (self.morse.decrease_speed, "Morse", "decrease speed", self.SHOW),
                "0": (self.morse.toggle_send_receive, "Morse", "Switch Send/Receive", self.SHOW),
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),
            }
        else :
            self.state_machine["Selection"] = {
                "1": (self.status_server.team1, "Selection", "Team 1", self.SHOW),
                "2": (self.status_server.team2, "Selection", "Team 2", self.SHOW),
                "3": (self.status_server.team3, "Selection", "Team 3", self.SHOW),
                "4": (self.status_server.solution, "Selection", "Solution", self.SHOW),
                "\n": (self.no_action, "Main", "Go the main Menu", self.SHOW),
            }
            self.state_machine["Main"]["1"] = (self.no_action, "Selection", "Select a Team", self.SHOW)
            del self.state_machine["Main"]["2"]

    def run(self):
        self.update_menu()
        while not self.doexit:
            try:
                self.key = self.stdscr.getkey()
            except:
                self.key = " "
            func, self.state, _, show = self.state_machine[self.state].get(self.key, (self.no_action, self.state, "", self.SHOW))
            try:
                func()
            except:
                pass
            if self.morse is not None:
                self.morse.update_status()
                if self.key != " ":
                    self.grid.serialize(self.name)
            self.update_menu()
            sleep(0.200)

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
        if self.key == "0" and self.hidden_state < 3:
            self.hidden_state += 1
        elif self.key == "7" and self.hidden_state == 3:
            self.hidden_state += 1
        elif self.key == "9" and self.hidden_state == 4:
            self.hidden_state += 1
        elif self.key == "8" and self.hidden_state == 5:
            self.hidden_state = 0
            self.state = "Hidden"
        else:
            self.hidden_state = 0

    def stash_key(self):
        self.stashed_key = self.key

    def place_Mine(self):
        y = int(self.stashed_key)-1
        x = int(self.key)-1
        self.grid.set_mine(y, x)

    def place_Uboat(self):
        y = int(self.stashed_key) - 1
        x = int(self.key) - 1
        message = "U"
        self.window.erase()
        self.window.addstr(0, 0, " Current Menu is {}. Type uboat number and hit Enter when done.".format(self.state))
        self.window.refresh()
        while self.key != "\n":
            try:
                self.key = self.stdscr.getkey()
            except:
                self.key = " "
            self.morse.update_status()
            if self.key.isdigit():
                message += self.key
            self.window.erase()
            self.window.addstr(0, 0,
                               " Current Menu is {}. Type uboat number and hit Enter when done.".format(self.state))
            self.window.addstr(1, 0, "UBoat Number is: " + message)
            self.window.refresh()
            sleep(0.05)
        if message != "U":
            self.grid.set_uboat(y, x, message)

    def reset_convoi(self):
        self.grid.reset_convoi()
        self.grid.reset_convoi()

    def submit(self):
        self.grid.serialize("foobar")

    def no_action(self):
        self.hidden_state = 0

    def exit(self):
        self.doexit = True
