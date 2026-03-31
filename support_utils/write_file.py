from pathlib import Path
import pandas as pd
import json


def write_json(data, file_name) -> json:
    """
    Writes json data to /json directory within project

    :param data: data in python dictionary format
    :type data: dict
    :param file_name: name of file to write
    :type file_name: str
    :return: JSON file
    :rtype: json
    """
    p = Path.cwd().joinpath("json", file_name)
    with open(p, "w") as f:
        # 'dump' the entire dict object with formatting
        json.dump(data, f, indent=4)


def append_json(data, file_name) -> json:
    """
    Writes json data to /json directory within project

    :param data: data in python dictionary format
    :type data: dict
    :param file_name: name of file to write
    :type file_name: str
    :return: JSON file
    :rtype: json
    """
    p = Path.cwd().joinpath("json", file_name)
    with open(p, "a") as f:
        # 'dump' the entire dict object with formatting
        json.dump(data, f, indent=4)


def write_excel(data, file_name):
    """
    converts data to excel, the writes to /json directory

    :param data: data in python dictionary format
    :type data: dict
    :param file_name: name of file to write
    :type file_name: str
    """
    df = pd.json_normalize(data)
    p = Path.cwd().joinpath("json", file_name)
    df.to_excel(p, index=False)
