from sqlalchemy import create_engine, text
from app import create_app, db
from app.models import User, Track, Profile, HiringPlan, PlanTrack, Instructor, InstructorTrack

def extract_from_neon():
    # ضع رابط النيون بتاعك هنا
    NEON_URL = 'postgresql://neondb_owner:npg_f5lOWNvnp0Mw@ep-shiny-thunder-alge97nj.c-3.eu-central-1.aws.neon.tech/neondb?sslmode=require'
    
    print("Step 1: Creating local SQLite schema...")
    # 1. نفترض مؤقتا إننا شغالين على SQLite عشان ننشئ الجداول الفاضية
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/instructors.db'
    
    with app.app_context():
        db.create_all() 
        print("Local tables created successfully.")

    print("Step 2: Connecting to Neon to read data...")
    # 2. نشبك مباشرة بقاعدة النيون عشان نقرأ الداتا
    neon_engine = create_engine(NEON_URL, connect_args={"sslmode": "require"})
    
    # 3. نشبك بالملف المحلي عشان نكتب فيه
    local_engine = create_engine('sqlite:///instance/instructors.db')
    sqlite_conn = local_engine.connect()

    with neon_engine.connect() as neon_conn:
        print("Step 3: Starting Data Transfer...\n")
        
        # 1. Users
        result = neon_conn.execute(text("SELECT id, username, password_hash, role FROM users"))
        for row in result:
            sqlite_conn.execute(text("INSERT OR IGNORE INTO users (id, username, password_hash, role) VALUES (:id, :username, :password_hash, :role)"), 
                               {"id": row.id, "username": row.username, "password_hash": row.password_hash, "role": row.role})
        print(f"- Extracted Users")

        # 2. Tracks
        result = neon_conn.execute(text("SELECT id, name FROM tracks"))
        for row in result:
            sqlite_conn.execute(text("INSERT OR IGNORE INTO tracks (id, name) VALUES (:id, :name)"), {"id": row.id, "name": row.name})
        print(f"- Extracted Tracks")

        # 3. Profiles
        result = neon_conn.execute(text("SELECT id, name, track_id FROM profiles"))
        for row in result:
            sqlite_conn.execute(text("INSERT OR IGNORE INTO profiles (id, name, track_id) VALUES (:id, :name, :track_id)"), 
                               {"id": row.id, "name": row.name, "track_id": row.track_id})
        print(f"- Extracted Profiles")

        # 4. Hiring Plans
        result = neon_conn.execute(text("SELECT id, title, start_date, end_date, created_at FROM hiring_plans"))
        for row in result:
            sqlite_conn.execute(text("INSERT OR IGNORE INTO hiring_plans (id, title, start_date, end_date, created_at) VALUES (:id, :title, :start_date, :end_date, :created_at)"), 
                               {"id": row.id, "title": row.title, "start_date": row.start_date, "end_date": row.end_date, "created_at": row.created_at})
        print(f"- Extracted Hiring Plans")

        # 5. Plan Tracks
        result = neon_conn.execute(text("SELECT id, plan_id, track_id, profile_id, target_number FROM plan_tracks"))
        for row in result:
            sqlite_conn.execute(text("INSERT OR IGNORE INTO plan_tracks (id, plan_id, track_id, profile_id, target_number) VALUES (:id, :plan_id, :track_id, :profile_id, :target_number)"), 
                               {"id": row.id, "plan_id": row.plan_id, "track_id": row.track_id, "profile_id": row.profile_id, "target_number": row.target_number})
        print(f"- Extracted Plan Tracks")

        # 6. Instructors
        result = neon_conn.execute(text("""SELECT id, name, instructor_id, phone, cv_url, video_url, rate_per_hour, 
                                         employment_type, business_type, technical_feedback, first_approval, 
                                         second_approval, review_date, reviewer_name, notes, score, created_at, plan_id, status 
                                         FROM instructors"""))
        for row in result:
            # تحويل الـ Decimal لـ float عشان SQLite يقبله
            rate = float(row.rate_per_hour) if row.rate_per_hour else 0
            
            sqlite_conn.execute(text("""INSERT OR IGNORE INTO instructors 
                (id, name, instructor_id, phone, cv_url, video_url, rate_per_hour, employment_type, business_type, 
                technical_feedback, first_approval, second_approval, review_date, reviewer_name, notes, score, created_at, plan_id, status) 
                VALUES (:id, :name, :instructor_id, :phone, :cv_url, :video_url, :rate_per_hour, :employment_type, :business_type, 
                :technical_feedback, :first_approval, :second_approval, :review_date, :reviewer_name, :notes, :score, :created_at, :plan_id, :status)"""), 
                               {"id": row.id, "name": row.name, "instructor_id": row.instructor_id, "phone": row.phone, "cv_url": row.cv_url, 
                                "video_url": row.video_url, "rate_per_hour": rate, # هنا حطينا المتغير اللي حولناه
                                "employment_type": row.employment_type, "business_type": row.business_type, 
                                "technical_feedback": row.technical_feedback, "first_approval": row.first_approval, "second_approval": row.second_approval, 
                                "review_date": row.review_date, "reviewer_name": row.reviewer_name, "notes": row.notes, "score": row.score, 
                                "created_at": row.created_at, "plan_id": row.plan_id, "status": row.status})
        print(f"- Extracted Instructors")
        
        # 7. Instructor Tracks
        result = neon_conn.execute(text('SELECT id, instructor_id, track_id, profile_id, "order" FROM instructor_tracks'))
        for row in result:
            sqlite_conn.execute(text('INSERT OR IGNORE INTO instructor_tracks (id, instructor_id, track_id, profile_id, "order") VALUES (:id, :instructor_id, :track_id, :profile_id, :order)'), 
                               {"id": row.id, "instructor_id": row.instructor_id, "track_id": row.track_id, "profile_id": row.profile_id, "order": row.order})
        print(f"- Extracted Instructor Tracks")

        sqlite_conn.commit()
        sqlite_conn.close()
        print("\n✅ Success! Your database has been extracted to 'instance/instructors.db' on your computer.")

if __name__ == '__main__':
    extract_from_neon()