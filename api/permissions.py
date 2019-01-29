from logging import getLogger

from rest_framework import permissions
from rest_framework.authtoken.models import Token

logger = getLogger(__name__)


class APITokenPermission(permissions.BasePermission):
    message = "API Token is not provided or it's invalid."

    def has_permission(self, request, view):
        api_key = request.query_params.get('apiKey', False)
        if api_key and Token.objects.filter(key=api_key).exists():
            return True

        return False
