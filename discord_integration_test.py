#!/usr/bin/env python3
"""
Discord Integration test for Event Attendance API
Tests Discord bot functionality with time-based attendance validation
"""

import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
DISCORD_USER = {
    "name": "Discord Test User",
    "discord_user_id": "123456789012345678",
    "discord_username": "test_user#1234"
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

def register_discord_user() -> Dict[str, Any]:
    """Register a Discord user"""
    print("\n🔄 Registering Discord user...")
    response = requests.post(
        f"{BASE_URL}/discord/users/register",
        json=DISCORD_USER,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 201:
        user_data = response.json()
        print(f"✅ Discord user registered successfully: {user_data['name']}")
        print(f"   Discord ID: {user_data['discord_user_id']}")
        print(f"   Discord Username: {user_data['discord_username']}")
        return user_data
    else:
        print(f"❌ Discord user registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        raise Exception("Discord user registration failed")

def create_timed_events() -> Dict[str, int]:
    """Create events with different timings to test attendance validation"""
    print("\n🔄 Creating timed events...")
    
    # Login as admin user first
    admin_user = {
        "email": "admin@example.com",
        "name": "Admin User",
        "password": "adminpass123"
    }
    
    # Register admin
    requests.post(f"{BASE_URL}/auth/register", json=admin_user)
    
    # Login admin
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        auth=(admin_user["email"], admin_user["password"])
    )
    admin_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    now = datetime.now()
    events = {}
    
    # 1. Past event (should not be attendable)
    past_event = {
        "title": "Past Thursday Meetup",
        "description": "This event has already ended",
        "start_time": (now - timedelta(hours=2)).isoformat(),
        "end_time": (now - timedelta(hours=1)).isoformat(),
        "discord_channel_id": "987654321098765432"
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=past_event, headers=headers)
    if response.status_code == 201:
        events["past"] = response.json()["id"]
        print(f"✅ Created past event (ID: {events['past']})")
    
    # 2. Future event (should not be attendable yet)
    future_event = {
        "title": "Future Thursday Meetup",
        "description": "This event hasn't started yet",
        "start_time": (now + timedelta(hours=1)).isoformat(),
        "end_time": (now + timedelta(hours=2)).isoformat(),
        "discord_channel_id": "987654321098765432"
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=future_event, headers=headers)
    if response.status_code == 201:
        events["future"] = response.json()["id"]
        print(f"✅ Created future event (ID: {events['future']})")
    
    # 3. Active event (should be attendable)
    active_event = {
        "title": "Current Thursday Meetup",
        "description": "This event is happening now!",
        "start_time": (now - timedelta(minutes=10)).isoformat(),
        "end_time": (now + timedelta(minutes=50)).isoformat(),
        "discord_channel_id": "987654321098765432"
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=active_event, headers=headers)
    if response.status_code == 201:
        events["active"] = response.json()["id"]
        print(f"✅ Created active event (ID: {events['active']})")
    
    return events

def test_event_status(event_id: int, expected_status: str) -> bool:
    """Test event status endpoint"""
    print(f"\n🔄 Testing event {event_id} status (expecting: {expected_status})...")
    
    response = requests.get(f"{BASE_URL}/discord/event/{event_id}/status")
    
    if response.status_code == 200:
        status_data = response.json()
        actual_status = status_data["status"]
        can_attend = status_data["can_attend"]
        
        print(f"✅ Event status: {actual_status}")
        print(f"   Can attend: {can_attend}")
        
        if expected_status == "active":
            return actual_status == "active" and can_attend
        else:
            return actual_status == expected_status and not can_attend
    else:
        print(f"❌ Failed to get event status: {response.status_code}")
        return False

def test_discord_attendance(event_id: int, should_succeed: bool) -> bool:
    """Test Discord attendance marking"""
    print(f"\n🔄 Testing Discord attendance for event {event_id} (should {'succeed' if should_succeed else 'fail'})...")
    
    response = requests.post(
        f"{BASE_URL}/discord/attend/{event_id}",
        params={"discord_user_id": DISCORD_USER["discord_user_id"]}
    )
    
    if response.status_code == 200:
        result = response.json()
        success = result.get("success", False)
        message = result.get("message", "")
        
        print(f"✅ Response received: {message}")
        print(f"   Success: {success}")
        
        return success == should_succeed
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return not should_succeed

def test_get_active_events():
    """Test getting active events"""
    print("\n🔄 Testing get active events...")
    
    response = requests.get(f"{BASE_URL}/discord/events/active")
    
    if response.status_code == 200:
        events = response.json()
        print(f"✅ Found {len(events)} active events")
        for event in events:
            print(f"   - {event['title']} (ID: {event['id']})")
        return len(events) == 1  # Should only have one active event
    else:
        print(f"❌ Failed to get active events: {response.status_code}")
        return False

def test_attendance_history():
    """Test getting attendance history for Discord user"""
    print(f"\n🔄 Testing attendance history for Discord user...")
    
    response = requests.get(f"{BASE_URL}/discord/attendance/{DISCORD_USER['discord_user_id']}")
    
    if response.status_code == 200:
        data = response.json()
        attended_events = data["attended_events"]
        total_attended = data["total_attended"]
        
        print(f"✅ Attendance history retrieved")
        print(f"   Total attended: {total_attended}")
        for event in attended_events:
            print(f"   - {event['title']} (ID: {event['id']})")
        
        return total_attended == 1  # Should have attended only the active event
    else:
        print(f"❌ Failed to get attendance history: {response.status_code}")
        return False

def run_discord_integration_test():
    """Run the complete Discord integration test"""
    print("🚀 Starting Discord Event Attendance Integration Test")
    print("=" * 60)
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            return False
        
        # Step 1: Register Discord user
        discord_user = register_discord_user()
        
        # Step 2: Create timed events
        events = create_timed_events()
        
        # Step 3: Test event statuses
        print("\n" + "="*40)
        print("TESTING EVENT STATUSES")
        print("="*40)
        
        if not test_event_status(events["past"], "ended"):
            print("❌ Past event status test failed")
            return False
            
        if not test_event_status(events["future"], "upcoming"):
            print("❌ Future event status test failed")
            return False
            
        if not test_event_status(events["active"], "active"):
            print("❌ Active event status test failed")
            return False
        
        # Step 4: Test attendance restrictions
        print("\n" + "="*40)
        print("TESTING ATTENDANCE RESTRICTIONS")
        print("="*40)
        
        # Should fail for past event
        if not test_discord_attendance(events["past"], False):
            print("❌ Past event attendance test failed")
            return False
        
        # Should fail for future event
        if not test_discord_attendance(events["future"], False):
            print("❌ Future event attendance test failed")
            return False
        
        # Should succeed for active event
        if not test_discord_attendance(events["active"], True):
            print("❌ Active event attendance test failed")
            return False
        
        # Step 5: Test active events endpoint
        if not test_get_active_events():
            print("❌ Get active events test failed")
            return False
        
        # Step 6: Test attendance history
        if not test_attendance_history():
            print("❌ Attendance history test failed")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 DISCORD INTEGRATION TEST PASSED!")
        print("✅ All Discord functionality working correctly:")
        print("   - Discord user registration ✅")
        print("   - Time-based attendance validation ✅")
        print("   - Event status checking ✅")
        print("   - Active events filtering ✅")
        print("   - Attendance history tracking ✅")
        print("   - Proper access control (only during events) ✅")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ DISCORD INTEGRATION TEST FAILED!")
        print(f"Error: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = run_discord_integration_test()
    exit(0 if success else 1) 