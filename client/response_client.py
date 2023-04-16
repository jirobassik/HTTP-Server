from socket import socket
from server.response import Response
from server.util.conf import ENCODING

class ClientResponse(Response):
    def __init__(self, status_code, message, connection_host: socket, body=None, version=None, **headers):
        super().__init__(status_code, message, connection_host, body, version=version, **headers)

    def send_response(self):
        reqeust_file = self.connection_host.makefile("wb")
        request_line = f"{self.status_code} {self.message} {self.version}\r\n"
        reqeust_file.write(request_line.encode(ENCODING))
        if self.headers:
            for key, value in self.headers.items():
                header_line = f"{key}: {value}\r\n"
                reqeust_file.write(header_line.encode(ENCODING))
        reqeust_file.write(b"\r\n")
        if self.body:
            reqeust_file.write(self.body)
        reqeust_file.flush()
        reqeust_file.close()
