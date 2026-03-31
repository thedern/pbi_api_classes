import requests
import json
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.write_file import write_json


"""
This will take a workspace, find all data models in that workspace, then find 
all data sources configured for those models.

The way the API works: in order to get datasource info, you
need to know the data model id and feed that into the datasource API
so you need to get data model ids first.

Note: At this time there is no way to directly query the data source connection
for all models which use it.


"""


def crud(api_endpoint, headers):
    """
    runs api call
    """
    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response
        else:
            print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def get_datasource_info(models_id_list, token):
    """
    for model {name: id} objects, get datasource(s)
    append to list

    dataset's id is required to get data source info

    # admin only endpoint
    # non-admin returns datasources from 'my workspace' only
    """
    data_source_list = []

    for dataset_obj in models_id_list:
        for dataset_name, dataset_id in dataset_obj.items():

            api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{dataset_id}/datasources"
            headers = {"Authorization": f"Bearer {token}"}

            if api_response := crud(api_endpoint, headers):
                data_source_list.append({dataset_name: api_response.json()["value"]})

    return data_source_list


def get_dataset_users(models_id_list, token):
    """
    for model {name: id} objects, get datasource(s)
    append to list

    dataset's id is required to get data source info

    # admin only endpoint
    # non-admin returns datasources from 'my workspace' only
    """
    dataset_users_list = []

    for dataset_obj in models_id_list:
        try:
            for dataset_name, dataset_id in dataset_obj.items():

                api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{dataset_id}/users"
                headers = {"Authorization": f"Bearer {token}"}

                if api_response := crud(api_endpoint, headers):
                    dataset_users_list.append(
                        {dataset_name: api_response.json()["value"]}
                    )
        except Exception as e:
            print(f"Exception:: {e}")
    return dataset_users_list


def get_ws_dataset(wkspcs, token):
    """
    Get data models per workspaces

    May use admin or non-admin endpoint
    """

    for wks_id in wkspcs.values():
        api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{wks_id}/datasets"
        )
        headers = {"Authorization": f"Bearer {token}"}

        return crud(api_endpoint, headers)


def main():
    """
    ADMIN API
    Finds datasets and datasources for the workspace input below.
    """

    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("non-passwd")

    workspaces = {
        "Office 365 Workspace": "",
    }

    dataset_resp = get_ws_dataset(workspaces, pbi_access_token)
    model_ids = [{model["name"]: model["id"]} for model in dataset_resp.json()["value"]]
    dataset_users = get_dataset_users(model_ids, pbi_access_token)
    # datasources = get_datasource_info(model_ids, pbi_access_token)

    users_json_string = json.dumps(dataset_users)
    print(users_json_string)

    # sources_json_string = json.dumps(datasources)
    # print(sources_json_string)
    write_json(dataset_users, f"{next(iter(workspaces))}_datasource_users.json")


if __name__ == "__main__":
    main()
