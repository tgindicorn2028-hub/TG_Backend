from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime , date , time 

class SessionExtensionCreateRequest(BaseModel):
    booking_id: int
    full_name: str
    age: int
    darshan_name: str
    payment_mode: str

class DarshanBookingCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    # email_address: str = Field(..., min_length=5, max_length=255)
    contact_number: str = Field(..., min_length=10, max_length=15)
    whatsapp_number: str = Field(..., min_length=10, max_length=15)
    address: str = Field(..., min_length=5)
    persons: int = Field(..., gt=0)
    slot_time: str = Field(..., min_length=3)
    slot_date: date = Field(...)
    payment_status: str = Field(..., min_length=3)
    

    @validator("full_name", "contact_number", "whatsapp_number", "address", "slot_time" )
    def no_empty_or_blank(cls, v):
        if v is None or not v.strip():
            raise ValueError("Field cannot be empty or blank")
        return v

class ParticipantCreate(BaseModel):
    full_name: str
    age: int
    darshan_name: str
    
class CompleteBookingDetails(BaseModel):
    participants: list[ParticipantCreate]
    payment_mode: str
    is_extension: Optional[bool] = False


class DarshanBookingResponse(BaseModel):
    id: int
    full_name: str
    contact_number: str
    whatsapp_number: str
    address: str
    persons: int
    slot_time: str
    qr_code: Optional[str] = None
    status: str

    created_at: datetime

    class Config:
        from_attributes = True


class DarshanSessionResponse(BaseModel):
    id: int
    booking_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    status: str

    class Config:
        from_attributes = True


class DarshanReviewCreate(BaseModel):
    booking_id: int
    experience_rating: int = Field(..., ge=1, le=5)
    vr_quality_rating: int = Field(..., ge=1, le=5)
    executive_rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class DarshanReviewResponse(BaseModel):
    id: int
    booking_id: int
    experience_rating: int
    vr_quality_rating: int
    executive_rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class QRVerifyRequest(BaseModel):
    qr_data: str


class SessionStartRequest(BaseModel):
    booking_id: int


class SessionEndRequest(BaseModel):
    booking_id: int
class SessionExtensionResponse(BaseModel):
    id: int
    booking_id: int
    minutes: int
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class SessionExtensionCheckRequest(BaseModel):
    booking_id: int





class SessionExtensionCheckResponse(BaseModel):
    possible: bool
    next_slot_id: Optional[int] = None
    amount: float
    message: str
