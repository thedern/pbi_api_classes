from src.support_classes.powerbi_api_crud_class import BiAPI


class PbiPipeline(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi API Pipeline Class
        Subclasses BiAPI
        This class is used for pipeline-based operations

        :param access_token: PBI api token
        :type access_token: str
        """

        self.access_token = access_token
        self.pipeline_id = None

    def get_pipelines(self) -> list:
        """
        Gets all existing pipelines from PBI tenant

        :return: list of pipeline dictionary objects
        :rtype: list
        """

        powerbi_api_endpoint = "https://api.powerbi.com/v1.0/myorg/pipelines"

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                return api_response["value"]
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def get_pipelines_admin(self) -> list:
        """
        Gets all existing pipelines from PBI tenant as admin
        NO PASSWORD REQUIRED

        :return: list of pipeline dictionary objects
        :rtype: list
        """

        powerbi_api_endpoint = "https://api.powerbi.com/v1.0/myorg/admin/pipelines"

        try:
            api_response = super().query_api(powerbi_api_endpoint, self.access_token)
            if isinstance(api_response, dict):
                return api_response["value"]
            else:
                print(
                    f"api response code other than 200. API Repsonse:: {api_response}"
                )
        except Exception as e:
            print(f"Exception:: {e}")

    def assign_pipline_ws(self, target_workspaces_dict) -> None:
        """
        Assign workspaces to pipeline based on Nonprod, UAT, Prod designations
        Requires pipeline id from pipeline generation method (self.pipelined_id)

        :param target_workspaces_dict: dictionary of workspace objects
        :type target_workspaces_dict: dict
        """

        results = []
        try:
            for workspace_name, workspace_metadata in target_workspaces_dict.items():
                ws_id = workspace_metadata[1]

                if "-nonprod" in workspace_name.lower():
                    stageOrder = 0
                elif "-uat" in workspace_name.lower():
                    stageOrder = 1
                elif "-prod" in workspace_name.lower():
                    stageOrder = 2

                powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/pipelines/{self.pipeline_id}/stages/{stageOrder}/assignWorkspace"

                payload = {
                    "workspaceId": ws_id,
                }

                if api_response := super().post_to_api(
                    payload, powerbi_api_endpoint, self.access_token
                ):
                    results.append((workspace_name.lower(), api_response))
                else:
                    print(f"Failed to create workspace. API Repsonse:: {api_response}")
            print(f"Pipeline Workspace Assignments: {results}")
        except Exception as e:
            print(f"Exception:: {e}")

    def generate_pipeline(self, pipeline_data) -> str:
        """
        Creates pipeline if not already exists.  Will error if pipeline exists thus checks first

        :param pipeline_data: pipeline metadata
        :type pipeline_data: dict
        :return: pipeline id
        :rtype: str
        """

        try:
            existing_pipelines = self.get_pipelines()
            pl_names = [pipline["displayName"] for pipline in existing_pipelines]

            if pipeline_data["name"] not in pl_names:

                payload = {
                    "displayName": pipeline_data["name"],
                    "description": "Helix Deployment Pipeline",
                }

                powerbi_api_endpoint = "https://api.powerbi.com/v1.0/myorg/pipelines"
                if api_response := super().post_to_api(
                    payload, powerbi_api_endpoint, self.access_token
                ):
                    # get 'id' from json repsonse
                    self.pipeline_id = api_response.json()["id"]
                    return api_response.json()["id"]
                else:
                    print(f"Failed to create pipelines. API Repsonse:: {api_response}")
            else:
                print(f"{pipeline_data['name']}, already exists. Skipping creation")
                return None
        except Exception as e:
            print(f"Exception:: {e}")

    def update_pipline_users_admin(self):
        """
        Adds ACL-DNA-PowerBiAdimn_RW AD group to all pipelines as admin

        :return: _description_
        :rtype: _type_
        """

        try:
            existing_pipelines = self.get_pipelines_admin()
            pipeline_ids = [pipeline["id"] for pipeline in existing_pipelines]

            for pipeline_id in pipeline_ids:

                payload = {
                    "identifier": "f8192940-296b-4e4d-9814-be0bbda727da",
                    "accessRight": "Admin",
                    "principalType": "Group",
                }

                powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/pipelines/{pipeline_id}/users"
                if api_response := super().post_to_api(
                    payload, powerbi_api_endpoint, self.access_token
                ):
                    print(f"{pipeline_id}: {api_response}")
                else:
                    print(
                        f"Failed to add admin AD group to pipeline. API Repsonse:: {api_response}"
                    )
        except Exception as e:
            print(f"Exception:: {e}")
