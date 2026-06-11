import resend
from app.config import settings

resend.api_key = settings.resend_api_key


async def send_user_approval_mail(booking):

    print("========== USER APPROVAL MAIL ==========")
    print("Booking ID:", booking.id)
    print("Email:", booking.email_address)
    print("QR:", booking.qr_code)
    print("========================================")

    qr_html = ""

    if booking.qr_code:
        qr_html = f"""
        <div style="text-align:center;margin:30px 0;">
            <img
                src="{booking.qr_code}"
                alt="QR Code"
                width="220"
                style="border:1px solid #E5E7EB;padding:12px;border-radius:12px;background:#FFFFFF;"
            />
        </div>
        """

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VR Darshan Booking Confirmed</title>
</head>

<body style="margin:0;padding:0;background:#F5F3FF;font-family:'Segoe UI',Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:30px 0;background:#F5F3FF;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,#4C1D95,#7C3AED);padding:35px;border-radius:12px 12px 0 0;">

<p style="margin:0;font-size:12px;color:#C4B5FD;font-weight:700;letter-spacing:2px;">
TIRTH GHUMO • DIVYA DRISHTI
</p>

<h1 style="margin:12px 0 0 0;color:#FFFFFF;font-size:28px;">
🙏 Booking Confirmed
</h1>

<p style="margin:10px 0 0 0;color:#DDD6FE;">
Booking ID # {booking.id}
</p>

</td>
</tr>

<!-- Main Body -->
<tr>
<td style="background:#FFFFFF;padding:35px;">

<h2 style="color:#111827;">
Namaste {booking.full_name} 🙏
</h2>

<p style="font-size:15px;color:#4B5563;line-height:1.8;">
We are delighted to inform you that your
<strong>Divya Drishti VR Darshan booking has been approved.</strong>
</p>

<p style="font-size:15px;color:#4B5563;line-height:1.8;">
Our Saarthi will visit your location and assist you throughout the VR Darshan experience.
</p>

<!-- Booking Details -->

<h3 style="color:#7C3AED;margin-top:30px;">
📋 Booking Details
</h3>

<table width="100%" cellpadding="0" cellspacing="0"
style="border:1px solid #E5E7EB;border-radius:10px;overflow:hidden;">

<tr style="background:#F5F3FF;">
<td style="padding:12px;font-weight:600;">Booking ID</td>
<td style="padding:12px;">#{booking.id}</td>
</tr>

<tr>
<td style="padding:12px;font-weight:600;">Date</td>
<td style="padding:12px;">{booking.slot_date}</td>
</tr>

<tr style="background:#F5F3FF;">
<td style="padding:12px;font-weight:600;">Time Slot</td>
<td style="padding:12px;">{booking.slot_time}</td>
</tr>

<tr>
<td style="padding:12px;font-weight:600;">Persons</td>
<td style="padding:12px;">{booking.persons}</td>
</tr>

<tr style="background:#F5F3FF;">
<td style="padding:12px;font-weight:600;">Status</td>
<td style="padding:12px;color:#059669;font-weight:700;">
Approved
</td>
</tr>

</table>

<!-- QR -->

<h3 style="color:#7C3AED;margin-top:30px;text-align:center;">
🎫 Your Entry QR Code
</h3>

{qr_html}

<p style="text-align:center;color:#6B7280;">
Please keep this QR code available during your session.
</p>

<!-- Instructions -->

<h3 style="color:#7C3AED;margin-top:30px;">
📝 Important Instructions
</h3>

<ul style="color:#4B5563;line-height:1.8;">
<li>Please be available 15 minutes before your scheduled slot.</li>
<li>Keep your phone reachable.</li>
<li>Our Saarthi will contact you before arrival.</li>
<li>If you need to reschedule, contact us at least 24 hours before the session.</li>
</ul>

<!-- Support -->

<div style="margin-top:30px;background:#F9FAFB;padding:18px;border-radius:10px;">

<p style="margin:0;">
📞 Support: +91 6260499299
</p>

<p style="margin-top:8px;">
📧 enquiry.tirthghumo@gmail.com
</p>

</div>

<p style="margin-top:30px;color:#4B5563;">
We hope this spiritual experience brings peace, positivity and divine blessings into your life. 🌸🙏
</p>

<p style="margin-top:25px;">
Warm Regards,<br>
<strong>Team TirthGhumo</strong><br>
Divya Drishti VR Darshan
</p>

</td>
</tr>

<!-- Footer -->

<tr>
<td style="background:#F5F3FF;border:1px solid #EDE9FE;border-top:none;border-radius:0 0 12px 12px;padding:20px;text-align:center;">

<p style="margin:0;font-size:11px;color:#9CA3AF;">
Automated confirmation email from TirthGhumo
</p>

<p style="margin-top:6px;font-size:11px;color:#9CA3AF;">
Please do not reply to this email.
</p>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    email = {
        "from": "Tirth Ghumo <no-reply@tirthghumo.in>",
        "to": [booking.email_address],
        "subject": f"🙏 Divya Drishti Booking Confirmed | Booking #{booking.id}",
        "html": html_body,
    }

    try:
        response = resend.Emails.send(email)
        print("MAIL SENT SUCCESSFULLY")
        print(response)
        return response

    except Exception as e:
        print("MAIL FAILED")
        print(str(e))
        raise Exception(f"Failed to send approval email: {str(e)}")