from app import db
from app.models import Instructor, InstructorTrack, Track, Profile, HiringPlan
from sqlalchemy import func, case, extract
from app.models import Instructor, InstructorTrack, Track, Profile
from datetime import datetime

def get_kpis():
    total = Instructor.query.count()
    approved = Instructor.query.filter_by(first_approval='Approved').count()
    rejected = Instructor.query.filter_by(first_approval='Rejected').count()
    pending = Instructor.query.filter_by(first_approval='Pending').count()
    
    success_rate = (approved / total * 100) if total > 0 else 0
    avg_rate = db.session.query(func.avg(Instructor.rate_per_hour)).scalar() or 0
    b2b = Instructor.query.filter_by(business_type='B2B').count()
    b2c = Instructor.query.filter_by(business_type='B2C').count()

    return {
        "total": total, "approved": approved, "rejected": rejected, "pending": pending,
        "success_rate": round(success_rate, 1), "avg_rate": round(float(avg_rate), 2),
        "b2b": b2b, "b2c": b2c
    }

def get_track_performance():
    data = db.session.query(
        Track.name,
        func.count(InstructorTrack.id).label('total'),
        func.sum(case((Instructor.first_approval == 'Approved', 1), else_=0)).label('approved'),
        func.sum(case((Instructor.first_approval == 'Rejected', 1), else_=0)).label('rejected'),
        func.sum(case((Instructor.first_approval == 'Pending', 1), else_=0)).label('pending'),
        func.avg(Instructor.rate_per_hour).label('avg_rate')
    ).join(InstructorTrack, Track.id == InstructorTrack.track_id)\
     .join(Instructor, Instructor.id == InstructorTrack.instructor_id)\
     .group_by(Track.id).all()

    return [{"name": d.name, "total": d.total, "approved": d.approved or 0, 
             "rejected": d.rejected or 0, "pending": d.pending or 0,
             "success_rate": round((d.approved/d.total*100),1) if d.total > 0 else 0,
             "avg_rate": round(float(d.avg_rate),2) if d.avg_rate else 0} for d in data]

def get_approval_distribution():
    data = db.session.query(Instructor.first_approval, func.count(Instructor.id))\
                     .filter(Instructor.first_approval.isnot(None))\
                     .group_by(Instructor.first_approval).all()
    return {d[0]: d[1] for d in data}

def get_business_performance():
    data = db.session.query(
        Instructor.business_type,
        func.count(Instructor.id).label('total'),
        func.sum(case((Instructor.first_approval == 'Approved', 1), else_=0)).label('approved')
    ).filter(Instructor.business_type.isnot(None))\
     .group_by(Instructor.business_type).all()
    return [{"type": d.business_type, "total": d.total, "approved": d.approved or 0,
             "success_rate": round((d.approved/d.total*100),1) if d.total > 0 else 0} for d in data]

def get_employment_performance():
    data = db.session.query(
        Instructor.employment_type,
        func.count(Instructor.id).label('total'),
        func.sum(case((Instructor.first_approval == 'Approved', 1), else_=0)).label('approved')
    ).filter(Instructor.employment_type.isnot(None))\
     .group_by(Instructor.employment_type).all()
    return [{"type": d.employment_type, "total": d.total, "approved": d.approved or 0,
             "success_rate": round((d.approved/d.total*100),1) if d.total > 0 else 0} for d in data]

def get_track_distribution():
    data = db.session.query(Track.name, func.count(InstructorTrack.id))\
                     .join(InstructorTrack, Track.id == InstructorTrack.track_id)\
                     .group_by(Track.id).all()
    return [{"name": d.name, "count": d[1]} for d in data]

def get_b2b_b2c_by_track():
    data = db.session.query(
        Track.name,
        func.sum(case((Instructor.business_type == 'B2B', 1), else_=0)).label('b2b'),
        func.sum(case((Instructor.business_type == 'B2C', 1), else_=0)).label('b2c')
    ).join(InstructorTrack, Track.id == InstructorTrack.track_id)\
     .join(Instructor, Instructor.id == InstructorTrack.instructor_id)\
     .group_by(Track.id).all()
    return [{"name": d.name, "b2b": d.b2b or 0, "b2c": d.b2c or 0} for d in data]

def get_profile_distribution():
    data = db.session.query(Profile.name, func.count(InstructorTrack.id))\
                     .join(InstructorTrack, Profile.id == InstructorTrack.profile_id)\
                     .group_by(Profile.id).all()
    return [{"name": d.name, "count": d[1]} for d in data]

def get_cost_analysis():
    data = db.session.query(
        Track.name,
        func.avg(Instructor.rate_per_hour).label('avg_rate'),
        func.sum(case((Instructor.first_approval == 'Approved', 1), else_=0)).label('approved')
    ).join(InstructorTrack, Track.id == InstructorTrack.track_id)\
     .join(Instructor, Instructor.id == InstructorTrack.instructor_id)\
     .group_by(Track.id).all()
    return [{"name": d.name, "avg_rate": round(float(d.avg_rate),2) if d.avg_rate else 0, 
             "approved": d.approved or 0} for d in data]

def get_leaderboard():
    return Instructor.query.order_by(Instructor.score.desc(), Instructor.rate_per_hour.asc()).limit(10).all()

def get_daily_trend():
    # نجيب الأيام اللي فيها تقييمات فعلاً ونرتبها يوم بيوم
    data = db.session.query(
        Instructor.review_date,
        func.sum(case((Instructor.first_approval == 'Approved', 1), else_=0)).label('approved'),
        func.sum(case((Instructor.first_approval == 'Rejected', 1), else_=0)).label('rejected'),
        func.sum(case((Instructor.first_approval == 'Pending', 1), else_=0)).label('pending')
    ).filter(Instructor.review_date.isnot(None))\
     .group_by(Instructor.review_date)\
     .order_by(Instructor.review_date).all()

    return [
        {"day": d.review_date.strftime('%b %d'), "approved": d.approved or 0, "rejected": d.rejected or 0, "pending": d.pending or 0} 
        for d in data
    ]

def get_aging_analysis():
    pending_instructors = Instructor.query.filter(Instructor.first_approval == 'Pending', Instructor.review_date.isnot(None)).all()
    buckets = {"< 7 Days": 0, "7-14 Days": 0, "15-30 Days": 0, "> 30 Days": 0}
    today = datetime.now().date()
    
    for inst in pending_instructors:
        diff = (today - inst.review_date).days
        if diff < 7: buckets["< 7 Days"] += 1
        elif diff < 15: buckets["7-14 Days"] += 1
        elif diff < 31: buckets["15-30 Days"] += 1
        else: buckets["> 30 Days"] += 1
    return buckets

def get_plans_progress():
    plans = HiringPlan.query.order_by(HiringPlan.created_at.desc()).limit(5).all()
    result = []
    for plan in plans:
        # إجمالي المطلوب
        total_target = sum(pt.target_number for pt in plan.plan_tracks)
        
        # الفعلي (اللي Approved بس - ده اللي بيملأ الخطة)
        actual_assigned = Instructor.query.filter_by(plan_id=plan.id, first_approval='Approved').count()
        
        # إحصائيات إضافية عشان نعرضها للادمن
        pending_count = Instructor.query.filter_by(plan_id=plan.id, first_approval='Pending').count()
        rejected_count = Instructor.query.filter_by(plan_id=plan.id, first_approval='Rejected').count()
        
        result.append({
            "id": plan.id,
            "title": plan.title,
            "start_date": plan.start_date.strftime('%b %d, %Y'),
            "target": total_target,
            "actual": actual_assigned,
            "gap": total_target - actual_assigned,
            "percentage": round((actual_assigned / total_target) * 100, 1) if total_target > 0 else 0,
            "pending": pending_count,
            "rejected": rejected_count
        })
    return result

def get_track_status_distribution():
    data = db.session.query(
        Track.name,
        func.sum(case((Instructor.status == 'New', 1), else_=0)).label('new_count'),
        func.sum(case((Instructor.status == 'Current', 1), else_=0)).label('current_count')
    ).join(InstructorTrack, Track.id == InstructorTrack.track_id)\
     .join(Instructor, Instructor.id == InstructorTrack.instructor_id)\
     .group_by(Track.id).all()

    return [{"name": d.name, "new": d.new_count or 0, "current": d.current_count or 0} for d in data]