from src.support_classes.powerbi_api_crud_class import BiAPI


class PbiAccess(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi API Tenant Object Access Control Class
        Subclasses BiAPI
        This class is used to set ACLs on workspaces and other tenant objects

        :param access_token: PBI access token
        :type access_token: str
        """
        self.access_token = access_token

    def add_ws_users(self, users_list, target_workspaces_dict, role) -> None:
        """
        Assigns admin role to users in admin_list for workspaces in target_workspaces_dict
        Can be executed on top of existing admins.  Will not error if attempting to re-add existing admin

        :param users_list: list of administrator/exec emails
        :type users_list: list
        :param target_workspaces_dict: workspaces to which the admins will be assigned
        :type target_workspaces_dict: dict
        """

        for workspace_name, workspace_meta_data in target_workspaces_dict.items():
            workspace_id = workspace_meta_data[1]
            powerbi_api_endpoint = (
                f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_id}/users"
            )
            for user_email in users_list:

                # api_obj = self.rest_api(powerbi_api_endpoint, self.access_token)

                payload = {"emailAddress": user_email, "groupUserAccessRight": role}

                if api_response := super().post_to_api(
                    payload, powerbi_api_endpoint, self.access_token
                ):
                    print(
                        f'Admin role assigned to {user_email} created in: "{workspace_name}", {api_response}'
                    )
                else:
                    print(f"Failed to add admin user {user_email}")

    def pbi_role_assigner(self, workspace_id, ad_groups_list, ws_name) -> None:
        """
        Assigns AD groups to workspaces

        :param workspace_id: unique workspace identifier
        :type workspace_id: str
        :param ad_groups_list: list of AD groups
        :type ad_groups_list: list
        :param ws_name: workspace to which AD groups will be assigned
        :type ws_name: str
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_id}/users"
        )
        # api_obj = self.rest_api(powerbi_api_endpoint, self.access_token)
        for ad_group_dict in ad_groups_list:

            for ad_group_name, entra_obj_id in ad_group_dict.items():
                if "contributor" in ad_group_name.lower():
                    payload = {
                        "identifier": entra_obj_id,
                        "groupUserAccessRight": "Contributor",
                        "principalType": "Group",
                    }
                elif "member" in ad_group_name.lower():
                    payload = {
                        "identifier": entra_obj_id,
                        "groupUserAccessRight": "Member",
                        "principalType": "Group",
                    }

                print(f"payload: {payload}")

                if api_response := super().post_to_api(
                    payload, powerbi_api_endpoint, self.access_token
                ):
                    print(
                        f"AD group {ad_group_dict} assigned to {ws_name}.  API Response {api_response}"
                    )
                else:
                    print(f"Failed to assign AD group. {ad_group_dict}")

    def add_ws_active_dir_groups(self, ad_groups_add, target_workspaces_dict) -> None:
        """
        Matches workspace name to workspace type and calls self.pbi_role_assigner

        Top-level keys in ad_groups_add are: -prod, -nonprod, -uat
        nonprod workspaces <--> nonprod members and contributors groups
        uat workspaces <--> uat members and contributors groups
        prod workspaces <--> prod members and contributors groups

        :param ad_groups_add: dictionary of AD groups to add
        :type workspace_id: dict
        :param target_workspaces_dict: dictionary of target workspaces to which to add AD groups
        :type target_workspaces_dict: dict
        """

        for workspace_type, ws_ad_groups in ad_groups_add.items():
            for workspace_name, workspace_metadata in target_workspaces_dict.items():

                ws_id = workspace_metadata[1]

                if (
                    "-nonprod" in workspace_type.lower()
                    and "-nonprod" in workspace_name.lower()
                ):
                    self.pbi_role_assigner(ws_id, ws_ad_groups, workspace_name)

                elif (
                    "-uat" in workspace_type.lower()
                    and "-uat" in workspace_name.lower()
                ):
                    self.pbi_role_assigner(ws_id, ws_ad_groups, workspace_name)

                elif (
                    "-prod" in workspace_type.lower()
                    and "-prod" in workspace_name.lower()
                ):
                    self.pbi_role_assigner(ws_id, ws_ad_groups, workspace_name)

    def check_current_access(self, workspace_id) -> list:
        """
        Check for and report back current access rights to workspace

        :param workspace_id: unique workspace identifier
        :type workspace_id: str
        :return: list of workspace user objects
        :rtype: list
        """
        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/groups/{workspace_id}/users"
        )
        # api_obj = self.rest_api(powerbi_api_endpoint, self.access_token)

        api_response = super().query_api(powerbi_api_endpoint, self.access_token)
        if isinstance(api_response, dict):
            # 'value' key is a list of user objects
            return api_response["value"]
        else:
            print(f"api response code other than 200. API Repsonse:: {api_response}")

    def assign_pipeline_users(self, pl_id, admins, ad_groups) -> None:
        """
        Assigns admins to pipeline.  Admins are PBI admins and Members AD group

        :param pl_id: unique pipeline identifier
        :type pl_id: str
        :param admins: list of admins
        :type admins: list
        :param ad_groups: dictionary of AD groups
        :type ad_groups: dict
        """

        powerbi_api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/admin/pipelines/{pl_id}/users"
        )
        # api_obj = self.rest_api(powerbi_api_endpoint, self.access_token)

        # Assign Admins
        results = []
        for admin in admins:
            payload = {
                "identifier": admin,
                "accessRight": "Admin",
                "principalType": "User",
            }

            if api_response := super().post_to_api(
                payload, powerbi_api_endpoint, self.access_token
            ):
                results.append((admin, api_response))
            else:
                print(f"Failed to assign admin:: {admin}")
        print(f"Pipline Admin Assignments: {results}")

        # Assign Members AD Groups
        results = []
        for ws_ad_groups in ad_groups.values():
            for ad_group in ws_ad_groups:
                for (
                    ad_group_name,
                    ad_group_id,
                ) in ad_group.items():
                    if "-member" in ad_group_name:
                        payload = {
                            "identifier": ad_group_id,
                            "accessRight": "Admin",
                            "principalType": "Group",
                        }

                        if api_response := super().post_to_api(
                            payload, powerbi_api_endpoint, self.access_token
                        ):
                            results.append((ad_group_name, api_response))
                        else:
                            print(f"Failed to assign AD group:: {ad_group_name}")
        print(f"Pipline AD Groupd Assignments: {results}")
