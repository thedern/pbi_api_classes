from src.support_classes.powerbi_api_crud_class import BiAPI
from rich.pretty import pprint


class PbiDataset(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi dataset Class
        Subclasses BiAPI
        This class is used for PowerBi dataset operations

        :param access_token: PBI access token
        :type access_token: str
        """

        self.access_token = access_token

    @staticmethod
    def create_data_object(name, id, configured_by, data) -> dict:
        """
        Static method to create data object for further processing in identifying datasets within workspaces

        :param name: dataset name
        :type name: str
        :param id: dataset id (unused)
        :type id: str
        :param data: dataset metadata
        :type data: dict
        :param users: users assigned to dataset
        :type users: list
        :return: dataset object
        :rtype: dict
        """
        return {"name": name, "configured by": configured_by, "datasources": data}

    @staticmethod
    def display_std_out(title, response) -> None:
        """
        displays dataset info to STDOUT

        :param title: title for stdout display
        :type title: str
        :param response: list of objects
        :type response: list
        """
        try:
            if response.get("value", None):
                print(title)
                for item in response["value"]:
                    print(item)
            else:
                print(f"{title}:: 'None'")
        except Exception as e:
            print(f"Exception:: {e}")

    def get_dataset_users_admin(self, ds_id) -> list:
        """
        Retuns users for a given dataset

        :param ds_id: dataset id
        :type ds_id: str
        :return: arrary of dataset users
        :rtype: list
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{ds_id}/users"
        )

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                return api_response.get("value", None)
            print("No users returned by API")
            return None
        except Exception as e:
            print(f"Exception:: {e}")

    def get_dataset_refresh_history(self, workspace_id, dataset_id) -> list:
        """
        Non-admin call requires token generated with admin password
        Get the refresh history of a specific dataset

        :param workspace_id: id of target workspace
        :type workspace_id: str
        :param dataset_id: id of target dataset
        :type dataset_id: str
        :return: array of refresh history objects
        :rtype: list
        """

        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                return api_response.get("value", None)
            print("No refresh history returned by API")
            return None
        except Exception as e:
            print(f"Exception:: {e}")

    def refresh_dataset(self, workspace_id, dataset_id) -> str:
        """
        Non-admin call requires token generated with admin password
        Post request to API triggering a dataset connection

        :param workspace_id: id of target workspace
        :type workspace_id: str
        :param dataset_id: id of target dataset
        :type dataset_id: str
        :return: api response code
        :rtype: str
        """

        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/refreshes"
        payload = {"notifyOption": "NoNotification", "retryCount": 3}

        try:
            api_response = super().post_to_api(
                payload, powerbi_api_endpoint, self.access_token
            )
            if api_response.status_code in {200, 201, 202}:
                return api_response.status_code
            print(f"api response code other than success, {api_response.status_code}")
        except Exception as e:
            print(f"Exception:: {e}")

    def get_ws_dataset(self, workspace_id) -> list:
        """
        Returns datasets for a single workspace

        :param workspace_id: id of target workspace
        :type workspace_id: str
        :return: dataset array
        :rtype: list
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_id}/datasets"
        )

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                return api_response.get("value", None)
            print("No datasets returned by API")
            return None
        except Exception as e:
            print(f"Exception:: {e}")

    def get_dataset_datasources(self, dataset_id) -> list:
        """_summary_

        :param dataset_id: identifier of dataset
        :type dataset_id: str
        :return: list of datasources
        :rtype: list
        """

        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/datasets/{dataset_id}/datasources"

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                return api_response.get("value", None)
            print("No datasources returned by API")
            return None
        except Exception as e:
            print(f"Exception:: {e}")

    def get_dataset_by_id(self, ds_id):
        """
        Gets dataset/model's metadata

        :param ds_id: dataset id
        :type ds_id: str
        """

        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/datasets/{ds_id}"

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                # return whole repsonse, not [value]
                return api_response
            print("No datasources returned by API")
            return None
        except Exception as e:
            print(f"Exception:: {e}")

    def get_dataset_users(self, datasetId) -> dict:
        """
        For dataset, gets dataset users

        :param datasetId: unique identifier of dataset
        :type datasetId: id
        :return: dictionary of dataset users
        :rtype: dict
        """
        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/datasets/{datasetId}/users"
        )

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                self.display_std_out("USERS::", api_response)
                return api_response
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def refresh_report(self, cap_id, refresh_duration) -> dict:
        """
        Reports on dataset refreshes within the designated capacity

        :param cap_id: unique identifier of the capacity
        :type cap_id: str
        :param refresh_duration: number of seconds to test against
        :type refresh_duration: int
        :return: dictionay of dataset objects
        :rtype: dict
        """
        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/capacities/{cap_id}/refreshables?$expand=group&$filter=averageDuration gt {refresh_duration}"
        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                return api_response
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def disable_dataset_refresh(self, dataset_id) -> tuple:
        """
        Disable scheduled refresh by dataset

        :param dataset_id: unique identifier of dataset
        :type dataset_id: str
        :return: tuple: (dataset_id, status code)
        :rtype: tuple
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshSchedule"
        )
        payload = {"value": {"enabled": False}}

        try:
            if api_response := super().patch_to_api(
                payload, powerbi_api_endpoint, self.access_token
            ):
                return (dataset_id, api_response)
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )

        except Exception as e:
            print(f"Exception:: {e}")

    def get_datasets_per_ws(self, groupid) -> list:
        """
        For a given workspace return all datasets AND datasource AND gateway information and write to a JSON file
        makes method calls to: get_dataset; get_datasources/get_gateway_data

        :param groupid: unique workspace ID
        :type groupid: str
        :return: list of dataset/datasource/gateway objects
        :rtype: list
        """

        try:
            dataset_response = self.get_dataset(groupid)
            data_objects = []
            data_sets = dataset_response.get("value", None)
            if data_sets:
                for ds in data_sets:
                    print(f"{ds['name']}:: {ds['id']}, {ds['configuredBy']}")
                    datasources_w_gateway = self.get_datasources(ds["id"])
                    obj = self.create_data_object(
                        ds["name"], ds["id"], ds["configuredBy"], datasources_w_gateway
                    )
                    data_objects.append(obj)
                    print("-------------------------", "\n")
                return {"datasets": data_objects}
        except Exception as e:
            print(f"Exception:: {e}")

    def get_dataset(self, groupid) -> dict:
        """
        For the workspaces id passed to the method, returns basic dataset information only

        :param groupid: unique workspace ID
        :type groupid: str
        :return: dict of dataset objects
        :rtype: dict
        """
        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{groupid}/datasets"
        )

        try:
            if api_response := super().query_api(
                powerbi_api_endpoint, self.access_token
            ):
                return api_response
            else:
                print(f"Failed to create workspace. API Repsonse:: {api_response}")
        except Exception as e:
            print(f"Exception:: {e}")
