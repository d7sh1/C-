import pytest
from fastapi.testclient import TestClient
import sys
import os
from uuid import uuid4

# Adjust the path to import the app from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, Task # TaskCreate and TaskUpdate are not directly used in tests, but Task is for response validation

client = TestClient(app)

# Global variable to store task ID for dependent tests
created_task_id = None
created_task_data = None

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_task():
    global created_task_id, created_task_data
    task_data = {
        "title": "Test Task",
        "description": "This is a test description",
        "status": "pending"
    }
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "id" in data
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    created_task_id = data["id"]
    created_task_data = data

def test_read_tasks_after_creation():
    assert created_task_id is not None, "Cannot run read_tasks_after_creation: created_task_id is None"
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    found = any(task["id"] == created_task_id for task in data)
    assert found, "Created task not found in the list of all tasks."

def test_read_one_task():
    global created_task_id, created_task_data
    assert created_task_id is not None, "Cannot run read_one_task: created_task_id is None"
    assert created_task_data is not None, "Cannot run read_one_task: created_task_data is None"
    response = client.get(f"/tasks/{created_task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_task_id
    assert data["title"] == created_task_data["title"]
    assert data["description"] == created_task_data["description"]
    assert data["status"] == created_task_data["status"]

def test_read_nonexistent_task():
    non_existent_id = str(uuid4())
    response = client.get(f"/tasks/{non_existent_id}")
    assert response.status_code == 404

def test_update_task():
    global created_task_id
    assert created_task_id is not None, "Cannot run update_task: created_task_id is None"
    update_data = {
        "title": "Updated Test Task",
        "description": "This is an updated test description",
        "status": "in progress"
    }
    response = client.put(f"/tasks/{created_task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_task_id
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]

    response_verify = client.get(f"/tasks/{created_task_id}")
    assert response_verify.status_code == 200
    data_verify = response_verify.json()
    assert data_verify["title"] == update_data["title"]
    assert data_verify["description"] == update_data["description"]
    assert data_verify["status"] == update_data["status"]

def test_update_nonexistent_task():
    non_existent_id = str(uuid4())
    update_data = {"title": "Trying to update non-existent"}
    response = client.put(f"/tasks/{non_existent_id}", json=update_data)
    assert response.status_code == 404

def test_delete_task():
    # Create a new task specifically for this delete test
    temp_task_data = {"title": "Task to be deleted", "description": "Delete me", "status": "pending"}
    response_create = client.post("/tasks", json=temp_task_data)
    assert response_create.status_code == 201
    temp_task_id = response_create.json()["id"]

    response_delete = client.delete(f"/tasks/{temp_task_id}")
    assert response_delete.status_code == 204

    response_verify = client.get(f"/tasks/{temp_task_id}")
    assert response_verify.status_code == 404

def test_delete_nonexistent_task():
    non_existent_id = str(uuid4())
    response = client.delete(f"/tasks/{non_existent_id}")
    assert response.status_code == 404
