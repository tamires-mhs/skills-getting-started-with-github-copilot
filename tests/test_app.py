"""
Tests for the High School Management System API
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirect(self):
        """Test that root redirects to /static/index.html"""
        # Arrange
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location


class TestGetActivities:
    """Test get activities endpoint"""
    
    def test_get_activities_returns_dict(self):
        """Test that get_activities returns a dictionary of activities"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
    
    def test_get_activities_contains_expected_fields(self):
        """Test that each activity has required fields"""
        # Arrange
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_specific_activities(self):
        """Test that known activities are present"""
        # Arrange
        expected_activities = [
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity in expected_activities:
            assert activity in activities


class TestSignupForActivity:
    """Test signup for activity endpoint"""
    
    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Basketball Team"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]
    
    def test_signup_already_registered(self):
        """Test signup fails for already registered student"""
        # Arrange
        email = "alex@mergington.edu"  # Already registered for Basketball Team
        activity = "Basketball Team"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_not_found(self):
        """Test signup fails for non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_students(self):
        """Test multiple students can sign up for the same activity"""
        # Arrange
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        activity = "Tennis Club"
        
        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestUnregisterFromActivity:
    """Test unregister from activity endpoint"""
    
    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # Arrange
        email = "unregister_test@mergington.edu"
        activity = "Drama Club"
        
        # First sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_not_registered(self):
        """Test unregistration fails for non-registered student"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_activity_not_found(self):
        """Test unregistration fails for non-existent activity"""
        # Arrange
        email = "student@mergington.edu"
        activity = "Fake Activity"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_removes_from_participants(self):
        """Test that unregistration actually removes student from participants"""
        # Arrange
        email = "removal_test@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        client.post(f"/activities/{activity}/signup", params={"email": email})
        
        # Verify in participants
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email in participants
        
        # Act
        client.delete(f"/activities/{activity}/signup", params={"email": email})
        
        # Assert
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email not in participants