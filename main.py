import csv
import time
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

start_time = time.time()
hostName = "localhost"
hostPort = 9000

i = 0
cache = {}
with open("F:\Работа\Поиск работы 2020\sorted_recommends.csv", encoding='utf-8') as r_file:
    file_reader = csv.reader(r_file, delimiter=",")
    for index, row in enumerate(file_reader):
        i += 1
        if row[0] not in cache:
            cache[row[0]] = f'{row[1]} {row[2]}'
        else:
            cache[row[0]] += f' {row[1]} {row[2]}'
        # if i > 1000:
        #     break
print(f"Finish {time.time() - start_time:.2f} сек")


class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if '/get_recomends/' in self.path:
            list_parts_from_url = self.path.split('/')
            self._set_headers()
            self.wfile.write(bytes(json.dumps({list_parts_from_url[2]: cache.get(list_parts_from_url[2],
                                                                                 'No such product')}), "utf-8"))
        if self.path == '/favicon.ico':
            pass


myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
