import datetime

from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_workspace_class import PbiWorkspace
from src.support_classes.azure_blob_class import AzureBlobStorage
from src.support_utils.write_file import write_json

azure_obj = AzureBlobStorage("<blob storage account>")
auth_obj = PowerbiAuthenticate()
pbi_access_token = auth_obj.generate_access("no-passwd")
workspace_object = PbiWorkspace(pbi_access_token)
master_workspace_list = []

# generate record timestamp based on program execution time
now = datetime.datetime.now()
record_timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")


def process_api_response(_s) -> None:
    """
    increment _s by adding 5000 and call get_tenant_ws

    :param _s: number of records to skip
    :type _s: int
    """
    _s += 5000
    get_tenant_ws(_s)


def get_tenant_ws(skipped_num=0) -> None:
    """
    Together with 'process_api_response' recursively gets all Workspaces;
    skipping the first 'n' records as indicated by 'skipped_num'
    stops when no more records are returned

    :param skipped_num: number of records, defaults to 0
    :type skipped_num: int, optional
    """
    if api_response_list := workspace_object.get_all_workspaces_as_admin(skipped_num):
        master_workspace_list.extend(api_response_list)
        process_api_response(skipped_num)
    else:
        print("processing complete")


def capacity_mapper(wkspc_obj):
    """
    for workspace objects assigned to a capacity, add capacity friendly name

    :param wkspc_obj: workspace meta data
    :type wkspc_obj: dict
    :return: updated workspace object
    :rtype: dict
    """

    # capacity ID to name map
    capacity_dict = {
        "<capacity id>": "name",
    }
    cap_id = wkspc_obj.get("capacityId").lower()
    if cap_id in capacity_dict:
        wkspc_obj["capacityDisplayName"] = capacity_dict.get(cap_id)
    return wkspc_obj


def get_workspace_id_timestamp(a_master) -> list:
    """
    creates a list of workspace id's and program execution timestamps for PBI reports
    :param a_master: list of all workspace objects
    :type a_master: list
    :return: list of workspace ids and program execution timestamp objects
    :rtype: list
    """
    timestamp_list = []
    timestamp_list.extend(
        {"workspace_id": workspace["id"], "record_timestamp": record_timestamp}
        for workspace in a_master
    )
    return timestamp_list


def main() -> None:
    """
    GETS ALL TENANT WORKSPACES REGARDLESS OF TYPE
    Writes to JSON and uploads JSON to Azure Blob Storage
    """
    get_tenant_ws()
    augmented_master = []

    # loop and add capacity name to ws object
    capacity_ws_list = [
        capacity_mapper(ws)
        for ws in master_workspace_list
        if ws.get("isOnDedicatedCapacity")
    ]

    # create list of all personal worspaces
    personal_ws_list = []
    personal_ws_list.extend(
        ws for ws in master_workspace_list if not ws.get("isOnDedicatedCapacity")
    )

    # combine lists in to master list
    augmented_master.extend(capacity_ws_list)
    augmented_master.extend(personal_ws_list)

    workspace_timestamp = get_workspace_id_timestamp(augmented_master)

    write_json(augmented_master, "mega_test.json")
    write_json(workspace_timestamp, "workspace_timestamp.json")

    # upload to blob storage
    azure_obj.write_blob("json", "mega_test.json")
    azure_obj.write_blob("json", "workspace_timestamp.json")
    azure_obj.list_blobs()
    print("DONE!!!!")


if __name__ == "__main__":
    main()
