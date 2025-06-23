from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime

# 用户 CRUD
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, house_area=user.house_area)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_or_update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        # 更新现有用户
        db_user.name = user.name
        db_user.house_area = user.house_area
    else:
        # 创建新用户
        db_user = models.User(id=user_id, name=user.name, house_area=user.house_area)
        db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"ok": True}
    return {"ok": False, "error": "User not found"}

# 房间 CRUD
def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def get_rooms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Room).offset(skip).limit(limit).all()

def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()

def delete_room(db: Session, room_id: int):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room:
        db.delete(db_room)
        db.commit()
        return {"ok": True}
    return {"ok": False, "error": "Room not found"}

# 设备 CRUD
def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(name=device.name, type=device.type, room_id=device.room_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Device).offset(skip).limit(limit).all()

def get_device(db: Session, device_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id).first()

def delete_device(db: Session, device_id: int):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device:
        db.delete(db_device)
        db.commit()
        return {"ok": True}
    return {"ok": False, "error": "Device not found"}

# 设备使用记录 CRUD
def create_device_usage(db: Session, usage: schemas.DeviceUsageCreate):
    db_usage = models.DeviceUsage(**usage.model_dump())
    db.add(db_usage)
    db.commit()
    db.refresh(db_usage)
    return db_usage

def get_device_usages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DeviceUsage).offset(skip).limit(limit).all()

def get_device_usage(db: Session, usage_id: int):
    return db.query(models.DeviceUsage).filter(models.DeviceUsage.id == usage_id).first()

def delete_device_usage(db: Session, usage_id: int):
    db_usage = db.query(models.DeviceUsage).filter(models.DeviceUsage.id == usage_id).first()
    if db_usage:
        db.delete(db_usage)
        db.commit()
        return {"ok": True}
    return {"ok": False, "error": "DeviceUsage not found"}

# 安防事件 CRUD
def create_security_event(db: Session, event: schemas.SecurityEventCreate):
    db_event = models.SecurityEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_security_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.SecurityEvent).offset(skip).limit(limit).all()

def get_security_event(db: Session, event_id: int):
    return db.query(models.SecurityEvent).filter(models.SecurityEvent.id == event_id).first()

def delete_security_event(db: Session, event_id: int):
    db_event = db.query(models.SecurityEvent).filter(models.SecurityEvent.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
        return {"ok": True}
    return {"ok": False, "error": "SecurityEvent not found"}

# 用户反馈 CRUD
def create_feedback(db: Session, feedback: schemas.FeedbackCreate):
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_feedbacks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Feedback).offset(skip).limit(limit).all()

def get_feedback(db: Session, feedback_id: int):
    return db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()

def delete_feedback(db: Session, feedback_id: int):
    db_feedback = db.query(models.Feedback).filter(models.Feedback.id == feedback_id).first()
    if db_feedback:
        db.delete(db_feedback)
        db.commit()
        return {"ok": True}
    return {"ok": False, "error": "Feedback not found"} 