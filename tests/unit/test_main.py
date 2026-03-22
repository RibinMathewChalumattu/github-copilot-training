from typing import List

import pytest

from app.main import (
    fetch_all_tasks,
    generate_productivity_report,
    get_all_tasks,
    get_productivity_report,
    get_status,
    get_task_status,
    log_task,
)
from app.models import DeveloperTask, ProductivityReport, TaskLogResponse, TaskStatus


@pytest.mark.asyncio
async def test_fetch_all_tasks_returns_all_mock_tasks() -> None:
    tasks = await fetch_all_tasks()

    assert len(tasks) == 3
    assert all(isinstance(task, DeveloperTask) for task in tasks)


@pytest.mark.asyncio
async def test_generate_productivity_report_calculates_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    test_tasks = [
        DeveloperTask(task_id=1, title="A", status=TaskStatus.COMPLETE, hours_spent=1.25),
        DeveloperTask(task_id=2, title="B", status=TaskStatus.IN_PROGRESS, hours_spent=2.75),
        DeveloperTask(task_id=3, title="C", status=TaskStatus.COMPLETE, hours_spent=3.0),
    ]

    async def fake_fetch_all_tasks() -> List[DeveloperTask]:
        return test_tasks

    monkeypatch.setattr("app.main.fetch_all_tasks", fake_fetch_all_tasks)

    report = await generate_productivity_report()

    assert report == ProductivityReport(
        total_tasks=3,
        completed_tasks=2,
        total_hours_spent=7.0,
        completion_rate=0.67,
    )


@pytest.mark.asyncio
async def test_generate_productivity_report_returns_zero_completion_rate_for_no_tasks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_fetch_all_tasks() -> List[DeveloperTask]:
        return []

    monkeypatch.setattr("app.main.fetch_all_tasks", fake_fetch_all_tasks)

    report = await generate_productivity_report()

    assert report == ProductivityReport(
        total_tasks=0,
        completed_tasks=0,
        total_hours_spent=0.0,
        completion_rate=0.0,
    )


@pytest.mark.asyncio
async def test_get_status_returns_ok_dict() -> None:
    assert await get_status() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_all_tasks_returns_fetch_results(monkeypatch: pytest.MonkeyPatch) -> None:
    test_tasks = [
        DeveloperTask(task_id=10, title="Review PR", status=TaskStatus.PENDING, hours_spent=0.5)
    ]

    async def fake_fetch_all_tasks() -> List[DeveloperTask]:
        return test_tasks

    monkeypatch.setattr("app.main.fetch_all_tasks", fake_fetch_all_tasks)

    assert await get_all_tasks() == test_tasks


@pytest.mark.asyncio
async def test_get_productivity_report_returns_generated_report(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_report = ProductivityReport(
        total_tasks=4,
        completed_tasks=3,
        total_hours_spent=12.5,
        completion_rate=0.75,
    )

    async def fake_generate_productivity_report() -> ProductivityReport:
        return expected_report

    monkeypatch.setattr("app.main.generate_productivity_report", fake_generate_productivity_report)

    assert await get_productivity_report() == expected_report


@pytest.mark.asyncio
async def test_log_task_assigns_next_id_and_returns_response() -> None:
    task = DeveloperTask(
        task_id=0,
        title="Document API",
        status=TaskStatus.PENDING,
        hours_spent=1.0,
    )

    response = await log_task(task)

    assert response == TaskLogResponse(
        message="Task ID 4 logged successfully.",
        task_id=4,
    )
    assert task.task_id == 4


@pytest.mark.asyncio
async def test_get_task_status_returns_existing_task_status() -> None:
    assert await get_task_status(1) == {"task_id": "1", "status": "complete"}


@pytest.mark.asyncio
async def test_get_task_status_returns_error_for_missing_task() -> None:
    assert await get_task_status(999) == {"error": "Task not found"}