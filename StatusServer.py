from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from io import BytesIO

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        data = json.loads(body)
        print(json.dumps(data, indent=2))
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('192.168.1.2', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
