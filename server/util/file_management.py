from itertools import chain
from os import listdir
from os.path import join, splitext
from types import MappingProxyType
from functools import lru_cache
from re import match

from logs.logging_conf import logger
from .substring import write_file_byte, create_file
from .json_util import json_upload_key
from .conf import JSON_PATH


class FileManagement:
    def __init__(self, target):
        self.__update_path = None
        self.target = target
        self.__valid_folders, self.__server_path = json_upload_key(JSON_PATH, 'valid_folders'), ["/", ]
        self.__standart_path = [
            join("/", valid_folder, file_name).replace("\\", "/")
            for valid_folder in self.__valid_folders
            for file_name in self.get_folder_files(valid_folder)
        ]
        self.__special_folder_path = [
            f"/{valid_folder}{path}"
            for valid_folder in self.__valid_folders
            for path in ("/*", "/",)
        ]
        self.__allow_path_request = tuple(
            chain(self.server_path, self.standart_path, self.special_folder_path)
        )

    def validate_path(self, method: str) -> bool:
        match method:
            case "GET":
                return self.validate_path_get()
            case "POST":
                return self.validate_path_post()
            case "OPTIONS":
                return self.validate_path_options()

    def validate_path_get(self) -> bool:
        if self.target in self.__standart_path:
            self.__update_path = (
                "standart",
                self.split_path(self.target),
            )
        elif self.target in self.__special_folder_path:
            self.__update_path = (
                "special",
                self.split_path(self.target),
            )
        elif self.target in self.__server_path:
            self.__update_path = (
                "server",
                self.target,
            )
        else:
            return False
        logger.debug(f"Update path {self.__update_path}")
        return True

    def validate_path_post(self) -> bool:
        if self.valid_post_path(self.target):
            folder_name, file_name = self.split_path(self.target)
            if folder_name in self.__valid_folders and file_name:
                return True
        return False

    def validate_path_options(self) -> bool:
        if self.target in self.__allow_path_request or self.target == '*':
            return True
        return False

    @staticmethod
    @lru_cache(maxsize=None)
    def extension_content_type(extension: str) -> str | None:
        extension_dict = MappingProxyType(
            {
                ".html": "text/html",
                ".css": "text/css",
                ".png": "image/png",
                ".jpeg": "image/jpeg",
                ".svg": "image/svg+xml",
                ".txt": "text/plain",
                ".js": "text/javascript"
            }
        )
        return extension_dict.get(extension)

    @staticmethod
    def get_folder_files(folder_name: str) -> list:
        try:
            list_dir = listdir(folder_name)
            return list_dir
        except FileNotFoundError:
            pass

    @staticmethod
    @lru_cache(maxsize=None, typed=True)
    def client_content_type(content_type: str, body):
        if content_type in ('image/png', 'image/jpeg',):
            return write_file_byte, body
        elif content_type in ('text/css', 'text/html', 'text/plain', 'text/javascript',
                              'application/octet-stream', 'image/svg+xml'):
            return create_file, body.decode()

    @staticmethod
    @lru_cache(maxsize=None)
    def get_file_extension(file_name):
        _, extension = splitext(file_name)
        return extension

    @staticmethod
    @lru_cache(maxsize=None)
    def split_path(path: str):
        return path.lstrip("/").split("/", 1)

    @staticmethod
    @lru_cache(maxsize=None)
    def valid_post_path(path: str) -> bool:
        return bool(match('^/\w+/\w+', path))

    @property
    def update_path(self):
        return self.__update_path

    @update_path.setter
    def update_path(self, update_path):
        self.__update_path = update_path

    @property
    def server_path(self):
        return self.__server_path

    @property
    def standart_path(self):
        return self.__standart_path

    @property
    def special_folder_path(self):
        return self.__special_folder_path

    @property
    def allow_path_request(self):
        return self.__allow_path_request
