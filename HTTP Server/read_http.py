from socket import socket
from typing import BinaryIO
from logging_conf import logger
from utilities import substring

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
        Request(method, target, version_http, headers, self.connection)

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
        return method, target, version_http

    @staticmethod
    def read_header_lines(req_line: list[str]):
        return {
            name_header: data_header.lstrip()
            for name_header, data_header in substring.split_substring(
                req_line, sign=":"
            )
        }


class HTTPError(Exception):
    def __init__(self, error, error_message, connection_host, message=None):
        self.num_error = error
        self.error_message = error_message
        self.message = message
        self.connection_host = connection_host
        Response(self.num_error, self.error_message, connection_host).send_response()

    def __str__(self):
        return f"Num error: {self.num_error}, Error message: {self.error_message}"


class Request:
    def __init__(self, method, target, version, headers: dict, connection: socket):
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.connection = connection
        self.valid_accept = {
            "text": ("html",),
            "image": (
                "png",
                "svg",
            ),
        }
        self.accept = self.get_dict_accept_el(
            self.headers.get("Accept", "*/*").split(",")
        )
        self.check_valid_request_line()
        self.validate_accept()
        self.analyze_request()

    def check_valid_request_line(self):
        if self.method not in (
            "GET",
            "POST",
            "OPTIONS",
        ):
            raise HTTPError(
                "405",
                "Method Not Allowed. Allowed: GET, POST, OPTIONS",
                connection_host=self.connection,
            )
        if self.version != "HTTP/1.1":
            raise HTTPError(
                "505",
                "HTTP Version Not Supported. Supported: HTTP/1.1",
                connection_host=self.connection,
            )

    @staticmethod
    def get_dict_accept_el(accept: list) -> dict:
        accept_dict = {}
        list_tuple_accept = [
            (
                name_header,
                data_header,
            )
            for name_header, data_header in substring.split_substring(accept, sign="/")
        ]
        for first, second in list_tuple_accept:
            accept_dict.setdefault(first, []).append(second)
        return accept_dict

    def validate_accept(self):
        logger.debug(f"Accept: {self.accept}")
        if not any(
            key
            for key in self.accept
            if set(self.accept.get(key, ())).intersection(
                self.valid_accept.get(key, ())
            )
        ):
            raise HTTPError("406", "Not Acceptable", self.connection)

    def validate_path(self):
        pass

    def analyze_request(self):
        if self.method == "GET":
            pass
        if self.method == "OPTIONS":
            header = {
                "Allow": "GET, POST, OPTIONS",
                "Allow-Headers": "Accept",
            }
            Response("200", "OK", self.connection, **header).send_response()


class Response:
    def __init__(
        self,
        status_code,
        message,
        connection_host: socket,
        body=None,
        version="HTTP/1.1",
        **headers,
    ):
        self.version = version
        self.status_code = status_code
        self.message = message
        self.connection_host = connection_host
        self.body = body
        self.headers = headers

    def send_response(self):
        request_file_str = ""
        reqeust_file = self.connection_host.makefile("wb")
        request_line = f"{self.version} {self.status_code} {self.message}\r\n"
        request_file_str += "\n" + request_line
        reqeust_file.write(request_line.encode("iso-8859-1"))
        if self.headers:
            for key, value in self.headers.items():
                header_line = f"{key}: {value}\r\n"
                request_file_str += header_line
                reqeust_file.write(header_line.encode("iso-8859-1"))
        if self.body:
            reqeust_file.write(self.body)
        reqeust_file.write(b"\r\n")
        request_file_str += "\r\n"
        logger.debug(f"Response: {request_file_str}")
        reqeust_file.flush()
        reqeust_file.close()
