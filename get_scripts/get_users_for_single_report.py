import requests
import json
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate

auth_obj = PowerbiAuthenticate()
pbi_access_token = auth_obj.generate_access()


def get_users_for_report(token, report_id):
    """
    Gets users for a specfic report
    ADMIN API ONLY
    """

    # static code
    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/reports/{report_id}/users"
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
    report_id_guid = ""
    resp = get_users_for_report(pbi_access_token, report_id_guid)
    print(f"api response: '{resp}'")
    for item in resp.get("value"):
        print(
            f"user: {item['displayName']};  email: {item['identifier']};  permission: {item['reportUserAccessRight']}"
        )


if __name__ == "__main__":
    main()
