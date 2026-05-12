from flask import Blueprint, jsonify
from app.models import Profile

lookups_bp = Blueprint('lookups', __name__)

@lookups_bp.route('/profiles/<int:track_id>')
def get_profiles(track_id):
    profiles = Profile.query.filter_by(track_id=track_id).all()
    return jsonify([{"id": p.id, "name": p.name} for p in profiles])