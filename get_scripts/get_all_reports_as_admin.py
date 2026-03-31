import requests
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate

auth_obj = PowerbiAuthenticate()


def get_reports_as_admin(token) -> dict:
    """ """

    api_endpoint = "https://api.powerbi.com/v1.0/myorg/admin/reports"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response.json()
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def main():
    auth_obj = PowerbiAuthenticate()
    if tkn := auth_obj.generate_access("no-passwd"):
        reports = get_reports_as_admin(tkn)
        print(reports)


if __name__ == "__main__":
    main()
