import http
import http.server
import urllib.request

import requests


class Proxy(http.server.SimpleHTTPRequestHandler):
    base = 'http://issues.127.1.0.1.nip.io:8080'
    
    def __init__(self, *args, **kwargs):
        super(Proxy, self).__init__(*args, directory='src', **kwargs)

    def do_GET(self):
        if self.path.startswith('/api'):
            print('>', self.base + self.path)
            # self.copyfile(urllib.request.urlopen(self.base + self.path), self.wfile)
            response = requests.get(self.base + self.path)
            self.send_response(response.status_code, 'OK')
            for k, v in response.headers.items():
                if k.lower() != 'server' and k.lower() != 'content-encoding':
                    self.send_header(k, v)
            self.flush_headers()
            self.wfile.write(b'\r\n' + response.content)
        else:
            super().do_GET()

    def do_POST(self):
        body = self.rfile.read(int(self.headers['Content-Length']))
        headers = {k: v for k, v in self.headers.items() if k != 'Host'}
        response = requests.post(self.base + self.path, data=body, headers=headers)
        self.send_response(response.status_code, 'OK')
        for k, v in response.headers.items():
            if k.lower() != 'server' and k.lower() != 'content-encoding':
                self.send_header(k, v)
        self.flush_headers()
        self.wfile.write(b'\r\n' + response.content)


server = http.server.HTTPServer(('0.0.0.0', 8000), Proxy)
server.serve_forever()
