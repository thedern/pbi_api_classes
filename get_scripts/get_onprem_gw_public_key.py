import requests
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate


def get_gw_metadata(token, gw) -> str:
    """ """

    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/gateways/{gw}"
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
    """
    main function of sample code

    "gateway1": "<id>",

    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("no-passwd")

    gateway = "<id>"

    if gateway_resp := get_gw_metadata(pbi_access_token, gateway):
        print(f"api response: '{gateway_resp['publicKey']}'")


if __name__ == "__main__":
    main()
