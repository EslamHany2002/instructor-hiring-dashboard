from app import db
from app.models import Track, Profile, User
from werkzeug.security import generate_password_hash

def seed_database():
    # Seed Users if empty
    if User.query.count() == 0:
        admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='Admin')
        recruiter = User(username='recruiter', password_hash=generate_password_hash('recruiter123'), role='Recruiter')
        viewer = User(username='viewer', password_hash=generate_password_hash('viewer123'), role='Viewer') # الجديد
        db.session.add(admin)
        db.session.add(recruiter)
        db.session.add(viewer)
        db.session.commit()

    # Seed Tracks & Profiles if empty
    if Track.query.count() == 0:
        tracks_data = {
            "AI": ["Data Scientist", "Machine Learning Engineer", "Data Engineer", "Generative AI Professional", "AI Agent Engineer", "AI for Developer", "AI Automation"],            
            "Cyber Security": ["Cyber Security Incident Response Analyst"],
            "Software Development": ["Software Tester", "React Frontend Developer", "Mobile App Developer", ".NET Developer", "Full Stack PHP Diploma", "Full Stack Node.js Diploma", "Full Stack Python Diploma"],            
            "Data Analytics": ["Data Analyst", "Power BI Specialist"],
            "Applied Technology": ["IoT Specialist", "Embedded Systems Engineer", "Embedded Linux", "Robotics Engineer", "Firmware Developer"]        
            }

        for track_name, profiles in tracks_data.items():
            track = Track(name=track_name)
            db.session.add(track)
            db.session.flush()
            
            for p_name in profiles:
                db.session.add(Profile(name=p_name, track_id=track.id))
                
        db.session.commit()