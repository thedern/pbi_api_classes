import os
import msal
from dotenv import load_dotenv


class GraphAuthenticate:
    def __init__(self) -> str:
        """
        PowerBi Tenant Authentication and Authorization class

        :return: PBI token
        :rtype: str
        """
        load_dotenv(".env", override=True)
        self.app_id = os.getenv("app_id")
        self.azure_tenant_id = os.getenv("azure_tenant_id")
        self.base_url = f"https://login.microsoftonline.com/{self.azure_tenant_id}"
        self.secret = os.getenv("secret")
        self.adm_user = os.getenv("adm_user")
        self.current_pwd = os.getenv("current_pwd")
        self.graph_scopes = ["https://graph.microsoft.com/.default"]

    def get_np_graph_access_token(self, client) -> str:
        try:
            # method does not require username/password
            return client.acquire_token_for_client(scopes=self.graph_scopes)

        except Exception as e:
            print(f"Unable to acquire Access Token:: {e}")
            raise

    def get_graph_access_token(self, client) -> str:
        """ """
        try:
            return client.acquire_token_by_username_password(
                username=self.adm_user,
                password=self.current_pwd,
                scopes=self.graph_scopes,
            )

        except Exception as e:
            print(f"Unable to acquire Access Token:: {e}")
            raise

    def get_ms_client(self) -> object:
        """
        Step 1 in the authentication path:
        Generates MSAL client using MS Authentication Library (MSAL)
        requires Azure app registration secret

        :return: msal client object
        :rtype: object
        """
        try:
            return msal.ConfidentialClientApplication(
                self.app_id, authority=self.base_url, client_credential=self.secret
            )
        except Exception as e:
            print(f"Unable to get Azure client instance:: {e}")
            raise

    def generate_access(self, flag=None) -> str:
        """
        Returns GRAPH access token to caller
        If flag set to 'no-passwd', get non-administrative access token

        :return: PBI access token
        :rtype: str
        """
        try:
            if ms_client := self.get_ms_client():
                if flag == "no-passwd":
                    ms_response = self.get_np_graph_access_token(ms_client)
                else:
                    ms_response = self.get_graph_access_token(ms_client)
                return ms_response.get("access_token", "No token returned")
        except Exception as e:
            print(f"Exception:: {e}")
            raise
