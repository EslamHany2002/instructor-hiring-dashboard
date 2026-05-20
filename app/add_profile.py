from app import create_app, db
from app.models import Track, Profile

app = create_app()
with app.app_context():
    # التأكد إن التراك موجود
    track = Track.query.filter_by(name="Software Development").first()
    if track:
        # التأكد إن البروفايل مش موجود قبل كده
        exists = Profile.query.filter_by(track_id=track.id, name=".NET Developer").first()
        if not exists:
            new_profile = Profile(name=".NET Developer", track_id=track.id)
            db.session.add(new_profile)
            db.session.commit()
            print("✅ Successfully added '.NET Developer' to Software Development!")
        else:
            print("⚠️ '.NET Developer' already exists!")
    else:
        print("❌ Software Development track not found!")