import os
import requests
BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "").strip()

print("BREVO KEY EXISTS:", bool(BREVO_API_KEY))

if BREVO_API_KEY:
    print("BREVO KEY STARTS WITH:", BREVO_API_KEY[:10])
def send_selected_email(to_email, score, role):

    subject = "Congratulations! Your Application Has Been Shortlisted"

    body = f"""
Dear Candidate,

Congratulations!

We are pleased to inform you that your application has been successfully shortlisted for the position of {role}.

Application Details:
Position: {role}
Resume Match Score: {score}%
Status: Strong Match

Our recruitment team will contact you regarding the next steps.

Best Regards,
HireSense AI Recruitment Team
"""

    send_email(to_email, subject, body)


def send_rejection_email(to_email, score, role):

    subject = "Application Status Update"

    body = f"""
Dear Candidate,

Thank you for your interest in the position of {role}.

After careful evaluation, we regret to inform you that your application has not been selected for the next stage.

We encourage you to apply again in the future.

Best Regards,
HireSense AI Recruitment Team
"""

    send_email(to_email, subject, body)


def send_email(to_email, subject, body):
    print("USING KEY:", BREVO_API_KEY[:15])

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "HireSense AI",
            "email": "laxmidornal12@gmail.com"
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": subject,
        "htmlContent": f"<html><body><pre>{body}</pre></body></html>"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    print("BREVO STATUS:", response.status_code)
    print("BREVO RESPONSE:", response.text)