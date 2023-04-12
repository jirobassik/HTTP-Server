from socket import socket
from typing import BinaryIO
from .util import substring
from .util.logging_conf import logger
from .util.conf import ENCODING
from .http_error import HTTPError
from .request import Request


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
                        self.http_treatment(self.connection)
                        logger.debug("Connection close")
                    except HTTPError as error:
                        logger.warning(error)
                logger.info(f"Connection {address} lost")

    def http_treatment(self, http: socket):
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
            headers.append(line.decode(ENCODING).replace("\r\n", ""))
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
