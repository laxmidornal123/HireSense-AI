
import smtplib
from email.mime.text import MIMEText

FROM_EMAIL = ""
PASSWORD = ""

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
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(FROM_EMAIL, PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print("❌ Email error:", e)