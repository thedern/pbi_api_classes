from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_api_crud_class import BiAPI
from src.support_utils.write_file import write_json
from rich import print
from rich.pretty import Pretty
from rich.panel import Panel
from rich.console import Console
from src.support_utils.console_themes import custom_theme
import time
import sys


def generate_tenant_domains_list(access_token) -> dict:
    """
    Returns a dictionary of capacity domains and writes them to a JSON file

    :param access_token: PBI access token
    :type access_token: str
    :return: capacity domain objects as python dictionaries
    :rtype: dict
    """

    try:
        console = Console(theme=custom_theme)
        fabric_api_endpoint = "https://api.fabric.microsoft.com/v1/admin/domains"
        api_obj = BiAPI()

        api_response = api_obj.query_api(fabric_api_endpoint, access_token)
        pretty = Pretty(api_response)
        panel = Panel(pretty, title="Domains")
        print(panel)
        console.print(
            f'[info]Number of Domains:[/info] [number]{len(api_response["domains"])}[/number]'
        )
        time.sleep(2)
        write_json(api_response, "tenant_domains.json")

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Unable to acquire tenant domains: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
        time.sleep(2)


if __name__ == "__main__":
    """
    Entry point
    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("no-passwd")
    generate_tenant_domains_list(pbi_access_token)
