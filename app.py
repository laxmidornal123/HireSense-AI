from flask import Flask, render_template, request, redirect, session, send_file
import os
import io
from config import *
from database import db
from models import User, Resume
from flask import flash,redirect
from datetime import datetime
from utils.emailer import send_selected_email, send_rejection_email
from utils.extractor import extract_text
from utils.validator import is_valid_resume
from utils.skills import extract_skills   
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
from reportlab.lib.styles import getSampleStyleSheet

from ai.parser import extract_details   # ✅ keep this
from flask_mail import Mail, Message
app = Flask(__name__)

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

print("EMAIL_USER =", EMAIL_USER)
print("EMAIL_PASSWORD EXISTS =", bool(EMAIL_PASSWORD))

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

app.config['MAIL_USERNAME'] = EMAIL_USER
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = EMAIL_USER
print("EMAIL_USER =", EMAIL_USER)
print("EMAIL_PASSWORD EXISTS =", bool(EMAIL_PASSWORD))
app.config['MAIL_USERNAME'] = EMAIL_USER
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = EMAIL_USER
mail = Mail(app)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

db.init_app(app)

with app.app_context():
    db.create_all()

    print("Columns:", Resume.__table__.columns.keys())
    print("Columns:", Resume.__table__.columns.keys())
import models
print(models.__file__)
print(Resume.__table__.columns.keys())
# ---------------- SIMPLE SIMILARITY (REPLACES BERT) ----------------
def simple_similarity(jd, resume):
    jd_words = set(jd.lower().split())
    resume_words = set(resume.lower().split())

    if len(jd_words) == 0:
        return 0

    common = jd_words.intersection(resume_words)
    return len(common) / len(jd_words)


# ---------------- REGISTER ----------------
@app.route("/", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!", "danger")
            return render_template("register.html")

        user = User(
            name=name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful! Please Login.", "success")
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session["user_id"] = user.id
            session["user_name"] = user.name

            flash("Login Successful!", "success")

            return redirect("/dashboard")

        else:
            flash("Invalid Email or Password!", "danger")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- ROLE EXTRACTOR ----------------
def extract_role(job_desc):
    job_desc = job_desc.lower()

    if "data analyst" in job_desc:
        return "Data Analyst"
    elif "sql developer" in job_desc:
        return "SQL Developer"
    elif "python developer" in job_desc:
        return "Python Developer"
    elif "machine learning" in job_desc:
        return "Machine Learning Engineer"
    elif "full stack" in job_desc:
        return "Full Stack Developer"
    else:
        return "Software Developer"


@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    resumes = Resume.query.filter_by(user_id=session["user_id"]).all()

    return render_template("history.html", resumes=resumes)

@app.route("/view/<int:id>")
def view(id):

    if "user_id" not in session:
        return redirect("/login")

    resume = Resume.query.get(id)

    if not resume:
        return "No record found"

    skills = resume.skills.split(",") if resume.skills else []

    return render_template(
    "result.html",
    candidate_name=session.get("user_name"),
    id=resume.id,
    status=resume.status,
    score=round(resume.score * 100, 2),
    email=resume.email,
    role=resume.role,
    skills=skills,
    matched=skills,
    missing=[],
    feedback=resume.feedback
)
@app.route("/download_pdf/<int:id>")
def download_pdf(id):

    if "user_id" not in session:
        return redirect("/login")

    resume = Resume.query.get(id)

    if not resume:
        return "Report not found"

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    content = []

    
    content.append(Spacer(1, 15))
    # HEADER
    content.append(
    Paragraph(
        "<b>HireSense AI - Candidate Analysis Report</b>",
        styles["Title"]
    )
)

    content.append(Spacer(1, 15))

# CANDIDATE INFORMATION
    content.append(
    Paragraph(
        "<b>Candidate Information</b>",
        styles["Heading2"]
    )
)

    content.append(
    Paragraph(
        f"<b>Candidate ID:</b> HR-{resume.id}",
        styles["Normal"]
    )
)

    content.append(
    Paragraph(
        f"<b>Email:</b> {resume.email}",
        styles["Normal"]
    )
)

    content.append(
    Paragraph(
        f"<b>Role:</b> {resume.role}",
        styles["Normal"]
    )
)

    content.append(
    Paragraph(
        f"<b>Status:</b> {resume.status}",
        styles["Normal"]
    )
)

    content.append(Spacer(1, 15))

# ATS ANALYSIS
    score = round(resume.score * 100, 2)

    content.append(
    Paragraph(
        "<b>ATS Analysis</b>",
        styles["Heading2"]
    )
)

    content.append(
    Paragraph(
        f"<b>ATS Score:</b> {score}%",
        styles["Normal"]
    )
)

    content.append(Spacer(1, 15))

# SKILLS
    skills = resume.skills.split(",") if resume.skills else []

    content.append(
    Paragraph(
        "<b>Extracted Skills</b>",
        styles["Heading2"]
    )
)

    for skill in skills:
        content.append(
        Paragraph(
            f"• {skill.strip()}",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 15))

# HIRING DECISION
    if score >= 75:
        decision = "Recommended for Interview"
    elif score >= 50:
        decision = "Needs Review"
    else:
        decision = "Not Recommended"

    content.append(
    Paragraph(
        "<b>Hiring Decision</b>",
        styles["Heading2"]
    )
)

    content.append(
    Paragraph(
        decision,
        styles["Normal"]
    )
)

    content.append(Spacer(1, 15))

# AI RECOMMENDATION
    content.append(
    Paragraph(
        "<b>AI Recommendation</b>",
        styles["Heading2"]
    )
)

    content.append(
    Paragraph(
        resume.feedback,
        styles["Normal"]
    )
)

    content.append(Spacer(1, 20))

# FOOTER
    content.append(
    Paragraph(
        f"Generated On: {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
        styles["Normal"]
    )
)

    content.append(
    Paragraph(
        "<i>Generated by HireSense AI</i>",
        styles["Normal"]
    )
)
    doc.build(content)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="HireSense_AI_Report.pdf",
        mimetype="application/pdf"
    )
# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    print("Dashboard Session:", session)

    if "user_id" not in session:
        flash("Please Login First!", "warning")
        return redirect("/login")

    if request.method == "POST":

        job_desc = request.form.get("job_desc")
        role = extract_role(job_desc)

        file = request.files["resume"]

        if not file.filename.endswith((".pdf", ".docx")):
            flash("Invalid File format. Upload PDF or DOCX Only","danger")
            return redirect("/dashboard")

        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        text = extract_text(path)

        if not is_valid_resume(text):
            flash("Not a valid resume. Upload PDF or DOCX Only","danger")
            return redirect("/dashboard")

        # ✅ SIMPLE SIMILARITY (NO BERT)
        similarity_score = simple_similarity(job_desc, text)

        # 🔥 Extract details
        details = extract_details(text)
        resume_skills = details.get("skills", [])
        resume_email = details.get("email")

        # 🔥 JD skills
        jd_skills = extract_skills(job_desc)

        resume_skills_lower = [s.lower() for s in resume_skills]

        # 🔥 Matching
        matched = list(set(jd_skills) & set(resume_skills_lower))
        missing = list(set(jd_skills) - set(matched))

        # 🔥 Skill score
        if len(jd_skills) > 0:
            skill_score = len(matched) / len(jd_skills)
        else:
            skill_score = 0

        if len(matched) >= 1:
            skill_score += 0.3

        # 🔥 Final score (internal only)
        final_score = (0.5 * similarity_score) + (0.5 * skill_score)

        # 🔥 STATUS + FEEDBACK
        if final_score > 0.6:
            status = "Strong Match"
            feedback = "Excellent fit for this role"
        elif final_score > 0.35:
            status = "Moderate Match"
            feedback = "Good but missing some skills"
        else:
            status = "Low Match"
            feedback = "Needs improvement in required skills"

        # 🔥 EMAIL
        if resume_email:
            if status == "Strong Match":
                send_selected_email(resume_email, round(final_score * 100, 2), role)
            elif status == "Low Match":
                send_rejection_email(resume_email, round(final_score * 100, 2), role)

        # 🔥 Save to DB
        res = Resume(
    user_id=session["user_id"],
    score=final_score,
    status=status,
    filename=file.filename,
    role=role,
    skills=",".join(resume_skills),
    feedback=feedback,
    email=resume_email
)
        db.session.add(res)
        db.session.commit()

        return render_template(
    "result.html",
    candidate_name=session.get("user_name"),
    id=res.id,
    status=status,
    score=round(final_score * 100, 2),
    email=resume_email,
    role=role,
    skills=resume_skills,
    matched=matched,
    missing=missing,
    feedback=feedback
)

    return render_template("dashboard.html")
@app.route("/send_mail/<int:id>")
def send_mail(id):

    resume = Resume.query.get(id)

    if not resume:
        flash("Resume not found!", "danger")
        return redirect("/history")

    print("Resume ID:", id)
    print("Resume Email:", resume.email)

    try:

        msg = Message(
            subject="Congratulations! Your Resume Has Been Shortlisted",
            sender=app.config['MAIL_USERNAME'],
            recipients=[resume.email]
        )

        msg.body = f"""
Dear Candidate,

Congratulations!

We are pleased to inform you that your resume has been shortlisted for further consideration.

Position: {resume.role}

Status: {resume.status}

Your profile demonstrates strong alignment with the requirements of the role.

Our recruitment team will contact you regarding the next steps.

Thank you for your interest in joining our organization.

Best Regards,
HireSense AI Recruitment Team
"""

        print("MAIL CONFIG:")
        print(app.config['MAIL_SERVER'])
        print(app.config['MAIL_PORT'])
        print(app.config['MAIL_USERNAME'])

        print("MAIL SENT SUCCESSFULLY")

        flash("Email Sent Successfully!", "success")

    except Exception as e:

        print("MAIL ERROR:", e)

        flash(f"Mail Error: {e}", "danger")

    return redirect(f"/view/{id}")
# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)