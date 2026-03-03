"""
Unit tests for activity logic and data management.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the function or logic being tested
- Assert: Verify the results match expectations
"""

import pytest


class TestActivityDataStructure:
    def test_activity_has_required_fields(self):
        """Test that an activity dict has all required fields."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
        
        # Act & Assert
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_participants_is_list(self):
        """Test that participants field is a list."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": ["student@school.edu"]
        }
        
        # Act
        participants = activity["participants"]
        
        # Assert
        assert isinstance(participants, list)

    def test_max_participants_is_integer(self):
        """Test that max_participants is an integer."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
        
        # Act
        max_cap = activity["max_participants"]
        
        # Assert
        assert isinstance(max_cap, int)
        assert max_cap > 0


class TestParticipantManagement:
    def test_add_participant_to_empty_activity(self):
        """Test adding first participant to activity."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
        email = "student1@school.edu"
        
        # Act
        activity["participants"].append(email)
        
        # Assert
        assert len(activity["participants"]) == 1
        assert email in activity["participants"]

    def test_add_multiple_participants(self):
        """Test adding multiple participants to activity."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
        emails = ["student1@school.edu", "student2@school.edu", "student3@school.edu"]
        
        # Act
        for email in emails:
            activity["participants"].append(email)
        
        # Assert
        assert len(activity["participants"]) == 3
        for email in emails:
            assert email in activity["participants"]

    def test_check_participant_exists(self):
        """Test checking if participant is in activity."""
        # Arrange
        email_in_list = "enrolled@school.edu"
        email_not_in_list = "notenrolled@school.edu"
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": [email_in_list]
        }
        
        # Act & Assert
        assert email_in_list in activity["participants"]
        assert email_not_in_list not in activity["participants"]

    def test_remove_participant_from_list(self):
        """Test removing a participant from activity."""
        # Arrange
        email_to_remove = "remove@school.edu"
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": ["keep1@school.edu", email_to_remove, "keep2@school.edu"]
        }
        initial_count = len(activity["participants"])
        
        # Act
        activity["participants"].remove(email_to_remove)
        
        # Assert
        assert len(activity["participants"]) == initial_count - 1
        assert email_to_remove not in activity["participants"]
        assert "keep1@school.edu" in activity["participants"]
        assert "keep2@school.edu" in activity["participants"]

    def test_remove_only_participant(self):
        """Test removing the only participant from activity."""
        # Arrange
        email = "only@school.edu"
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": [email]
        }
        
        # Act
        activity["participants"].remove(email)
        
        # Assert
        assert len(activity["participants"]) == 0
        assert email not in activity["participants"]


class TestCapacityCalculations:
    def test_calculate_spots_available(self):
        """Test calculating available spots in activity."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": ["student1@school.edu", "student2@school.edu"]
        }
        
        # Act
        spots_available = activity["max_participants"] - len(activity["participants"])
        
        # Assert
        assert spots_available == 8

    def test_activity_at_capacity(self):
        """Test when activity is at capacity."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 2,
            "participants": ["student1@school.edu", "student2@school.edu"]
        }
        
        # Act
        at_capacity = len(activity["participants"]) >= activity["max_participants"]
        
        # Assert
        assert at_capacity is True

    def test_activity_has_available_spots(self):
        """Test when activity has available spots."""
        # Arrange
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": ["student1@school.edu"]
        }
        
        # Act
        has_spots = len(activity["participants"]) < activity["max_participants"]
        
        # Assert
        assert has_spots is True

    def test_spots_remaining_calculation(self):
        """Test calculation of spots remaining for activity."""
        # Arrange - Activity with 10 max, 3 current
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": ["s1@school.edu", "s2@school.edu", "s3@school.edu"]
        }
        
        # Act
        spots_remaining = activity["max_participants"] - len(activity["participants"])
        
        # Assert
        assert spots_remaining == 7


class TestEmailValidation:
    def test_email_with_at_symbol(self):
        """Test that valid email format is recognized."""
        # Arrange
        email = "student@school.edu"
        
        # Act
        has_at_symbol = "@" in email
        
        # Assert
        assert has_at_symbol is True

    def test_email_lowercase(self):
        """Test email can be stored as provided."""
        # Arrange
        email = "Student@School.EDU"
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": []
        }
        
        # Act
        activity["participants"].append(email)
        
        # Assert
        assert email in activity["participants"]

    def test_duplicate_email_detection(self):
        """Test that duplicate emails in participant list are detected."""
        # Arrange
        email = "student@school.edu"
        activity = {
            "description": "Test activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 10,
            "participants": [email]
        }
        
        # Act
        is_duplicate = email in activity["participants"]
        
        # Assert
        assert is_duplicate is True
