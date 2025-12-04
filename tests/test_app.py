import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    # Remove if already present
    client.post(f"/activities/{activity}/signup?email={email}")
    # Try to sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200 or response.status_code == 400
    if response.status_code == 200:
        assert f"Signed up {email}" in response.json()["message"]
    else:
        assert response.json()["detail"] == "Student is already signed up for this activity"

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_max_capacity():
    activity = "Chess Club"
    # Fill up the activity
    for i in range(20):
        email = f"user{i}@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={email}")
    # Set max_participants to current number
    from src.app import activities
    activities[activity]["max_participants"] = len(activities[activity]["participants"])
    response = client.post(f"/activities/{activity}/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is at maximum capacity"
