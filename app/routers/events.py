from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth import get_current_active_user
from app.database import get_db

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
def create_event(
    event: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.create_event(db=db, event=event, current_user=current_user)


@router.get("/", response_model=List[schemas.Event])
def read_events(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    events = crud.get_events(db, skip=skip, limit=limit, active_only=active_only)
    return events


@router.get("/active", response_model=List[schemas.Event])
def read_active_events(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get events that are currently happening (can be attended)"""
    events = crud.get_active_events(db)
    return events


@router.get("/upcoming", response_model=List[schemas.Event])
def read_upcoming_events(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    events = crud.get_upcoming_events(db, limit=limit)
    return events


@router.get("/discord-channel/{channel_id}", response_model=List[schemas.Event])
def read_events_by_discord_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get events for a specific Discord channel"""
    events = crud.get_events_by_discord_channel(db, channel_id)
    return events


@router.get("/{event_id}", response_model=schemas.Event)
def read_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


@router.get("/{event_id}/status", response_model=schemas.EventStatus)
def get_event_status(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get the current status of an event and whether it can be attended"""
    event_status = crud.get_event_status(db, event_id)
    if not event_status:
        raise HTTPException(status_code=404, detail="Event not found")
    return event_status


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(
    event_id: int,
    event_update: schemas.EventUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    updated_event = crud.update_event(db, event_id, event_update)
    if not updated_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated_event


@router.post("/{event_id}/attend", response_model=schemas.AttendanceResponse)
def mark_event_attendance(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Mark attendance for an event (only during event time)"""
    db_event, error_msg = crud.mark_attendance(db, current_user.id, event_id)
    
    if error_msg:
        event_status = crud.get_event_status(db, event_id)
        if event_status:
            raise HTTPException(
                status_code=400, 
                detail={
                    "error": error_msg,
                    "event_status": event_status.dict()
                }
            )
        else:
            raise HTTPException(status_code=404, detail=error_msg)
    
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return schemas.AttendanceResponse(
        message="Attendance marked successfully",
        event=db_event,
        user=current_user,
        attended_at=db_event.attendees[0].attended_at if db_event.attendees else None
    )


@router.post("/discord/attend", response_model=schemas.AttendanceResponse)
def mark_discord_attendance(
    attendance: schemas.AttendanceCreateDiscord,
    db: Session = Depends(get_db)
):
    """Mark attendance for a Discord user (no authentication required)"""
    db_event, error_msg, db_user = crud.mark_attendance_discord(
        db, attendance.discord_user_id, attendance.event_id
    )
    
    if error_msg:
        event_status = crud.get_event_status(db, attendance.event_id)
        if event_status:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": error_msg,
                    "event_status": event_status.dict()
                }
            )
        else:
            raise HTTPException(status_code=404, detail=error_msg)
    
    if not db_event or not db_user:
        raise HTTPException(status_code=404, detail="Event or user not found")
    
    return schemas.AttendanceResponse(
        message="Attendance marked successfully",
        event=db_event,
        user=db_user,
        attended_at=db_event.attendees[0].attended_at if db_event.attendees else None
    )


@router.get("/{event_id}/attendees", response_model=List[schemas.User])
def read_event_attendees(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    attendees = crud.get_event_attendees(db, event_id)
    return attendees


@router.get("/{event_id}/check-attendance")
def check_attendance(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    attended = crud.check_user_attendance(db, current_user.id, event_id)
    return {"attended": attended, "user_id": current_user.id, "event_id": event_id}


@router.get("/discord/{discord_user_id}/{event_id}/check-attendance")
def check_discord_attendance(
    discord_user_id: str,
    event_id: int,
    db: Session = Depends(get_db)
):
    """Check if a Discord user has attended an event"""
    attended = crud.check_discord_user_attendance(db, discord_user_id, event_id)
    return {
        "attended": attended, 
        "discord_user_id": discord_user_id, 
        "event_id": event_id
    } 