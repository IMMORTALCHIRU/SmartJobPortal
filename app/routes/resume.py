from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.resume import Resume
from app.services.resume_parser import ResumeParserService
from app.services.recommendation_service import RecommendationService
from app.decorators import candidate_required
import os

resume_bp = Blueprint('resume', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@candidate_required
@resume_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add user ID to filename for uniqueness
            unique_filename = f"{current_user.id}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Parse resume
            parsed_data = ResumeParserService.parse_resume(filepath, filename)
            
            if parsed_data:
                # Store in database
                resume = Resume.create(current_user.id, parsed_data)
                
                # Generate recommendations
                RecommendationService.generate_job_recommendations(current_user.id)
                
                flash('Resume uploaded and analyzed successfully!', 'success')
                return redirect(url_for('resume.analysis', resume_id=resume.id))
            else:
                flash('Error parsing resume. Please try a different file.', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF or DOCX file.', 'error')
            return redirect(request.url)
    
    return render_template('resume/upload.html')

@candidate_required
@resume_bp.route('/analysis/<resume_id>')
@login_required
def analysis(resume_id):
    resume = Resume.get_by_id(resume_id)
    
    if not resume or resume.user_id != current_user.id:
        flash('Resume not found', 'error')
        return redirect(url_for('resume.upload'))
    
    # Get recommendations
    from app.models.recommendation import Recommendation
    recommendations = Recommendation.get_latest_by_user(current_user.id)
    
    return render_template('resume/analysis.html', resume=resume, recommendations=recommendations)

@candidate_required
@resume_bp.route('/history')
@login_required
def history():
    resumes = Resume.get_by_user(current_user.id)
    return render_template('resume/history.html', resumes=resumes)