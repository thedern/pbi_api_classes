import requests
import sys
import time
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate

auth_obj = PowerbiAuthenticate()
pbi_access_token = auth_obj.generate_access("no-passwd")


"""

The way the API works: in order to get datasource info, you
need to know the data model id and feed that into the datasource API
so you need to get data model ids first.  Then, get datasources per model

Note: At this time there is no way to directly query the data source connection
for all models which use it.

"""


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
        if counter < 4:
            for dataset_name, dataset_values in dataset_obj.items():
                dataset_id = dataset_values[0]
                api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{dataset_id}/datasources"
                headers = {"Authorization": f"Bearer {token}"}
                counter += 1
                print(f"counter: {counter}")
                if api_response := crud(api_endpoint, headers):
                    created_by = dataset_values[1]

                    master_data_source_list.append(
                        {
                            "dataset_name": dataset_name,
                            "dataset_id": dataset_id,
                            "datasources": api_response["value"],
                            "dataset_created_by": created_by,
                        }
                    )
                    time.sleep(1)

        # else:
        #     # sleep, reset counter, refresh access token
        #     for i in range(3600, 0, -1):  # 3600
        #         sys.stdout.write(f"{str(i)} ")
        #         sys.stdout.flush()
        #         time.sleep(1)
        #     counter = 0
        #     token = auth_obj.generate_access("no-passwd")
        #     print("**** resuming api calls ****")

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


def main():
    """
    1. get all data sets
    2. get all data sources per dataset

    NOTE:  This script may run for hours depending on the number of datasets
    to investigate.
    """

    all_datasets = get_pbi_datasets(pbi_access_token)

    model_ids = [
        {
            model.get("name"): [
                model.get("id"),
                model.get("configuredBy", "No configuredBy found"),
            ]
        }
        for model in all_datasets["value"]
    ]

    datasources = get_datasource_info(model_ids, pbi_access_token)
    print(datasources)


if __name__ == "__main__":
    main()
