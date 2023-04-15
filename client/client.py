from socket import socket
from typing import BinaryIO

from server.http_server import HTTPServer
from server.http_error import HTTPError


class Client(HTTPServer):
    def connect_server(self, message: bytes):
        with socket() as cl_sk:
            cl_sk.connect((self.host, self.port,))
            cl_sk.sendall(message)
            try:
                self.http_accept(cl_sk)
            except HTTPError:
                pass

    def http_treatment(self, http: socket):
        http_file = http.makefile("rb")
        http_list = self.read_byte_file(http_file)
        request_line = http_list.pop(0)
        method, target, version_http = self.read_request_line(request_line)
        headers = self.read_header_lines(http_list)
        body = self.read_body(headers, http_file)
        return method, target, version_http, headers, body

    def read_request_line(self, req_line: str) -> tuple[str, str, str]:
        method, target, version_http = req_line.split(' ', 2)
        return method, target, version_http

    def read_body(self, header: dict, http_byte: BinaryIO):
        if (content_length := int(header.get('Content-Length', '0'))) >= 0:
            return http_byte.read(content_length)

    def http_accept(self, http: socket):
        version_http, status_code, status_message, headers, body = self.http_treatment(http)
        print(version_http, status_code, status_message, )
        if body:
            print('Body')
            print(body.decode())


client = Client.default_connection()
mes = (b"GET /view/viw.css HTTP/1.1\r\n"
       b"Accept: text/html\r\n\r\n")
client.connect_server(mes)
