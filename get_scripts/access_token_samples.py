import os
import msal
import requests
from dotenv import load_dotenv
import json


def generate_access_token() -> str:
    """
    https://learn.microsoft.com/en-us/azure/databricks/dev-tools/service-prin-aad-token
    Authenticates into DBX directly using SPN which has been added
    to a workspace

    scope: dbx default
    grant_type: "client credentials"; indicates exchange of clientid/secret
    for access token

    format: "application/x-www-form-urlencoded"; transforms key-value pairs
    into a query string format
    """

    load_dotenv(".env", override=True)
    spn_app_id = os.getenv("spn_app_id")
    spn_secret = os.getenv("spn_secret")
    azure_tenant_id = os.getenv("azure_tenant_id")

    url = f"https://login.microsoftonline.com/{azure_tenant_id}/oauth2/v2.0/token"
    payload = {
        "client_id": spn_app_id,
        "client_secret": spn_secret,
        "grant_type": "client_credentials",
        "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # generate access token - post (msal uses client method)
    try:
        api_response = requests.post(url, headers=headers, data=payload)
        if api_response.status_code in {200, 201, 202}:
            response = json.loads(api_response.text)
            if response.get("access_token"):
                return response.get("access_token", None)
        else:
            print(f"API response: {api_response.status_code}")

    except Exception as e:
        print(f"Exception:::  {e}")


def generate_access_token_msal() -> str:
    """
    utility function used to generate an api access token
    assumes the use of an .env file containing IDs and secret
    :return: PBI api token string value
    """
    # protected args
    # force .env reload
    load_dotenv(".env", override=True)
    app_id = os.getenv("app_id")
    secret = os.getenv("secret")
    azure_tenant_id = os.getenv("azure_tenant_id")

    # urls
    base_url = f"https://login.microsoftonline.com/{azure_tenant_id}"
    scopes = ["https://analysis.windows.net/powerbi/api/.default"]

    # generate access token
    client = msal.ConfidentialClientApplication(
        app_id, authority=base_url, client_credential=secret
    )

    # return access token
    response = client.acquire_token_for_client(scopes=scopes)
    return response.get("access_token")
