import json
import sys
from classfiles.powerbi_authenticate_class import (
    PowerbiAuthenticate,
)
from classfiles.powerbi_api_log_class import (
    PbiLogs,
)

auth_obj = PowerbiAuthenticate()
access_token = auth_obj.generate_access("no-passwd")
log_obj = PbiLogs(access_token)


def retrieve_records(start_timestamp, end_timestamp):
    """
    Get PowerBi Activity Log Records

    :param start_timestamp: beginning date
    :type start_timestamp: str
    :param end_timestamp: ending date
    :type end_timestamp: str
    :return: list of actvity log entries
    :rtype: str

    """

    try:

        # API enpoint must be passed to class as it changes with continuation token
        powerbi_api_endpoint = f"https://api.powerbi.com/v1.0/myorg/admin/activityevents?startDateTime='{start_timestamp}'&endDateTime='{end_timestamp}'"

        # get_pbi_activity_logs method looks for continuation token to get all records.
        if api_response := log_obj.get_pbi_activity_logs(powerbi_api_endpoint):
            print("Activity log collection completed, check json/logs* file")
            print(f"Log entries:{len(api_response)}")
            return json.dumps(api_response)

        else:
            return None

    except Exception:
        # print exeption and raise error
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Error unable to get activity logs: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
        raise


def seed_activity_list(y, m, d, m2, d2):
    """
    Seeding activity log table with initial data

    :param y: year
    :type year: str
    :param m: from month
    :type m: str
    :param d: from day
    :type d: str
    :param m2: to month
    :type m2: str
    :param d2: to day
    :type d2: str
    :return: list of actvity log entries
    :rtype: str
    """

    try:
        s_timestamp = f"{y}-{m}-{d}T00:00:00"
        e_timestamp = f"{y}-{m2}-{d2}T23:59:59"
        return retrieve_records(s_timestamp, e_timestamp)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Error unable to get activity logs: {exc_type, exc_obj, exc_tb}. Trace for more"
        )


def generate_activity_list(y, m, d) -> list:
    """

    Gets activity logs for desired day
    Writes to stdout, json, xlsx

    :param y: year
    :type year: str
    :param m: from month
    :type m: str
    :param d: from day
    :return: list of actvity log entries
    :rtype: str

    """
    try:
        s_timestamp = f"{y}-{m}-{d}T00:00:00"
        e_timestamp = f"{y}-{m}-{d}T23:59:59"
        return retrieve_records(s_timestamp, e_timestamp)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(
            f"Error unable to get activity logs: {exc_type, exc_obj, exc_tb}. Trace for more"
        )
