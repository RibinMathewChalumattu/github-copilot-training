from typing import List

import pytest
from httpx import AsyncClient
from pydantic import TypeAdapter

from app.models import DeveloperTask, ProductivityReport, TaskLogResponse


@pytest.mark.asyncio
@pytest.mark.integration
async def test_status_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_returns_valid_developer_task_list(client: AsyncClient) -> None:
    response = await client.get("/tasks")

    assert response.status_code == 200
    tasks = TypeAdapter(List[DeveloperTask]).validate_python(response.json())
    assert len(tasks) == 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_report_returns_valid_productivity_report(client: AsyncClient) -> None:
    response = await client.get("/report")

    assert response.status_code == 200
    report = ProductivityReport.model_validate(response.json())
    assert report.total_tasks == 3
    assert report.completed_tasks == 1
    assert report.total_hours_spent == 23.5
    assert report.completion_rate == 0.33


@pytest.mark.asyncio
@pytest.mark.integration
async def test_log_task_creates_task_and_status_endpoint_reflects_it(client: AsyncClient) -> None:
    response = await client.post(
        "/log_task",
        json={
            "task_id": 0,
            "title": "Ship release notes",
            "status": "pending",
            "hours_spent": 2.5,
        },
    )

    assert response.status_code == 200
    task_log_response = TaskLogResponse.model_validate(response.json())
    assert task_log_response.task_id == 4

    status_response = await client.get(f"/task/{task_log_response.task_id}/status")

    assert status_response.status_code == 200
    assert status_response.json() == {"task_id": "4", "status": "pending"}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_log_task_rejects_invalid_payload(client: AsyncClient) -> None:
    response = await client.post(
        "/log_task",
        json={
            "task_id": 0,
            "status": "pending",
            "hours_spent": 1.0,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_task_status_returns_not_found_payload_for_missing_task(client: AsyncClient) -> None:
    response = await client.get("/task/999/status")

    assert response.status_code == 200
    assert response.json() == {"error": "Task not found"}