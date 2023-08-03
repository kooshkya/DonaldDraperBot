import requests
import json
from DonDraperAPI.settings import API_DOMAIN, API_TOKEN, BASE_DIR, FILES_DIRECTORY
from MyUtils.singleton import SingletonMeta
from rest_framework.parsers import JSONParser
import io
import os


class TelegramAPIClient(metaclass=SingletonMeta):
    def _make_target_api_url(self, function_and_params):
        return f"{API_DOMAIN}/bot{API_TOKEN}/{function_and_params}"

    def _create_function_and_params(self, function: str, params: dict):
        function_and_params = f"{function}"
        if params.keys():
            function_and_params += "?"
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
    

    def generate_file_directory(self, file_id):
        return os.path.join(BASE_DIR, f"{FILES_DIRECTORY}/{file_id}")

    def download_file(self, file_id, renew=False):
        directory_path = self.generate_file_directory(file_id)
        if os.path.exists(directory_path) and not renew:
            return directory_path
        file_path = self.get_download_link(file_id)
        if not file_path:
            #logger.log(f"Failed to download file_id {file_id}, link not fetched.")
            return None
        target_url = f"{API_DOMAIN}/file/bot{API_TOKEN}/{file_path}"
        response = requests.get(target_url, stream=True)
        if response.status_code == 200:
            with open(directory_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            #logger.log(f"Successfully downloaded file_id {file_id}")
            return directory_path
        else:
            #logger.log(f"Failed to download file_id {file_id}. Couldn't download from link")
            return None
        

    def get_download_link(self, file_id):
        r = self.call_get_format_function("getFile", file_id=file_id)
        if r.status_code == 200:
            res = JSONParser().parse(io.BytesIO(r.content))
            return res.get("result").get("file_path")
        else:
            return None
