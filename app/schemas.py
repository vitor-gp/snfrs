from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, validator


# User schemas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: str
    discord_user_id: Optional[str] = None
    discord_username: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserCreateDiscord(BaseModel):
    name: str
    discord_user_id: str
    discord_username: str
    email: Optional[EmailStr] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    discord_user_id: Optional[str] = None
    discord_username: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    discord_channel_id: Optional[str] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    discord_channel_id: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v and values['start_time'] and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


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


class EventStatus(BaseModel):
    id: int
    title: str
    status: str  # "upcoming", "active", "ended"
    start_time: datetime
    end_time: datetime
    can_attend: bool
    time_until_start: Optional[int] = None  # seconds
    time_until_end: Optional[int] = None    # seconds


# Attendance schemas
class AttendanceCreate(BaseModel):
    event_id: int


class AttendanceCreateDiscord(BaseModel):
    event_id: int
    discord_user_id: str


class AttendanceResponse(BaseModel):
    message: str
    event: Event
    user: User
    attended_at: datetime


class AttendanceError(BaseModel):
    error: str
    event_status: EventStatus


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    discord_user_id: Optional[str] = None


# Discord-specific schemas
class DiscordRegistrationResponse(BaseModel):
    user: User
    is_new_user: bool
    message: str
    changes: Optional[List[str]] = None

class DiscordEventNotification(BaseModel):
    event_id: int
    title: str
    channel_id: Optional[str]
    message: str
    action: str  # "starting", "ending", "reminder"


# Admin schemas
class MakeAdminRequest(BaseModel):
    discord_user_id: str
    password: str


class AdminResponse(BaseModel):
    message: str
    user: User
    success: bool 