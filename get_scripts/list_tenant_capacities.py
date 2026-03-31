from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_api_crud_class import BiAPI
from src.support_classes.azure_blob_class import AzureBlobStorage
from src.support_classes.logger_class import Logger
from src.support_utils.write_file import write_json
from rich import print
from rich.pretty import Pretty
from rich.panel import Panel
from rich.console import Console
from src.support_utils.console_themes import custom_theme
import time
import sys

# instantiate logger
logger_obj = Logger()


def generate_tenant_capacity_list(access_token) -> dict:
    """
    Returns a dictionary of capacity objects and writes them to a JSON file
    and Azure blob storage.

    :param access_token: PBI access token
    :type access_token: str
    :return: powerbi capacity objects as python dictionaries
    :rtype: dict
    """

    try:
        blob_acct = ""
        console = Console(theme=custom_theme)
        fabric_api_endpoint = "https://api.fabric.microsoft.com/v1/capacities"
        storage_obj = AzureBlobStorage(blob_acct)
        api_obj = BiAPI()

        api_response = api_obj.query_api(fabric_api_endpoint, access_token)
        pretty = Pretty(api_response["value"])
        panel = Panel(pretty, title="Capactities")
        print(panel)
        console.print(
            f'[info]Number of Capacities:[/info] [number]{len(api_response["value"])}[/number]'
        )
        time.sleep(2)
        write_json(api_response, "tenant_capacities.json")
        # write to azure blob storage
        # storage_obj.write_blob("json", "tenant_capacities.json", "api_inputs")
        # for capacity in api_response["value"]:
        #     logger_obj.logger_capacity(capacity)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger_obj.logger_error((__name__, exc_type, exc_obj, exc_tb))
        print(
            f"Unable to generate capacity list: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
        time.sleep(2)


if __name__ == "__main__":
    """
    Entry point
    """
    auth_obj = PowerbiAuthenticate()
    # adm password required
    pbi_access_token = auth_obj.generate_access()
    generate_tenant_capacity_list(pbi_access_token)
