from app import db
from datetime import datetime
from flask_login import UserMixin

class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    profiles = db.relationship('Profile', backref='track', lazy=True)

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)

class Instructor(db.Model):
    __tablename__ = 'instructors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    instructor_id = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    cv_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    rate_per_hour = db.Column(db.Numeric(10, 2))
    employment_type = db.Column(db.String(50))
    business_type = db.Column(db.String(50))
    technical_feedback = db.Column(db.String(50))
    first_approval = db.Column(db.String(50))
    second_approval = db.Column(db.String(50))
    review_date = db.Column(db.Date)
    reviewer_name = db.Column(db.String(255))
    notes = db.Column(db.Text)
    score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='New') # New or Current
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقة الجديدة: كل انستراكتر ممكن يتبع خطة واحدة
    plan_id = db.Column(db.Integer, db.ForeignKey('hiring_plans.id'), nullable=True)
    
    tracks = db.relationship('InstructorTrack', backref='instructor', lazy=True, cascade='all, delete-orphan')

class InstructorTrack(db.Model):
    __tablename__ = 'instructor_tracks'
    id = db.Column(db.Integer, primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    track = db.relationship('Track', backref='instructor_tracks')
    profile = db.relationship('Profile', backref='instructor_tracks')

# ================= الجداول الجديدة للـ Plans =================

class HiringPlan(db.Model):
    __tablename__ = 'hiring_plans'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # علاقة: الخطة فيها كم تراك (متطلبات)
    plan_tracks = db.relationship('PlanTrack', backref='plan', lazy=True, cascade='all, delete-orphan')
    # علاقة: الخطة فيها كم انستراكتر (تم تعيينهم)
    assigned_instructors = db.relationship('Instructor', backref='hiring_plan', lazy=True)

class PlanTrack(db.Model):
    __tablename__ = 'plan_tracks'
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('hiring_plans.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True) # اختياري
    target_number = db.Column(db.Integer, default=1) # كام انستراكتر محتاج
    
    track = db.relationship('Track')
    profile = db.relationship('Profile')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    
# ================= Activity Log Table =================
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Nullable in case system does something
    action = db.Column(db.String(100), nullable=False) # e.g., 'Create', 'Login', 'Delete'
    target_type = db.Column(db.String(50)) # e.g., 'Instructor', 'Plan', 'User'
    details = db.Column(db.String(500)) # e.g., 'Created Instructor: Ahmed Ali'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to easily get who did it
    user = db.relationship('User', backref='logs')