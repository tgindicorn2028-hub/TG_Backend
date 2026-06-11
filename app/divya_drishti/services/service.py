from sqlalchemy.orm import Session
from datetime import datetime, timezone , date , time , timedelta
import qrcode
import asyncio
import os
from fastapi import HTTPException, status , BackgroundTasks, UploadFile 
from typing import List
from app.utils.supabase_uploads import upload_to_supabase
from ..models import DarshanBooking, DarshanSession, DarshanReview  , SessionExtension
from ..schema import DarshanBookingCreate, DarshanReviewCreate , CompleteBookingDetails 
from app.utils.mail.vr_admin_mail import send_admin_vr_darshan_email
from app.utils.mail.vr_user_mail import send_user_approval_mail 
import qrcode
import io
from app.utils.supabase_uploads import upload_to_supabase_bytes
from app.utils.whatsapp.divya_drishti import send_whatsapp_message
from math import ceil
from ..slots import WEEKDAY_SLOTS , WEEKEND_SLOTS


def get_available_slots(
    db: Session,
    selected_date: date
):

    slots = (
        WEEKEND_SLOTS
        if selected_date.weekday() >= 5
        else WEEKDAY_SLOTS
    )

    bookings = db.query(
        DarshanBooking
    ).filter(
        DarshanBooking.slot_date == selected_date,
        DarshanBooking.status != "rejected"
    ).all()

    result = []

    for slot in slots:

        slot_start = datetime.combine(
            selected_date,
            datetime.strptime(
                slot,
                "%H:%M"
            ).time()
        )

        slot_end = slot_start + timedelta(
            minutes=30
        )

        available = True

        for booking in bookings:

            if (
                booking.start_datetime is None
                or
                booking.end_datetime is None
            ):
                continue

            overlap = (
                slot_start < booking.end_datetime
                and
                slot_end > booking.start_datetime
            )

            if overlap:
                available = False
                break

        result.append({
            "slot_time": slot,
            "available": available
        })

    return result

def book_session(
    db: Session,
    booking_in: DarshanBookingCreate,
    payment_screenshot: UploadFile,
    background_tasks: BackgroundTasks,
) -> DarshanBooking:

    # -------------------------
    # Upload payment screenshot
    # -------------------------

    payment_screenshot_url = None

    if payment_screenshot:
        try:
            payment_screenshot_url = upload_to_supabase(
                payment_screenshot,
                folder="vr_darshan_payments"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Payment upload failed: {str(e)}"
            )

    # -------------------------
    # Get valid slots
    # -------------------------

    slots = (
        WEEKEND_SLOTS
        if booking_in.slot_date.weekday() >= 5
        else WEEKDAY_SLOTS
    )

    selected_slot = booking_in.slot_time.strip()

    if selected_slot not in slots:
        raise HTTPException(
            status_code=400,
            detail="Invalid slot selected"
        )

    # -------------------------
    # Calculate booking duration
    # -------------------------

    occupied_units = ceil(
        booking_in.persons / 2
    )

    booking_minutes = occupied_units * 30

    buffer_minutes = 30

    total_minutes = booking_minutes + buffer_minutes

    # -------------------------
    # Build datetime range
    # -------------------------

    start_dt = datetime.combine(
        booking_in.slot_date,
        datetime.strptime(
            selected_slot,
            "%H:%M"
        ).time()
    )

    end_dt = start_dt + timedelta(
        minutes=total_minutes
    )

    # -------------------------
    # Check overlap
    # -------------------------

    existing_bookings = db.query(
        DarshanBooking
    ).filter(
        DarshanBooking.slot_date == booking_in.slot_date,
        DarshanBooking.status != "rejected"
    ).all()

    for booking in existing_bookings:
        if(
        booking.start_datetime is None
        or
        booking.end_datetime is None
        ):
            continue

        overlap = (
            start_dt < booking.end_datetime
            and
            end_dt > booking.start_datetime
        )

        if overlap:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Selected slot unavailable. "
                    "Required booking duration or "
                    "buffer overlaps another booking."
                )
            )
    # -------------------------
    # Create booking
    # -------------------------

    new_booking = DarshanBooking(
        full_name=booking_in.full_name,
        contact_number=booking_in.contact_number,
        email_address=booking_in.email_address,
        whatsapp_number=booking_in.whatsapp_number,
        address=booking_in.address,
        persons=booking_in.persons,
        slot_date=booking_in.slot_date,
        slot_time=selected_slot,
        occupied_units=occupied_units,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status="pending",
        payment_status="partial",
        payment_screenshot=payment_screenshot_url,
    )

    db.add(new_booking)

    try:
        db.commit()
        db.refresh(new_booking)

        background_tasks.add_task(
            send_admin_vr_darshan_email,
            new_booking
        )

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Booking creation failed: {str(e)}"
        )

    return new_booking


def complete_booking_details(
    db: Session,
    booking_id: int,
    details: CompleteBookingDetails,
    full_payment_screenshot: UploadFile,
    background_tasks: BackgroundTasks

):
    booking = db.query(DarshanBooking).filter(
        DarshanBooking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    booking.age = details.age
    # booking.gender = details.gender
    booking.darshan_name = details.darshan_name
    booking.payment_mode = details.payment_mode
        # Handle full payment screenshot upload 
    if full_payment_screenshot:
        try:
            full_payment_screenshot_url = upload_to_supabase(
                full_payment_screenshot,
                folder="vr_darshan_full_payments"
            )
            booking.payment_screenshot = full_payment_screenshot_url
            booking.payment_status = "full"
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Full payment screenshot upload failed: {str(e)}"
            )


    db.commit()
    db.refresh(booking)

    return booking

def get_bookings(db: Session):
    try:
        return db.query(DarshanBooking).order_by(DarshanBooking.created_at.desc()).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching bookings: {str(e)}"
        )

def approve_booking(db: Session, booking_id: int, background_tasks: BackgroundTasks) -> DarshanBooking:
    booking = db.query(DarshanBooking).filter(DarshanBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

    if booking.status != "pending":
        raise HTTPException(status_code=400, detail=f"Only pending bookings can be approved. Current: {booking.status}")

    # Generate QR code in memory (no local file)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(f"divya_drishti_booking_{booking_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to bytes buffer instead of disk
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Upload to Supabase so Twilio can access it via public URL
    try:
        qr_code_url = upload_to_supabase_bytes(
            file_bytes=buffer,
            filename=f"booking_{booking_id}.png",
            content_type="image/png",
            folder="vr_darshan_qrcodes"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR upload failed: {str(e)}")

    booking.qr_code = qr_code_url
    booking.status = "approved"

    try:
        db.commit()
        db.refresh(booking)
        asyncio.run(
            send_user_approval_mail(booking)
        )
        
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to approve booking: {str(e)}")

    return booking


def reject_booking(db: Session, booking_id: int) -> DarshanBooking:
    booking = db.query(DarshanBooking).filter(DarshanBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only pending bookings can be rejected. Current status: {booking.status}"
        )
    
    booking.status = "rejected"
    
    try:
        db.commit()
        db.refresh(booking)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject booking: {str(e)}"
        )
        
    return booking


def verify_qr(db: Session, qr_data: str) -> DarshanBooking:
    if not qr_data.startswith("divya_drishti_booking_"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid QR code data format"
        )
    
    try:
        booking_id = int(qr_data.split("_")[-1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid booking ID inside QR code"
        )
        
    booking = db.query(DarshanBooking).filter(DarshanBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking associated with the QR code (ID {booking_id}) not found"
        )
        
    if booking.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking QR verification failed. Booking status must be 'approved'. Current status: {booking.status}"
        )
        
    booking.status = "verified"
    
    try:
        db.commit()
        db.refresh(booking)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update booking verification status: {str(e)}"
        )
        
    return booking


def start_session(db: Session, booking_id: int) -> DarshanSession:
    booking = db.query(DarshanBooking).filter(DarshanBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
        
    if booking.status != "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start session. Booking must be verified first. Current status: {booking.status}"
        )
        
    # Check if there is already an active session
    existing_session = db.query(DarshanSession).filter(
        DarshanSession.booking_id == booking_id,
        DarshanSession.status == "active"
    ).first()
    
    if existing_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active session already exists for this booking."
        )
        
    new_session = DarshanSession(
        booking_id=booking_id,
        start_time=datetime.now(timezone.utc),
        status="active"
    )
    
    booking.status = "started"
    
    db.add(new_session)
    try:
        db.commit()
        db.refresh(new_session)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )
        
    return new_session


def end_session(db: Session, booking_id: int) -> DarshanSession:
    booking = db.query(DarshanBooking).filter(DarshanBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
        
    session = db.query(DarshanSession).filter(
        DarshanSession.booking_id == booking_id,
        DarshanSession.status == "active"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active session found for booking ID {booking_id}"
        )
        
    end_time = datetime.now(timezone.utc)
    session.end_time = end_time
    session.status = "completed"
    
    if session.start_time:
        duration_delta = end_time - session.start_time
        session.duration = int(duration_delta.total_seconds())
        
    booking.status = "completed"
    
    try:
        db.commit()
        db.refresh(session)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )
        
    return session


def create_review(db: Session, review_in: DarshanReviewCreate) -> DarshanReview:
    booking_id = review_in.booking_id
    
    booking = db.query(DarshanBooking).filter(DarshanBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
        
    if booking.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit review. Booking must be completed (session ended). Current status: {booking.status}"
        )
        
    # Check if a review already exists
    existing_review = db.query(DarshanReview).filter(DarshanReview.booking_id == booking_id).first()
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A review has already been submitted for this booking."
        )
        
    new_review = DarshanReview(
        booking_id=booking_id,
        experience_rating=review_in.experience_rating,
        vr_quality_rating=review_in.vr_quality_rating,
        executive_rating=review_in.executive_rating,
        comment=review_in.comment
    )
    
    booking.status = "reviewed"
    
    db.add(new_review)
    try:
        db.commit()
        db.refresh(new_review)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save review: {str(e)}"
        )
        
    return new_review



def check_extension(
    db: Session,
    booking_id: int
):
    booking = db.query(
        DarshanBooking
    ).filter(
        DarshanBooking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            404,
            "Booking not found"
        )

    extension_start = booking.end_datetime

    extension_end = (
        extension_start
        + timedelta(minutes=60)
    )

    other_bookings = db.query(
        DarshanBooking
    ).filter(
        DarshanBooking.slot_date == booking.slot_date,
        DarshanBooking.id != booking.id,
        DarshanBooking.status != "rejected"
    ).all()

    for other in other_bookings:

        if (
            other.start_datetime is None
            or
            other.end_datetime is None
        ):
            continue

        overlap = (
            extension_start < other.end_datetime
            and
            extension_end > other.start_datetime
        )

        if overlap:
            return {
                "possible": False,
                "amount": 0,
                "message": "Extension not available"
            }

    return {
        "possible": True,
        "amount": 500,
        "message": "Extension available"
    }

def extend_session(
    db: Session,
    booking_id: int
):
    booking = db.query(
        DarshanBooking
    ).filter(
        DarshanBooking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(
            404,
            "Booking not found"
        )

    check = check_extension(
        db,
        booking_id
    )

    if not check["possible"]:
        raise HTTPException(
            400,
            check["message"]
        )

    booking.end_datetime = (
        booking.end_datetime
        + timedelta(minutes=60)
    )

    extension = SessionExtension(
        booking_id=booking.id,
        minutes=30,
        amount=399
    )

    db.add(extension)

    db.commit()
    db.refresh(extension)

    return extension