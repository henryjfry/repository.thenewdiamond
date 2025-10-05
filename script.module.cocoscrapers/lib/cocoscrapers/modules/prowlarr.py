import xbmc
import xbmcaddon
import xbmcgui
import json
from queue import Queue
from threading import Thread
import urllib.request
import urllib.error
import urllib.parse
from cocoscrapers.modules.control import setting as getSetting, notification
from cocoscrapers.modules.log_utils import LOGINFO


class Prowlarr:
    def __init__(self):
        pass

    def pretty_print(self, value: any):
        xbmc.log('script.module.cocoscrapers' + str(value), LOGINFO)

    def get_prowlarr_settings(self) -> (bool, str, str):
        prowlarr_enabled = getSetting("prowlarr.enabled") == "true"
        prowlarr_server_url = getSetting("prowlarr.serverurl")
        prowlarr_api_key = getSetting("prowlarr.apikey")
        return prowlarr_enabled, prowlarr_server_url, prowlarr_api_key

    def is_prowlarr_configured(self) -> bool:
        is_enabled, server_url, api_key = self.get_prowlarr_settings()
        if not is_enabled or not server_url or not api_key:
            return False
        else:
            return True

    def _fetch_data(self, endpoint: str, headers: dict, result_queue: Queue):
        if not self.is_prowlarr_configured():
            result_queue.put("Prowlarr is not configured")
            return

        _, server_url, api_key = self.get_prowlarr_settings()
        headers["X-Api-Key"] = api_key
        request_url = server_url + endpoint

        try:
            req = urllib.request.Request(url=request_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                result_queue.put(data)  # Put the result in the queue
        except Exception as e:
            xbmc.log("Error fetching data: " + str(e), xbmc.LOGERROR)
            result_queue.put("Error")

    def _get(self, endpoint: str, headers: dict = None):
        if headers is None:
            headers = {}
        result_queue = Queue()
        thread = Thread(target=self._fetch_data, args=(endpoint, headers, result_queue))
        thread.start()
        thread.join()  # Wait for the thread to complete
        return result_queue.get()  # Retrieve the result from the queue

    def test(self):
        result = self._get(endpoint="/api")
        notification(title="Prowlarr Test Results", message=result)

    def get_indexers(self):
        result = self._get("/api/v1/indexer")
        if result == "Error":
            return []

        indexers = [
            indexer["definitionName"].lower() for indexer in result if "definitionName" in indexer
        ]
        notification(title="Prowlarr Indexers", message=indexers)
        return indexers
