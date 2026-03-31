import os
from pathlib import Path
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


class AzureBlobStorage:
    def __init__(self, storage_acct, container_name="powerbiadmin"):
        """
        Uses azure-storage-blob library versus pure REST implemention
        library: https://pypi.org/project/azure-storage-blob/
        alternate REST API:  https://learn.microsoft.com/en-us/rest/api/storageservices/blob-service-rest-api

        defaults to dev storage account

        :param storage_acct:  name of Azure Storage Account
        :type storage_acct: str
        :param container_name: name of blob container
        :type container_name: str
        """

        load_dotenv(".env", override=True)
        self.container_name = container_name
        self.blob_service_client = None
        self.storage_acct = storage_acct
        self.app_id = os.getenv("app_id")
        self.azure_tenant_id = os.getenv("azure_tenant_id")
        self.secret = os.getenv("secret")
        self.authenticate()

    def authenticate(self):
        """
        Authenticates in Azure Blob Storage using service principal
        (role: storage blob data contributor)
        """
        account_url = f"https://{self.storage_acct}.blob.core.windows.net"

        try:
            credential = ClientSecretCredential(
                tenant_id=self.azure_tenant_id,
                client_id=self.app_id,
                client_secret=self.secret,
            )
            self.blob_service_client = BlobServiceClient(
                account_url=account_url, credential=credential
            )
        except Exception as e:
            print(f"Unable to authenticate into blob storage: {e}")

    def write_blob(
        self,
        file_path,
        file_name,
        blob_subdirectory=None,
    ):
        """
        Create a blob client using the local file name as the name for the blob

        :param file_name: name of file
        :type file_name: str
        :param file_path: path to file execluding name
        :type file_path: str
        """
        # convert windows path to string
        upload_path = str(Path.cwd().joinpath(file_path, file_name))

        try:
            # if writing to a subdir in blob storage
            if blob_subdirectory:

                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=f"{blob_subdirectory}/{file_name}",
                )
            else:
                blob_client = self.blob_service_client.get_blob_client(
                    container=self.container_name, blob=file_name
                )

            print("\nUploading to Azure Storage as blob:\n\t" + upload_path)

            with open(file=upload_path, mode="rb") as data:
                blob_client.upload_blob(data, overwrite=True)

        except Exception as e:
            print(f"Write blob execption: {e} ")

    def download_blob_to_file(self, blob_name, file_path):
        """
        Downloads blob to file_path
        :param file_path: blob download destination
        :type file_path: str
        :param blob_name: name of blob to download
        :type blob_name: str
        """

        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # convert windows path to string
            download_path = str(Path.cwd().joinpath(file_path, blob_name))
            with open(download_path, mode="wb") as file_handler:
                download_stream = blob_client.download_blob()
                file_handler.write(download_stream.readall())
        except Exception as e:
            print(f"Exception:: {e}")

    def download_blob_to_string(self, blob_name):
        """
        Read contents of blob (print or save to variable)
        :param blob_name: name of blob
        :type blob_name: str

        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, blob=blob_name
            )

            # encoding param is necessary for readall() to return str, otherwise it returns bytes
            downloader = blob_client.download_blob(max_concurrency=1, encoding="UTF-8")
            return downloader.readall()

        except Exception as e:
            print(f"Exception:: {e}")

    def list_blobs(self):
        """
        Lists all blobs in container
        """
        print("\nListing blobs...")

        try:
            blob_list = self.blob_service_client.get_container_client(
                self.container_name
            ).list_blobs()
            for blob in blob_list:
                print(blob.name)

        except Exception as e:
            print(f"Error listing blobs: {e}")
