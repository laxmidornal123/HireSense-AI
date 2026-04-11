from database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    score = db.Column(db.Float)
    status = db.Column(db.String(50))

    filename = db.Column(db.String(200))   # ✅ NEW
    role = db.Column(db.String(100))       # ✅ NEW
    created_at = db.Column(db.DateTime, default=db.func.now())  # ✅ NEW
    skills = db.Column(db.Text)    # ✅ NEW (store skills as string)
    feedback = db.Column(db.Text)  