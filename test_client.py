from socket import socket
from typing import Final

HOST: Final = '127.0.0.1'
PORT: Final = 54879

with socket() as sk:
    sk.connect((HOST, PORT, ))
    sk.sendall(b"GET /view/viw.css HTTP/1.1\r\n"
               b"Accept: text/html\r\n\r\n")
    data = sk.recv(1024)
    print(f"Received {data!r}")