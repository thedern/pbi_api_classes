import requests
import sys
import time

from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.open_file import open_named_json
from src.support_utils.write_file import write_json

auth_obj = PowerbiAuthenticate()
master_list = []


def get_workspace_reports(headers, group_id) -> str:
    """
    Gets all reports for specific workspace

    :param token: access token
    :type token: str
    :param group_id: workspace ID GUID
    :type group_id: str
    :return: report metadata json
    :rtype: str
    """

    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports"

    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response.json()
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def get_report_users(headers, report_id):
    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/reports/{report_id}/users"

    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response.json()
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def update_master_list(rpt):
    master_list.append(
        {
            "ReportName": rpt["name"],
            "ReportCreator": rpt.get("createdBy", None),
            "ReportType": rpt.get("reportType", None),
            "DatasetID": rpt.get("datasetId", None),
            "ReportUsers": rpt.get("value", None),
        }
    )


def single_report(workspace_id, headers):
    # Single Workspace run

    json_name = "reports_and_users"

    if report_resp := get_workspace_reports(headers, workspace_id):
        for report_object in report_resp["value"]:
            report_users = get_report_users(headers, report_object["id"])
            update_master_list(report_users)
            # to not overrun api
            time.sleep(1)
        for object in master_list:
            print(object)
        write_json(master_list, f"{json_name}.json")


def get_report_subscribers(headers, report_id):
    # add in subscriptions https://api.powerbi.com/v1.0/myorg/admin/reports/{reportId}/subscriptions
    pass


def get_report_ids(workspace_list):
    """
    get the id for each report

    :param workspace_list: list of workspace objects
    :type workspace_list: list
    :return: list of ids
    :rtype: list
    """
    reports_collector = []
    for workspace_obj in workspace_list:
        if reports_list := workspace_obj.get("reports"):
            reports_collector.extend(report.get("id") for report in reports_list)
    return reports_collector


def run_single_report(headers):
    # single reports
    single_workspace_id = "<id>"
    single_report(single_workspace_id, headers)


def run_multiple_reports(headers):

    counter = 0
    report_counter = 0
    workspace_object_list = open_named_json("mega_test.json")

    report_ids = get_report_ids(workspace_object_list)
    print(len(report_ids))

    for report_id in report_ids:
        report_counter += 1
        if counter < 199:
            report_users = get_report_users(headers, report_id)
            counter += 1
            update_master_list(report_users)
            time.sleep(1)
        else:
            # sleep, reset counter, refresh access token
            for i in range(3600, 0, -1):  # 3600
                sys.stdout.write(f"{str(i)} ")
                sys.stdout.flush()
                time.sleep(1)
            counter = 0
            # reset headers
            pbi_access_token = auth_obj.generate_access("no-passwd")
            headers = {"Authorization": f"Bearer {pbi_access_token}"}
            print("**** resuming api calls ****")

    json_name = "all_reports_and_users"
    write_json(master_list, f"{json_name}.json")


def main() -> None:
    """
    main function of sample code
    enter ID for workspace and report name
    API reference: https://learn.microsoft.com/en-us/rest/api/power-bi/
    NOTE:  getting workspace users in an /admin api endpoint only!
    """

    pbi_access_token = auth_obj.generate_access()
    headers = {"Authorization": f"Bearer {pbi_access_token}"}

    # run_single_report(headers)
    run_multiple_reports(headers)


if __name__ == "__main__":
    main()
