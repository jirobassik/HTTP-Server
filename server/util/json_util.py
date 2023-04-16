import json
from typing import NoReturn

def json_save(path: str, list_folders: tuple, key_name: str) -> NoReturn:
    with open(path, encoding='utf-8') as file_json:
        data = json.load(file_json)
    data[key_name].extend(list_folders)
    with open(path, 'w', encoding='utf-8') as file_json:
        json.dump(data, file_json, indent=4, ensure_ascii=False)

def json_save_one(path: str, value_name, key_name: str) -> NoReturn:
    with open(path, encoding='utf-8') as file_json:
        data = json.load(file_json)
    data[key_name] = value_name
    with open(path, 'w', encoding='utf-8') as file_json:
        json.dump(data, file_json, indent=4, ensure_ascii=False)

def json_upload_key(path: str, key_name: str) -> list:
    with open(path, encoding='utf-8') as file_json:
        data = json.load(file_json)
    return data[key_name]

def json_clear_valid_folders(path: str, key_js: str) -> NoReturn:
    with open(path) as file_json:
        data = json.load(file_json)
    data[key_js].clear()
    with open(path, 'w') as file_json:
        json.dump(data, file_json, indent=4, ensure_ascii=False)

def json_del_valid_folder(path: str, key_js: str, name_to_del: str) -> NoReturn:
    with open(path, encoding='utf-8') as file_json:
        data = json.load(file_json)
    data[key_js].remove(name_to_del)
    with open(path, 'w', encoding='utf-8') as file_json:
        json.dump(data, file_json, indent=4, ensure_ascii=False)
