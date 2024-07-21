import random
import base64


def rand_filename(length: int):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))


def b64e(s):
    return base64.b64encode(s).decode()


def b64d(s):
    return base64.b64decode(s).decode()