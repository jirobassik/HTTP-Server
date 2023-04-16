import threading
from socket import socket
from typing import BinaryIO
from .util import substring
from logs.logging_conf import logger
from .util.conf import ENCODING
from .http_error import HTTPError
from .request import Request


class HTTPServer:
    def __init__(self, port, host=""):
        self.__host = host
        self.__port = port
        self.connection = None

    @classmethod
    def default_connection(cls):
        return cls(54879, '127.0.0.1')

    def start_server(self):
        with socket() as sk:
            sk.bind((self.__host, self.__port,))
            sk.listen(4)
            sk.settimeout(None)
            while True:
                self.connection, address = sk.accept()
                with self.connection:
                    logger.info(f"Connect address {address}")
                    try:
                        self.http_accept(self.connection)
                        logger.debug("Connection close")
                    except (HTTPError, Exception) as error:
                        logger.warning(error)
                logger.info(f"Connection {address} lost")

    def http_treatment(self, http: socket):
        http_file = http.makefile("rb")
        http_list = self.read_byte_file(http_file, timeout=2)
        request_line = http_list.pop(0)
        method, target, version_http = self.read_request_line(request_line)
        logger.debug(
            f"Method: {method}, Target: {target}, Version HTTP: {version_http}"
        )
        headers = self.read_header_lines(http_list)
        logger.debug(f"Headers: {headers}")
        body = self.read_body(headers, http_file)
        return method, target, version_http, headers, body

    def http_accept(self, http: socket):
        method, target, version_http, headers, body = self.http_treatment(http)
        Request(method, target, version_http, headers, self.connection, body=body)

    def read_body(self, header: dict, http_byte: BinaryIO):
        try:
            if (content_length := int(header.get('Content-Length', '0'))) >= 0:
                return http_byte.read(content_length)
            raise HTTPError("400", "Bad request", self.connection)
        except ValueError:
            raise HTTPError("400", "Bad request", self.connection)

    def read_byte_file(self, http_byte: BinaryIO, timeout: int) -> list[str]:
        headers = []

        def read():
            while (line := http_byte.readline()) not in b"\r\n":
                headers.append(line.decode(ENCODING).replace("\r\n", ""))

        event = threading.Event()
        thread_read_file = threading.Thread(target=read)
        thread_read_file.start()
        thread_read_file.join(timeout)
        if thread_read_file.is_alive():
            event.set()
            raise HTTPError("400", "Bad request", connection_host=self.connection)
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

    @property
    def host(self):
        return self.__host

    @property
    def port(self):
        return self.__port
