import os
import random
from pathlib import Path, PurePath


def get_title(blade_details):
    title = blade_details["type"]
    if type(title) is list:
        title = random.choice(title)

    return title


def get_crystal(blade_details):
    crystal = blade_details["crystal"]
    if type(crystal) is list:
        crystal = random.choice(crystal)

    return crystal


def get_path(part, path):
    if part != ".":
        part = Path(f"{path}/{part}")
    else:
        part = Path(f"{path}/{random.choice(os.listdir(path))}")

    return part
