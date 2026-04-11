from flask import Flask, render_template, request, redirect, session, send_file
import os
import io
from config import *
from database import db
from models import User, Resume

from utils.emailer import send_selected_email, send_rejection_email
from utils.extractor import extract_text
from utils.validator import is_valid_resume
from utils.skills import extract_skills   
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer 
from reportlab.lib.styles import getSampleStyleSheet

from ai.parser import extract_details   # ✅ keep this

app = Flask(__name__)
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
        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            email=request.form["email"],
            password=request.form["password"]
        ).first()

        if user:
            session["user_id"] = user.id
            session["email"] = user.email
            return redirect("/dashboard")

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

    # Convert skills string → list
    skills = resume.skills.split(",") if resume.skills else []

    return render_template(
        "result.html",
        status=resume.status,
        id=resume.id,
        skills=skills,
        matched=skills,   # simple (since no stored match)
        missing=[],
        feedback=resume.feedback if resume.feedback else "No feedback available"
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

    # 🔥 TITLE
    content.append(Paragraph("<b>Resume Analysis Report</b>", styles["Title"]))
    content.append(Spacer(1, 15))

    # 🔥 ROLE
    role = getattr(resume, "role", "Software Developer")
    content.append(Paragraph(f"<b>Role:</b> {role}", styles["Normal"]))
    content.append(Spacer(1, 10))

    # 🔥 STATUS (highlight)
    status_color = "green" if resume.status == "Strong Match" else "orange" if resume.status == "Moderate Match" else "red"

    content.append(Paragraph(
        f"<b>Status:</b> <font color='{status_color}'>{resume.status}</font>",
        styles["Normal"]
    ))
    content.append(Spacer(1, 15))

    # 🔥 SKILLS
    skills = resume.skills.split(",") if hasattr(resume, "skills") and resume.skills else []

    content.append(Paragraph("<b>Skills:</b>", styles["Heading2"]))
    for s in skills:
        content.append(Paragraph(f"• {s}", styles["Normal"]))

    content.append(Spacer(1, 15))

    # 🔥 FEEDBACK
    feedback = getattr(resume, "feedback", "No feedback available")

    content.append(Paragraph("<b>Feedback:</b>", styles["Heading2"]))
    content.append(Paragraph(feedback, styles["Normal"]))

    content.append(Spacer(1, 20))

    # 🔥 FOOTER
    content.append(Paragraph(
        "<i>Generated by Resume Ranker System</i>",
        styles["Normal"]
    ))

    # BUILD PDF
    doc.build(content)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Resume_Report.pdf",
        mimetype="application/pdf"
    )
# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        job_desc = request.form.get("job_desc")
        role = extract_role(job_desc)

        file = request.files["resume"]

        if not file.filename.endswith((".pdf", ".docx")):
            return "❌ Invalid file format"

        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(path)

        text = extract_text(path)

        if not is_valid_resume(text):
            return "❌ Not a valid resume"

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
            filename=file.filename,   # ✅ FIX
            role=role,
            skills=",".join(resume_skills),   # ✅ convert list to string
            feedback=feedback
        )
        db.session.add(res)
        db.session.commit()

        return render_template(
            "result.html",
            id=res.id,
            status=status,
            skills=resume_skills,
            matched=matched,
            missing=missing,
            feedback=feedback
        )

    return render_template("dashboard.html")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)