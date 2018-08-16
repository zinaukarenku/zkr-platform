import json

from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library

register = Library()


@register.filter()
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return serialize('json', obj)
    return json.dumps(obj)
