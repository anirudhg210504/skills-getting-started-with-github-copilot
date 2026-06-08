"""
Comprehensive test suite for FastAPI activities management endpoints.

Tests cover:
- GET /activities: retrieving all activities
- POST /activities/{activity_name}/signup: registering students
- DELETE /activities/{activity_name}/participants: removing participants
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
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Outdoor soccer training and inter-school matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu", "nina@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Indoor basketball practices and pickup games",
            "schedule": "Wednesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "sara@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and mixed-media workshops",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and school play productions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs, and research projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debating and public speaking practice",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["zoe@mergington.edu", "henry@mergington.edu"]
        }
    }
    
    # Clear and reset activities dict
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


# ============================================================================
# GET /activities Tests
# ============================================================================

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_returns_correct_structure(client):
    """Test that each activity has the correct structure."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_get_activities_includes_participants(client):
    """Test that activities include their participant lists."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

def test_signup_for_activity_success(client):
    """Test successful signup for an activity."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify participant was added
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client):
    """Test signup for an activity that doesn't exist returns 404."""
    response = client.post(
        "/activities/NonExistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_participant_rejected(client):
    """Test that signup rejects duplicate registrations with 400."""
    # First signup succeeds
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response1.status_code == 200
    
    # Second signup with same email should fail
    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response2.status_code == 400
    data = response2.json()
    assert "already signed up" in data["detail"]


def test_signup_multiple_students_to_same_activity(client):
    """Test that multiple different students can sign up for the same activity."""
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    
    response1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email1}
    )
    assert response1.status_code == 200
    
    response2 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email2}
    )
    assert response2.status_code == 200
    
    assert email1 in activities["Chess Club"]["participants"]
    assert email2 in activities["Chess Club"]["participants"]


def test_signup_with_whitespace_email(client):
    """Test signup with email containing whitespace."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "  newstudent@mergington.edu  "}
    )
    assert response.status_code == 200
    
    # Verify participant was added (including whitespace)
    assert "  newstudent@mergington.edu  " in activities["Chess Club"]["participants"]


def test_signup_fills_activity_to_capacity(client):
    """Test that students can sign up until max_participants is reached."""
    activity_name = "Chess Club"
    max_cap = activities[activity_name]["max_participants"]
    current_count = len(activities[activity_name]["participants"])
    
    # Sign up students until we reach capacity
    for i in range(max_cap - current_count):
        email = f"student{i}@mergington.edu"
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify we're at capacity
    assert len(activities[activity_name]["participants"]) == max_cap


# ============================================================================
# DELETE /activities/{activity_name}/participants Tests
# ============================================================================

def test_remove_participant_success(client):
    """Test successful removal of a participant."""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])
    
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email in data["message"]
    
    # Verify participant was removed
    assert email not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == initial_count - 1


def test_remove_participant_activity_not_found(client):
    """Test removal from non-existent activity returns 404."""
    response = client.delete(
        "/activities/NonExistent Club/participants",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant_not_found(client):
    """Test removal of non-existent participant returns 404."""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "nonexistent@mergington.edu"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_remove_participant_case_insensitive(client):
    """Test that participant removal is case-insensitive."""
    activity_name = "Chess Club"
    email_original = "michael@mergington.edu"
    email_uppercase = "MICHAEL@MERGINGTON.EDU"
    
    # Should remove the participant using uppercase email
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_uppercase}
    )
    assert response.status_code == 200
    
    # Verify original email was removed
    assert email_original not in activities[activity_name]["participants"]


def test_remove_participant_with_whitespace(client):
    """Test removal of participant with whitespace in email."""
    activity_name = "Chess Club"
    
    # First add a participant with whitespace
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "  student@mergington.edu  "}
    )
    assert response1.status_code == 200
    
    # Remove with different whitespace (should still work due to normalization)
    response2 = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "student@mergington.edu"}
    )
    assert response2.status_code == 200
    
    # Verify removal worked
    assert "  student@mergington.edu  " not in activities[activity_name]["participants"]


def test_remove_multiple_participants_sequentially(client):
    """Test removing multiple participants from an activity."""
    activity_name = "Chess Club"
    email1 = "michael@mergington.edu"
    email2 = "daniel@mergington.edu"
    
    response1 = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email1}
    )
    assert response1.status_code == 200
    assert email1 not in activities[activity_name]["participants"]
    
    response2 = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email2}
    )
    assert response2.status_code == 200
    assert email2 not in activities[activity_name]["participants"]
    assert len(activities[activity_name]["participants"]) == 0


def test_signup_after_removal(client):
    """Test that a participant can re-signup after being removed."""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    
    # Remove participant
    response1 = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    assert response1.status_code == 200
    assert email not in activities[activity_name]["participants"]
    
    # Re-signup should succeed
    response2 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert response2.status_code == 200
    assert email in activities[activity_name]["participants"]


# ============================================================================
# Integration Tests (Signup + Removal Flow)
# ============================================================================

def test_signup_and_removal_integration(client):
    """Test complete flow: signup, verify, remove, verify."""
    activity_name = "Programming Class"
    email = "integration_test@mergington.edu"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity_name]["participants"])
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify signup in list
    list_response = client.get("/activities")
    assert email in list_response.json()[activity_name]["participants"]
    assert len(list_response.json()[activity_name]["participants"]) == initial_count + 1
    
    # Remove
    remove_response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )
    assert remove_response.status_code == 200
    
    # Verify removal
    final_response = client.get("/activities")
    assert email not in final_response.json()[activity_name]["participants"]
    assert len(final_response.json()[activity_name]["participants"]) == initial_count
