import json

import pytest
from django_celery_results.models import TaskResult

from scaleos.core.signals import store_failure_in_db
from scaleos.core.signals import store_success_in_db


@pytest.mark.django_db
def test_store_success_in_db_creates_task_result():
    task_id = "success-task-id-123"
    task_name = "my_app.tasks.example_success"
    result = {"status": "done"}
    args = [1, 2]
    kwargs_ = {"foo": "bar"}

    success_signal_data = {
        "task_id": task_id,
        "args": args,
        "kwargs": kwargs_,
    }

    class DummySender:
        name = task_name
        request = {"id": task_id}

    assert (
        store_success_in_db(
            sender=DummySender(),
            result=result,
            **success_signal_data,
        )
        is True
    )

    task_result = TaskResult.objects.get(task_id=task_id)
    assert task_result.status == "SUCCESS"
    assert json.loads(task_result.result) == result
    assert json.loads(task_result.meta) == {"args": args, "kwargs": kwargs_}

    class DummySenderWithoutTaskID:
        name = task_name

    success_signal_data_without_task_id = {
        "args": args,
        "kwargs": kwargs_,
    }
    assert (
        store_success_in_db(
            sender=DummySenderWithoutTaskID(),
            result=result,
            **success_signal_data_without_task_id,
        )
        is False
    )


@pytest.mark.django_db
def test_store_failure_in_db_creates_task_result():
    task_id = "failure-task-id-456"
    task_name = "my_app.tasks.example_failure"
    exception = ValueError("Something went wrong")
    fake_traceback = "Traceback (most recent call last): ..."

    args = [9]
    kwargs_ = {"key": "value"}

    failure_signal_data = {
        "task_id": task_id,
        "args": args,
        "kwargs": kwargs_,
    }

    class DummySender:
        name = task_name
        request = {"id": task_id}

    assert (
        store_failure_in_db(
            sender=DummySender(),
            exception=exception,
            traceback=fake_traceback,
            **failure_signal_data,
        )
        is True
    )

    task_result = TaskResult.objects.get(task_id=task_id)
    assert task_result.status == "FAILURE"
    assert task_result.result == str(exception)
    assert task_result.traceback == fake_traceback
    assert json.loads(task_result.meta) == {"args": args, "kwargs": kwargs_}

    class DummySenderWithoutTaskID:
        name = task_name

    failure_signal_data_without_task_id = {
        "args": args,
        "kwargs": kwargs_,
    }
    assert (
        store_failure_in_db(
            sender=DummySenderWithoutTaskID(),
            exception=exception,
            traceback=fake_traceback,
            **failure_signal_data_without_task_id,
        )
        is False
    )
