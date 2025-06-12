from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_password_hash


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_discord_id(db: Session, discord_user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.discord_user_id == discord_user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        discord_user_id=user.discord_user_id,
        discord_username=user.discord_username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_discord_user(db: Session, user: schemas.UserCreateDiscord) -> models.User:
    # For Discord users, create a temporary password if no email provided
    temp_password = f"discord_{user.discord_user_id}_{datetime.now().timestamp()}"
    hashed_password = get_password_hash(temp_password)
    
    db_user = models.User(
        email=user.email or f"{user.discord_user_id}@discord.temp",
        name=user.name,
        discord_user_id=user.discord_user_id,
        discord_username=user.discord_username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


# Event CRUD operations
def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[models.Event]:
    query = db.query(models.Event)
    if active_only:
        query = query.filter(models.Event.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_active_events(db: Session) -> List[models.Event]:
    """Get events that are currently happening"""
    now = datetime.now()
    return (
        db.query(models.Event)
        .filter(models.Event.is_active == True)
        .filter(models.Event.start_time <= now)
        .filter(models.Event.end_time >= now)
        .all()
    )


def get_upcoming_events(db: Session, limit: int = 10) -> List[models.Event]:
    now = datetime.now()
    return (
        db.query(models.Event)
        .filter(models.Event.is_active == True)
        .filter(models.Event.start_time >= now)
        .order_by(models.Event.start_time)
        .limit(limit)
        .all()
    )


def get_events_by_discord_channel(db: Session, channel_id: str) -> List[models.Event]:
    return (
        db.query(models.Event)
        .filter(models.Event.discord_channel_id == channel_id)
        .filter(models.Event.is_active == True)
        .all()
    )


def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(db: Session, event_id: int, event_update: schemas.EventUpdate) -> Optional[models.Event]:
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event


def get_event_status(db: Session, event_id: int) -> Optional[schemas.EventStatus]:
    """Get the current status of an event"""
    event = get_event(db, event_id)
    if not event:
        return None
    
    now = datetime.now()
    
    if now < event.start_time:
        status = "upcoming"
        can_attend = False
        time_until_start = int((event.start_time - now).total_seconds())
        time_until_end = None
    elif now > event.end_time:
        status = "ended"
        can_attend = False
        time_until_start = None
        time_until_end = None
    else:
        status = "active"
        can_attend = True
        time_until_start = None
        time_until_end = int((event.end_time - now).total_seconds())
    
    return schemas.EventStatus(
        id=event.id,
        title=event.title,
        status=status,
        start_time=event.start_time,
        end_time=event.end_time,
        can_attend=can_attend,
        time_until_start=time_until_start,
        time_until_end=time_until_end
    )


# Attendance CRUD operations
def can_attend_event(db: Session, event_id: int) -> tuple[bool, Optional[str]]:
    """Check if an event can be attended right now"""
    event = get_event(db, event_id)
    if not event:
        return False, "Event not found"
    
    if not event.is_active:
        return False, "Event is not active"
    
    now = datetime.now()
    
    if now < event.start_time:
        time_until_start = int((event.start_time - now).total_seconds())
        return False, f"Event hasn't started yet. Starts in {time_until_start // 60} minutes"
    
    if now > event.end_time:
        return False, "Event has already ended"
    
    return True, None


def mark_attendance(db: Session, user_id: int, event_id: int) -> tuple[Optional[models.Event], Optional[str]]:
    """Mark attendance for an event with time validation"""
    # Check if event can be attended
    can_attend, error_msg = can_attend_event(db, event_id)
    if not can_attend:
        return None, error_msg
    
    db_user = get_user(db, user_id)
    db_event = get_event(db, event_id)
    
    if not db_user or not db_event:
        return None, "User or event not found"
    
    # Check if already attended
    if db_event in db_user.attended_events:
        return db_event, "Already marked as attended"
    
    db_user.attended_events.append(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event, None


def mark_attendance_discord(db: Session, discord_user_id: str, event_id: int) -> tuple[Optional[models.Event], Optional[str], Optional[models.User]]:
    """Mark attendance for a Discord user"""
    # Check if event can be attended
    can_attend, error_msg = can_attend_event(db, event_id)
    if not can_attend:
        return None, error_msg, None
    
    db_user = get_user_by_discord_id(db, discord_user_id)
    if not db_user:
        return None, "Discord user not registered", None
    
    db_event = get_event(db, event_id)
    if not db_event:
        return None, "Event not found", db_user
    
    # Check if already attended
    if db_event in db_user.attended_events:
        return db_event, "Already marked as attended", db_user
    
    db_user.attended_events.append(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event, None, db_user


def get_user_attended_events(db: Session, user_id: int) -> List[models.Event]:
    db_user = get_user(db, user_id)
    if not db_user:
        return []
    return db_user.attended_events


def get_event_attendees(db: Session, event_id: int) -> List[models.User]:
    db_event = get_event(db, event_id)
    if not db_event:
        return []
    return db_event.attendees


def check_user_attendance(db: Session, user_id: int, event_id: int) -> bool:
    db_user = get_user(db, user_id)
    db_event = get_event(db, event_id)
    
    if not db_user or not db_event:
        return False
    
    return db_event in db_user.attended_events


def check_discord_user_attendance(db: Session, discord_user_id: str, event_id: int) -> bool:
    db_user = get_user_by_discord_id(db, discord_user_id)
    db_event = get_event(db, event_id)
    
    if not db_user or not db_event:
        return False
    
    return db_event in db_user.attended_events 