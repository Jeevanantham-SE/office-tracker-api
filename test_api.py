import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
from auth import EXPECTED_API_KEY

# Use a separate test SQLite database so real office_tracker.db is untouched
TEST_DATABASE_URL = "sqlite:///./test_office_tracker.db"
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)
HEADERS = {"X-API-Key": EXPECTED_API_KEY}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Office Leave & Task Tracker" in response.text


def test_missing_api_key_rejected():
    response = client.get("/tasks")
    assert response.status_code == 401


def test_create_list_update_delete_task():
    # Create task
    create_res = client.post(
        "/tasks",
        json={"title": "Prepare monthly report", "assignee": "Jeevanantham"},
        headers=HEADERS,
    )
    assert create_res.status_code == 201
    created = create_res.json()
    task_id = created["id"]
    assert created["title"] == "Prepare monthly report"
    assert created["done"] is False

    # List tasks
    list_res = client.get("/tasks", headers=HEADERS)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # Update task
    patch_res = client.patch(
        f"/tasks/{task_id}",
        json={"done": True},
        headers=HEADERS,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["done"] is True

    # Delete task
    delete_res = client.delete(f"/tasks/{task_id}", headers=HEADERS)
    assert delete_res.status_code == 200

    # Confirm deleted
    after_delete = client.get("/tasks", headers=HEADERS)
    assert after_delete.status_code == 200
    assert len(after_delete.json()) == 0


def test_create_and_approve_leave():
    leave_res = client.post(
        "/leaves",
        json={
            "employee_name": "Jeevanantham",
            "start_date": "2026-12-10",
            "end_date": "2026-12-12",
            "reason": "Family function",
        },
        headers=HEADERS,
    )
    assert leave_res.status_code == 201
    leave_id = leave_res.json()["id"]
    assert leave_res.json()["status"] == "Pending"

    approve_res = client.patch(f"/leaves/{leave_id}/approve", headers=HEADERS)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "Approved"
