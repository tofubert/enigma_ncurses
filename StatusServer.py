from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from threading import Thread
from queue import Queue

TEAM1 = "UNIT1"
TEAM2 = "UNIT2"
TEAM3 = "UNIT3"
SOLUTION = "SOLUTION"

class StatusServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        data = json.loads(body.decode("utf-8"))
        if self.server.callback is not None:
            self.server.callback(data)

    def log_message(self, format, *args, **kwargs):
        pass


class StatusServerThread(Thread):
    def __init__(self, address, datacallback,  port=8000):
        super(StatusServerThread, self).__init__()
        self.httpd = HTTPServer((address, port), StatusServerHandler)
        self.httpd.callback = datacallback
        self.callback = datacallback

    def run(self):
        self.httpd.serve_forever()

class StatusServer:
    def __init__(self, address, grid, sidewindow, highlght_color, default_color, solution, port=8000):
        self.address = address
        self.port = port
        self.grid = grid
        self.sidewindow = sidewindow
        self.highlght_color = highlght_color
        self.default_color = default_color
        self.data = {}
        with open(solution, 'r') as f:
            solution_data = json.load(f)
        self.data[SOLUTION] = solution_data
        self.current = ""
        self.server_thread = StatusServerThread(self.address, self.handle_data, self.port)
        self.server_thread.start()
        self.queue = Queue(maxsize=0)

    def handle_data(self, data):
        self.queue.put(data)

    def sort_data(self):
        while not self.queue.empty():
            data = self.queue.get(block=False, timeout=0.05)
            self.data[data["name"]] = data
            self.update_teams(self.current)

    def team1(self):
        self.sort_data()
        self.grid.preload(data_input=self.data[TEAM1])
        self.current = TEAM1
        self.update_teams(self.current)


    def team2(self):
        self.sort_data()
        self.grid.preload(data_input=self.data[TEAM2])
        self.current = TEAM2
        self.update_teams(self.current)

    def team3(self):
        self.sort_data()
        self.grid.preload(data_input=self.data[TEAM3])
        self.current = TEAM3
        self.update_teams(self.current)

    def solution(self):
        self.sort_data()
        self.grid.preload(data_input=self.data[SOLUTION])
        self.current = SOLUTION
        self.update_teams(self.current)

    def update_teams(self, highlight=""):
        self.sort_data()
        self.sidewindow.clear()
        self.sidewindow.bkgd(" ", self.default_color)
        count = 1
        for name in self.data.keys():
            if( name == highlight):
                self.sidewindow.addstr(count, 0, "Team: " + name, self.highlght_color)
            else:
                self.sidewindow.addstr(count, 0, "Team: " + name, self.default_color)
            count += 1
        self.sidewindow.refresh()
