from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from database import Base
import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    house_area = Column(Float, nullable=True)
    # 关系
    usages = relationship('DeviceUsage', back_populates='user')
    events = relationship('SecurityEvent', back_populates='user')
    feedbacks = relationship('Feedback', back_populates='user')


class Room(Base):
    __tablename__ = 'rooms'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    devices = relationship('Device', back_populates='room')


class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(30), nullable=True)
    room_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    room = relationship('Room', back_populates='devices')
    usages = relationship('DeviceUsage', back_populates='device')
    events = relationship('SecurityEvent', back_populates='device')
    feedbacks = relationship('Feedback', back_populates='device')


class DeviceUsage(Base):
    __tablename__ = 'device_usages'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    device_id = Column(Integer, ForeignKey('devices.id'))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    usage_type = Column(String(30), nullable=True)
    energy_consumed = Column(Float, nullable=True)
    device_type = Column(String(30), nullable=True)
    user_name = Column(String(50), nullable=True)
    user = relationship('User', back_populates='usages')
    device = relationship('Device', back_populates='usages')


class SecurityEvent(Base):
    __tablename__ = 'security_events'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    device_id = Column(Integer, ForeignKey('devices.id'))
    event_type = Column(String(30), nullable=False)
    event_level = Column(String(10), nullable=True)
    location = Column(String(50), nullable=True)
    status = Column(String(20), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User', back_populates='events')
    device = relationship('Device', back_populates='events')


class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    feedback_type = Column(String(20), nullable=True)
    status = Column(String(20), nullable=True)
    device_id = Column(Integer, ForeignKey('devices.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User', back_populates='feedbacks')
    device = relationship('Device', back_populates='feedbacks')
