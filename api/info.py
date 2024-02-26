from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)
        print(urlparse(self.path))
        print(urlparse(self.path).query)
        print(parse_qs(urlparse(self.path).query))
        query = parse_qs(urlparse(self.path).query)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps(query)
        self.wfile.write(response.encode('utf-8'))
        return
