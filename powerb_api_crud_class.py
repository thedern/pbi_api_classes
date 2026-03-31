import requests
from src.support_classes.logger_class import Logger


class BiAPI:
    def __init__(self) -> None:
        """
        PowerBi API CRUD Class
        This class is used for CREATE, READ, UPDATE, and DELETE calls against
        the PBI API endpoints
        Other support classes are subclasses of this base class
        """
        self.logger_instance = Logger()

    @staticmethod
    def api_response_parser(response) -> dict:
        """
        Returns parsed api response provided response code == 200

        :param response: api response
        :type response: object
        :return: parsed api response
        :rtype: dict
        """
        return response.json() if response.status_code == 200 else response.status_code

    def query_api(self, api_endpoint, access_token) -> dict:
        """
        GET data from api

        :return: parsed api reponse via self.api_repsonse_parser
        :rtype: dict
        """

        try:
            api_response = requests.get(
                api_endpoint, headers={"Authorization": f"Bearer {access_token}"}
            )
            if api_response.status_code == 200:
                return self.api_response_parser(api_response)
            print(f"api response code other than success, {api_response.status_code}")

        except Exception as e:
            self.logger_instance.error_logger.exception(
                f"Unexpected failure getting API response:: {e}", exc_info=True
            )

    def post_to_api(self, payload_data, api_endpoint, access_token) -> object:
        """
        POST data to api
        if api response code is in set of {200, 201}, returns the api response.
        api post response does not return JSON to parse

        :param payload_data: payload sent to api
        :type payload_data: dict
        :return: response object
        :rtype: object
        """

        try:
            api_response = requests.post(
                api_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload_data,
            )
            if api_response.status_code in {200, 201}:
                return api_response
            print(f"api response code other than success, {api_response.status_code}")

        except Exception as e:
            print(f"Unexpected failure getting API response:: {e}")
            raise

    def patch_to_api(self, payload_data, api_endpoint, access_token) -> object:
        """
        PATCH data to api
        if api response code is in set of {200, 201}, returns the api response.
        api patch response does not return JSON to parse

        :param payload_data: payload sent to api
        :type payload_data: dict
        :return: response object
        :rtype: object
        """

        try:
            api_response = requests.patch(
                api_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload_data,
            )
            if api_response.status_code in {200, 201}:
                return api_response
            print(f"api response code other than success, {api_response.status_code}")

        except Exception as e:
            print(f"Unexpected failure getting API response:: {e}")
            raise
