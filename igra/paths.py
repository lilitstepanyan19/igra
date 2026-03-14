import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def file_path(path):
    return os.path.join(BASE_DIR, path)
