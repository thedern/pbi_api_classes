from src.support_classes.powerbi_api_crud_class import BiAPI


class PbiLogs(BiAPI):
    def __init__(self, access_token) -> None:
        """
        PowerBi Logs Class, subclasses BiAPI crud class
        This class is used for operations against the PowerBi Logs

        :param access_token: PBI access token
        :type access_token: str
        """

        # self.rest_api = rest_class
        self.access_token = access_token
        self.log_entries = []
        self.counter = 0

    def extender(self, ls):
        for entry in ls:
            self.log_entries.append(entry)

    def process_api_response(self, resp) -> None:
        """
        Process API response, save to instance variable
        If continuation token, recall endpoint until last result set

        :param response: API response
        :type response: dict
        """
        try:
            if resp["activityEventEntities"]:
                self.log_entries.extend(resp["activityEventEntities"])
                # self.extender(resp["activityEventEntities"])
                if resp["continuationUri"] and resp["lastResultSet"] is False:
                    self.counter += 1
                    print(f"Log fetch continue: {self.counter}")
                    self.get_pbi_activity_logs(resp["continuationUri"])
        except Exception as e:
            print(f"Exception:: {e}")

    def get_pbi_activity_logs(self, api_endpoint) -> list:
        """
        Get PowerBi actvity logs

        :param api_endpoint: API endpoint url (endpoint and continue endpoint)
        :type api_endpoint: str
        :return: activity log objects
        :rtype: list
        """

        try:
            if api_response := super().query_api(api_endpoint, self.access_token):
                self.process_api_response(api_response)
            return self.log_entries
        except Exception as e:
            print(f"Exception:: {e}")
