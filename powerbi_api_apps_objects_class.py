from src.support_classes.powerbi_api_crud_class import BiAPI


class PbiAppsObjects(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi Capacity Class
        Subclasses BiAPI
        This class is used for operations against the PowerBi capacity

        :param access_token: PBI access token
        :type access_token: str
        """
        self.access_token = access_token
        self.master_apps_list = []

    @staticmethod
    def clean_user_entry(user_list):
        """
        eliminate extra user information, return emails only
        :param user_list: list of user objects
        :type user_list: dict
        :return: list of user emails
        :rtype: list
        """

        return [
            {
                "displayName": user["displayName"],
                "emailAddress": user.get("emailAddress"),
            }
            for user in user_list
        ]

    def get_apps(self) -> list:
        """
        Returns list of all deployed apps

        :return: list of apps objects
        :rtype: list
        """
        powerbi_api_endpoint = "https://api.powerbi.com/v1.0/myorg/admin/apps?$top=1000"

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                # update app information with users who have access
                self.get_apps_users(api_response["value"])
                return self.master_apps_list
                # return api_response["value"]
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def get_apps_users(self, apps_list) -> None:
        """
        using app id, get users with access to app
        updates master list

        :return: None
        :rtype: list
        """

        try:
            for app in apps_list:
                powerbi_api_endpoint = (
                    f"https://api.powerbi.com/v1.0/myorg/admin/apps/{app['id']}/users"
                )

                api_response = super().query_api(
                    powerbi_api_endpoint, self.access_token
                )
                if isinstance(api_response, dict):
                    if len(api_response["value"]) > 0:
                        cleaned_users = self.clean_user_entry(api_response["value"])
                        app["users"] = cleaned_users
                    else:
                        app["users"] = "None"
                    self.master_apps_list.append(app)
                else:
                    print(
                        f"api response code other than 200. API Repsonse:: {api_response}"
                    )
        except Exception as e:
            print(f"Exception:: {e}")
