from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.application import Application
from app.models.resume import Resume
from app.models.interview import MockInterview
from app import mongo
from datetime import datetime, timedelta
from bson import ObjectId
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_EMAIL = 'admin@jobportal.in'
ADMIN_PASSWORD_HASH = None  # Will be seeded on first request


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


def ensure_admin_exists():
    """Create admin user if doesn't exist."""
    admin = mongo.db.users.find_one({'email': ADMIN_EMAIL})
    if not admin:
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        mongo.db.users.insert_one({
            'name': 'Admin',
            'email': ADMIN_EMAIL,
            'password_hash': generate_password_hash('Admin@123'),
            'role': 'admin',
            'preferred_roles': [],
            'date_joined': datetime.utcnow(),
            'profile_summary': 'System Administrator',
            'avatar_color': '#7c3aed',
            'is_active': True,
            'is_approved': True,
        })


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    ensure_admin_exists()
    total_candidates = mongo.db.users.count_documents({'role': 'candidate'})
    total_employers = mongo.db.users.count_documents({'role': 'employer'})
    pending_employers = mongo.db.users.count_documents({'role': 'employer', 'is_approved': False})
    total_jobs = JobPosting.count_active()
    total_applications = mongo.db.applications.count_documents({})
    total_resumes = mongo.db.resumes.count_documents({})
    total_interviews = mongo.db.mock_interviews.count_documents({'status': 'completed'})

    # Recent activity
    recent_employers = User.get_pending_employers()
    recent_candidates = list(mongo.db.users.find({'role': 'candidate'}).sort('date_joined', -1).limit(5))
    recent_candidates = [User(u) for u in recent_candidates]

    # Platform activity for the last 7 days
    labels = []
    candidates_counts = []
    employers_counts = []
    jobs_counts = []
    today = datetime.utcnow()
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_start = datetime(d.year, d.month, d.day)
        day_end = day_start + timedelta(days=1)
        labels.append(day_start.strftime('%b %d'))
        candidates_counts.append(mongo.db.users.count_documents({'role': 'candidate', 'date_joined': {'$gte': day_start, '$lt': day_end}}))
        employers_counts.append(mongo.db.users.count_documents({'role': 'employer', 'date_joined': {'$gte': day_start, '$lt': day_end}}))
        jobs_counts.append(mongo.db.job_postings.count_documents({'created_at': {'$gte': day_start, '$lt': day_end}}))

    act_data = {
        'labels': labels,
        'candidates': candidates_counts,
        'employers': employers_counts,
        'jobs': jobs_counts
    }

    # Recent jobs
    recent_jobs_cursor = mongo.db.job_postings.find().sort('created_at', -1).limit(5)
    recent_jobs = [JobPosting(j) for j in recent_jobs_cursor]
    for job in recent_jobs:
        try:
            job.applicant_count = len(Application.get_by_job(job.id))
        except Exception:
            job.applicant_count = 0

    return render_template('admin/dashboard.html',
                           total_candidates=total_candidates,
                           total_employers=total_employers,
                           pending_employers=pending_employers,
                           total_jobs=total_jobs,
                           total_applications=total_applications,
                           total_resumes=total_resumes,
                           total_interviews=total_interviews,
                           recent_employers=recent_employers,
                           recent_candidates=recent_candidates,
                           act_data=act_data,
                           recent_jobs=recent_jobs)


@admin_bp.route('/employers')
@login_required
@admin_required
def employers():
    filter_type = request.args.get('filter', 'all')
    if filter_type == 'pending':
        employer_list = User.get_pending_employers()
    elif filter_type == 'approved':
        users = mongo.db.users.find({'role': 'employer', 'is_approved': True}).sort('date_joined', -1)
        employer_list = [User(u) for u in users]
    else:
        employer_list = User.get_all_by_role('employer')

    pending_list = User.get_pending_employers()
    return render_template('admin/employers.html',
                           employers=employer_list,
                           pending=pending_list,
                           filter_type=filter_type)


@admin_bp.route('/employers/<employer_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_employer(employer_id):
    User.approve_employer(employer_id)
    flash('Employer approved successfully. They can now post jobs.', 'success')
    return redirect(url_for('admin.employers', filter='pending'))


@admin_bp.route('/employers/<employer_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_employer(employer_id):
    User.set_active(employer_id, False)
    flash('Employer registration rejected.', 'success')
    return redirect(url_for('admin.employers', filter='pending'))


@admin_bp.route('/candidates')
@login_required
@admin_required
def candidates():
    candidate_list = User.get_all_by_role('candidate')
    enriched = []
    for candidate in candidate_list:
        resume = Resume.get_latest_by_user(candidate.id)
        app_count = Application.count_by_candidate(candidate.id)
        enriched.append({
            'candidate': candidate,
            'resume': resume,
            'app_count': app_count,
        })
    return render_template('admin/candidates.html', candidates=enriched)


@admin_bp.route('/users/<user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.get_by_id(user_id)
    if not user or user.role == 'admin':
        flash('Cannot modify this user.', 'error')
        return redirect(request.referrer or url_for('admin.dashboard'))
    User.set_active(user_id, not user.is_active)
    status = 'activated' if not user.is_active else 'deactivated'
    flash(f'User {status} successfully.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.get_by_id(user_id)
    if not user or user.role == 'admin':
        flash('Cannot delete this user.', 'error')
        return redirect(request.referrer or url_for('admin.dashboard'))
    User.delete_user(user_id)
    flash('User deleted successfully.', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/jobs')
@login_required
@admin_required
def jobs():
    all_jobs = mongo.db.job_postings.find().sort('created_at', -1)
    jobs_list = []
    for job_data in all_jobs:
        job = JobPosting(job_data)
        employer = User.get_by_id(job.employer_id)
        app_count = len(Application.get_by_job(job.id))
        jobs_list.append({'job': job, 'employer': employer, 'app_count': app_count})
    return render_template('admin/jobs.html', jobs=jobs_list)


@admin_bp.route('/jobs/<job_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_job(job_id):
    job = JobPosting.get_by_id(job_id)
    if job:
        job.delete()
        flash('Job posting deleted.', 'success')
    return redirect(url_for('admin.jobs'))
