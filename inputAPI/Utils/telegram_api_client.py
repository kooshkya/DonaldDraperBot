import requests
import json
from DonDraperAPI.settings import API_DOMAIN, API_TOKEN
from MyUtils.singleton import SingletonMeta


class TelegramAPIClient(metaclass=SingletonMeta):
    def _make_target_api_url(self, function_and_params):
        return f"{API_DOMAIN}/bot{API_TOKEN}/{function_and_params}"

    def _create_function_and_params(self, function: str, params: dict):
        function_and_params = f"{function}"
        if params.keys():
            function_and_params += "/?"
            param_items = [f"{key}={value}" for key, value in params.items()]
            function_and_params += "&".join(param_items)
        return function_and_params

    def call_get_format_function(self, function, **params):
        function_and_params = self._create_function_and_params(function, params)
        call_target = self._make_target_api_url(function_and_params)
        response = requests.get(call_target)
        return response
        
    def convert_response_to_pretty_string(self, response):
        result = ""
        result += f"Status Code: {response.status_code}\n"
        temp_obj = json.loads(response.text)
        pretty_json = json.dumps(temp_obj, indent=2, ensure_ascii=False)
        result += pretty_json
        return result
