from socket import socket
from typing import Final

HOST: Final = '127.0.0.1'
PORT: Final = 54879

with socket() as sk:
    sk.connect((HOST, PORT, ))
    sk.sendall(b"Hello server socket")
    data = sk.recv(1024)
    print(f"Received {data!r}")