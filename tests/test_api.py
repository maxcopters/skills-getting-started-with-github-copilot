"""
Integration tests for Mergington High School API endpoints.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the function or endpoint being tested
- Assert: Verify the results match expectations
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test."""
    # Arrange: Set up clean test data
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["tyler@mergington.edu", "grace@mergington.edu"]
        }
    })
    yield
    # Cleanup after test
    activities.clear()


# Tests for GET /activities
class TestGetActivities:
    def test_get_all_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_correct_structure(self, client):
        """Test that GET /activities returns activities with correct data structure."""
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "description" in data["Chess Club"]
        assert "schedule" in data["Chess Club"]
        assert "max_participants" in data["Chess Club"]
        assert "participants" in data["Chess Club"]
        assert isinstance(data["Chess Club"]["participants"], list)

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all populated activities."""
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Debate Team" in data

    def test_get_activities_shows_current_participants(self, client):
        """Test that activities show the current list of participants."""
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 2


# Tests for POST /activities/{activity_name}/signup
class TestSignupForActivity:
    def test_signup_new_student_returns_200(self, client):
        """Test signing up a new student returns 200 status code."""
        # Act
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 200

    def test_signup_new_student_returns_success_message(self, client):
        """Test that successful signup returns appropriate message."""
        # Act
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Act
        client.post(
            "/activities/Programming Class/signup?email=john.doe@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "john.doe@mergington.edu" in data["Programming Class"]["participants"]
        assert len(data["Programming Class"]["participants"]) == 2

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that signing up twice with same email returns 400 error."""
        # Arrange
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        # Act
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404."""
        # Act
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_different_students_to_same_activity(self, client):
        """Test that multiple different students can sign up for same activity."""
        # Arrange
        email1 = "alice@mergington.edu"
        email2 = "bob@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/Programming Class/signup?email={email1}"
        )
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email2}"
        )
        activities_response = client.get("/activities")
        activity_data = activities_response.json()["Programming Class"]
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activity_data["participants"]
        assert email2 in activity_data["participants"]
        assert len(activity_data["participants"]) == 3

    def test_signup_same_student_different_activities(self, client):
        """Test that same student can sign up for different activities."""
        # Arrange
        email = "versatile@mergington.edu"
        
        # Act
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        activities_response = client.get("/activities")
        data = activities_response.json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


# Tests for DELETE /activities/{activity_name}/unregister
class TestUnregisterFromActivity:
    def test_unregister_existing_participant_returns_200(self, client):
        """Test that unregistering an enrolled student returns 200."""
        # Act
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns appropriate message."""
        # Act
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_unregister_removes_participant_from_activity(self, client):
        """Test that unregister actually removes participant from activity."""
        # Arrange
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Act
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Chess Club"]["participants"])
        
        # Assert
        assert final_count == initial_count - 1
        assert "michael@mergington.edu" not in final_response.json()["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from non-existent activity returns 404."""
        # Act
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_non_registered_student_returns_404(self, client):
        """Test that unregistering non-enrolled student returns 404."""
        # Act
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_unregister_all_participants_from_activity(self, client):
        """Test that all participants can be unregistered from an activity."""
        # Arrange
        participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        for email in participants:
            client.delete(
                f"/activities/Chess Club/unregister?email={email}"
            )
        response = client.get("/activities")
        final_participants = response.json()["Chess Club"]["participants"]
        
        # Assert
        assert len(final_participants) == 0


# Tests for special scenarios
class TestActivityCapacityAndAvailability:
    def test_can_fill_activity_to_capacity(self, client):
        """Test signing up students until activity is at max capacity."""
        # Arrange - Debate Team has max 3 participants, already has 2
        emails = ["student1@mergington.edu", "student2@mergington.edu", 
                  "student3@mergington.edu", "student4@mergington.edu"]
        
        # Act - Try to fill and overfill
        response1 = client.post(
            f"/activities/Debate Team/signup?email={emails[2]}"
        )  # Should succeed (3rd spot)
        response2 = client.post(
            f"/activities/Debate Team/signup?email={emails[3]}"
        )  # Should succeed (4th spot, no capacity check in current implementation)
        
        # Assert
        assert response1.status_code == 200
        # Note: Current implementation doesn't enforce max_participants, so response2 also succeeds
        assert response2.status_code == 200

    def test_signup_and_unregister_in_sequence(self, client):
        """Test complete flow of signup, verify, unregister, verify."""
        # Arrange
        email = "test@mergington.edu"
        activity = "Programming Class"
        
        # Act & Assert - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Check participant added
        get_response = client.get("/activities")
        assert email in get_response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Check participant removed
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]
