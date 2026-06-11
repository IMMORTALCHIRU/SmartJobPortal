from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from app.models.resume import Resume
from app.models.interview import MockInterview
from app.models.recommendation import Recommendation
from app.models.job_posting import JobPosting
from app.models.application import Application
from app.models.question import Question
from app.services.resume_parser import ResumeParserService
from app.services.recommendation_service import RecommendationService
from app.services.question_service import QuestionService
from app.services.feedback_service import FeedbackService
from app.services.analytics_service import AnalyticsService
from datetime import datetime
import os

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

def candidate_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'candidate':
            flash('Access denied.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx'}


@candidate_bp.route('/dashboard')
@login_required
@candidate_required
def dashboard():
    resume = Resume.get_latest_by_user(current_user.id)
    recent_interviews = MockInterview.get_completed_by_user(current_user.id, limit=5)
    recommendations = Recommendation.get_latest_by_user(current_user.id)
    analytics = AnalyticsService.get_user_analytics(current_user.id)
    raw_apps = Application.get_by_candidate(current_user.id)
    # Build dict of applied jobs for quick lookup
    applied_jobs = {a.job_id: a for a in raw_apps}
    # Enrich applications with job/company for dashboard display
    applications = []
    for a in raw_apps:
        job = JobPosting.get_by_id(a.job_id)
        applications.append({
            'id': a.id,
            'job_title': job.title if job else 'Unknown',
            'company_name': job.company_name if job else '',
            'status': a.status,
            'applied_at': a.applied_at,
        })
    # Get suggested jobs based on resume and mark which ones are applied
    suggested_jobs = []
    if resume:
        jobs = JobPosting.get_matching_jobs(resume.skills, resume.experience_years, limit=6)
        for job in jobs:
            # Add applied flag to each job
            if not hasattr(job, 'applied'):
                job.applied = job.id in applied_jobs
            suggested_jobs.append(job)
    return render_template('candidate/dashboard.html',
                           resume=resume,
                           recent_interviews=recent_interviews,
                           recommendations=recommendations,
                           analytics=analytics,
                           applications=applications,
                           suggested_jobs=suggested_jobs)


@candidate_bp.route('/resume/upload', methods=['GET', 'POST'])
@login_required
@candidate_required
def resume_upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        file = request.files['resume']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            parsed_data = ResumeParserService.parse_resume(filepath, filename)
            if parsed_data:
                resume = Resume.create(current_user.id, parsed_data)
                RecommendationService.generate_job_recommendations(current_user.id)
                flash('Resume uploaded and analyzed successfully!', 'success')
                return redirect(url_for('candidate.resume_analysis', resume_id=resume.id))
            else:
                flash('Error parsing resume. Please try a different file.', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF or DOCX file.', 'error')
            return redirect(request.url)
    return render_template('candidate/resume_upload.html')


@candidate_bp.route('/resume/analysis/<resume_id>')
@login_required
@candidate_required
def resume_analysis(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume.user_id != current_user.id:
        flash('Resume not found.', 'error')
        return redirect(url_for('candidate.resume_upload'))
    recommendations = Recommendation.get_latest_by_user(current_user.id)
    suggested_jobs = JobPosting.get_matching_jobs(resume.skills, resume.experience_years, limit=8)
    return render_template('candidate/resume_analysis.html',
                           resume=resume,
                           recommendations=recommendations,
                           suggested_jobs=suggested_jobs)


@candidate_bp.route('/resume/history')
@login_required
@candidate_required
def resume_history():
    resumes = Resume.get_by_user(current_user.id)
    return render_template('candidate/resume_history.html', resumes=resumes)


@candidate_bp.route('/jobs')
@login_required
@candidate_required
def jobs():
    resume = Resume.get_latest_by_user(current_user.id)
    all_jobs = JobPosting.get_all_active()
    my_applications = {a.job_id: a for a in Application.get_by_candidate(current_user.id)}

    jobs_with_eligibility = []
    for job in all_jobs:
        eligible = False
        applied = job.id in my_applications
        if resume and resume.resume_score >= job.min_resume_score:
            eligible = True
        app = my_applications.get(job.id)
        jobs_with_eligibility.append({
            'job': job,
            'eligible': eligible,
            'applied': applied,
            'application': app,
            'score_gap': max(0, job.min_resume_score - (resume.resume_score if resume else 0))
        })

    return render_template('candidate/jobs.html',
                           jobs=jobs_with_eligibility,
                           resume=resume)


@candidate_bp.route('/jobs/<job_id>/apply', methods=['POST'])
@login_required
@candidate_required
def apply_job(job_id):
    job = JobPosting.get_by_id(job_id)
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('candidate.jobs'))

    resume = Resume.get_latest_by_user(current_user.id)
    if not resume:
        flash('Please upload your resume before applying.', 'error')
        return redirect(url_for('candidate.resume_upload'))

    if resume.resume_score < job.min_resume_score:
        flash(f'Your resume score ({resume.resume_score}%) does not meet the minimum requirement ({job.min_resume_score}%) for this job.', 'error')
        return redirect(url_for('candidate.jobs'))

    existing = Application.get_by_candidate_and_job(current_user.id, job_id)
    if existing:
        flash('You have already applied for this job.', 'info')
        return redirect(url_for('candidate.jobs'))

    Application.create(current_user.id, job_id, job.employer_id, resume.id, resume.resume_score)
    job.increment_applicants()
    flash(f'Successfully applied for {job.title}! You can now take the interview.', 'success')
    return redirect(url_for('candidate.jobs'))


@candidate_bp.route('/interview/<job_id>/start', methods=['GET', 'POST'])
@login_required
@candidate_required
def start_interview(job_id):
    job = JobPosting.get_by_id(job_id)
    if not job:
        flash('Job not found.', 'error')
        return redirect(url_for('candidate.jobs'))

    application = Application.get_by_candidate_and_job(current_user.id, job_id)
    if not application:
        flash('You must apply for this job before taking the interview.', 'error')
        return redirect(url_for('candidate.jobs'))

    resume = Resume.get_latest_by_user(current_user.id)
    if not resume or resume.resume_score < job.min_resume_score:
        flash('You do not meet the score requirement for this interview.', 'error')
        return redirect(url_for('candidate.jobs'))

    # If an interview was scheduled/attached by the employer reuse it
    if application.interview_id:
        scheduled = MockInterview.get_by_id(application.interview_id)
        if scheduled:
            if scheduled.status == 'completed':
                flash('You have already completed the interview for this job.', 'info')
                return redirect(url_for('candidate.interview_results', interview_id=scheduled.id))
            # If scheduled but not started, start and redirect to session
            if scheduled.status == 'scheduled':
                scheduled.start()
            return redirect(url_for('candidate.interview_session', interview_id=scheduled.id))

    # Get questions for this interview
    questions = QuestionService.get_questions_for_interview(
        job.field or job.title,
        resume.skills if resume else [],
        job.difficulty,
        job.num_questions,
        job_id=job.id
    )

    if not questions:
        flash('No questions available for this interview. Please try again later.', 'warning')
        return redirect(url_for('candidate.jobs'))

    interview_data = {
        'job_id': job_id,
        'interview_type': job.field or job.title,
        'difficulty': job.difficulty,
        'scheduled_time': datetime.utcnow(),
        'questions': [q.id for q in questions],
        'total_questions': len(questions),
        'skills_tested': list(set(tag for q in questions for tag in q.tags))
    }
    interview = MockInterview.create(current_user.id, interview_data)
    interview.start()
    return redirect(url_for('candidate.interview_session', interview_id=interview.id))


@candidate_bp.route('/interview/session/<interview_id>', methods=['GET', 'POST'])
@login_required
@candidate_required
def interview_session(interview_id):
    interview = MockInterview.get_by_id(interview_id)
    if not interview or interview.user_id != current_user.id:
        flash('Interview not found.', 'error')
        return redirect(url_for('candidate.jobs'))

    if interview.status == 'completed':
        return redirect(url_for('candidate.interview_results', interview_id=interview_id))

    if request.method == 'POST':
        answers = {}
        for key, value in request.form.items():
            if key.startswith('answer_'):
                question_id = key.replace('answer_', '')
                answers[question_id] = value

        questions = [Question.get_by_id(qid) for qid in interview.questions]
        questions = [q for q in questions if q]
        evaluation = QuestionService.evaluate_answers(questions, answers)

        start_time = interview.started_at or datetime.utcnow()
        time_taken = int((datetime.utcnow() - start_time).total_seconds())

        interview.complete(
            answers=answers,
            score=evaluation['score'],
            correct_answers=evaluation['correct'],
            time_taken=time_taken
        )

        FeedbackService.generate_feedback(current_user.id, interview_id, evaluation)

        # Update application record
        if interview.job_id:
            application = Application.get_by_candidate_and_job(current_user.id, interview.job_id)
            if application:
                application.set_interview(interview_id, evaluation['score'])

        flash('Interview completed! Check your results.', 'success')
        return redirect(url_for('candidate.interview_results', interview_id=interview_id))

    questions = [Question.get_by_id(qid) for qid in interview.questions]
    questions = [q for q in questions if q]
    job = JobPosting.get_by_id(interview.job_id) if interview.job_id else None
    return render_template('candidate/interview_session.html',
                           interview=interview,
                           questions=questions,
                           job=job)


@candidate_bp.route('/interview/results/<interview_id>')
@login_required
@candidate_required
def interview_results(interview_id):
    interview = MockInterview.get_by_id(interview_id)
    if not interview or interview.user_id != current_user.id:
        flash('Interview not found.', 'error')
        return redirect(url_for('candidate.jobs'))

    if interview.status != 'completed':
        return redirect(url_for('candidate.interview_session', interview_id=interview_id))

    from app.models.feedback import Feedback
    feedback = Feedback.get_by_interview(interview_id)

    questions = [Question.get_by_id(qid) for qid in interview.questions]
    questions = [q for q in questions if q]

    results_list = []
    for question in questions:
        user_answer = interview.answers.get(question.id, '')
        is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
        results_list.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct
        })

    job = JobPosting.get_by_id(interview.job_id) if interview.job_id else None
    passed = interview.score >= (job.interview_criteria_score if job else 60) if job else True

    return render_template('candidate/interview_results.html',
                           interview=interview,
                           results=results_list,
                           feedback=feedback,
                           job=job,
                           passed=passed)


@candidate_bp.route('/interview/history')
@login_required
@candidate_required
def interview_history():
    interviews = MockInterview.get_by_user(current_user.id)
    return render_template('candidate/interview_history.html', interviews=interviews)


@candidate_bp.route('/analytics')
@login_required
@candidate_required
def analytics():
    analytics = AnalyticsService.get_user_analytics(current_user.id)
    chart_data = AnalyticsService.get_performance_chart_data(current_user.id)
    return render_template('candidate/analytics.html',
                           analytics=analytics,
                           chart_data=chart_data)


@candidate_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@candidate_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        preferred_roles = request.form.getlist('preferred_roles')
        profile_summary = request.form.get('profile_summary', '').strip()

        if name and len(name) >= 2:
            current_user.update_profile({
                'name': name,
                'phone': phone,
                'location': location,
                'preferred_roles': preferred_roles,
                'profile_summary': profile_summary,
            })
            flash('Profile updated successfully!', 'success')
        else:
            flash('Name must be at least 2 characters.', 'error')
        return redirect(url_for('candidate.profile'))

    resume = Resume.get_latest_by_user(current_user.id)
    return render_template('candidate/profile.html', resume=resume)
