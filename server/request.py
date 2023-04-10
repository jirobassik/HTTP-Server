from itertools import chain
from socket import socket
from types import MappingProxyType

from .http_error import HTTPError
from .util import substring
from .util import logging_conf
from .response import Response
from .util.file_management import FileManagement

class Request(FileManagement):
    def __init__(
            self, method: str, target: str, version: str, headers: dict, connection: socket
    ):
        super().__init__(target)
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

        if not self.validate_path():
            raise HTTPError("404", "Not Found", self.connection)

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
        logging_conf.logger.debug(f"Accept: {self.accept}")
        if not any(
                key
                for key in self.accept
                if set(self.accept.get(key, ())).intersection(
                    self.valid_accept.get(key, ())
                )
        ):
            raise HTTPError("406", "Not Acceptable", self.connection)

    def get_choose(self, path_type: str) -> dict:
        dict_get = MappingProxyType(
            {
                "standart": self.standart_request,
                "special": self.special_request,
                "server": self.server_request,
            }
        )
        return dict_get.get(path_type)

    def standart_request(self, path):
        folder, file_name = path
        read_file = substring.read_file(folder, f'/{file_name}')
        header = {"Content-Type": "text/html; charset=utf-8"}
        Response('200', 'OK', self.connection, body=read_file, **header).send_response()

    def server_request(self, path):
        allow_path_request = tuple(chain(self.server_path, self.standart_path, self.special_folder_path))
        message_allow_path = f'\nAllow path requests: {allow_path_request}'
        Response('200', message_allow_path, self.connection, ).send_response()

    def special_request(self, path):
        folder, file_name = path
        match file_name:
            case '':
                self.special_print_all(folder)
            case '*':
                self.special_get_all(folder)

    def special_print_all(self, folder_name):
        folder_files = f'Folder files: {self.get_folder_files(folder_name)}'
        Response('200', folder_files, self.connection).send_response()

    def special_get_all(self, folder_name):
        pass

    def analyze_request(self):
        if self.method == "GET":
            path_type, path = self.get_update_path()
            logging_conf.logger.debug(f'Path type: {path_type}, Path: {path}')
            path_type_method = self.get_choose(path_type)
            path_type_method(path)

        if self.method == "POST":
            pass
        if self.method == "OPTIONS":
            header = {
                "Allow": "GET, POST, OPTIONS",
                "Allow-Headers": "Accept",
            }
            Response("200", "OK", self.connection, **header).send_response()
