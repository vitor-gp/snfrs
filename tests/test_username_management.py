import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def registered_user():
    """Create and register a Discord user"""
    user_data = {
        "name": "Test User",
        "discord_user_id": "123456789",
        "discord_username": "testuser#1234"
    }
    response = client.post("/discord/users/register", json=user_data)
    assert response.status_code in [200, 201]
    return response.json()["user"]


@pytest.fixture
def admin_user():
    """Create and register an admin Discord user"""
    user_data = {
        "name": "Admin User",
        "discord_user_id": "987654321",
        "discord_username": "admin#1234"
    }
    response = client.post("/discord/users/register", json=user_data)
    assert response.status_code in [200, 201]
    
    # Make user admin
    admin_response = client.post(
        "/discord/admin/make-admin",
        json={"discord_user_id": "987654321", "password": "123"}
    )
    assert admin_response.status_code == 200
    return admin_response.json()["user"]


@pytest.fixture
def active_event():
    """Create an active event"""
    # First create a regular user to authenticate
    client.post("/auth/register", json={
        "email": "creator@test.com",
        "name": "Event Creator",
        "password": "password123"
    })
    login_response = client.post("/auth/login", auth=("creator@test.com", "password123"))
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create event that's currently active
    now = datetime.now()
    start_time = now - timedelta(minutes=30)
    end_time = now + timedelta(minutes=30)
    
    event_data = {
        "title": "Test Active Event",
        "description": "Test event for attendance",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    response = client.post("/events/", json=event_data, headers=headers)
    assert response.status_code == 201
    return response.json()


class TestUsernameManagement:
    """Test username management functionality"""
    
    def test_set_username_success(self, registered_user):
        """Test successfully setting a username"""
        response = client.post(
            "/discord/users/set-username",
            json={"username": "testuser123"},
            params={"discord_user_id": "123456789"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "successfully" in data["message"].lower()
        assert data["user"]["username"] == "testuser123"
    
    def test_set_username_invalid_format(self, registered_user):
        """Test setting username with invalid format"""
        response = client.post(
            "/discord/users/set-username",
            json={"username": "ab"},  # Too short
            params={"discord_user_id": "123456789"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_set_username_reserved(self, registered_user):
        """Test setting reserved username"""
        response = client.post(
            "/discord/users/set-username",
            json={"username": "admin"},
            params={"discord_user_id": "123456789"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_set_username_duplicate(self, registered_user):
        """Test setting duplicate username"""
        # First user sets username
        client.post(
            "/discord/users/set-username",
            json={"username": "taken"},
            params={"discord_user_id": "123456789"}
        )
        
        # Register second user
        user2_data = {
            "name": "User Two",
            "discord_user_id": "111111111",
            "discord_username": "user2#1234"
        }
        client.post("/discord/users/register", json=user2_data)
        
        # Second user tries same username
        response = client.post(
            "/discord/users/set-username",
            json={"username": "taken"},
            params={"discord_user_id": "111111111"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "already taken" in data["message"].lower()
    
    def test_set_username_unregistered_user(self):
        """Test setting username for unregistered user"""
        response = client.post(
            "/discord/users/set-username",
            json={"username": "newuser"},
            params={"discord_user_id": "999999999"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()


class TestUserListing:
    """Test user listing functionality"""
    
    def test_list_users_as_admin(self, admin_user, registered_user):
        """Test listing users as admin"""
        response = client.get(
            "/discord/users/list",
            params={"discord_user_id": "987654321"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert len(data["users"]) >= 2  # admin + regular user
    
    def test_list_users_as_non_admin(self, registered_user):
        """Test listing users as non-admin"""
        response = client.get(
            "/discord/users/list",
            params={"discord_user_id": "123456789"}
        )
        assert response.status_code == 403
        assert "Only admins" in response.json()["detail"]
    
    def test_list_users_unregistered(self):
        """Test listing users as unregistered user"""
        response = client.get(
            "/discord/users/list",
            params={"discord_user_id": "999999999"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAdminAttendance:
    """Test admin attendance marking functionality"""
    
    def test_admin_mark_attendance_success(self, admin_user, registered_user, active_event):
        """Test admin successfully marking attendance for another user"""
        # First set username for target user
        client.post(
            "/discord/users/set-username",
            json={"username": "targetuser"},
            params={"discord_user_id": "123456789"}
        )
        
        # Admin marks attendance for user
        response = client.post(
            "/discord/attend/for-user",
            json={"target_username": "targetuser"},
            params={"admin_discord_user_id": "987654321"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "marked attendance" in data["message"].lower()
        assert data["admin_user"]["id"] == admin_user["id"]
        assert data["target_user"]["username"] == "targetuser"
        assert data["event"]["id"] == active_event["id"]
    
    def test_admin_mark_attendance_non_admin(self, registered_user, active_event):
        """Test non-admin trying to mark attendance for another user"""
        response = client.post(
            "/discord/attend/for-user",
            json={"target_username": "someone"},
            params={"admin_discord_user_id": "123456789"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "only admins" in data["message"].lower()
    
    def test_admin_mark_attendance_user_not_found(self, admin_user, active_event):
        """Test admin marking attendance for non-existent user"""
        response = client.post(
            "/discord/attend/for-user",
            json={"target_username": "nonexistent"},
            params={"admin_discord_user_id": "987654321"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_admin_mark_attendance_for_self(self, admin_user, active_event):
        """Test admin trying to mark attendance for themselves"""
        # Set username for admin
        client.post(
            "/discord/users/set-username",
            json={"username": "adminuser"},
            params={"discord_user_id": "987654321"}
        )
        
        response = client.post(
            "/discord/attend/for-user",
            json={"target_username": "adminuser"},
            params={"admin_discord_user_id": "987654321"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "regular" in data["message"].lower()
    
    def test_admin_mark_attendance_no_active_event(self, admin_user, registered_user):
        """Test admin marking attendance when no event is active"""
        # Set username for target user
        client.post(
            "/discord/users/set-username",
            json={"username": "targetuser"},
            params={"discord_user_id": "123456789"}
        )
        
        response = client.post(
            "/discord/attend/for-user",
            json={"target_username": "targetuser"},
            params={"admin_discord_user_id": "987654321"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "evento" in data["message"].lower()


class TestUsernameRateLimit:
    """Test username change rate limiting"""
    
    def test_username_rate_limit(self, registered_user):
        """Test that users can't change username too frequently"""
        # Set initial username
        response1 = client.post(
            "/discord/users/set-username",
            json={"username": "first"},
            params={"discord_user_id": "123456789"}
        )
        assert response1.status_code == 200
        assert response1.json()["success"] is True
        
        # Try to change again immediately
        response2 = client.post(
            "/discord/users/set-username",
            json={"username": "second"},
            params={"discord_user_id": "123456789"}
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["success"] is False
        assert "30 days" in data["message"]


class TestCaseInsensitiveUsername:
    """Test case-insensitive username handling"""
    
    def test_username_case_insensitive_uniqueness(self, registered_user):
        """Test that usernames are case-insensitive unique"""
        # Set username in lowercase
        client.post(
            "/discord/users/set-username",
            json={"username": "testuser"},
            params={"discord_user_id": "123456789"}
        )
        
        # Register second user
        user2_data = {
            "name": "User Two",
            "discord_user_id": "222222222",
            "discord_username": "user2#1234"
        }
        client.post("/discord/users/register", json=user2_data)
        
        # Try to set same username with different case
        response = client.post(
            "/discord/users/set-username",
            json={"username": "TestUser"},  # Different case
            params={"discord_user_id": "222222222"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "already taken" in data["message"].lower()
    
    def test_find_user_by_username_case_insensitive(self, admin_user, registered_user, active_event):
        """Test finding users by username is case-insensitive"""
        # Set username in mixed case
        client.post(
            "/discord/users/set-username",
            json={"username": "MixedCase"},
            params={"discord_user_id": "123456789"}
        )
        
        # Admin marks attendance using lowercase
        response = client.post(
            "/discord/attend/for-user",
            json={"target_username": "mixedcase"},  # lowercase
            params={"admin_discord_user_id": "987654321"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True 