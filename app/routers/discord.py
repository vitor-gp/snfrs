from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/discord", tags=["discord"])


@router.post("/users/register", response_model=schemas.DiscordRegistrationResponse)
def register_discord_user(
    user: schemas.UserCreateDiscord,
    db: Session = Depends(get_db)
):
    """Register or update a Discord user"""
    db_user, is_new, changes = crud.upsert_discord_user(db=db, user=user)  # type: ignore
    
    if is_new:
        message = f"🎉 Welcome {user.name}! Your Discord account has been successfully registered."
    elif changes:
        changes_str = ", ".join(changes)
        message = f"✅ Profile updated for {user.name}! Changes: {changes_str}"
    else:
        message = f"👋 Welcome back {user.name}! Your profile is already up to date."
    
    return schemas.DiscordRegistrationResponse(
        user=db_user,
        is_new_user=is_new,
        message=message,
        changes=changes if changes else None
    )


@router.post("/events/create", response_model=schemas.Event)
def create_event_discord(
    event: schemas.EventCreate,
    discord_user_id: str,
    db: Session = Depends(get_db)
):
    """Create an event via Discord (requires admin status in database)"""
    # Check if user exists and is admin
    user = crud.get_user_by_discord_id(db, discord_user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Discord user not registered. Please register first with /register."
        )
    
    if not getattr(user, 'is_admin', False):
        raise HTTPException(
            status_code=403,
            detail="Only admins can create events. Use /make_admin command to become admin."
        )
    
    # Create the event
    db_event = crud.create_event(db=db, event=event)
    return db_event


@router.get("/users/{discord_user_id}", response_model=schemas.User)
def get_discord_user(
    discord_user_id: str,
    db: Session = Depends(get_db)
):
    """Get Discord user information"""
    user = crud.get_user_by_discord_id(db, discord_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Discord user not found")
    return user


@router.get("/events/active", response_model=List[schemas.Event])
def get_active_events_for_discord(db: Session = Depends(get_db)):
    """Get all currently active events that can be attended"""
    return crud.get_active_events(db)


@router.get("/events/channel/{channel_id}", response_model=List[schemas.Event])
def get_channel_events(
    channel_id: str,
    db: Session = Depends(get_db)
):
    """Get events for a specific Discord channel"""
    return crud.get_events_by_discord_channel(db, channel_id)


@router.post("/attend/{event_id}")
def attend_event_discord(
    event_id: int,
    discord_user_id: str,
    db: Session = Depends(get_db)
):
    """Attend an event via Discord"""
    # First ensure user exists
    user = crud.get_user_by_discord_id(db, discord_user_id)
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="Discord user not registered. Please register first."
        )
    
    # Check event status
    event_status = crud.get_event_status(db, event_id)
    if not event_status:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if not event_status.can_attend:
        return {
            "success": False,
            "message": f"Cannot attend: {event_status.status}",
            "event_status": event_status.dict()
        }
    
    # Mark attendance
    db_event, error_msg, db_user = crud.mark_attendance_discord(db, discord_user_id, event_id)
    
    if error_msg:
        return {
            "success": False,
            "message": error_msg,
            "event_status": event_status.dict()
        }
    
    if error_msg == "Already marked as attended":
        return {
            "success": True,
            "message": "You have already been marked as attended for this event",
            "event": {
                "id": db_event.id,
                "title": db_event.title
            }
        }
    
    return {
        "success": True,
        "message": f"Successfully attended '{db_event.title}'!",
        "event": {
            "id": db_event.id,
            "title": db_event.title,
            "end_time": db_event.end_time.isoformat()
        },
        "user": {
            "name": db_user.name,
            "discord_username": db_user.discord_username
        }
    }


@router.get("/attendance/{discord_user_id}")
def get_user_attendance(
    discord_user_id: str,
    db: Session = Depends(get_db)
):
    """Get attendance history for a Discord user"""
    user = crud.get_user_by_discord_id(db, discord_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Discord user not found")
    
    attended_events = crud.get_user_attended_events(db, user.id)
    
    return {
        "user": {
            "discord_user_id": user.discord_user_id,
            "discord_username": user.discord_username,
            "name": user.name
        },
        "attended_events": [
            {
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat()
            }
            for event in attended_events
        ],
        "total_attended": len(attended_events)
    }


@router.get("/event/{event_id}/status", response_model=schemas.EventStatus)
def get_event_status_discord(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get event status for Discord bot"""
    event_status = crud.get_event_status(db, event_id)
    if not event_status:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_status


@router.get("/event/{event_id}/attendees")
def get_event_attendees_discord(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get event attendees for Discord display"""
    attendees = crud.get_event_attendees(db, event_id)
    event = crud.get_event(db, event_id)
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return {
        "event": {
            "id": event.id,
            "title": event.title,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat()
        },
        "attendees": [
            {
                "name": attendee.name,
                "discord_username": attendee.discord_username,
                "discord_user_id": attendee.discord_user_id
            }
            for attendee in attendees
            if attendee.discord_user_id  # Only show Discord users
        ],
        "total_attendees": len([a for a in attendees if a.discord_user_id])
    }


@router.post("/admin/make-admin", response_model=schemas.AdminResponse)
def make_admin_discord(
    request: schemas.MakeAdminRequest,
    db: Session = Depends(get_db)
):
    """Make a Discord user admin with password verification"""
    user, success, message = crud.make_user_admin(
        db=db, 
        discord_user_id=request.discord_user_id, 
        password=request.password
    )
    
    if not user:
        raise HTTPException(
            status_code=400, 
            detail=message
        )
    
    return schemas.AdminResponse(
        message=message,
        user=user,
        success=success
    ) 