def split_substring(sub: list, sign: str):
    return map(lambda str_: str_.split(sign, 1), sub)

def read_file_byte(path_folder: str, file_name: str):
    with open(path_folder + file_name, 'rb') as file:
        response = file.read()
    return response

def write_file_byte(path_folder: str, file_name: str, data):
    with open(path_folder + file_name, f'wb') as file:
        file.write(data)

def add_file_byte(path_folder: str, file_name: str, data):
    with open(path_folder + file_name, f'ab') as file:
        file.write(data)

def clear_file(path_folder: str, file_name: str):
    open(path_folder + file_name, 'w').close()

def create_file(path_folder: str, file_name: str, data):
    with open(path_folder + file_name, 'w') as file:
        file.write(data)
