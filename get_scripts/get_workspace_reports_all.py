import requests
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.write_file import write_json


def get_workspace_reports(token, group_id) -> str:
    """
    Gets all reports for specific workspace

    :param token: Power Bi Access Token
    :type token: str
    :param group_id: workspace ID
    :type group_id: str
    :return: report metadata json
    :rtype: str
    """

    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/reports"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response.json()
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def main() -> None:
    """
    main function of sample code
    enter ID for workspace and report name
    API reference: https://learn.microsoft.com/en-us/rest/api/power-bi/
    SPN must have 'member' role on workspace
    NOTE:  No longer returns users of report, that is an /admin api endpoint only
            user's array in respose will be empty
    """

    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access()

    # constants
    workspace_id = "<ws_id>"
    # json_name = "<enter a name for your JSON>"

    if report_resp := get_workspace_reports(pbi_access_token, workspace_id):
        for report_object in report_resp["value"]:
            print(f"Report:'{report_object}'")
        print(len(report_resp["value"]))
        # write_json(report_resp, f"{json_name}.json")


if __name__ == "__main__":
    main()
