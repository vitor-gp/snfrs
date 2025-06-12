from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: datetime


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class Event(EventBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    attendees: List[User] = []

    class Config:
        from_attributes = True


class EventWithAttendees(Event):
    attendees: List[User] = []


# Attendance schemas
class AttendanceCreate(BaseModel):
    event_id: int


class AttendanceResponse(BaseModel):
    message: str
    event: Event
    user: User


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None 