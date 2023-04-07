from socket import socket
from typing import BinaryIO
from logging_conf import logger

test_str = (
    b"GET /index.html HTTP/1.1\r\nHost: www.example.com\r\nConnection: keep-alive\r\n"
    b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    b"Chrome/89.0.4389.82 Safari/537.36\r\n"
    b"Accept: */*\r\n\r\n"
)


class HTTPServer:
    def __init__(self, port, host=""):
        self.host = host
        self.port = port
        self.connection = None

    def start_server(self):
        with socket() as sk:
            sk.bind(
                (
                    self.host,
                    self.port,
                )
            )
            sk.listen(4)
            while True:
                self.connection, address = sk.accept()
                with self.connection:
                    logger.info(f"Connect address {address}")
                    try:
                        self.read_http(self.connection)
                    except HTTPError as error:
                        logger.warning(error)
                    while data := self.connection.recv(1024):
                        logger.info(f"Client message {data} {type(data)}")
                        self.connection.sendall(b"Hello client socket")
                logger.info(f"Connection {address} lost")

    def read_http(self, http: socket):
        http_file = http.makefile("rb")
        http_list = self.read_byte_file(http_file)
        method, target, version_http = self.read_request_line(http_list.pop(0))
        logger.debug(
            f"Method: {method}, Target: {target}, Version HTTP: {version_http}"
        )
        headers = self.read_header_lines(http_list)
        logger.debug(f"Headers: {headers}")

    @staticmethod
    def read_byte_file(http_byte: BinaryIO) -> list[str]:
        headers = []
        while (line := http_byte.readline()) not in b"\r\n":
            headers.append(line.decode("iso-8859-1").replace("\r\n", ""))
        return headers

    def read_request_line(self, req_line: str) -> tuple[str, str, str]:
        split_request = req_line.split()
        if len(split_request) != 3:
            raise HTTPError("400", "Bad request", connection_host=self.connection)
        method, target, version_http = split_request
        if method not in (
            "GET",
            "POST",
            "OPTIONS",
        ):
            raise HTTPError(
                "405", "Method Not Allowed", connection_host=self.connection
            )  # Так же можно добавить подсказку о поддерживаемых методах
        if version_http != "HTTP/1.1":
            raise HTTPError(
                "505", "HTTP Version Not Supported", connection_host=self.connection
            )
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
    def __init__(self, error, error_message, connection_host, message=None):
        self.num_error = error
        self.error_message = error_message
        self.message = message
        self.connection_host = connection_host
        Request(self.num_error, self.error_message, connection_host).send_request()

    def __str__(self):
        return f"Num error: {self.num_error}, Error message: {self.error_message}"

    def send_error(self):
        pass


class Request:
    def __init__(
        self,
        status_code,
        message,
        connection_host: socket,
        version="HTTP/1.1",
        **headers,
    ):
        self.version = version
        self.status_code = status_code
        self.message = message
        self.connection_host = connection_host
        self.headers = headers or {}

    def send_request(self):
        #  Почему-то сам отправляет
        reqeust_file = self.connection_host.makefile("wb")
        request_line = f"{self.version} {self.status_code} {self.message}\r\n"
        reqeust_file.write(request_line.encode("iso-8859-1"))
        reqeust_file.write(b"\r\n")
        reqeust_file.flush()
        reqeust_file.close()
