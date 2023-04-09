from typing import Final
from server.http_server import HTTPServer

HOST: Final = "127.0.0.1"
PORT: Final = 54879

a = HTTPServer(port=PORT, host=HOST)
a.start_server()
