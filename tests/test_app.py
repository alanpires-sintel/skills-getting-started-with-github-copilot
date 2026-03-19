import pytest
from fastapi.testclient import TestClient
from src import app
import copy

# Use a fixture to reset the in-memory activities before each test
@pytest.fixture(autouse=True)
def reset_activities(monkeypatch):
    from src import app as app_module
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))

def get_test_client():
    return TestClient(app.app)

# --- /activities endpoint ---
def test_get_activities():
    # Arrange
    client = get_test_client()
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

# --- /activities/{activity_name}/signup endpoint ---
def test_signup_success():
    # Arrange
    client = get_test_client()
    email = "newstudent@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup?email=" + email)
    # Assert
    assert response.status_code == 200
    assert f"Signed up {email} for Chess Club" in response.json()["message"]
    # Confirm participant added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    # Arrange
    client = get_test_client()
    email = "michael@mergington.edu"
    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_activity_not_found():
    # Arrange
    client = get_test_client()
    # Act
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

# --- /activities/{activity_name}/unregister endpoint ---
def test_unregister_success():
    # Arrange
    client = get_test_client()
    email = "michael@mergington.edu"
    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert f"Removed {email} from Chess Club" in response.json()["message"]
    # Confirm participant removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_registered():
    # Arrange
    client = get_test_client()
    email = "notregistered@mergington.edu"
    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Student not registered" in response.json()["detail"]

def test_unregister_activity_not_found():
    # Arrange
    client = get_test_client()
    # Act
    response = client.delete("/activities/Nonexistent/unregister?email=someone@mergington.edu")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
