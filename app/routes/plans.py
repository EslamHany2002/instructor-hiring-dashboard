from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, HiringPlan, PlanTrack, Track, Profile, Instructor
from app.services.log_service import log_activity
from datetime import datetime

plans_bp = Blueprint('plans', __name__)

@plans_bp.route('/')
@login_required
def list_plans():
    plans = HiringPlan.query.order_by(HiringPlan.created_at.desc()).all()
    return render_template('plans/index.html', plans=plans)

@plans_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_plan():
    if current_user.role != 'Admin':
        flash('Only Admins can create hiring plans.', 'danger')
        return redirect(url_for('plans.list_plans'))
        
    tracks = Track.query.all()
    
    if request.method == 'POST':
        try:
            start_str = request.form.get('start_date')
            end_str = request.form.get('end_date')
            
            plan = HiringPlan(
                title=request.form.get('title'),
                start_date=datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else None,
                end_date=datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None,
            )
            db.session.add(plan)
            db.session.flush()

            # جلب التراكات المطلوبة من الفورم (مصفوفات)
            track_ids = request.form.getlist('track_ids[]')
            profile_ids = request.form.getlist('profile_ids[]')
            targets = request.form.getlist('targets[]')

            for i in range(len(track_ids)):
                if track_ids[i]: # لو التراك مش فاضي
                    db.session.add(PlanTrack(
                        plan_id=plan.id,
                        track_id=track_ids[i],
                        profile_id=profile_ids[i] if profile_ids[i] else None,
                        target_number=int(targets[i]) if targets[i] else 1
                    ))

            db.session.commit()
            # تسجيل الحدث في الـ Logs
            log_activity(action='Create', target_type='Plan', details=f'Created Plan: {plan.title}')
            
            flash('Hiring Plan created successfully!', 'success')
            return redirect(url_for('plans.list_plans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    # إصلاح مشكلة الـ JSON Serializing (تحويل الكائنات لقواميس)
    tracks_list = [{"id": t.id, "name": t.name} for t in tracks]
    
    return render_template('plans/create.html', tracks=tracks, tracks_list=tracks_list)

@plans_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_plan(id):
    if current_user.role != 'Admin':
        flash('Only Admins can edit hiring plans.', 'danger')
        return redirect(url_for('plans.list_plans'))
        
    plan = HiringPlan.query.get_or_404(id)
    tracks = Track.query.all()
    
    if request.method == 'POST':
        try:
            start_str = request.form.get('start_date')
            end_str = request.form.get('end_date')
            
            # تحديث بيانات الخطة الأساسية
            plan.title = request.form.get('title')
            plan.start_date = datetime.strptime(start_str, '%Y-%m-%d').date() if start_str else None
            plan.end_date = datetime.strptime(end_str, '%Y-%m-%d').date() if end_str else None
            
            # حذف التراكات القديمة الخاصة بالخطة دي
            PlanTrack.query.filter_by(plan_id=id).delete()
            
            # إضافة التراكات الجديدة (من الفورم)
            track_ids = request.form.getlist('track_ids[]')
            profile_ids = request.form.getlist('profile_ids[]')
            targets = request.form.getlist('targets[]')

            for i in range(len(track_ids)):
                if track_ids[i]:
                    db.session.add(PlanTrack(
                        plan_id=plan.id,
                        track_id=track_ids[i],
                        profile_id=profile_ids[i] if profile_ids[i] else None,
                        target_number=int(targets[i]) if targets[i] else 1
                    ))

            db.session.commit()
            log_activity(action='Update', target_type='Plan', details=f'Updated Plan: {plan.title}')
            flash('Hiring Plan updated successfully!', 'success')
            return redirect(url_for('plans.list_plans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    # تجهيز البيانات للفورم (القوائم + التراكات الموجودة حالياً)
    tracks_list = [{"id": t.id, "name": t.name} for t in tracks]
    plan_tracks = [{
        "track_id": pt.track_id, 
        "profile_id": pt.profile_id, 
        "target": pt.target_number
    } for pt in plan.plan_tracks]
    
    return render_template('plans/edit.html', plan=plan, tracks=tracks, tracks_list=tracks_list, plan_tracks=plan_tracks)

@plans_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_plan(id):
    if current_user.role != 'Admin':
        flash('Only Admins can delete plans.', 'danger')
        return redirect(url_for('plans.list_plans'))
        
    plan = HiringPlan.query.get_or_404(id)
    plan_title = plan.title
    
    # فك الارتباط بين الانستراكترز والخطة قبل الحذف
    Instructor.query.filter_by(plan_id=id).update({'plan_id': None})
    db.session.delete(plan)
    db.session.commit()
    
    # تسجيل الحدث في الـ Logs
    log_activity(action='Delete', target_type='Plan', details=f'Deleted Plan: {plan_title}')
    
    flash('Plan deleted.', 'info')
    return redirect(url_for('plans.list_plans'))