import time
import sys
from src.support_classes.powerbi_api_apps_objects_class import PbiAppsObjects
from src.support_classes.powerbi_workspace_class import PbiWorkspace
from src.support_classes.azure_blob_class import AzureBlobStorage
from src.support_utils.write_file import write_json
from rich.console import Console
from src.support_utils.console_themes import custom_theme


def generate_deployed_apps_list(access_token) -> None:
    """
    Generates a list of deployed apps and prints to STDOUT
    Writes a list of workspace objects to deployed_apps.json
    Apps list augmented to unclude workspace name and users list

    :param access_token: PBI access token
    :type access_token: str
    :param rest_class: PBI REST class
    :type rest_class: class
    """

    # storage object
    blob_acct = ""
    storage_obj = AzureBlobStorage(blob_acct)
    apps_obj = PbiAppsObjects(access_token)
    workspace_obj = PbiWorkspace(access_token)

    try:
        console = Console(theme=custom_theme)
        with console.status(
            "[header]Getting Deployed Apps...[/header]", spinner="smiley"
        ):
            # get all deployed apps and app users
            if apps := apps_obj.get_apps():
                for app in apps:
                    # get app workspace info, check for dedicated capacity
                    # gets most current workspaces from API, not blob storage json
                    if ws_name := workspace_obj.get_workspace_by_id(app["workspaceId"]):
                        # capacity true, write data
                        if ws_name["isOnDedicatedCapacity"]:
                            app["workspace_info"] = {
                                "name": ws_name["name"],
                                "id": ws_name["id"],
                                "isOnDedicatedCapacity": ws_name[
                                    "isOnDedicatedCapacity"
                                ],
                            }
                        # capacity false, write false
                        else:
                            app["workspace_info"] = {
                                "name": ws_name["name"],
                                "isOnDedicatedCapacity": "false",
                            }
                    else:
                        app["workspace_info"] = "Unable to get WS info"

                # check for apps which reside within capacity 'true' and create JSON
                if capacity_apps_list := [
                    app for app in apps if app["workspace_info"].get("id")
                ]:
                    console.print(
                        f"[info]Number of capacity apps:[/info] [number]{len(capacity_apps_list)}[/number]"
                    )
                    write_json(capacity_apps_list, "deployed_apps_capacity_only.json")

                # display total apps
                console.print(
                    f"[info]Number of deployed apps:[/info] [number]{len(apps)}[/number]"
                )
                time.sleep(2)
                write_json(apps, "deployed_apps_raw.json")
                # write to Azure storage for metadata reporting
                storage_obj.write_blob("json", "deployed_apps_raw.json")
            else:
                print("unable to get apps from API")

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(f"Unable to crre: {exc_type, exc_obj, exc_tb}. Trace for more")
        time.sleep(2)
