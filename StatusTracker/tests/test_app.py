#TODO: Create Unit Tests + unit test coverage

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

import pytest

"""
Sample data to use for most task operations
"""
@pytest.fixture
def sample_task_with_title_and_description():
    return {"title": "TEST TITLE", "description": "TEST DESCRIPTION"}


"""
Task with id, title, description, and completed fields
"""
@pytest.fixture
def sample_all_fields_task():
    return {"id": 67, "title": "67 FULL TEST TITLE", "description": "FULL TEST DESCRIPTION", "completed": False}

def test_root_returns_something():
    response = client.get("/")
    assert response.status_code < 500


def test_python_still_does_math():
    assert 10 + 5 == 15

def test_get_root():
    response = client.get("/")
    assert response.status_code == 200

def test_create_task_with_no_title():
    response = client.post("/tasks", json = {"description": "description"})
    assert response.status_code == 422

def test_create_task_with_valid_title_and_description(sample_task_with_title_and_description):
    payload = {"title": sample_task_with_title_and_description["title"], "description": sample_task_with_title_and_description["description"]}
    response = client.post("/tasks", json = payload)
    assert response.status_code == 201

#TODO: Set up test DB connection, add sample data (sample_all_fields_task), and test GET using test fixtures making sure that the returned task matches sample_all_fields_task
#Started Implementation Below
# def test_get_task_by_valid_task_id():
#     response = client.get("/tasks", params = {"task_id": })

#TODO: Create tests for all other endpoints
#TODO: Create tests for database connection



"""
Running the Application

Requirements
------------
Python 3.9+

Setup
-----
Create a virtual environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements.txt

Run
---
Start the application:

    uvicorn app.main:app --reload

The API will be available at:

    http://127.0.0.1:8000

Interactive API documentation is available at:

    http://127.0.0.1:8000/docs
"""