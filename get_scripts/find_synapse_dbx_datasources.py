from pathlib import Path
import json
import datetime


def write_json(data, gw, time_stamp):
    """
    Write parsed data to json
    :param data: parsed dict
    :type data: dict
    """
    write_file = Path.cwd().joinpath(
        "json", f"synapse_dbx_datasources_{gw}_{time_stamp}.json"
    )
    with open(write_file, "w") as f:
        # 'dump' the entire dict object with formatting
        json.dump(data, f, indent=4)


def json_data(file_name) -> dict:
    """
    loads the json file data into a python dict

    :param file_name: json file
    :type file_name: object
    :return: dict of json objects
    :rtype: dict
    """

    with open(file_name, "r") as f:
        data = f.read()
        data = json.loads(data)
        return data


def check_string(conn_str):
    if "azuresynapse" in conn_str or "azuredatabricks" in conn_str:
        return True


def find_synapse_dbx(dataset_json, gw):
    """
    Takes JSON of all datasets and their sources on a gateway
    and returns only the azure synapse and dbx connections
    Input comes from running:  datasets_and_sources_by_gw_id.py

    :param dataset_json list of all datasource object
    :type dataset_json: list
    :return: list of only dataset objects
    :rtype: list
    """

    now = datetime.datetime.now()
    formatted_time = now.strftime("%Y-%m-%d_%H-%M-%S")

    parsed_connections = []
    for dataset_obj in dataset_json:
        datasources = list(dataset_obj.values())
        for source_list in datasources:
            for connection in source_list[0]:
                conn = connection.get("connectionDetails")
                conn = list(conn.values())[0]
                if result := check_string(conn):
                    parsed_connections.append(dataset_obj)
    write_json(parsed_connections, gw, formatted_time)
    return parsed_connections


print("did you update data_set_json filename and gateway_designator in this script?")
response = input("continue (y/n):  ")
data_set_json = "outputfile.json"
gateway_designator = "nonprod"
if response == "y":
    p = Path.cwd().joinpath("json", data_set_json)
    d = json_data(p)
    parsed_results = find_synapse_dbx(d, gateway_designator)
    print(parsed_results)
    print(len(d))
    print(len(parsed_results))
