import requests
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate


def refresh_ds(token, workspace_id, dataset_id):
    """
    Refresh dataset
    https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/refresh-dataset-in-group
    NOTE: notifyOption in header is required but not supported for SPN

    :param token: PowerBi Access Token
    :type token: str
    :param workspace_id: Workspace ID
    :type workspace_id: str
    :param dataset_id: Dataset ID
    :type dataset_id: str
    """

    # static code
    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"notifyOption": "NoNotification", "retryCount": 3}

    try:
        api_response = requests.post(api_endpoint, headers=headers, json=payload)
        if api_response.status_code in {200, 201, 202}:
            return api_response
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def main():
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access()

    # replace these with variable input
    wksp_id = ""
    model_id = ""
    resp = refresh_ds(pbi_access_token, wksp_id, model_id)
    print(f"api refresh response: '{resp}'")


if __name__ == "__main__":
    main()
