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


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
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


def get_upcoming_events(db: Session, limit: int = 10) -> List[models.Event]:
    return (
        db.query(models.Event)
        .filter(models.Event.is_active == True)
        .filter(models.Event.event_date >= datetime.now())
        .order_by(models.Event.event_date)
        .limit(limit)
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


# Attendance CRUD operations
def mark_attendance(db: Session, user_id: int, event_id: int) -> Optional[models.Event]:
    db_user = get_user(db, user_id)
    db_event = get_event(db, event_id)
    
    if not db_user or not db_event:
        return None
    
    # Check if already attended
    if db_event in db_user.attended_events:
        return db_event
    
    db_user.attended_events.append(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


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