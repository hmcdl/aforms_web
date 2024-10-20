"""
Некоторые вспомогательные функции
"""
import os

from fastapi import UploadFile

def upload_file(dir_name: str, file_name: str, file: UploadFile) -> None:
    """
    Функция, выгружающая файл на диск
    """
    with open(os.path.join(dir_name, file_name), 'wb+') as f:
                contents = file.file.read()
                f.write(contents)