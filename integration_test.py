#!/usr/bin/env python3
"""
Integration test for Event Attendance API
Tests the complete flow: user registration -> login -> event creation -> attendance marking
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "test@example.com",
    "name": "John Doe",
    "password": "testpassword123"
}

def wait_for_server(max_attempts: int = 30, delay: float = 1.0):
    """Wait for the server to be ready"""
    print("🔄 Waiting for server to start...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
    
    print("❌ Server failed to start within the timeout period")
    return False

def register_user() -> Dict[str, Any]:
    """Register a new user"""
    print("\n🔄 Registering user...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=TEST_USER,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        user_data = response.json()
        print(f"✅ User registered successfully: {user_data['name']} ({user_data['email']})")
        print(f"   User ID: {user_data['id']}")
        return user_data
    else:
        print(f"❌ User registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("User registration failed")

def login_user() -> str:
    """Login user and return JWT token"""
    print("\n🔄 Logging in user...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        auth=(TEST_USER["email"], TEST_USER["password"])
    )
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"✅ Login successful!")
        print(f"   Token type: {token_data['token_type']}")
        print(f"   Token preview: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Login failed")

def create_event(token: str) -> Dict[str, Any]:
    """Create a new event"""
    print("\n🔄 Creating event...")
    
    # Create event for next Thursday
    event_date = datetime.now() + timedelta(days=((3 - datetime.now().weekday()) % 7 + 7))  # Next Thursday
    event_data = {
        "title": "Thursday Tech Meetup #1",
        "description": "Weekly Thursday meetup for tech enthusiasts",
        "event_date": event_date.isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/events/",
        json=event_data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    
    if response.status_code == 201:
        event = response.json()
        print(f"✅ Event created successfully: {event['title']}")
        print(f"   Event ID: {event['id']}")
        print(f"   Date: {event['event_date']}")
        print(f"   Active: {event['is_active']}")
        return event
    else:
        print(f"❌ Event creation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Event creation failed")

def mark_attendance(token: str, event_id: int) -> Dict[str, Any]:
    """Mark attendance for an event"""
    print(f"\n🔄 Marking attendance for event {event_id}...")
    
    response = requests.post(
        f"{BASE_URL}/events/{event_id}/attend",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        attendance_data = response.json()
        print(f"✅ Attendance marked successfully!")
        print(f"   Message: {attendance_data['message']}")
        print(f"   User: {attendance_data['user']['name']}")
        print(f"   Event: {attendance_data['event']['title']}")
        return attendance_data
    else:
        print(f"❌ Marking attendance failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Marking attendance failed")

def check_attendance(token: str, event_id: int) -> Dict[str, Any]:
    """Check attendance status for an event"""
    print(f"\n🔄 Checking attendance for event {event_id}...")
    
    response = requests.get(
        f"{BASE_URL}/events/{event_id}/check-attendance",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        attendance_status = response.json()
        attended = attendance_status["attended"]
        print(f"✅ Attendance check completed!")
        print(f"   Attended: {attended}")
        print(f"   User ID: {attendance_status['user_id']}")
        print(f"   Event ID: {attendance_status['event_id']}")
        return attendance_status
    else:
        print(f"❌ Checking attendance failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Checking attendance failed")

def get_user_events(token: str) -> Dict[str, Any]:
    """Get user's attended events"""
    print("\n🔄 Getting user's attended events...")
    
    response = requests.get(
        f"{BASE_URL}/users/me/events",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Retrieved user's events!")
        print(f"   Number of attended events: {len(events)}")
        for event in events:
            print(f"   - {event['title']} ({event['event_date']})")
        return events
    else:
        print(f"❌ Getting user events failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Getting user events failed")

def get_event_attendees(token: str, event_id: int) -> Dict[str, Any]:
    """Get event attendees"""
    print(f"\n🔄 Getting attendees for event {event_id}...")
    
    response = requests.get(
        f"{BASE_URL}/events/{event_id}/attendees",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        attendees = response.json()
        print(f"✅ Retrieved event attendees!")
        print(f"   Number of attendees: {len(attendees)}")
        for attendee in attendees:
            print(f"   - {attendee['name']} ({attendee['email']})")
        return attendees
    else:
        print(f"❌ Getting event attendees failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Getting event attendees failed")

def run_integration_test():
    """Run the complete integration test"""
    print("🚀 Starting Event Attendance API Integration Test")
    print("=" * 60)
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            return False
        
        # Step 1: Register user
        user = register_user()
        
        # Step 2: Login and get token
        token = login_user()
        
        # Step 3: Create event
        event = create_event(token)
        event_id = event["id"]
        
        # Step 4: Check attendance before marking (should be False)
        attendance_before = check_attendance(token, event_id)
        if attendance_before["attended"]:
            print("❌ User should not be marked as attended initially")
            return False
        
        # Step 5: Mark attendance
        attendance_response = mark_attendance(token, event_id)
        
        # Step 6: Check attendance after marking (should be True)
        attendance_after = check_attendance(token, event_id)
        if not attendance_after["attended"]:
            print("❌ User should be marked as attended after marking attendance")
            return False
        
        # Step 7: Get user's attended events
        user_events = get_user_events(token)
        if len(user_events) != 1:
            print(f"❌ Expected 1 attended event, got {len(user_events)}")
            return False
        
        # Step 8: Get event attendees
        attendees = get_event_attendees(token, event_id)
        if len(attendees) != 1:
            print(f"❌ Expected 1 attendee, got {len(attendees)}")
            return False
        
        if attendees[0]["email"] != TEST_USER["email"]:
            print(f"❌ Expected attendee {TEST_USER['email']}, got {attendees[0]['email']}")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 INTEGRATION TEST PASSED!")
        print("✅ All functionality working correctly:")
        print("   - User registration ✅")
        print("   - User login ✅") 
        print("   - Event creation ✅")
        print("   - Attendance marking ✅")
        print("   - Attendance checking ✅")
        print("   - User events retrieval ✅")
        print("   - Event attendees retrieval ✅")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED!")
        print(f"Error: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = run_integration_test()
    exit(0 if success else 1) 