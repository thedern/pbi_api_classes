import time
import sys
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_api_dataset_class import PbiDataset
from src.support_utils.open_file import open_capacities_json
from src.support_utils.write_file import write_json
from rich.pretty import pprint
from rich.console import Console
from src.support_utils.console_themes import custom_theme


def list_long_running_refreshes(access_token) -> list:
    """
    Generate a list of long running workspaces from selected capacity
    Capacity ID comes from input_values.json
    Default is to report on refreshes > 10 mins.

    :param access_token: PBI axcess token
    :type access_token: str
    :return: list of workspace objects
    :rtype: list
    """

    # todo:  NEED to update with a process to read from the capacity json files
    # read input data from JSON
    if not (input_values := open_capacities_json()):
        print(f"Input Values missing: {input_values}")
        time.sleep(2)
        return

    try:
        # create objects
        console = Console(theme=custom_theme)
        dataset_obj = PbiDataset(access_token)
        capacity_list = input_values["value"]
        print("Checks for dataset refresh duration greater than seconds entered.")
        duration = console.input("[warning]-enter a number of seconds:  ")
        int(duration)

        for capacity in capacity_list:
            # omit 'Premium Per User - Reserved'
            # API recognizes uppercase IDs only
            if capacity["id"] != "<exclude this capacity id if needed>":
                api_response = dataset_obj.refresh_report(
                    capacity["id"].upper(), duration
                )
                for item in api_response["value"]:
                    pprint(item)
                console.print(
                    f'[info] Number of refreshes returned:[/info] [number]{len(api_response["value"])}[/number]'
                )

                time.sleep(2)
                write_json(
                    api_response,
                    f"{capacity['displayName']}_long_running_refreshes.json",
                )

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Error listing long running refreshes: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
        time.sleep(2)


if __name__ == "__main__":
    """
    Entry point
    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access()
    list_long_running_refreshes(pbi_access_token)
