from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy import Date, Time, Boolean, Float


    

class DarshanBooking(Base):
    __tablename__ = "darshan_bookings"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    contact_number = Column(String(15), nullable=False)
    whatsapp_number = Column(String(15), nullable=False)
    address = Column(Text, nullable=False)
    persons = Column(Integer, nullable=False)
    slot_date = Column(Date, nullable=False)
    slot_time = Column(String(100), nullable=False)
    occupied_units = Column(Integer , nullable=False, default=1)  # New field to track occupied units for the slot
    qr_code = Column(String(500), nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    payment_screenshot = Column(String(255), nullable=False)
    payment_status = Column(String(50), default="partial", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)

    age = Column(Integer, nullable=True)
    darshan_name = Column(String(100), nullable=True)
    payment_mode = Column(String(50), nullable=True)
    sessions = relationship("DarshanSession", back_populates="booking", cascade="all, delete-orphan")
    reviews = relationship("DarshanReview", back_populates="booking", cascade="all, delete-orphan")
    
    extensions = relationship("SessionExtension", back_populates="booking", cascade="all, delete-orphan")

class DarshanSession(Base):
    __tablename__ = "darshan_sessions"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("darshan_bookings.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    status = Column(String(50), default="created", nullable=False)

    booking = relationship("DarshanBooking", back_populates="sessions")


class DarshanReview(Base):
    __tablename__ = "darshan_reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("darshan_bookings.id", ondelete="CASCADE"), nullable=False)
    experience_rating = Column(Integer, nullable=False)
    vr_quality_rating = Column(Integer, nullable=False)
    executive_rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    booking = relationship("DarshanBooking", back_populates="reviews")

class SessionExtension(Base):
    __tablename__ = "session_extensions"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("darshan_bookings.id", ondelete="CASCADE"), nullable=False)
    minutes = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    booking = relationship("DarshanBooking", back_populates="extensions")
