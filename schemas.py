from __future__ import annotations
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ==============================================================================
# Base and Create Schemas (without relationships)
# ==============================================================================

# User


class UserBase(BaseModel):
    name: str
    house_area: Optional[float] = None


class UserCreate(UserBase):
    pass


# Room
class RoomBase(BaseModel):
    name: str


class RoomCreate(RoomBase):
    pass


# Device
class DeviceBase(BaseModel):
    name: str
    type: Optional[str] = None
    room_id: Optional[int] = None


class DeviceCreate(DeviceBase):
    pass


# DeviceUsage
class DeviceUsageBase(BaseModel):
    user_id: int
    device_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    usage_type: Optional[str] = None
    energy_consumed: Optional[float] = None


class DeviceUsageCreate(DeviceUsageBase):
    pass


# SecurityEvent
class SecurityEventBase(BaseModel):
    user_id: int
    device_id: int
    event_type: str
    timestamp: datetime


class SecurityEventCreate(SecurityEventBase):
    pass


# Feedback
class FeedbackBase(BaseModel):
    user_id: int
    content: str
    feedback_type: Optional[str] = None
    device_id: Optional[int] = None
    timestamp: datetime


class FeedbackCreate(FeedbackBase):
    pass


# ==============================================================================
# Full Output Schemas (with relationships and forward references)
# ==============================================================================

# Simple output models (without nested relationships)
class Room(RoomBase):
    id: int

    class Config:
        from_attributes = True


class Device(DeviceBase):
    id: int

    class Config:
        from_attributes = True

# Advanced output models (with nested relationships for detailed views)


class RoomOut(RoomBase):
    id: int
    devices: List["Device"] = []  # Use simple Device schema here

    class Config:
        from_attributes = True


class DeviceOut(DeviceBase):
    id: int
    room: Optional[Room] = None  # Use simple Room schema here

    class Config:
        from_attributes = True


class DeviceUsage(DeviceUsageBase):
    id: int
    device: Device

    class Config:
        from_attributes = True


class SecurityEvent(SecurityEventBase):
    id: int
    device: Device

    class Config:
        from_attributes = True


class Feedback(FeedbackBase):
    id: int
    device: Optional[Device] = None

    class Config:
        from_attributes = True


# This is the primary output model for a single user, including all their
# related data.
class UserOut(UserBase):
    id: int
    usages: List[DeviceUsage] = []
    events: List[SecurityEvent] = []
    feedbacks: List[Feedback] = []

    class Config:
        from_attributes = True


# Update any forward references to resolve them.
Room.model_rebuild()
Device.model_rebuild()
RoomOut.model_rebuild()
DeviceOut.model_rebuild()
DeviceUsage.model_rebuild()
SecurityEvent.model_rebuild()
Feedback.model_rebuild()
UserOut.model_rebuild()
