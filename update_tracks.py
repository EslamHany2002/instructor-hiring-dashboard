from app import create_app, db
from app.models import Track, Profile

app = create_app()
with app.app_context():
    
    sd_track = Track.query.filter_by(name="Software Development").first()
    if sd_track:
        # مصفوفة التعديلات (الاسم القديم، الاسم الجديد)
        updates = {
            "Node": "Full Stack Node.js Diploma",
            "Python": "Full Stack Python Diploma",
            "PHP Developer": "Full Stack PHP Diploma"
        }
        
        for old_name, new_name in updates.items():
            profile = Profile.query.filter_by(track_id=sd_track.id, name=old_name).first()
            if profile:
                profile.name = new_name
                print(f"✅ Renamed '{old_name}' to '{new_name}'")
            else:
                print(f"⚠️ '{old_name}' not found")
                
        db.session.commit()
        print("\nDone!")
    else:
        print("Track not found!")