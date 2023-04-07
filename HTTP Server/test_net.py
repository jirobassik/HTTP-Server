from socket import socket
from typing import Final
from read_http import HTTPServer
from logging_conf import logger

HOST: Final = '127.0.0.1'
PORT: Final = 54879

#
# def load_page_from_request(request_data: str):
#     hdrs = 'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
#     hdrs_404 = 'HTTP/1.1 404 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n'
#     print(f"request_Data:{request_data}")
#     path = request_data.split(' ')[1]
#     print(path)
#     try:
#         with open('view' + path, 'rb') as file:
#             response = file.read()
#         return hdrs.encode('utf-8') + response
#     except (FileNotFoundError, PermissionError):
#         response = 'File not found'.encode('utf-8')
#         return hdrs_404.encode('utf-8') + response
#
#
# with socket() as sk:
#     sk.bind((HOST, PORT,))
#     sk.listen(4)
#     while True:
#         connection, address = sk.accept()
#         with connection:
#             print(f"Connect address {address}")
#             while data := connection.recv(1024):
#                 hdrs = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n'
#                 print(f"Client message {data}")
#                 connection.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n')
#
#                 # connection.send(hdrs.encode('utf-8') + "Lox".encode('utf-8'))
#         print(f"Connection {address} lost")

a = HTTPServer()
with socket() as sk:
    sk.bind((HOST, PORT,))
    sk.listen(4)
    while True:
        connection, address = sk.accept()
        with connection:
            logger.info(f'Connect address {address}')
            a.read_http(connection)
            while data := connection.recv(1024):
                logger.info(f"Client message {data} {type(data)}")
                connection.sendall(b'Hello client socket')
        logger.info(f"Connection {address} lost")
