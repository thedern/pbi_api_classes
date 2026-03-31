import requests
from pathlib import Path
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.write_file import write_json
from src.support_utils.open_file import json_data


def get_dataset_refresh(dataset_id, token) -> dict:
    """
    Returns dataset refresh records

    :param dataset_id: dataset identifier
    :type dataset_id: str
    :param token: access token
    :type token: str
    :return: _description_
    :rtype: dict
    """

    api_endpoint = (
        f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes?$top=1"
    )
    headers = {"Authorization": f"Bearer {token}"}
    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            if api_response.json()["value"]:
                return {"datasetId": {dataset_id: api_response.json()["value"]}}
            else:
                return {"datasetId": {dataset_id: "No refresh found"}}
        else:
            return {"datasetId": {dataset_id: "No refresh found"}}
    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def get_datasource_by_dataset(dataset_id, token) -> dict:
    """
    Gets data source(s) per dataset

    :param dataset_id: dataset identifier
    :type dataset_id: str
    :param token: access token
    :type token: str
    :return: dictionart of datas sources
    :rtype: dict
    """
    api_endpoint = (
        f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{dataset_id}/datasources"
    )
    headers = {"Authorization": f"Bearer {token}"}
    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return {"datasetId": {dataset_id: api_response.json()["value"]}}
        else:
            return {"datasetId": {dataset_id: "No datasets found"}}
    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def get_workspace_reports(token, capacity_data, capacity_name) -> None:
    """
    Gets reports per workpace

    :param token: access token
    :type token: str
    :param capacity_data: list of workpaces objects
    :type capacity_data: list
    :param capacity_name: name of target capacity
    :type capacity_name: str
    """
    reports_final_list = []

    for workspace_obj in capacity_data:
        print(workspace_obj["id"])
        print(workspace_obj["name"])

        api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_obj['id']}/reports"
        headers = {"Authorization": f"Bearer {token}"}

        try:
            api_response = requests.get(api_endpoint, headers=headers)
            if api_response.status_code in {200, 201, 202}:
                resp = api_response.json()
                if resp.get("value"):
                    for report_obj in resp.get("value"):
                        if report_obj.get("datasetId"):
                            ds = get_datasource_by_dataset(
                                report_obj["datasetId"], token
                            )
                            report_obj["dataSources"] = ds

                            rf = get_dataset_refresh(report_obj["datasetId"], token)
                            report_obj["datasetRefresh"] = rf

                    reports_final_list.append(
                        {
                            workspace_obj["name"]: resp.get("value"),
                            "capacityName": capacity_name,
                        }
                    )
            else:
                print(
                    f"api response code other than success, {api_response.status_code}"
                )

        except Exception as e:
            print(f"Unexpected failure getting API response:: {e}")
            raise

    if reports_final_list:
        write_json(reports_final_list, f"{capacity_name}_reports.json")


def main() -> None:
    """
    ADMIN API ONLY
    for capacity listed in json_files,
    open file and loop through workspace objects getting
        the reports for each workspace
    Need to update capacity workspaces json before running
    due to number of workspaces, running short of API calls
        will use mega_test.json as input
    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access()

    json_files = [
        "file1_workspaces.json",
    ]
    for json_file in json_files:
        p = Path.cwd().joinpath("json", json_file)
        d = json_data(p)
        get_workspace_reports(pbi_access_token, d, json_file.split("_")[0])


if __name__ == "__main__":
    main()
