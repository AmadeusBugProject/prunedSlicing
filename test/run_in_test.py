import os
import pathlib


def distance_to_project_root():
    project_root = pathlib.Path(__file__).parent.parent
    path = pathlib.Path(os.getcwd())
    distance = 0
    while path != project_root:
        if path == path.parent:
            return -1
        path = path.parent
        distance += 1
    return distance


def relative_to_project_root(string_path):
    return '../'*distance_to_project_root() + string_path
