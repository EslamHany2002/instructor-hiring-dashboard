from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services import dashboard_service

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def view_dashboard():
    # منع الـ Recruiter بس (الـ Admin والـ Viewer يقدرون يشوفوا)
    if current_user.role == 'Recruiter':
        flash('You do not have permission to view the Dashboard.', 'danger')
        return redirect(url_for('instructors.list_instructors'))
    return render_template('dashboard.html')

@dashboard_bp.route('/api/kpis')
@login_required
def api_kpis():
    return jsonify(dashboard_service.get_kpis())

@dashboard_bp.route('/api/track-performance')
@login_required
def api_track_performance():
    return jsonify(dashboard_service.get_track_performance())

@dashboard_bp.route('/api/approval-distribution')
@login_required
def api_approval_distribution():
    return jsonify(dashboard_service.get_approval_distribution())

@dashboard_bp.route('/api/business-performance')
@login_required
def api_business_performance():
    return jsonify(dashboard_service.get_business_performance())

@dashboard_bp.route('/api/employment-performance')
@login_required
def api_employment_performance():
    return jsonify(dashboard_service.get_employment_performance())

@dashboard_bp.route('/api/track-distribution')
@login_required
def api_track_distribution():
    return jsonify(dashboard_service.get_track_distribution())

@dashboard_bp.route('/api/b2b-b2c-track')
@login_required
def api_b2b_b2c_track():
    return jsonify(dashboard_service.get_b2b_b2c_by_track())

@dashboard_bp.route('/api/profile-distribution')
@login_required
def api_profile_distribution():
    return jsonify(dashboard_service.get_profile_distribution())

@dashboard_bp.route('/api/cost-analysis')
@login_required
def api_cost_analysis():
    return jsonify(dashboard_service.get_cost_analysis())

@dashboard_bp.route('/api/leaderboard')
@login_required
def api_leaderboard():
    data = dashboard_service.get_leaderboard()
    return jsonify([{"name": i.name, "score": i.score, "rate": float(i.rate_per_hour) if i.rate_per_hour else 0} for i in data])

@dashboard_bp.route('/api/daily-trend')
@login_required
def api_daily_trend():
    return jsonify(dashboard_service.get_daily_trend())

@dashboard_bp.route('/api/aging-analysis')
@login_required
def api_aging_analysis():
    return jsonify(dashboard_service.get_aging_analysis())

@dashboard_bp.route('/api/plans-progress')
@login_required
def api_plans_progress():
    return jsonify(dashboard_service.get_plans_progress())

@dashboard_bp.route('/api/track-status')
@login_required
def api_track_status():
    return jsonify(dashboard_service.get_track_status_distribution())