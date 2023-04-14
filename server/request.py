from itertools import chain
from socket import socket
from types import MappingProxyType

from .http_error import HTTPError
from .util import substring
from .util import logging_conf
from .response import Response
from .multipart import Multipart


class Request(Multipart):
    def __init__(
            self, method: str, target: str, version: str, headers: dict, connection: socket, body=None
    ):
        super().__init__(target)
        self.method = method
        self.target = target
        self.version = version
        self.headers = headers
        self.connection = connection
        self.body = body
        self.valid_accept = {
            "text": (
                "html",
                "css",
            ),
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

        if not self.validate_path(self.method):
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
        read_file = substring.read_file_byte(folder, f"/{file_name}")
        header = {
            "Content-Type": f"{self.extension_content_type(self.get_file_extension(file_name))}; charset=utf-8",
            "Content-Length": len(read_file),
        }
        Response("200", "OK", self.connection, body=read_file, **header).send_response()

    def server_request(self, path):
        allow_path_request = tuple(
            chain(self.server_path, self.standart_path, self.special_folder_path)
        )
        headers = {"Allow path requests": allow_path_request}
        Response("200", "OK", self.connection, **headers).send_response()

    def special_request(self, path):
        folder, file_name = path
        match file_name:
            case "":
                self.special_print_all(folder)
            case "*":
                self.special_send_all(folder)

    def special_print_all(self, folder_name):
        headers = {"Folder files": self.get_folder_files(folder_name)}
        Response("200", "OK", self.connection, **headers).send_response()

    def special_send_all(self, folder_name):
        body, headers = self.write_file_data(folder_name)
        Response("200", "OK", self.connection, body=body, **headers).send_response()

    def analyze_request(self):
        match self.method:
            case "GET":
                self.get_request()
            case "POST":
                self.post_request()
            case "OPTIONS":
                self.options_request()

    def get_request(self):
        path_type, path = self.update_path
        logging_conf.logger.debug(f"Path type: {path_type}, Path: {path}")
        path_type_method = self.get_choose(path_type)
        path_type_method(path)

    def post_request(self):
        folder_name, file_name = self.split_path(self.target)
        create_file, body = self.post_content_type()
        create_file(folder_name, f'/{file_name}', body)
        Response("200", "OK", self.connection).send_response()

    def post_content_type(self):
        print('post_cont')
        if content_type := self.headers.get('Content-Type', ''):
            print(content_type)
            if client_cont := self.client_content_type(content_type, self.body):
                return client_cont
        raise HTTPError('400', 'Bad request', self.connection)

    def options_request(self):
        header = {
            "Allow": "GET, POST, OPTIONS",
            "Allow-Headers": "Accept",
            "POST-Headers": "Content-Type, Content-Length",
        }
        Response("200", "OK", self.connection, **header).send_response()
