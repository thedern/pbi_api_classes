from src.support_classes.powerbi_api_crud_class import BiAPI
from rich.pretty import pprint


class PbiWorkspace(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi Workspace Class
        Subclasses BiAPI
        This class is used for PowerBi Workspace operations

        :param access_token: PBI access token
        :type access_token: str
        """
        # self.rest_api = rest_class
        self.access_token = access_token

    def disable_log_analytics(self, workspace_id):
        """
        Configure Azure Log Analytics for workspace specified

        :param workspace_id: unique workspace identifier
        :type workspace_id: str
        :return: tuple (workspace_id, api_response)
        :rtype: tuple
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_id}"
        )

        try:
            # DNA prod log analytics subscription metadata
            payload = {"logAnalyticsWorkspace": None}

            if api_response := super().patch_to_api(
                payload, powerbi_api_endpoint, self.access_token
            ):
                return (workspace_id, api_response)
            else:
                print(f"Failed to set log analytics. API Repsonse:: {api_response}")
        except Exception as e:
            print(f"Exception:: {e}")

    def set_log_analytics(self, workspace_id) -> tuple:
        """
        Configure Azure Log Analytics for workspace specified

        :param workspace_id: unique workspace identifier
        :type workspace_id: str
        :return: tuple (workspace_id, api_response)
        :rtype: tuple
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_id}"
        )

        try:
            # DNA prod log analytics subscription metadata
            payload = {
                "logAnalyticsWorkspace": {
                    "subscriptionId": "fdd748dd-5ab3-4158-ab96-ba3adadd6204",
                    "resourceGroup": "use2rgr004mdpprd01",
                    "resourceName": "use2log004mdpprd01",
                }
            }

            if api_response := super().patch_to_api(
                payload, powerbi_api_endpoint, self.access_token
            ):
                return (workspace_id, api_response)
            else:
                print(f"Failed to set log analytics. API Repsonse:: {api_response}")
        except Exception as e:
            print(f"Exception:: {e}")

    def workspace_generator(self, workspace_names) -> list:
        # sourcery skip: class-extract-method
        """
        Creates workspaces from a list of workspace names

        :param workspace_names: list of workspaces to create
        :type workspace_names: list
        :return: (workspace name, api response object indicating success/failure)
        :rtype: list
        """

        powerbi_api_endpoint = (
            "https://api.powerbi.com/v1.0/myorg/groups?workspaceV2=True"
        )

        results = []
        try:
            for workspace_name in workspace_names:

                payload = {"name": workspace_name}

                if api_response := super().post_to_api(
                    payload, powerbi_api_endpoint, self.access_token
                ):
                    results.append((workspace_name, api_response))
                else:
                    print(f"Failed to create workspace. API Repsonse:: {api_response}")
            return results
        except Exception as e:
            print(f"Exception:: {e}")

    def get_all_workspaces(self) -> list:
        """
        Returns a list of all workspace objects in tenant
        Will not return personal workspaces. Its more efficient to not parse those
        as capacity workspaces will not be included in that subset

        :return: list of workspace objects
        :rtype: list
        """

        powerbi_api_endpoint = "https://api.powerbi.com/v1.0/myorg/groups"

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                return list(api_response.values())[2]
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def get_all_workspaces_as_admin(self, skip) -> list:
        """
        Returns a list of all workspace objects in tenant
        Uses admin api calls in batches of 5000
        If you have more the 5,000 workspaces, then use the $skip parameter to
        page through the remaining workspaces with a batch size of 5,000.

        :return: list of workspace objects
        :rtype: list
        """

        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/Groups?$top=5000&$skip={skip}&$expand=users,reports,dashboards,datasets"

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if api_response.get("value"):
                return list(api_response.values())[2]
            print("out of workspaces to collect")
            return None
        except Exception as e:
            print(f"Exception:: {e}")

    def check_for_ws_by_name(self, ws_names) -> dict:
        """
        Checks for existing workspace(s) by name.  Indicates if workspace already exists

        :param ws_names: list of workspace names
        :type ws_names: list
        :return: map of workspaces 'found', includes WS ID and Capacity ID if exists
        :rtype: dict
        """

        try:
            existing_workspaces_list = self.get_all_workspaces()

            results_dict = {}
            for workspace in ws_names:
                results_dict[workspace] = None
                for current_ws in existing_workspaces_list:
                    if any(True for k, v in current_ws.items() if v == workspace):
                        results_dict[workspace] = (
                            "found",
                            current_ws.get("id", None),
                            current_ws.get("capacityId", None),
                        )

            # sanity check
            for k, v in results_dict.items():
                pprint(f"WORKSPACE NAME: {k} | WORKSPACE METADATA: {v}")

            return results_dict
        except Exception as e:
            print(f"Exception:: {e}")

    def get_workspace_by_id(self, ws_id) -> dict:
        """
        Returns a workspace by workspace ID
        limited to workspaces user has access to.  Example: Will not return personal workspaces

        :param ws_id: unqiue workspace idenfier
        :type ws_id: str
        :return: workspace objects
        :rtype: dict
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{ws_id}"
        )

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                return api_response
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")
