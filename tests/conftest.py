import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from uuid import uuid4

from api.db.database import get_db
from api.services.auth import AuthService
from main import app



USER_ID = str(uuid4())
TASK_ID = str(uuid4())
USER_EMAIL = "testing@demo.com"
USER_USERNAME = "test"

@pytest.fixture
def mock_task_object():
    return {
        # "id": TASK_ID,
        "title": "Test Task",
        "description": "Test Task Description",
        "dueDate": "2021-09-01",
        "status": "pending",
        "priority": "low",
        "created_by": USER_ID,
        "assigned_to": USER_EMAIL,
        "tags": ["test", "task"],
        "user": {
            # "id": USER_ID,
            "email": USER_EMAIL,
            "username": USER_USERNAME,
            "password": "test_password"
        }
    }

@pytest.fixture
def mock_user_object():
    return {
        # "id": USER_ID,
        "email": USER_EMAIL,
        "username": USER_USERNAME,
        "password": "test_password",
        "tasks": []
    }


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = lambda: mock_db_session

    client = TestClient(app)
    yield client
    app.dependency_overrides = {}


# @pytest.fixture
# def mock_item_service(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr('api.services.task.TaskService', mock)
#     return mock


# @pytest.fixture
# def mock_redis_cache(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr('api.services.task.redis_cache', mock)
#     return mock


# @pytest.fixture
# def mock_auth_service(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr('api.services.auth.AuthService.get_current_user', mock)
#     return mock



# @pytest.fixture
# def mock_requests(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr('requests.get', mock)
#     return mock

# # set up mocking with sqlalchemy
# @pytest.fixture
# def mock_sqlalchemy(monkeypatch):
#     mock = MagicMock()
#     monkeypatch.setattr('api.services.task.TaskService.get_task_by_id', mock)
#     return mock

