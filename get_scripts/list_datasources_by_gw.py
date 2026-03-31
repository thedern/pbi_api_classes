import requests
from src.support_classes.powerbi_authenticate_class import PowerbiAuthenticate
from src.support_utils.write_file import write_json


auth_obj = PowerbiAuthenticate()
pbi_access_token = auth_obj.generate_access("no-passwd")
headers = {"Authorization": f"Bearer {pbi_access_token}"}


def flatten_records(ds_list):
    """
    flatten data for making single records in table
    :param ds_list: list of gatway and datasource dicts
    :type ds_list: list
    """

    flat_list = []

    for gw_dssource_dict in ds_list:
        for datasources in gw_dssource_dict.values():
            flat_list.extend(
                {
                    "gatewayId": record["gatewayId"],
                    "datasourceId": record["id"],
                    "datasourceType": record["datasourceType"],
                    "connectionDetails": record["connectionDetails"],
                    "credentialType": record["credentialType"],
                    "datasourceName": record["datasourceName"],
                    "privacyLevel": record["credentialDetails"]["privacyLevel"],
                    "useEndUserOAuth2Credentials": record["credentialDetails"][
                        "useEndUserOAuth2Credentials"
                    ],
                }
                for record in datasources
            )
    return flat_list


def get_datasource_users(data_source_list):
    """_summary_

    :param data_source_list: list of datasource objects [{gw_id: [{ds_obj, ds_obj...}]]}
    :type data_source_list: list
    :return: _description_
    :rtype: _type_
    """

    ds_users_master = []

    for datasource_obj in data_source_list:
        for gw_id, datsources in datasource_obj.items():
            for datasource in datsources:
                # if counter < 198:

                api_endpoint = f"https://api.powerbi.com/v1.0/myorg/gateways/{gw_id}/datasources/{datasource['id']}/users"
                try:
                    api_response = requests.get(api_endpoint, headers=headers)
                    if api_response.status_code in {200, 201, 202}:
                        # flatten array entries into single records
                        ds_users_master.extend(
                            {
                                "datasource_name": datasource["datasourceName"],
                                "datasource_id": datasource["id"],
                                "emailAddress": val.get("emailAddress", None),
                                "datasourceAccessRight": val.get(
                                    "datasourceAccessRight", None
                                ),
                                "displayName": val.get("displayName", None),
                                "identifier": val.get("identifier"),
                                "principalType": val.get("principalType", None),
                            }
                            for val in api_response.json()["value"]
                        )
                    else:
                        print(
                            f"api response code other than success, {api_response.status_code}"
                        )

                except Exception as e:
                    print(f"Unexpected failure getting API response:: {e}")
                    raise

    return ds_users_master


def get_gateway_datasources(gws):
    """
    for each gw, get all datasources

    :param gws: dict of gw ids
    :type gws: dict
    :return: list of datasources per gw
    :rtype: list
    """

    gw_response_list = []

    for gw_id in gws.values():
        api_endpoint = (
            f"https://api.powerbi.com/v1.0/myorg/gateways/{gw_id}/datasources"
        )

        try:
            api_response = requests.get(api_endpoint, headers=headers)
            if api_response.status_code in {200, 201, 202}:
                gw_response_list.append({gw_id: api_response.json()["value"]})
            else:
                print(
                    f"api response code other than success, {api_response.status_code}"
                )
                gw_response_list.append({gw_id: None})

        except Exception as e:
            print(f"Unexpected failure getting API response:: {e}")
            raise

    return gw_response_list


def main():
    """
    using non-admin apis,
    added BTS-DNA-PowerBiAdminApp to gw's as admin role so I would not need user/name password auth

    """

    # dna on-prem gateways (static id's)
    gateways = {
        "Gateway1": "<id>",
        "Gateway2": "<id>",

    }

    # get gws and datasources
    gw_ds_list = get_gateway_datasources(gateways)
    flattened_list = flatten_records(gw_ds_list)
    write_json(flattened_list, "all_datasouces_flat.json")

    # get users of each datasource
    data_source_users = get_datasource_users(gw_ds_list)
    write_json(data_source_users, "all_datasouce_users.json")


if __name__ == "__main__":
    main()
