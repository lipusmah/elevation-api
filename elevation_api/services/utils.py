import json
import math
import random
import string


def get_distance(c1: tuple[float, float], c2: tuple[float, float]):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)


def get_distance_3d(c1: tuple[float, float, float], c2: tuple[float, float, float]):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2)


def read_file_as_json(path) -> object:
    with open(path, 'r') as f:
        return json.load(f)


def extent_contains(extent: list[float], x: float, y: float) -> bool:
    if extent[0] < x < extent[2] and extent[1] < y < extent[3]:
        return True
    return False


# printing lowercase
letters = string.ascii_lowercase


def get_random_string():
    return ''.join(random.choice(letters) for i in range(12))
