from fastapi import FastAPI , HTTPException , Response , status , Depends , APIRouter , Form , File , UploadFile
from app import models , schema
from sqlalchemy.orm import Session
from app.database import engine , get_db
from app.config import settings
from fastapi import BackgroundTasks
from datetime import date
import requests
import resend 
from app.utils.mail.bhajan_jamming_mail import bhajan_jamming_free_mail , bhajan_jamming_private_mail

router = APIRouter()

@router.post("/bhajan-jamming/free")
async def create_bhajan_jamming_form(
    background_tasks: BackgroundTasks,

    full_name: str = Form(...),
    age: int = Form(None),
    contact_number: str = Form(...),
    db: Session = Depends(get_db)
):
    bhajan_jamming_entry = models.BhajanJamming(
        full_name=full_name,
        age=age,
        contact_number=contact_number
    )

    db.add(bhajan_jamming_entry)
    db.commit()
    db.refresh(bhajan_jamming_entry)
    
    background_tasks.add_task(bhajan_jamming_free_mail, bhajan_jamming_entry)

    return {"status": "Bhajan Jamming form submitted successfully"}

@router.post("/bhajan-jamming/private")
async def create_private_booking(
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    age: int = Form(...),
    contact_number: str = Form(...),
    city: str = Form(...),
    occasion: str = Form(...),
    date: date = Form(...),
    theme_preference: str = Form(None),
    special_requests: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        entry = models.BhajanJammingBooking(
            full_name=full_name,
            age=age,
            contact_number=contact_number,
            city=city,
            occasion=occasion,
            date=date,
            theme_preference=theme_preference,
            special_requests=special_requests
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)

        background_tasks.add_task(bhajan_jamming_private_mail, entry)

        return {
            "message": "Booking submitted successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
