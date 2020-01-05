from celery import shared_task
from politicians.models import Promises, PromiseAction

@shared_task(soft_time_limit=30)
def get_promise_action_scores(promiseaction_id=None):
    promiseAction = PromiseAction.objects.filter(pk=promiseaction_id)