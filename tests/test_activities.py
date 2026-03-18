"""
Comprehensive tests for Mergington High School API using AAA (Arrange-Act-Assert) pattern
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_complete_list(self, client, reset_activities):
        """Test retrieving all activities returns the complete list"""
        # ARRANGE - No setup needed, activities are pre-loaded
        
        # ACT
        response = client.get("/activities")
        data = response.json()
        
        # ASSERT
        assert response.status_code == 200
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activity_has_correct_structure(self, client, reset_activities):
        """Test that activities contain all required fields with correct types"""
        # ARRANGE
        activity_name = "Chess Club"
        
        # ACT
        response = client.get("/activities")
        activity = response.json()[activity_name]
        
        # ASSERT
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)
    
    def test_activities_have_initial_participants(self, client, reset_activities):
        """Test that pre-loaded activities have their initial participants"""
        # ARRANGE
        expected_chess_club_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # ACT
        response = client.get("/activities")
        chess_club = response.json()["Chess Club"]
        
        # ASSERT
        assert len(chess_club["participants"]) == len(expected_chess_club_participants)
        for email in expected_chess_club_participants:
            assert email in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_new_student_can_sign_up_for_activity(self, client, reset_activities):
        """Test that a new student can successfully sign up for an activity"""
        # ARRANGE
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity's list"""
        # ARRANGE
        email = "testuser@mergington.edu"
        activity_name = "Basketball Club"
        
        # ACT
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        
        # ASSERT
        participants = response.json()[activity_name]["participants"]
        assert email in participants
    
    def test_signup_fails_for_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails with 404 when activity doesn't exist"""
        # ARRANGE
        email = "student@mergington.edu"
        nonexistent_activity = "Nonexistent Club"
        
        # ACT
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_fails_when_student_already_registered(self, client, reset_activities):
        """Test that signup fails with 400 when student already signed up"""
        # ARRANGE
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_multiple_students_can_signup_for_same_activity(self, client, reset_activities):
        """Test that multiple different students can sign up for the same activity"""
        # ARRANGE
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        activity_name = "Gym Class"
        
        # ACT
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # ASSERT
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants
    
    def test_student_can_signup_for_multiple_activities(self, client, reset_activities):
        """Test that the same student can sign up for different activities"""
        # ARRANGE
        email = "versatile@mergington.edu"
        activities_to_join = ["Soccer Team", "Art Studio", "Science Club"]
        
        # ACT
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # ASSERT
        response = client.get("/activities")
        all_activities = response.json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_student_can_unregister_from_activity(self, client, reset_activities):
        """Test that a student can successfully unregister from an activity"""
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]
    
    def test_unregister_removes_participant_from_activity(self, client, reset_activities):
        """Test that unregister actually removes the participant from the list"""
        # ARRANGE
        email = "daniel@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
        response = client.get("/activities")
        
        # ASSERT
        participants = response.json()[activity_name]["participants"]
        assert email not in participants
    
    def test_unregister_fails_for_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails with 404 when activity doesn't exist"""
        # ARRANGE
        email = "student@mergington.edu"
        nonexistent_activity = "Phantom Club"
        
        # ACT
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_fails_when_student_not_signed_up(self, client, reset_activities):
        """Test that unregister fails with 400 when student is not signed up"""
        # ARRANGE
        email = "nosuchstudent@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # ASSERT
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_one_student_doesnt_affect_others(self, client, reset_activities):
        """Test that removing one student doesn't affect other participants"""
        # ARRANGE
        removed_email = "emma@mergington.edu"
        remaining_email = "sophia@mergington.edu"
        activity_name = "Programming Class"
        
        # ACT
        client.delete(f"/activities/{activity_name}/unregister", params={"email": removed_email})
        response = client.get("/activities")
        
        # ASSERT
        participants = response.json()[activity_name]["participants"]
        assert removed_email not in participants
        assert remaining_email in participants
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can unregister and then sign up again"""
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # ACT - First unregister
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # ACT - Then signup again
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT
        assert response2.status_code == 200
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_path_redirects_to_static_index(self, client):
        """Test that accessing root redirects to the static index.html"""
        # ARRANGE - No setup needed
        
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""
    
    def test_complete_signup_and_unregister_flow(self, client, reset_activities):
        """Test the complete flow: signup, verify presence, unregister, verify absence"""
        # ARRANGE
        email = "integration@mergington.edu"
        activity_name = "Art Studio"
        
        # ACT & ASSERT - Step 1: Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # ACT & ASSERT - Step 2: Verify in activity
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # ACT & ASSERT - Step 3: Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # ACT & ASSERT - Step 4: Verify removed
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
    
    def test_signup_unregister_and_reregister(self, client, reset_activities):
        """Test signing up, unregistering, and re-registering for an activity"""
        # ARRANGE
        email = "boomerang@mergington.edu"
        activity_name = "Music Ensemble"
        
        # ACT - Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        
        # ASSERT - Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # ACT - Unregister
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})
        
        # ASSERT - Verify removed
        response = client.get("/activities")
        assert email not in response.json()[activity_name]["participants"]
        
        # ACT - Re-register
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # ASSERT - Verify re-registered
        assert response.status_code == 200
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
