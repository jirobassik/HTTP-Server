from socket import socket
from typing import BinaryIO

test_str = (
    b"GET /index.html HTTP/1.1\r\nHost: www.example.com\r\nConnection: keep-alive\r\n"
    b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    b"Chrome/89.0.4389.82 Safari/537.36\r\n"
    b"Accept: */*\r\n\r\n"
)


class HTTPServer:
    def read_http(self, http: socket):
        http_file = http.makefile("rb")
        http_list = self.read_byte_file(http_file)
        method, target, version_http = self.read_request_line(http_list.pop(0))
        print(method, target, version_http)
        headers = self.read_header_lines(http_list)
        print(headers)

    @staticmethod
    def read_byte_file(http_byte: BinaryIO) -> list[str]:
        headers = []
        while (line := http_byte.readline()) not in b"\r\n":
            headers.append(line.decode("iso-8859-1").replace("\r\n", ""))
        return headers

    @staticmethod
    def read_request_line(req_line: str) -> tuple[str, str, str]:
        split_request = req_line.split()
        if len(split_request) != 3:
            raise Exception("400 Bad request")
        method, target, version_http = split_request
        if method not in (
            "GET",
            "POST",
            "OPTIONS",
        ):
            raise Exception(
                "405 Method Not Allowed"
            )  # Так же можно добавить подсказку о поддерживаемых методах
        if version_http != "HTTP/1.1":
            raise Exception("505 HTTP Version Not Supported")
        return method, target, version_http

    @staticmethod
    def read_header_lines(req_line: list[str]):
        return {
            name_header: data_header.lstrip()
            for name_header, data_header in map(
                lambda str_: str_.split(":", 1), req_line
            )
        }


class HTTPError(Exception):
    pass
