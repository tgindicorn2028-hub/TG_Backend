
# from twilio.rest import Client
# from app.config import settings

# def send_whatsapp_booking_confirmation(booking):
#     client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
#     print("Starting WhatsApp send...")
#     print("Booking ID:", booking.id)
#     print("QR:", booking.qr_code)
#     print("Phone:", booking.contact_number)
#     message_body = f"""✅ *VR Darshan Booking Confirmed!*

# Namaste {booking.full_name} 🙏

# Your Divya Drishti VR Darshan booking has been *approved*.

# 📋 *Booking Details*
# - Booking ID  : #{booking.id}
# - Persons     : {booking.persons}
# - Slot Time   : {booking.slot_time}

# 🎫 Your QR code is attached. Please show it at the entry counter.

# _Tirth Ghumo — Experience the Divine_ 🕌"""
    
#     # Send QR code image + message
#     try:
        
#         message = client.messages.create(
#             from_=settings.twilio_whatsapp_from,
#             to=f"whatsapp:{booking.contact_number}",
#             body=message_body,
#             media_url=[booking.qr_code]
#         )
#         print("Sending WhatsApp message to:", booking.contact_number)
#         print("Message SID:", message.sid)

#     except Exception as e:
#         print("TWILIO ERROR:", str(e))

import requests
from app.config import settings


def send_whatsapp_message(phone: str, message: str):

    url = (
        f"https://graph.facebook.com/v23.0/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
    "messaging_product": "whatsapp",
    "to": phone,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )
    

    return response.json()