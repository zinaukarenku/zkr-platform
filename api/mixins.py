from rest_framework_tracking.mixins import LoggingMixin

from utils.utils import get_request_information


class APILoggingMixin(LoggingMixin):

    def _get_ip_address(self, request):
        request_info = get_request_information(request)

        return request_info.client_ip
