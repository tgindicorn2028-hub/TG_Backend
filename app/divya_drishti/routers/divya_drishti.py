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
from ..models import Executive
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
    contact_number: str = Form(...),
    whatsapp_number: str = Form(...),
    address: str = Form(...),
    persons: int = Form(...),
    slot_time: str = Form(...),
    slot_date: date = Form(...),
    payment_status:str = Form(...),
    payment_screenshot: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    booking_in = DarshanBookingCreate(
        full_name=full_name,
        contact_number=contact_number,
        whatsapp_number=whatsapp_number,
        address=address,
        persons=persons,
        slot_time=slot_time,
        slot_date=slot_date,
        payment_status=payment_status
    )

    return service.book_session(
        db,
        booking_in,
        payment_screenshot,
        background_tasks
    )
@router.post("/executive/login")
def executive_login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    executive =db.query(Executive).filter(
        Executive.username == username,
        Executive.password == password
    ).first()

    if not executive:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return{
        "success" : True , 
        "executive_id" : executive.id ,
        "full_name" : executive.full_name
    }
@router.put("/update/{booking_id}", response_model=DarshanBookingResponse)
async def update_booking(
    
    booking_id: int,
    booking_in: CompleteBookingDetails,
    db:Session = Depends(get_db),
):
    return service.complete_booking_details(
        db,
        booking_id,
        booking_in
    )

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
🙏 *Divya Drishti VR Darshan Booking Confirmed*

Namaste {booking.full_name},

We are delighted to inform you that your booking has been approved.

📋 *Booking Details*

• Booking ID: #{booking.id}
• Date: {booking.slot_date}
• Time Slot: {booking.slot_time}
• Persons: {booking.persons}

🎫 Your QR Code:
<a href="{booking.qr_code}" target="_blank">View QR Code</a>

📝 Important Instructions

• Please be available 15 minutes before your scheduled slot.
• Keep your phone reachable.
• Our Saarthi will contact you before arrival.
• If you need to reschedule, contact us at least 24 hours before the session.

📞 Support: +91 6260499299
📧 enquiry.tirthghumo@gmail.com

We hope this spiritual experience brings peace, positivity and divine blessings into your life. 🌸🙏

Warm Regards,
*Team TirthGhumo*
Divya Drishti VR Darshan
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

    decline_message = f"""
🙏 *Divya Drishti VR Darshan Booking Update*

Namaste {booking.full_name},

Thank you for choosing Divya Drishti VR Darshan.

After reviewing your booking request, we regret to inform you that we are currently unable to approve your booking.

❌ *Booking Status: Declined*

📋 *Booking Details*

• Booking ID: #{booking.id}
• Date: {booking.slot_date}
• Time Slot: {booking.slot_time}
• Persons: {booking.persons}

This may happen due to:

• Slot availability issues
• Payment verification issues
• Incomplete booking information
• Operational limitations for the selected schedule

If you believe this was a mistake or would like to book another slot, please contact our support team.

📞 Support: +91 6260499299
📧 enquiry.tirthghumo@gmail.com

We sincerely apologize for any inconvenience caused and hope to serve you in the future. 🌸🙏

Warm Regards,
*Team TirthGhumo*
Divya Drishti VR Darshan
"""



    whatsapp_url = (
        f"https://wa.me/91{booking.whatsapp_number}"
        f"?text={quote(decline_message)}"
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