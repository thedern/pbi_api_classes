import requests
import sys
import time
from functools import wraps
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.write_file import write_json


"""

The way the API works: in order to get datasource info, you
need to know the data model id and feed that into the datasource API
so you need to get data model ids first.  Then, get datasources per model

Note: At this time there is no way to directly query the data source connection
for all models which use it.

"""


def timethis(func):
    """
    decorator to time a function

    Args:
        func (_type_): function to be timed
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        return result

    return wrapper


def crud(api_endpoint, headers):
    """
    executes API call

    :param api_endpoint: API url
    :type api_endpoint: str
    :param headers: headers
    :type headers: dict
    :return: json response
    :rtype: dict
    """
    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response.json()
        else:
            print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def get_datasource_info(models_id_list, token):
    """
    for model {name: [id, configuredBy]} objects, get datasource(s)
    append to list

    dataset's id is required to get data source info

    NOTE: API call limit is 300 calls an hour, after every 300, sleep 3600
    NOTE: Access token must be refreshed else, 403

    # admin only endpoint
    # non-admin returns datasources from 'my workspace' only

    :param models_id_list: list of data model info
    :type models_id_list: list
    :param token: access token
    :type token: str
    :return: list of datasources per dataset
    :rtype: list
    """
    master_data_source_list = []
    counter = 0

    for dataset_obj in models_id_list:
        if counter < 300:
            for dataset_name, dataset_values in dataset_obj.items():
                dataset_id = dataset_values[0]
                api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{dataset_id}/datasources"
                headers = {"Authorization": f"Bearer {token}"}
                counter += 1
                print(f"counter: {counter}")
                if api_response := crud(api_endpoint, headers):
                    created_by = dataset_values[1]

                    master_data_source_list.append(
                        {dataset_name: [dataset_id, api_response["value"], created_by]}
                    )
                    time.sleep(1)

                    """
                    # block for testing against a subset only #
                    if len(master_data_source_list) == 5:
                        return master_data_source_list
                    """
        else:
            # sleep, reset counter, refresh access token
            for i in range(3600, 0, -1):  # 3600
                sys.stdout.write(f"{str(i)} ")
                sys.stdout.flush()
                time.sleep(1)
            counter = 0
            token = auth_obj.generate_access("no-passwd")
            print("**** resuming api calls ****")

    return master_data_source_list


def get_pbi_datasets(token):
    """
    Get data models per workspaces
    May use admin or non-admin endpoint
    """

    # for wks_id in wkspcs.values():
    api_endpoint = "https://api.powerbi.com/v1.0/myorg/admin/datasets"
    headers = {"Authorization": f"Bearer {token}"}
    return crud(api_endpoint, headers)


def get_capacity_workspaces(token, capacity_list) -> list:
    """

    get list of active workspaces which exist in supported capacities
    note API call requires ID in uppercase

    :param token: access token
    :type token: str
    :param capacity_list: list of capacity ids
    :type capacity_list: list
    :return: list of workspace ids
    :rtype: list
    """

    master_list_workspace_ids = []

    headers = {"Authorization": f"Bearer {token}"}
    endpoint_url = "https://api.powerbi.com/v1.0/myorg/admin/groups?$filter=capacityId"

    try:
        for capacity_id in capacity_list:
            powerbi_api_endpoint = (
                f"{endpoint_url} eq '{capacity_id.upper()}'&$top=5000"
            )
            if api_response := crud(powerbi_api_endpoint, headers):
                workspaces = list(api_response.values())[2]
                active_workspaces = [
                    item["id"] for item in workspaces if item["state"] == "Active"
                ]
                master_list_workspace_ids.extend(active_workspaces)
            else:
                print(f"Error with API Repsonse:: {api_response}")
        return master_list_workspace_ids
    except Exception as e:
        print(e)


def filter_datasets(wkspc_list, dataset_objects):
    """
    filter all datasets for only those which exist in
    supported capacities

    :param wkspc_list: list of capacity workspaces
    :type wkspc_list: list
    :param dataset_objects: list of dataset objects
    :type dataset_objects: list
    :return: filtered list of capacity datasets
    :rtype: list
    """
    filtered_list = []
    filtered_list.extend(
        dataset
        for dataset in dataset_objects["value"]
        if dataset.get("workspaceId", None) in wkspc_list
    )
    return filtered_list


def filter_by_gw(ds_list, gw):
    """
    filter datasets/sources by gateway

    ds_list: [{key:[[{ds},{ds}], conifiguredBy]}]
        key is data set name
        value[0] is a list of data source objects
        value[1] is configuredBy

    :param ds_list: list of dataset/source objects
    :type ds_list: list
    :param gw: gateway id
    :type gw: str
    :return: list of dataset/source objects
    :rtype: list
    """

    list_of_matches = []
    for ds_object in ds_list:
        try:
            for key, value in ds_object.items():
                for sub_object in value[0]:
                    if sub_object.get("gatewayId") == gw:
                        print("match!!!")
                        list_of_matches.append(ds_object)
                        # advance to next if any one sub-object matches, avoids dupes
                        continue
                    else:
                        print("no match")
        except Exception as e:
            print(e)
            continue

    return list_of_matches


@timethis
def main():
    """
    ADMIN API

    Discovers datasets/datasources per desired gateway in supported Worskspaces
    Steps in the discovery process:

    1. get workspaces existing in supported capacities only
    2. get ALL data sets in tenant (via single API call)
    3. filter ALL data sets against supported workspaces
    4. reduce datasets to object {name: [id, configuredBy]}}
    5. get datasource and gw info for filtered datasets
    6. filter for only datasets/sources configured against desired gateway
    7. write results to json

    NOTE:  This script may run for hours depending on the number of datasets
    to investigate.
    """

    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("no-passwd")

    # constants
    gateway = {"gatway1": "<id>"}


    capacity_ids = [
        "<id>",
        "<id>",
    ]

    # 1
    list_of_workspaces = get_capacity_workspaces(pbi_access_token, capacity_ids)
    # 2
    all_datasets = get_pbi_datasets(pbi_access_token)
    # 3
    targeted_datasets = filter_datasets(list_of_workspaces, all_datasets)
    # 4
    model_ids = [
        {
            model["name"]: [
                model["id"],
                model.get("configuredBy", "No configuredBy found"),
            ]
        }
        for model in targeted_datasets
    ]
    # 5
    datasources = get_datasource_info(model_ids, pbi_access_token)
    # 6
    filtered_datasets = filter_by_gw(datasources, gateway.get("<gw name>"))
    print(f"number of filtered datasets: {len(filter_datasets)}")
    # 7
    write_json(filtered_datasets, "datasets_dna_nonprod_gw.json")


if __name__ == "__main__":
    main()
