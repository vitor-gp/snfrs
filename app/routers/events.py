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
    return crud.create_event(db=db, event=event)


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


@router.get("/upcoming", response_model=List[schemas.Event])
def read_upcoming_events(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    events = crud.get_upcoming_events(db, limit=limit)
    return events


@router.get("/{event_id}", response_model=schemas.EventWithAttendees)
def read_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event


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
    db_event = crud.mark_attendance(db, current_user.id, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return schemas.AttendanceResponse(
        message="Attendance marked successfully",
        event=db_event,
        user=current_user
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