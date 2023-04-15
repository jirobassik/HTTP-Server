from os import getpid

from server.util import substring
from server.util.file_management import FileManagement


class Multipart(FileManagement):
    path_to_bin_folder, name_bin_file = "server/temp_files", "/multiple.bin"

    def __init__(self, target):
        self.boundary = getpid()
        self.write_to_binary = substring.add_file_byte
        super().__init__(target)

    def write_file_data(self, folder_name):
        substring.clear_file(self.path_to_bin_folder, self.name_bin_file)
        for number, file_name in enumerate(self.get_folder_files(folder_name)):
            read_data_file = substring.read_file_byte(folder_name, f"/{file_name}")
            sub_body = self.__sub_body_template(
                file_number=number, file_name=file_name, file_data=read_data_file
            )
            self.__multiple_write_binary(read_data_file, sub_body)
        self.write_to_binary(
            self.path_to_bin_folder,
            self.name_bin_file,
            f"----{self.boundary}----\r\n".encode(),
        )
        return self.__send_data_multipart_message()

    def __multiple_write_binary(self, read_data_file, sub_body):
        data_to_binary = (
            sub_body.encode(),
            read_data_file,
            f"\r\n".encode(),
        )
        for data in data_to_binary:
            self.write_to_binary(self.path_to_bin_folder, self.name_bin_file, data)

    def __sub_body_template(self, file_number: int, file_name: str, file_data):
        return (
            f"----{self.boundary}\r\n"
            f"Content-Type: {self.extension_content_type(self.get_file_extension(file_name))}; "
            f"charset=utf-8\r\n"
            f'Content-Disposition: form-data; name="file{file_number + 1}"; filename="{file_name}"\r\n'
            f"Content-Length: {len(file_data)}\r\n\r\n"
        )

    def __send_data_multipart_message(self):
        body = substring.read_file_byte(self.path_to_bin_folder, self.name_bin_file)
        headers = {
            "Content-Type": f"multipart/form-data; boundary={self.boundary}",
            "Content-Length": len(body),
        }
        # substring.clear_file(path_to_bin_folder, name_bin_file)
        return body, headers
