from logging import getLogger

from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework_tracking.models import APIRequestLog

logger = getLogger(__name__)


@receiver(pre_save, sender=APIRequestLog)
def modify_api_request_log(sender, instance, **kwargs):
    instance.response = None
