from pathlib import Path
from socket import socket
from typing import BinaryIO
from os import path
import re

from server.http_server import HTTPServer
from server.util.file_management import FileManagement
from server.util.conf import ENCODING
from server.util.substring import read_file_byte
from .client_error import ClientError
from .response_client import ClientResponse


class Client(HTTPServer, FileManagement):
    def connect_server_cli(self, method, url, headers_dict, body, version=None, ):
        with socket() as cl_sk:
            cl_sk.connect((self.host, self.port,))
            ClientResponse(method, url, cl_sk, body, version, **headers_dict).send_response()
            cl_sk.settimeout(None)
            self.http_handle(cl_sk)

    def connect_server_file(self, file_mes):
        with socket() as cl_sk:
            cl_sk.connect((self.host, self.port,))
            cl_sk.sendall(file_mes)
            cl_sk.settimeout(None)
            self.http_handle(cl_sk)

    def http_handle(self, http: socket):
        try:
            self.http_accept(http)
        except ClientError as cle:
            print(cle)

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

    def read_byte_file(self, http_byte: BinaryIO, timeout: int = 2) -> list[str]:
        headers = []
        while (line := http_byte.readline()) not in b"\r\n":
            headers.append(line.decode(ENCODING).replace("\r\n", ""))
        return headers

    def read_body(self, header: dict, http_byte: BinaryIO):
        if (content_length := int(header.get('Content-Length', '0'))) >= 0:
            return http_byte.read(content_length)
        raise ClientError()

    def read_content_type(self, header: dict, body):
        if content_type := header.get('Content-Type', ''):
            content_type = content_type.split('; ')[0]
            if client_cont := self.client_content_type(content_type, body):
                return client_cont
        raise ClientError()

    @staticmethod
    def read_file_name(header: dict):
        content_disp = header.get('Content-Disposition', 'filename="default"')
        match = re.search(r"filename='(.+)'", content_disp)
        try:
            match_str = match.group(1)
            return match_str
        except AttributeError:
            raise ClientError('No content-disposition')

    def http_accept(self, http: socket):
        version_http, status_code, status_message, headers, body = self.http_treatment(http)
        print(version_http, status_code, status_message)
        self.header_view(headers)
        if body:
            file_name = self.read_file_name(headers)
            create_new_file, body = self.read_content_type(headers, body)
            create_new_file('client/accept_files', f'/{file_name}', body)

    @staticmethod
    def request_from_file(file_name):
        if path.exists(Path(Path.cwd(), 'client', 'requests', file_name)):
            return read_file_byte('client/requests', f'/{file_name}')
        else:
            raise ClientError(f'File not found')

    @staticmethod
    def header_view(headers: dict):
        for name, value in headers.items():
            print(f'{name}: {value}')
