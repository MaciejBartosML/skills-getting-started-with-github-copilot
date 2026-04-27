"""
Tests for the Mergington High School API.

All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import copy

import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app

ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after every test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_returns_all_activities(self, client):
        # Arrange

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9

    def test_activity_has_required_fields(self, client):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        activity = response.json()[activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    def test_signup_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in app_module.activities[activity]["participants"]

    def test_signup_returns_confirmation_message(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.json() == {"message": f"Signed up {email} for {activity}"}

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_duplicate_returns_400(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student already signed up for this activity"}


class TestUnregister:
    def test_unregister_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email not in app_module.activities[activity]["participants"]

    def test_unregister_returns_confirmation_message(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.json() == {"message": f"Unregistered {email} from {activity}"}

    def test_unregister_unknown_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_unregister_not_signed_up_returns_404(self, client):
        # Arrange
        activity = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Student is not signed up for this activity"}
