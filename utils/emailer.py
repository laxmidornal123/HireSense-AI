
import smtplib
from email.mime.text import MIMEText
import os

FROM_EMAIL = os.environ.get("EMAIL_USER")
PASSWORD = os.environ.get("EMAIL_PASSWORD")

# ✅ UPDATED FUNCTION (3 PARAMETERS)
def send_selected_email(to_email, score, role):
    subject = f"🎉 Shortlisted for {role}"

    body = f"""
Hello Candidate,

Congratulations 🎉

You have been shortlisted for the position of {role}.

Our team will contact you soon.

Best Regards,
HR Team
"""

    send_email(to_email, subject, body)


# ❌ UPDATED FUNCTION (3 PARAMETERS)
def send_rejection_email(to_email, score, role):
    subject = f"Application Update - {role}"

    body = f"""
Hello Candidate,

Thank you for applying for the {role} role.

After evaluation, we regret to inform you that you were not shortlisted.

We encourage you to improve and apply again.

Best Regards,
HR Team
"""

    send_email(to_email, subject, body)


# 🔧 COMMON FUNCTION
def send_email(to_email, subject, body):

    print("FROM_EMAIL =", FROM_EMAIL)
    print("PASSWORD EXISTS =", bool(PASSWORD))
    print("TO_EMAIL =", to_email)

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    try:
        print("STEP 1: Connecting SMTP")

        server = smtplib.SMTP("smtp.gmail.com", 587)

        print("STEP 2: Starting TLS")

        server.starttls()

        print("STEP 3: Login")

        server.login(FROM_EMAIL, PASSWORD)

        print("STEP 4: Sending")

        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

        print("STEP 5: Success")

        server.quit()

    except Exception as e:
        print("EMAIL ERROR:", str(e))