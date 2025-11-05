from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# Association table for many-to-many relationship between users and events
user_event_attendance = Table(
    'user_event_attendance',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('attended_at', DateTime(timezone=True), server_default=func.now())
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, unique=True, index=True, nullable=False)  # Name serves as username
    hashed_password = Column(String, nullable=False)
    discord_user_id = Column(String, unique=True, index=True, nullable=True)  # Discord user ID
    discord_username = Column(String, nullable=True)  # Discord username
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to attended events
    attended_events = relationship(
        "Event",
        secondary=user_event_attendance,
        back_populates="attendees"
    )

    created_events = relationship(
        "Event",
        back_populates="creator"
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime(timezone=True), nullable=False)  # Event start time
    end_time = Column(DateTime(timezone=True), nullable=False)    # Event end time
    discord_channel_id = Column(String, nullable=True)  # Discord channel where event happens
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Creator of the event
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship to attendees
    attendees = relationship(
        "User",
        secondary=user_event_attendance,
        back_populates="attended_events"
    ) 

    creator = relationship(
        "User", 
        back_populates="created_events"
    )
