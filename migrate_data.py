import sqlite3
from sqlalchemy import create_engine, text
from app import create_app, db
from app.models import Track, Profile, Instructor, InstructorTrack, User, HiringPlan, PlanTrack

def migrate():
    app = create_app()
    
    # 1. الـ Connection String بتاع قاعدة البيانات السحابية (حطه هنا تاني عشان السكربت يقرأه)
    POSTGRES_URL = 'postgresql://neondb_owner:npg_f5lOWNvnp0Mw@ep-shiny-thunder-alge97nj.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require'
    
    # 2. الاتصال بقاعدة SQLite القديمة
    sqlite_conn = sqlite3.connect('instance/instructors.db') # تأكد إن مسار الملف صحيح
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    with app.app_context():
        # 3. إنشاء الجداول الفاضية في السحابة
        print("Creating tables in Neon...")
        db.create_all()

        print("Starting Data Migration...")

        # --- أ. نقل الـ Users ---
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            if not User.query.filter_by(id=row['id']).first():
                db.session.add(User(id=row['id'], username=row['username'], password_hash=row['password_hash'], role=row['role']))
        db.session.commit()
        print("Users migrated.")

        # --- ب. نقل الـ Tracks ---
        cursor.execute("SELECT * FROM tracks")
        for row in cursor.fetchall():
            if not Track.query.filter_by(id=row['id']).first():
                db.session.add(Track(id=row['id'], name=row['name']))
        db.session.commit()
        print("Tracks migrated.")

        # --- ج. نقل الـ Profiles ---
        cursor.execute("SELECT * FROM profiles")
        for row in cursor.fetchall():
            if not Profile.query.filter_by(id=row['id']).first():
                db.session.add(Profile(id=row['id'], name=row['name'], track_id=row['track_id']))
        db.session.commit()
        print("Profiles migrated.")

        # --- د. نقل الـ Hiring Plans ---
        cursor.execute("SELECT * FROM hiring_plans")
        for row in cursor.fetchall():
            if not HiringPlan.query.filter_by(id=row['id']).first():
                db.session.add(HiringPlan(id=row['id'], title=row['title'], start_date=row['start_date'], end_date=row['end_date'], created_at=row['created_at']))
        db.session.commit()
        print("Plans migrated.")

        # --- هـ. نقل الـ Plan Tracks ---
        cursor.execute("SELECT * FROM plan_tracks")
        for row in cursor.fetchall():
            if not PlanTrack.query.filter_by(id=row['id']).first():
                db.session.add(PlanTrack(id=row['id'], plan_id=row['plan_id'], track_id=row['track_id'], profile_id=row['profile_id'], target_number=row['target_number']))
        db.session.commit()
        print("Plan Tracks migrated.")

        # --- و. نقل الـ Instructors ---
        cursor.execute("SELECT * FROM instructors")
        for row in cursor.fetchall():
            if not Instructor.query.filter_by(id=row['id']).first():
                db.session.add(Instructor(
                    id=row['id'], name=row['name'], instructor_id=row['instructor_id'], phone=row['phone'],
                    cv_url=row['cv_url'], video_url=row['video_url'], rate_per_hour=row['rate_per_hour'],
                    employment_type=row['employment_type'], business_type=row['business_type'],
                    technical_feedback=row['technical_feedback'], first_approval=row['first_approval'],
                    second_approval=row['second_approval'], review_date=row['review_date'],
                    reviewer_name=row['reviewer_name'], notes=row['notes'], score=row['score'],
                    created_at=row['created_at'], plan_id=row['plan_id'], status=row['status']
                ))
        db.session.commit()
        print("Instructors migrated.")

        # --- ز. نقل الـ Instructor Tracks ---
        cursor.execute("SELECT * FROM instructor_tracks")
        for row in cursor.fetchall():
            if not InstructorTrack.query.filter_by(id=row['id']).first():
                db.session.add(InstructorTrack(id=row['id'], instructor_id=row['instructor_id'], track_id=row['track_id'], profile_id=row['profile_id'], order=row['order']))
        db.session.commit()
        print("Instructor Tracks migrated.")

        print("\n✅ Migration completed successfully! All your data is now in the cloud.")

    sqlite_conn.close()

if __name__ == '__main__':
    migrate()