def split_substring(sub: list, sign: str):
    return map(lambda str_: str_.split(sign, 1), sub)


def read_file(path_folder: str, file_name: str):
    with open(path_folder + file_name, 'rb') as file:
        response = file.read()
    return response
