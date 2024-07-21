import random


def rand_filename(length: int):
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
