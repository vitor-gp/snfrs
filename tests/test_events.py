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
def auth_headers():
    # Register and login user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpassword123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        auth=("test@example.com", "testpassword123")
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_event(auth_headers):
    event_date = datetime.now() + timedelta(days=7)
    response = client.post(
        "/events/",
        json={
            "title": "Thursday Meetup",
            "description": "Weekly Thursday meetup",
            "event_date": event_date.isoformat()
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Thursday Meetup"
    assert data["description"] == "Weekly Thursday meetup"
    assert data["is_active"] is True


def test_get_events(auth_headers):
    # Create an event first
    event_date = datetime.now() + timedelta(days=7)
    client.post(
        "/events/",
        json={
            "title": "Thursday Meetup",
            "description": "Weekly Thursday meetup",
            "event_date": event_date.isoformat()
        },
        headers=auth_headers
    )
    
    response = client.get("/events/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Thursday Meetup"


def test_mark_attendance(auth_headers):
    # Create an event first
    event_date = datetime.now() + timedelta(days=7)
    event_response = client.post(
        "/events/",
        json={
            "title": "Thursday Meetup",
            "description": "Weekly Thursday meetup",
            "event_date": event_date.isoformat()
        },
        headers=auth_headers
    )
    event_id = event_response.json()["id"]
    
    # Mark attendance
    response = client.post(
        f"/events/{event_id}/attend",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Attendance marked successfully"
    assert data["event"]["id"] == event_id


def test_check_attendance(auth_headers):
    # Create an event first
    event_date = datetime.now() + timedelta(days=7)
    event_response = client.post(
        "/events/",
        json={
            "title": "Thursday Meetup",
            "description": "Weekly Thursday meetup",
            "event_date": event_date.isoformat()
        },
        headers=auth_headers
    )
    event_id = event_response.json()["id"]
    
    # Check attendance before marking
    response = client.get(
        f"/events/{event_id}/check-attendance",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["attended"] is False
    
    # Mark attendance
    client.post(f"/events/{event_id}/attend", headers=auth_headers)
    
    # Check attendance after marking
    response = client.get(
        f"/events/{event_id}/check-attendance",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["attended"] is True


def test_get_upcoming_events(auth_headers):
    # Create past and future events
    past_date = datetime.now() - timedelta(days=7)
    future_date = datetime.now() + timedelta(days=7)
    
    client.post(
        "/events/",
        json={
            "title": "Past Event",
            "description": "Past event",
            "event_date": past_date.isoformat()
        },
        headers=auth_headers
    )
    
    client.post(
        "/events/",
        json={
            "title": "Future Event",
            "description": "Future event",
            "event_date": future_date.isoformat()
        },
        headers=auth_headers
    )
    
    response = client.get("/events/upcoming", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Future Event"


def test_unauthorized_access():
    response = client.get("/events/")
    assert response.status_code == 401 