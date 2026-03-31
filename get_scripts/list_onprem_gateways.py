import time
import sys
import json
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_api_crud_class import BiAPI
from src.support_utils.console_themes import custom_theme
from rich.console import Console


def generate_gateway_list(access_token) -> None:
    """
    Displays primary on-prem gateway of each cluster.  API does not return all gateway members

    :param access_token: PBI access token
    :type access_token: str
    """

    try:
        api_obj = BiAPI()
        console = Console(theme=custom_theme)
        powerbi_api_endpoint = "https://api.powerbi.com/v1.0/myorg/gateways"

        api_response = api_obj.query_api(powerbi_api_endpoint, access_token)

        if api_response["value"]:
            for metadata_dict in api_response["value"]:
                console.print("[header]PRIMARY GATEWAY:[/header]")
                console.print(
                    f"[info]Name: {metadata_dict['name']}; ID: {metadata_dict['id']}[/info]"
                )
                powerbi_api_gateway_endpoint = (
                    f"https://api.powerbi.com/v1.0/myorg/gateways/{metadata_dict['id']}"
                )
                gw_api_response = api_obj.query_api(
                    powerbi_api_gateway_endpoint, access_token
                )

                gw_metadata = json.loads(gw_api_response["gatewayAnnotation"])
                console.print(
                    f"[info]Gateway Version: {gw_metadata['gatewayVersion']}; Machine: {gw_metadata['gatewayMachine']} \n-Gateway Status: {gw_api_response['gatewayStatus']}[/info]"
                )
        else:
            print("Empty response from gateway query, check API call.")

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Unable to list gateways: {exc_type, exc_obj, exc_tb}. Trace for more")
        time.sleep(2)


if __name__ == "__main__":
    """
    Entry point
    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("no-passwd")
    generate_gateway_list(pbi_access_token)
