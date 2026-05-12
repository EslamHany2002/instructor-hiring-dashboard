from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import ActivityLog

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/')
@login_required
def view_logs():
    # السماح للأدمن فقط بمشاهدة الـ Logs
    if current_user.role != 'Admin':
        flash('Access Denied. Only Admins can view activity logs.', 'danger')
        return redirect(url_for('main.index'))
        
    # جلب آخر 200 حدث مرتبة من الأحدث للأقدم
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(200).all()
    return render_template('logs/index.html', logs=logs)