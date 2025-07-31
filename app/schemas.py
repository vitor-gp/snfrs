from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, validator


# User schemas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: str


class UserCreate(UserBase):
    password: str


class UserCreateDiscord(BaseModel):
    """Schema for Discord user registration"""
    name: str
    discord_user_id: str
    discord_username: str
    email: Optional[EmailStr] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool = False
    discord_user_id: Optional[str] = None
    discord_username: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    discord_channel_id: Optional[str] = None


class EventCreate(EventBase):
    start_time: datetime
    end_time: datetime

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    discord_channel_id: Optional[str] = None
    is_active: Optional[bool] = None

    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class Event(EventBase):
    id: int
    start_time: datetime
    end_time: datetime
    is_active: bool
    created_at: datetime
    user_id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EventStatus(BaseModel):
    """Status information for an event"""
    event_id: int
    title: str
    status: str  # "upcoming", "active", "ended"
    can_attend: bool
    start_time: datetime
    end_time: datetime
    current_time: datetime


# Attendance schemas
class AttendanceRequest(BaseModel):
    event_id: int


class AttendanceCreateDiscord(BaseModel):
    """Request to mark Discord user attendance"""
    discord_user_id: str
    event_id: int


class AttendanceResponse(BaseModel):
    success: bool
    message: str
    event: Optional[Event] = None
    user: Optional[User] = None


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    discord_user_id: Optional[str] = None


# Discord-specific schemas
class DiscordRegistrationResponse(BaseModel):
    """Response for Discord user registration"""
    user: User
    is_new_user: bool
    message: str
    changes: Optional[List[str]] = None


class DiscordEventNotification(BaseModel):
    """Schema for Discord event notifications"""
    event: Event
    notification_type: str  # "starting_soon", "ending_soon", "new_event"
    message: str


# Admin schemas
class MakeAdminRequest(BaseModel):
    """Request to make a Discord user admin"""
    discord_user_id: str
    password: str


class AdminResponse(BaseModel):
    """Response for admin operations"""
    message: str
    user: User
    success: bool


# Username management schemas
class UsernameSetRequest(BaseModel):
    """Request to set or update username"""
    name: str

    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')

        # Clean the name
        v = v.strip()

        # Length validation
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters long')
        if len(v) > 30:
            raise ValueError('Name must be at most 30 characters long')

        # Character validation (letters, numbers, underscore, hyphen)
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Name can only contain letters, numbers, underscore (_) and hyphen (-)')

        # Reserved names check
        reserved_names = ['admin', 'root', 'system', 'bot', 'discord', 'everyone', 'here']
        if v.lower() in reserved_names:
            raise ValueError(f"Name '{v}' is reserved. Please choose another one.")

        return v.lower()  # Store in lowercase for consistency


class UsernameSetResponse(BaseModel):
    """Response for username setting"""
    success: bool
    message: str
    user: Optional[User] = None


class UserListItem(BaseModel):
    """Item in user list response"""
    id: int
    name: str
    discord_username: Optional[str] = None
    discord_user_id: Optional[str] = None
    is_admin: bool


class UserListResponse(BaseModel):
    """Response for user list"""
    users: List[UserListItem]
    total: int


# Admin attendance schemas
class AdminAttendanceRequest(BaseModel):
    """Request for admin to mark attendance for another user"""
    target_name: str
    event_id: Optional[int] = None


class AdminAttendanceResponse(BaseModel):
    """Response for admin attendance operations"""
    success: bool
    message: str
    admin_user: Optional[User] = None
    target_user: Optional[User] = None
    event: Optional[Event] = None 