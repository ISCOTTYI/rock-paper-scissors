from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

PORT = 8000

class handler(SimpleHTTPRequestHandler):
    position_data = {
        "x1": 100,
        "y1": 100,
        "x2": 300,
        "y2": 300,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.extensions_map.update({
        #     '.js': 'text/javascript',
        #     '.css': 'text/css'
        # })

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as f:
                contents = f.read()
                self.wfile.write(contents)
        elif self.path.endswith('.js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/javascript')
            self.end_headers()
            with open(self.path[1:], 'rb') as f:
                contents = f.read()
                self.wfile.write(contents)
        elif self.path.endswith('.css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open(self.path[1:], 'rb') as f:
                contents = f.read()
                self.wfile.write(contents)
        elif self.path == '/init':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            message = "Init"
            self.wfile.write(bytes(message, "utf8"))
        elif self.path == '/state':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            # message = "State"
            print("--- GET data is", handler.position_data)
            print('--- GET type is', type(handler.position_data))
            self.wfile.write(
                bytes(json.dumps(handler.position_data), "utf8")
            )
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "Error: Page not found."
            self.wfile.write(bytes(message, "utf8"))
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = body.decode()
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        print(f'--- POST data {data}')
        print(f'--- POST type is {type(data)}')
        handler.position_data = json.loads(data)
        print('--- after POST position_data is', handler.position_data)
        print(f'--- after POST type is {type(handler.position_data)}')
        self.wfile.write(bytes(data, "utf8"))

with HTTPServer(('localhost', PORT), handler) as server:
    print(f'Serving on http://localhost:{PORT}')
    server.serve_forever()