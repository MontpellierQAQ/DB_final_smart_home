from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 用户
class UserBase(BaseModel):
    name: str
    house_area: Optional[float] = None

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    class Config:
        from_attributes = True

# 房间
class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    pass

class RoomOut(RoomBase):
    id: int
    class Config:
        from_attributes = True

# 设备
class DeviceBase(BaseModel):
    name: str
    type: Optional[str] = None
    room_id: Optional[int] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceOut(DeviceBase):
    id: int
    class Config:
        from_attributes = True

# 设备使用记录
class DeviceUsageBase(BaseModel):
    user_id: int
    device_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    usage_type: Optional[str] = None
    energy_consumed: Optional[float] = None
    device_type: Optional[str] = None
    user_name: Optional[str] = None

class DeviceUsageCreate(DeviceUsageBase):
    pass

class DeviceUsage(DeviceUsageBase):
    id: int
    user: "User"
    device: "Device"

    class Config:
        from_attributes = True

# 安防事件
class SecurityEventBase(BaseModel):
    user_id: int
    device_id: int
    event_type: str
    event_level: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    timestamp: Optional[datetime] = None

class SecurityEventCreate(SecurityEventBase):
    pass

class SecurityEvent(SecurityEventBase):
    id: int
    user: "User"
    device: "Device"

    class Config:
        from_attributes = True

# 用户反馈
class FeedbackBase(BaseModel):
    user_id: int
    content: str
    feedback_type: Optional[str] = None
    status: Optional[str] = None
    device_id: Optional[int] = None
    timestamp: Optional[datetime] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    user: "User"
    device: Optional["Device"] = None

    class Config:
        from_attributes = True 