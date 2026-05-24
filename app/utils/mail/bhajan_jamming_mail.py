import resend
import base64
import os
async def bhajan_jamming_free_mail(data):
    """
    Send enquiry popup details to admin via Resend API
    """

    email_body = f"""
    New Enquiry Received for Free Bhajan Jamming Session

    Full Name         : {data.full_name}
    Contact Number    : {data.contact_number}
    Age       : {data.age}
    """

    email = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": ["enquiry.tirthghumo@gmail.com"],
        "subject": "New Enquiry Popup Received",
        "text": email_body.strip(), 
    }

    try:
        resend.Emails.send(email)
        print("Email sent successfully")
        return {"status": "Enquiry popup email sent successfully"}
    except Exception as e:
        raise Exception(f"Enquiry popup email sending failed: {str(e)}")

async def bhajan_jamming_private_mail(data):
    """
    Send enquiry popup details to admin via Resend API
    """

    email_body = f"""
    New Enquiry Received for Private Bhajan Jamming Session

    Full Name         : {data.full_name}
    Contact Number    : {data.contact_number}
    Age       : {data.age}
    City    : {data.city}
    Occassion : {data.occasion}
    Date        : {data.date}
    Theme Preference : {data.theme_preference or "N/A"}
    Special Requests : {data.special_requests or "N/A"}
    """

    email = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": ["enquiry.tirthghumo@gmail.com"],
        "subject": "New Enquiry Popup Received",
        "text": email_body.strip(), 
    }

    try:
        resend.Emails.send(email)
        print("Email sent successfully")
        return {"status": "Enquiry popup email sent successfully"}
    except Exception as e:
        raise Exception(f"Enquiry popup email sending failed: {str(e)}")