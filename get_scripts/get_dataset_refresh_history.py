import requests
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate


def refresh_ds_history(token, dataset_id, wkspc):
    """
    Get refresh history from specifi dataset in workspace
    """

    # static code
    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{wkspc}/datasets/{dataset_id}/refreshes"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            return api_response
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def main():
    # SPN must have 'member' role on Workspace
    # replace these with variable input
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access()
    model_id = ""
    grp = ""
    resp = refresh_ds_history(pbi_access_token, model_id, grp)

    for refresh_obj in resp.json()["value"]:
        print(refresh_obj, "\n")


if __name__ == "__main__":
    main()
