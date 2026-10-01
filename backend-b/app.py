from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):

    def _send(self, code, body, extra_headers=None):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-Backend', 'B')
        self.send_header('Cache-Control', 'max-age=60')

        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)

        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        if self.path == '/':
            self._send(200, {"message": "Backend B is running"})

        elif self.path == '/api/status':
            self._send(200, {"backend": "B", "status": "ok"})

        else:
            self._send(404, {"error": "not found"})


if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 3002), Handler)
    print("Backend B listening on port 3002")
    server.serve_forever()
