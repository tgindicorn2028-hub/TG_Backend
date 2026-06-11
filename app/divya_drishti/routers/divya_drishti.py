from fastapi import APIRouter, Depends, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
from fastapi.responses import HTMLResponse
from urllib.parse import quote
from app.database import get_db
from ..schema import (
    DarshanBookingCreate,
    CompleteBookingDetails,
    DarshanBookingResponse,
    DarshanSessionResponse,
    DarshanReviewCreate,
    DarshanReviewResponse,
    QRVerifyRequest,
    SessionStartRequest,
    SessionEndRequest,
    SessionExtensionCheckRequest,
    SessionExtensionCheckResponse,
    SessionExtensionCreateRequest,
    SessionExtensionResponse,

)
from ..services import service

router = APIRouter(
    prefix="/divya-drishti",
    tags=["Divya Drishti"]
)

@router.post(
    "/book",
    response_model=DarshanBookingResponse,
    status_code=status.HTTP_201_CREATED
)
async def book_session(
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email_address: str = Form(...),
    contact_number: str = Form(...),
    whatsapp_number: str = Form(...),
    address: str = Form(...),
    persons: int = Form(...),
    slot_time: str = Form(...),
    slot_date: date = Form(...),
    payment_screenshot: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    booking_in = DarshanBookingCreate(
        full_name=full_name,
        email_address=email_address,
        contact_number=contact_number,
        whatsapp_number=whatsapp_number,
        address=address,
        persons=persons,
        slot_time=slot_time,
        slot_date=slot_date
    )

    return service.book_session(
        db,
        booking_in,
        payment_screenshot,
        background_tasks
    )

@router.put("/update/{booking_id}", response_model=DarshanBookingResponse)
async def update_booking(
    background_tasks: BackgroundTasks,
    booking_id: int,
    age: int = Form(...),
    darshan_name: str = Form(...),
    payment_mode: str = Form(...),
    full_payment_screenshot: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    booking_in = CompleteBookingDetails(
        age=age,    
        darshan_name=darshan_name,
        payment_mode=payment_mode
    )
    return service.complete_booking_details(db, booking_id, booking_in, full_payment_screenshot, background_tasks)





@router.get("/approve-booking/{booking_id}")
def approve_booking_email(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = service.approve_booking(
        db,
        booking_id,
        BackgroundTasks()
    )

    whatsapp_message = f"""
Namaste {booking.full_name} 🙏

Your Divya Drishti VR Darshan booking has been approved.

Booking ID: #{booking.id}

Date: {booking.slot_date}

Time: {booking.slot_time}

Persons: {booking.persons}

Our Saarthi will contact you before arrival.

Team TirthGhumo
"""

    whatsapp_url = (
        f"https://wa.me/91{booking.whatsapp_number}"
        f"?text={quote(whatsapp_message)}"
    )

    return HTMLResponse(f"""
    <html>
    <body style="
        font-family:Arial;
        text-align:center;
        padding-top:50px;
        background:#f8fafc;
    ">

        <h2 style="color:green;">
            ✅ Booking Approved Successfully
        </h2>

        <br>

        <a href="{booking.qr_code}"
           target="_blank"
           style="
             background:#2563EB;
             color:white;
             padding:12px 20px;
             text-decoration:none;
             border-radius:8px;
             margin-right:10px;
           ">
           🖼 View QR Code
        </a>

        <a href="{whatsapp_url}"
           target="_blank"
           style="
             background:#25D366;
             color:white;
             padding:12px 20px;
             text-decoration:none;
             border-radius:8px;
           ">
           📱 Send WhatsApp Message
        </a>

    </body>
    </html>
    """)

@router.get("/reject-booking/{booking_id}")
def reject_booking_email(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = service.reject_booking(db, booking_id)

    whatsapp_message = f"""
Namaste {booking.full_name} 🙏

Unfortunately, your Divya Drishti booking could not be approved.

Booking ID: #{booking.id}

For assistance please contact:
+91 6260499299

Team TirthGhumo
"""

    whatsapp_url = (
        f"https://wa.me/91{booking.whatsapp_number}"
        f"?text={quote(whatsapp_message)}"
    )

    return HTMLResponse(f"""
    <html>
        <body style="font-family:Arial;text-align:center;padding-top:50px;">
            <h2>❌ Booking Rejected Successfully</h2>

            <a href="{whatsapp_url}"
               style="background:#25D366;color:white;padding:12px 20px;
                      text-decoration:none;border-radius:8px;">
               Send WhatsApp Message
            </a>
        </body>
    </html>
    """)

@router.patch("/approve/{booking_id}", response_model=DarshanBookingResponse)
def approve_booking(booking_id: int, db: Session = Depends(get_db)):
    return  service.approve_booking(db, booking_id , background_tasks=BackgroundTasks())

@router.patch("/reject/{booking_id}", response_model=DarshanBookingResponse)
async  def reject_booking(booking_id: int, db: Session = Depends(get_db)):
    return service.reject_booking(db, booking_id)

@router.post("/verify-qr", response_model=DarshanBookingResponse)
def verify_qr(verify_in: QRVerifyRequest, db: Session = Depends(get_db)):
    return service.verify_qr(db, verify_in.qr_data)

@router.post("/session/start", response_model=DarshanSessionResponse)
def start_session(start_in: SessionStartRequest, db: Session = Depends(get_db)):
    return service.start_session(db, start_in.booking_id)

@router.post("/session/end", response_model=DarshanSessionResponse)
def end_session(end_in: SessionEndRequest, db: Session = Depends(get_db)):
    return service.end_session(db, end_in.booking_id)



@router.post("/review", response_model=DarshanReviewResponse)
def create_review(review_in: DarshanReviewCreate, db: Session = Depends(get_db)):
    return service.create_review(db, review_in)

@router.post("/check-extension")
def check_extension(
    check_in: SessionExtensionCheckRequest,
    db: Session = Depends(get_db)
):
    return service.check_extension(
        db,
        check_in.booking_id
    )


@router.post("/session/extend")
def extend_session(
    extend_in: SessionExtensionCreateRequest,
    db: Session = Depends(get_db)
):
    return service.extend_session(
        db,
        extend_in.booking_id
    )
@router.get("/slots")
def get_available_slots(
    selected_date: date,
    db: Session = Depends(get_db)
):
    return service.get_available_slots(
        db,
        selected_date
    )