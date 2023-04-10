from socket import socket
from .util.logging_conf import logger
from .util.conf import ENCODING


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
        reqeust_file.write(request_line.encode(ENCODING))
        if self.headers:
            for key, value in self.headers.items():
                header_line = f"{key}: {value}\r\n"
                request_file_str += header_line
                reqeust_file.write(header_line.encode(ENCODING))
        if self.body:
            reqeust_file.write(self.body)
        reqeust_file.write(b"\r\n")
        request_file_str += "\r\n"
        logger.debug(f"Response: {request_file_str}")
        reqeust_file.flush()
        reqeust_file.close()
