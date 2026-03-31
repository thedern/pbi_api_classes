import requests
import json
from pathlib import Path
from src.support_classes.graph_authenticate_class import GraphAuthenticate

auth_obj = GraphAuthenticate()
GRAPH_ACCESS_TOKEN = auth_obj.generate_access()
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

# to use 'endswith', must ConsistenyLevel header
HEADERS = {
    "Authorization": f"Bearer {GRAPH_ACCESS_TOKEN}",
    "ConsistencyLevel": "eventual",
}


def write_json(tg, data):
    """
    Write parsed data to json
    :param data: parsed dict
    :type data: dict
    """
    write_file = Path.cwd().joinpath("json", f"{tg}_test_recursion.json")
    with open(write_file, "w") as f:
        # 'dump' the entire dict object with formatting
        json.dump(data, f, indent=4)


def get_user_details(user_id):
    """
    Use this function if you already know user's Azure ID
    :param user_id: user's GUID
    :type user_id: str
    """
    user_info_url = f"{GRAPH_ENDPOINT}/users/{user_id}"
    try:
        api_response_user = requests.get(user_info_url, headers=HEADERS)
        if api_response_user.status_code in {200, 201, 202}:
            response_json_users = api_response_user.json()
            print(response_json_users)
    except Exception as e:
        print(e)


def get_users(HEADERS):
    """
    Use this function if you already know user's Azure ID
    :param user_id: user's GUID
    :type user_id: str
    """
    user_info_url = f"{GRAPH_ENDPOINT}/users"
    try:
        api_response_user = requests.get(user_info_url, headers=HEADERS)
        if api_response_user.status_code in {200, 201, 202}:
            return api_response_user.json()
    except Exception as e:
        print(e)


def get_ad_grp_members(ad_grp_id):
    # TODO: get continue token if exists.  Only returns 100 members at a time

    all_users = []
    get_users_url = f"{GRAPH_ENDPOINT}/groups/{ad_grp_id}/members"
    while get_users_url:
        try:
            api_response = requests.get(get_users_url, headers=HEADERS)
            if api_response.status_code in {200, 201, 202}:
                # response_json = api_response.json().get("value", None)
                all_users.extend(api_response.json().get("value", None))
                get_users_url = api_response.json().get("@odata.nextLink")
        except Exception as e:
            print(e)

    print(len(all_users))
    return all_users


def search_ad_groups(filter_term=None):

    all_groups = []
    next_page_url = f"{GRAPH_ENDPOINT}/groups"

    while next_page_url:
        params = {}
        if filter_term:
            params["$filter"] = filter_term

        try:
            api_response = requests.get(next_page_url, headers=HEADERS, params=params)
            if api_response.status_code in {200, 201, 202}:
                response_json = api_response.json()
                all_groups.extend(response_json.get("value", None))
                next_page_url = response_json.get("@odata.nextLink")
        except Exception as e:
            print(e)
            continue

    return all_groups


# def collect_data(k, v):
#     # TODO: fix this... does not work
#     if super_list:
#         for entry in super_list:
#             if k in entry:
#                 for i, j in entry.items():
#                     j.append(v)
#     else:
#         super_list.extend({k: v})


# def entry_parser(entries, grp):
#     # recusion to deep dive into subgroups
#     # sub_lists = []
#     # master_list = [{grp: sub_lists}]
#     for entry in entries:

#         # base case
#         if entry.get("@odata.type") == "#microsoft.graph.user":
#             # sub_lists.append(entry["userPrincipalName"])
#             collect_data(grp, entry["userPrincipalName"])
#             # TODO: I somehow need to write this out and save it before the recursive call
#             # call capture data?  {grp: [sub_lists]}
#         # recursion case
#         elif entry.get("@odata.type") == "#microsoft.graph.group":
#             x = get_ad_grp_members(entry["id"])
#             # recursive call
#             return entry_parser(x, entry["displayName"])


def main():
    test_groups = [
       "<test Ad grouo 1>",
       "<test Ad group 2>"
    ]

    # tkn = test_auth()
    # HEADERS = {"Authorization": f"Bearer {tkn}"}
    # users = get_users(HEADERS)
    # for user in users["value"]:
    #     print(user)
    # print(len(users["value"]))

    # for top_grp in test_groups:
    #     groups = search_ad_groups(filter_term=f"startswith(displayName,'{top_grp}')")
    #     print(f"these are the groups:: {groups}")

    groups = search_ad_groups(filter_term="endswith(displayName,'<add ad group name here>')")
    for group in groups:
        print(group["displayName"])

    # for group in groups:
    #     # top-level call
    #     ad_users = get_ad_grp_members(group["id"])
    #     print(f"these are the users in the groups::{ad_users}")

    # entry_parser(all_users, top_grp)
    # print(len(super_list))
    # write_json(top_grp, super_list)
    # print(super_list)


if __name__ == "__main__":
    main()
