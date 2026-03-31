import os
from dotenv import load_dotenv
from azure.keyvault.secrets import SecretClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential


class AzureKeyVault:
    def __init__(self, keyvault_name):
        """
        Securely store and control access to tokens, passwords, certificates,
            API keys, and other secrets
        All methods coded below are synchronous.
        Asynchronous methods are also available

        References:
        https://azuresdkdocs.z19.web.core.windows.net/python/azure-keyvault-secrets/latest/azure.keyvault.secrets.html#azure.keyvault.secrets.SecretClient
        https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.clientsecretcredential?view=azure-python
        https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme?view=azure-python
        https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme?view=azure-python#asynchronously-create-a-secret

        :param keyvault_name: target key vault to manage
        :type keyvault_name: str
        """

        load_dotenv(".env", override=True)
        self.app_id = os.getenv("app_id")
        self.azure_tenant_id = os.getenv("azure_tenant_id")
        self.secret = os.getenv("secret")
        self.keyvault_name = keyvault_name
        self.kv_url = f"https://{self.keyvault_name}.vault.azure.net"
        self.client = None

    def get_client_spn(self):
        """
        creates secret client with SPN
        Best for interactive or local use
        """

        kv_credential = ClientSecretCredential(
            tenant_id=self.azure_tenant_id,
            client_id=self.app_id,
            client_secret=self.secret,
        )

        self.client = SecretClient(vault_url=self.kv_url, credential=kv_credential)

    def get_client_default_credential(self):
        """
        NOTE:  Need to authenticate via Azure CLI or PowerShell first
            https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-python?tabs=azure-cli#sign-in-to-azure
        creates scrent client using DefaultCredentail
        best used in deployed functions (function app or other)
        """
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=self.kv_url, credential=credential)

    def get_secret_value(self, secret_alias):
        """
        for secret_alias, returns secret object

        print(secret.name)
        print(secret.value)
        print(secret.id)
        print(secret.properties)

        :param secret_value_alias: alias in keyvault assigned to secret value
        :type secret_value_alias: str
        :return: secret object
        :rtype: object
        """

        return self.client.get_secret(secret_alias)

    def set_secret(self, secret_name, secret_value):
        """
        Creates new secrets and changes the values of existing secrets.
        If no secret with the given name exists, set_secret creates a new
        secret with that name and the given value.
        If the given name is in use, set_secret creates a new version of that
        secret, with the given value.

        Reference:
        https://azuresdkdocs.z19.web.core.windows.net/python/azure-keyvault-secrets/latest/azure.keyvault.secrets.html#azure.keyvault.secrets.SecretClient.set_secret

        TODO:  use this to set DBX PATs in KeyVault?

        print(secret.name)
        print(secret.value)
        print(secret.properties.version)

        :param secret_name: _description_
        :type secret_name: _type_
        :param secret_value: _description_
        :type secret_value: _type_
        """
        return self.client.set_secret(secret_name, secret_value)

    def delete_secret(self, target_secret):
        """
        deletes target secret from key vault
        :param target_secret: secret to delete
        :type target_secret: string
        """
        deleted_secret = self.client.begin_delete_secret(target_secret).result()
        print(deleted_secret.name)
        print(deleted_secret.deleted_date)

    def list_secrets(self):
        """
        returns a list all secret objects
        https://azuresdkdocs.z19.web.core.windows.net/python/azure-keyvault-secrets/latest/azure.keyvault.secrets.html#azure.keyvault.secrets.SecretClient.list_properties_of_secrets
        """
        return self.client.list_properties_of_secrets()
