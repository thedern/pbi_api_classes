from src.support_classes.powerbi_api_crud_class import BiAPI


class PbiDataSource(BiAPI):
    def __init__(self, access_token) -> None:
        """
        This code defines a PbiDataSource class for interacting with Power BI
        data sources and gateways via API calls.
        It provides methods to display output,
        retrieve and update data source and gateway information,
        and manage user roles for data sources.

        Inherits from BiAPI to leverage API

        :param access_token: PBI access token
        :type access_token: str

        """
        self.access_token = access_token

    @staticmethod
    def display_std_out(title, response) -> None:
        """
        displays info to STDOUT

        :param title: title for stdout display
        :type title: str
        :param response: dict
        :type response: dict
        """
        try:
            if response.get("value", None):
                print(title)
                for item in response["value"]:
                    print(item)
            else:
                print(f"{title}:: 'None'")
        except Exception as e:
            print(f"Excpection:: {e}")

    def get_gateway_data(self, response) -> list:
        """
        For datasource dict in response[values] list,
            gets gateway data

        :param response: list of objects
        :type response: list
        :return: list of objects
        :rtype: list
        """

        updatedValue = []
        try:
            for data_source_dict_item in response["value"]:
                if "gatewayId" in data_source_dict_item:
                    powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/gateways/{data_source_dict_item['gatewayId']}"
                    api_response = super().query_api(
                        powerbi_api_endpoint, self.access_token
                    )
                    if api_response.get("name", None):
                        print(
                            f"GW ID: {data_source_dict_item['gatewayId']}; GATEWAY: {api_response['name']}"
                        )
                        data_source_dict_item["gatewayName"] = api_response["name"]
                        updatedValue.append(data_source_dict_item)
                    else:
                        print(
                            f"GW ID: {data_source_dict_item['gatewayId']}; GW NAME: is NONE!"
                        )
                        data_source_dict_item["gatewayName"] = None
                        updatedValue.append(data_source_dict_item)
                else:
                    print("GATEWAY_ID: is NONE!")
                    data_source_dict_item["gatewayName"] = None
                    updatedValue.append(data_source_dict_item)

            response["value"] = updatedValue
            return response["value"]

        except Exception as e:
            print(f"Exception:: {e}")

    def get_datasources(self, datasetId) -> list:
        """
        For dataset, get underyling data source metadata

        :param datasetId: unique identifier of dataset
        :type datasetId: str
        :return: list of datasoure objects
        :rtype: list
        """
        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/datasets/{datasetId}/datasources"
        )

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                self.display_std_out("DATASOURCES::", api_response)
                # get gateway(s) for datasources
                return self.get_gateway_data(api_response)
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def update_datasource_users(
        self, datasource_id, active_directory_id, role
    ) -> object:
        """
        for the given active_directory_id (user id or group id), update
        the data source per the role provided

        :param datasource_id: identifier of datasource
        :type datasource_id: str
        :param active_directory_id: id of user or group in AD
        :type active_directory_id: str
        :param role: ACLs on datasource
        :type role: str
        :return: api response
        :rtype: object
        """
        fabric_api_endpoint = f"https://api.fabric.microsoft.com/v1/connections/{datasource_id}/roleAssignments/{active_directory_id}"
        payload = {"role": role}

        try:
            if api_response := super().patch_to_api(
                payload, fabric_api_endpoint, self.access_token
            ):
                return api_response
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def add_datasource_users(
        self, datasource_id, active_directory_id, role, type
    ) -> object:
        """
        for the given active_directory_id (user id or group id), update
        the data source per the role provided

        :return: api response
        :rtype: obj
        """
        fabric_api_endpoint = f"https://api.fabric.microsoft.com/v1/connections/{datasource_id}/roleAssignments"
        payload = {
            "principal": {"id": active_directory_id, "type": type},
            "role": role,
        }

        try:
            if api_response := super().post_to_api(
                payload, fabric_api_endpoint, self.access_token
            ):
                return api_response
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def get_gateway_datasources(self, gws) -> list:
        """
        for each gw, get all datasources

        :param gws: dict of gw ids
        :type gws: dict
        :return: list of datasources per gw
        :rtype: list
        """

        gw_response_list = []

        try:
            for gw_id in gws.values():
                powerbi_api_endpoint = (
                    f"https://api.powerbi.com/v1.0/myorg/gateways/{gw_id}/datasources"
                )

                api_response = super().query_api(
                    powerbi_api_endpoint, self.access_token
                )
                gw_response_list.append({gw_id: api_response["value"]})

            return gw_response_list
        except Exception as e:
            print(f"Exception:: {e}")
