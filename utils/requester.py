from abc import ABC, abstractmethod

import requests


class BaseRequester(ABC):
    TIMEOUT = 120
    BASE_URL = ""

    def _get_response_data(self, method, endpoint, params={}):
        url = f"{self.BASE_URL}{endpoint}"
        values = {"url": url, "timeout": self.TIMEOUT}
        if method == "get":
            values.update({"params": params})
        elif method in ("post", "put", "patch"):
            values.update({"json": params})
        requests_method = getattr(requests, method)
        response = requests_method(**values)
        response.raise_for_status()  # raise HTTPError if response.status_code != 200
        return response.json()
