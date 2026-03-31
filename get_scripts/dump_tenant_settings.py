import sys
import time

from rich.console import Console
from rich.pretty import pprint

from src.support_classes.powerbi_api_crud_class import BiAPI
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.console_themes import custom_theme
from src.support_utils.write_file import write_json


def generate_tenant_settings_list(access_token) -> dict:
    """
    Returns an api response object of all tenant settings and writes to a JSON file

    :param access_token: PBI access token
    :type access_token: str
    :return: api reponse dictionary
    :rtype: dict
    """

    try:
        fabric_api_endpoint = "https://api.fabric.microsoft.com/v1/admin/tenantsettings"
        console = Console(theme=custom_theme)
        api_obj = BiAPI()

        api_response = api_obj.query_api(fabric_api_endpoint, access_token)

        for item in api_response["tenantSettings"]:
            pprint(item)
        console.print(
            f"[info] Number of tenant settings returned:[/info] [number]{len(api_response['tenantSettings'])}[/number]"
        )
        time.sleep(2)
        write_json(api_response, "tenant_settings.json")

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Unable to acquire tenant settings: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
        time.sleep(2)


if __name__ == "__main__":
    """
    Entry point
    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("no-passwd")
    generate_tenant_settings_list(pbi_access_token)
