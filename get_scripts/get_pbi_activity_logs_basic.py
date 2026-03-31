from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_api_log_class import PbiLogs
from src.support_classes.azure_blob_class import AzureBlobStorage
from src.support_utils.write_file import write_json
from rich.console import Console
from src.support_utils.console_themes import custom_theme
import time
import sys


def validate_input(console_in, msg) -> str:
    """
    validate user input as digits

    :param console_in: console object
    :type console_in: obj
    :param msg: on screen message
    :type msg: str
    :return: date values
    :rtype: str
    """
    input_value = "wrong"
    while not input_value.isdigit():
        input_value = console_in.input(msg)
        if not input_value.isdigit():
            print("please enter a valid day/month/year")
    return input_value


def generate_activity_list(access_token) -> list:
    """

    Gets activity logs for desired day
    Writes to stdout, json, xlsx

    :param access_token: PBI access token
    :type access_token: str
    :return: list of workspace objects
    :rtype: list

    """
    try:
        console = Console(theme=custom_theme)
        log_obj = PbiLogs(access_token)

        print("Enter date for which Activity Logs are required \n")
        y = validate_input(console, "[warning]-enter year (yyyy):  ")
        m = validate_input(console, "[warning]-enter month (mm):  ")
        d = validate_input(console, "[warning]-enter day (dd):  ")

        print()

        start_timestamp = f"{y}-{m}-{d}T00:00:00"
        end_timestamp = f"{y}-{m}-{d}T23:59:59"

        # API enpoint must be passed to class as it changes with continuation token
        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/activityevents?startDateTime='{start_timestamp}'&endDateTime='{end_timestamp}'"

        with console.status(
            "[header]Running PBI Activity Logs..[/header]", spinner="runner"
        ):
            api_response = log_obj.get_pbi_activity_logs(powerbi_api_endpoint)
            console.print(
                "[info]Activity log collection completed, check json/logs* file[/info]"
            )
            console.print(
                f"[info]Log entries:[/info] [number]{len(api_response)}[/number]"
            )

        time.sleep(1)

        file_name = start_timestamp.split("T")[0]
        write_json(api_response, f"activity_string_{file_name}.json")
        # write_excel(api_response, f"activity_string_{file_name}.xlsx")

        # write to blob storage
        azure_obj = AzureBlobStorage("<blob storage account>")
        azure_obj.write_blob(
            "json", f"activity_string_{file_name}.json", "activity_logs"
        )
        azure_obj.list_blobs()
        print("DONE!!!!")

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Error unable to get activity logs: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
        time.sleep(2)


if __name__ == "__main__":
    """
    Entry point
    """
    auth_obj = PowerbiAuthenticate()
    pbi_access_token = auth_obj.generate_access("no-passwd")
    generate_activity_list(pbi_access_token)
