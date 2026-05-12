from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User
from werkzeug.security import generate_password_hash
from app.services.log_service import log_activity

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@login_required
def list_users():
    if current_user.role != 'Admin':
        flash('Access Denied.', 'danger')
        return redirect(url_for('main.index'))
        
    users = User.query.order_by(User.id).all()
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'Admin':
        return redirect(url_for('users.list_users'))
        
    username = request.form.get('username').strip()
    password = request.form.get('password')
    role = request.form.get('role')
    
    if not username or not password or not role:
        flash('All fields are required.', 'danger')
        return redirect(url_for('users.list_users'))
        
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('users.list_users'))
        
    try:
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        log_activity(action='Create', target_type='User', details=f'Created User: {username} ({role})')
        flash(f'User {username} created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('users.list_users'))

@users_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'Admin':
        return redirect(url_for('users.list_users'))
        
    # منع الأدمن من حذف نفسه
    if id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('users.list_users'))
        
    user = User.query.get_or_404(id)
    username = user.username
    
    # فك الارتباطات لو في (مثلاً لو يوزر له Logs)
    db.session.delete(user)
    db.session.commit()
    
    log_activity(action='Delete', target_type='User', details=f'Deleted User: {username}')
    flash(f'User {username} deleted.', 'info')
    return redirect(url_for('users.list_users'))