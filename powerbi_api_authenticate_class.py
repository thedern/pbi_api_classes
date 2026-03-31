import os
import msal
import requests
from dotenv import load_dotenv


class PowerbiAuthenticate:
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
        self.scopes = ["https://analysis.windows.net/powerbi/api/.default"]

    def get_np_pbi_access_token(self, client) -> str:
        """
        Step 2 in the authentication path:
        Uses MSAL client to get PBI access token
        this method is for non-admin use

        :param client: msal client object
        :type client: object
        :return: PBI access token
        :rtype: str
        """
        try:
            # method does not require username/password
            return client.acquire_token_for_client(scopes=self.scopes)

        except Exception as e:
            print(f"Unable to acquire Access Token:: {e}")
            raise

    def get_pbi_access_token(self, client) -> str:
        """
        pbi ADMIN api endpoints work with PBI admin SPN, no username/password

        Step 2 in the authentication path:
        Uses MSAL client to get PBI access token

        :param client: msal client object
        :type client: object
        :return: PBI access token
        :rtype: str
        """
        try:
            return client.acquire_token_by_username_password(
                username=self.adm_user, password=self.current_pwd, scopes=self.scopes
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
        Returns PBI access token to caller
        If flag set to 'no-passwd', get non-administrative access token

        Password can be omitted when:
        1.  calling '/admin' api enpoints with PowerBi admin SPN
            (BTS-DNA-PowerBiAdminApp)
        2.  when calling non-admin api enpoints with a SPN which has been
            specifically added to the Workspace as 'admin' or 'member' role
        Else use get_pbi_access_token method (for admin)

        :return: PBI access token
        :rtype: str
        """
        if ms_client := self.get_ms_client():
            if flag == "no-passwd":
                ms_response = self.get_np_pbi_access_token(ms_client)
            else:
                ms_response = self.get_pbi_access_token(ms_client)
            return ms_response.get("access_token", "No token returned")

    @staticmethod
    def get_access_token_generic(app, secret, azure_tenant) -> str:
        """
        static method
        generate Azure access token, requests w/o MSAL
        :return: access token
        :rtype: str
        """

        url = f"https://login.microsoftonline.com/{azure_tenant}/oauth2/v2.0/token"
        payload = {
            "client_id": app,
            "client_secret": secret,
            "grant_type": "client_credentials",
            "scope": "https://analysis.windows.net/powerbi/api/.default",
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            api_response = requests.post(url, headers=headers, data=payload)
            if api_response.status_code in {200, 201, 202}:
                response = api_response.json()
                if response.get("access_token"):
                    return response.get("access_token", None)
            else:
                print(f"API response: {api_response.status_code}")

        except Exception as e:
            print(f"Exception:::  {e}")
