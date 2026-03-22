from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app import main


@pytest.fixture
def app() -> FastAPI:
    return main.app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture(autouse=True)
def reset_mock_tasks() -> Iterator[None]:
    original_tasks = {
        task_id: task.model_copy(deep=True)
        for task_id, task in main.MOCK_TASKS.items()
    }
    yield
    main.MOCK_TASKS.clear()
    main.MOCK_TASKS.update(
        {
            task_id: task.model_copy(deep=True)
            for task_id, task in original_tasks.items()
        }
    )


@pytest.fixture
def db_session() -> None:
    return None


@pytest.fixture
def auth_token() -> str:
    return "test-token"