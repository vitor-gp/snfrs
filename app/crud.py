from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_password_hash


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_discord_id(
    db: Session, discord_user_id: str
) -> Optional[models.User]:
    return db.query(models.User).filter(
        models.User.discord_user_id == discord_user_id
    ).first()


def get_users(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.User]:
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


def create_discord_user(
    db: Session, user: schemas.UserCreateDiscord
) -> models.User:
    # For Discord users, create a temporary password
    temp_password = (
        f"discord_{user.discord_user_id}_{datetime.now().timestamp()}"
    )
    hashed_password = get_password_hash(temp_password)

    db_user = models.User(
        email=user.email,  # Can be None for Discord users
        name=user.name,
        discord_user_id=user.discord_user_id,
        discord_username=user.discord_username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def upsert_discord_user(
    db: Session, user: schemas.UserCreateDiscord
) -> Tuple[models.User, bool, List[str]]:
    """Create or update a Discord user, returning (user, is_new, changes)"""
    # Try to find existing user by Discord ID
    existing_user = get_user_by_discord_id(db, user.discord_user_id)

    if existing_user:
        # Update existing user
        changes = []

        if existing_user.name != user.name:
            existing_user.name = user.name
            changes.append("name")

        if existing_user.discord_username != user.discord_username:
            existing_user.discord_username = user.discord_username
            changes.append("discord_username")

        if user.email and existing_user.email != user.email:
            existing_user.email = user.email
            changes.append("email")

        if changes:
            db.commit()
            db.refresh(existing_user)

        return existing_user, False, changes
    else:
        # Create new user
        new_user = create_discord_user(db, user)
        return new_user, True, []


def update_user(
    db: Session, user_id: int, user_update: schemas.UserUpdate
) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, field, value)

    db_user.updated_at = datetime.now()
    db.commit()
    db.refresh(db_user)
    return db_user


# Event CRUD operations
def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_events(
    db: Session, skip: int = 0, limit: int = 100, active_only: bool = True
) -> List[models.Event]:
    query = db.query(models.Event)
    if active_only:
        query = query.filter(models.Event.is_active.is_(True))
    return query.offset(skip).limit(limit).all()


def get_active_events(db: Session) -> List[models.Event]:
    """Get all currently active events"""
    now = datetime.now()
    return (
        db.query(models.Event)
        .filter(models.Event.is_active.is_(True))
        .filter(models.Event.start_time <= now)
        .filter(models.Event.end_time >= now)
        .all()
    )


def get_single_ongoing_event(
    db: Session
) -> Tuple[Optional[models.Event], Optional[str]]:
    """Get the single ongoing event, or return error message"""
    ongoing_events = get_active_events(db)

    if len(ongoing_events) == 0:
        return None, "Nenhum evento rolando agora, parça! Cola mais tarde."
    elif len(ongoing_events) > 1:
        return None, "Opa, tem mais de um evento rolando! Usa `/events` para ver todos."
    else:
        return ongoing_events[0], None


def get_upcoming_events(db: Session, limit: int = 10) -> List[models.Event]:
    """Get upcoming events (starting in the future)"""
    now = datetime.now()
    return (
        db.query(models.Event)
        .filter(models.Event.is_active.is_(True))
        .filter(models.Event.start_time > now)
        .order_by(models.Event.start_time)
        .limit(limit)
        .all()
    )


def get_events_by_discord_channel(
    db: Session, channel_id: str
) -> List[models.Event]:
    """Get events filtered by Discord channel (if implemented)"""
    return (
        db.query(models.Event)
        .filter(models.Event.is_active.is_(True))
        .all()
    )


def create_event(db: Session, event: schemas.EventCreate) -> models.Event:
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def update_event(
    db: Session, event_id: int, event_update: schemas.EventUpdate
) -> Optional[models.Event]:
    db_event = get_event(db, event_id)
    if not db_event:
        return None

    for field, value in event_update.dict(exclude_unset=True).items():
        setattr(db_event, field, value)

    db_event.updated_at = datetime.now()
    db.commit()
    db.refresh(db_event)
    return db_event


def get_event_status(
    db: Session, event_id: int
) -> Optional[schemas.EventStatus]:
    """Get event status for attendance validation"""
    db_event = get_event(db, event_id)
    if not db_event or not db_event.is_active:
        return None

    now = datetime.now()

    if now < db_event.start_time:
        status = "Event has not started yet"
        can_attend = False
    elif now > db_event.end_time:
        status = "Event has ended"
        can_attend = False
    else:
        status = "Event is currently active"
        can_attend = True

    return schemas.EventStatus(
        event_id=db_event.id,
        title=db_event.title,
        status=status,
        can_attend=can_attend,
        start_time=db_event.start_time,
        end_time=db_event.end_time,
        current_time=now
    )


# Attendance CRUD operations
def can_attend_event(
    db: Session, event_id: int
) -> Tuple[bool, Optional[str]]:
    """Check if an event can be attended right now"""
    event_status = get_event_status(db, event_id)
    if not event_status:
        return False, "Event not found or inactive"

    if not event_status.can_attend:
        return False, event_status.status

    return True, None


def mark_attendance(
    db: Session, user_id: int, event_id: int
) -> Tuple[Optional[models.Event], Optional[str]]:
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


def mark_attendance_discord(
    db: Session, discord_user_id: str, event_id: int
) -> Tuple[Optional[models.Event], Optional[str], Optional[models.User]]:
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


def get_user_attended_events(
    db: Session, user_id: int
) -> List[models.Event]:
    db_user = get_user(db, user_id)
    if not db_user:
        return []
    return db_user.attended_events


def get_event_attendees(db: Session, event_id: int) -> List[models.User]:
    db_event = get_event(db, event_id)
    if not db_event:
        return []
    return db_event.attendees


def check_user_attendance(
    db: Session, user_id: int, event_id: int
) -> bool:
    db_user = get_user(db, user_id)
    db_event = get_event(db, event_id)

    if not db_user or not db_event:
        return False

    return db_event in db_user.attended_events


def check_discord_user_attendance(
    db: Session, discord_user_id: str, event_id: int
) -> bool:
    db_user = get_user_by_discord_id(db, discord_user_id)
    db_event = get_event(db, event_id)

    if not db_user or not db_event:
        return False

    return db_event in db_user.attended_events


# Admin CRUD operations
def make_user_admin(
    db: Session, discord_user_id: str, password: str
) -> Tuple[Optional[models.User], bool, str]:
    """Make a Discord user admin if password is correct"""
    # Check password
    if password != "123":
        return None, False, "Invalid password"

    # Get user by Discord ID
    db_user = get_user_by_discord_id(db, discord_user_id)
    if not db_user:
        return None, False, "User not found. Please register first using /register"

    # Check if already admin
    if db_user.is_admin:
        return db_user, False, f"{db_user.name} is already an admin"

    # Make user admin
    db_user.is_admin = True
    db.commit()
    db.refresh(db_user)

    return db_user, True, f"🎉 {db_user.name} is now an admin!"


# Name management CRUD operations
def get_user_by_name(db: Session, name: str) -> Optional[models.User]:
    """Get user by their name (case-insensitive)"""
    return db.query(models.User).filter(models.User.name.ilike(name)).first()


def check_name_available(
    db: Session, name: str, exclude_user_id: Optional[int] = None
) -> bool:
    """Check if name is available (case-insensitive)"""
    query = db.query(models.User).filter(models.User.name.ilike(name))
    if exclude_user_id:
        query = query.filter(models.User.id != exclude_user_id)
    return query.first() is None


def set_user_name(
    db: Session, discord_user_id: str, name: str
) -> Tuple[Optional[models.User], str]:
    """Set or update a user's name"""
    user = get_user_by_discord_id(db, discord_user_id)
    if not user:
        return None, "User not found. Please register first."

    # Check if name is available
    if not check_name_available(db, name, user.id):
        return None, f"Name '{name}' is already taken. Please choose another one."

    # Update name
    user.name = name.lower()
    user.updated_at = datetime.now()

    db.commit()
    db.refresh(user)

    return user, f"✅ Name set to '{name}' successfully!"


def get_all_users_list(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.User]:
    """Get list of all registered users for admin purposes"""
    return (
        db.query(models.User)
        .filter(models.User.is_active.is_(True))
        .offset(skip)
        .limit(limit)
        .all()
    )


def mark_attendance_for_user(
    db: Session,
    admin_discord_id: str,
    target_name: str,
    event_id: Optional[int] = None
) -> Tuple[bool, str, Optional[models.User], Optional[models.User],
           Optional[models.Event]]:
    """Admin marks attendance for another user by name"""
    # Check if admin user exists and is admin
    admin_user = get_user_by_discord_id(db, admin_discord_id)
    if not admin_user:
        return False, "Admin user not found. Please register first.", None, None, None

    if not admin_user.is_admin:
        return False, "Only admins can mark attendance for other users.", None, None, None

    # Find target user by name
    target_user = get_user_by_name(db, target_name)
    if not target_user:
        return False, f"User with name '{target_name}' not found.", admin_user, None, None

    # Prevent admin from marking attendance for themselves using this function
    if admin_user.id == target_user.id:
        return (
            False,
            "Use the regular /bater-ponto command to mark your own attendance.",
            admin_user,
            target_user,
            None
        )

    # If no event_id specified, get the single ongoing event
    if event_id is None:
        ongoing_event, error_msg = get_single_ongoing_event(db)
        if error_msg or not ongoing_event:
            return (
                False,
                error_msg or "No ongoing event found.",
                admin_user,
                target_user,
                None
            )
        event_id = ongoing_event.id

    # Get the event
    event = get_event(db, event_id)
    if not event:
        return (
            False,
            f"Event with ID {event_id} not found.",
            admin_user,
            target_user,
            None
        )

    # Check if event can be attended (time validation)
    can_attend, error_msg = can_attend_event(db, event_id)
    if not can_attend:
        return (
            False,
            error_msg or "Event cannot be attended at this time.",
            admin_user,
            target_user,
            event
        )

    # Check if user already attended
    if check_user_attendance(db, target_user.id, event_id):
        return (
            False,
            f"{target_user.name} (@{target_user.discord_username}) already attended this event.",
            admin_user,
            target_user,
            event
        )

    # Mark attendance
    event.attendees.append(target_user)
    db.commit()
    db.refresh(event)

    success_msg = (
        f"✅ {admin_user.name} marked attendance for {target_user.name} "
        f"(@{target_user.discord_username}) in event '{event.title}'"
    )

    return True, success_msg, admin_user, target_user, event 