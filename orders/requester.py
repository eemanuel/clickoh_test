from django.conf import settings
from utils.requester import BaseRequester


class DolarSiRequester(BaseRequester):
    BASE_URL = settings.DOLAR_SI_URL

    def get_main_values(self):
        endpoint = "/api/api.php?type=valoresprincipales"
        return self._get_response_data(method="get", endpoint=endpoint)
