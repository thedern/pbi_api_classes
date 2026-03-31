from pathlib import Path
from src.support_utils.console_themes import custom_theme
from rich.console import Console
import json

console = Console(theme=custom_theme)


def json_data(file_name) -> dict:
    """
    loads the json file data into a python dict

    :param file_name: json file
    :type file_name: object
    :return: dict of json objects
    :rtype: dict
    """
    if file_name.exists():
        with open(file_name, "r") as f:
            data = f.read()
            data = json.loads(data)
            return data
    else:
        console.print(
            "[warning]input_values.json does not exist please create and then retry.[/warning]"
        )


def open_json() -> dict:
    """
    Opens file input_values.json for reading
    :return: input data
    :rtype: dict
    """
    return json_data(Path.cwd().joinpath("json", "input_values.json"))


def open_named_json(name):
    return json_data(Path.cwd().joinpath("json", name))


def open_tenant_workspaces() -> dict:
    """
    Opens <capacity name>_workspaces.json for reading based on user input
    Multiple capacities exist
    :return: workspaces data
    :rtype: list of workspace objects
    """

    capacities_dict = open_capacities_json()
    for val in capacities_dict.values():
        console.print("[header]AVAILABLE CAPACITIES:[/header]")
        for capacity_obj in val:
            print(capacity_obj["displayName"])

    console.print(
        "\n" "[info]To get workspaces, select a capacity from the list above.[/info]"
    )

    json_file = console.input("[warning]Enter capacity name:  ")
    return json_data(Path.cwd().joinpath("json", f"{json_file}_workspaces.json"))
    # return json_data(Path.cwd().joinpath("json", "tenant_workspaces.json"))


def open_capacities_json() -> dict:
    """
    Opens tenant_capacities.json for reading
    :return: workspaces data
    :rtype: dict
    """
    return json_data(Path.cwd().joinpath("json", "tenant_capacities.json"))
