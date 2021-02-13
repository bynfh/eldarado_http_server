from http.server import HTTPServer, BaseHTTPRequestHandler


class CustomRequest(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def _html(self, message):
        """This just generates an HTML document that includes `message`
        in the body. Override, or re-write this do do more interesting stuff.
        """
        content = f"<html><body><h1>{message}</h1></body></html>"
        return content.encode("utf8")  # NOTE: must return a bytes object!

    def do_GET(self):
        self._set_headers()
        self.wfile.write(self._html("hi!"))


def RunServer(host="localhost", port=8000, server_class=HTTPServer, handler_class=CustomRequest):
    server_address = (host, port)
    Server = server_class(server_address, handler_class)
    print(f"Starting http server on {host}:{port}")
    try:
        Server.serve_forever()
    except KeyboardInterrupt:
        Server.server_close()