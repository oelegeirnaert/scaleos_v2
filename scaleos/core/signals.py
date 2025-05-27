import json
import logging

from celery.signals import task_failure
from celery.signals import task_success
from django.utils.timezone import now
from django_celery_results.models import TaskResult

logger = logging.getLogger(__name__)


@task_success.connect
def store_success_in_db(sender=None, result=None, **kwargs):
    task_id = kwargs.get("task_id") or getattr(sender, "request", {}).get("id")
    task_name = sender.name if sender else None
    args = kwargs.get("args", [])
    kwargs_ = kwargs.get("kwargs", {})
    logger.debug("Storing SUCCESS result for task %s", task_id)

    if task_id is None:
        logger.warning("Task ID is missing. Could not store success.")
        return False  # You can choose to raise an error or return silently

    TaskResult.objects.update_or_create(
        task_id=task_id,
        defaults={
            "task_name": task_name,
            "status": "SUCCESS",
            "result": json.dumps(result),
            "date_done": now(),
            "traceback": None,
            "meta": json.dumps({"args": args, "kwargs": kwargs_}),
        },
    )
    return True


@task_failure.connect
def store_failure_in_db(sender=None, exception=None, traceback=None, **kwargs):
    task_id = kwargs.get("task_id") or getattr(sender, "request", {}).get("id")
    task_name = sender.name if sender else None
    args = kwargs.get("args", [])
    kwargs_ = kwargs.get("kwargs", {})

    if task_id is None:
        logger.warning("Task ID is missing. Could not store failure.")
        return False  # You can choose to raise an error or return silently

    logger.warning("Storing FAILURE result for task %s: %s", task_id, exception)

    TaskResult.objects.update_or_create(
        task_id=task_id,
        defaults={
            "task_name": task_name,
            "status": "FAILURE",
            "result": str(exception),
            "date_done": now(),
            "traceback": traceback,
            "meta": json.dumps({"args": args, "kwargs": kwargs_}),
        },
    )
    return True
