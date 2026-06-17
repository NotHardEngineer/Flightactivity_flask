import os

def delete_spaces(s: str):
    return " ".join(s.split())


def higher_first(s: str):
    s = s[0].upper() + s[1:]
    return s

def make_dir(name: str):
    if not os.path.exists(name):
        os.makedirs(name)