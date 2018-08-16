import json

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from django.templatetags.static import StaticNode

register = Library()


class FullStaticNode(StaticNode):
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(super().url(context))


@register.tag('full_static')
def do_static(parser, token):
    return FullStaticNode.handle_token(parser, token)
