import requests
import win32com.client as win32
from src.support_utils.write_file import write_json
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_classes.powerbi_api_dataset_class import PbiDataset

auth_obj = PowerbiAuthenticate()
pbi_access_token = auth_obj.generate_access()
dataset_obj = PbiDataset(pbi_access_token)


def send_email(text_info):
    outlook = win32.Dispatch("outlook.application")
    mail = outlook.CreateItem(0)
    print(mail.__dict__)
    mail.To = "<user>@<domain>.com"
    mail.Subject = "Message subject - TEST"
    mail.Body = f"Message body: \n {text_info}"
    mail.HTMLBody = "<h2>HTML Message body</h2>"  # this field is optional

    # To attach a file to the email (optional):
    # attachment  = "Path to the attachment"
    # mail.Attachments.Add(attachment)

    # mail.Send()


def report_model(m_args):
    return {
        m_args[0]: [
            {"report_creator": m_args[1]},
            {"ds_name": m_args[2]},
            {"ds_configured_by": m_args[3]},
        ]
    }


def get_dataset_metadata(dataset_id):

    return dataset_obj.get_dataset_by_id(dataset_id)


def get_workspace_reports_creator(token, group_id) -> str:
    """
    Gets all reports for specific workspace
    Admin api url will return report "created_by"

    :param token: access token
    :type token: str
    :param group_id: workspace ID GUID
    :type group_id: str
    :return: report metadata json
    :rtype: str
    """

    api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/groups/{group_id}/reports"
    headers = {"Authorization": f"Bearer {token}"}
    master_list = []
    try:
        # api_response = requests.get(api_endpoint, headers=headers)
        api_response = requests.get(api_endpoint, headers=headers)
        if api_response.status_code in {200, 201, 202}:
            for item in api_response.json()["value"]:
                dataset_meta = get_dataset_metadata(item["datasetId"])

                if item and dataset_meta:

                    model_args = (
                        item.get("name"),
                        item.get("createdBy"),
                        dataset_meta.get("name"),
                        dataset_meta.get("configuredBy"),
                    )

                else:
                    model_args = (
                        item.get("name"),
                        item.get("createdBy"),
                        "dataset: None",
                        "configuredBy: None",
                    )

                modeled = report_model(model_args)

                master_list.append(modeled)

            return master_list
        print(f"api response code other than success, {api_response.status_code}")

    except Exception as e:
        print(f"Unexpected failure getting API response:: {e}")
        raise


def main():
    """
    main function of sample code
    enter IDs for workspace and workspace name
    returns report creator and datasets
    API reference: https://learn.microsoft.com/en-us/rest/api/power-bi/

    """
    workspace_id = ""
    workspace_name = ""

    if report_resp := get_workspace_reports_creator(
        pbi_access_token,
        workspace_id,
    ):
        for item in report_resp:
            print(item)
            write_json(report_resp, f"{workspace_name}_reports.json")

        # final_text = ""
        # for item in report_resp.json()["value"]:
        #     print(f'Report: {item.get("name")}; Created By: {item.get("createdBy")}')
        #     final_text += (
        #         f'Report: {item.get("name")}; Created By: {item.get("createdBy")}\n'
        #     )

    # send_email(final_text)


if __name__ == "__main__":
    main()
