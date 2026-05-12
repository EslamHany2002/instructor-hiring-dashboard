from flask import Blueprint, redirect, url_for
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # الـ Viewer يروح للداشبورد
    # الـ Recruiter يروح للانستراكترز (زي ما هو)
    if current_user.role == 'Recruiter':
        return redirect(url_for('instructors.list_instructors'))
        
    return redirect(url_for('dashboard.view_dashboard'))