from src.support_classes.powerbi_api_crud_class import BiAPI


class PbiCapacity(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi Capacity Class
        Subclasses BiAPI
        This class is used for operations against the PowerBi capacity

        :param access_token: PBI access token
        :type access_token: str
        """

        self.access_token = access_token

    def get_capacity_workspaces(self, capacity) -> list:
        """
        Returns list of all Workspaces from designated capacity

        :param capacity: unique capacity identifier
        :type capacity: str
        :return: list of workspace objects
        :rtype: list
        """
        endpoint_url = (
            "https://api.powerbi.com/v1.0/myorg/admin/groups?$filter=capacityId"
        )
        powerbi_api_endpoint = f"{endpoint_url} eq '{capacity}'&$top=5000"

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                workspaces = list(api_response.values())[2]
                return [item for item in workspaces if item["state"] == "Active"]
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    @staticmethod
    def set_capacity_id(workspace_name, capacity_list) -> str:
        """
        Evaluates workspace name and returns prod or nonprod capacity id
        :param workspace_name: workspace name
        :type workspace_name: str
        :param capacity_list: list of capacity objects
        :type capacity_list: list
        :return: capacity id
        :rtype: str
        """
        if "-prod" not in workspace_name.lower():
            return capacity_list[0]["nonprod_capacity_id"]
        return capacity_list[1]["prod_capacity_id"]

    def add_ws_to_capacity(self, workspaces_to_add, capacity) -> None:
        """
        Using workspace ID, add workspace to desired capacity
        Dictionaries in list are key: value where key is ws name and value is tuple
        Tuple: ('found', workpaceId, capacityID)
        Prints a list of api response objects indicating success/failure

        :param workspaces_to_add: dictionary of workspaces to add to capacity
        :type workspaces_to_add: dict
        :param capacity: unique capacity identifier
        :type capacity: str
        """

        results = []
        try:
            for key, value in workspaces_to_add.items():
                if value[1] and value[2] is None:

                    payload = {"capacityId": self.set_capacity_id(key, capacity)}

                    powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{value[1]}/AssignToCapacity"

                    if api_response := super().post_to_api(
                        payload, powerbi_api_endpoint, self.access_token
                    ):
                        results.append((key, api_response))
                    else:
                        print(
                            f"Failed to add workspace to capacity. API Repsonse:: {api_response}"
                        )
                else:
                    print(f"Workspace {key}, already assigned to a capacity")
            if results:
                print(f" API post response(s): {results}")
        except Exception as e:
            print(f"Exception:: {e}")
