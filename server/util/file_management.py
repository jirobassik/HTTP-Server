from os import listdir
from os.path import join
from .logging_conf import logger


class FileManagement:
    def __init__(self, target):
        self.__update_path = None
        self.target = target
        self.valid_folders, self.server_path = ("view",), ["/", ]
        self.standart_path = [
            join("/", valid_folder, file_name).replace("\\", "/")
            for valid_folder in self.valid_folders
            for file_name in listdir(valid_folder)
        ]
        self.special_folder_path = [
            f"/{valid_folder}{path}"
            for valid_folder in self.valid_folders
            for path in ("/*", "/",)
        ]

    def validate_path(self):
        if self.target in self.standart_path:
            self.__update_path = ('standart', self.target.lstrip("/").split("/", 1),)
        elif self.target in self.special_folder_path:
            self.__update_path = ('special', self.target.lstrip("/").split("/", 1),)
        elif self.target in self.server_path:
            self.__update_path = ('server', self.target,)
        else:
            return False
        logger.debug(f"Update path {self.__update_path}")
        return True

    def get_update_path(self):
        return self.__update_path

    def set_update_path(self, update_path):
        self.__update_path = update_path
