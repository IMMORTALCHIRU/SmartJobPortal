import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.application import Application
from app.models.resume import Resume
from app.models.interview import MockInterview
from app.services.question_service import QuestionService
from app import mongo
from bson import ObjectId
from datetime import datetime

employer_bp = Blueprint('employer', __name__, url_prefix='/employer')

def employer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'employer':
            flash('Access denied. Employer account required.', 'error')
            return redirect(url_for('main.index'))
        if not current_user.is_approved:
            flash('Your account is pending admin approval.', 'info')
            return redirect(url_for('auth.pending'))
        return f(*args, **kwargs)
    return decorated

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


@employer_bp.route('/dashboard')
@login_required
@employer_required
def dashboard():
    jobs = JobPosting.get_by_employer(current_user.id)
    total_applications = Application.count_by_employer(current_user.id)
    active_jobs = sum(1 for j in jobs if j.is_active)
    recent_applications = list(mongo.db.applications.find(
        {'employer_id': ObjectId(current_user.id)}
    ).sort('applied_at', -1).limit(10))

    # Enrich recent apps with candidate and job info
    enriched_apps = []
    for app in recent_applications:
        candidate = User.get_by_id(str(app['candidate_id']))
        job = JobPosting.get_by_id(str(app['job_id']))
        resume = Resume.get_by_id(str(app.get('resume_id', ''))) if app.get('resume_id') else None
        enriched_apps.append({
            'application': Application(app),
            'candidate': candidate,
            'job': job,
            'resume': resume,
        })

    return render_template('employer/dashboard.html',
                           jobs=jobs,
                           total_applications=total_applications,
                           active_jobs=active_jobs,
                           recent_applications=enriched_apps)


@employer_bp.route('/post-job', methods=['GET', 'POST'])
@login_required
@employer_required
def post_job():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        required_skills_raw = request.form.get('required_skills', '')
        required_skills = [s.strip() for s in required_skills_raw.split(',') if s.strip()]
        experience_required = int(request.form.get('experience_required', 0) or 0)
        education_required = request.form.get('education_required', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full-time')
        salary_range = request.form.get('salary_range', '').strip()
        field = request.form.get('field', '').strip()
        min_resume_score = int(request.form.get('min_resume_score', 50) or 50)
        interview_criteria_score = int(request.form.get('interview_criteria_score', 60) or 60)
        num_questions = int(request.form.get('num_questions', 10) or 10)
        difficulty = request.form.get('difficulty', 'medium')

        errors = []
        if not title:
            errors.append('Job title is required.')
        if not description:
            errors.append('Job description is required.')
        if not required_skills:
            errors.append('At least one required skill is needed.')
        if not field:
            errors.append('Job field/category is required.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('employer/post_job.html',
                                   form_data=request.form)

        job_data = {
            'title': title,
            'company_name': current_user.company_name,
            'company_logo': current_user.company_logo,
            'description': description,
            'required_skills': required_skills,
            'experience_required': experience_required,
            'education_required': education_required,
            'location': location,
            'job_type': job_type,
            'salary_range': salary_range,
            'field': field,
            'min_resume_score': min_resume_score,
            'interview_criteria_score': interview_criteria_score,
            'num_questions': num_questions,
            'difficulty': difficulty,
        }
        JobPosting.create(current_user.id, job_data)
        flash(f'Job "{title}" posted successfully!', 'success')
        return redirect(url_for('employer.my_jobs'))

    return render_template('employer/post_job.html', form_data={})


@employer_bp.route('/jobs')
@login_required
@employer_required
def my_jobs():
    jobs = JobPosting.get_by_employer(current_user.id)
    # Attach applicant counts to JobPosting objects so templates can access them directly
    for job in jobs:
        try:
            job.applicant_count = len(Application.get_by_job(job.id))
        except Exception:
            job.applicant_count = getattr(job, 'applicant_count', 0)
    return render_template('employer/my_jobs.html', jobs=jobs)


@employer_bp.route('/jobs/<job_id>/toggle', methods=['POST'])
@login_required
@employer_required
def toggle_job(job_id):
    job = JobPosting.get_by_id(job_id)
    if not job or job.employer_id != current_user.id:
        flash('Job not found.', 'error')
        return redirect(url_for('employer.my_jobs'))
    job.update({'is_active': not job.is_active})
    status = 'activated' if not job.is_active else 'deactivated'
    flash(f'Job {status} successfully.', 'success')
    return redirect(url_for('employer.my_jobs'))


@employer_bp.route('/jobs/<job_id>/delete', methods=['POST'])
@login_required
@employer_required
def delete_job(job_id):
    job = JobPosting.get_by_id(job_id)
    if not job or job.employer_id != current_user.id:
        flash('Job not found.', 'error')
        return redirect(url_for('employer.my_jobs'))
    job.delete()
    flash('Job deleted successfully.', 'success')
    return redirect(url_for('employer.my_jobs'))


@employer_bp.route('/applicants')
@login_required
@employer_required
def applicants():
    job_filter = request.args.get('job_id', '')
    skill_filter = request.args.get('skill', '').strip().lower()
    min_score = int(request.args.get('min_score', 0) or 0)

    if job_filter:
        raw_apps = Application.get_by_job(job_filter)
    else:
        raw_apps = Application.get_by_employer(current_user.id)

    enriched = []
    for app in raw_apps:
        candidate = User.get_by_id(app.candidate_id)
        resume = Resume.get_by_id(app.resume_id) if app.resume_id else None
        job = JobPosting.get_by_id(app.job_id)
        if not candidate or not job:
            continue

        # Apply filters
        if min_score and app.resume_score < min_score:
            continue
        if skill_filter and resume:
            skills_lower = [s.lower() for s in resume.skills]
            if skill_filter not in skills_lower:
                continue

        # Calculate job match %
        job_match = 0
        if resume and job.required_skills:
            skills_lower = [s.lower() for s in resume.skills]
            matched = sum(1 for s in job.required_skills if s.lower() in skills_lower)
            job_match = round((matched / len(job.required_skills)) * 100)

        enriched.append({
            'application': app,
            'candidate': candidate,
            'resume': resume,
            'job': job,
            'job_match': job_match,
        })

    jobs = JobPosting.get_by_employer(current_user.id)
    return render_template('employer/applicants.html',
                           applicants=enriched,
                           jobs=jobs,
                           job_filter=job_filter,
                           skill_filter=skill_filter,
                           min_score=min_score)


@employer_bp.route('/applicants/<app_id>')
@login_required
@employer_required
def candidate_detail(app_id):
    application = Application.get_by_id(app_id)
    if not application or application.employer_id != current_user.id:
        flash('Application not found.', 'error')
        return redirect(url_for('employer.applicants'))

    candidate = User.get_by_id(application.candidate_id)
    resume = Resume.get_by_id(application.resume_id) if application.resume_id else None
    job = JobPosting.get_by_id(application.job_id)
    interview = MockInterview.get_by_id(application.interview_id) if application.interview_id else None

    job_match = 0
    if resume and job and job.required_skills:
        skills_lower = [s.lower() for s in resume.skills]
        matched = sum(1 for s in job.required_skills if s.lower() in skills_lower)
        job_match = round((matched / len(job.required_skills)) * 100)

    return render_template('employer/candidate_detail.html',
                           application=application,
                           candidate=candidate,
                           resume=resume,
                           job=job,
                           interview=interview,
                           job_match=job_match)


@employer_bp.route('/applicants/<app_id>/status', methods=['POST'])
@login_required
@employer_required
def update_status(app_id):
    application = Application.get_by_id(app_id)
    if not application or application.employer_id != current_user.id:
        flash('Application not found.', 'error')
        return redirect(url_for('employer.applicants'))

    new_status = request.form.get('status')
    notes = request.form.get('notes', '').strip()
    valid_statuses = ['applied', 'interview_pending', 'interview_completed', 'shortlisted', 'rejected']
    if new_status in valid_statuses:
        # If scheduling an interview, create a MockInterview and attach it to the application
        if new_status == Application.STATUS_INTERVIEW_PENDING:
            try:
                job = JobPosting.get_by_id(application.job_id)
                resume = Resume.get_by_id(application.resume_id) if application.resume_id else None
                num_q = getattr(job, 'num_questions', 10) or 10
                difficulty = getattr(job, 'difficulty', 'medium') or 'medium'
                questions = QuestionService.get_questions_for_interview(
                    job.field or job.title,
                    resume.skills if resume else [],
                    difficulty,
                    num_q
                )
                if questions:
                    interview_data = {
                        'job_id': job.id,
                        'interview_type': job.field or job.title,
                        'difficulty': difficulty,
                        'scheduled_time': datetime.utcnow(),
                        'questions': [q.id for q in questions],
                        'total_questions': len(questions),
                        'skills_tested': list({t for q in questions for t in q.tags})
                    }
                    interview = MockInterview.create(application.candidate_id, interview_data)
                    # Attach interview id to application (do not mark completed)
                    try:
                        application.attach_interview(interview.id)
                    except Exception:
                        current_app.logger.exception('Failed to attach interview to application')
            except Exception:
                current_app.logger.exception('Error creating interview for application')

        application.update_status(new_status, notes)
        flash(f'Application status updated to {new_status.replace("_", " ").title()}.', 'success')
    return redirect(url_for('employer.candidate_detail', app_id=app_id))


@employer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@employer_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        company_description = request.form.get('company_description', '').strip()
        company_website = request.form.get('company_website', '').strip()
        company_size = request.form.get('company_size', '').strip()
        industry = request.form.get('industry', '').strip()
        years_in_business = request.form.get('years_in_business', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()

        # Handle logo upload
        logo_file = request.files.get('company_logo')
        company_logo = current_user.company_logo
        if logo_file and logo_file.filename and allowed_image(logo_file.filename):
            logo_filename = secure_filename(f"logo_{current_user.email.replace('@','_')}_{logo_file.filename}")
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)
            company_logo = logo_filename

        current_user.update_profile({
            'name': name,
            'company_description': company_description,
            'company_website': company_website,
            'company_size': company_size,
            'industry': industry,
            'years_in_business': years_in_business,
            'phone': phone,
            'location': location,
            'company_logo': company_logo,
        })
        flash('Company profile updated successfully!', 'success')
        return redirect(url_for('employer.profile'))

    return render_template('employer/profile.html')
