import json

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class NonHtmlDebugToolbarMiddleware(MiddlewareMixin):
    """
    The Django Debug Toolbar usually only works for views that return HTML.
    This middleware wraps any JSON response in HTML if the request
    has a 'debug' query parameter (e.g. http://localhost/foo?debug)
    """

    def process_response(self, request, response):
        if request.GET.get('debug'):
            if response['Content-Type'] == 'application/json':
                content = json.dumps(json.loads(response.content), sort_keys=True, indent=2)
                response = HttpResponse('<!DOCTYPE html><html><head></head><body><pre>{}</pre></body></html>'.format(content))
                response['Content-Length'] = str(len(response.content))
                response['Content-Type'] = 'text/html'

        return response
